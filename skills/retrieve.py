"""Retrieval skills. Return evidence plus a quality signal the graphs use to decide
whether to proceed, re-plan, or abstain."""
from __future__ import annotations

import config


def _result(hits: list[dict], floor: float) -> dict:
    kept = [h for h in hits if h["score"] >= floor]
    best = max((h["score"] for h in hits), default=0.0)
    return {"evidence": kept, "best_score": round(best, 3),
            "n_retrieved": len(hits), "n_kept": len(kept), "sufficient": bool(kept)}


def retrieve_regulations(rt, query: str, parts: list[str] | None = None,
                         k: int | None = None) -> dict:
    k = k or rt.ctx.reg_top_k
    hits = rt.store.search_regulations(query, k=k, parts=parts or None)
    if parts and not any(h["score"] >= config.REG_MIN_SCORE for h in hits):
        # The classifier's part filter may be wrong; fall back to all regulations.
        hits = rt.store.search_regulations(query, k=k, parts=None)
    return _result(hits, config.REG_MIN_SCORE)


def retrieve_cases(rt, query: str, product_keyword: str | None = None, k: int | None = None,
                   exclude_id: int | None = None) -> dict:
    k = k or rt.ctx.case_top_k
    hits = rt.store.search_complaints(query, k=k, product_keyword=product_keyword,
                                      exclude_id=exclude_id)
    return _result(hits, config.CASE_MIN_SCORE)
