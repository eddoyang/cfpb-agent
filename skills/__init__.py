"""Reusable agent skills. Both workflows call these same functions.

    classify             fast model   complaint -> product, issue, regulations, priority
    retrieve_regulations vector DB    query -> cited regulation chunks
    retrieve_cases       vector DB    query -> similar past complaints
    run_stats            SQL          structured request -> aggregate table (no free-form SQL)
    draft                strong model evidence -> response with per-claim citations
    verify               rules + strong model  draft -> supported / unsupported claims
"""
from skills.classify import classify
from skills.draft import draft
from skills.retrieve import retrieve_cases, retrieve_regulations
from skills.stats import run_stats
from skills.verify import verify

__all__ = ["classify", "draft", "retrieve_cases", "retrieve_regulations", "run_stats", "verify"]
