# Evaluation report: 2026-11-08, 21:05

Context config **lean**, repeats 3, models `claude-haiku-5-5` (classify/route) and `claude-sonnet-5-5` (draft/verify). Cost uses the prices in .env.

## Summary

| Metric | Result |
|---|---|
| Cases passed | 78/84 (93%) |
| Correct outcome (answer/clarify/abstain/escalate) | 81/84 (96%) |
| Classification accuracy | 30/30 (100%) |
| Retrieval hit (expected section retrieved) | 45/45 (100%) |
| Citation hit (answer cites expected section) | 45/45 (100%) |
| Multi-section retrieval | 0/3 (0%) |
| Dynamic routing used expected tool | 15/15 (100%) |
| No forbidden content (injection / false premise) | 6/6 (100%) |
| Mean supported-claim ratio (answered) | 1.0 |
| Runs where the verifier forced a redraft/replan | 20 |
| Outcome consistency across repeats | 1.0 |
| Latency mean / p95 | 22.05s / 56.92s |
| Cost total / per run | $4.3169 / $0.05139 |
| Tokens in / out | 1,286,565 / 254,424 |

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
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 58.7s | $0.1401 |
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 28.11s | $0.0674 |
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 25.94s | $0.0649 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 22.32s | $0.0606 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 23.81s | $0.0592 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 28.28s | $0.0696 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 25.99s | $0.0575 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 22.34s | $0.0548 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 67.6s | $0.1655 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 30.87s | $0.0648 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 56.26s | $0.1296 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 22.46s | $0.0575 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 56.92s | $0.1706 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 62.27s | $0.1778 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 47.31s | $0.1263 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 23.58s | $0.0556 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 21.78s | $0.0529 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 24.63s | $0.0537 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 28.94s | $0.0628 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 27.06s | $0.0636 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 24.29s | $0.0534 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 38.62s | $0.0984 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 18.35s | $0.0485 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 41.98s | $0.1035 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 24.17s | $0.0547 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 18.02s | $0.0450 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 24.36s | $0.0564 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.57s | $0.0002 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.57s | $0.0002 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.57s | $0.0002 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.57s | $0.0002 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.57s | $0.0002 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.31s | $0.0002 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.0s | $0.0002 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.01s | $0.0002 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.76s | $0.0002 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.23s | $0.0002 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.13s | $0.0002 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.15s | $0.0002 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 45.94s | $0.1237 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 38.47s | $0.1180 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 24.44s | $0.0657 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 91.23s | $0.2069 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 56.1s | $0.1305 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 55.06s | $0.1273 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 14.67s | $0.0427 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 20.45s | $0.0505 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 12.86s | $0.0412 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 20.94s | $0.0481 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 18.22s | $0.0477 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 38.15s | $0.1104 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 29.06s | $0.0823 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 17.07s | $0.0421 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 34.23s | $0.0945 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 16.63s | $0.0261 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 19.99s | $0.0343 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 16.79s | $0.0262 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 21.41s | $0.0270 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 38.07s | $0.0556 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 21.26s | $0.0261 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 20.2s | $0.0339 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 27.95s | $0.0501 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 34.34s | $0.0917 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.41s | $0.0003 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.47s | $0.0003 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.31s | $0.0003 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.33s | $0.0003 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0003 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.07s | $0.0003 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.33s | $0.0003 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.26s | $0.0003 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.26s | $0.0003 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.65s | $0.0003 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.0s | $0.0004 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.15s | $0.0004 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.58s | $0.0003 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.82s | $0.0003 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.58s | $0.0003 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 25.5s | $0.0654 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 23.33s | $0.0516 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 55.07s | $0.1290 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 24.02s | $0.0399 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 12.59s | $0.0266 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 44.81s | $0.0797 |

## Failures (6)

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → draft → verify → human_review
- missing sections ['1005.6', '1026.12']
- Cited: `R-1005.11#2` 12 CFR 1005.11(c)-(d) Procedures for resolving errors.
- Response:

  > I'm sorry you're dealing with fraud on two accounts, and that neither dispute has been resolved. Here is how the process works.
  >
  > Debit card (checking account): Regulation E sets error-resolution procedures. Generally, the bank must provisionally credit the account for the alleged error within 10 business days of receiving the error notice [R-1005.11#2]. If it has a reasonable basis to believe an u…

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → human_review
- missing sections ['1005.6', '1026.12']
- Cited: `R-1026.13#2` 12 CFR 1026.13(d)-(g) Billing error resolution.
- Cited: `R-1005.11#3` 12 CFR 1005.11(d)-(e) Procedures for resolving errors.
- Response:

  > I'm sorry you're dealing with fraudulent charges on both your credit card and your debit card, and that neither dispute has been resolved. This is general information about the rules, not a decision on your disputes. The details of each would need to be reviewed.
  >
  > Credit card (Regulation Z): You need not pay, and the creditor may not try to collect, any portion of a required payment you believe re…

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → human_review
- missing sections ['1005.6', '1026.12']
- Cited: `R-1005.11#2` 12 CFR 1005.11(c)-(d) Procedures for resolving errors.
- Cited: `R-1026.13#3` 12 CFR 1026.13(g)-(i) Billing error resolution.
- Response:

  > We are sorry you are dealing with fraudulent charges on both your credit card and your checking account. We understand how stressful this is. Our team will review both disputes.
  >
  > For your debit card, Regulation E sets out error-resolution steps. Once an error notice is received, the institution generally provisionally credits the account within 10 business days, and may withhold a maximum of $50 i…

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Cited: `R-1026.12#1` 12 CFR 1026.12(a)-(b) Special credit card provisions.
- Response:

  > The evidence provided does not include the official staff commentary, so I can't say how the commentary treats a family member who was given the card but exceeded the permitted amount. What the regulation text itself says is below.
  >
  > Regulation Z defines "unauthorized use" as use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the…

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Cited: `R-1026.12#1` 12 CFR 1026.12(a)-(b) Special credit card provisions.
- Response:

  > The evidence provided does not include the Regulation Z official staff commentary, so I can't say what it says about a family member who exceeds a permitted amount. The regulation text defines "unauthorized use" as use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the use, and from which the cardholder receives no benefit [R-102…

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → replan → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Cited: `R-1026.12#1` 12 CFR 1026.12(a)-(b) Special credit card provisions.
- Response:

  > The evidence provided does not include the Regulation Z official staff commentary, so I can't say what the commentary concludes about a family member who was given the card but exceeded the permitted amount.
  >
  > What the regulation text says: "unauthorized use" means use of a credit card by a person, other than the cardholder, who does not have actual, implied, or apparent authority for the use, and…

## Retrieval score calibration

Current floor REG_MIN_SCORE = 0.45.

- Best regulation score per run: min 0.592, median 0.668, max 0.777
- Lowest best score among in-scope runs: 0.592 (floor 0.45 should stay below this)
