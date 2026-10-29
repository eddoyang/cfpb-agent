-- Runs automatically on first `docker compose up` (and is safe to re-run).
CREATE EXTENSION IF NOT EXISTS vector;

-- Regulation chunks: one row per section-aligned chunk of Reg E / F / Z.
CREATE TABLE IF NOT EXISTS reg_chunks (
    chunk_id       TEXT PRIMARY KEY,          -- e.g. '1026.13#2'
    part           TEXT NOT NULL,             -- '1026'
    regulation     TEXT NOT NULL,             -- 'Regulation Z (Truth in Lending)'
    section        TEXT NOT NULL,             -- '1026.13'
    section_title  TEXT NOT NULL,             -- 'Billing error resolution.'
    citation       TEXT NOT NULL,             -- '12 CFR 1026.13(a)-(b)'
    text           TEXT NOT NULL,             -- chunk text WITH contextual header
    token_count    INT  NOT NULL,
    source_url     TEXT NOT NULL,
    as_of_date     DATE NOT NULL,             -- eCFR issue date pulled
    embedding      vector(1536)
);

-- Complaints: typed columns (not JSONB) so the stats skill can run plain SQL.
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id     BIGINT PRIMARY KEY,
    date_received    DATE,
    product          TEXT,
    sub_product      TEXT,
    issue            TEXT,
    sub_issue        TEXT,
    company          TEXT,
    state            TEXT,
    submitted_via    TEXT,
    company_response TEXT,
    timely           BOOLEAN,
    reg_hint         TEXT,                    -- '1005' | '1006' | '1026'
    narrative        TEXT NOT NULL,
    token_count      INT,
    embedding        vector(1536)
);

-- Approximate nearest-neighbour indexes (cosine distance)
CREATE INDEX IF NOT EXISTS reg_chunks_embedding_idx
    ON reg_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS complaints_embedding_idx
    ON complaints USING hnsw (embedding vector_cosine_ops);

-- Metadata filters used by retrieval and stats
CREATE INDEX IF NOT EXISTS reg_chunks_part_idx ON reg_chunks (part);
CREATE INDEX IF NOT EXISTS complaints_product_idx ON complaints (product);
CREATE INDEX IF NOT EXISTS complaints_date_idx ON complaints (date_received);
CREATE INDEX IF NOT EXISTS complaints_reg_hint_idx ON complaints (reg_hint);
