# content_parser.py
# DESCENT QED engine — module: content_parser
# PRIME LAW: This module is MATHEMATICS-BLIND. It enforces the STRUCTURE of
# the corridor file format and produces data objects. It NEVER interprets a
# mathematical fact, equation meaning, or color-to-concept mapping.
#
# Pure Python text processing. No third-party deps. No graphics. No math eval.

from __future__ import annotations

import os
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ParseError(Exception):
    """Raised on a structural violation of the corridor file format.

    Always carries the file name and (where known) the offending line so the
    courier/tester can locate the problem without reading this module.
    """


# ---------------------------------------------------------------------------
# Data objects (shared vocabulary — other modules import these)
# ---------------------------------------------------------------------------

@dataclass
class ValueArc:
    latex: str   # sub-expression, surrounding $...$ stripped
    value: str   # concrete number string (trimmed)


@dataclass
class Segment:
    latex: str                          # mathtext, surrounding $...$ stripped
    ledger_key: str                     # a ledger key, or "NEUTRAL"
    exemplify: list = field(default_factory=list)  # list[ValueArc]; [] for SEGMENTS


@dataclass
class RobotData:
    number: int
    name: str
    briefing_hint: str
    problem: str
    explain: dict           # keys EXACTLY: mathematician, physicist, biologist, engineer
    segments: list          # list[Segment], in file order
    eye_color_key: str      # a ledger key, or "NEUTRAL"
    fizzles: dict           # weapon_name -> why-not text
    required_technique_id: str   # <-- ADDED (Brief #9)


@dataclass
class ColorLedger:
    primaries: dict   # key -> one of "red","yellow","blue"
    blends: dict      # key -> (parentKeyA, parentKeyB)

    def is_defined(self, key: str) -> bool:
        """True for any primary key, any blend key, or the reserved key NEUTRAL.

        This module does NOT know what colors mean; it only knows which keys
        the ledger structurally defines.
        """
        if key == "NEUTRAL":
            return True
        return key in self.primaries or key in self.blends


@dataclass
class CorridorData:
    number: int
    title: str
    flavor: str
    briefing_intro: str
    entry_text: str
    exit_text: str
    robots: list      # list[RobotData], in file order
    ledger: ColorLedger


# ---------------------------------------------------------------------------
# Public: discovery
# ---------------------------------------------------------------------------

import re

# Filename pattern: NN_slug.txt . Leading number is human ordering only.
_FILENAME_RE = re.compile(r"^\d+_.+\.txt$")


def discover_corridors(dir_path: str) -> list:
    """Scan dir_path for files matching NN_slug.txt, sort by filename, parse
    each, and return the list of CorridorData. The COUNT of returned items is
    the number of corridors; N is never hard-coded (0..many).
    """
    if not os.path.isdir(dir_path):
        raise ParseError(f"discover_corridors: not a directory: {dir_path!r}")

    names = sorted(
        n for n in os.listdir(dir_path)
        if _FILENAME_RE.match(n) and os.path.isfile(os.path.join(dir_path, n))
    )
    return [parse_corridor(os.path.join(dir_path, n)) for n in names]


# ---------------------------------------------------------------------------
# Low-level block tokenizer
# ---------------------------------------------------------------------------
#
# The file is a flat sequence of items at top level:
#   - comment lines (# ... ) OUTSIDE any block  -> ignored
#   - single-value lines:  KEYWORD: value       (CORRIDOR:, ROBOT:, EYE handled
#                                                 as a block; see below)
#   - blocks:  KEYWORD { ... }  and  FIZZLE <weapon> { ... }  and
#              EYE { <key> }
#
# Braces may span many lines. A literal brace inside text is escaped \{ \}.
# We tokenize the whole file into an ordered list of (kind, ...) tuples so the
# corridor/robot grammar can be enforced by counting ROBOT: lines.

_KEYWORD = r"[A-Z_]+"


def _strip_dollars(s: str) -> str:
    """Strip a single pair of surrounding $...$ from s (after trimming).
    Leaves inner $...$ untouched. If not wrapped, returns trimmed s.
    """
    s = s.strip()
    if len(s) >= 2 and s.startswith("$") and s.endswith("$"):
        return s[1:-1].strip()
    return s


