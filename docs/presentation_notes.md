# Presentation notes (30 minutes, client framing)

Where each required topic lives in the code, and what to say. Items marked **[fill]**
need numbers from your own runs (`python -m eval.harness --repeats 3` and
`python -m experiments.context_compare`).

## 1. Problem and business value (3 min)
- **Who:** complaint-handling and compliance teams at banks and card issuers.
- **Problem:** high complaint volume, each needing the right regulation, a correct reply and
  an audit trail. Wrong or late replies lead to regulatory findings and repeat complaints.
- **Success metrics:** correct outcome rate, classification accuracy, citation hit rate,
  supported-claim ratio, escalation rate, minutes per complaint vs manual, cost per complaint.
- **Why multiple agents:** separate jobs (triage, legal research, case lookup, drafting,
  checking) with different models and costs; the verifier must be independent of the drafter.

## 2. Data, RAG, vector database (4 min) → `ingest/`, `db/schema.sql`, `retrieval/store.py`
- Sources: eCFR (authoritative regulation text), CFPB complaint database (real narratives).
- Chunking: section-aligned + contextual header + precise citations (see README).
- Embeddings: OpenAI `text-embedding-3-small`, 1536 dims; the same model for documents and queries.
- Retrieval: pgvector HNSW cosine, part/product metadata filters, iterative scan so filters
  don't starve results, explicit section mentions injected, score floor for sufficiency.
- Why pgvector: vectors, metadata and stats in one database, plain SQL, no extra service.
- Data quality: consent filter, redaction normalisation, dedupe, truncation; limitations above.

## 3. Architecture, skills, workflows (6 min) → `skills/`, `graphs/`
- Show `docs/static_graph.png` and `docs/dynamic_graph.png`.
- Shared state is a typed dict; agents exchange evidence dicts with stable IDs (`R-`, `C-`, `S-`).
- Skills are plain functions taking a `Runtime`, so both graphs (and tests) reuse them.
- Stats agent never writes SQL: it fills a schema, and code builds parameterised, read-only SQL.
- Error handling: every node is wrapped, errors become state, routers send to escalate.
- Stopping conditions: 2 redrafts, 6 supervisor steps, 1 re-plan, 2 consecutive tool errors,
  LangGraph recursion limit 40.

## 4. Models and context management (4 min) → `config.py`, `context.py`, `experiments/`
- Haiku for high-volume, low-risk calls (classify, route, summarise); Sonnet for drafting and
  verification, where quality matters most.
- Evidence is packed by priority (regulations → stats → complaints) into a token budget;
  complaint narratives are clipped; the supervisor sees summaries, never full text.
- History: lean keeps the last 2 turns + a Haiku summary; rich keeps everything.
- **[fill]** lean vs rich table: tokens, cost, latency, supported ratio, sections cited.

## 5. Evaluation and hallucination handling (5 min) → `eval/`
- 28 cases across success, ambiguous, out of scope, missing info, adversarial, known failure.
- Metrics: outcome, classification, retrieval hit, citation hit, routing, forbidden content,
  supported-claim ratio, verifier catches, consistency across repeats, latency, cost.
- **[fill]** headline numbers from `eval/results/latest.md`.
- Failure to show: `dy-commentary` (needs Supplement I, not ingested) and/or `st-multi-product`.
- How unsupported claims arise: the model fills gaps from memory (deadlines, dollar limits),
  over-generalises from a similar complaint, or follows injected instructions. Response:
  verify → redraft/re-plan → abstain/escalate → human approval.

## 6. Infrastructure and trade-offs (3 min)
- Demo: Docker Postgres + pgvector, Python, Streamlit; LangSmith tracing optional.
- Production: managed Postgres (RDS/Cloud SQL) with pgvector, scheduled ingestion with
  eCFR change detection, LangGraph Postgres checkpointer for durable human-review queues,
  per-request cost logging, PII scanning, model fallbacks.
- Trade-offs: model tier vs cost; top-k and budget vs latency; verifier strictness vs
  escalation volume; LLM judge cost (roughly doubles strong-model calls) vs safety.

## 7. Live demo (4 min) → `streamlit run app.py` (backup: `cli.py`)
- Static success: `st-unauth-credit` → approve in the UI.
- Static uncertainty: `st-ambiguous-money` (clarify) or `st-injection`.
- Dynamic: `dy-relief-and-rule` (stats + regulation routing), then `dy-oos-reg-dd` (abstain).
- **[fill]** lessons learned from your runs (what surprised you, what you changed).

## 8. Limitations and next steps (1 min)
- Ingest Official Interpretations and more regulations; legal-reviewed gold answers;
  hybrid (BM25 + vector) retrieval and reranking; a judge from a different model family;
  calibrated thresholds; durable checkpointer; monitoring dashboards.
