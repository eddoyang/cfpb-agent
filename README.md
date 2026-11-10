# CFPB complaint triage: multi-agent RAG

A LangGraph multi-agent system for a bank's complaint team. It triages consumer
complaints against Regulation E, F and Z, drafts cited replies, verifies every claim
against its sources, and answers analyst questions by routing between regulation
search, similar-complaint search and SQL statistics.

![static workflow](docs/static_graph.png)

## Quick start
```bash
docker compose up -d                                  # Postgres 16 + pgvector
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                  # add API keys and model prices (see Configuration)

python -m pytest -q tests                             # 53 tests; DB tests need step 1 and use a separate cfpb_test DB
python -m ingest.run --dry-run                        # fetch regs, read archive, chunk; no cost
python -m ingest.run --complaints-csv data/raw/cfpb_archive   # embed + load (see Data below)
python preflight.py                                   # checks keys, models, data, retrieval

python cli.py ask "How often can a debt collector call?"
python cli.py triage --sample --approve
streamlit run app.py
python -m eval.harness --repeats 3
python -m eval.harness --cases eval/holdout.yaml --repeats 3   # held-out set, run once
python -m experiments.context_compare
```

## How it fits together
```
config.py            models, prices, thresholds, stopping conditions
runtime.py           Claude clients (2 tiers) + call ledger (tokens, latency, cost)
context.py           evidence packing under a token budget; history summary vs full
retrieval/store.py   pgvector search (HNSW, cosine, metadata filters), read-only SQL
skills/              classify, retrieve, stats, draft, verify (written once, called by both graphs)
graphs/static.py     fixed triage pipeline
graphs/dynamic.py    supervisor-routed analyst workflow + policy guardrails
graphs/runner.py     run_static / resume_static / run_dynamic -> one result format
eval/                cases.yaml (28 cases), harness.py (metrics + markdown report)
experiments/         context_compare.py (lean vs rich on one query)
app.py, cli.py       demo interfaces
preflight.py         setup checker
ingest/, db/         data pipeline and schema
docs/                graph diagrams, presentation notes
```

## Skills (reusable, framework-agnostic functions)
| Skill | Uses | Input → output | Static | Dynamic |
|---|---|---|---|---|
| `classify` | Claude fast tier | complaint → product, issue, regulation parts, priority, scope, clarity | yes | no |
| `retrieve_regulations` | pgvector | query (+ part filter) → cited chunks + best score + sufficiency | yes | yes |
| `retrieve_cases` | pgvector | text (+ product filter) → similar real complaints | yes | yes |
| `run_stats` | Postgres | structured `StatsRequest` → aggregate table (whitelisted SQL, read-only) | no | yes |
| `draft` | Claude strong tier | request + packed evidence → response with per-claim citations | yes | yes |
| `verify` | rules + Claude strong tier | draft → supported/unsupported claims, policy issues, feedback | yes | yes |

Each skill is a plain Python function, written once. The graphs only decide which skill runs
and when: retrieval, drafting and verification are used by both workflows, `classify` only by
the static one (the dynamic supervisor does its own routing) and `run_stats` only by the
dynamic one. A fix to a shared skill reaches both workflows, and every skill can be tested on
its own with a fake model.

## Workflows
**Static (complaint triage):** classify → retrieve regulations → retrieve similar cases →
draft → verify → human approval. Guardrail exits: unclear (including an unknown product) →
clarify, checked before scope; out of scope → abstain; best regulation score below the floor → escalate; verification fails 3 times
(1 draft + 2 redrafts) → escalate; any node error → escalate.

**Dynamic (analyst Q&A):** a supervisor picks the next action from the question and from
what earlier steps returned: search regulations, search complaints, run stats, synthesize,
clarify or abstain. The supervisor is told today's date and the date range of the loaded
complaints, and workers add only evidence it doesn't already have. A deterministic policy
layer overrides it: 6-step cap, repeated identical search → synthesize, 2 searches in a
row that add no new evidence → synthesize, synthesize with no evidence → search or
abstain, 2 consecutive tool errors → escalate. After synthesis, failed verification sends feedback
back to the supervisor once (re-plan), then abstains or escalates.

![dynamic workflow](docs/dynamic_graph.png)

## Hallucination handling
1. **Grounded drafting:** evidence only, an ID after every claim. Partial answers are allowed:
   what the evidence doesn't cover goes in `gaps`; `insufficient_evidence` is set only when the
   main question can't be answered.
2. **Deterministic checks:** every claim cited, every cited ID was actually in context, no
   promised refunds or outcomes (negation-aware, so "we can't guarantee a refund" passes).
3. **LLM judge:** each claim is checked against the evidence it cites (catches a real
   citation attached to a wrong deadline). The judge sees each evidence block exactly as the
   drafter saw it, citation header included. It also flags facts in the reply that aren't in
   the claims list. Policy issues are **blocking** (promises, legal conclusions about this
   customer, misleading statements, rude tone) or **advisory** (wording, warmth); only blocking
   issues fail the draft, advisory notes go to the reviewer.
4. **Act on failure:** redraft with feedback, re-plan, abstain, or escalate to a human.
5. **Prompt injection:** customer text is wrapped and marked untrusted; eval cases test it.