def _tokenize(text: str, fname: str) -> list:
    r"""Produce an ordered token list.

    Tokens:
      ("kv",    keyword, value, lineno)        # KEYWORD: value
      ("block", keyword, arg, body, lineno)    # KEYWORD { body }  (arg=None)
                                               # FIZZLE <weapon> { body } (arg=weapon)
    Comments outside blocks and blank lines are dropped here.

    Brace handling honours \{ and \} escapes (they do not change nesting and
    are preserved verbatim in the body for later un-escaping).
    """
    tokens = []
    i = 0
    n = len(text)
    line = 1

    def err(msg, ln):
        raise ParseError(f"{fname}:{ln}: {msg}")

    while i < n:
        ch = text[i]

        # newline / whitespace tracking
        if ch == "\n":
            line += 1
            i += 1
            continue
        if ch in " \t\r":
            i += 1
            continue

        # comment line (only reachable at top level / line start since we skip
        # whitespace; a '#' that begins meaningful content at top level is a
        # comment to end of line)
        if ch == "#":
            j = text.find("\n", i)
            if j == -1:
                break
            i = j  # newline counted next loop
            continue

        # must be the start of a keyword
        m = re.match(_KEYWORD, text[i:])
        if not m:
            err(f"unexpected character {ch!r} at top level", line)
        keyword = m.group(0)
        kstart_line = line
        i += len(keyword)

        # consume spaces/tabs (not newlines) after keyword
        while i < n and text[i] in " \t":
            i += 1

        if i >= n:
            err(f"keyword {keyword!r} with no value or block", kstart_line)

        # Single-value line:  KEYWORD: value
        if text[i] == ":":
            i += 1
            j = text.find("\n", i)
            if j == -1:
                j = n
            value = text[i:j].strip()
            tokens.append(("kv", keyword, value, kstart_line))
            i = j
            continue

        # FIZZLE <weapon> { ... }  -> capture the weapon argument
        arg = None
        if keyword == "FIZZLE":
            wm = re.match(r"(\S+)", text[i:])
            if not wm:
                err("FIZZLE missing weapon name", kstart_line)
            arg = wm.group(1)
            i += len(arg)
            while i < n and text[i] in " \t":
                i += 1

        # Block:  KEYWORD { ... }
        if i >= n or text[i] != "{":
            err(f"expected '{{' after keyword {keyword!r}", kstart_line)
        i += 1  # consume '{'

        body_chars = []
        depth = 1
        while i < n:
            c = text[i]
            if c == "\\" and i + 1 < n and text[i + 1] in "{}":
                # escaped brace: keep both chars verbatim, do not affect depth
                body_chars.append(c)
                body_chars.append(text[i + 1])
                i += 2
                continue
            if c == "{":
                depth += 1
                body_chars.append(c)
                i += 1
                continue
            if c == "}":
                depth -= 1
                if depth == 0:
                    i += 1
                    break
                body_chars.append(c)
                i += 1
                continue
            if c == "\n":
                line += 1
            body_chars.append(c)
            i += 1
        else:
            err(f"unterminated block {keyword!r} (missing '}}')", kstart_line)

        tokens.append(("block", keyword, arg, "".join(body_chars), kstart_line))

    return tokens


def _unescape_braces(s: str) -> str:
    r"""Convert escaped \{ and \} back to literal { } for storage."""
    return s.replace(r"\{", "{").replace(r"\}", "}")


def _clean_body(body: str) -> str:
    """Trim a block body for prose fields: strip outer whitespace and
    un-escape literal braces. Inner $...$ math is left intact.
    """
    return _unescape_braces(body.strip())


# ---------------------------------------------------------------------------
# Ledger parsing
# ---------------------------------------------------------------------------

_PRIMARY_COLORS = {"red", "yellow", "blue"}


