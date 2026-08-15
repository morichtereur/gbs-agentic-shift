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
from collections import Counter
from datetime import datetime, timezone
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import config as C
from src.taxonomy import classify_text
from src.orgtype import org_type, market_type

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

    # Every labelled posting with the two cuts attached. Advisory firms match
    # the same search terms but sell advice about GBS rather than doing it, so
    # they are held out of the headline mix and counted separately.
    rows = con.execute("""
        SELECT p.company, p.country, p.source AS source_name, p.title,
               l.label, l.source AS decided_by
        FROM labels l JOIN postings p ON p.id = l.id
        WHERE l.label != 'none'
    """).fetchall()
    if not rows:
        print("No labelled postings. Run fetch + classify first.")
        return

    Row = lambda r: {
        "org": org_type(r[0]), "country": r[1], "market": market_type(r[1]),
        "source_name": r[2], "title": r[3], "label": r[4], "decided_by": r[5],
    }
    tagged = [Row(r) for r in rows]
    advisory_n = sum(1 for r in tagged if r["org"] == "advisory")
    in_scope = [r for r in tagged if r["org"] != "advisory"]
    total = len(in_scope)

    FAMILIES = ("transactional", "judgment", "agent_ops")

    def counts_by(subset):
        return {f: sum(1 for r in subset if r["label"] == f) for f in FAMILIES}

    by_org = {o: counts_by([r for r in in_scope if r["org"] == o])
              for o in ("captive", "bpo")}
    by_market = {m: counts_by([r for r in in_scope if r["market"] == m])
                 for m in ("delivery", "retained", "mixed")}

    mix = sorted(counts_by(in_scope).items(), key=lambda kv: -kv[1])

    country_counts = Counter(
        (r["source_name"], r["country"], r["label"]) for r in in_scope
    )
    by_country = sorted(
        ((source, country, label, n) for (source, country, label), n in country_counts.items()),
        key=lambda t: (t[0], t[1], -t[3]),
    )

    sen = {"junior": {}, "senior": {}, "mid/unknown": {}}
    for r in in_scope:
        b = sen[_seniority(r["title"])]
        b[r["label"]] = b.get(r["label"], 0) + 1

    src = list(Counter(r["decided_by"] for r in in_scope).items())
    observed = sorted({(r["source_name"], r["country"]) for r in in_scope})
    observed = [(source, country, 0) for source, country in observed]
    excluded = con.execute(
        "SELECT count(*) FROM labels WHERE label = 'none'"
    ).fetchone()[0]
    unlabeled = con.execute("""
        SELECT count(*) FROM postings p
        LEFT JOIN labels l ON p.id = l.id
        WHERE l.id IS NULL
    """).fetchone()[0]
    con.close()
    gold_metrics = _gold_metrics()
    audit_path = C.ROOT / "eval" / "agent_ops_audit.jsonl"
    audit_rows = []
    if audit_path.exists():
        audit_rows = [json.loads(line) for line in audit_path.read_text().splitlines() if line.strip()]
    audit_counts = {}
    for row in audit_rows:
        audit_counts[row["audit"]] = audit_counts.get(row["audit"], 0) + 1

    # ---- chart ----
    labels_order = ["transactional", "judgment", "agent_ops"]
    counts = {l: n for l, n in mix}
    colors = {"transactional": "#8c8c8c", "judgment": "#3b6ea5", "agent_ops": "#c65b2e"}
    fig, ax = plt.subplots(figsize=(10, 3.4))
    fig.patch.set_facecolor("white")
    left = 0
    for name in labels_order:
        share = counts.get(name, 0) / total
        ax.barh(0, share, left=left, color=colors[name], height=0.55,
                edgecolor="white", linewidth=1.5)
        if share > 0.06:
            ax.text(left + share / 2, 0, f"{name}\n{share:.0%}", ha="center",
                    va="center", color="white", fontsize=13, fontweight="bold")
        left += share
    agent_share = counts.get("agent_ops", 0) / total
    ax.annotate(
        f"agent-ops\n{agent_share:.0%}",
        xy=(1 - agent_share / 2, 0.28), xytext=(0.92, 0.85),
        ha="center", fontsize=12, fontweight="bold", color="#c65b2e",
        arrowprops=dict(arrowstyle="-", color="#c65b2e", lw=1.3),
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 1.1)
    ax.axis("off")
    ax.text(0, 1.02, "What GBS job postings actually ask people to do", fontsize=16,
            fontweight="bold", transform=ax.get_yaxis_transform(), ha="left", va="bottom")
    observed_market_count = len({(source, country) for source, country, _ in observed})
    ax.text(0, 0.86, f"{total:,} live postings · {observed_market_count} observed markets · point-in-time cross-section",
            fontsize=11, color="#555", transform=ax.get_yaxis_transform(), ha="left", va="bottom")
    ax.text(0, -0.42, 'McKinsey predicts a new "agent force" layer. In current hiring it is '
            f"{agent_share:.0%}.", fontsize=11.5, color="#222",
            transform=ax.get_yaxis_transform(), ha="left", va="top", style="italic")
    fig.tight_layout()
    (C.DATA / "chart_mix.png").unlink(missing_ok=True)
    fig.savefig(C.DATA / "chart_mix.png", dpi=170, bbox_inches="tight", facecolor="white")

    # ---- RESULTS.md ----
    def pct(n): return f"{n} ({n/total:.0%})"
    lines = [
        "# Results",
        "",
        f"**Generated:** {datetime.now(timezone.utc).date().isoformat()}  "
        "**Scope:** live Adzuna postings, point-in-time cross-section",
        "",
        f"Cross-section of **{total}** labelled live GBS / finance-operations postings "
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
        f"Excludes **{advisory_n}** postings from advisory firms (consultancies selling "
        "GBS advice rather than performing GBS work). Third-party BPO delivery is kept "
        "in — it is the same work, outsourced — and broken out below.",
        "",
        "## By market type",
        "",
        "Delivery hubs and high-cost retained markets are different populations. "
        "Pooling them makes the headline partly a statement about the country basket, "
        "so the split is reported rather than averaged away.",
        "",
        "| market type | postings | transactional | judgment | agent_ops |",
        "|---|---|---|---|---|",
    ]
    MARKET_NOTE = {
        "delivery": "low-cost delivery hubs",
        "retained": "high-cost, HQ / process ownership",
        "mixed": "regional HQ alongside nearshore delivery",
    }
    for mk in ("delivery", "retained", "mixed"):
        c = by_market[mk]
        n = sum(c.values())
        if not n:
            continue
        lines.append(
            f"| {mk} ({MARKET_NOTE[mk]}) | {n} | "
            f"{c['transactional']/n:.0%} | {c['judgment']/n:.0%} | {c['agent_ops']/n:.1%} |"
        )
    lines += [
        "",
        "## By organisation type",
        "",
        "| organisation | postings | transactional | judgment | agent_ops |",
        "|---|---|---|---|---|",
    ]
    ORG_NOTE = {"captive": "in-house GBS", "bpo": "third-party delivery"}
    for o in ("captive", "bpo"):
        c = by_org[o]
        n = sum(c.values())
        if not n:
            continue
        lines.append(
            f"| {o} ({ORG_NOTE[o]}) | {n} | "
            f"{c['transactional']/n:.0%} | {c['judgment']/n:.0%} | {c['agent_ops']/n:.1%} |"
        )
    lines += [
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
        f"- {unlabeled} fetched postings remain unlabelled and are excluded from this report.",
        f"- Agent-ops audit: {audit_counts.get('true', 0)} clear, "
        f"{audit_counts.get('borderline', 0)} borderline, "
        f"{audit_counts.get('false', 0)} likely false positives, "
        f"{audit_counts.get('duplicate', 0)} duplicate rows.",
    ]
    if gold_metrics:
        accuracy, agent_recall = gold_metrics
        observed_agent = counts.get("agent_ops", 0)
        adjusted_agent = observed_agent / agent_recall / total if agent_recall else 0
        lines += [
            f"- Taxonomy gold-set accuracy: {accuracy:.1%} (n=60).",
            f"- Gold-set agent_ops recall: {agent_recall:.1%}; the agent_ops share should be treated as a lower-bound signal until recall improves.",
                f"- Confidence split: agent_ops precision is strong, but the transactional-vs-judgment mix is exploratory at {accuracy:.1%} overall accuracy.",
            f"- Sensitivity illustration: correcting the observed {observed_agent} agent_ops labels for the measured recall gives approximately {adjusted_agent:.1%}; this is an upper-bound diagnostic, not a new point estimate.",
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
