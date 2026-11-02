"""Skill and runtime tests that don't need a graph."""

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


def test_judge_sees_narrative_clipped_like_the_drafter():
    long_case = {**CASE_1, "text": "word " * 2000 + "TAIL"}
    seen = {}

    def script(name, schema, system, user):
        seen["user"] = user
        return judge_all_supported()

    verify(make_rt(script), Draft(**good_draft(ids=("C-111",))), [long_case])
    assert "TAIL" not in seen["user"]


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
