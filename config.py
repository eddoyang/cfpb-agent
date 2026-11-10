"""Central configuration. Every tunable lives here so experiments are one-line changes."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# --- Models ---------------------------------------------------------------
FAST_MODEL = os.getenv("FAST_MODEL", "claude-haiku-5-5") # Small/fast tier: classification + supervisor routing
STRONG_MODEL = os.getenv("STRONG_MODEL", "claude-sonnet-5-5") # Strong tier: drafting + verification


EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))  # must match db/schema.sql
EMBED_BATCH_SIZE = 128

# --- Database -------------------------------------------------------------
PG_DSN = (
    f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
    f"port={os.getenv('POSTGRES_PORT', '5432')} "
    f"dbname={os.getenv('POSTGRES_DB', 'cfpb')} "
    f"user={os.getenv('POSTGRES_USER', 'cfpb')} "
    f"password={os.getenv('POSTGRES_PASSWORD', 'cfpb_local_dev')}"
)

# --- Data sources ---------------------------------------------------------
ECFR_BASE = "https://www.ecfr.gov/api/versioner/v1"

# Regulations we ingest (Title 12 parts) -> short name
REGULATIONS = {
    "1005": "Regulation E (Electronic Fund Transfers)",
    "1006": "Regulation F (Debt Collection Practices)",
    "1026": "Regulation Z (Truth in Lending)",
}

# Classifier product -> keyword matched against CFPB product names (CFPB has renamed
# products over time, so we match loosely) and the regulation parts it maps to.
# Ingest keeps only complaints whose product matches a keyword.
PRODUCT_CATEGORIES = {
    "credit_card": {"keyword": "credit card", "parts": ["1026"]},
    "checking_savings": {"keyword": "checking or savings", "parts": ["1005"]},
    "money_transfer": {"keyword": "money transfer", "parts": ["1005"]},
    "prepaid_card": {"keyword": "prepaid", "parts": ["1005"]},
    "debt_collection": {"keyword": "debt collection", "parts": ["1006"]},
    "other": {"keyword": None, "parts": []},
}
COMPLAINTS_PER_PRODUCT = 1200
COMPLAINTS_SINCE = "2023-01-01"
COMPLAINTS_UNTIL = "2026-08-14"  # the CFPB stopped publishing narratives after this date
COMPLAINTS_SOURCE = RAW_DIR / "cfpb_archive" # Narratives archive (CCDB_Export_*.zip); a CSV, ZIP of CSVs, or folder of either

# --- Chunking -------------------------------------------------------------
REG_CHUNK_MAX_TOKENS = 700  # regulation chunks, split on paragraph boundaries
COMPLAINT_MAX_TOKENS = 1500  # long narratives are truncated before embedding

# --- LLM settings ----------------------------------------------------------
# No temperature is sent: Claude 5.5-generation models reject a custom one, so each runs
# at its default. Run-to-run variation is measured instead (eval --repeats).
LLM_TIMEOUT_S = 90
LLM_MAX_RETRIES = 2
MAX_OUTPUT_TOKENS = {"fast": 1024, "strong": 4096}

# USD per 1M tokens, required in .env (no defaults). Unset prices are None; computing a
# cost with one raises, and preflight reports it.
PRICE_ENV_VARS = (
    "FAST_PRICE_IN",
    "FAST_PRICE_OUT",
    "STRONG_PRICE_IN",
    "STRONG_PRICE_OUT",
    "EMBED_PRICE",
)


def _price(name: str) -> float | None:
    value = os.getenv(name)
    return float(value) if value else None


MODEL_PRICES = {  # model -> (input, output)
    FAST_MODEL: (_price("FAST_PRICE_IN"), _price("FAST_PRICE_OUT")),
    STRONG_MODEL: (_price("STRONG_PRICE_IN"), _price("STRONG_PRICE_OUT")),
}
EMBED_PRICE = _price("EMBED_PRICE")  # embedding model, input only

# --- Retrieval ------------------------------------------------------------
# Cosine-similarity floors. text-embedding-3-small scores run lower than people
# expect (relevant hits are often 0.35-0.6). CALIBRATE after ingestion with
# `python -m eval.harness`, which reports the score distribution.
REG_MIN_SCORE = float(os.getenv("REG_MIN_SCORE", "0.45"))
CASE_MIN_SCORE = float(os.getenv("CASE_MIN_SCORE", "0.30"))
HNSW_EF_SEARCH = 100

# --- Workflow stopping conditions -----------------------------------------
MAX_REDRAFTS = 2  # static: verify failures before escalating
MAX_SUPERVISOR_STEPS = 6  # dynamic: hard cap on worker calls
MAX_REPLANS = 1  # dynamic: re-plans after a failed verification
MAX_CONSECUTIVE_ERRORS = 2  # dynamic: tool failures in a row before escalating
MAX_STALE_SEARCHES = 2  # dynamic: searches in a row that found nothing new -> synthesize
RECURSION_LIMIT = 40  # LangGraph safety net on top of the caps above
