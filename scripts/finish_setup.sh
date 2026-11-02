#!/usr/bin/env bash
# Finish local setup in one go:  bash scripts/finish_setup.sh
#   1. start Postgres + pgvector        2. embed and load the regulations
#   3. reload complaints from the CFPB narratives archive (clean, reproducible sample)
#   4. run the tests                    5. run preflight          6. commit the fixes
# Costs a few cents in OpenAI embeddings. Safe to re-run.
set -uo pipefail
cd "$(dirname "$0")/.."

step() { printf "\n\033[1m== %s\033[0m\n" "$1"; }
fail() { printf "\n\033[31mStopped: %s\033[0m\nPaste the output above to Claude.\n" "$1"; exit 1; }

[ -f .venv/bin/activate ] && source .venv/bin/activate
[ -f .env ] || fail ".env is missing (copy .env.example and add your API keys)"

step "1/6 Starting Postgres + pgvector"
docker compose up -d || fail "Docker isn't running. Open Docker Desktop and re-run."
for _ in $(seq 1 30); do
  docker exec cfpb-pgvector pg_isready -U cfpb -d cfpb >/dev/null 2>&1 && break
  sleep 1
done
docker exec cfpb-pgvector pg_isready -U cfpb -d cfpb >/dev/null 2>&1 || fail "Postgres didn't start"

step "2/6 Loading regulations (Reg E, F, Z)"
python -m ingest.run --only regs || fail "regulation ingest failed"

step "3/6 Reloading complaints from the narratives archive"
[ -d data/raw/cfpb_archive ] || fail "data/raw/cfpb_archive not found (download the CCDB_Export ZIPs)"
docker exec cfpb-pgvector psql -q -U cfpb -d cfpb -c "TRUNCATE complaints;" || fail "couldn't reset complaints"
python -m ingest.run --only complaints --complaints-csv data/raw/cfpb_archive || fail "complaint ingest failed"

step "4/6 Running tests"
python -m pytest -q tests || fail "tests failed"

step "5/6 Preflight"
python preflight.py || fail "preflight found problems"

step "6/6 Committing fixes"
git add config.py README.md AGENTS.md .gitignore scripts/finish_setup.sh ingest/complaints.py
if git diff --cached --quiet; then
  echo "Nothing new to commit."
else
  git commit -q -m "Stop sending temperature to Claude 5.5 models; add setup script and AGENTS.md" \
    && git log --oneline -1
fi

printf "\n\033[32mAll done.\033[0m Try:  python cli.py ask \"How often can a debt collector call?\"\n"
