"""STATIC workflow: complaint triage with a fixed sequence of steps.

  classify -> retrieve_regs -> retrieve_cases -> draft -> verify -> human_review
                |                    |                       |
         abstain / clarify       escalate        redraft (max 2) / escalate

The order never changes. The only branches are guardrails: out of scope, unclear,
weak evidence, failed verification, or a node error.
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

import config
from graphs.common import traced
from skills import classify, draft, retrieve_cases, retrieve_regulations, verify
from skills.schemas import Draft


class TriageState(TypedDict, total=False):
    request: str
    exclude_complaint_id: int | None
    classification: dict
    evidence: list[dict]
    retrieval: dict
    draft: dict
    context_ids: list[str]
    verification: dict
    attempts: int
    outcome: str  # answer | clarify | abstain | escalate | rejected
    final_response: str
    escalation_reason: str
    review: dict
    failed: bool
    trace: Annotated[list[dict], operator.add]
    errors: Annotated[list[str], operator.add]


def build_static_graph(rt):
    # ---------------------------------------------------------------- nodes
    @traced("classify")
    def classify_node(s: TriageState):
        c = classify(rt, s["request"])
        return {
            "classification": c.model_dump(),
            "attempts": 0,
            "_detail": f"{c.product} | {c.issue} | parts={c.regulation_parts} | "
            f"priority={c.priority} | in_scope={c.in_scope} | "
            f"unclear={c.needs_clarification}",
        }

    @traced("retrieve_regulations")
    def regs_node(s: TriageState):
        c = s["classification"]
        res = retrieve_regulations(
            rt, f"{c['search_query']} ({c['issue']})", parts=c["regulation_parts"]
        )
        return {
            "evidence": res["evidence"],
            "retrieval": {
                "regs": {"best_score": res["best_score"], "sufficient": res["sufficient"]}
            },
            "_detail": f"{res['n_kept']}/{res['n_retrieved']} chunks above floor, "
            f"best={res['best_score']}",
        }

    @traced("retrieve_similar_cases")
    def cases_node(s: TriageState):
        product = s["classification"]["product"]
        keyword = config.PRODUCT_CATEGORIES[product]["keyword"]
        res = retrieve_cases(
            rt,
            s["request"][:4000],
            product_keyword=keyword,
            exclude_id=s.get("exclude_complaint_id"),
        )
        retrieval = dict(s.get("retrieval", {}))
        retrieval["cases"] = {"best_score": res["best_score"]}
        return {
            "evidence": s["evidence"] + res["evidence"],
            "retrieval": retrieval,
            "_detail": f"{res['n_kept']} similar complaints, best={res['best_score']}",
        }

    @traced("draft")
    def draft_node(s: TriageState):
        attempt = s.get("attempts", 0) + 1
        feedback = s["verification"]["feedback"] if attempt > 1 else None
        d, used = draft(
            rt,
            s["request"],
            s["evidence"],
            mode="customer_reply",
            classification=s["classification"],
            feedback=feedback,
        )
        return {
            "draft": d.model_dump(),
            "context_ids": [e["id"] for e in used],
            "attempts": attempt,
            "_detail": f"attempt {attempt}: {len(d.claims)} claims, "
            f"{len(used)} evidence items in context"
            + (" (redraft with verifier feedback)" if feedback else ""),
        }

    @traced("verify")
    def verify_node(s: TriageState):
        used = [e for e in s["evidence"] if e["id"] in set(s["context_ids"])]
        v = verify(rt, Draft(**s["draft"]), used, request=s["request"])
        return {
            "verification": v,
            "_detail": ("PASS" if v["passed"] else f"FAIL: {len(v['issues'])} issues")
            + f", supported={v['supported_ratio']}",
        }

    @traced("human_review")
    def review_node(s: TriageState):
        if rt.require_approval:
            decision = interrupt(
                {
                    "draft": s["draft"]["response"],
                    "verification": s["verification"],
                    "classification": s["classification"],
                }
            )
        else:
            decision = {"approved": True, "reviewer": "auto (approval disabled)"}
        if decision.get("approved"):
            text = decision.get("edited_response") or s["draft"]["response"]
            return {
                "outcome": "answer",
                "final_response": text,
                "review": decision,
                "_detail": f"approved by {decision.get('reviewer', 'reviewer')}",
            }
        return {
            "outcome": "rejected",
            "final_response": "",
            "review": decision,
            "_detail": f"rejected: {decision.get('note', '')}",
        }

    @traced("abstain")
    def abstain_node(s: TriageState):
        c = s["classification"]
        return {
            "outcome": "abstain",
            "final_response": (
                "This complaint is outside what this assistant handles "
                f"(it covers credit cards, bank accounts, transfers, prepaid "
                f"cards and debt collection). Reason: {c['rationale']} "
                "Routing to the general complaints queue."
            ),
            "_detail": "out of scope",
        }

    @traced("clarify")
    def clarify_node(s: TriageState):
        q = s["classification"].get("clarifying_question") or (
            "Could you tell us which product this is about (credit card, bank account, "
            "transfer, prepaid card, or a debt collector) and what happened?"
        )
        return {"outcome": "clarify", "final_response": q, "_detail": "asked for details"}

    @traced("escalate")
    def escalate_node(s: TriageState):
        if s.get("errors"):
            reason = f"System error: {s['errors'][-1]}"
        elif s.get("retrieval", {}).get("regs", {}).get("sufficient") is False:
            reason = (
                "No regulation passed the relevance threshold "
                f"(best score {s['retrieval']['regs']['best_score']})."
            )
        elif s.get("draft", {}).get("insufficient_evidence"):
            reason = "The drafter reported that the evidence does not cover this complaint."
        else:
            reason = (
                "Draft failed verification after "
                f"{s.get('attempts', 0)} attempts:\n{s.get('verification', {}).get('feedback', '')}"
            )
        return {
            "outcome": "escalate",
            "escalation_reason": reason,
            "final_response": f"Escalated to a human specialist. {reason}",
            "_detail": reason.splitlines()[0],
        }

    # ---------------------------------------------------------------- routing
    def after_classify(s):
        if s.get("failed"):
            return "escalate"
        c = s["classification"]
        # Clarify before abstaining: a vague complaint has an unknown product, which the
        # classifier may also mark out of scope.
        if c["needs_clarification"]:
            return "clarify"
        if not c["in_scope"]:
            return "abstain"
        return "retrieve_regulations"

    def ok_then(nxt):
        return lambda s: "escalate" if s.get("failed") else nxt

    def after_cases(s):
        if s.get("failed") or not s["retrieval"]["regs"]["sufficient"]:
            return "escalate"
        return "draft"

    def after_verify(s):
        if s.get("failed") or s["draft"].get("insufficient_evidence"):
            return "escalate"
        if s["verification"]["passed"]:
            return "human_review"
        if s["attempts"] <= config.MAX_REDRAFTS:
            return "draft"
        return "escalate"

    # ---------------------------------------------------------------- graph
    g = StateGraph(TriageState)
    for name, fn in [
        ("classify", classify_node),
        ("retrieve_regulations", regs_node),
        ("retrieve_similar_cases", cases_node),
        ("draft", draft_node),
        ("verify", verify_node),
        ("human_review", review_node),
        ("abstain", abstain_node),
        ("clarify", clarify_node),
        ("escalate", escalate_node),
    ]:
        g.add_node(name, fn)
    g.add_edge(START, "classify")
    g.add_conditional_edges(
        "classify", after_classify, ["retrieve_regulations", "abstain", "clarify", "escalate"]
    )
    g.add_conditional_edges(
        "retrieve_regulations",
        ok_then("retrieve_similar_cases"),
        ["retrieve_similar_cases", "escalate"],
    )
    g.add_conditional_edges("retrieve_similar_cases", after_cases, ["draft", "escalate"])
    g.add_conditional_edges("draft", ok_then("verify"), ["verify", "escalate"])
    g.add_conditional_edges("verify", after_verify, ["human_review", "draft", "escalate"])
    for terminal in ["human_review", "abstain", "clarify", "escalate"]:
        g.add_edge(terminal, END)
    return g.compile(checkpointer=InMemorySaver())
