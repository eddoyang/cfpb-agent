"""Fetch and clean CFPB complaints that include a consumer narrative.

Two sources, same output:
  1. CFPB search API (default): pulls a balanced sample per product.
  2. Bulk CSV fallback: if you downloaded complaints.csv from
     https://files.consumerfinance.gov/ccdb/complaints.csv.zip into data/raw/,
     pass --complaints-csv and nothing hits the API.

Data quality steps (the interview talking point):
  * Keep only complaints whose narrative the consumer consented to publish.
  * CFPB already scrubs PII to 'XXXX'; we normalise it to [REDACTED] / [DATE]
    so the embedding doesn't cluster complaints by redaction pattern.
  * Drop near-empty narratives (< 30 words) and exact duplicates (template spam).
  * Truncate very long narratives before embedding (cost + 8k token limit).
"""
from __future__ import annotations

import re
import time
from pathlib import Path

import pandas as pd
import requests

import config
from ingest.tokens import count_tokens, truncate_tokens

HEADERS = {"User-Agent": "cfpb-agent-demo/0.1 (educational project)"}
PAGE_SIZE = 100

COLUMNS = [
    "complaint_id", "date_received", "product", "sub_product", "issue", "sub_issue",
    "company", "state", "submitted_via", "company_response", "timely", "narrative",
]

# Bulk CSV header -> our column names
CSV_RENAME = {
    "Complaint ID": "complaint_id",
    "Date received": "date_received",
    "Product": "product",
    "Sub-product": "sub_product",
    "Issue": "issue",
    "Sub-issue": "sub_issue",
    "Company": "company",
    "State": "state",
    "Submitted via": "submitted_via",
    "Company response to consumer": "company_response",
    "Timely response?": "timely",
    "Consumer complaint narrative": "narrative",
}


# ---------------------------------------------------------------- helpers
def reg_hint_for(product: str) -> str | None:
    p = (product or "").lower()
    for rule in config.PRODUCT_RULES:
        if rule["keyword"] in p:
            return rule["reg_hint"]
    return None


def clean_narrative(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"\bXX/XX/(XXXX|\d{2,4})\b", "[DATE]", text)
    text = re.sub(r"\bX{2,}\b", "[REDACTED]", text)
    text = re.sub(r"(\[REDACTED\]\s*){2,}", "[REDACTED] ", text)
    text = re.sub(r"\{\$([\d,]+\.?\d*)\}", r"$\1", text)   # CFPB wraps amounts as {$500.00}
    return re.sub(r"\s+", " ", text).strip()


def _find_buckets(obj, name: str):
    """Aggregation JSON nests buckets a variable depth; find them by key name."""
    if isinstance(obj, dict):
        if name in obj and isinstance(obj[name], dict):
            inner = obj[name]
            if "buckets" in inner:
                return inner["buckets"]
            found = _find_buckets(inner, name)
            if found is not None:
                return found
        for v in obj.values():
            found = _find_buckets(v, name)
            if found is not None:
                return found
    return None


# ---------------------------------------------------------------- API source
def _get(params: dict) -> dict:
    for attempt in range(4):
        try:
            r = requests.get(config.CFPB_API, params=params, headers=HEADERS, timeout=90)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt == 3:
                raise
            wait = 2 ** attempt
            print(f"    API error ({e}); retrying in {wait}s")
            time.sleep(wait)
    return {}


def discover_products() -> list[str]:
    data = _get({
        "has_narrative": "true",
        "date_received_min": config.COMPLAINTS_SINCE,
        "size": 1,
    })
    buckets = _find_buckets(data.get("aggregations", {}), "product") or []
    names = [b["key"] for b in buckets]
    keep = [n for n in names if reg_hint_for(n)]
    print(f"  CFPB products matched: {keep}")
    return keep


