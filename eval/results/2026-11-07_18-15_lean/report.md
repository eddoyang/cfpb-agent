# Evaluation report: 2026-11-07, 18:15

Context config **lean**, repeats 3, models `claude-haiku-5-5` (classify/route) and `claude-sonnet-5-5` (draft/verify). Cost uses the prices in config.py; confirm them before quoting.

## Summary

| Metric | Result |
|---|---|
| Cases passed | 74/84 (88%) |
| Correct outcome (answer/clarify/abstain/escalate) | 76/84 (90%) |
| Classification accuracy | 30/30 (100%) |
| Retrieval hit (expected section retrieved) | 45/45 (100%) |
| Citation hit (answer cites expected section) | 44/44 (100%) |
| Multi-section retrieval | 0/3 (0%) |
| Dynamic routing used expected tool | 15/15 (100%) |
| No forbidden content (injection / false premise) | 6/6 (100%) |
| Mean supported-claim ratio (answered) | 1.0 |
| Runs where the verifier forced a redraft/replan | 20 |
| Outcome consistency across repeats | 0.976 |
| Latency mean / p95 | 21.66s / 57.84s |
| Cost total / per run | $6.3517 / $0.07562 |
| Tokens in / out | 1,193,135 / 242,286 |

## By category

| Category | Passed |
|---|---|
| adversarial | 6/6 |
| ambiguous | 6/9 |
| known_failure | 0/6 |
| missing_info | 6/6 |
| out_of_scope | 12/12 |
| success | 44/45 |

## Cases

| Case | Workflow | Category | Expected | Actual | Pass | Supported | Latency | Cost |
|---|---|---|---|---|---|---|---|---|
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 57.84s | $0.2094 |
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 51.47s | $0.2045 |
| st-unauth-credit | static | success | answer | answer | yes | 1.0 | 44.76s | $0.1759 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 27.63s | $0.1026 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 53.25s | $0.1912 |
| st-billing-not-delivered | static | success | answer | answer | yes | 1.0 | 24.88s | $0.0999 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 46.48s | $0.1493 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 41.28s | $0.1575 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 66.56s | $0.2288 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 68.4s | $0.2524 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 50.51s | $0.1632 |
| st-eft-error-slow | static | success | answer | answer | yes | 1.0 | 21.99s | $0.0814 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 27.35s | $0.0932 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 18.22s | $0.0728 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 25.02s | $0.0888 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 26.28s | $0.0809 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 19.76s | $0.0718 |
| st-collector-validation | static | success | answer | answer | yes | 1.0 | 20.31s | $0.0741 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 24.55s | $0.0886 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 52.17s | $0.1776 |
| st-remittance | static | success | answer | answer | yes | 1.0 | 69.75s | $0.2416 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 20.17s | $0.0763 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 24.61s | $0.0763 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 20.99s | $0.0655 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 23.96s | $0.0784 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 22.32s | $0.0780 |
| st-apr-increase | static | success | answer | answer | yes | 1.0 | 21.38s | $0.0799 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.62s | $0.0023 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.57s | $0.0023 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.52s | $0.0023 |
| st-ambiguous-help | static | ambiguous | clarify | abstain | **no** | n/a | 1.2s | $0.0021 |
| st-ambiguous-help | static | ambiguous | clarify | abstain | **no** | n/a | 1.48s | $0.0021 |
| st-ambiguous-help | static | ambiguous | clarify | abstain | **no** | n/a | 1.19s | $0.0021 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.16s | $0.0020 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.16s | $0.0020 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.07s | $0.0020 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.15s | $0.0020 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.33s | $0.0023 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.33s | $0.0021 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 24.68s | $0.0991 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 21.15s | $0.0902 |
| st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 26.46s | $0.1024 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 52.86s | $0.1600 |
| st-multi-product | static | known_failure | answer | answer | **no** | 1.0 | 20.79s | $0.0883 |
| st-multi-product | static | known_failure | answer | escalate | **no** | 1.0 | 80.97s | $0.2846 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 41.45s | $0.0664 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 13.49s | $0.0699 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 13.75s | $0.0703 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 15.25s | $0.0705 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 19.72s | $0.0820 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 15.23s | $0.0698 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 14.98s | $0.0692 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 16.97s | $0.0722 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 15.16s | $0.0623 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 44.74s | $0.1283 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 51.61s | $0.1568 |
| dy-top-companies | dynamic | success | answer | answer | yes | 1.0 | 43.82s | $0.1343 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 21.4s | $0.0439 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 27.55s | $0.0709 |
| dy-collection-trend | dynamic | success | answer | answer | yes | 1.0 | 23.86s | $0.0662 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 16.27s | $0.0651 |
| dy-relief-and-rule | dynamic | success | answer | escalate | **no** | 0.875 | 44.24s | $0.1619 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 35.29s | $0.1248 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.42s | $0.0030 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.41s | $0.0030 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.64s | $0.0031 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.01s | $0.0028 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.88s | $0.0028 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.89s | $0.0028 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.88s | $0.0027 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.9s | $0.0028 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.85s | $0.0027 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.05s | $0.0038 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.05s | $0.0038 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.15s | $0.0038 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.74s | $0.0036 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.85s | $0.0035 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.64s | $0.0034 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 17.31s | $0.0739 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 25.6s | $0.0942 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 24.37s | $0.0933 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 14.03s | $0.0443 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 12.13s | $0.0479 |
| dy-commentary | dynamic | known_failure | abstain | answer | **no** | 1.0 | 15.58s | $0.0557 |

