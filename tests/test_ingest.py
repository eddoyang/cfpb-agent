"""Offline tests for parsing, chunking and cleaning (no network, no DB, no API keys)."""
import pandas as pd

from ingest.complaints import (
    _find_buckets,
    clean_complaints,
    clean_narrative,
    reg_hint_for,
)
from ingest.regulations import chunk_section, parse_sections

SAMPLE_XML = b"""<DIV5 N="1026" TYPE="PART"><HEAD>PART 1026-TRUTH IN LENDING</HEAD>
<DIV6 N="B" TYPE="SUBPART">
<DIV8 N="1026.12" TYPE="SECTION"><HEAD>\xc2\xa7 1026.12 Special credit card provisions.</HEAD>
<P>(a) <I>Issuance of credit card.</I> No credit card shall be issued except in response to a request.</P>
<P>(b) <I>Liability of cardholder for unauthorized use</I>-(1) <I>Limitation on amount.</I> The liability shall not exceed the lesser of $50 or the amount obtained.</P>
<P>(c) <I>Right of cardholder to assert claims or defenses.</I> A card issuer is subject to claims.</P>
</DIV8>
<DIV8 N="1026.13" TYPE="SECTION"><HEAD>\xc2\xa7 1026.13 Billing error resolution.</HEAD>
<P>(a) <I>Definition of billing error.</I> A billing error means a reflection on a statement of an extension of credit that was not made to the consumer.</P>
<P>(1) A reflection on a periodic statement of an extension of credit not made to the consumer.</P>
<P>(b) <I>Billing error notice.</I> A billing error notice is a written notice received within 60 days.</P>
</DIV8>
<DIV8 N="1026.15" TYPE="SECTION"><HEAD>\xc2\xa7 1026.15 [Reserved]</HEAD></DIV8>
</DIV6></DIV5>"""


def test_parse_sections_skips_reserved():
    secs = parse_sections(SAMPLE_XML)
    assert [s["section"] for s in secs] == ["1026.12", "1026.13"]
    assert secs[1]["title"] == "Billing error resolution."
    assert secs[0]["paragraphs"][1].startswith("(b) Liability of cardholder")


def test_chunks_have_header_and_citation():
    sec = parse_sections(SAMPLE_XML)[1]
    chunks = chunk_section(sec, "1026", "2026-10-01")
    assert len(chunks) == 1
    c = chunks[0]
    assert c.text.startswith("12 CFR 1026.13 Billing error resolution. (Regulation Z")
    assert c.citation == "12 CFR 1026.13(a)-(b)"  # nested (1) does not count as top-level
    assert c.source_url.endswith("section-1026.13")


def test_small_budget_splits_without_crossing_sections():
    sec = parse_sections(SAMPLE_XML)[0]
    chunks = chunk_section(sec, "1026", "2026-10-01", max_tokens=60)
    assert len(chunks) > 1
    assert all(c.section == "1026.12" for c in chunks)
    assert chunks[0].chunk_id == "1026.12#1"
    assert all(c.citation.startswith("12 CFR 1026.12") for c in chunks)


def test_clean_narrative_normalises_redactions_and_amounts():
    raw = "On XX/XX/2024 XXXX XXXX charged {$500.00} to my card ending XXXX."
    out = clean_narrative(raw)
    assert "[DATE]" in out and "$500.00" in out
    assert "XXXX" not in out and "{" not in out


def test_reg_hint_mapping():
    assert reg_hint_for("Credit card") == "1026"
    assert reg_hint_for("Checking or savings account") == "1005"
    assert reg_hint_for("Debt collection") == "1006"
    assert reg_hint_for("Mortgage") is None


def test_clean_complaints_drops_short_and_duplicates():
    long_text = "I disputed an unauthorized charge on my credit card " * 5
    df = pd.DataFrame([
        {"complaint_id": "1", "date_received": "2024-03-01", "product": "Credit card",
         "sub_product": None, "issue": "Problem with a purchase", "sub_issue": None,
         "company": "Bank A", "state": "WA", "submitted_via": "Web",
         "company_response": "Closed with explanation", "timely": "Yes", "narrative": long_text},
        {"complaint_id": "2", "date_received": "2024-03-02", "product": "Credit card",
         "sub_product": None, "issue": "Fees", "sub_issue": None, "company": "Bank B",
         "state": "CA", "submitted_via": "Web", "company_response": "Closed",
         "timely": "No", "narrative": long_text},                     # duplicate text
        {"complaint_id": "3", "date_received": "2024-03-03", "product": "Debt collection",
         "sub_product": None, "issue": "Attempts to collect", "sub_issue": None,
         "company": "Agency C", "state": "NY", "submitted_via": "Web",
         "company_response": "Closed", "timely": "Yes", "narrative": "Too short."},
    ])
    out = clean_complaints(df)
    assert list(out["complaint_id"]) == [1]
    assert out.loc[0, "reg_hint"] == "1026"
    assert bool(out.loc[0, "timely"]) is True


def test_find_buckets_handles_nesting():
    aggs = {"product": {"doc_count": 10, "product": {"buckets": [{"key": "Credit card"}]}}}
    assert _find_buckets(aggs, "product") == [{"key": "Credit card"}]
