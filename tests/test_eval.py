"""The harness itself is tested with fakes so its scoring logic is trustworthy."""

import eval.harness as h
from tests.fakes import classification, good_draft, judge_all_supported, make_rt


def script(name, schema, system, user):
    if name == "classify":
        if "mortgage" in user:
            return classification(in_scope=False, product="other")
        return classification()
    if name == "draft":
        return good_draft()
    if name == "verify":
        return judge_all_supported()
    if name == "supervisor":
        return (
            {"action": "abstain", "reason": "Reg DD not ingested"}
            if "Regulation DD" in user
            else {"action": "search_regulations", "reason": "x", "query": "q"}
            if "Actions so far:\n(none)" in user
            else {"action": "synthesize", "reason": "y"}
        )
    raise AssertionError(name)


def test_cases_file_is_valid():
    cases = h.load_cases()
    assert len(cases) >= 25
    assert len({c["id"] for c in cases}) == len(cases)
    cats = {c["category"] for c in cases}
    assert {
        "success",
        "ambiguous",
        "out_of_scope",
        "missing_info",
        "adversarial",
        "known_failure",
    } <= cats
    for c in cases:
        assert c["workflow"] in {"static", "dynamic"} and c["expect"]["outcome"]


def test_harness_scores_and_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(h, "RESULTS_DIR", tmp_path)
    cases = h.load_cases(
        ids={
            "st-unauth-credit",
            "st-oos-mortgage",
            "dy-oos-reg-dd",
            "dy-billing-deadlines",
            "st-debit-atm-fraud",
        }
    )
    rows = h.run_cases(make_rt(script), cases, repeats=2, progress=lambda *_: None)
    by_id = {r["id"]: r for r in rows}
    assert by_id["st-unauth-credit"]["passed"]
    assert by_id["st-oos-mortgage"]["passed"] and by_id["dy-oos-reg-dd"]["passed"]
    # The fake always classifies as credit_card and cites 1026.12, so these must FAIL:
    assert not by_id["st-debit-atm-fraud"]["passed"]
    assert any("product" in x for x in by_id["st-debit-atm-fraud"]["reasons"])
    assert not by_id["dy-billing-deadlines"]["checks"]["citation_hit"]

    summary = h.summarize(rows)
    assert summary["runs"] == 10 and summary["consistency"] == 1.0
    out = h.write_results(rows, summary, {"timestamp": "t", "context": "lean", "repeats": 2})
    report = (out / "report.md").read_text()
    assert "## Failures" in report and "st-debit-atm-fraud" in report
    assert (tmp_path / "latest.md").exists()


def test_forbidden_phrase_check():
    case = {
        "id": "x",
        "workflow": "static",
        "category": "adversarial",
        "expect": {"outcome": ["answer"], "must_not_contain": ["guarantee"]},
    }
    r = {
        "outcome": "answer",
        "response": "We GUARANTEE a refund.",
        "latency_s": 1,
        "usage": {"cost_usd": 0, "input_tokens": 0, "output_tokens": 0, "llm_calls": 0},
    }
    s = h.score(case, r)
    assert not s["passed"] and not s["checks"]["forbidden"]
