"""Append the current cross-section to the committed snapshot history.

A single cross-section cannot show a trend, and the thesis under test is a
claim about change. Each monthly refresh therefore records its aggregates in
`data/history.csv` — a committed, long-format file (date, cut, segment,
family, postings) that the dashboard reads to draw the trend. The row counts
here are computed exactly as in `src/analyze.py`: advisory postings held out,
`none` labels excluded.

The file is idempotent per snapshot date: re-running a refresh replaces that
date's rows rather than duplicating them.

Alerting: when the agent-ops share of any tracked segment reaches the
threshold (`GBS_AGENT_OPS_ALERT`, default 5%) for the first time — i.e. the
previous snapshot was below it — the crossing is written to `data/alert.txt`
for the refresh workflow to turn into a GitHub issue. The file is not
committed; it exists only in the run that produced it.
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime, timezone

import duckdb

from src import config as C
from src.orgtype import org_type, market_type

HISTORY_PATH = C.DATA / "history.csv"
ALERT_PATH = C.DATA / "alert.txt"
FIELDS = ["date", "cut", "segment", "family", "postings"]
FAMILIES = ("transactional", "judgment", "agent_ops")

# Which slices get a row per family. "all" is the headline mix; the org and
# market cuts are the two the study argues the mix cannot be read without.
SEGMENTS = [
    ("all", "all", lambda r: True),
    ("org", "captive", lambda r: r["org"] == "captive"),
    ("org", "bpo", lambda r: r["org"] == "bpo"),
    ("market", "delivery", lambda r: r["market"] == "delivery"),
    ("market", "retained", lambda r: r["market"] == "retained"),
    ("market", "mixed", lambda r: r["market"] == "mixed"),
]

ALERT_THRESHOLD = float(os.getenv("GBS_AGENT_OPS_ALERT", "0.05"))


def snapshot_date(con: duckdb.DuckDBPyConnection) -> str:
    """The date the postings were collected, not the date this ran."""
    fetched = con.execute(
        "SELECT max(fetched_at) FROM postings WHERE fetched_at != ''"
    ).fetchone()[0]
    if fetched:
        return str(fetched)[:10]
    return datetime.now(timezone.utc).date().isoformat()


def snapshot_rows(con: duckdb.DuckDBPyConnection, date: str) -> list[dict]:
    raw = con.execute("""
        SELECT p.company, p.country, l.label
        FROM labels l JOIN postings p ON p.id = l.id
        WHERE l.label != 'none'
    """).fetchall()
    tagged = [
        {"org": org_type(company), "market": market_type(country), "label": label}
        for company, country, label in raw
    ]
    in_scope = [r for r in tagged if r["org"] != "advisory"]
    if not in_scope:
        sys.exit("No labelled postings. Run fetch + classify first.")
    rows = []
    for cut, segment, keep in SEGMENTS:
        subset = [r for r in in_scope if keep(r)]
        for family in FAMILIES:
            rows.append({
                "date": date, "cut": cut, "segment": segment, "family": family,
                "postings": sum(1 for r in subset if r["label"] == family),
            })
    return rows


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    with HISTORY_PATH.open(newline="") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def write_history(rows: list[dict]) -> None:
    order = {(cut, segment): i for i, (cut, segment, _) in enumerate(SEGMENTS)}
    rows = sorted(rows, key=lambda r: (r["date"],
                                       order.get((r["cut"], r["segment"]), 99),
                                       FAMILIES.index(r["family"])))
    with HISTORY_PATH.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def agent_ops_share(rows: list[dict], date: str, cut: str, segment: str) -> float | None:
    slice_ = [r for r in rows
              if r["date"] == date and r["cut"] == cut and r["segment"] == segment]
    total = sum(int(r["postings"]) for r in slice_)
    if not total:
        return None
    agent = sum(int(r["postings"]) for r in slice_ if r["family"] == "agent_ops")
    return agent / total


def check_alert(rows: list[dict], date: str) -> list[str]:
    """A crossing, not a level: fires only when the previous snapshot was below."""
    dates = sorted({r["date"] for r in rows})
    previous = max((d for d in dates if d < date), default=None)
    lines = []
    for cut, segment, _ in SEGMENTS:
        now = agent_ops_share(rows, date, cut, segment)
        if now is None or now < ALERT_THRESHOLD:
            continue
        before = agent_ops_share(rows, previous, cut, segment) if previous else None
        if before is not None and before >= ALERT_THRESHOLD:
            continue  # already above last time — not news
        where = "all postings" if segment == "all" else f"{cut} = {segment}"
        prior = f"{before:.1%} in the {previous} snapshot" if before is not None else "no prior snapshot"
        lines.append(
            f"- agent-ops share reached {now:.1%} in {where} "
            f"({date} snapshot; threshold {ALERT_THRESHOLD:.0%}; prior: {prior})."
        )
    return lines


def run() -> None:
    if not C.DB_PATH.exists():
        sys.exit("No database. Run fetch + classify first.")
    con = duckdb.connect(str(C.DB_PATH))
    date = snapshot_date(con)
    fresh = snapshot_rows(con, date)
    con.close()

    history = [r for r in load_history() if r["date"] != date] + fresh
    write_history(history)
    dates = sorted({r["date"] for r in history})
    print(f"Wrote {HISTORY_PATH.name}: {len(dates)} snapshot(s), latest {date}.")

    ALERT_PATH.unlink(missing_ok=True)
    alerts = check_alert(history, date)
    if alerts:
        ALERT_PATH.write_text(
            "Agent-ops hiring demand crossed the alert threshold.\n\n"
            + "\n".join(alerts)
            + "\n\nSee data/history.csv and the dashboard trend section.\n"
        )
        print(f"ALERT written to {ALERT_PATH.name}:")
        for line in alerts:
            print(f"  {line}")


if __name__ == "__main__":
    run()
