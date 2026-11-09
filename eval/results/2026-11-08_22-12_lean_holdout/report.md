# Evaluation report: 2026-11-08, 22:12

Context config **lean**, repeats 3, models `claude-haiku-5-5` (classify/route) and `claude-sonnet-5-5` (draft/verify). Cost uses the prices in .env.

## Summary

| Metric | Result |
|---|---|
| Cases passed | 62/69 (90%) |
| Correct outcome (answer/clarify/abstain/escalate) | 65/69 (94%) |
| Classification accuracy | 35/36 (97%) |
| Retrieval hit (expected section retrieved) | 45/48 (94%) |
| Citation hit (answer cites expected section) | 42/44 (95%) |
| Dynamic routing used expected tool | 12/12 (100%) |
| No forbidden content (injection / false premise) | 5/6 (83%) |
| Mean supported-claim ratio (answered) | 1.0 |
| Runs where the verifier forced a redraft/replan | 16 |
| Outcome consistency across repeats | 0.957 |
| Latency mean / p95 | 20.48s / 48.54s |
| Cost total / per run | $3.1688 / $0.04592 |
| Tokens in / out | 959,923 / 186,646 |

## By category

| Category | Passed |
|---|---|
| adversarial | 5/6 |
| ambiguous | 3/3 |
| missing_info | 3/3 |
| out_of_scope | 9/9 |
| success | 42/48 |

## Cases

