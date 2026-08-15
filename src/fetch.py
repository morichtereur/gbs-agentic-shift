"""
Pull live GBS / finance-operations postings from the Adzuna API into DuckDB.

Adzuna is a legal, keyed job-search API (no scraping, no ToS grey zone). The
important limitation: the search endpoint returns CURRENT live postings only,
so this produces a point-in-time cross-section, not a historical trend. That is
a deliberate v1 scope decision — see README.

Idempotent: postings are keyed on Adzuna id, so re-running upserts rather than
duplicating.
"""

from __future__ import annotations

import sys
import time
import requests
import duckdb

from src import config as C


API = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"


def _init_db(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS postings (
            id           VARCHAR PRIMARY KEY,
            country      VARCHAR,
            term         VARCHAR,
            title        VARCHAR,
            company      VARCHAR,
            description  VARCHAR,
            category     VARCHAR,
            created      VARCHAR,
            redirect_url VARCHAR
        )
    """)


def _fetch_page(country: str, term: str, page: int) -> list[dict]:
    url = API.format(country=country.strip(), page=page)
    params = {
        "app_id": C.ADZUNA_APP_ID,
        "app_key": C.ADZUNA_APP_KEY,
        "what": term,
        "results_per_page": C.RESULTS_PER_PAGE,
        "content-type": "application/json",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("results", [])


def run() -> int:
    if not (C.ADZUNA_APP_ID and C.ADZUNA_APP_KEY):
        sys.exit("Set ADZUNA_APP_ID and ADZUNA_APP_KEY (see .env.example).")

    C.DATA.mkdir(exist_ok=True)
    con = duckdb.connect(str(C.DB_PATH))
    _init_db(con)

    inserted = 0
    for country in C.COUNTRIES:
        for term in C.SEARCH_TERMS:
            for page in range(1, C.MAX_PAGES + 1):
                try:
                    results = _fetch_page(country, term, page)
                except requests.HTTPError as e:
                    print(f"  ! {country}/{term} p{page}: {e}")
                    break
                if not results:
                    break
                for j in results:
                    con.execute(
                        """INSERT OR REPLACE INTO postings VALUES (?,?,?,?,?,?,?,?,?)""",
                        [
                            str(j.get("id")),
                            country.strip(),
                            term,
                            j.get("title", ""),
                            (j.get("company") or {}).get("display_name", ""),
                            j.get("description", ""),
                            (j.get("category") or {}).get("label", ""),
                            j.get("created", ""),
                            j.get("redirect_url", ""),
                        ],
                    )
                    inserted += 1
                print(f"  {country}/{term:28} p{page}: {len(results)} rows")
                time.sleep(0.3)  # be polite to the API

    total = con.execute("SELECT count(*) FROM postings").fetchone()[0]
    con.close()
    print(f"\nUpserted {inserted} rows. Table now holds {total} distinct postings.")
    return total


if __name__ == "__main__":
    run()
