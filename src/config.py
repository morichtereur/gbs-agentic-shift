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
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY", "")
JOOBLE_REQUEST_LIMIT = int(os.getenv("JOOBLE_REQUEST_LIMIT", "500"))
JOOBLE_REQUEST_INTERVAL = float(os.getenv("JOOBLE_REQUEST_INTERVAL", "0.5"))

# Countries to pull. Adzuna uses ISO-ish codes: de, gb, us, fr, ...
# Comparison set: Western Europe, Central/Eastern Europe, and established
# global GBS delivery hubs. Keep the set explicit so geography is reproducible.
ADZUNA_COUNTRIES = os.getenv("ADZUNA_COUNTRIES", "pl,in,mx,nl,de,ch,es,sg").split(",")
JOOBLE_COUNTRIES = os.getenv("JOOBLE_COUNTRIES", "pt,ro,hu,cz").split(",")
COUNTRIES = ADZUNA_COUNTRIES + JOOBLE_COUNTRIES

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
MODEL_WORKERS = int(os.getenv("GBS_MODEL_WORKERS", "3"))
MODEL_REQUEST_INTERVAL = float(os.getenv("GBS_MODEL_REQUEST_INTERVAL", "0.25"))
MODEL_TIMEOUT = float(os.getenv("GBS_MODEL_TIMEOUT", "5"))

RESULTS_PER_PAGE = 50
MAX_PAGES = int(os.getenv("GBS_MAX_PAGES", "5"))  # 5 pages x 50 x terms x countries
