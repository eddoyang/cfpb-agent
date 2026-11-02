"""Context management: what evidence and history each LLM call sees, and how much.

Two named configurations are compared in experiments/context_compare.py:
  lean : few chunks, tight evidence budget, older history summarised
  rich : many chunks, large budget, full history verbatim
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ingest.tokens import count_tokens, truncate_tokens


@dataclass(frozen=True)
class ContextConfig:
    name: str
    reg_top_k: int
    case_top_k: int
    max_evidence_tokens: int  # budget for the packed evidence block
    max_case_tokens: int  # each complaint narrative is clipped to this
    history_mode: str  # "summary" | "full"
    history_keep_turns: int  # turns kept verbatim in summary mode
    max_history_tokens: int


CONTEXT_CONFIGS = {
    "lean": ContextConfig(
        "lean",
        reg_top_k=3,
        case_top_k=2,
        max_evidence_tokens=2500,
        max_case_tokens=250,
        history_mode="summary",
        history_keep_turns=2,
        max_history_tokens=500,
    ),
    "rich": ContextConfig(
        "rich",
        reg_top_k=10,
        case_top_k=5,
        max_evidence_tokens=9000,
        max_case_tokens=800,
        history_mode="full",
        history_keep_turns=99,
        max_history_tokens=6000,
    ),
}


def get_context_config(name: str, **overrides) -> ContextConfig:
    return replace(CONTEXT_CONFIGS[name], **overrides)


# ---------------------------------------------------------------- evidence
def _render(ev: dict, cfg: ContextConfig) -> str:
    text = ev["text"]
    if ev["kind"] == "complaint":
        text = truncate_tokens(text, cfg.max_case_tokens)
    return f"[{ev['id']}] {ev['citation']}\n{text}"


def pack_evidence(evidence: list[dict], cfg: ContextConfig) -> tuple[str, list[dict], int]:
    """Order, dedupe and pack evidence into a token budget.

    Order: regulations first (they carry the legal answer), then stats, then
    complaints, each by score. Items that don't fit are dropped, not truncated
    mid-sentence, except complaint narratives which are clipped by design.
    Returns (block_text, items_used, tokens_used).
    """
    rank = {"regulation": 0, "stats": 1, "complaint": 2}
    seen, ordered = set(), []
    for ev in sorted(evidence, key=lambda e: (rank.get(e["kind"], 9), -e.get("score", 0))):
        if ev["id"] in seen:
            continue
        seen.add(ev["id"])
        ordered.append(ev)

    parts, used, tokens = [], [], 0
    for ev in ordered:
        block = _render(ev, cfg)
        t = count_tokens(block)
        if tokens + t > cfg.max_evidence_tokens:
            continue
        parts.append(block)
        used.append(ev)
        tokens += t
    return "\n\n---\n\n".join(parts), used, tokens


# ---------------------------------------------------------------- history
def render_history(history: list[dict] | None, cfg: ContextConfig, summarize=None) -> str:
    """history: [{"role": "user"|"assistant", "content": str}, ...]

    summary mode keeps the last N turns verbatim and compresses older turns with
    `summarize(text) -> str` (a fast-model call). Either way the result is
    capped at max_history_tokens, trimming the oldest material first.
    """
    if not history:
        return ""
    lines = [f"{h['role']}: {h['content']}" for h in history]
    if cfg.history_mode == "summary" and len(lines) > cfg.history_keep_turns:
        older = "\n".join(lines[: -cfg.history_keep_turns])
        recent = lines[-cfg.history_keep_turns :]
        summary = summarize(older) if summarize else truncate_tokens(older, 200)
        lines = [f"(summary of earlier conversation) {summary}"] + recent
    text = "\n".join(lines)
    while count_tokens(text) > cfg.max_history_tokens and len(lines) > 1:
        lines = lines[1:]
        text = "\n".join(lines)
    return truncate_tokens(text, cfg.max_history_tokens)
