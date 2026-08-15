"""Central config. All secrets come from the environment — nothing is hardcoded."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DB_PATH = DATA / "postings.duckdb"

# Adzuna — free tier, legal, covers de/gb (ch coverage is thin, see README).
# Register at https://developer.adzuna.com/ for app_id + app_key.
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")

# Countries to pull. Adzuna uses ISO-ish codes: de, gb, us, fr, ...
COUNTRIES = os.getenv("GBS_COUNTRIES", "de,gb").split(",")

# Search terms that surface GBS / finance-operations postings.
SEARCH_TERMS = [
    "global business services",
    "shared services finance",
    "finance operations",
    "record to report",
    "procure to pay",
    "order to cash",
]

# Claude — only used for the ambiguous residual the taxonomy can't decide.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLASSIFIER_MODEL = os.getenv("CLASSIFIER_MODEL", "claude-sonnet-5")
RECLASSIFY = os.getenv("GBS_RECLASSIFY", "0").lower() in {"1", "true", "yes"}

RESULTS_PER_PAGE = 50
MAX_PAGES = int(os.getenv("GBS_MAX_PAGES", "5"))  # 5 pages x 50 x terms x countries
