"""Static text-level lint of a generated figure.asy (§3.A.5 invariants).

Pure, deterministic text scan. Does NOT execute Asymptote (that is
asy_compile's job). Returns plain-English violation strings; empty = clean.
"""

from __future__ import annotations

import re
from pathlib import Path

from map.raw_models import Palette, GroupName  # noqa: F401  (GroupName per contract)

_IMPORT_RE = re.compile(r"\bimport\s+prooffig\s*;")
_HIGHLIGHT_RE = re.compile(r"\bint\s+highlight\s*=\s*-1\s*;")
_DRAWALL_RE = re.compile(r"\bdrawAll\s*\(\s*highlight\s*\)\s*;")

_ZONE_RES = [
    re.compile(r"ZONE\s+1\b[^\n]*settings", re.IGNORECASE),
    re.compile(r"ZONE\s+2\b[^\n]*construction", re.IGNORECASE),
    re.compile(r"ZONE\s+3\b[^\n]*registration", re.IGNORECASE),
    re.compile(r"ZONE\s+4\b[^\n]*render", re.IGNORECASE),
]

# elem((path)(...), "group", step [, "marker"] ...)
_ELEM_RE = re.compile(
    r'elem\(\s*[^,]+,\s*"([a-z][a-z0-9_]*)"\s*,\s*(\d+)\s*(?:,\s*"([^"]*)")?'
)
# lbl("$..$", at, "group", step, ...)
_LBL_RE = re.compile(
    r'lbl\(\s*"([^"]*)"\s*,\s*([^"]*?),\s*"([a-z][a-z0-9_]*)"\s*,\s*(\d+)'
)

_RESERVED_SCALARS = {"grey_ink", "grey_text", "bg_key", "map_node_default"}
_RESERVED_IMPORTANCE = {f"map_importance.{i}" for i in range(1, 6)}


def lint(figure_asy: Path, palette: Palette, n_steps: int) -> list[str]:
    """Text-level lint. Returns plain-English violations. Empty = clean."""
    text = Path(figure_asy).read_text(encoding="utf-8")
    violations: list[str] = []

    # 1. import prooffig
    if not _IMPORT_RE.search(text):
        violations.append("MISSING_IMPORT: file does not import prooffig")

    # 2. int highlight=-1;
    if not _HIGHLIGHT_RE.search(text):
        violations.append("MISSING_HIGHLIGHT: no 'int highlight=-1;' declaration")

    # 3. ends with drawAll(highlight);
    last_stmt = _last_code_line(text)
    if last_stmt is None or not _DRAWALL_RE.search(last_stmt):
        violations.append("MISSING_DRAWALL: file does not end with drawAll(highlight)")

    # 4. four zone markers in order
    search_from = 0
    for idx, zre in enumerate(_ZONE_RES, start=1):
        m = zre.search(text, search_from)
        if m is None:
            violations.append(f"MISSING_ZONE_{idx}: zone {idx} marker not found")
        else:
            search_from = m.end()

    # 5. parse elem/lbl calls
    valid_groups = set(palette.groups.keys()) | _RESERVED_SCALARS | _RESERVED_IMPORTANCE

    used_steps: set[int] = set()
    seen_unknown: set[str] = set()

    for m in _ELEM_RE.finditer(text):
        group, step_s, marker = m.group(1), m.group(2), m.group(3)
        step = int(step_s)
        used_steps.add(step)
        if group not in valid_groups and group not in seen_unknown:
            seen_unknown.add(group)
            violations.append(
                f"UNKNOWN_GROUP: elem/lbl uses group '{group}' not in palette"
            )
        # 7. marker check
        if marker == "tick":
            violations.append("BAD_MARKER: marker 'tick' used (must be none or dot)")

        for m in _LBL_RE.finditer(text):
            group, step_s = m.group(3), m.group(4)
            step = int(step_s)
            used_steps.add(step)
            if group not in valid_groups and group not in seen_unknown:
                seen_unknown.add(group)
                violations.append(
                    f"UNKNOWN_GROUP: elem/lbl uses group '{group}' not in palette"
                )

    # 5b. steps contiguous from 1..n_steps
    for k in range(1, n_steps + 1):
        if k not in used_steps:
            violations.append(f"STEP_GAP: step {k} never registered in elem/lbl calls")

    return violations


def _last_code_line(text: str) -> str | None:
    """Return the last non-blank, non-comment line of source, or None."""
    for raw in reversed(text.splitlines()):
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("//"):
            continue
        return stripped
    return None
