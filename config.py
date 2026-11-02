"""Central configuration. Every tunable lives here so experiments are one-line changes."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# --- Models ---------------------------------------------------------------
# Small/fast tier: classification + supervisor routing
FAST_MODEL = os.getenv("FAST_MODEL", "claude-haiku-5-5")
# Strong tier: drafting + verification
STRONG_MODEL = os.getenv("STRONG_MODEL", "claude-sonnet-5-5")

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
CFPB_API = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"

# Regulations we ingest (Title 12 parts) -> short name
REGULATIONS = {
    "1005": "Regulation E (Electronic Fund Transfers)",
    "1006": "Regulation F (Debt Collection Practices)",
    "1026": "Regulation Z (Truth in Lending)",
}

# Complaint products we keep, matched by keyword against CFPB product names
# (CFPB has renamed products over time, so we match loosely), and the
# regulation each one most often maps to.
PRODUCT_RULES = [
    {"keyword": "credit card", "reg_hint": "1026"},
    {"keyword": "checking or savings", "reg_hint": "1005"},
    {"keyword": "money transfer", "reg_hint": "1005"},
    {"keyword": "prepaid", "reg_hint": "1005"},
    {"keyword": "debt collection", "reg_hint": "1006"},
]
COMPLAINTS_PER_PRODUCT = 1200
COMPLAINTS_SINCE = "2023-01-01"

# --- Chunking -------------------------------------------------------------
REG_CHUNK_MAX_TOKENS = 700  # regulation chunks, split on paragraph boundaries
COMPLAINT_MAX_TOKENS = 1500  # long narratives are truncated before embedding

# --- LLM settings ----------------------------------------------------------
# Claude 5.5-generation models (Haiku and Sonnet) reject a custom temperature, so by
# default none is sent and each model runs at its default. Run-to-run variation is
# measured instead (eval --repeats). Set LLM_TEMPERATURE=0 only for models that accept it.
_temp = os.getenv("LLM_TEMPERATURE", "none")
LLM_TEMPERATURE = None if _temp.lower() == "none" else float(_temp)
MODELS_WITHOUT_TEMPERATURE = ("claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5")
LLM_TIMEOUT_S = 90
LLM_MAX_RETRIES = 2
MAX_OUTPUT_TOKENS = {"fast": 1024, "strong": 2048}

# USD per 1M tokens (input, output). PLACEHOLDERS: confirm against
# https://claude.com/pricing and https://openai.com/api/pricing before quoting costs.
MODEL_PRICES = {
    FAST_MODEL: (
        float(os.getenv("FAST_PRICE_IN", "1.00")),
        float(os.getenv("FAST_PRICE_OUT", "5.00")),
    ),
    STRONG_MODEL: (
        float(os.getenv("STRONG_PRICE_IN", "3.00")),
        float(os.getenv("STRONG_PRICE_OUT", "15.00")),
    ),
}
EMBED_PRICE_PER_1M = float(os.getenv("EMBED_PRICE", "0.02"))

# --- Product taxonomy (classifier output -> data filters) -----------------
PRODUCT_CATEGORIES = {
    "credit_card": {"keyword": "credit card", "parts": ["1026"]},
    "checking_savings": {"keyword": "checking or savings", "parts": ["1005"]},
    "money_transfer": {"keyword": "money transfer", "parts": ["1005"]},
    "prepaid_card": {"keyword": "prepaid", "parts": ["1005"]},
    "debt_collection": {"keyword": "debt collection", "parts": ["1006"]},
    "other": {"keyword": None, "parts": []},
}

# --- Retrieval ------------------------------------------------------------
# Cosine-similarity floors. text-embedding-3-small scores run lower than people
# expect (relevant hits are often 0.35-0.6). CALIBRATE after ingestion with
# `python -m eval.harness`, which reports the score distribution.
REG_MIN_SCORE = float(os.getenv("REG_MIN_SCORE", "0.30"))
CASE_MIN_SCORE = float(os.getenv("CASE_MIN_SCORE", "0.30"))
HNSW_EF_SEARCH = 100

# --- Workflow stopping conditions -----------------------------------------
MAX_REDRAFTS = 2  # static: verify failures before escalating
MAX_SUPERVISOR_STEPS = 6  # dynamic: hard cap on worker calls
MAX_REPLANS = 1  # dynamic: re-plans after a failed verification
MAX_CONSECUTIVE_ERRORS = 2  # dynamic: tool failures in a row before escalating
RECURSION_LIMIT = 40  # LangGraph safety net on top of the caps above
