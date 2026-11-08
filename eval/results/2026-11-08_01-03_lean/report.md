# Evaluation report: 2026-11-08, 01:03

Context config **lean**, repeats 5, models `claude-haiku-5-5` (classify/route) and `claude-sonnet-5-5` (draft/verify). Cost uses the prices in config.py; confirm them before quoting.

## Summary

| Metric | Result |
|---|---|
| Cases passed | 5/5 (100%) |
| Correct outcome (answer/clarify/abstain/escalate) | 5/5 (100%) |
| Classification accuracy | 5/5 (100%) |
| Retrieval hit (expected section retrieved) | 5/5 (100%) |
| Citation hit (answer cites expected section) | 5/5 (100%) |
| Mean supported-claim ratio (answered) | 1.0 |
| Runs where the verifier forced a redraft/replan | 2 |
| Outcome consistency across repeats | 1.0 |
| Latency mean / p95 | 32.43s / 43.9s |
| Cost total / per run | $0.3823 / $0.07646 |
| Tokens in / out | 94,850 / 21,594 |

## By category

| Category | Passed |
|---|---|
| success | 5/5 |

## Cases

| Case | Workflow | Category | Expected | Actual | Pass | Supported | Latency | Cost |
|---|---|---|---|---|---|---|---|---|
| st-remittance | static | success | answer | answer | yes | 1.0 | 23.85s | $0.0508 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 43.9s | $0.1094 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 38.19s | $0.0959 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 26.01s | $0.0600 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 30.21s | $0.0662 |

## Failures (0)

## Retrieval score calibration

Current floor REG_MIN_SCORE = 0.45.

- Best regulation score per run: min 0.650, median 0.657, max 0.670
- Set the floor just above typical out-of-scope scores and below in-scope ones.
