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


def run() -> None:
    con = duckdb.connect(str(C.DB_PATH), read_only=True)
    rows = con.execute("""
        WITH ranked AS (
            SELECT
                p.id,
                p.title,
                p.description,
                l.label AS sampling_bucket,
                row_number() OVER (
                    PARTITION BY l.label ORDER BY md5(p.id)
                ) AS sample_rank
            FROM postings p
            JOIN labels l ON l.id = p.id
            WHERE l.label IN ('transactional', 'judgment', 'agent_ops')
        )
        SELECT id, title, description, sampling_bucket
        FROM ranked
        ORDER BY sample_rank <= 20 DESC, md5(id)
    """).fetchall()
    con.close()

    selected = rows[:60]

    OUT.write_text(
        "\n".join(
            json.dumps(
                {"id": pid, "text": f"{title} {description}", "gold": ""},
                ensure_ascii=True,
            )
            for pid, title, description, _ in selected
        )
        + "\n"
    )
    print(f"Wrote {OUT} ({len(selected)} unlabeled postings).")
    print("Fill gold with transactional, judgment, or agent_ops, then copy to eval/labels.jsonl.")


if __name__ == "__main__":
    run()