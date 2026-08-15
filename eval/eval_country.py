"""Evaluate a completed country-stratified gold set.

Expected input: eval/labels_country.jsonl with id, country, text, and gold.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from src.taxonomy import classify_text


GOLD = Path(__file__).resolve().parent / "labels_country.jsonl"


def run() -> None:
    if not GOLD.exists():
        raise SystemExit("Create eval/labels_country.jsonl from labels_country.todo.jsonl first.")
    rows = [json.loads(line) for line in GOLD.read_text().splitlines() if line.strip()]
    confusion = defaultdict(Counter)
    for row in rows:
        confusion[row["country"]][(row["gold"], classify_text(row["text"]).label)] += 1

    correct = sum(
        n for country in confusion.values()
        for (gold, pred), n in country.items() if gold == pred
    )
    print(f"Overall accuracy: {correct / len(rows):.1%} ({correct}/{len(rows)})")
    print(f"{'country':10} {'n':>4} {'accuracy':>10} {'agent_ops recall':>17}")
    for country in sorted(confusion):
        counts = confusion[country]
        n = sum(counts.values())
        acc = sum(v for (gold, pred), v in counts.items() if gold == pred) / n
        agent_total = sum(v for (gold, _), v in counts.items() if gold == "agent_ops")
        agent_hit = counts[("agent_ops", "agent_ops")]
        recall = agent_hit / agent_total if agent_total else 0
        print(f"{country:10} {n:4} {acc:10.1%} {recall:17.1%}")


if __name__ == "__main__":
    run()
