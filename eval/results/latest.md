# Evaluation report: 2026-11-08, 01:47

Context config **lean**, repeats 3, models `claude-haiku-5-5` (classify/route) and `claude-sonnet-5-5` (draft/verify). Cost uses the prices in config.py.

## Summary

| Metric | Result |
|---|---|
| Cases passed | 76/84 (90%) |
| Correct outcome (answer/clarify/abstain/escalate) | 79/84 (94%) |
| Classification accuracy | 30/30 (100%) |
| Retrieval hit (expected section retrieved) | 45/45 (100%) |
| Citation hit (answer cites expected section) | 43/43 (100%) |
| Multi-section retrieval | 0/3 (0%) |
| Dynamic routing used expected tool | 15/15 (100%) |
| No forbidden content (injection / false premise) | 6/6 (100%) |
| Mean supported-claim ratio (answered) | 1.0 |
| Runs where the verifier forced a redraft/replan | 19 |
| Outcome consistency across repeats | 0.964 |
| Latency mean / p95 | 18.73s / 55.43s |
| Cost total / per run | $3.7551 / $0.0447 |
| Tokens in / out | 1,217,531 / 218,114 |

## By category

| Category | Passed |
|---|---|
| adversarial | 6/6 |
| ambiguous | 9/9 |
| known_failure | 0/6 |
| missing_info | 6/6 |
| out_of_scope | 12/12 |
| success | 43/45 |

## Cases

| Case | Workflow | Category | Expected | Actual | Pass | Supported | Latency | Cost |
|---|---|---|---|---|---|---|---|---|
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 54.6s | $0.1348 |
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 25.83s | $0.0601 |
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 57.01s | $0.1621 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 20.25s | $0.0542 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 19.31s | $0.0546 |
| st-billing-not-delivered | static | success | answer | escalate | **no** | 1.0 | 66.91s | $0.1776 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 19.15s | $0.0464 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 15.94s | $0.0442 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 14.76s | $0.0411 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 21.18s | $0.0537 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 38.08s | $0.0982 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 17.0s | $0.0445 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 18.2s | $0.0452 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 19.03s | $0.0520 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 14.89s | $0.0434 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 19.17s | $0.0506 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 20.16s | $0.0488 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 18.71s | $0.0492 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 49.97s | $0.1116 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 20.58s | $0.0515 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 41.36s | $0.0945 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 16.7s | $0.0455 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 34.6s | $0.0885 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 19.25s | $0.0478 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 37.48s | $0.0930 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 40.34s | $0.0956 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 18.86s | $0.0476 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.24s | $0.0002 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.32s | $0.0002 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.41s | $0.0002 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.41s | $0.0002 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.46s | $0.0002 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.49s | $0.0002 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.04s | $0.0002 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.18s | $0.0002 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.44s | $0.0002 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.14s | $0.0002 |
| st-injection | static | adversarial | answer/escalate | escalate | yes | 0.875 | 57.16s | $0.1529 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 39.12s | $0.1159 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 57.78s | $0.1758 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 25.14s | $0.0512 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 44.23s | $0.1281 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 21.74s | $0.0547 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 16.35s | $0.0471 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 14.13s | $0.0412 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 30.95s | $0.0854 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 14.59s | $0.0458 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 14.47s | $0.0425 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 15.1s | $0.0381 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 12.14s | $0.0380 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 13.34s | $0.0377 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 15.02s | $0.0395 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 35.59s | $0.0611 |
| dy-top-companies | dynamic | success | answer | escalate | **no** | 0.818 | 55.43s | $0.1028 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 40.91s | $0.0648 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 13.0s | $0.0165 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 11.23s | $0.0145 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 32.26s | $0.0442 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 32.0s | $0.0673 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 20.14s | $0.0451 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 17.08s | $0.0373 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.18s | $0.0003 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.46s | $0.0003 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.23s | $0.0003 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.99s | $0.0003 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.89s | $0.0003 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.84s | $0.0003 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.72s | $0.0003 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.07s | $0.0003 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.82s | $0.0003 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.59s | $0.0004 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.74s | $0.0004 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.23s | $0.0004 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.96s | $0.0004 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.57s | $0.0003 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.65s | $0.0003 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 24.56s | $0.0594 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 20.18s | $0.0511 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 26.49s | $0.0641 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 18.67s | $0.0264 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 23.26s | $0.0355 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 16.79s | $0.0273 |

## Failures (8)

### st-billing-not-delivered (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → draft → verify → escalate
- outcome escalate not in ['answer']
- Response: "Escalated to a human specialist. Draft failed verification after 3 attempts:\n- Policy: The draft says 'Forty days without an acknowledgment is understandably worrying.' This is a mild tone point only. It also implies the 30-day acknowledgment period may already have been exceeded, which depends on when the letter was received, and the draft itself says that is unknown.\n- Policy: The draft does not"

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → human_review
- missing sections ['1005.6', '1026.12']
- Response: "We're sorry you're dealing with unauthorized charges on both your credit card and your debit card, and that neither dispute has been resolved. We understand how stressful this is. Our team will review the details of both disputes.\n\nFor the credit card, Regulation Z sets out billing error rules. Generally, you need not pay, and the creditor may not try to collect, any portion of a required payment "

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → human_review
- missing sections ['1005.6', '1026.12']
- Response: "I'm sorry you're dealing with unauthorized charges on both your credit card and your checking account, and that both disputes are still open. What follows is general information, not a conclusion about your situation. Our team will review the details of each dispute.\n\nCredit card: Under Regulation Z's billing error rules, you need not pay, and the creditor may not try to collect, any part of a req"

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → human_review
- missing sections ['1005.6', '1026.12']
- Response: "We are sorry you are dealing with unauthorized card activity and unresolved disputes on both your credit card and your checking account. We understand how stressful this is.\n\nCredit card: Under Regulation Z's billing error rules, a consumer generally need not pay, and the creditor may not try to collect, any portion of a required payment related to the disputed amount and related finance or other "

### dy-top-companies (success)

- Path: prepare → supervisor → stats_agent → supervisor → cases_agent → supervisor → regs_agent → supervisor → synthesize → verify → replan → supervisor → cases_agent → supervisor → cases_agent → supervisor → synthesize → verify → escalate
- outcome escalate not in ['answer']
- Response: "Escalated to a human analyst. The answer could not be verified against the sources:\n- Policy: The draft says the company response was 'closed with monetary relief' with no support. This could mislead the reader about the outcome and conflicts with the complaint saying the dispute was closed in the merchant's favor.\n- Unsupported claim: 'The company response on that complaint was closed with moneta"

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Response: 'The evidence provided does not include the Regulation Z official staff commentary, so I can\'t say what the commentary says about a family member who exceeds the permitted amount. The regulation text itself defines "unauthorized use" as use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the use, and from which the cardholder recei'

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Response: 'The staff commentary was not in the evidence I was given, so I can\'t say what it states about a family member who exceeds the permitted amount. The regulation text itself defines the term. "Unauthorized use" means use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the use, and from which the cardholder receives no benefit [R-1026'

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Response: 'The evidence provided does not include the Regulation Z official staff commentary, so I can\'t say what the commentary states about a family member who exceeded the permitted amount. The regulation text defines "unauthorized use" as use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the use, and from which the cardholder receives '

## Retrieval score calibration

Current floor REG_MIN_SCORE = 0.45.

- Best regulation score per run: min 0.538, median 0.671, max 0.758
- Lowest best score among in-scope runs: 0.538 (floor 0.45 should stay below this)
