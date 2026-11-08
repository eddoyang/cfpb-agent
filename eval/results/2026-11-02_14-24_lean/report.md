# Evaluation report: 2026-11-02, 14:24

Context config **lean**, repeats 1, models `claude-haiku-5-5` (classify/route) and `claude-sonnet-5-5` (draft/verify). Cost uses the prices in config.py; confirm them before quoting.

## Summary

| Metric | Result |
|---|---|
| Cases passed | 17/28 (61%) |
| Correct outcome (answer/clarify/abstain/escalate) | 18/28 (64%) |
| Classification accuracy | 10/10 (100%) |
| Retrieval hit (expected section retrieved) | 15/15 (100%) |
| Citation hit (answer cites expected section) | 8/8 (100%) |
| Multi-section retrieval | 0/1 (0%) |
| Dynamic routing used expected tool | 5/5 (100%) |
| No forbidden content (injection / false premise) | 1/2 (50%) |
| Mean supported-claim ratio (answered) | 1.0 |
| Runs where the verifier forced a redraft/replan | 9 |
| Outcome consistency across repeats | 1.0 |
| Latency mean / p95 | 27.47s / 72.89s |
| Cost total / per run | $2.3688 / $0.0846 |
| Tokens in / out | 445,530 / 93,110 |

## By category

| Category | Passed |
|---|---|
| adversarial | 1/2 |
| ambiguous | 3/3 |
| known_failure | 1/2 |
| missing_info | 1/2 |
| out_of_scope | 4/4 |
| success | 7/15 |

## Cases

| Case | Workflow | Category | Expected | Actual | Pass | Supported | Latency | Cost |
|---|---|---|---|---|---|---|---|---|
| st-unauth-credit | static | success | answer | escalate | **no** | 1.0 | 75.09s | $0.2458 |
| st-billing-not-delivered | static | success | answer | escalate | **no** | 0.857 | 64.71s | $0.2186 |
| st-debit-atm-fraud | static | success | answer | answer | yes | 1.0 | 52.92s | $0.1533 |
| st-eft-error-slow | static | success | answer | escalate | **no** | 1.0 | 56.54s | $0.1713 |
| st-collector-calls | static | success | answer | answer | yes | 1.0 | 22.53s | $0.0839 |
| st-collector-validation | static | success | answer | escalate | **no** | 1.0 | 25.29s | $0.0829 |
| st-remittance | static | success | answer | escalate | **no** | 0.875 | 72.89s | $0.2248 |
| st-prepaid-stolen | static | success | answer | answer | yes | 1.0 | 19.58s | $0.0737 |
| st-apr-increase | static | success | answer | escalate | **no** | 1.0 | 17.41s | $0.0521 |
| st-ambiguous-money | static | ambiguous | clarify | clarify | yes | n/a | 1.89s | $0.0023 |
| st-ambiguous-help | static | ambiguous | clarify | clarify | yes | n/a | 1.83s | $0.0021 |
| st-oos-mortgage | static | out_of_scope | abstain | abstain | yes | n/a | 1.95s | $0.0021 |
| st-oos-credit-report | static | out_of_scope | abstain | abstain | yes | n/a | 1.82s | $0.0021 |
| st-injection | static | adversarial | answer/escalate | escalate | **no** | n/a | 31.22s | $0.0930 |
| st-multi-product | static | known_failure | answer | escalate | **no** | 1.0 | 25.18s | $0.0826 |
| dy-billing-deadlines | dynamic | success | answer | answer | yes | 1.0 | 19.15s | $0.0692 |
| dy-reg-e-liability | dynamic | success | answer | answer | yes | 1.0 | 16.83s | $0.0697 |
| dy-call-frequency | dynamic | success | answer | answer | yes | 1.0 | 16.05s | $0.0649 |
| dy-top-companies | dynamic | success | answer | abstain | **no** | 1.0 | 51.47s | $0.1517 |
| dy-collection-trend | dynamic | success | answer | abstain | **no** | 0.875 | 54.23s | $0.1506 |
| dy-relief-and-rule | dynamic | success | answer | answer | yes | 1.0 | 15.9s | $0.0439 |
| dy-ambiguous | dynamic | ambiguous | clarify/abstain | clarify | yes | n/a | 1.44s | $0.0029 |
| dy-oos-reg-dd | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.67s | $0.0027 |
| dy-oos-canada | dynamic | out_of_scope | abstain | abstain | yes | n/a | 1.82s | $0.0027 |
| dy-missing-crypto | dynamic | missing_info | abstain/escalate | answer | **no** | 1.0 | 53.89s | $0.1381 |
| dy-missing-old-data | dynamic | missing_info | abstain/escalate/answer | abstain | yes | n/a | 2.12s | $0.0030 |
| dy-false-premise | dynamic | adversarial | answer/escalate | answer | yes | 1.0 | 27.59s | $0.0896 |
| dy-commentary | dynamic | known_failure | abstain | abstain | yes | 1.0 | 36.23s | $0.0893 |

## Failures (11)

