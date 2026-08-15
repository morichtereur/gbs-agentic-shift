"""Build a balanced, unlabeled worksheet for the taxonomy gold set.

The worksheet is intentionally not an evaluation fixture. Fill each empty
``gold`` value by reading the posting, then copy it to ``eval/labels.jsonl``.
Existing model labels are used only to balance the sample, never as labels.
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from src import config as C


OUT = Path(__file__).resolve().parent / "labels.todo.jsonl"
GOLD = Path(__file__).resolve().parent / "labels.jsonl"

# Manual review labels for the 60-posting validation sample. These are kept
# separate from the model labels in DuckDB; changing the taxonomy must never
# silently rewrite this reference set.
GOLD_LABELS = {
    "5822114785": "judgment", "5837169817": "judgment", "5792269936": "judgment",
    "5822284825": "transactional", "5842044591": "judgment", "5801355754": "transactional",
    "5843085557": "judgment", "5210480967": "judgment", "5804565169": "judgment",
    "5823210142": "judgment", "5831646065": "none", "5821646580": "transactional",
    "5826818395": "judgment", "5843314100": "judgment", "5835234350": "judgment",
    "5722146736": "agent_ops", "5728469474": "agent_ops", "5806167908": "judgment",
    "5830568324": "judgment", "5819785350": "judgment", "5727295694": "judgment",
    "5210485821": "transactional", "5210489357": "transactional", "5819990707": "transactional",
    "5802976075": "judgment", "5831400621": "judgment", "5835552726": "none",
    "5210487028": "transactional", "5210487811": "transactional", "5210487675": "transactional",
    "5210487979": "transactional", "5295888964": "transactional", "5816459704": "transactional",
    "5210480180": "transactional", "5831513937": "judgment", "5829115820": "transactional",
    "5210487966": "transactional", "5810553326": "judgment", "5210487669": "transactional",
    "5295888654": "transactional", "5799918756": "transactional", "5803014479": "agent_ops",
    "5818981920": "judgment", "5787279150": "agent_ops", "5730793369": "agent_ops",
    "5838652687": "agent_ops", "4575281117": "agent_ops", "5809414040": "agent_ops",
    "5787145466": "agent_ops", "5819997737": "agent_ops", "5819873214": "agent_ops",
    "5759148302": "agent_ops", "5804573598": "agent_ops", "5779387958": "agent_ops",
    "5831339399": "none", "5836767198": "judgment", "5832307492": "judgment",
    "5808131961": "judgment", "5831948720": "transactional", "5771796773": "judgment",
}


def run() -> None:
    con = duckdb.connect(str(C.DB_PATH), read_only=True)
    ids = ", ".join(f"'{pid}'" for pid in GOLD_LABELS)
    rows = con.execute("""
        SELECT p.id, p.title, p.description, l.label
        FROM postings p JOIN labels l ON l.id = p.id
        WHERE p.id IN (""" + ids + ") ORDER BY md5(p.id)""").fetchall()
    con.close()

    selected = rows[:60]

    worksheet = [
        {"id": pid, "text": f"{title} {description}", "gold": ""}
        for pid, title, description, _ in selected
    ]
    OUT.write_text(
        "\n".join(
            json.dumps(row, ensure_ascii=True) for row in worksheet
        )
        + "\n"
    )
    gold_rows = [row | {"gold": GOLD_LABELS[row["id"]]} for row in worksheet]
    GOLD.write_text("\n".join(json.dumps(row, ensure_ascii=True) for row in gold_rows) + "\n")
    print(f"Wrote {OUT} ({len(selected)} unlabeled postings).")
    print(f"Wrote {GOLD} ({len(gold_rows)} reviewed postings).")
    print("Fill gold with transactional, judgment, or agent_ops, then copy to eval/labels.jsonl.")


if __name__ == "__main__":
    run()