def fetch_product(product: str, limit: int) -> list[dict]:
    rows, frm = [], 0
    while len(rows) < limit:
        data = _get({
            "product": product,
            "has_narrative": "true",
            "date_received_min": config.COMPLAINTS_SINCE,
            "size": PAGE_SIZE,
            "frm": frm,
            "sort": "created_date_desc",
            "no_aggs": "true",
        })
        hits = data.get("hits", {}).get("hits", []) if isinstance(data, dict) else data
        if not hits:
            break
        for h in hits:
            s = h.get("_source", h)
            rows.append({
                "complaint_id": s.get("complaint_id"),
                "date_received": s.get("date_received"),
                "product": s.get("product"),
                "sub_product": s.get("sub_product"),
                "issue": s.get("issue"),
                "sub_issue": s.get("sub_issue"),
                "company": s.get("company"),
                "state": s.get("state"),
                "submitted_via": s.get("submitted_via"),
                "company_response": s.get("company_response"),
                "timely": s.get("timely"),
                "narrative": s.get("complaint_what_happened"),
            })
        frm += PAGE_SIZE
        time.sleep(0.3)  # be polite to a public API
    return rows[:limit]


def fetch_from_api(per_product: int) -> pd.DataFrame:
    cache = config.RAW_DIR / f"cfpb_api_{config.COMPLAINTS_SINCE}_{per_product}.parquet"
    if cache.exists():
        print(f"  Using cached API pull {cache.name}")
        return pd.read_parquet(cache)
    rows = []
    for product in discover_products():
        got = fetch_product(product, per_product)
        print(f"  {product}: {len(got)} complaints")
        rows.extend(got)
    df = pd.DataFrame(rows, columns=COLUMNS)
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache, index=False)
    return df


# ---------------------------------------------------------------- CSV source
def load_from_csv(path: Path, per_product: int) -> pd.DataFrame:
    frames = []
    for chunk in pd.read_csv(path, usecols=list(CSV_RENAME), dtype=str, chunksize=200_000):
        chunk = chunk.rename(columns=CSV_RENAME)
        chunk = chunk[chunk["narrative"].notna()]
        chunk = chunk[chunk["date_received"] >= config.COMPLAINTS_SINCE]
        chunk = chunk[chunk["product"].map(lambda p: reg_hint_for(p) is not None)]
        frames.append(chunk)
    df = pd.concat(frames, ignore_index=True)
    # Balanced, reproducible sample per product
    df = (df.groupby("product", group_keys=False)
            .apply(lambda g: g.sample(min(len(g), per_product), random_state=42)))
    return df[COLUMNS]


# ---------------------------------------------------------------- cleaning
def clean_complaints(df: pd.DataFrame) -> pd.DataFrame:
    start = len(df)
    df = df.copy()
    df["narrative"] = df["narrative"].map(clean_narrative)
    df = df[df["narrative"].str.split().str.len() >= 30]
    df = df.drop_duplicates(subset="narrative")
    df = df.drop_duplicates(subset="complaint_id")
    df["complaint_id"] = pd.to_numeric(df["complaint_id"], errors="coerce")
    df = df[df["complaint_id"].notna()]
    df["complaint_id"] = df["complaint_id"].astype("int64")
    df["date_received"] = pd.to_datetime(df["date_received"], errors="coerce", utc=True).dt.date
    df["timely"] = df["timely"].map(lambda v: str(v).strip().lower() in {"yes", "true"})
    df["reg_hint"] = df["product"].map(reg_hint_for)
    df["narrative"] = df["narrative"].map(lambda t: truncate_tokens(t, config.COMPLAINT_MAX_TOKENS))
    df["token_count"] = df["narrative"].map(count_tokens)
    print(f"  Cleaning: {start} -> {len(df)} complaints "
          f"(dropped {start - len(df)} short/duplicate/invalid)")
    return df.reset_index(drop=True)


def build_complaints(per_product: int = config.COMPLAINTS_PER_PRODUCT,
                     csv_path: Path | None = None) -> pd.DataFrame:
    df = load_from_csv(csv_path, per_product) if csv_path else fetch_from_api(per_product)
    df = clean_complaints(df)
    out = config.PROCESSED_DIR / "complaints.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"Wrote {len(df)} complaints to {out}")
    print(df["product"].value_counts().to_string())
    return df
