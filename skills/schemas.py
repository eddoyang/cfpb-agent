"""Structured outputs for every LLM-backed skill. Claude fills these via tool calling,
so downstream code never parses free text."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Product = Literal["credit_card", "checking_savings", "money_transfer", "prepaid_card",
                  "debt_collection", "other"]
RegPart = Literal["1005", "1006", "1026"]


class Classification(BaseModel):
    in_scope: bool = Field(description="True if this is a US consumer complaint about a credit "
                           "card, bank account, money transfer, prepaid card, or debt collection.")
    product: Product
    issue: str = Field(description="Short issue label, e.g. 'unauthorized charge', 'billing dispute'.")
    regulation_parts: list[RegPart] = Field(
        description="12 CFR parts likely to apply: 1005=Reg E (electronic transfers, debit, "
                    "prepaid, remittances), 1006=Reg F (debt collection), 1026=Reg Z (credit cards).")
    priority: Literal["high", "medium", "low"] = Field(
        description="high = money lost, fraud, or legal deadline at risk.")
    needs_clarification: bool = Field(
        description="True only if the product or core problem cannot be determined.")
    clarifying_question: str | None = None
    search_query: str = Field(description="A concise query to search regulations for this issue.")
    rationale: str


class Claim(BaseModel):
    text: str = Field(description="One factual statement made in the response.")
    citations: list[str] = Field(description="Evidence IDs supporting it, e.g. ['R-1026.13#1'].")


class Draft(BaseModel):
    response: str = Field(description="The full text shown to the reader, with [evidence-id] "
                          "markers after supported statements.")
    claims: list[Claim] = Field(description="Every factual or legal statement in the response.")
    insufficient_evidence: bool = Field(
        description="True if the evidence does not cover the question.")
    internal_notes: str = Field(description="Notes for the human reviewer.")


class ClaimVerdict(BaseModel):
    claim_index: int
    supported: bool
    reason: str


class JudgeOutput(BaseModel):
    verdicts: list[ClaimVerdict]
    policy_issues: list[str] = Field(
        default_factory=list,
        description="Promises of outcomes/refunds, legal conclusions stated as certain, tone problems.")


class StatsRequest(BaseModel):
    metric: Literal["count", "timely_rate", "relief_rate"] = "count"
    group_by: Literal["none", "product", "issue", "company", "month", "state",
                      "company_response"] = "none"
    product_keyword: str | None = Field(None, description="e.g. 'credit card', 'debt collection'")
    issue_keyword: str | None = Field(None, description="Substring of the CFPB issue label.")
    company_keyword: str | None = None
    state: str | None = Field(None, description="Two-letter state code.")
    date_from: str | None = Field(None, description="YYYY-MM-DD")
    date_to: str | None = Field(None, description="YYYY-MM-DD")
    limit: int = Field(10, ge=1, le=50)


SupervisorAction = Literal["search_regulations", "search_complaints", "query_stats",
                           "synthesize", "clarify", "abstain"]


class SupervisorDecision(BaseModel):
    action: SupervisorAction
    reason: str = Field(description="One sentence: why this is the best next step.")
    query: str | None = Field(None, description="Search query for search_* actions.")
    regulation_parts: list[RegPart] = Field(default_factory=list)
    product_keyword: str | None = None
    stats: StatsRequest | None = None
    clarifying_question: str | None = None


class HistorySummary(BaseModel):
    summary: str
