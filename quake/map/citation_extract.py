"""Deterministic scanner over the Principia _djvu.txt.

Extracts verbatim cross-reference citation phrases using pinned regex
patterns. Pure function, deterministic, no IO/network. Produces
CitationsRaw with source="text".
"""

from __future__ import annotations

import re
from typing import Optional

from map.raw_models import (
    CitationsRaw,
    RawCitation,
    RawCiteItem,
    PageMap,
    PageEntry,
    PageLabel,
    LevelId,
    SCHEMA_VERSION,
)


CITE_PATTERNS = [
    re.compile(r"by\s+(the\s+)?(first|second|third|fourth|fifth|[IVXLC]+)\s+Law(\s+of\s+Motion)?", re.IGNORECASE),
    re.compile(r"by\s+(Lem\.|Lemma)\s+[IVXLC]+", re.IGNORECASE),
    re.compile(r"by\s+(Prop\.|Proposition)\s+[IVXLC]+", re.IGNORECASE),
    re.compile(r"by\s+(Cor\.|Corollary)\s+\d+\.?\s*(Prop\.|Proposition)?\s*[IVXLC]*", re.IGNORECASE),
    re.compile(r"by\s+(Def\.|Definition)\s+[IVXLC]+", re.IGNORECASE),
    re.compile(r"(per|by)\s+Cor\.\s*\d+\.?\s*of\s+the\s+Laws", re.IGNORECASE),
]

VAGUE_PATTERNS = [
    re.compile(r"as\s+(was\s+)?(shown|demonstrated)\s+above", re.IGNORECASE),
    re.compile(r"by\s+what\s+was\s+demonstrated", re.IGNORECASE),
    re.compile(r"\babove\b", re.IGNORECASE),  # standalone "above"
]


def _build_heading_regex(label: str) -> re.Pattern:
    """Build a regex that finds the label appearing as a likely heading.

    A heading appears at/near the start of a line in all-caps or title-case
    form. We require the label to be at the start of a line (allowing leading
    whitespace) and NOT immediately preceded by a citation cue like "by".
    """
    # Escape the literal label text, but allow flexible separators between
    # tokens so "PROP. I. THEOREM I." and "LEMMA II." both match.
    tokens = [re.escape(tok.rstrip(". ,;:")) for tok in label.split()]
    # Allow any non-alphanumeric chars between tokens (periods, spaces, etc.)
    body = r"[\W_]*".join(tokens)
    # Anchor to the start of a line (after optional leading whitespace).
    pattern = r"(?m)^[ \t]*" + body + r"[\W_]*"
    return re.compile(pattern, re.IGNORECASE)


def _find_heading_owner(
    chunk_text: str,
    node_labels: list[str],
    heading_regexes: list[re.Pattern],
) -> Optional[str]:
    """Return the node_label whose heading appears latest (last) in the chunk.

    Labels are already sorted longest-first so prefix matches don't steal.
    We use > (not >=) so a longer match at the same start position wins.
    """
    best_label: Optional[str] = None
    best_pos = -1
    for label, rx in zip(node_labels, heading_regexes):
        for m in rx.finditer(chunk_text):
            if m.start() > best_pos:
                best_pos = m.start()
                best_label = label
    return best_label


