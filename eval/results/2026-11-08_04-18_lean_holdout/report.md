# Evaluation report: 2026-11-08, 04:18

Context config **lean**, repeats 3, models `claude-haiku-5-5` (classify/route) and `claude-sonnet-5-5` (draft/verify). Cost uses the prices in .env.

## Summary

| Metric | Result |
|---|---|
| Cases passed | 64/69 (93%) |
| Correct outcome (answer/clarify/abstain/escalate) | 66/69 (96%) |
| Classification accuracy | 34/36 (94%) |
| Retrieval hit (expected section retrieved) | 44/48 (92%) |
| Citation hit (answer cites expected section) | 43/45 (96%) |
| Dynamic routing used expected tool | 12/12 (100%) |
| No forbidden content (injection / false premise) | 6/6 (100%) |
| Mean supported-claim ratio (answered) | 1.0 |
| Runs where the verifier forced a redraft/replan | 15 |
| Outcome consistency across repeats | 0.971 |
| Latency mean / p95 | 20.92s / 62.57s |
| Cost total / per run | $3.325 / $0.04819 |
| Tokens in / out | 949,966 / 200,520 |

## By category

| Category | Passed |
|---|---|
| adversarial | 6/6 |
| ambiguous | 3/3 |
| missing_info | 3/3 |
| out_of_scope | 9/9 |
| success | 43/48 |

## Cases

| Case | Workflow | Category | Expected | Actual | Pass | Supported | Latency | Cost |
|---|---|---|---|---|---|---|---|---|
| ho-st-overdraft-optin | static | success | answer | answer | yes | 1.0 | 20.06s | $0.0440 |
| ho-st-overdraft-optin | static | success | answer | answer | yes | 1.0 | 62.57s | $0.1561 |
| ho-st-overdraft-optin | static | success | answer | answer | yes | 1.0 | 22.53s | $0.0489 |
| ho-st-recurring-stop | static | success | answer | answer | yes | 1.0 | 18.91s | $0.0410 |
| ho-st-recurring-stop | static | success | answer | answer | yes | 1.0 | 18.16s | $0.0388 |
| ho-st-recurring-stop | static | success | answer | answer | yes | 1.0 | 19.43s | $0.0387 |
| ho-st-gift-card-expiry | static | success | answer | answer | yes | 1.0 | 21.12s | $0.0478 |
| ho-st-gift-card-expiry | static | success | answer | abstain | **no** | n/a | 2.91s | $0.0004 |
| ho-st-gift-card-expiry | static | success | answer | abstain | **no** | n/a | 5.28s | $0.0006 |
| ho-st-payment-posted-late | static | success | answer | answer | yes | 1.0 | 19.04s | $0.0439 |
| ho-st-payment-posted-late | static | success | answer | answer | yes | 1.0 | 17.92s | $0.0423 |
| ho-st-payment-posted-late | static | success | answer | answer | yes | 1.0 | 38.29s | $0.0943 |
| ho-st-payment-allocation | static | success | answer | answer | yes | 1.0 | 55.57s | $0.1274 |
| ho-st-payment-allocation | static | success | answer | answer | yes | 1.0 | 39.16s | $0.0867 |
| ho-st-payment-allocation | static | success | answer | answer | yes | 1.0 | 15.05s | $0.0340 |
| ho-st-credit-balance-refund | static | success | answer | answer | yes | 1.0 | 68.15s | $0.1607 |
| ho-st-credit-balance-refund | static | success | answer | answer | yes | 1.0 | 24.71s | $0.0552 |
| ho-st-credit-balance-refund | static | success | answer | answer | yes | 1.0 | 24.08s | $0.0517 |
| ho-st-defective-goods | static | success | answer | answer | yes | 1.0 | 77.96s | $0.1902 |
| ho-st-defective-goods | static | success | answer | answer | yes | 1.0 | 16.87s | $0.0423 |
| ho-st-defective-goods | static | success | answer | answer | yes | 1.0 | 36.16s | $0.0913 |
| ho-st-collector-workplace | static | success | answer | answer | yes | 1.0 | 17.08s | $0.0428 |
| ho-st-collector-workplace | static | success | answer | answer | yes | 1.0 | 16.38s | $0.0420 |
| ho-st-collector-workplace | static | success | answer | answer | yes | 1.0 | 16.89s | $0.0439 |
| ho-st-collector-arrest-threat | static | success | answer | answer | **no** | 1.0 | 64.93s | $0.1583 |
| ho-st-collector-arrest-threat | static | success | answer | answer | yes | 1.0 | 16.07s | $0.0420 |
| ho-st-collector-arrest-threat | static | success | answer | answer | yes | 1.0 | 18.14s | $0.0432 |
| ho-st-time-barred | static | success | answer | answer | yes | 1.0 | 13.98s | $0.0321 |
| ho-st-time-barred | static | success | answer | answer | yes | 1.0 | 17.21s | $0.0360 |
| ho-st-time-barred | static | success | answer | answer | yes | 1.0 | 15.39s | $0.0364 |
| ho-st-remittance-cancel | static | success | answer | answer | yes | 1.0 | 48.03s | $0.0944 |
| ho-st-remittance-cancel | static | success | answer | answer | **no** | 1.0 | 23.9s | $0.0556 |
| ho-st-remittance-cancel | static | success | answer | answer | yes | 1.0 | 19.61s | $0.0367 |
| ho-st-ambiguous | static | ambiguous | clarify | clarify | yes | n/a | 1.65s | $0.0002 |
| ho-st-ambiguous | static | ambiguous | clarify | clarify | yes | n/a | 1.25s | $0.0002 |
| ho-st-ambiguous | static | ambiguous | clarify | clarify | yes | n/a | 1.27s | $0.0002 |
| ho-st-oos-auto-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| ho-st-oos-auto-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| ho-st-oos-auto-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| ho-st-oos-student-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| ho-st-oos-student-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| ho-st-oos-student-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| ho-st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 42.78s | $0.1038 |
| ho-st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 37.11s | $0.0905 |
| ho-st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 49.62s | $0.1107 |
| ho-dy-overdraft-rule | dynamic | success | answer | answer | yes | 1.0 | 20.21s | $0.0607 |
| ho-dy-overdraft-rule | dynamic | success | answer | answer | yes | 1.0 | 21.73s | $0.0685 |
| ho-dy-overdraft-rule | dynamic | success | answer | answer | yes | 1.0 | 20.97s | $0.0679 |
| ho-dy-validation-notice | dynamic | success | answer | answer | yes | 1.0 | 28.01s | $0.0702 |
| ho-dy-validation-notice | dynamic | success | answer | answer | yes | 1.0 | 22.66s | $0.0649 |
| ho-dy-validation-notice | dynamic | success | answer | answer | yes | 1.0 | 21.16s | $0.0657 |
| ho-dy-grace-period | dynamic | success | answer | answer | yes | 1.0 | 39.63s | $0.0827 |
| ho-dy-grace-period | dynamic | success | answer | escalate | **no** | 1.0 | 43.73s | $0.0900 |
| ho-dy-grace-period | dynamic | success | answer | answer | yes | 1.0 | 36.85s | $0.0845 |
| ho-dy-prepaid-stats | dynamic | success | answer | answer | yes | 1.0 | 13.49s | $0.0190 |
| ho-dy-prepaid-stats | dynamic | success | answer | answer | yes | 1.0 | 13.99s | $0.0204 |
| ho-dy-prepaid-stats | dynamic | success | answer | answer | yes | 1.0 | 15.11s | $0.0210 |
| ho-dy-collection-relief | dynamic | success | answer | answer | yes | 1.0 | 8.29s | $0.0136 |
| ho-dy-collection-relief | dynamic | success | answer | answer | yes | 1.0 | 7.54s | $0.0133 |
| ho-dy-collection-relief | dynamic | success | answer | answer | yes | 1.0 | 8.04s | $0.0141 |
| ho-dy-oos-fcra | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.86s | $0.0003 |
| ho-dy-oos-fcra | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.95s | $0.0003 |
| ho-dy-oos-fcra | dynamic | out_of_scope | abstain | abstain | yes | n/a | 0.81s | $0.0003 |
| ho-dy-missing-future | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.84s | $0.0004 |
| ho-dy-missing-future | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.36s | $0.0003 |
| ho-dy-missing-future | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.63s | $0.0003 |
| ho-dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 19.29s | $0.0493 |
| ho-dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 24.17s | $0.0561 |
| ho-dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 19.68s | $0.0546 |

