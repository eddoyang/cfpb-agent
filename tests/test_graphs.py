"""Workflow behaviour tests: routing, retries, stopping conditions, error handling."""

from graphs.dynamic import apply_policy
from graphs.runner import resume_static, run_dynamic, run_static
from tests.fakes import (
    REG_1026_12,
    FakeStore,
    bad_draft,
    classification,
    good_draft,
    judge_all_supported,
    make_rt,
)

COMPLAINT = (
    "Someone charged $500 to my credit card. I reported it and the bank refused to refund me."
)


def script_static(cls=None, drafts=None, judge=None):
    drafts = list(drafts or [good_draft()])

    def script(name, schema, system, user):
        if name == "classify":
            return cls or classification()
        if name == "draft":
            return drafts.pop(0) if len(drafts) > 1 else drafts[0]
        if name == "verify":
            return judge or judge_all_supported()
        raise AssertionError(name)

    return script


# ---------------------------------------------------------------- static
def test_static_happy_path():
    r = run_static(make_rt(script_static()), COMPLAINT)
    assert r["outcome"] == "answer"
    assert r["path"] == [
        "classify",
        "retrieve_regulations",
        "retrieve_similar_cases",
        "draft",
        "verify",
        "human_review",
    ]
    assert r["citations"][0]["id"] == "R-1026.12#1"
    assert r["verification"]["passed"]
    assert r["usage"]["llm_calls"] == 3


def test_static_out_of_scope_abstains():
    rt = make_rt(script_static(cls=classification(in_scope=False, product="other")))
    r = run_static(rt, "My mortgage servicer lost my escrow payment.")
    assert r["outcome"] == "abstain" and r["path"] == ["classify", "abstain"]


def test_static_ambiguous_clarifies():
    cls = classification(
        needs_clarification=True, clarifying_question="Was this a credit card or a bank account?"
    )
    r = run_static(make_rt(script_static(cls=cls)), "The bank took my money.")
    assert r["outcome"] == "clarify"
    assert "credit card or a bank account" in r["response"]


def test_static_redrafts_then_passes():
    r = run_static(make_rt(script_static(drafts=[bad_draft(), good_draft()])), COMPLAINT)
    assert r["outcome"] == "answer"
    assert r["path"].count("draft") == 2 and r["attempts"] == 2


def test_static_escalates_after_max_redrafts():
    r = run_static(make_rt(script_static(drafts=[bad_draft()])), COMPLAINT)
    assert r["outcome"] == "escalate"
    assert r["path"].count("draft") == 3  # 1 draft + 2 redrafts
    assert "failed verification" in r["escalation_reason"]


def test_static_escalates_on_weak_retrieval():
    weak = dict(FakeStore().regs[0], score=0.05)
    rt = make_rt(script_static(), store=FakeStore(regs=[weak]))
    r = run_static(rt, COMPLAINT)
    assert r["outcome"] == "escalate" and "relevance threshold" in r["escalation_reason"]
    assert "draft" not in r["path"]


def test_static_escalates_on_tool_error():
    rt = make_rt(script_static(), store=FakeStore(fail_on={"regs"}))
    r = run_static(rt, COMPLAINT)
    assert r["outcome"] == "escalate" and r["errors"]
    assert "System error" in r["escalation_reason"]


def test_static_judge_catches_wrong_fact():
    judge = {
        "verdicts": [{"claim_index": 0, "supported": False, "reason": "says $500"}],
        "policy_issues": [],
    }
    r = run_static(make_rt(script_static(judge=judge)), COMPLAINT)
    assert r["outcome"] == "escalate"
    assert r["verification"]["unsupported"]


def test_static_human_approval_interrupt_and_resume():
    rt = make_rt(script_static(), require_approval=True)
    r = run_static(rt, COMPLAINT)
    assert r["outcome"] == "pending_review" and r["pending_review"]
    done = resume_static(rt, r["thread_id"], approved=True, edited_response="Edited reply.")
    assert done["outcome"] == "answer" and done["response"] == "Edited reply."
    rejected = resume_static(rt, run_static(rt, COMPLAINT)["thread_id"], approved=False)
    assert rejected["outcome"] == "rejected"


# ---------------------------------------------------------------- dynamic
def script_dynamic(decisions, drafts=None, judge=None):
    decisions = list(decisions)
    drafts = list(drafts or [good_draft()])

    def script(name, schema, system, user):
        if name == "supervisor":
            return decisions.pop(0) if len(decisions) > 1 else decisions[0]
        if name == "draft":
            return drafts.pop(0) if len(drafts) > 1 else drafts[0]
        if name == "verify":
            return judge or judge_all_supported()
        if name == "summarize_history":
            return {"summary": "Earlier they asked about credit card disputes."}
        raise AssertionError(name)

    return script


def dec(action, **kw):
    return {"action": action, "reason": f"test {action}", **kw}


def test_dynamic_routes_regs_then_stats_then_answers():
    decisions = [
        dec("search_regulations", query="unauthorized credit card use", regulation_parts=["1026"]),
        dec(
            "query_stats",
            stats={"metric": "count", "group_by": "month", "product_keyword": "credit card"},
        ),
        dec("synthesize"),
    ]
    r = run_dynamic(
        make_rt(script_dynamic(decisions)),
        "What limits cardholder liability, and are complaints rising?",
    )
    assert r["outcome"] == "answer"
    assert r["path"] == [
        "prepare",
        "supervisor",
        "regs_agent",
        "supervisor",
        "stats_agent",
        "supervisor",
        "synthesize",
        "verify",
        "respond",
    ]
    assert any(i.startswith("S-") for i in r["retrieved_ids"])