def extract(
    djvu_text: str,
    page_map: PageMap,
    level_id: str,
    node_labels: list[str],
) -> CitationsRaw:
    # 1. SPLIT
    chunks = djvu_text.split("\x0c")
    n_chunks = len(chunks)
    n_pages = len(page_map.pages)
    if n_chunks != n_pages:
        raise ValueError(
            f"chunk count {n_chunks} != page_map length {n_pages}"
        )

    # Precompile heading regexes (parallel to node_labels).
    # Sort by label length DESCENDING so "Lemma II" is checked before "Lemma I".
    sorted_pairs = sorted(
        zip(node_labels, [_build_heading_regex(lbl) for lbl in node_labels]),
        key=lambda x: -len(x[0])
    )
    sorted_labels = [lbl for lbl, _ in sorted_pairs]
    sorted_heading_rx = [rx for _, rx in sorted_pairs]

    # Track owner order and the citations per owner.
    owner_order: list[str] = []
    owner_citations: dict[str, list[RawCitation]] = {}

    def _ensure_owner(label: str) -> None:
        if label not in owner_citations:
            owner_citations[label] = []
            owner_order.append(label)

    current_owner: Optional[str] = None

    for chunk_text, page in zip(chunks, page_map.pages):
        leaf_index = page.leaf_index
        page_label = page.page_label
        if page_label:
            page_seen = page_label
        else:
            page_seen = f"[leaf {leaf_index}]"

        # 3 (heading update first): detect a new heading in this chunk.
        heading = _find_heading_owner(chunk_text, sorted_labels, sorted_heading_rx)
        if heading is not None:
            current_owner = heading

        # If no owner has ever been set, citations in this chunk are skipped.
        if current_owner is None:
            continue

        lowered = chunk_text.lower()

        # 3 + 5. SCAN citations, collecting spans for the overlap guard.
        cite_spans: list[tuple[int, int]] = []
        chunk_citations: list[RawCitation] = []
        for rx in CITE_PATTERNS:
            for m in rx.finditer(chunk_text):
                phrase = m.group(0)
                # 5. SUBSTRING GUARD (case-insensitive).
                if phrase.lower() not in lowered:
                    continue
                cite_spans.append((m.start(), m.end()))
                chunk_citations.append(
                    RawCitation(
                        phrase=phrase,
                        page_seen=page_seen,
                        vague=False,
                    )
                )

        # Deduplicate citations: if one span fully contains another, keep the longest.
        _dedup_citations: list[RawCitation] = []
        _dedup_spans: list[tuple[int, int]] = []
        for (cs, ce), cit in sorted(zip(cite_spans, chunk_citations), key=lambda x: (x[0][0], -(x[0][1]-x[0][0]))):
            if any(cs >= ds and ce <= de for (ds, de) in _dedup_spans):
                continue
            _dedup_spans.append((cs, ce))
            _dedup_citations.append(cit)
        cite_spans = _dedup_spans
        chunk_citations = _dedup_citations

        # 6. VAGUE scan — skip any vague match overlapping a citation span.
        vague_citations: list[RawCitation] = []
        vague_spans: list[tuple[int, int]] = []
        for rx in VAGUE_PATTERNS:
            for m in rx.finditer(chunk_text):
                vstart, vend = m.start(), m.end()
                overlaps = any(
                    vstart < cend and cstart < vend
                    for (cstart, cend) in cite_spans
                )
                if overlaps:
                    continue
                phrase = m.group(0)
                if phrase.lower() not in lowered:
                    continue
                vague_spans.append((vstart, vend))
                vague_citations.append(
                    RawCitation(
                        phrase=phrase,
                        page_seen=page_seen,
                        vague=True,
                    )
                )

        # Deduplicate vague: if one span fully contains another, keep longest.
        _vd: list[RawCitation] = []
        _vs: list[tuple[int, int]] = []
        for (vs, ve), vc in sorted(zip(vague_spans, vague_citations), key=lambda x: (x[0][0], -(x[0][1]-x[0][0]))):
            if any(vs >= ds and ve <= de for (ds, de) in _vs):
                continue
            _vs.append((vs, ve))
            _vd.append(vc)
        vague_citations = _vd

        if chunk_citations or vague_citations:
            _ensure_owner(current_owner)
            owner_citations[current_owner].extend(chunk_citations)
            owner_citations[current_owner].extend(vague_citations)

    # 7. BUILD
    items: list[RawCiteItem] = []
    for owner in owner_order:
        items.append(
            RawCiteItem(
                local_label=owner,
                citations=owner_citations[owner],
                summary="",
            )
        )

    # 8. EMPTY EDGE CASE handled naturally (items=[]).
    return CitationsRaw(
        schema_version="1.0",
        level_id=level_id,
        source="text",
        items=items,
    )