def _parse_ledger(body: str, fname: str, lineno: int) -> ColorLedger:
    """Parse a LEDGER block body. One entry per non-empty line:
        PRIMARY <key> = <color>
        BLEND   <key> = <keyA> + <keyB>
    Structural validation (raises ParseError on any violation):
      - at most 3 PRIMARY entries
      - each PRIMARY color is exactly red/yellow/blue
      - a BLEND names exactly two DISTINCT keys, both PRIMARY keys defined here
    The parser does NOT know what colors mean; it only checks structure.
    """
    primaries: dict = {}
    blends: dict = {}
    # process lines; track approximate line number relative to block start
    for offset, raw in enumerate(body.splitlines(), start=lineno):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue

        if line.startswith("PRIMARY"):
            m = re.match(r"PRIMARY\s+(\S+)\s*=\s*(\S+)\s*$", line)
            if not m:
                raise ParseError(f"{fname}:~{offset}: malformed PRIMARY entry: {line!r}")
            key, color = m.group(1), m.group(2)
            if color not in _PRIMARY_COLORS:
                raise ParseError(
                    f"{fname}:~{offset}: PRIMARY color must be red/yellow/blue, got {color!r}"
                )
            if key in primaries or key in blends:
                raise ParseError(f"{fname}:~{offset}: duplicate ledger key {key!r}")
            primaries[key] = color

        elif line.startswith("BLEND"):
            m = re.match(r"BLEND\s+(\S+)\s*=\s*(\S+)\s*\+\s*(\S+)\s*$", line)
            if not m:
                raise ParseError(f"{fname}:~{offset}: malformed BLEND entry: {line!r}")
            key, a, b = m.group(1), m.group(2), m.group(3)
            if key in primaries or key in blends:
                raise ParseError(f"{fname}:~{offset}: duplicate ledger key {key!r}")
            if a == b:
                raise ParseError(
                    f"{fname}:~{offset}: BLEND {key!r} names two identical keys {a!r}"
                )
            if a not in primaries:
                raise ParseError(
                    f"{fname}:~{offset}: BLEND {key!r} parent {a!r} is not a defined PRIMARY"
                )
            if b not in primaries:
                raise ParseError(
                    f"{fname}:~{offset}: BLEND {key!r} parent {b!r} is not a defined PRIMARY"
                )
            blends[key] = (a, b)

        else:
            raise ParseError(f"{fname}:~{offset}: unknown ledger line: {line!r}")

    if len(primaries) > 3:
        raise ParseError(
            f"{fname}:~{lineno}: ledger has {len(primaries)} PRIMARY entries (max 3)"
        )

    return ColorLedger(primaries=primaries, blends=blends)


# ---------------------------------------------------------------------------
# Segment parsing
# ---------------------------------------------------------------------------

def _parse_segments(body: str, ledger: ColorLedger, fname: str, lineno: int) -> list:
    """Parse a SEGMENTS block. One segment per non-empty line:
        <mathtext> | <ledger_key>
    Split on the LAST '|'. Strip surrounding $...$ from mathtext.
    Validate that every ledger_key is ledger.is_defined(key).
    Segment.exemplify is always [] (value arcs are NOT in SEGMENTS).
    """
    segments = []
    for offset, raw in enumerate(body.splitlines(), start=lineno):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if "|" not in line:
            raise ParseError(f"{fname}:~{offset}: segment line missing '|': {line!r}")
        math_part, _, key_part = line.rpartition("|")
        latex = _strip_dollars(math_part)
        key = key_part.strip()
        if not ledger.is_defined(key):
            raise ParseError(
                f"{fname}:~{offset}: segment ledger key {key!r} is not defined in ledger"
            )
        segments.append(Segment(latex=latex, ledger_key=key, exemplify=[]))
    return segments


# ---------------------------------------------------------------------------
# VULNERABLE_TO parsing (Brief #9 — TODO(DeepSeek): this needs to be
# integrated into _parse_robot()'s block-token dispatch, NOT called as a
# standalone line-by-line parser. The tokenizer already produces block
# tokens for this directive. Follow the existing EYE { } pattern.)
_VULNERABLE_RE = re.compile(r'VULNERABLE_TO\s*\{\s*([A-Za-z0-9_]+)\s*\}')

def _parse_vulnerable_to(line, lineno, filename):
    """Returns the technique id token, or None if this line isn't the directive."""
    m = _VULNERABLE_RE.search(line)
    if m:
        return m.group(1)
    return None