## Results (final runs, 2026-11-08)
All runs use lean context and 3 repeats per case, on the code at commit `b50c452` or later
(the judge sees the customer's message; only blocking issues go back to the drafter).

| Metric | Development (`eval/cases.yaml`, 28 cases) | Held-out (`eval/holdout.yaml`, 23 cases) |
|---|---|---|
| Pass rate | 78/84 (93%); 78/78 (100%) excluding the two known-failure cases | 62/69 (90%) |
| Consistency across repeats | 1.0 | 0.957 |
| Cost per run | $0.051 | $0.046 |
| Latency mean / p95 | 22.1 s / 56.9 s | 20.5 s / 48.5 s |
| Verifier-forced redrafts or re-plans | 20 of 84 runs | 16 of 69 runs |
| Report | `eval/results/2026-11-08_21-05_lean/` | `eval/results/2026-11-08_22-12_lean_holdout/` |

Development progression: 17/28 (61%, baseline, one run per case) -> 74/84 -> 76/84 -> 78/84 ->
78/84 with consistency 1.0. The only development failures are the two known-failure cases:
`st-multi-product` (one search query for a two-issue complaint misses both liability sections)
and `dy-commentary` (the Reg Z commentary isn't ingested; the reply says so and answers from the
regulation text instead of abstaining).

**Held-out check.** Because prompts and the cutoff were tuned on the development cases, 23 new
cases were written after tuning with expectations fixed in advance, and never tuned on. They
passed 64/69 (93%) before the latest judge fix and 62/69 (90%) after it; the judge fix came from
the demo and the context comparison, not from held-out results. Latest held-out failures: a store
gift card declined as out of scope (1 of 3 runs; the classifier's scope list names prepaid cards,
not gift cards), a remittance cancellation where search found 1005.33 instead of 1005.34 (and one
run cited an evidence ID it was never shown, caught by the deterministic check), two escalations
where the judge blocked an ambiguous opening line about a rule's scope, and one correct refutation
of a false premise that tripped the plain-text forbidden-phrase check. Held-out results are never
used for tuning; fixing them would make them development cases.

**Context comparison** (`python -m experiments.context_compare`, the same two-part question, two
runs per config, `experiments/results/context_compare_20261108-223923.md`): lean (top 3 rules / 2
cases, 2,500-token budget, summarized history) used 5.5 evidence items, cost $0.072 and took 41 s
per answer; rich (top 10 / 5, 9,000 tokens, full history) used 17 items, cost $0.101 (40% more)
and took 39 s. Both answered both runs with a supported-claim ratio of 1.0; each cited 3 of the 4
expected sections, and rich found 1026.12, which lean missed. Lean stays the default on cost; rich
is an option for multi-part questions. Earlier runs, before the judge fixes, showed rich at 2.2x
the cost escalating both runs, then 37% more with one escalation on a false alarm; most of that
gap was the judge.

## Configuration notes
- **Models:** `claude-haiku-5-5` (classify, route, summarize) and `claude-sonnet-5-5` (draft,
  verify). Override with `FAST_MODEL` / `STRONG_MODEL`.
- **Temperature:** Claude Haiku 5.5 and Sonnet 5.5 don't accept a custom temperature, so both run
  at their defaults; run-to-run variation is measured with `eval.harness --repeats`.
- **Prices** are read from `.env` (`FAST_PRICE_IN`, `FAST_PRICE_OUT`, `STRONG_PRICE_IN`,
  `STRONG_PRICE_OUT`, `EMBED_PRICE`, USD per 1M tokens) and are required; there are no defaults in
  code, and `preflight.py` fails if one is missing. The reported results used Haiku 5.5 $0.10 / $0.50, Sonnet 5.5 $2 / $10 and
  text-embedding-3-small $0.02; check the providers' pricing pages before quoting costs.
- **Output limits:** 1,024 tokens for the fast tier, 4,096 for the strong tier (drafts were
  being cut off at 2,048).
- **Score floor** (`REG_MIN_SCORE`, default 0.45) was calibrated from eval runs: the lowest
  best score for an in-scope case was 0.509. Recalibrate on new data; the eval report includes
  a calibration section. `CASE_MIN_SCORE` is 0.30.

## Data design decisions
**Regulations (12 CFR 1005, 1006, 1026):** section-aligned chunks (never cross a section),
paragraphs packed to 700 tokens, a contextual header on every chunk, citations down to
top-level paragraphs (`12 CFR 1026.13(a)-(b)`), and the eCFR issue date on every row.

**Complaints:** consented narratives only; CFPB `XXXX` redactions normalised; under-30-word
and duplicate narratives dropped; long ones truncated; typed SQL columns so stats run in SQL.
**Data source change (August 2026):** the CFPB stopped publishing complaint narratives on
2026-08-14, so the live API and current bulk download no longer include them. Use the CFPB's
official [narratives archive](https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/):
download a few recent `CCDB_Export_*.zip` files into `data/raw/cfpb_archive/` and run
`python -m ingest.run --only complaints --complaints-csv data/raw/cfpb_archive`. ZIPs are read
directly; overlapping periods are de-duplicated. The sample is therefore frozen at
August 2026, which is a stated limitation. The loaded sample is 5,163 complaints received
2026-04-01 to 2026-07-29 (five products, up to 1,200 each) plus 413 regulation chunks.

## Known limitations
- Official Interpretations (Reg Z Supplement I) and other regulations (Reg DD, FCRA) are not
  ingested; the eval includes a case that fails because of this (`dy-commentary`).
- A complaint about two products gets one retrieval query, so only one regulation is found
  (`st-multi-product`, a known failure). Fix: one query per issue.
- Complaint narratives are consumer-reported and unverified; the sample is not the whole market.
- The LLM judge shares a model family with the drafter; a human reviewer remains the final gate.
- `reg_hint` and product mapping are heuristics, not legal determinations.
- Lean retrieval keeps the top 3 sections, so a neighbouring section can crowd out the most
  specific one (held-out: 1006.18, 1005.34). Fix: one query per issue, or re-rank more hits.
- The classifier's scope list doesn't mention gift cards, so store gift cards can be declined
  even though Reg E 1005.20 covers them.
