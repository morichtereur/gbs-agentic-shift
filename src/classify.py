"""
Two-stage classification.

Stage 1 (taxonomy.py): deterministic, auditable, decides the clear majority.
Stage 2 (here): Claude decides ONLY the residual the taxonomy flagged ambiguous,
and its reasoning is logged so a reader can audit it the same way as stage 1.

The split matters for credibility: the headline number is carried by the
transparent rule set, not by a model's opinion. The model handles the tail.
"""

from __future__ import annotations

import json
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

    rows = con.execute(
        """SELECT p.id, p.title, p.description
           FROM postings p
           LEFT JOIN labels l ON p.id = l.id
           WHERE l.id IS NULL"""
    ).fetchall()

    if not rows:
        print("Nothing new to classify.")
        return

    client = None
    tax_n = model_n = 0
    for pid, title, desc in rows:
        r = classify_text(f"{title} {desc}")
        if not r.ambiguous:
            row = r.to_row()
            con.execute(
                "INSERT OR REPLACE INTO labels VALUES (?,?,?,?,?,?,?,?)",
                [pid, r.label, "taxonomy", row["score_transactional"],
                 row["score_judgment"], row["score_agent_ops"], row["hits"], ""],
            )
            tax_n += 1
        else:
            if client is None:
                from anthropic import Anthropic
                client = Anthropic(api_key=C.ANTHROPIC_API_KEY, timeout=30.0,
                                   max_retries=1)
            try:
                out = _model_label(client, title, desc)
            except Exception as exc:
                out = {"label": "none", "reason": f"model request failed: {type(exc).__name__}"}
            con.execute(
                "INSERT OR REPLACE INTO labels VALUES (?,?,?,?,?,?,?,?)",
                [pid, out["label"], "model", r.scores["transactional"],
                 r.scores["judgment"], r.scores["agent_ops"], "",
                 out.get("reason", "")],
            )
            model_n += 1

    con.close()
    print(f"Classified {tax_n} by taxonomy, {model_n} by model "
          f"({model_n / max(tax_n + model_n, 1):.0%} needed the fallback).")


if __name__ == "__main__":
    run()