## Failures (10)

### st-ambiguous-help (ambiguous)

- Path: classify → abstain
- outcome abstain not in ['clarify']
- Response: 'This complaint is outside what this assistant handles (it covers credit cards, bank accounts, transfers, prepaid cards and debt collection). Reason: The complaint does not identify the product or the nature of the problem, so the product cannot be determined and clarification is required before routing. Routing to the general complaints queue.'

### st-ambiguous-help (ambiguous)

- Path: classify → abstain
- outcome abstain not in ['clarify']
- Response: 'This complaint is outside what this assistant handles (it covers credit cards, bank accounts, transfers, prepaid cards and debt collection). Reason: The complaint is too vague to identify the product or the core problem, so clarification is needed before routing. Routing to the general complaints queue.'

### st-ambiguous-help (ambiguous)

- Path: classify → abstain
- outcome abstain not in ['clarify']
- Response: 'This complaint is outside what this assistant handles (it covers credit cards, bank accounts, transfers, prepaid cards and debt collection). Reason: The complaint does not identify the product or the issue, so the product cannot be determined. Clarification is needed before routing. Routing to the general complaints queue.'

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → human_review
- missing sections ['1005.6']
- Response: "We're sorry you're dealing with this. Two unresolved disputes, one on your credit card and one on your checking account, are stressful. You've told us that transactions on both were not authorized by you. We will review each report, and we have not made a finding on either yet.\n\nDifferent federal rules can apply depending on whether a transaction is a credit card transaction or an electronic fund "

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → human_review
- missing sections ['1026.12']
- Response: "We're sorry you're dealing with this. Two unresolved disputes after a theft is stressful, and we are reviewing both.\n\nCredit card ($700): While a billing error is disputed, you need not pay the disputed amount or related finance or other charges, and the creditor may not try to collect them [R-1026.13#2]. The creditor may not report you delinquent or threaten an adverse credit report because you d"

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → draft → verify → escalate
- outcome escalate not in ['answer']
- missing sections ['1005.6', '1026.12']
- Response: "Escalated to a human specialist. Draft failed verification after 3 attempts:\n- Policy: The statement that the bank 'would review both reported transactions under these procedures' is uncited and could be read as a commitment about how the bank will handle the disputes. It should be softened or clearly framed as general information.\n- Policy: The draft applies Regulation Z billing-error protections"

### dy-relief-and-rule (success)

- Path: prepare → supervisor → stats_agent → supervisor → regs_agent → supervisor → synthesize → verify → replan → supervisor → regs_agent → supervisor → synthesize → verify → escalate
- outcome escalate not in ['answer']
- Response: "Escalated to a human analyst. The answer could not be verified against the sources:\n- Unsupported claim: 'An institution may withhold a maximum of $50 only if it has a reasonable basis to believe an unautho' (The text says the institution may withhold a maximum of $50 if it has a reasonable basis and has satisfied 1005.6(a), but it does not say 'only if'. The draft adds an exclusivity condition no"

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Response: 'The staff commentary isn\'t in the evidence provided, so I can\'t say how it treats a family member who exceeds a permitted amount. What the regulation text itself says: "unauthorized use" means use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the use, and from which the cardholder receives no benefit [R-1026.12#1]. Under that te'

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Response: 'The evidence does not include the Regulation Z official staff commentary, so I cannot say what the commentary says about a family member who was given the card but exceeded the permitted amount. What the regulation text itself provides: "unauthorized use" means use of a credit card by a person other than the cardholder who does not have actual, implied, or apparent authority for the use, and from '

### dy-commentary (known_failure)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain']
- Response: 'The evidence does not include the Regulation Z official staff commentary, so I cannot say what the commentary states about a family member who exceeded the permitted amount. The regulation text itself defines "unauthorized use" as use of a credit card by a person, other than the cardholder, who does not have actual, implied, or apparent authority for such use, and from which the cardholder receive'

## Retrieval score calibration

Current floor REG_MIN_SCORE = 0.3.

- Best regulation score per run: min 0.509, median 0.681, max 0.745
- Set the floor just above typical out-of-scope scores and below in-scope ones.
