"""Build a country-stratified, unlabeled worksheet for manual review.

This deliberately creates a worksheet, not gold labels. Review each posting and
write the completed file to ``eval/labels_country.jsonl`` before evaluating.
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from src import config as C


OUT = Path(__file__).resolve().parent / "labels_country.todo.jsonl"
COUNTRIES = ("de", "gb", "in", "nl", "pl", "za")
PER_COUNTRY = 10


def run() -> None:
    con = duckdb.connect(str(C.DB_PATH), read_only=True)
    rows = con.execute(
        """
        WITH ranked AS (
            SELECT p.id, p.country, p.title, p.description,
                   row_number() OVER (
                       PARTITION BY p.country ORDER BY md5(p.id)
                   ) AS sample_rank
            FROM postings p
            JOIN labels l ON l.id = p.id
            WHERE p.country IN ('de', 'gb', 'in', 'nl', 'pl', 'za')
              AND l.label != 'none'
        )
        SELECT id, country, title, description
        FROM ranked
        WHERE sample_rank <= ?
        ORDER BY country, id
        """,
        [PER_COUNTRY],
    ).fetchall()
    con.close()

    OUT.write_text(
        "\n".join(
            json.dumps(
                {"id": pid, "country": country,
                 "text": f"{title} {description}", "gold": ""},
                ensure_ascii=True,
            )
            for pid, country, title, description in rows
        )
        + "\n"
    )
    print(f"Wrote {OUT} ({len(rows)} unlabeled postings).")
    print("Fill gold with transactional, judgment, agent_ops, or none.")
    print("Then copy to eval/labels_country.jsonl and evaluate it separately.")


if __name__ == "__main__":
    run()
