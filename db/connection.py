"""Postgres connection helper with pgvector type registration."""

from contextlib import contextmanager
from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector

import config


@contextmanager
def get_conn(dsn: str | None = None):
    conn = psycopg.connect(dsn or config.PG_DSN, autocommit=False)
    try:
        register_vector(conn)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def apply_schema(dsn: str | None = None) -> None:
    """Idempotently apply db/schema.sql (useful if the container already existed)."""
    sql = (Path(__file__).parent / "schema.sql").read_text()
    with psycopg.connect(dsn or config.PG_DSN, autocommit=True) as conn:
        conn.execute(sql)