## Failures (5)

### ho-st-gift-card-expiry (success)

- Path: classify → abstain
- outcome abstain not in ['answer']
- product other != prepaid_card
- none of ['1005.20'] retrieved (got [])
- Response:

  > This complaint is outside what this assistant handles (it covers credit cards, bank accounts, transfers, prepaid cards and debt collection). Reason: The complaint concerns a retailer's store gift card, not a bank-issued prepaid card, bank account, credit card, money transfer, or debt collection, so it falls outside the products this team covers. Routing to the general complaints queue.

### ho-st-gift-card-expiry (success)

- Path: classify → abstain
- outcome abstain not in ['answer']
- product other != prepaid_card
- none of ['1005.20'] retrieved (got [])
- Response:

  > This complaint is outside what this assistant handles (it covers credit cards, bank accounts, transfers, prepaid cards and debt collection). Reason: The complaint concerns a retailer-issued store gift card, not a bank credit card, bank account, money transfer, prepaid card, or debt collection product, and no bank is named as issuer. Gift card fee and expiration rules exist under Reg E 1005.20, but…

### ho-st-collector-arrest-threat (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → draft → verify → human_review
- none of ['1006.18'] retrieved (got ['1006.14', '1006.22', '1006.30'])
- answer cites ['1006.14', '1006.22'], expected one of ['1006.18']
- Response:

  > We're sorry you received a voicemail like this; a threat of arrest and a demand for same-day payment can be frightening. Under Regulation F, a debt collector must not engage in conduct whose natural consequence is to harass, oppress, or abuse any person in connection with collecting a debt [R-1006.14#1]. A collector also must not use or threaten to use violence or other criminal means to harm a pe…

### ho-st-remittance-cancel (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → human_review
- none of ['1005.34'] retrieved (got ['1005.33'])
- answer cites ['1005.33'], expected one of ['1005.34']
- Response:

  > We're sorry about the stress of sending the wrong amount to your brother, and we understand why you want this sorted out quickly.
  >
  > Under the federal remittance rules, an "error" includes an incorrect amount paid by a sender in connection with a remittance transfer, unless the disclosure stated an estimate and the difference results from the actual exchange rate, fees, and taxes [R-1005.33#1]. Our…

### ho-dy-grace-period (success)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → replan → supervisor → synthesize → verify → escalate
- outcome escalate not in ['answer']
- Response:

  > Escalated to a human analyst. The answer could not be verified against the sources:
  > - Policy: The sentence "A balance in such a program may therefore be treated differently from the situation described above" is not among the numbered claims, and none of the cited text supports it. Nothing cited says deferred interest balances are exempt from or treated differently under §1026.54. This could misle…

## Retrieval score calibration

Current floor REG_MIN_SCORE = 0.45.

- Best regulation score per run: min 0.598, median 0.697, max 0.765
- Lowest best score among in-scope runs: 0.598 (floor 0.45 should stay below this)
