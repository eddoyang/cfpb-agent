"""One entry point per workflow, returning a flat result dict that the CLI, the
Streamlit app and the evaluation harness all consume."""
from __future__ import annotations

import time
import uuid

from langgraph.types import Command

import config
from graphs.dynamic import build_dynamic_graph
from graphs.static import build_static_graph

_GRAPHS: dict[tuple[int, str], object] = {}


def _graph(rt, kind: str):
    key = (id(rt), kind)
    if key not in _GRAPHS:
        _GRAPHS[key] = build_static_graph(rt) if kind == "static" else build_dynamic_graph(rt)
    return _GRAPHS[key]


def _citations(state: dict) -> list[dict]:
    cited = set((state.get("verification") or {}).get("cited_ids", []))
    return [{"id": e["id"], "kind": e["kind"], "citation": e["citation"],
             "score": round(e["score"], 3), "url": e["source_url"]}
            for e in state.get("evidence", []) if e["id"] in cited]


def _package(state: dict, workflow: str, thread_id: str | None, rt, ledger_start: int,
             t0: float, interrupted: bool) -> dict:
    return {
        "workflow": workflow,
        "thread_id": thread_id,
        "outcome": "pending_review" if interrupted else state.get("outcome", "unknown"),
        "response": (state.get("draft") or {}).get("response", "") if interrupted
                    else state.get("final_response", ""),
        "pending_review": interrupted,
        "classification": state.get("classification"),
        "draft": state.get("draft"),
        "verification": state.get("verification"),
        "citations": _citations(state),
        "retrieved_ids": [e["id"] for e in state.get("evidence", [])],
        "retrieved_sections": sorted({e["section"] for e in state.get("evidence", [])
                                      if e.get("section")}),
        "retrieved_scores": [round(e["score"], 3) for e in state.get("evidence", [])
                             if e["kind"] == "regulation"],
        "context_ids": state.get("context_ids", []),
        "actions": state.get("actions", []),
        "overrides": state.get("overrides", []),
        "attempts": state.get("attempts"),
        "escalation_reason": state.get("escalation_reason"),
        "trace": state.get("trace", []),
        "path": [t["node"] for t in state.get("trace", [])],
        "errors": state.get("errors", []),
        "usage": rt.usage(since=ledger_start),
        "latency_s": round(time.perf_counter() - t0, 2),
        "context_config": rt.ctx.name,
    }


def run_static(rt, complaint: str, exclude_complaint_id: int | None = None,
               thread_id: str | None = None) -> dict:
    thread_id = thread_id or str(uuid.uuid4())
    cfg = {"configurable": {"thread_id": thread_id}, "recursion_limit": config.RECURSION_LIMIT}
    start, t0 = len(rt.ledger), time.perf_counter()
    out = _graph(rt, "static").invoke(
        {"request": complaint, "exclude_complaint_id": exclude_complaint_id}, cfg)
    interrupted = "__interrupt__" in out
    return _package(out, "static", thread_id, rt, start, t0, interrupted)


def resume_static(rt, thread_id: str, approved: bool, edited_response: str | None = None,
                  reviewer: str = "reviewer", note: str = "") -> dict:
    cfg = {"configurable": {"thread_id": thread_id}, "recursion_limit": config.RECURSION_LIMIT}
    start, t0 = len(rt.ledger), time.perf_counter()
    decision = {"approved": approved, "edited_response": edited_response,
                "reviewer": reviewer, "note": note}
    out = _graph(rt, "static").invoke(Command(resume=decision), cfg)
    return _package(out, "static", thread_id, rt, start, t0, "__interrupt__" in out)


def run_dynamic(rt, question: str, history: list[dict] | None = None) -> dict:
    start, t0 = len(rt.ledger), time.perf_counter()
    out = _graph(rt, "dynamic").invoke(
        {"request": question, "history": history or []},
        {"recursion_limit": config.RECURSION_LIMIT})
    return _package(out, "dynamic", None, rt, start, t0, False)
