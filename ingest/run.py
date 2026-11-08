"""Ingestion CLI.

python -m ingest.run                       # regs from eCFR + complaints from data/raw/cfpb_archive
python -m ingest.run --only regs           # regulations only
python -m ingest.run --only complaints --per-product 300
python -m ingest.run --complaints-csv data/raw/complaints.csv
python -m ingest.run --dry-run             # fetch regs, read complaints, chunk; no embeddings / DB
"""

import argparse
from pathlib import Path

import config
from db.connection import apply_schema
from ingest.complaints import build_complaints
from ingest.regulations import build_regulation_chunks


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest CFPB complaints + Reg E/F/Z into pgvector")
    ap.add_argument("--only", choices=["regs", "complaints"], help="run one source only")
    ap.add_argument("--per-product", type=int, default=config.COMPLAINTS_PER_PRODUCT)
    ap.add_argument(
        "--complaints-csv",
        type=Path,
        default=config.COMPLAINTS_SOURCE,
        help="CSV, ZIP of CSVs, or folder of them (default: %(default)s)",
    )
    ap.add_argument("--dry-run", action="store_true", help="skip embedding and database writes")
    args = ap.parse_args()

    if not args.dry_run:
        apply_schema()
        from ingest import load  # imported late so --dry-run needs no API keys

    if args.only in (None, "regs"):
        print("\n== Regulations ==")
        chunks = build_regulation_chunks()
        if not args.dry_run:
            load.load_regulations(chunks)

    if args.only in (None, "complaints"):
        print("\n== Complaints ==")
        df = build_complaints(args.per_product, args.complaints_csv)
        if not args.dry_run:
            load.load_complaints(df)

    if not args.dry_run:
        load.summary()


if __name__ == "__main__":
    main()
