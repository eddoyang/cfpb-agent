"""Fetch and clean CFPB complaints that include a consumer narrative.

IMPORTANT: on 2026-08-14 the CFPB stopped publishing complaint narratives. The live
API and the current bulk download (complaints.csv.zip) no longer contain them. All
narratives published up to that date are in the CFPB's official FOIA archive:
https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/

Sources, same output:
  1. Narratives archive (recommended): download one or more CCDB_Export_*.zip files into
     a folder and pass --complaints-csv <folder>. ZIPs are read directly.
  2. Any CSV, ZIP of CSVs, or folder of them that has a narrative column.
  3. CFPB search API: kept for reference; it no longer returns narratives and may 403.

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
import zipfile
from pathlib import Path

import pandas as pd
import requests

import config
from ingest.tokens import count_tokens, truncate_tokens

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.consumerfinance.gov/data-research/consumer-complaints/search/",
}
PAGE_SIZE = 100

COLUMNS = [
    "complaint_id",
    "date_received",
    "product",
    "sub_product",
    "issue",
    "sub_issue",
    "company",
    "state",
    "submitted_via",
    "company_response",
    "timely",
    "narrative",
]

# Our column name -> header names seen in CFPB files. The bulk CSV uses human labels
# ("Date received"); API-style exports use field names ("date_received"). Matching
# ignores case, spaces and punctuation.
COLUMN_ALIASES = {
    "complaint_id": ["Complaint ID", "complaint_id"],
    "date_received": ["Date received", "date_received"],
    "product": ["Product"],
    "sub_product": ["Sub-product", "sub_product"],
    "issue": ["Issue"],
    "sub_issue": ["Sub-issue", "sub_issue"],
    "company": ["Company"],
    "state": ["State"],
    "submitted_via": ["Submitted via", "submitted_via"],
    "company_response": ["Company response to consumer", "company_response"],
    "timely": ["Timely response?", "timely"],
    "narrative": [
        "Consumer complaint narrative",
        "complaint_what_happened",
        "Complaint narrative",
        "Narrative",
        "What happened",
    ],
}
REQUIRED_COLUMNS = {"complaint_id", "date_received", "product", "narrative"}


def _norm(name) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def resolve_columns(header) -> dict[str, str]:
    """Map a file's header names to our column names; explain clearly if any are missing."""
    lookup = {_norm(h): h for h in header}
    mapping: dict[str, str] = {}
    for ours, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if _norm(alias) in lookup:
                mapping[lookup[_norm(alias)]] = ours
                break
    if "narrative" not in mapping.values():
        for h in header:
            if "narrative" in _norm(h) or "whathappened" in _norm(h):
                mapping[h] = "narrative"
                break
    missing = REQUIRED_COLUMNS - set(mapping.values())
    if missing:
        hint = ""
        if "narrative" in missing:
            hint = (
                " This file has no complaint narrative text, which the system needs. "
                "Use the bulk file https://files.consumerfinance.gov/ccdb/complaints.csv.zip, "
                "which includes the 'Consumer complaint narrative' column."
            )
        raise ValueError(
            f"CSV is missing required columns {sorted(missing)}. "
            f"Columns found: {list(header)}.{hint}"
        )
    return mapping


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
    text = re.sub(r"\{\$([\d,]+\.?\d*)\}", r"$\1", text)  # CFPB wraps amounts as {$500.00}
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
        except requests.RequestException as e:
            if attempt == 3:
                raise
            wait = 2**attempt
            print(f"    Network error ({e}); retrying in {wait}s")
            time.sleep(wait)
            continue
        if r.status_code in (401, 403):
            raise RuntimeError(
                f"CFPB API refused the request ({r.status_code}). Use the bulk file instead: "
                "python -m ingest.run --only complaints "
                "--complaints-csv data/raw/complaints.csv.zip (see README)"
            )
        if r.status_code >= 500 and attempt < 3:
            wait = 2**attempt
            print(f"    CFPB server error {r.status_code}; retrying in {wait}s")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    return {}


def discover_products() -> list[str]:
    data = _get(
        {
            "has_narrative": "true",
            "date_received_min": config.COMPLAINTS_SINCE,
            "size": 1,
        }
    )
    buckets = _find_buckets(data.get("aggregations", {}), "product") or []
    names = [b["key"] for b in buckets]
    keep = [n for n in names if reg_hint_for(n)]
    print(f"  CFPB products matched: {keep}")
    return keep