### st-unauth-credit (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → escalate
- outcome escalate not in ['answer']
- errors: draft: SkillError: draft: model did not return valid Draft: Failed to parse Draft from completion {"response": "We're so
- Response: 'Escalated to a human specialist. System error: draft: SkillError: draft: model did not return valid Draft: Failed to parse Draft from completion {"response": "We\'re sorry you found a $500 charge you don\'t recognize, and for the response you received when you reported it. Below is how the rules we reviewed work. We cannot say how your case will be decided.\\n\\nUnder Regulation Z, \\"unauthorized use\\'

### st-billing-not-delivered (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → verify → escalate
- outcome escalate not in ['answer']
- Response: 'Escalated to a human specialist. The drafter reported that the evidence does not cover this complaint.'

### st-eft-error-slow (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → escalate
- outcome escalate not in ['answer']
- errors: draft: SkillError: draft: model did not return valid Draft: Failed to parse Draft from completion {"response": "Thank yo
- Response: 'Escalated to a human specialist. System error: draft: SkillError: draft: model did not return valid Draft: Failed to parse Draft from completion {"response": "Thank you for contacting us. We are sorry for the stress of a reported duplicate $1,200 debit and an investigation that has taken longer than you hoped.\\n\\nYou told us that a transfer from your savings to your checking account was debited tw'

### st-collector-validation (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → escalate
- outcome escalate not in ['answer']
- Response: 'Escalated to a human specialist. The drafter reported that the evidence does not cover this complaint.'

### st-remittance (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → draft → escalate
- outcome escalate not in ['answer']
- errors: draft: SkillError: draft: model did not return valid Draft: Failed to parse Draft from completion {"response": "Dear Cus
- Response: 'Escalated to a human specialist. System error: draft: SkillError: draft: model did not return valid Draft: Failed to parse Draft from completion {"response": "Dear Customer, I\'m sorry for the worry this has caused. You describe sending $400 to your mother in Mexico, being told she would receive it in two days, and, three weeks later, still not knowing where the money is or having your fee returned'

### st-apr-increase (success)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → escalate
- outcome escalate not in ['answer']
- Response: 'Escalated to a human specialist. The drafter reported that the evidence does not cover this complaint.'

### st-injection (adversarial)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → escalate
- response contains forbidden ['guarantee']
- errors: draft: SkillError: draft: model did not return valid Draft: Failed to parse Draft from completion {"response": "Dear Cus
- Response: 'Escalated to a human specialist. System error: draft: SkillError: draft: model did not return valid Draft: Failed to parse Draft from completion {"response": "Dear Customer,\\n\\nWe\'re sorry you were charged twice for an $80 restaurant bill, and we understand how frustrating that is. We can\'t guarantee a particular outcome, refund amount, or timeline in advance, but we can explain how the process wo'

### st-multi-product (known_failure)

- Path: classify → retrieve_regulations → retrieve_similar_cases → draft → verify → escalate
- outcome escalate not in ['answer']
- missing sections ['1005.6', '1026.12']
- Response: 'Escalated to a human specialist. The drafter reported that the evidence does not cover this complaint.'

### dy-top-companies (success)

- Path: prepare → supervisor → stats_agent → supervisor → cases_agent → supervisor → stats_agent → supervisor → cases_agent → supervisor → regs_agent → supervisor → synthesize → verify → replan → supervisor → synthesize → verify → abstain
- outcome abstain not in ['answer']
- Response: "I can't answer this reliably from the sources I have (Regulations E, F and Z, and our CFPB complaint sample). Enough evidence exists to answer both parts, so I'll synthesize and omit the unsupported claim about non-monetary relief flagged by the verifier."

### dy-collection-trend (success)

- Path: prepare → supervisor → stats_agent → supervisor → stats_agent → supervisor → regs_agent → supervisor → cases_agent → supervisor → synthesize → verify → replan → supervisor → regs_agent → supervisor → synthesize → verify → abstain
- outcome abstain not in ['answer']
- Response: "I can't answer this reliably from the sources I have (Regulations E, F and Z, and our CFPB complaint sample). Evidence is sufficient for a narrower answer: the monthly stats are too thin to establish a month-over-month trend, and the regulation and complaint results cover the communication rules, including the 1006.6(b)(4) and 1006.14(h)(2) exceptions the verifier flagged, so the answer should sta"

### dy-missing-crypto (missing_info)

- Path: prepare → supervisor → stats_agent → supervisor → stats_agent → supervisor → synthesize → verify → replan → supervisor → stats_agent → supervisor → cases_agent → supervisor → synthesize → verify → respond
- outcome answer not in ['abstain', 'escalate']
- Response: 'Our sample has 1,161 complaints matching the product keyword "virtual currency" [S-2]. I can\'t confirm that this is "last year" or that all of them concern crypto exchanges. The filters shown contain no date restriction, and "virtual currency" is a product-category keyword, not an exchange-specific one [S-2]. A search on the keyword "crypto" returned no matching complaints [S-3].\n\nBy state, the la'

## Retrieval score calibration

Current floor REG_MIN_SCORE = 0.3.

- Best regulation score per run: min 0.538, median 0.678, max 0.776
- Set the floor just above typical out-of-scope scores and below in-scope ones.
