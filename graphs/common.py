"""Helpers shared by both graphs: node wrapper with tracing + error capture."""

from __future__ import annotations

import functools
import time

from langgraph.errors import GraphInterrupt


def traced(name: str):
    """Wrap a node so every run leaves a trace entry and exceptions become state,
    not crashes. The graph's routers read `failed` and send the run to `escalate`.
    A node can return `_detail` to annotate its trace entry."""

    def deco(fn):
        @functools.wraps(fn)
        def wrapper(state):
            start = time.perf_counter()
            try:
                out = dict(fn(state) or {})
            except GraphInterrupt:
                raise  # human-in-the-loop pause, not an error
            except Exception as e:  # noqa: BLE001 - we want every failure in state
                ms = int((time.perf_counter() - start) * 1000)
                return {
                    "failed": True,
                    "errors": [f"{name}: {type(e).__name__}: {e}"],
                    "trace": [{"node": name, "detail": f"ERROR: {e}", "ms": ms}],
                }
            ms = int((time.perf_counter() - start) * 1000)
            out["trace"] = [{"node": name, "detail": out.pop("_detail", ""), "ms": ms}]
            return out

        return wrapper

    return deco