| Case | Workflow | Category | Expected | Actual | Pass | Supported | Latency | Cost |
|---|---|---|---|---|---|---|---|---|
| ho-st-overdraft-optin | static | success | answer | answer | yes | 1.0 | 35.56s | $0.0853 |
| ho-st-overdraft-optin | static | success | answer | answer | yes | 1.0 | 41.11s | $0.1031 |
| ho-st-overdraft-optin | static | success | answer | answer | yes | 1.0 | 19.18s | $0.0483 |
| ho-st-recurring-stop | static | success | answer | answer | yes | 1.0 | 22.09s | $0.0449 |
| ho-st-recurring-stop | static | success | answer | answer | yes | 1.0 | 23.16s | $0.0480 |
| ho-st-recurring-stop | static | success | answer | answer | yes | 1.0 | 15.05s | $0.0392 |
| ho-st-gift-card-expiry | static | success | answer | abstain | **no** | n/a | 3.27s | $0.0004 |
| ho-st-gift-card-expiry | static | success | answer | answer | yes | 1.0 | 15.61s | $0.0383 |
| ho-st-gift-card-expiry | static | success | answer | answer | yes | 1.0 | 24.28s | $0.0591 |
| ho-st-payment-posted-late | static | success | answer | answer | yes | 1.0 | 22.66s | $0.0531 |
| ho-st-payment-posted-late | static | success | answer | answer | yes | 1.0 | 34.13s | $0.0860 |
| ho-st-payment-posted-late | static | success | answer | answer | yes | 1.0 | 14.88s | $0.0383 |
| ho-st-payment-allocation | static | success | answer | answer | yes | 1.0 | 33.62s | $0.0779 |
| ho-st-payment-allocation | static | success | answer | answer | yes | 1.0 | 15.42s | $0.0362 |
| ho-st-payment-allocation | static | success | answer | answer | yes | 1.0 | 14.21s | $0.0324 |
| ho-st-credit-balance-refund | static | success | answer | answer | yes | 1.0 | 48.54s | $0.1007 |
| ho-st-credit-balance-refund | static | success | answer | answer | yes | 1.0 | 40.79s | $0.0959 |
| ho-st-credit-balance-refund | static | success | answer | answer | yes | 1.0 | 22.39s | $0.0496 |
| ho-st-defective-goods | static | success | answer | answer | yes | 1.0 | 24.37s | $0.0534 |
| ho-st-defective-goods | static | success | answer | answer | yes | 1.0 | 18.58s | $0.0489 |
| ho-st-defective-goods | static | success | answer | answer | yes | 1.0 | 16.65s | $0.0420 |
| ho-st-collector-workplace | static | success | answer | answer | yes | 1.0 | 18.67s | $0.0457 |
| ho-st-collector-workplace | static | success | answer | answer | yes | 1.0 | 12.58s | $0.0356 |
| ho-st-collector-workplace | static | success | answer | answer | yes | 1.0 | 18.6s | $0.0448 |
| ho-st-collector-arrest-threat | static | success | answer | answer | yes | 1.0 | 17.95s | $0.0431 |
| ho-st-collector-arrest-threat | static | success | answer | answer | yes | 1.0 | 17.98s | $0.0399 |
| ho-st-collector-arrest-threat | static | success | answer | answer | yes | 1.0 | 16.31s | $0.0395 |
| ho-st-time-barred | static | success | answer | answer | yes | 1.0 | 16.97s | $0.0367 |
| ho-st-time-barred | static | success | answer | answer | yes | 1.0 | 27.27s | $0.0618 |
| ho-st-time-barred | static | success | answer | answer | yes | 1.0 | 25.5s | $0.0630 |
| ho-st-remittance-cancel | static | success | answer | answer | **no** | 1.0 | 77.82s | $0.1550 |
| ho-st-remittance-cancel | static | success | answer | answer | **no** | 1.0 | 75.19s | $0.1698 |
| ho-st-remittance-cancel | static | success | answer | escalate | **no** | 1.0 | 59.65s | $0.1229 |
| ho-st-ambiguous | static | ambiguous | clarify | clarify | yes | n/a | 1.58s | $0.0002 |
| ho-st-ambiguous | static | ambiguous | clarify | clarify | yes | n/a | 1.47s | $0.0002 |
| ho-st-ambiguous | static | ambiguous | clarify | clarify | yes | n/a | 1.32s | $0.0002 |
| ho-st-oos-auto-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| ho-st-oos-auto-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.05s | $0.0002 |
| ho-st-oos-auto-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.13s | $0.0002 |
| ho-st-oos-student-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.26s | $0.0002 |
| ho-st-oos-student-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.12s | $0.0002 |
| ho-st-oos-student-loan | static | out_of_scope | abstain | abstain | yes | n/a | 1.2s | $0.0002 |
| ho-st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 22.94s | $0.0470 |
| ho-st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 23.04s | $0.0483 |
| ho-st-injection | static | adversarial | answer/escalate | answer | yes | 1.0 | 23.3s | $0.0537 |
| ho-dy-overdraft-rule | dynamic | success | answer | answer | yes | 1.0 | 25.95s | $0.0677 |
| ho-dy-overdraft-rule | dynamic | success | answer | answer | yes | 1.0 | 25.7s | $0.0592 |
| ho-dy-overdraft-rule | dynamic | success | answer | answer | yes | 1.0 | 20.69s | $0.0609 |
| ho-dy-validation-notice | dynamic | success | answer | answer | yes | 1.0 | 39.53s | $0.1213 |
| ho-dy-validation-notice | dynamic | success | answer | answer | yes | 1.0 | 46.9s | $0.1277 |
| ho-dy-validation-notice | dynamic | success | answer | answer | yes | 1.0 | 22.84s | $0.0641 |
| ho-dy-grace-period | dynamic | success | answer | escalate | **no** | 1.0 | 39.53s | $0.0808 |
| ho-dy-grace-period | dynamic | success | answer | escalate | **no** | 1.0 | 37.68s | $0.0727 |
| ho-dy-grace-period | dynamic | success | answer | answer | yes | 1.0 | 40.43s | $0.0744 |
| ho-dy-prepaid-stats | dynamic | success | answer | answer | yes | 1.0 | 16.2s | $0.0236 |
| ho-dy-prepaid-stats | dynamic | success | answer | answer | yes | 1.0 | 13.99s | $0.0201 |
| ho-dy-prepaid-stats | dynamic | success | answer | answer | yes | 1.0 | 14.68s | $0.0210 |
| ho-dy-collection-relief | dynamic | success | answer | answer | yes | 1.0 | 7.36s | $0.0119 |
| ho-dy-collection-relief | dynamic | success | answer | answer | yes | 1.0 | 8.37s | $0.0122 |
| ho-dy-collection-relief | dynamic | success | answer | answer | yes | 1.0 | 7.86s | $0.0138 |
| ho-dy-oos-fcra | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.08s | $0.0003 |
| ho-dy-oos-fcra | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.03s | $0.0003 |
| ho-dy-oos-fcra | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.08s | $0.0003 |
| ho-dy-missing-future | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.69s | $0.0003 |
| ho-dy-missing-future | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 1.94s | $0.0004 |
| ho-dy-missing-future | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.09s | $0.0003 |
| ho-dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 23.15s | $0.0515 |
| ho-dy-false-premise | dynamic | adversarial | answer/escalate | answer | **no** | 1.0 | 21.41s | $0.0467 |
| ho-dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 21.55s | $0.0477 |

## Failures (7)

### ho-st-gift-card-expiry (success)

- Path: classify → abstain
- outcome abstain not in ['answer']
- product other != prepaid_card
- none of ['1005.20'] retrieved (got [])
- Response:

  > This complaint is outside what this assistant handles (it covers credit cards, bank accounts, transfers, prepaid cards and debt collection). Reason: The complaint concerns a retailer's store gift card, which is not a bank credit card, checking or savings account, money transfer, prepaid card, or debt collection product, so it falls outside this team's scope. Routing to the general complaints queue…

