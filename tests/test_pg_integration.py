"""Integration tests against a real Postgres + pgvector (no OpenAI needed: a
deterministic hash embedder stands in). Skipped unless a database is reachable:

    docker compose up -d && python -m pytest tests/test_pg_integration.py

They run in a SEPARATE database (cfpb_test) on the same server, created on first use,
so they never read or modify the real reg_chunks/complaints data.
"""

import hashlib
import re

import numpy as np
import psycopg
import pytest

import config
from db.connection import apply_schema, get_conn
from retrieval.store import PgStore
from skills.schemas import StatsRequest
from skills.stats import build_sql, run_stats
from tests.fakes import make_rt

TEST_PREFIX = "TEST-"
TEST_DB = "cfpb_test"
TEST_DSN = re.sub(r"dbname=\S+", f"dbname={TEST_DB}", config.PG_DSN)
assert TEST_DSN != config.PG_DSN, "integration tests must not use the main database"


class HashEmbedder:
    """Bag-of-words hashed into 1536 dims: similar wording -> similar vectors."""

    def embed_query(self, text):
        v = np.zeros(config.EMBEDDING_DIM, dtype=np.float32)
        for w in text.lower().split():
            v[
                int(hashlib.md5(w.strip(".,()").encode()).hexdigest(), 16) % config.EMBEDDING_DIM
            ] += 1
        return (v / (np.linalg.norm(v) or 1)).tolist()


def _db_available():
    try:
        psycopg.connect(config.PG_DSN, connect_timeout=2).close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_available(), reason="Postgres not reachable")

REGS = [
    (
        "1026.12",
        "Special credit card provisions.",
        "1026",
        "liability of cardholder for unauthorized use of credit card shall not exceed $50",
    ),
    (
        "1026.13",
        "Billing error resolution.",
        "1026",
        "billing error notice written notice within 60 days of periodic statement",
    ),
    (
        "1006.14",
        "Harassing, oppressive, or abusive conduct.",
        "1006",
        "debt collector telephone calls more than seven times within seven days",
    ),
]
COMPLAINTS = [
    (
        990001,
        "Credit card",
        "Problem with a purchase",
        "Bank A",
        "2024-01-15",
        True,
        "Closed with monetary relief",
        "unauthorized charge on my credit card the bank refused",
    ),
    (
        990002,
        "Credit card",
        "Fees or interest",
        "Bank B",
        "2024-02-10",
        False,
        "Closed with explanation",
        "late fee charged even though I paid on time",
    ),
    (
        990003,
        "Debt collection",
        "Communication tactics",
        "Agency C",
        "2024-02-20",
        True,
        "Closed with explanation",
        "debt collector calls me ten times a day at work",
    ),
]


def _ensure_test_database():
    with psycopg.connect(config.PG_DSN, autocommit=True) as conn:
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB,)).fetchone()
        if not exists:
            conn.execute(f'CREATE DATABASE "{TEST_DB}"')


@pytest.fixture(scope="module")
def store():
    _ensure_test_database()
    apply_schema(TEST_DSN)
    emb = HashEmbedder()
    with get_conn(TEST_DSN) as conn:
        conn.execute("TRUNCATE reg_chunks, complaints")  # test database only
        for sec, title, part, text in REGS:
            conn.execute(
                """INSERT INTO reg_chunks VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    f"{TEST_PREFIX}{sec}#1",
                    part,
                    config.REGULATIONS[part],
                    sec,
                    title,
                    f"12 CFR {sec}",
                    text,
                    20,
                    f"https://www.ecfr.gov/x/{sec}",
                    "2026-10-01",
                    np.array(emb.embed_query(text), dtype=np.float32),
                ),
            )
        for cid, prod, issue, co, date, timely, resp, text in COMPLAINTS:
            conn.execute(
                """INSERT INTO complaints (complaint_id, date_received, product, issue, company,
                   state, company_response, timely, reg_hint, narrative, token_count, embedding)
                   VALUES (%s,%s,%s,%s,%s,'WA',%s,%s,NULL,%s,20,%s)""",
                (
                    cid,
                    date,
                    prod,
                    issue,
                    co,
                    resp,
                    timely,
                    text,
                    np.array(emb.embed_query(text), dtype=np.float32),
                ),
            )
    yield PgStore(embedder=emb, dsn=TEST_DSN)
    with get_conn(TEST_DSN) as conn:
        conn.execute("TRUNCATE reg_chunks, complaints")


def test_vector_search_ranks_relevant_section_first(store):
    hits = store.search_regulations("unauthorized use of my credit card liability", k=3)
    assert hits[0]["section"] == "1026.12"
    assert hits[0]["score"] > hits[-1]["score"]
    assert hits[0]["id"].startswith("R-") and "12 CFR 1026.12" in hits[0]["citation"]


def test_part_filter(store):
    hits = store.search_regulations("calls", k=5, parts=["1006"])
    assert hits and all(h["meta"]["part"] == "1006" for h in hits)


def test_section_mention_is_injected(store):
    hits = store.search_regulations("what does 1006.14 say about fees", k=1, parts=["1026"])
    assert any(h["section"] == "1006.14" for h in hits)


def test_complaint_search_product_filter_and_exclude(store):
    hits = store.search_complaints(
        "collector calls at work", k=3, product_keyword="debt collection"
    )
    assert [h["id"] for h in hits] == ["C-990003"]
    assert (
        store.search_complaints("collector calls", k=3, product_keyword="debt", exclude_id=990003)
        == []
    )


@pytest.mark.parametrize(
    "req, check",
    [
        (
            StatsRequest(metric="count", group_by="product", company_keyword="Bank"),
            lambda rows: {r["grp"] for r in rows} == {"Credit card"},
        ),
        (
            StatsRequest(
                metric="count",
                group_by="month",
                date_from="2024-01-01",
                date_to="2024-02-28",
                company_keyword="Agency C",
            ),
            lambda rows: rows[0]["grp"] == "2024-02" and rows[0]["value"] == 1,
        ),
        (
            StatsRequest(
                metric="relief_rate",
                group_by="none",
                product_keyword="credit card",
                company_keyword="Bank",
            ),
            lambda rows: float(rows[0]["value"]) == 50.0,
        ),
        (
            StatsRequest(metric="timely_rate", group_by="company", company_keyword="Bank"),
            lambda rows: (
                {r["grp"]: float(r["value"]) for r in rows} == {"Bank A": 100.0, "Bank B": 0.0}
            ),
        ),
    ],
)
def test_stats_sql_runs_on_postgres(store, req, check):
    sql, params = build_sql(req)
    rows = store.run_readonly(sql, params)
    assert check(rows), (sql, rows)
    res = run_stats(make_rt(script=None, store=store), req)
    assert res["sufficient"] and "(n=" in res["evidence"][0]["text"]


def test_readonly_blocks_writes(store):
    with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
        store.run_readonly("DELETE FROM complaints WHERE complaint_id = %(x)s", {"x": 990001})


def test_complaint_date_range_reads_loaded_data(store):
    dates = sorted(str(c[4]) for c in COMPLAINTS)
    assert store.complaint_date_range() == (dates[0], dates[-1])