def fetch_product(product: str, limit: int) -> list[dict]:
    rows, frm = [], 0
    while len(rows) < limit:
        data = _get(
            {
                "product": product,
                "has_narrative": "true",
                "date_received_min": config.COMPLAINTS_SINCE,
                "size": PAGE_SIZE,
                "frm": frm,
                "sort": "created_date_desc",
                "no_aggs": "true",
            }
        )
        hits = data.get("hits", {}).get("hits", []) if isinstance(data, dict) else data
        if not hits:
            break
        for h in hits:
            s = h.get("_source", h)
            rows.append(
                {
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
                }
            )
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
def _csv_sources(path: Path) -> list[tuple[str, object]]:
    """Expand a path into (label, opener) pairs, one per CSV to read.

    Accepts a CSV file, a ZIP containing one or more CSVs (e.g. the CFPB narratives
    archive exports), or a folder holding any mix of CSVs and ZIPs.
    """
    if path.is_dir():
        files = sorted(p for p in path.iterdir() if p.suffix.lower() in {".csv", ".zip"})
        if not files:
            raise FileNotFoundError(f"No .csv or .zip files found in {path}")
        return [src for f in files for src in _csv_sources(f)]
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            members = [
                m
                for m in zf.namelist()
                if m.lower().endswith(".csv") and not m.startswith("__MACOSX")
            ]
            if not members:
                raise ValueError(f"{path.name} contains no CSV files. Contents: {zf.namelist()}")
        return [
            (f"{path.name}:{m}", lambda p=path, m=m: zipfile.ZipFile(p).open(m)) for m in members
        ]
    return [(path.name, lambda p=path: open(p, "rb"))]


def load_from_csv(path: Path, per_product: int) -> pd.DataFrame:
    """Read CFPB complaint CSVs in chunks; filter and sample.

    `path` may be a CSV, a ZIP of CSVs (bulk file or narratives archive), or a folder
    of either. See _csv_sources.
    """
    sources = _csv_sources(Path(path))
    since = pd.Timestamp(config.COMPLAINTS_SINCE)
    frames = []
    for label, opener in sources:
        with opener() as fh:
            mapping = resolve_columns(pd.read_csv(fh, nrows=0).columns)
        with opener() as fh:
            reader = pd.read_csv(fh, usecols=list(mapping), dtype=str, chunksize=200_000)
            frames += list(_filter_chunks(reader, mapping, since))
        print(f"  Read {label}")
    return _sample(frames, per_product)


def _filter_chunks(reader, mapping: dict, since: pd.Timestamp):
    for chunk in reader:
        chunk = chunk.rename(columns=mapping)
        for col in COLUMNS:  # optional columns this file doesn't have
            if col not in chunk:
                chunk[col] = None
        chunk = chunk[chunk["narrative"].notna() & (chunk["narrative"].str.strip() != "")]
        # Parse dates rather than compare strings: exports differ in date format.
        dates = pd.to_datetime(chunk["date_received"], errors="coerce", format="mixed")
        chunk = chunk[dates >= since]
        chunk = chunk[chunk["product"].map(lambda p: reg_hint_for(p) is not None)]
        yield chunk


def _sample(frames: list[pd.DataFrame], per_product: int) -> pd.DataFrame:
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=COLUMNS)
    df = df.drop_duplicates(subset="complaint_id")  # archive periods can overlap
    if df.empty:
        raise ValueError(
            "No complaints left after filtering (narrative, date, product). "
            "Check the CSV covers the products and dates in config.py."
        )
    # Balanced, reproducible sample per product: shuffle once, keep the first N per group.
    df = df.sample(frac=1, random_state=42).groupby("product").head(per_product)
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
    print(
        f"  Cleaning: {start} -> {len(df)} complaints "
        f"(dropped {start - len(df)} short/duplicate/invalid)"
    )
    return df.reset_index(drop=True)


def build_complaints(
    per_product: int = config.COMPLAINTS_PER_PRODUCT, csv_path: Path | None = None
) -> pd.DataFrame:
    df = load_from_csv(csv_path, per_product) if csv_path else fetch_from_api(per_product)
    df = clean_complaints(df)
    out = config.PROCESSED_DIR / "complaints.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"Wrote {len(df)} complaints to {out}")
    print(df["product"].value_counts().to_string())
    return df