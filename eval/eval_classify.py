"""
Eval the deterministic taxonomy against a hand-labelled gold set.

This is the number that makes the headline defensible: the taxonomy is a
*constructed* metric, so its accuracy is measured, not assumed. Reports overall
accuracy plus per-family precision/recall so you can see WHERE it's weak
(usually: judgment vs agent_ops overlap).

Gold set format (JSONL), one posting per line:
    {"text": "<title + description>", "gold": "transactional|judgment|agent_ops"}

Start from eval/labels.sample.jsonl, then replace it with your own hand labels
(aim for >=60 postings, balanced across families) as eval/labels.jsonl.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from src.taxonomy import classify_text

HERE = Path(__file__).resolve().parent
GOLD = HERE / "labels.jsonl"
SAMPLE = HERE / "labels.sample.jsonl"
FAMILIES = ["transactional", "judgment", "agent_ops"]


def load(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def run() -> None:
    path = GOLD if GOLD.exists() else SAMPLE
    data = load(path)
    print(f"Gold set: {path.name}  (n={len(data)})\n")

    correct = 0
    tp = defaultdict(int); fp = defaultdict(int); fn = defaultdict(int)
    confusion = defaultdict(lambda: defaultdict(int))

    for row in data:
        pred = classify_text(row["text"]).label
        gold = row["gold"]
        confusion[gold][pred] += 1
        if pred == gold:
            correct += 1
            tp[gold] += 1
        else:
            fp[pred] += 1
            fn[gold] += 1

    acc = correct / len(data) if data else 0
    print(f"Overall accuracy: {acc:.1%}  ({correct}/{len(data)})\n")
    print(f"{'family':14} {'precision':>10} {'recall':>8}")
    for f in FAMILIES:
        prec = tp[f] / (tp[f] + fp[f]) if (tp[f] + fp[f]) else 0
        rec = tp[f] / (tp[f] + fn[f]) if (tp[f] + fn[f]) else 0
        print(f"{f:14} {prec:>10.1%} {rec:>8.1%}")

    print("\nConfusion (rows = gold, cols = predicted):")
    header = "gold\\pred     " + "".join(f"{p[:11]:>13}" for p in FAMILIES + ["ambiguous"])
    print(header)
    for g in FAMILIES:
        line = f"{g:14}"
        for p in FAMILIES + ["ambiguous"]:
            line += f"{confusion[g][p]:>13}"
        print(line)


if __name__ == "__main__":
    run()