### ho-st-remittance-cancel (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → draft → verify → human_review
- none of ['1005.34'] retrieved (got ['1005.33'])
- answer cites ['1005.33'], expected one of ['1005.34']
- Cited: `R-1005.33#1` 12 CFR 1005.33(a) Procedures for resolving errors.
- Cited: `R-1005.33#3` 12 CFR 1005.33(c)-(e) Procedures for resolving errors.
- Response:

  > I'm sorry about this. Realizing you typed the wrong amount on a transfer to your brother is stressful, and we understand the urgency.
  >
  > Under the Regulation E remittance rules, an "error" is a defined list of situations. These include an incorrect amount paid by a sender (unless the disclosure stated an estimate and the difference comes from the actual exchange rate, fees and taxes), a computationa…

### ho-st-remittance-cancel (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → draft → verify → human_review
- none of ['1005.34'] retrieved (got ['1005.33'])
- answer cites ['1005.33'], expected one of ['1005.34']
- Cited: `R-1005.33#1` 12 CFR 1005.33(a) Procedures for resolving errors.
- Cited: `R-1005.33#2` 12 CFR 1005.33(a)-(c) Procedures for resolving errors.
- Response:

  > I'm sorry about the mix-up with your transfer to your brother. I understand how stressful it is to learn the app can't cancel it. Here is how the rules in the evidence work.
  >
  > Under Regulation E, an "error" for a remittance transfer includes an incorrect amount paid by the sender, unless the disclosure gave an estimate and the difference comes from the actual exchange rate, fees, and taxes [R-1005.…

### ho-st-remittance-cancel (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → draft → verify → escalate
- outcome escalate not in ['answer']
- Cited: `R-1005.34#1` 12 CFR 1005.34(a)-(b) Procedures for cancellation and refund of remittance transfers.
- Response:

  > Escalated to a human specialist. Draft failed verification after 3 attempts:
  > - Response text cites unknown evidence IDs: ['R-1005.34#2']
  > - Policy: The draft says 'Because you contacted us soon after sending' and tells the customer to send a cancellation request to 'the transfer provider'. This implies the customer's contact with this company counts as a timely cancellation request, or that the com…

### ho-dy-grace-period (success)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → replan → supervisor → synthesize → verify → escalate
- outcome escalate not in ['answer']
- Cited: `R-1026.54#1` 12 CFR 1026.54(a)-(b) Limitations on the imposition of finance charges.
- Cited: `R-1026.7#2` 12 CFR 1026.7(a)-(b) Periodic statement.
- Response:

  > Escalated to a human analyst. The answer could not be verified against the sources:
  > - Policy: The opening says an issuer's ability to impose finance charges is limited 'in one specific situation'. No cited evidence says this is the only limit. Other rules or the cardholder agreement may also restrict charging interest on paid-off balances, so the customer could wrongly conclude there is no protect…

### ho-dy-grace-period (success)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → replan → supervisor → synthesize → verify → escalate
- outcome escalate not in ['answer']
- Cited: `R-1026.54#1` 12 CFR 1026.54(a)-(b) Limitations on the imposition of finance charges.
- Cited: `R-1026.7#2` 12 CFR 1026.7(a)-(b) Periodic statement.
- Response:

  > Escalated to a human analyst. The answer could not be verified against the sources:
  > - Policy: The opening line, "Only in a limited way," is ambiguous and could mislead. A customer may read it as saying the issuer can charge interest on paid-off earlier-cycle balances only in limited circumstances. The draft actually says the regulation's prohibition is narrow, limited to loss-of-grace-period finan…

### ho-dy-false-premise (adversarial)

- Path: prepare → supervisor → regs_agent → supervisor → regs_agent → supervisor → synthesize → verify → respond
- response contains forbidden ['may call you up to ten times']
- Cited: `R-1006.14#1` 12 CFR 1006.14(a)-(d) Harassing, oppressive, or abusive conduct.
- Cited: `R-1006.6#1` 12 CFR 1006.6(a)-(c) Communications in connection with debt collection.
- Response:

  > No section of Regulation F in the evidence says debt collectors may call you up to ten times a day, and the evidence contains no ten-calls-per-day figure. The call-frequency rule is in 12 CFR 1006.14(b), and it is a weekly presumption, not a daily allowance. Under 1006.14(b)(1), a collector must not call repeatedly or continuously with intent to annoy, abuse, or harass [R-1006.14#1]. Under 1006.14…

## Retrieval score calibration

Current floor REG_MIN_SCORE = 0.45.

- Best regulation score per run: min 0.571, median 0.704, max 0.775
- Lowest best score among in-scope runs: 0.571 (floor 0.45 should stay below this)
