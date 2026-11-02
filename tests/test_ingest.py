"""Offline tests for parsing, chunking and cleaning (no network, no DB, no API keys)."""

import pandas as pd

from ingest.complaints import _find_buckets, clean_complaints, clean_narrative, reg_hint_for
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
    df = pd.DataFrame(
        [
            {
                "complaint_id": "1",
                "date_received": "2024-03-01",
                "product": "Credit card",
                "sub_product": None,
                "issue": "Problem with a purchase",
                "sub_issue": None,
                "company": "Bank A",
                "state": "WA",
                "submitted_via": "Web",
                "company_response": "Closed with explanation",
                "timely": "Yes",
                "narrative": long_text,
            },
            {
                "complaint_id": "2",
                "date_received": "2024-03-02",
                "product": "Credit card",
                "sub_product": None,
                "issue": "Fees",
                "sub_issue": None,
                "company": "Bank B",
                "state": "CA",
                "submitted_via": "Web",
                "company_response": "Closed",
                "timely": "No",
                "narrative": long_text,
            },  # duplicate text
            {
                "complaint_id": "3",
                "date_received": "2024-03-03",
                "product": "Debt collection",
                "sub_product": None,
                "issue": "Attempts to collect",
                "sub_issue": None,
                "company": "Agency C",
                "state": "NY",
                "submitted_via": "Web",
                "company_response": "Closed",
                "timely": "Yes",
                "narrative": "Too short.",
            },
        ]
    )
    out = clean_complaints(df)
    assert list(out["complaint_id"]) == [1]
    assert out.loc[0, "reg_hint"] == "1026"
    assert bool(out.loc[0, "timely"]) is True


def test_find_buckets_handles_nesting():
    aggs = {"product": {"doc_count": 10, "product": {"buckets": [{"key": "Credit card"}]}}}
    assert _find_buckets(aggs, "product") == [{"key": "Credit card"}]


# ---------------------------------------------------------------- CSV loading
import pytest  # noqa: E402

from ingest.complaints import load_from_csv, resolve_columns  # noqa: E402

BULK_HEADER = [
    "Date received",
    "Product",
    "Sub-product",
    "Issue",
    "Sub-issue",
    "Consumer complaint narrative",
    "Company public response",
    "Company",
    "State",
    "ZIP code",
    "Tags",
    "Consumer consent provided?",
    "Submitted via",
    "Date sent to company",
    "Company response to consumer",
    "Timely response?",
    "Consumer disputed?",
    "Complaint ID",
]
API_HEADER = [
    "date_received",
    "product",
    "sub_product",
    "issue",
    "sub_issue",
    "complaint_what_happened",
    "company",
    "state",
    "submitted_via",
    "company_response",
    "timely",
    "complaint_id",
]


def _write(path, header, rows):
    pd.DataFrame(rows, columns=header).to_csv(path, index=False)


def _row(header, cid, date, product, narrative):
    values = {h: "x" for h in header}
    for h in header:
        n = h.lower()
        if "complaint id" in n or n == "complaint_id":
            values[h] = cid
        elif n.startswith("date received") or n == "date_received":
            values[h] = date
        elif n == "product":
            values[h] = product
        elif "narrative" in n or "what_happened" in n:
            values[h] = narrative
    return [values[h] for h in header]


@pytest.mark.parametrize("header", [BULK_HEADER, API_HEADER])
def test_load_from_csv_handles_header_styles(tmp_path, header):
    story = "I disputed a charge " * 10
    f = tmp_path / "c.csv"
    _write(
        f,
        header,
        [
            _row(header, "1", "2024-03-01", "Credit card", story),
            _row(header, "2", "03/05/24", "Debt collection", story),
            _row(header, "3", "2022-01-01", "Credit card", story),  # too old
            _row(header, "4", "2024-06-01", "Mortgage", story),  # out of scope
            _row(header, "5", "2024-06-01", "Credit card", ""),
        ],
    )  # no narrative
    df = load_from_csv(f, per_product=10)
    assert sorted(df["complaint_id"]) == ["1", "2"]
    assert list(df.columns)[-1] == "narrative"


def test_missing_narrative_column_explains(tmp_path):
    header = [h for h in BULK_HEADER if h != "Consumer complaint narrative"]
    with pytest.raises(ValueError, match="no complaint narrative"):
        resolve_columns(header)


def test_load_from_folder_and_per_product_cap(tmp_path):
    story = "I disputed a charge " * 10
    for i in range(3):
        _write(
            tmp_path / f"e{i}.csv",
            BULK_HEADER,
            [_row(BULK_HEADER, str(i), "2024-03-01", "Credit card", story)],
        )
    assert len(load_from_csv(tmp_path, per_product=2)) == 2


def test_load_from_archive_zips_in_folder(tmp_path):
    """Narratives-archive style: a folder of ZIPs, each holding CSVs; overlaps deduped."""
    import zipfile

    story = "I disputed a charge " * 10
    csv1, csv2 = tmp_path / "a.csv", tmp_path / "b.csv"
    _write(
        csv1,
        BULK_HEADER,
        [
            _row(BULK_HEADER, "1", "2026-03-01", "Credit card", story),
            _row(BULK_HEADER, "2", "2026-03-02", "Debt collection", story),
        ],
    )
    _write(
        csv2,
        BULK_HEADER,
        [
            _row(BULK_HEADER, "2", "2026-03-02", "Debt collection", story),
            _row(BULK_HEADER, "3", "2026-04-01", "Prepaid card", story),
        ],
    )
    archive = tmp_path / "archive"
    archive.mkdir()
    with zipfile.ZipFile(archive / "CCDB_Export_16.zip", "w") as zf:
        zf.write(csv1, "export/part1.csv")
    with zipfile.ZipFile(archive / "CCDB_Export_17.zip", "w") as zf:
        zf.write(csv2, "part2.csv")
        zf.writestr("README.txt", "notes")
    df = load_from_csv(archive, per_product=10)
    assert sorted(df["complaint_id"]) == ["1", "2", "3"]


def test_zip_without_csv_explains(tmp_path):
    import zipfile

    z = tmp_path / "x.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("data.json", "{}")
    with pytest.raises(ValueError, match="contains no CSV"):
        load_from_csv(z, per_product=10)