def test_dynamic_loop_detection_forces_synthesis():
    same = dec("search_regulations", query="billing error")
    r = run_dynamic(make_rt(script_dynamic([same])), "billing error rules?")
    assert any("repeated identical search" in o for o in r["overrides"])
    assert r["outcome"] == "answer" and r["path"].count("regs_agent") == 1


class FreshStore(FakeStore):
    """Every search returns a chunk not seen before, so only the step cap stops it."""

    def search_regulations(self, query, k, parts=None):
        self._maybe_fail("regs")
        n = self.calls.count("regs")
        return [{**REG_1026_12, "id": f"R-1026.12#{n}"}]


def test_dynamic_step_cap():
    counter = {"i": 0}

    def script(name, schema, system, user):
        if name == "supervisor":
            counter["i"] += 1
            return dec("search_regulations", query=f"query {counter['i']}")
        return judge_all_supported() if name == "verify" else good_draft()

    r = run_dynamic(make_rt(script, store=FreshStore()), "keep searching")
    assert r["path"].count("regs_agent") == 6
    assert any("step cap" in o for o in r["overrides"]) and r["outcome"] == "answer"


def test_dynamic_stops_reworded_searches_that_find_nothing_new():
    counter = {"i": 0}

    def script(name, schema, system, user):
        if name == "supervisor":
            counter["i"] += 1
            return dec("search_regulations", query=f"reworded query {counter['i']}")
        return judge_all_supported() if name == "verify" else good_draft()

    r = run_dynamic(make_rt(script), "keep searching")
    # 1st search adds 3 chunks; the next 2 return the same chunks -> synthesize.
    assert r["path"].count("regs_agent") == 3
    assert any("found nothing new" in o for o in r["overrides"]) and r["outcome"] == "answer"
    assert len(r["retrieved_ids"]) == len(set(r["retrieved_ids"])) == 3
    assert [c["id"] for c in r["citations"]] == ["R-1026.12#1"]


def test_dynamic_abstains_out_of_scope():
    r = run_dynamic(
        make_rt(script_dynamic([dec("abstain", reason="Reg DD is not ingested")])),
        "What does Reg DD require for savings account disclosures?",
    )
    assert r["outcome"] == "abstain" and r["path"] == ["prepare", "supervisor", "abstain"]
    assert "Reg DD is not ingested" in r["response"]


def test_dynamic_abstain_after_verify_reports_gaps_not_supervisor_reason():
    no_cover = {**good_draft(), "insufficient_evidence": True, "gaps": ["complaint volume by bank"]}
    decisions = [
        dec("search_regulations", query="collector validation notice"),
        dec("synthesize", reason="Enough evidence exists, so I'll synthesize"),
    ]
    r = run_dynamic(
        make_rt(script_dynamic(decisions, drafts=[no_cover])),
        "Which banks get the most validation-notice complaints?",
    )
    assert r["outcome"] == "abstain"
    assert "synthesize" not in r["response"]
    assert "complaint volume by bank" in r["response"]


def test_supervisor_is_told_todays_date_and_sample_range():
    from datetime import date

    import config

    seen = []
    base = script_dynamic([dec("abstain", reason="out of scope")])

    def script(name, schema, system, user):
        if name == "supervisor":
            seen.append(user)
        return base(name, schema, system, user)

    run_dynamic(make_rt(script), "How many complaints did we get last year?")
    assert date.today().isoformat() in seen[0]
    assert config.COMPLAINTS_SINCE in seen[0] and config.COMPLAINTS_UNTIL in seen[0]


def test_dynamic_tool_errors_escalate():
    decisions = [
        dec("search_regulations", query="a"),
        dec("search_regulations", query="b"),
        dec("search_regulations", query="c"),
    ]
    rt = make_rt(script_dynamic(decisions), store=FakeStore(fail_on={"regs"}))
    r = run_dynamic(rt, "anything")
    assert r["outcome"] == "escalate" and len(r["errors"]) == 2
    assert "Repeated tool errors" in r["response"]


def test_dynamic_replans_after_failed_verification():
    decisions = [
        dec("search_regulations", query="debt collector calls"),
        dec("synthesize"),
        dec("search_complaints", query="collector calling daily"),
        dec("synthesize"),
    ]
    r = run_dynamic(
        make_rt(script_dynamic(decisions, drafts=[bad_draft(), good_draft()])),
        "How often can a collector call?",
    )
    assert "replan" in r["path"] and r["outcome"] == "answer"


def test_dynamic_uses_history_summary():
    history = [{"role": "user", "content": f"q{i}"} for i in range(5)]
    rt = make_rt(script_dynamic([dec("search_regulations", query="x"), dec("synthesize")]))
    run_dynamic(rt, "follow-up question", history=history)
    assert "summarize_history" in rt.calls


def test_policy_synthesize_without_evidence_searches_first():
    d, why = apply_policy({"request": "q", "steps": 0}, dec("synthesize"))
    assert d["action"] == "search_regulations" and d["query"] == "q" and why
