"""Fetch Reg E / F / Z from the eCFR API and split them into section-aligned chunks.

Chunking strategy (the interview talking point):
  * Never cross a section boundary, so every chunk maps to one citable section.
  * Within a section, pack whole paragraphs up to REG_CHUNK_MAX_TOKENS.
  * Prefix each chunk with a contextual header ("12 CFR 1026.13 Billing error
    resolution, Regulation Z") so the embedding knows what the paragraph is about
    even when the paragraph itself only says "(b) Billing error notice...".
  * Track top-level paragraph labels so citations are precise: 12 CFR 1026.13(a)-(c).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

import requests
from lxml import etree

import config
from ingest.tokens import count_tokens

HEADERS = {"User-Agent": "cfpb-agent-demo/0.1 (educational project)"}
SECTION_RE = re.compile(r"§\s*(\d+\.\d+[a-z]?)")
LABEL_RE = re.compile(r"^\(([a-z])\)")


@dataclass
class RegChunk:
    chunk_id: str
    part: str
    regulation: str
    section: str
    section_title: str
    citation: str
    text: str
    token_count: int
    source_url: str
    as_of_date: str


# ---------------------------------------------------------------- fetching
def resolve_issue_date(title: int = 12) -> str:
    """eCFR 404s on dates that aren't valid issue dates, so ask titles.json."""
    resp = requests.get(f"{config.ECFR_BASE}/titles.json", headers=HEADERS, timeout=60)
    resp.raise_for_status()
    for t in resp.json()["titles"]:
        if t["number"] == title:
            return t.get("up_to_date_as_of") or t["latest_issue_date"]
    raise ValueError(f"Title {title} not found in eCFR titles.json")


def fetch_part_xml(part: str, date: str, title: int = 12) -> bytes:
    cache = config.RAW_DIR / f"ecfr_title{title}_part{part}_{date}.xml"
    if cache.exists():
        return cache.read_bytes()
    url = f"{config.ECFR_BASE}/full/{date}/title-{title}.xml"
    resp = requests.get(url, params={"part": part}, headers=HEADERS, timeout=180)
    resp.raise_for_status()
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(resp.content)
    return resp.content


# ---------------------------------------------------------------- parsing
def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_sections(xml_bytes: bytes) -> list[dict]:
    """Return [{section, title, paragraphs:[str]}] for every regulatory section."""
    root = etree.fromstring(xml_bytes)
    sections = []
    for div in root.iter():
        if not isinstance(div.tag, str) or div.get("TYPE") != "SECTION":
            continue
        head_el = div.find("HEAD")
        head = _clean("".join(head_el.itertext())) if head_el is not None else ""
        m = SECTION_RE.search(head) or SECTION_RE.search("§ " + (div.get("N") or ""))
        if not m:
            continue
        number = m.group(1)
        title = _clean(SECTION_RE.sub("", head, count=1))
        paragraphs = [_clean("".join(p.itertext())) for p in div.iter("P", "FP")]
        paragraphs = [p for p in paragraphs if p]
        # Skip [Reserved] / removed sections
        if not paragraphs or "[Reserved]" in title:
            continue
        sections.append({"section": number, "title": title, "paragraphs": paragraphs})
    return sections


# ---------------------------------------------------------------- chunking
def _split_long_paragraph(para: str, max_tokens: int) -> list[str]:
    if count_tokens(para) <= max_tokens:
        return [para]
    pieces, current = [], ""
    for sentence in re.split(r"(?<=[.;])\s+", para):
        candidate = f"{current} {sentence}".strip()
        if current and count_tokens(candidate) > max_tokens:
            pieces.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def _citation(section: str, labels: list[str]) -> str:
    if not labels:
        return f"12 CFR {section}"
    if labels[0] == labels[-1]:
        return f"12 CFR {section}({labels[0]})"
    return f"12 CFR {section}({labels[0]})-({labels[-1]})"


def chunk_section(
    sec: dict, part: str, as_of: str, max_tokens: int = config.REG_CHUNK_MAX_TOKENS
) -> list[RegChunk]:
    regulation = config.REGULATIONS[part]
    header = f"12 CFR {sec['section']} {sec['title']} ({regulation})"
    budget = max_tokens - count_tokens(header) - 4

    # Expand any oversized paragraph first, remembering its top-level label.
    units: list[tuple[str, str | None]] = []
    current_label = None
    for para in sec["paragraphs"]:
        m = LABEL_RE.match(para)
        if m and (
            current_label is None or ord(m.group(1)) == ord(current_label) + 1 or m.group(1) == "a"
        ):
            current_label = m.group(1)
        for piece in _split_long_paragraph(para, budget):
            units.append((piece, current_label))

    chunks: list[RegChunk] = []
    buf: list[str] = []
    labels: list[str] = []
    buf_tokens = 0

    def flush():
        nonlocal buf, labels, buf_tokens
        if not buf:
            return
        idx = len(chunks) + 1
        text = header + "\n\n" + "\n".join(buf)
        chunks.append(
            RegChunk(
                chunk_id=f"{sec['section']}#{idx}",
                part=part,
                regulation=regulation,
                section=sec["section"],
                section_title=sec["title"],
                citation=_citation(sec["section"], labels),
                text=text,
                token_count=count_tokens(text),
                source_url=f"https://www.ecfr.gov/current/title-12/section-{sec['section']}",
                as_of_date=as_of,
            )
        )
        buf, labels, buf_tokens = [], [], 0

    for piece, label in units:
        t = count_tokens(piece)
        if buf and buf_tokens + t > budget:
            flush()
        buf.append(piece)
        buf_tokens += t
        if label and (not labels or labels[-1] != label):
            labels.append(label)
    flush()
    return chunks


# ---------------------------------------------------------------- entrypoint
def build_regulation_chunks() -> list[RegChunk]:
    as_of = resolve_issue_date(12)
    print(f"eCFR Title 12 as of {as_of}")
    all_chunks: list[RegChunk] = []
    for part in config.REGULATIONS:
        xml = fetch_part_xml(part, as_of)
        sections = parse_sections(xml)
        part_chunks = [c for s in sections for c in chunk_section(s, part, as_of)]
        print(f"  Part {part}: {len(sections)} sections -> {len(part_chunks)} chunks")
        all_chunks.extend(part_chunks)

    out = config.PROCESSED_DIR / "reg_chunks.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for c in all_chunks:
            f.write(json.dumps(asdict(c)) + "\n")
    print(f"Wrote {len(all_chunks)} regulation chunks to {out}")
    return all_chunks
