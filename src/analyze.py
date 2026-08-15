"""
Aggregate the classified cross-section and write the findings.

Everything here is measured from the postings table — RESULTS.md is generated,
never hand-written, so the README's claims always match the last run.

Two cuts, both aimed at McKinsey's thesis:
  1. Overall family mix (transactional / judgment / agent_ops) -> is the base
     really shrinking and a new agent-ops layer appearing?
  2. Seniority split -> the "less entry-level talent" claim. Junior vs senior
     is inferred from the title (crude but transparent; flagged as such).
"""

from __future__ import annotations

import re
import json
from datetime import datetime, timezone
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import config as C
from src.taxonomy import classify_text

SENIOR = re.compile(r"(?i)\b(senior|lead|manager|head|principal|director|vp)\b")
JUNIOR = re.compile(r"(?i)\b(junior|graduate|entry|trainee|apprentice|intern|clerk|assistant)\b")


def _seniority(title: str) -> str:
    if SENIOR.search(title):
        return "senior"
    if JUNIOR.search(title):
        return "junior"
    return "mid/unknown"


def _gold_metrics() -> tuple[float, float] | None:
    gold_path = C.ROOT / "eval" / "labels.jsonl"
    if not gold_path.exists():
        return None
    rows = [json.loads(line) for line in gold_path.read_text().splitlines() if line.strip()]
    if not rows:
        return None
    predictions = [classify_text(row["text"]).label for row in rows]
    accuracy = sum(pred == row["gold"] for pred, row in zip(predictions, rows)) / len(rows)
    agent_rows = [(pred, row["gold"]) for pred, row in zip(predictions, rows) if row["gold"] == "agent_ops"]
    agent_recall = sum(pred == "agent_ops" for pred, _ in agent_rows) / len(agent_rows) if agent_rows else 0
    return accuracy, agent_recall


def run() -> None:
    con = duckdb.connect(str(C.DB_PATH))

    total = con.execute(
        "SELECT count(*) FROM labels WHERE label != 'none'"
    ).fetchone()[0]
    if total == 0:
        print("No labelled postings. Run fetch + classify first.")
        return

    mix = con.execute("""
        SELECT label, count(*) AS n
        FROM labels WHERE label != 'none'
        GROUP BY label ORDER BY n DESC
    """).fetchall()

    by_country = con.execute("""
        SELECT p.source, p.country, l.label, count(*) AS n
        FROM labels l JOIN postings p ON p.id = l.id
        WHERE l.label != 'none'
        GROUP BY p.source, p.country, l.label ORDER BY p.source, p.country, n DESC
    """).fetchall()

    titles = con.execute("""
        SELECT p.title, l.label
        FROM labels l JOIN postings p ON p.id = l.id
        WHERE l.label != 'none'
    """).fetchall()

    sen = {"junior": {}, "senior": {}, "mid/unknown": {}}
    for title, label in titles:
        b = sen[_seniority(title)]
        b[label] = b.get(label, 0) + 1

    src = con.execute("""
        SELECT source, count(*) FROM labels WHERE label != 'none' GROUP BY source
    """).fetchall()
    observed = con.execute("""
        SELECT p.source, p.country, count(*)
        FROM postings p JOIN labels l ON p.id = l.id
        WHERE l.label != 'none'
        GROUP BY p.source, p.country
        ORDER BY p.source, p.country
    """).fetchall()
    excluded = con.execute(
        "SELECT count(*) FROM labels WHERE label = 'none'"
    ).fetchone()[0]
    con.close()
    gold_metrics = _gold_metrics()

    # ---- chart ----
    labels_order = ["transactional", "judgment", "agent_ops"]
    counts = {l: n for l, n in mix}
    vals = [counts.get(l, 0) for l in labels_order]
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="#f5f1e8")
    ax.set_facecolor("#f5f1e8")
    ax.bar(labels_order, vals, color=["#6f7d8c", "#14213d", "#2f8f83"])
    ax.set_ylabel("postings", color="#475467")
    ax.set_title(f"GBS posting mix / point-in-time / n={total}", loc="left", color="#14213d")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#d9d5ca")
    ax.tick_params(axis="both", colors="#667085", length=0)
    ax.grid(axis="y", color="#d9d5ca", linewidth=0.7)
    ax.set_axisbelow(True)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v}\n{v/total:.0%}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    (C.DATA / "chart_mix.png").unlink(missing_ok=True)
    fig.savefig(C.DATA / "chart_mix.png", dpi=130)

    # ---- RESULTS.md ----
    def pct(n): return f"{n} ({n/total:.0%})"
    lines = [
        "# Results",
        "",
        f"**Generated:** {datetime.now(timezone.utc).date().isoformat()}  "
        "**Scope:** live Adzuna postings, point-in-time cross-section",
        "",
        f"Cross-section of **{total}** live GBS / finance-operations postings "
        f"({', '.join(f'{source}/{country}' for source, country, _ in observed)}), "
        "pulled from the sources shown. Point-in-time, not a trend.",
        "",
        "## Family mix",
        "",
        "| family | postings |",
        "|---|---|",
    ]
    for l in labels_order:
        lines.append(f"| {l} | {pct(counts.get(l, 0))} |")
    lines += [
        "",
        "![mix](data/chart_mix.png)",
        "",
        "## By seniority (title-inferred, crude)",
        "",
        "| seniority | transactional | judgment | agent_ops |",
        "|---|---|---|---|",
    ]
    for s in ["junior", "mid/unknown", "senior"]:
        b = sen[s]
        lines.append(f"| {s} | {b.get('transactional',0)} | "
                     f"{b.get('judgment',0)} | {b.get('agent_ops',0)} |")
    lines += [
        "",
        "## Method transparency",
        "",
        f"- {dict(src).get('taxonomy',0)} labelled by the deterministic taxonomy, "
        f"{dict(src).get('model',0)} by the Claude fallback.",
        f"- Claude fallback share among included postings: {dict(src).get('model',0)/total:.0%}.",
        f"- {excluded} postings were labelled `none` and excluded from the family mix.",
    ]
    if gold_metrics:
        accuracy, agent_recall = gold_metrics
        lines += [
            f"- Taxonomy gold-set accuracy: {accuracy:.1%} (n=60).",
            f"- Gold-set agent_ops recall: {agent_recall:.1%}; the agent_ops share should be treated as a lower-bound signal until recall improves.",
        ]
    lines += [
        "",
        "## Country cut",
        "",
        "| country | family | postings |",
        "|---|---|---|",
    ]
    lines[-2] = "| source / country | family | postings |"
    for source_name, country, label, n in by_country:
        lines.append(f"| {source_name} / {country} | {label} | {n} |")
    lines += [
        "",
        "- Gold-set detail: `python -m eval.eval_classify` prints the confusion matrix and per-family metrics.",
        "- Seniority is inferred from title keywords only — treat as directional.",
    ]
    (C.ROOT / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote RESULTS.md and data/chart_mix.png (n={total}).")
    for l in labels_order:
        print(f"  {l:14} {pct(counts.get(l, 0))}")


if __name__ == "__main__":
    run()
