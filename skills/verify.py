"""Two-layer verification.

Layer 1 (deterministic, free, always runs): every claim cites something, every cited
ID exists in the evidence the drafter actually saw, the response doesn't promise
outcomes, and inline [IDs] match the claim list.
Layer 2 (LLM judge, strong model): is each claim actually supported by the text of
the evidence it cites? This catches the subtle case: a real citation attached to a
claim the source doesn't say (e.g. a wrong deadline).
"""

from __future__ import annotations

import re

from ingest.tokens import truncate_tokens
from skills.schemas import Draft, JudgeOutput

PROMISE_PATTERNS = [
    r"\bwe will (refund|reimburse|credit|reverse)\b",
    r"\byou will (receive|get) (a )?(full )?(refund|reimbursement|credit)\b",
    r"\bguarantee[sd]?\b",
    r"\b100% (refund|reimburse)",
]
# A negation up to three words before a match ("we do not guarantee", "there is no
# guarantee", "we're not able to guarantee") is a disclaimer, not a promise.
NEGATED = re.compile(
    r"\b(no|not|never|cannot|can[’']?t|don[’']?t|doesn[’']?t|won[’']?t|isn[’']?t|"
    r"aren[’']?t|unable)\b(\W+\w+){0,3}\W*$",
    re.IGNORECASE,
)
INLINE_ID = re.compile(r"\[([RCS]-[^\]\s]+)\]")


def promises(text: str) -> list[str]:
    """Promise patterns that match somewhere without a negation just before them."""
    hits = []
    for pat in PROMISE_PATTERNS:
        for m in re.finditer(pat, text, re.IGNORECASE):
            before = re.split(r"[.,!?;:\n]", text[max(0, m.start() - 60) : m.start()])[-1]
            if not NEGATED.search(before):
                hits.append(pat)
                break
    return hits


JUDGE_SYSTEM = """You are a compliance reviewer checking a draft against its sources.
For each numbered claim, decide if the cited evidence text directly supports it.
A claim is NOT supported if it adds a number, deadline, condition, or right that the
cited text does not state, even if it is true in general. Be strict but fair:
paraphrase is fine. Also list policy issues: promising refunds or outcomes, stating legal
conclusions about this specific customer as certain, or an inappropriate tone."""


def judge_text(ev: dict, ctx) -> str:
    """The evidence text exactly as the drafter saw it. Regulation chunks go in whole
    (already capped at REG_CHUNK_MAX_TOKENS); narratives are clipped as in pack_evidence.
    Showing the judge less than the drafter makes correct claims look unsupported."""
    if ev["kind"] == "complaint":
        return truncate_tokens(ev["text"], ctx.max_case_tokens)
    return ev["text"]


def deterministic_checks(d: Draft, evidence: list[dict]) -> list[str]:
    ids = {e["id"] for e in evidence}
    issues = []
    if not d.claims and not d.insufficient_evidence:
        issues.append("The draft makes no cited claims.")
    for i, c in enumerate(d.claims):
        if not c.citations:
            issues.append(f"Claim {i} has no citation: '{c.text[:80]}'")
        bad = [x for x in c.citations if x not in ids]
        if bad:
            issues.append(f"Claim {i} cites evidence that was not provided: {bad}")
    inline_bad = sorted(set(INLINE_ID.findall(d.response)) - ids)
    if inline_bad:
        issues.append(f"Response text cites unknown evidence IDs: {inline_bad}")
    for pat in promises(d.response):
        issues.append(f"Response promises an outcome (matched '{pat}').")
    return issues


def verify(rt, d: Draft, evidence: list[dict], use_judge: bool = True) -> dict:
    issues = deterministic_checks(d, evidence)
    by_id = {e["id"]: e for e in evidence}
    unsupported: list[dict] = []
    verdicts: list[dict] = []

    if use_judge and d.claims:
        blocks = []
        for i, c in enumerate(d.claims):
            sources = (
                "\n".join(
                    f"  [{x}] {judge_text(by_id[x], rt.ctx)}" for x in c.citations if x in by_id
                )
                or "  (no valid sources)"
            )
            blocks.append(f"Claim {i}: {c.text}\nCited evidence:\n{sources}")
        user = "Draft response:\n" + d.response + "\n\nClaims to check:\n\n" + "\n\n".join(blocks)
        judge = rt.structured("strong", JudgeOutput, JUDGE_SYSTEM, user, name="verify")
        verdicts = [v.model_dump() for v in judge.verdicts]
        for v in judge.verdicts:
            if not v.supported and 0 <= v.claim_index < len(d.claims):
                unsupported.append({"claim": d.claims[v.claim_index].text, "reason": v.reason})
        issues += [f"Policy: {p}" for p in judge.policy_issues]

    n = len(d.claims)
    supported = n - len(unsupported)
    issues += [f"Unsupported claim: '{u['claim'][:100]}' ({u['reason']})" for u in unsupported]
    return {
        "passed": not issues,
        "issues": issues,
        "unsupported": unsupported,
        "verdicts": verdicts,
        "n_claims": n,
        "supported_ratio": round(supported / n, 3) if n else None,
        "cited_ids": sorted({x for c in d.claims for x in c.citations}),
        "feedback": "\n".join(f"- {i}" for i in issues),
    }
