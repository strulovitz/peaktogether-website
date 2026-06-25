"""Normalize verbatim Principia citation phrases to target node ids.

Pure, deterministic, IO-free.
"""

from __future__ import annotations

import re

from map.raw_models import NodeId, NodesRaw

# LabelIndex: maps a normalized lookup key -> the node's proposed_id
# Examples of keys: "lemma 1", "prop 11", "law 2", "cor 2 prop 4", "def 3"
LabelIndex = dict[str, NodeId]


# --- Roman numeral parsing ---------------------------------------------------

_ROMAN_VALUES = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}


def roman_to_int(s: str) -> int:
    """Standard additive/subtractive Roman numeral parsing (I,V,X,L,C)."""
    s = s.strip().lower()
    total = 0
    prev = 0
    for ch in reversed(s):
        val = _ROMAN_VALUES.get(ch)
        if val is None:
            raise ValueError(f"invalid roman numeral: {s!r}")
        if val < prev:
            total -= val
        else:
            total += val
            prev = val
    return total


_ROMAN_RE = re.compile(r"^[ivxlc]+$", re.IGNORECASE)


def _is_roman(token: str) -> bool:
    return bool(_ROMAN_RE.match(token))


# --- Kind normalization ------------------------------------------------------

_KIND_MAP = {
    "law": "law",
    "laws": "law",
    "lem": "lemma",
    "lemma": "lemma",
    "prop": "prop",
    "proposition": "prop",
    "cor": "cor",
    "corollary": "cor",
    "def": "def",
    "definition": "def",
}

_KIND_FROM_ID = {
    "law": "law",
    "lemma": "lemma",
    "prop": "prop",
    "cor": "cor",
    "def": "def",
}

_SPELLED_ORDINALS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
}


# --- build_index -------------------------------------------------------------

_ID_NUM_RE = re.compile(r"^\d+$")


def build_index(nodes_raw: NodesRaw) -> LabelIndex:
    """Build the lookup index from the STRUCTURE-pass nodes_raw output."""
    index: LabelIndex = {}
    for node in nodes_raw.nodes:
        pid = node.proposed_id
        # Split off leading kind letters and trailing/embedded digits, since
        # proposed ids may be either "lemma_7" or "lemma7" / "cor2_prop4".
        tokens = _tokenize_id(pid)
        if not tokens:
            continue
        key_parts: list[str] = []
        for tok in tokens:
            if tok in _KIND_FROM_ID:
                key_parts.append(tok)
            elif _ID_NUM_RE.match(tok):
                key_parts.append(str(int(tok)))
            else:
                key_parts.append(tok)
        key = " ".join(key_parts)
        index[key] = pid
    return index


_ID_SPLIT_RE = re.compile(r"[a-z]+|\d+")


def _tokenize_id(pid: str) -> list[str]:
    """Split a proposed_id into alternating kind/number tokens.

    Handles "law_2", "lemma7", "cor2_prop4", "cor_2_prop_4".
    """
    return _ID_SPLIT_RE.findall(pid.lower())


# --- normalize ---------------------------------------------------------------

_VAGUE_PHRASES = {
    "as shown above",
    "as was shown above",
    "as demonstrated above",
    "as was demonstrated above",
    "by what was demonstrated",
    "above",
    "the preceding",
}

_LEADING_PREFIXES = ("by ", "per ")
_TRAILING_SUFFIXES = (" of this book", " of the laws", " of motion")


def normalize(phrase: str, label_index: LabelIndex) -> NodeId | None:
    """Parse a verbatim citation phrase and return the target node_id, or None."""
    if phrase is None:
        return None

    raw = phrase.strip()
    work = re.sub(r"\s+", " ", raw).strip()
    lowered = work.lower()

    # STEP 1 — vague phrases.
    if lowered in _VAGUE_PHRASES:
        return None
    # vague with a leading prefix stripped (e.g. "by what was demonstrated")
    stripped_for_vague = lowered
    for pref in _LEADING_PREFIXES:
        if stripped_for_vague.startswith(pref):
            stripped_for_vague = stripped_for_vague[len(pref):]
            break
    if stripped_for_vague.strip() in _VAGUE_PHRASES:
        return None

    # STEP 2 — strip prefixes/suffixes.
    s = lowered
    for pref in _LEADING_PREFIXES:
        if s.startswith(pref):
            s = s[len(pref):]
            break

    of_the_laws = " of the laws" in s

    for suf in _TRAILING_SUFFIXES:
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    s = s.strip()

    # STEP 3 — tokenize into kinds and numbers.
    tokens = re.findall(r"[a-z]+\.?|\d+", s)

    parsed: list[tuple[str, object]] = []  # ("kind", str) | ("num", int)
    for tok in tokens:
        clean = tok.rstrip(".")
        if clean in _KIND_MAP:
            parsed.append(("kind", _KIND_MAP[clean]))
        elif clean in _SPELLED_ORDINALS:
            parsed.append(("num", _SPELLED_ORDINALS[clean]))
        elif clean.isdigit():
            parsed.append(("num", int(clean)))
        elif _is_roman(clean):
            try:
                parsed.append(("num", roman_to_int(clean)))
            except ValueError:
                pass
        # else: ignore noise tokens (the, of, etc.)

    # Collect ordered kinds and numbers.
    kinds = [v for (t, v) in parsed if t == "kind"]
    numbers = [v for (t, v) in parsed if t == "num"]

    if not kinds or not numbers:
        return None

    # Special frozen rule: "Cor. N. of the Laws" -> "law N".
    if of_the_laws and kinds and kinds[0] == "cor":
        n = numbers[0]
        key = f"law {n}"
        return label_index.get(key)

    # STEP 4 — assemble key.
    # Compound: Cor. N. Prop. M.
    if kinds[0] == "cor" and "prop" in kinds[1:]:
        cor_n = numbers[0]
        # prop number is the number associated after the prop kind; take last.
        prop_m = numbers[-1] if len(numbers) >= 2 else numbers[0]
        compound = f"cor {cor_n} prop {prop_m}"
        if compound in label_index:
            return label_index[compound]
        parent = f"prop {prop_m}"
        return label_index.get(parent)

    # Single kind + number (use first kind, first number).
    kind = kinds[0]
    num = numbers[0]
    key = f"{kind} {num}"

    # STEP 5 — lookup.
    return label_index.get(key)
