"""Skill and runtime tests that don't need a graph."""

from context import pack_evidence
from runtime import Runtime
from skills import verify
from skills.schemas import Draft, HistorySummary
from tests.fakes import CASE_1, REG_1006_14, good_draft, judge_all_supported, make_rt


def test_judge_sees_whole_regulation_chunk():
    # Real chunks run to ~3,000 chars; the supporting text is often in the second half.
    long_reg = {**REG_1006_14, "text": "filler " * 400 + "PRIOR CONSENT RULE"}
    seen = {}

    def script(name, schema, system, user):
        seen["user"] = user
        return judge_all_supported()

    v = verify(make_rt(script), Draft(**good_draft(ids=("R-1006.14#1",))), [long_reg])
    assert v["passed"] and "PRIOR CONSENT RULE" in seen["user"]


def test_judge_flags_facts_left_out_of_claims():
    # A fact the drafter files as a "caveat" isn't in claims; the judge must still catch it.
    seen = {}

    def script(name, schema, system, user):
        seen["system"] = system
        return judge_all_supported()

    verify(make_rt(script), Draft(**good_draft(ids=("R-1006.14#1",))), [REG_1006_14])
    assert "not among the\nnumbered claims, report it as a blocking policy issue" in seen["system"]


def test_judge_sees_narrative_clipped_like_the_drafter():
    long_case = {**CASE_1, "text": "word " * 2000 + "TAIL"}
    seen = {}

    def script(name, schema, system, user):
        seen["user"] = user
        return judge_all_supported()

    verify(make_rt(script), Draft(**good_draft(ids=("C-111",))), [long_case])
    assert "TAIL" not in seen["user"]


def test_judge_sees_evidence_rendered_like_the_drafter():
    # The citation header carries a complaint's product, issue and company response;
    # claims drawn from it must not look unsupported to the judge.
    evidence = [REG_1006_14, CASE_1]
    rt = make_rt(lambda name, schema, system, user: seen.update(user=user) or judge_all_supported())
    seen = {}

    block, used, _ = pack_evidence(evidence, rt.ctx)
    verify(rt, Draft(**good_draft(ids=("R-1006.14#1", "C-111"))), used)
    for drafter_block in block.split("\n\n---\n\n"):
        assert drafter_block in seen["user"]
    assert "Closed with monetary relief" in seen["user"]


def test_structured_output_uses_json_schema():
    calls = {}

    class StubLLM:
        def with_structured_output(self, schema, **kw):
            calls.update(kw)
            return self

        def invoke(self, messages):
            return {"raw": None, "parsed": HistorySummary(summary="ok"), "parsing_error": None}

    rt = Runtime(store=None)
    rt._llms["fast"] = StubLLM()
    assert rt.structured("fast", HistorySummary, "s", "u", name="t").summary == "ok"
    assert calls["method"] == "json_schema"


def test_promise_check_ignores_negated_guarantees():
    from skills.verify import promises

    for ok in [
        "We do not guarantee a refund.",
        "We don't guarantee any outcome.",
        "We can’t guarantee the result.",
        "There is no guarantee of a credit.",
        "We're not able to guarantee a refund.",
    ]:
        assert promises(ok) == [], ok
    for bad in [
        "We guarantee a full refund.",
        "We can't say much. We guarantee a refund.",
        "No problem, we will refund you.",
        "We don't guarantee speed, but we will reimburse you.",
    ]:
        assert promises(bad), bad


def test_draft_partial_answers_are_not_insufficient():
    from skills import draft

    seen = {}

    def script(name, schema, system, user):
        seen["system"] = system
        return {**good_draft(), "gaps": ["exact refund timing"]}

    d, _ = draft(make_rt(script), "When will I get my money back?", [REG_1006_14])
    assert d.gaps == ["exact refund timing"] and not d.insufficient_evidence
    assert "only if the evidence does not address the main question" in seen["system"]
    assert "Do not list general caveats or disclaimers as claims" in seen["system"]
