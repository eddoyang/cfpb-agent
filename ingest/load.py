"""Embed chunks with OpenAI and upsert them into Postgres/pgvector.

Re-runnable: rows that already have an embedding are skipped, so a crash halfway
through (or adding more complaints later) never re-pays for embeddings.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm

import config
from db.connection import get_conn


def _embed_cost(tokens: int) -> float:
    if config.EMBED_PRICE is None:
        raise RuntimeError("No embedding price: set EMBED_PRICE in .env")
    return tokens / 1e6 * config.EMBED_PRICE


def _embedder() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=config.EMBEDDING_MODEL, dimensions=config.EMBEDDING_DIM)


def _existing_ids(table: str, key: str) -> set:
    with get_conn() as conn:
        rows = conn.execute(f"SELECT {key} FROM {table} WHERE embedding IS NOT NULL").fetchall()
    return {r[0] for r in rows}


def _embed(texts: list[str]) -> list[np.ndarray]:
    emb = _embedder()
    vectors = []
    for i in tqdm(range(0, len(texts), config.EMBED_BATCH_SIZE), desc="  embedding"):
        batch = texts[i : i + config.EMBED_BATCH_SIZE]
        vectors.extend(np.array(v, dtype=np.float32) for v in emb.embed_documents(batch))
    return vectors


def load_regulations(chunks) -> None:
    done = _existing_ids("reg_chunks", "chunk_id")
    todo = [c for c in chunks if c.chunk_id not in done]
    tokens = sum(c.token_count for c in todo)
    print(
        f"Regulations: {len(todo)} new chunks, ~{tokens:,} tokens "
        f"(~${_embed_cost(tokens):.4f})"
    )
    if not todo:
        return
    vectors = _embed([c.text for c in todo])
    with get_conn() as conn, conn.cursor() as cur:
        cur.executemany(
            """INSERT INTO reg_chunks (chunk_id, part, regulation, section, section_title,
                    citation, text, token_count, source_url, as_of_date, embedding)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    text = EXCLUDED.text, citation = EXCLUDED.citation,
                    token_count = EXCLUDED.token_count, as_of_date = EXCLUDED.as_of_date,
                    embedding = EXCLUDED.embedding""",
            [
                (
                    c.chunk_id,
                    c.part,
                    c.regulation,
                    c.section,
                    c.section_title,
                    c.citation,
                    c.text,
                    c.token_count,
                    c.source_url,
                    c.as_of_date,
                    v,
                )
                for c, v in zip(todo, vectors, strict=True)
            ],
        )


def load_complaints(df: pd.DataFrame) -> None:
    done = _existing_ids("complaints", "complaint_id")
    todo = df[~df["complaint_id"].isin(done)]
    tokens = int(todo["token_count"].sum())
    print(
        f"Complaints: {len(todo)} new rows, ~{tokens:,} tokens "
        f"(~${_embed_cost(tokens):.4f})"
    )
    if todo.empty:
        return
    # Embed product + issue alongside the narrative so similar-case search
    # respects the complaint category, not just wording.
    texts = [f"Product: {r.product}. Issue: {r.issue}.\n{r.narrative}" for r in todo.itertuples()]
    vectors = _embed(texts)

    def none_if_nan(v):
        return None if pd.isna(v) else v

    with get_conn() as conn, conn.cursor() as cur:
        cur.executemany(
            """INSERT INTO complaints (complaint_id, date_received, product, sub_product, issue,
                    sub_issue, company, state, submitted_via, company_response, timely,
                    reg_hint, narrative, token_count, embedding)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (complaint_id) DO NOTHING""",
            [
                (
                    int(r.complaint_id),
                    none_if_nan(r.date_received),
                    r.product,
                    none_if_nan(r.sub_product),
                    r.issue,
                    none_if_nan(r.sub_issue),
                    r.company,
                    none_if_nan(r.state),
                    none_if_nan(r.submitted_via),
                    none_if_nan(r.company_response),
                    bool(r.timely),
                    r.reg_hint,
                    r.narrative,
                    int(r.token_count),
                    v,
                )
                for r, v in zip(todo.itertuples(), vectors, strict=True)
            ],
        )


def summary() -> None:
    with get_conn() as conn:
        regs = conn.execute(
            "SELECT part, count(*) FROM reg_chunks GROUP BY part ORDER BY part"
        ).fetchall()
        comps = conn.execute(
            "SELECT product, count(*) FROM complaints GROUP BY product ORDER BY 2 DESC"
        ).fetchall()
    print("\nDatabase contents")
    for part, n in regs:
        print(f"  12 CFR {part}: {n} chunks")
    for product, n in comps:
        print(f"  {product}: {n} complaints")
