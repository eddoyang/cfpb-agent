# Evaluation report: 20261107-192031

Context config **lean**, repeats 3, models `claude-haiku-5-5` (classify/route) and `claude-sonnet-5-5` (draft/verify). Cost uses the prices in config.py; confirm them before quoting.

## Summary

| Metric | Result |
|---|---|
| Cases passed | 12/12 (100%) |
| Correct outcome (answer/clarify/abstain/escalate) | 12/12 (100%) |
| Mean supported-claim ratio (answered) | None |
| Runs where the verifier forced a redraft/replan | 0 |
| Outcome consistency across repeats | 1.0 |
| Latency mean / p95 | 1.34s / 2.53s |
| Cost total / per run | $0.0261 / $0.00218 |
| Tokens in / out | 15,321 / 2,157 |

## By category

| Category | Passed |
|---|---|
| ambiguous | 6/6 |
| out_of_scope | 6/6 |

## Cases

| Case | Workflow | Category | Expected | Actual | Pass | Supported | Latency | Cost |
|---|---|---|---|---|---|---|---|---|
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 2.53s | $0.0024 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.48s | $0.0024 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.45s | $0.0024 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.33s | $0.0023 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.49s | $0.0023 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.24s | $0.0022 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0021 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.01s | $0.0021 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.17s | $0.0021 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.09s | $0.0020 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.32s | $0.0021 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 0.93s | $0.0020 |

## Failures (0)

## Retrieval score calibration

Current floor REG_MIN_SCORE = 0.3.

- Set the floor just above typical out-of-scope scores and below in-scope ones.
