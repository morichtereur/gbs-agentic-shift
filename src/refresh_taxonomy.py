"""Refresh deterministic labels without making any model/API calls."""

from __future__ import annotations

import duckdb

from src import config as C
from src.taxonomy import classify_text


def run() -> None:
    con = duckdb.connect(str(C.DB_PATH))
    rows = con.execute("SELECT id, title, description FROM postings ORDER BY id").fetchall()
    refreshed = 0
    preserved_model = 0
    for pid, title, description in rows:
        result = classify_text(f"{title} {description}")
        if result.ambiguous:
            preserved_model += 1
            continue
        row = result.to_row()
        con.execute(
            """INSERT OR REPLACE INTO labels
               (id, label, source, score_transactional, score_judgment,
                score_agent_ops, hits, reason)
               VALUES (?, ?, 'taxonomy', ?, ?, ?, ?, '')""",
            [pid, result.label, row["score_transactional"],
             row["score_judgment"], row["score_agent_ops"], row["hits"]],
        )
        refreshed += 1
    con.close()
    print(f"Refreshed {refreshed} deterministic labels; preserved {preserved_model} ambiguous/model labels.")


if __name__ == "__main__":
    run()
