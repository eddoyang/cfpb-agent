"""Headless smoke test of the Streamlit app with the fake runtime."""
from pathlib import Path

import pytest

import runtime
from tests.fakes import (
    FakeStore,
    classification,
    good_draft,
    judge_all_supported,
    make_rt,
)

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest


def script(name, schema, system, user):
    return {"classify": classification(), "draft": good_draft(), "verify": judge_all_supported(),
            "supervisor": ({"action": "search_regulations", "reason": "r", "query": "q"}
                           if "(none)" in user else {"action": "synthesize", "reason": "s"}),
            "summarize_history": {"summary": "s"}}[name]


class Store(FakeStore):
    def random_complaints(self, n=1):
        return [{"complaint_id": 1, "product": "Credit card", "issue": "x", "narrative": "text"}]


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(runtime, "build_runtime",
                        lambda context="lean", require_approval=False:
                        make_rt(script, store=Store(), context=context,
                                require_approval=require_approval))
    at = AppTest.from_file(str(Path(__file__).parent.parent / "app.py"), default_timeout=30)
    at.run()
    assert not at.exception
    return at


def test_static_tab_with_approval(app):
    app.text_area[0].input("Someone charged $500 to my credit card.").run()
    next(b for b in app.button if b.label == "Run triage").click().run()
    assert not app.exception
    assert any("Waiting for human approval" in m.value for m in app.markdown)
    next(b for b in app.button if b.label == "Approve and send").click().run()
    assert not app.exception
    assert any("Answered" in m.value for m in app.markdown)


def test_dynamic_tab_chat(app):
    app.chat_input[0].set_value("How often can a collector call?").run()
    assert not app.exception
    assert any("limited to $50" in m.value for m in app.markdown)
