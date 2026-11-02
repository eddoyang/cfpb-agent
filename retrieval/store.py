"""pgvector-backed store: vector search over regulations and complaints, plus
read-only SQL for the stats skill. Evidence is returned as plain dicts so it can
live in LangGraph state (and be checkpointed) without custom serialisers.

Evidence dict:
  {"id": "R-1026.13#1", "kind": "regulation"|"complaint"|"stats",
   "citation": "12 CFR 1026.13(a)-(b) Billing error resolution.",
   "text": "...", "score": 0.53, "section": "1026.13", "source_url": "...", "meta": {...}}
"""

from __future__ import annotations

import re

import numpy as np
import psycopg
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

import config

SECTION_MENTION = re.compile(r"\b(10(?:05|06|26)\.\d+[a-z]?)\b")


class PgStore:
    def __init__(self, embedder=None, dsn: str = config.PG_DSN):
        self.dsn = dsn
        self._embedder = embedder
        self._conn = None
        self.embed_calls = 0
        self.embed_tokens = 0

    # ------------------------------------------------------------ plumbing
    @property
    def conn(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg.connect(self.dsn, autocommit=True, row_factory=dict_row)
            register_vector(self._conn)
            self._conn.execute(f"SET hnsw.ef_search = {config.HNSW_EF_SEARCH}")
            try:
                # pgvector >= 0.8: keep scanning when metadata filters remove
                # candidates, so filtered queries still return k rows.
                self._conn.execute("SET hnsw.iterative_scan = relaxed_order")
            except psycopg.Error:
                pass
        return self._conn

    @property
    def embedder(self):
        if self._embedder is None:
            from langchain_openai import OpenAIEmbeddings

            self._embedder = OpenAIEmbeddings(
                model=config.EMBEDDING_MODEL, dimensions=config.EMBEDDING_DIM
            )
        return self._embedder

    def embed_query(self, text: str) -> np.ndarray:
        return _cached_embed(self, text)

    # ------------------------------------------------------------ regulations
    def search_regulations(self, query: str, k: int, parts: list[str] | None = None) -> list[dict]:
        vec = self.embed_query(query)
        sql = """SELECT chunk_id, part, regulation, section, section_title, citation, text,
                        source_url, as_of_date, 1 - (embedding <=> %(v)s) AS score
                 FROM reg_chunks
                 WHERE embedding IS NOT NULL {filt}
                 ORDER BY embedding <=> %(v)s LIMIT %(k)s"""
        params = {"v": vec, "k": k}
        filt = ""
        if parts:
            filt = "AND part = ANY(%(parts)s)"
            params["parts"] = list(parts)
        rows = self.conn.execute(sql.format(filt=filt), params).fetchall()
        hits = [_reg_evidence(r) for r in rows]

        # If the user names a section ("under 1026.13"), make sure it is present.
        for section in SECTION_MENTION.findall(query):
            if not any(h["section"] == section for h in hits):
                hits = self.get_section(section, vec) + hits
        return hits

    def get_section(self, section: str, vec=None) -> list[dict]:
        vec = vec if vec is not None else np.zeros(config.EMBEDDING_DIM, dtype=np.float32)
        rows = self.conn.execute(
            """SELECT chunk_id, part, regulation, section, section_title, citation, text,
                      source_url, as_of_date, 1 - (embedding <=> %s) AS score
               FROM reg_chunks WHERE section = %s ORDER BY chunk_id""",
            (vec, section),
        ).fetchall()
        return [_reg_evidence(r) for r in rows]

    # ------------------------------------------------------------ complaints
    def search_complaints(
        self, query: str, k: int, product_keyword: str | None = None, exclude_id: int | None = None
    ) -> list[dict]:
        vec = self.embed_query(query)
        clauses, params = ["embedding IS NOT NULL"], {"v": vec, "k": k}
        if product_keyword:
            clauses.append("product ILIKE %(prod)s")
            params["prod"] = f"%{product_keyword}%"
        if exclude_id:
            clauses.append("complaint_id <> %(ex)s")
            params["ex"] = exclude_id
        rows = self.conn.execute(
            f"""SELECT complaint_id, date_received, product, issue, company, company_response,
                       timely, narrative, 1 - (embedding <=> %(v)s) AS score
                FROM complaints WHERE {" AND ".join(clauses)}
                ORDER BY embedding <=> %(v)s LIMIT %(k)s""",
            params,
        ).fetchall()
        return [
            {
                "id": f"C-{r['complaint_id']}",
                "kind": "complaint",
                "citation": (
                    f"CFPB complaint {r['complaint_id']} ({r['product']}; {r['issue']}; "
                    f"company response: {r['company_response']})"
                ),
                "text": r["narrative"],
                "score": float(r["score"]),
                "section": None,
                "source_url": f"https://www.consumerfinance.gov/data-research/consumer-complaints/search/detail/{r['complaint_id']}",
                "meta": {
                    "company": r["company"],
                    "date": str(r["date_received"]),
                    "company_response": r["company_response"],
                    "timely": r["timely"],
                },
            }
            for r in rows
        ]

    def get_complaint(self, complaint_id: int) -> dict | None:
        return self.conn.execute(
            "SELECT complaint_id, product, issue, company, narrative FROM complaints "
            "WHERE complaint_id = %s",
            (complaint_id,),
        ).fetchone()

    def random_complaints(self, n: int = 5) -> list[dict]:
        return self.conn.execute(
            "SELECT complaint_id, product, issue, narrative FROM complaints "
            "ORDER BY random() LIMIT %s",
            (n,),
        ).fetchall()

    # ------------------------------------------------------------ stats
    def run_readonly(self, sql: str, params: dict) -> list[dict]:
        """Execute a parameterised SELECT inside a read-only, time-limited transaction."""
        with psycopg.connect(self.dsn, row_factory=dict_row) as conn:
            conn.execute("SET TRANSACTION READ ONLY")
            conn.execute("SET LOCAL statement_timeout = '5s'")
            rows = conn.execute(sql, params).fetchall()
            conn.rollback()
        return rows


# Query embeddings are cached: the dynamic workflow often re-searches the same
# query string, and eval repeats re-embed identical inputs.
_EMBED_CACHE: dict[tuple[int, str], np.ndarray] = {}


def _cached_embed(store: PgStore, text: str) -> np.ndarray:
    key = (id(store), text)
    if key not in _EMBED_CACHE:
        store.embed_calls += 1
        store.embed_tokens += max(1, len(text) // 4)
        _EMBED_CACHE[key] = np.array(store.embedder.embed_query(text), dtype=np.float32)
        if len(_EMBED_CACHE) > 2048:
            _EMBED_CACHE.pop(next(iter(_EMBED_CACHE)))
    return _EMBED_CACHE[key]


def _reg_evidence(r: dict) -> dict:
    return {
        "id": f"R-{r['chunk_id']}",
        "kind": "regulation",
        "citation": f"{r['citation']} {r['section_title']}",
        "text": r["text"],
        "score": float(r["score"]),
        "section": r["section"],
        "source_url": r["source_url"],
        "meta": {"part": r["part"], "regulation": r["regulation"], "as_of": str(r["as_of_date"])},
    }