# Value-arc parsing (public helper)
# ---------------------------------------------------------------------------

# Markup:  [[ $expr$ | value ]]
# We match the smallest non-greedy span between [[ and ]], then split on the
# LAST '|' inside it (expr may itself contain no pipe, but be safe).
_VALUE_ARC_RE = re.compile(r"\[\[(.*?)\]\]", re.DOTALL)


def parse_value_arcs(text: str) -> list:
    """Extract value-arc markup of the form  [[ $expr$ | value ]]  from text.

    Returns a list of ValueArc in order of appearance. For each:
      - split the inner content on the LAST '|';
      - left side -> strip surrounding $...$  -> ValueArc.latex
      - right side -> trimmed string          -> ValueArc.value
    Markup with no '|' inside is ignored (not a value arc).
    The raw text (with [[..]] intact) is what reading_system re-parses for
    layout; this helper is provided so it need not re-implement extraction.
    """
    arcs = []
    for m in _VALUE_ARC_RE.finditer(text):
        inner = m.group(1)
        if "|" not in inner:
            continue
        expr_part, _, value_part = inner.rpartition("|")
        arcs.append(ValueArc(latex=_strip_dollars(expr_part), value=value_part.strip()))
    return arcs


# ---------------------------------------------------------------------------
# Corridor / robot assembly
# ---------------------------------------------------------------------------

# The required corridor header blocks, in order (FLAVOR optional).
# We do not hard-code counts of robots/corridors anywhere.

