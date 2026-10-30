"""Runtime: the one object every skill and graph node receives.

It owns the LLM clients (two Claude tiers), the vector store, the active context
configuration, and a ledger of every model call (tokens, latency, cost). Tests
swap in a FakeRuntime that overrides `structured()`; nothing else changes.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, TypeVar

from pydantic import BaseModel

import config
from context import ContextConfig, get_context_config

T = TypeVar("T", bound=BaseModel)


def make_chat_model(model: str, max_tokens: int):
    """Build a ChatAnthropic client. Some newer Claude models (e.g. Sonnet 5.5) reject a
    non-default temperature, so we only send it when the model accepts it. Where it is
    not accepted, run-to-run variation is measured instead (eval --repeats)."""
    from langchain_anthropic import ChatAnthropic
    kwargs = {"model": model, "max_tokens": max_tokens, "timeout": config.LLM_TIMEOUT_S,
                  "max_retries": config.LLM_MAX_RETRIES}
    fixed_sampling = model.startswith(config.MODELS_WITHOUT_TEMPERATURE)
    if config.LLM_TEMPERATURE is not None and not fixed_sampling:
        kwargs["temperature"] = config.LLM_TEMPERATURE
    return ChatAnthropic(**kwargs)


class SkillError(RuntimeError):
    """Raised when a skill cannot produce a valid result (caught by graph nodes)."""


@dataclass
class LLMCall:
    name: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_s: float

    @property
    def cost(self) -> float:
        p_in, p_out = config.MODEL_PRICES.get(self.model, (0.0, 0.0))
        return (self.input_tokens * p_in + self.output_tokens * p_out) / 1e6


@dataclass
class Runtime:
    store: Any
    ctx: ContextConfig = field(default_factory=lambda: get_context_config("lean"))
    require_approval: bool = False
    ledger: list[LLMCall] = field(default_factory=list)
    _llms: dict = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------ models
    def llm(self, tier: str):
        if tier not in self._llms:
            model = config.FAST_MODEL if tier == "fast" else config.STRONG_MODEL
            self._llms[tier] = make_chat_model(model, config.MAX_OUTPUT_TOKENS[tier])
        return self._llms[tier]

    def structured(self, tier: str, schema: type[T], system: str, user: str, name: str) -> T:
        """Call Claude with a Pydantic output schema; log usage; retry once on bad output."""
        model = config.FAST_MODEL if tier == "fast" else config.STRONG_MODEL
        runnable = self.llm(tier).with_structured_output(schema, include_raw=True)
        messages = [("system", system), ("human", user)]
        last_error = None
        for _ in range(2):
            start = time.perf_counter()
            out = runnable.invoke(messages)
            usage = getattr(out["raw"], "usage_metadata", None) or {}
            self.ledger.append(LLMCall(name, model, usage.get("input_tokens", 0),
                                       usage.get("output_tokens", 0),
                                       time.perf_counter() - start))
            if out.get("parsed") is not None:
                return out["parsed"]
            last_error = out.get("parsing_error")
        raise SkillError(f"{name}: model did not return valid {schema.__name__}: {last_error}")

    # ------------------------------------------------------------ usage
    def usage(self, since: int = 0) -> dict:
        calls = self.ledger[since:]
        return {
            "llm_calls": len(calls),
            "input_tokens": sum(c.input_tokens for c in calls),
            "output_tokens": sum(c.output_tokens for c in calls),
            "llm_latency_s": round(sum(c.latency_s for c in calls), 2),
            "cost_usd": round(sum(c.cost for c in calls), 5),
            "by_call": [
                {"name": c.name, "model": c.model, "in": c.input_tokens,
                 "out": c.output_tokens, "s": round(c.latency_s, 2)} for c in calls
            ],
        }


def build_runtime(context: str = "lean", require_approval: bool = False) -> Runtime:
    from retrieval.store import PgStore
    return Runtime(store=PgStore(), ctx=get_context_config(context),
                   require_approval=require_approval)
