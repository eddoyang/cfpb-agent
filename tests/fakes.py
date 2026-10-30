"""Test doubles: an in-memory store and a scripted LLM runtime. They let the graphs,
skills and eval harness run end to end with no network, no API keys and no database."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from context import get_context_config
from runtime import LLMCall, Runtime

REG_1026_12 = {
    "id": "R-1026.12#1", "kind": "regulation", "section": "1026.12",
    "citation": "12 CFR 1026.12(b) Special credit card provisions.",
    "text": "12 CFR 1026.12 ... (b) The liability of a cardholder for unauthorized use of a "
            "credit card shall not exceed the lesser of $50 or the amount obtained.",
    "score": 0.58, "source_url": "https://www.ecfr.gov/current/title-12/section-1026.12",
    "meta": {}}
REG_1026_13 = {
    "id": "R-1026.13#1", "kind": "regulation", "section": "1026.13",
    "citation": "12 CFR 1026.13(a)-(b) Billing error resolution.",
    "text": "12 CFR 1026.13 ... A billing error notice is a written notice received by a "
            "creditor within 60 days after the creditor transmitted the first periodic statement.",
    "score": 0.52, "source_url": "https://www.ecfr.gov/current/title-12/section-1026.13",
    "meta": {}}
REG_1006_14 = {
    "id": "R-1006.14#1", "kind": "regulation", "section": "1006.14",
    "citation": "12 CFR 1006.14(b) Harassing, oppressive, or abusive conduct.",
    "text": "12 CFR 1006.14 ... a debt collector is presumed to violate this paragraph if it "
            "places telephone calls more than seven times within seven consecutive days.",
    "score": 0.55, "source_url": "https://www.ecfr.gov/current/title-12/section-1006.14",
    "meta": {}}
CASE_1 = {
    "id": "C-111", "kind": "complaint", "section": None,
    "citation": "CFPB complaint 111 (Credit card; Problem with a purchase; Closed with monetary relief)",
    "text": "I found a charge I did not make and the bank refused to remove it.",
    "score": 0.61, "source_url": "https://example.org/111", "meta": {}}


class FakeStore:
    def __init__(self, regs=None, cases=None, stats_rows=None, fail_on: set | None = None):
        self.regs = regs if regs is not None else [REG_1026_12, REG_1026_13, REG_1006_14]
        self.cases = cases if cases is not None else [CASE_1]
        self.stats_rows = stats_rows if stats_rows is not None else [
            {"grp": "2024-01", "value": 40, "n": 40}, {"grp": "2024-02", "value": 55, "n": 55}]
        self.fail_on = fail_on or set()
        self.calls: list[tuple] = []

    def _maybe_fail(self, op):
        self.calls.append(op)
        if op in self.fail_on:
            raise ConnectionError(f"simulated {op} failure")

    def search_regulations(self, query, k, parts=None):
        self._maybe_fail("regs")
        hits = [r for r in self.regs if not parts or r["section"].split(".")[0] in parts]
        return [dict(h) for h in hits[:k]]

    def search_complaints(self, query, k, product_keyword=None, exclude_id=None):
        self._maybe_fail("cases")
        return [dict(c) for c in self.cases[:k]]

    def run_readonly(self, sql, params):
        self._maybe_fail("stats")
        return list(self.stats_rows)


@dataclass
class FakeRuntime(Runtime):
    """`script(name, schema, system, user)` returns a schema instance (or dict)."""
    script: Callable = None
    calls: list[str] = field(default_factory=list)

    def structured(self, tier, schema, system, user, name):
        self.calls.append(name)
        out = self.script(name, schema, system, user)
        if isinstance(out, Exception):
            raise out
        out = out if isinstance(out, schema) else schema(**out)
        self.ledger.append(LLMCall(name, f"fake-{tier}", len(system + user) // 4, 50, 0.01))
        return out


def make_rt(script, store=None, context="lean", require_approval=False) -> FakeRuntime:
    return FakeRuntime(store=store or FakeStore(), ctx=get_context_config(context),
                       require_approval=require_approval, script=script)


# ---------------------------------------------------------------- canned outputs
def classification(**kw):
    base = {"in_scope": True, "product": "credit_card", "issue": "unauthorized charge",
                "regulation_parts": ["1026"], "priority": "high", "needs_clarification": False,
                "clarifying_question": None, "search_query": "unauthorized credit card charge liability",
                "rationale": "Credit card fraud dispute."}
    return {**base, **kw}


def good_draft(ids=("R-1026.12#1",)):
    return {"response": "We're sorry about the charge. Your liability for unauthorized use is "
                         f"limited to $50 [{ids[0]}]. We are reviewing your dispute.",
                "claims": [{"text": "Liability for unauthorized use is limited to $50.",
                         "citations": list(ids)}],
                "insufficient_evidence": False, "internal_notes": ""}


def bad_draft():
    return {"response": "We will refund you in full within 5 days [R-9999.1#1].",
                "claims": [{"text": "Refund within 5 days.", "citations": ["R-9999.1#1"]}],
                "insufficient_evidence": False, "internal_notes": ""}


def judge_all_supported(n=1):
    return {"verdicts": [{"claim_index": i, "supported": True, "reason": "ok"} for i in range(n)],
            "policy_issues": []}
