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
                   l.label,
                   row_number() OVER (
                       PARTITION BY p.country, (l.label = 'agent_ops')
                       ORDER BY md5(p.id)
                   ) AS sample_rank
            FROM postings p
            JOIN labels l ON l.id = p.id
            WHERE p.country IN ('de', 'gb', 'in', 'nl', 'pl', 'za')
              AND l.label != 'none'
        )
        SELECT id, country, title, description, label
        FROM ranked
        WHERE sample_rank <= ?
        ORDER BY country, (label = 'agent_ops') DESC, id
        """,
        [PER_COUNTRY],
    ).fetchall()
    con.close()

    selected = []
    by_country = {}
    for row in rows:
        by_country.setdefault(row[1], []).append(row)
    for country in COUNTRIES:
        candidates = by_country.get(country, [])
        selected.extend(candidates[:PER_COUNTRY])
    selected = selected[:PER_COUNTRY * len(COUNTRIES)]

    OUT.write_text(
        "\n".join(
            json.dumps(
                {"id": pid, "country": country,
                 "text": f"{title} {description}", "gold": ""},
                ensure_ascii=True,
            )
            for pid, country, title, description, _ in selected
        )
        + "\n"
    )
    print(f"Wrote {OUT} ({len(selected)} unlabeled postings).")
    print("Fill gold with transactional, judgment, agent_ops, or none.")
    print("Then copy to eval/labels_country.jsonl and evaluate it separately.")


if __name__ == "__main__":
    run()