def parse_corridor(file_path: str) -> CorridorData:
    """Parse one corridor file into a CorridorData (see CORRIDOR FILE FORMAT
    v0.2). Robot count is derived by counting ROBOT: lines; never declared.
    """
    fname = os.path.basename(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        raise ParseError(f"{fname}: cannot read file: {e}")

    tokens = _tokenize(text, fname)
    if not tokens:
        raise ParseError(f"{fname}: empty or contains no parseable content")

    # ---- Split header tokens from robot blocks at the first ROBOT: kv -------
    first_robot = None
    for idx, tok in enumerate(tokens):
        if tok[0] == "kv" and tok[1] == "ROBOT":
            first_robot = idx
            break
    if first_robot is None:
        header_tokens = tokens
        robot_tokens = []
    else:
        header_tokens = tokens[:first_robot]
        robot_tokens = tokens[first_robot:]

    # ---- Parse corridor header ---------------------------------------------
    corridor_number = None
    title = None
    flavor = ""
    ledger = None
    briefing_intro = None
    entry_text = None
    exit_text = None

    for tok in header_tokens:
        kind = tok[0]
        if kind == "kv":
            keyword, value, ln = tok[1], tok[2], tok[3]
            if keyword == "CORRIDOR":
                try:
                    corridor_number = int(value.strip())
                except ValueError:
                    raise ParseError(f"{fname}:{ln}: CORRIDOR value not an int: {value!r}")
            else:
                raise ParseError(f"{fname}:{ln}: unexpected single-value line {keyword}: in header")
        else:  # block
            keyword, arg, body, ln = tok[1], tok[2], tok[3], tok[4]
            if keyword == "TITLE":
                title = _clean_body(body)
            elif keyword == "FLAVOR":
                flavor = _clean_body(body)
            elif keyword == "LEDGER":
                ledger = _parse_ledger(body, fname, ln)
            elif keyword == "BRIEFING_INTRO":
                briefing_intro = _clean_body(body)
            elif keyword == "ENTRY_TEXT":
                entry_text = _clean_body(body)
            elif keyword == "EXIT_TEXT":
                exit_text = _clean_body(body)
            else:
                raise ParseError(f"{fname}:{ln}: unexpected header block {keyword!r}")

    # required header fields
    if corridor_number is None:
        raise ParseError(f"{fname}: missing CORRIDOR: line")
    if title is None:
        raise ParseError(f"{fname}: missing TITLE block")
    if ledger is None:
        raise ParseError(f"{fname}: missing LEDGER block")
    if briefing_intro is None:
        raise ParseError(f"{fname}: missing BRIEFING_INTRO block")
    if entry_text is None:
        raise ParseError(f"{fname}: missing ENTRY_TEXT block")
    if exit_text is None:
        raise ParseError(f"{fname}: missing EXIT_TEXT block")

    # ---- Parse robots: each runs from a ROBOT: kv to the next/EOF ----------
    robots = []
    cur_start = None
    for idx, tok in enumerate(robot_tokens):
        if tok[0] == "kv" and tok[1] == "ROBOT":
            if cur_start is not None:
                robots.append(_parse_robot(robot_tokens[cur_start:idx], ledger, fname))
            cur_start = idx
    if cur_start is not None:
        robots.append(_parse_robot(robot_tokens[cur_start:], ledger, fname))

    return CorridorData(
        number=corridor_number,
        title=title,
        flavor=flavor,
        briefing_intro=briefing_intro,
        entry_text=entry_text,
        exit_text=exit_text,
        robots=robots,
        ledger=ledger,
    )


def _parse_robot(toks: list, ledger: ColorLedger, fname: str) -> RobotData:
    """Parse one robot block's token slice (begins with a ROBOT: kv)."""
    head = toks[0]
    if not (head[0] == "kv" and head[1] == "ROBOT"):
        raise ParseError(f"{fname}: robot block does not start with ROBOT: line")
    try:
        number = int(head[2].strip())
    except ValueError:
        raise ParseError(f"{fname}:{head[3]}: ROBOT value not an int: {head[2]!r}")

    name = None
    briefing_hint = None
    problem = None
    explain = {}
    segments = []
    eye = None
    fizzles = {}

    _explain_map = {
        "EXPLAIN_MATHEMATICIAN": "mathematician",
        "EXPLAIN_PHYSICIST": "physicist",
        "EXPLAIN_BIOLOGIST": "biologist",
        "EXPLAIN_ENGINEER": "engineer",
    }

    for tok in toks[1:]:
        if tok[0] == "kv":
            # No single-value lines expected inside a robot besides ROBOT:,
            # which would have started a new block already.
            raise ParseError(f"{fname}:{tok[3]}: unexpected single-value line {tok[1]}: inside robot")
        keyword, arg, body, ln = tok[1], tok[2], tok[3], tok[4]
        if keyword == "NAME":
            name = _clean_body(body)
        elif keyword == "BRIEFING_HINT":
            briefing_hint = _clean_body(body)
        elif keyword == "PROBLEM":
            problem = _clean_body(body)
        elif keyword in _explain_map:
            explain[_explain_map[keyword]] = _clean_body(body)
        elif keyword == "SEGMENTS":
            segments = _parse_segments(body, ledger, fname, ln)
        elif keyword == "EYE":
            key = _clean_body(body).strip()
            if not ledger.is_defined(key):
                raise ParseError(f"{fname}:{ln}: EYE key {key!r} not defined in ledger")
            eye = key
        elif keyword == "FIZZLE":
            if arg is None:
                raise ParseError(f"{fname}:{ln}: FIZZLE missing weapon name")
            fizzles[arg] = _clean_body(body)
        else:
            raise ParseError(f"{fname}:{ln}: unexpected robot block {keyword!r}")

    # required robot fields
    if name is None:
        raise ParseError(f"{fname}: robot {number} missing NAME block")
    if briefing_hint is None:
        raise ParseError(f"{fname}: robot {number} missing BRIEFING_HINT block")
    if problem is None:
        raise ParseError(f"{fname}: robot {number} missing PROBLEM block")
    for required in ("mathematician", "physicist", "biologist", "engineer"):
        if required not in explain:
            raise ParseError(f"{fname}: robot {number} missing EXPLAIN_{required.upper()} block")
    if eye is None:
        raise ParseError(f"{fname}: robot {number} missing EYE block")

    return RobotData(
        number=number,
        name=name,
        briefing_hint=briefing_hint,
        problem=problem,
        explain=explain,
        segments=segments,
        eye_color_key=eye,
        fizzles=fizzles,
    )


# === DEEPSEEK TODO SUMMARY ===
# no DeepSeek TODOs