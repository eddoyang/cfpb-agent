"""Run this first:  python preflight.py

Checks, in order, everything a demo depends on, and says what to fix.
Costs a fraction of a cent (two 1-token Claude calls and one embedding).
"""
from __future__ import annotations

import os
import sys
import time

import config

OK, FAIL, WARN = "\033[32mOK\033[0m", "\033[31mFAIL\033[0m", "\033[33mWARN\033[0m"
problems = 0


def check(label, fn):
    global problems
    try:
        start = time.perf_counter()
        status, detail = fn()
        print(f"[{status}] {label}: {detail} ({time.perf_counter() - start:.1f}s)")
        if status == FAIL:
            problems += 1
    except Exception as e:  # noqa: BLE001
        problems += 1
        print(f"[{FAIL}] {label}: {type(e).__name__}: {str(e)[:200]}")


def keys():
    missing = [k for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY") if not os.getenv(k)]
    return (FAIL, f"missing {missing} in .env") if missing else (OK, "both keys set")


def database():
    from db.connection import get_conn
    with get_conn() as conn:
        ext = conn.execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()
        regs = conn.execute("SELECT count(*), count(embedding) FROM reg_chunks").fetchone()
        comps = conn.execute("SELECT count(*), count(embedding) FROM complaints").fetchone()
    if not ext:
        return FAIL, "pgvector extension missing"
    if not regs[1] or not comps[1]:
        return FAIL, (f"pgvector {ext[0]}, but data not loaded (reg_chunks {regs[1]}, "
                      f"complaints {comps[1]} embedded). Run: python -m ingest.run")
    return OK, f"pgvector {ext[0]}; {regs[1]} regulation chunks, {comps[1]} complaints embedded"


def claude(model):
    def fn():
        from runtime import make_chat_model
        out = make_chat_model(model, max_tokens=5).invoke("Say OK")
        return OK, f"{model} replied {out.content!r}"
    return fn


def embeddings():
    from langchain_openai import OpenAIEmbeddings
    v = OpenAIEmbeddings(model=config.EMBEDDING_MODEL, dimensions=config.EMBEDDING_DIM).embed_query("test")
    if len(v) != config.EMBEDDING_DIM:
        return FAIL, f"got {len(v)} dims, schema expects {config.EMBEDDING_DIM}"
    return OK, f"{config.EMBEDDING_MODEL}, {len(v)} dims"


def retrieval():
    from retrieval.store import PgStore
    hits = PgStore().search_regulations("liability for unauthorized use of a credit card", k=3)
    if not hits:
        return FAIL, "no results"
    top = hits[0]
    status = OK if top["section"] == "1026.12" else WARN
    return status, (f"top hit {top['section']} score {top['score']:.3f} "
                    f"(expected 1026.12; floor is {config.REG_MIN_SCORE})")


if __name__ == "__main__":
    check("API keys", keys)
    check("Postgres + pgvector + data", database)
    check("Claude fast tier", claude(config.FAST_MODEL))
    check("Claude strong tier", claude(config.STRONG_MODEL))
    check("OpenAI embeddings", embeddings)
    check("Retrieval sanity", retrieval)
    print("\nAll good. Try: python cli.py ask \"How often can a debt collector call?\""
          if not problems else f"\n{problems} problem(s) to fix first.")
    sys.exit(1 if problems else 0)
