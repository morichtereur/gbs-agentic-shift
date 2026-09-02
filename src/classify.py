"""
Two-stage classification.

Stage 1 (taxonomy.py): deterministic, auditable, decides the clear majority.
Stage 2 (here): the LLM decides ONLY the residual the taxonomy flagged ambiguous,
and its reasoning is logged so a reader can audit it the same way as stage 1.

The split matters for credibility: the headline number is carried by the
transparent rule set, not by a model's opinion. The model handles the tail.
"""

from __future__ import annotations

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import duckdb

from src import config as C
from src.taxonomy import classify_text

FALLBACK_PROMPT = """You classify a global-business-services job posting into exactly one bucket:

- transactional: rule-based processing work (data entry, invoice processing, reconciliation execution, high-volume back-office).
- judgment: analytical, advisory or planning work (FP&A, forecasting, business partnering, strategic sourcing, process design).
- agent_ops: work that centres on building, orchestrating or supervising AI/automation (agentic AI, prompt work, managing a digital workforce, AI ops).
- none: not a GBS/finance-operations role at all (facilities, reception, unrelated).

Return ONLY compact JSON: {"label": "...", "reason": "<12 words"}. No prose, no markdown."""


def _model_label(client, title: str, description: str) -> dict:
    text = f"TITLE: {title}\n\nDESCRIPTION: {description[:2500]}"
    msg = client.messages.create(
        model=C.CLASSIFIER_MODEL,
        max_tokens=120,
        system=FALLBACK_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    raw = "".join(b.text for b in msg.content if b.type == "text").strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        out = json.loads(raw)
        if out.get("label") not in {"transactional", "judgment", "agent_ops", "none"}:
            out["label"] = "none"
        return out
    except json.JSONDecodeError:
        return {"label": "none", "reason": "unparseable model output"}


_RATE_LOCK = threading.Lock()
_NEXT_REQUEST = 0.0
_THREAD_STATE = threading.local()


def _model_label_safe(title: str, description: str) -> dict:
    """Call the LLM with bounded concurrency and a process-wide request gap."""
    global _NEXT_REQUEST
    with _RATE_LOCK:
        now = time.monotonic()
        wait = max(0.0, _NEXT_REQUEST - now)
        _NEXT_REQUEST = max(now, _NEXT_REQUEST) + C.MODEL_REQUEST_INTERVAL
    if wait:
        time.sleep(wait)

    try:
        client = getattr(_THREAD_STATE, "client", None)
        if client is None:
            from anthropic import Anthropic
            client = Anthropic(api_key=C.ANTHROPIC_API_KEY, timeout=C.MODEL_TIMEOUT,
                               max_retries=0)
            _THREAD_STATE.client = client
        return _model_label(client, title, description)
    except Exception as exc:
        detail = str(exc).splitlines()[0][:160] if str(exc) else ""
        return {"label": "none",
                "reason": f"model request failed: {type(exc).__name__}: {detail}"}


def run() -> None:
    con = duckdb.connect(str(C.DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS labels (
            id VARCHAR PRIMARY KEY,
            label VARCHAR,
            source VARCHAR,          -- 'taxonomy' | 'model'
            score_transactional INT,
            score_judgment INT,
            score_agent_ops INT,
            hits VARCHAR,
            reason VARCHAR
        )
    """)

    if C.RECLASSIFY:
        rows = con.execute(
            "SELECT id, title, description FROM postings ORDER BY id"
        ).fetchall()
    else:
        rows = con.execute(
            """SELECT p.id, p.title, p.description
               FROM postings p
               LEFT JOIN labels l ON p.id = l.id
               WHERE l.id IS NULL"""
        ).fetchall()

    if not rows:
        print("Nothing new to classify.")
        return

    tax_rows = []
    model_tasks = []
    for pid, title, desc in rows:
        r = classify_text(f"{title} {desc}")
        if not r.ambiguous:
            tax_rows.append((pid, r))
        else:
            model_tasks.append((pid, title, desc, r))

    for pid, r in tax_rows:
        row = r.to_row()
        con.execute(
            "INSERT OR REPLACE INTO labels VALUES (?,?,?,?,?,?,?,?)",
            [pid, r.label, "taxonomy", row["score_transactional"],
             row["score_judgment"], row["score_agent_ops"], row["hits"], ""],
        )

    model_results = {}
    if model_tasks:
        workers = max(1, min(C.MODEL_WORKERS, len(model_tasks)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_model_label_safe, title, desc): (pid, r)
                for pid, title, desc, r in model_tasks
            }
            for future in as_completed(futures):
                pid, r = futures[future]
                model_results[pid] = (r, future.result())

    for pid, r in ((pid, r) for pid, _, _, r in model_tasks):
        tax_result, out = model_results[pid]
        con.execute(
            "INSERT OR REPLACE INTO labels VALUES (?,?,?,?,?,?,?,?)",
            [pid, out["label"], "model", tax_result.scores["transactional"],
             tax_result.scores["judgment"], tax_result.scores["agent_ops"], "",
             out.get("reason", "")],
        )

    con.close()
    tax_n = len(tax_rows)
    model_n = len(model_tasks)
    print(f"Classified {tax_n} by taxonomy, {model_n} by model "
          f"({model_n / max(tax_n + model_n, 1):.0%} needed the fallback).")

    # A failed model call degrades to label 'none' per row, which is right for
    # a stray timeout but catastrophic in bulk: every ambiguous posting drops
    # out and the run ships a taxonomy-only mix that looks measured. Bulk
    # failure is therefore fatal — better no snapshot than a biased one.
    failures = [out["reason"] for _, out in model_results.values()
                if out.get("reason", "").startswith("model request failed")]
    if failures:
        counts: dict[str, int] = {}
        for reason in failures:
            counts[reason] = counts.get(reason, 0) + 1
        print(f"WARNING: {len(failures)} of {model_n} model calls failed:")
        for reason, n in sorted(counts.items(), key=lambda kv: -kv[1])[:5]:
            print(f"  {n:5d}  {reason}")
        if len(failures) > 0.1 * model_n:
            raise SystemExit(
                "More than 10% of LLM fallback calls failed — refusing to pass "
                "a taxonomy-only sample off as the measured mix. Fix the cause "
                "above (usually the ANTHROPIC_API_KEY secret) and re-run."
            )


if __name__ == "__main__":
    run()
