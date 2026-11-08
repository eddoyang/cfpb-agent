# Evaluation report: 2026-11-08, 03:36

Context config **lean**, repeats 3, models `claude-haiku-5-5` (classify/route) and `claude-sonnet-5-5` (draft/verify). Cost uses the prices in .env.

## Summary

| Metric | Result |
|---|---|
| Cases passed | 78/84 (93%) |
| Correct outcome (answer/clarify/abstain/escalate) | 80/84 (95%) |
| Classification accuracy | 30/30 (100%) |
| Retrieval hit (expected section retrieved) | 45/45 (100%) |
| Citation hit (answer cites expected section) | 45/45 (100%) |
| Multi-section retrieval | 0/3 (0%) |
| Dynamic routing used expected tool | 15/15 (100%) |
| No forbidden content (injection / false premise) | 6/6 (100%) |
| Mean supported-claim ratio (answered) | 1.0 |
| Runs where the verifier forced a redraft/replan | 14 |
| Outcome consistency across repeats | 0.988 |
| Latency mean / p95 | 20.72s / 54.15s |
| Cost total / per run | $3.9995 / $0.04761 |
| Tokens in / out | 1,181,719 / 247,481 |

## By category

| Category | Passed |
|---|---|
| adversarial | 6/6 |
| ambiguous | 9/9 |
| known_failure | 0/6 |
| missing_info | 6/6 |
| out_of_scope | 12/12 |
| success | 45/45 |

## Cases

| Case | Workflow | Category | Expected | Actual | Pass | Supported | Latency | Cost |
|---|---|---|---|---|---|---|---|---|
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 57.27s | $0.1369 |
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 26.92s | $0.0680 |
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 26.69s | $0.0716 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 29.47s | $0.0774 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 23.81s | $0.0577 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 20.73s | $0.0582 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 24.02s | $0.0562 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 25.0s | $0.0571 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 23.24s | $0.0527 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 33.85s | $0.0721 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 51.72s | $0.1244 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 26.33s | $0.0616 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 44.13s | $0.1160 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 16.01s | $0.0489 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 46.67s | $0.1308 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 19.11s | $0.0478 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 46.89s | $0.1168 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 23.58s | $0.0559 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 54.26s | $0.1263 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 28.79s | $0.0667 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 23.74s | $0.0614 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 30.28s | $0.0636 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 27.65s | $0.0648 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 22.29s | $0.0523 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 26.2s | $0.0565 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 29.54s | $0.0627 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 23.26s | $0.0525 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.38s | $0.0002 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.26s | $0.0002 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.41s | $0.0002 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.33s | $0.0002 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.24s | $0.0002 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.23s | $0.0002 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.04s | $0.0002 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 0.95s | $0.0002 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.06s | $0.0002 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 0.97s | $0.0002 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 24.65s | $0.0660 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 46.89s | $0.1319 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 26.17s | $0.0695 |
| st-multi-product | static | known_failure | answer | escalate | **no** | 0.857 | 92.11s | $0.2102 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 27.78s | $0.0650 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 26.74s | $0.0671 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 18.9s | $0.0502 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 14.65s | $0.0437 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 37.91s | $0.1015 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 17.67s | $0.0449 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 17.86s | $0.0491 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 19.19s | $0.0503 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 17.21s | $0.0442 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 15.7s | $0.0462 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 30.2s | $0.0933 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 30.2s | $0.0466 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 26.67s | $0.0394 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 25.72s | $0.0441 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 31.44s | $0.0464 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 15.19s | $0.0208 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 16.8s | $0.0201 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 20.73s | $0.0468 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 47.28s | $0.1015 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 22.69s | $0.0497 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.29s | $0.0003 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.22s | $0.0003 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.4s | $0.0003 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.83s | $0.0003 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.83s | $0.0003 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.96s | $0.0003 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.9s | $0.0003 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.85s | $0.0003 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.88s | $0.0003 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.1s | $0.0004 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.1s | $0.0004 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.69s | $0.0004 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.47s | $0.0004 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.88s | $0.0003 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.45s | $0.0003 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 27.59s | $0.0650 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 59.34s | $0.1319 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 54.15s | $0.1275 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 18.25s | $0.0293 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 21.09s | $0.0348 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 24.03s | $0.0382 |

## Failures (6)

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → draft → verify → escalate
- outcome escalate not in ['answer']
- missing sections ['1005.6', '1026.12']
- Response:

  > Escalated to a human specialist. Draft failed verification after 3 attempts:
  > - Unsupported claim: 'Regulation E (12 CFR 1005.11) sets out procedures for resolving errors in electronic fund transfers,' (The excerpt is titled as Regulation E procedures for resolving errors, but it does not say that unauthorized transfers count as errors or that the procedures apply to this customer's debit card or c…

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → human_review
- missing sections ['1005.6', '1026.12']
- Response:

  > I'm sorry a thief used both your credit card and your debit card, and that neither dispute has been resolved. Our team will review the details of both disputes.
  >
  > Debit card (Regulation E): As a general rule, when an institution receives a notice of error, it must provisionally credit the amount of the alleged error within 10 business days. If it has a reasonable basis to believe an unauthorized tr…

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → human_review
- missing sections ['1005.6', '1026.12']
- Response:

  > We're sorry you're dealing with fraudulent charges on both your credit card and your checking account. We understand how stressful that is. This reply covers what the rules we have say about your credit card dispute.
  >
  > Under Regulation Z, a billing error includes a charge on your statement for credit not made to you or to someone with authority to use your card [R-1026.13#1]. To start the formal pr…

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Response:

  > The evidence provided does not include the official staff commentary, so I cannot say what the commentary concludes about a family member who exceeds a permitted amount. The regulation text does define the term. "Unauthorized use" means use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the use, and from which the cardholder rece…

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Response:

  > The evidence does not include the Regulation Z official staff commentary, so I can't say what it states about a family member who exceeds the permitted amount. The regulation text itself defines "unauthorized use" as use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the use, and from which the cardholder receives no benefit [R-1…

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Response:

  > The evidence provided does not include the official staff commentary, so I cannot say how the commentary treats a family member who exceeds the permitted amount. The regulation text defines the term. "Unauthorized use" means use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the use, and from which the cardholder receives no bene…

## Retrieval score calibration

Current floor REG_MIN_SCORE = 0.45.

- Best regulation score per run: min 0.543, median 0.673, max 0.738
- Lowest best score among in-scope runs: 0.543 (floor 0.45 should stay below this)
