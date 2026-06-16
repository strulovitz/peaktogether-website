# level_parser.py
# DESCENT QED engine — module: level_parser  (sibling of content_parser)
#
# PRIME LAW: MATHEMATICS-BLIND. This module groups corridors into an ordered,
# titled LEVEL. It parses STRUCTURE only (which corridors, in what order, the
# level's title). It NEVER interprets mathematics and NEVER assigns color.
#
# It does NOT redefine how a single corridor is parsed. It CALLS the existing
# content_parser.parse_corridor / discover_corridors. content_parser.py is
# UNCHANGED.
#
# Pure Python. No third-party deps. No graphics. No math eval.

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

# Reuse the existing single-corridor layer verbatim — do not reimplement it.
from content_parser import (
    CorridorData,
    ParseError,
    parse_corridor,
)


# ---------------------------------------------------------------------------
# Data object
# ---------------------------------------------------------------------------

@dataclass
class Level:
    """An ordered, distinct collection of corridors plus a display title.

    A Level IS iterable: iterating it yields its CorridorData in order, so
    hub_builder.build_hub(level) works directly (build_hub iterates its
    argument and reads .title off each item). build_hub(level.corridors)
    also works, since .corridors is a list[CorridorData].
    """
    title: str
    corridors: list = field(default_factory=list)  # list[CorridorData], ORDERED, DISTINCT

    def __iter__(self):
        return iter(self.corridors)

    def __len__(self):
        return len(self.corridors)


# ---------------------------------------------------------------------------
# Manifest filename convention (mirrors content_parser's NN_slug.txt style)
# ---------------------------------------------------------------------------

# A level manifest is any .txt under the levels/ folder. We do not impose
# NN_ ordering on level files (a level is named, not numbered), but we keep
# the .txt suffix to match the project's plain-text fixture style.
_LEVEL_FILE_RE = re.compile(r".+\.txt$")


# ---------------------------------------------------------------------------
# Manifest tokenizer
# ---------------------------------------------------------------------------
#
# ON-DISK FORMAT — Option A, LEVEL MANIFEST FILE. Dead simple, line-based,
# consistent with the project's plain-text fixtures:
#
#     # comments allowed, full-line, start with '#'
#     title: <the level display name>
#     corridors:
#       <relative-or-absolute path to a corridor fixture>
#       <another path>
#       ...
#
# Rules:
#   - exactly one `title:` line (required, non-empty).
#   - exactly one `corridors:` line, followed by 1..N indented path lines.
#   - corridor paths are resolved RELATIVE TO THE MANIFEST FILE'S directory
#     (so a manifest in levels/ can say `../corridors/01_dummy.txt` or, if you
#     keep corridors alongside, `corridors/...`). Absolute paths pass through.
#   - blank lines and `#` comment lines are ignored.
#
# Why Option A (manifest) over Option B (folder-as-level): a level needs
# EXPLICIT, ORDERED, DISTINCT membership and a real display title. Folder
# discovery only gives implicit filename ordering and no clean title source.
# The manifest makes "which corridors form this level, in what order" auditable
# in one file, and lets the same corridor fixture belong to multiple levels.


def _read_manifest(path: str) -> tuple[str, str, list[str]]:
    """Parse a level manifest file into (title, baked_dir, [corridor_path, ...]).

    `baked_dir` is the OPTIONAL `baked:` folder (where Understanding Mode's
    pre-baked LaTeX PNGs live), resolved against the manifest's directory.
    "" when absent. Paths are returned already resolved.
    Raises ParseError with file:line on any structural violation.
    """
    fname = os.path.basename(path)
    base_dir = os.path.dirname(os.path.abspath(path))

    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw_lines = fh.readlines()
    except OSError as e:
        raise ParseError(f"{fname}: cannot read level manifest: {e}")

    title = None
    baked_dir = None          # Brief #A — optional baked-PNG folder
    corridor_paths: list[str] = []
    in_corridors = False

    for lineno, raw in enumerate(raw_lines, start=1):
        # Preserve indentation knowledge but work on a stripped copy for keywords.
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue

        low = stripped.lower()

        if low.startswith("title:"):
            if title is not None:
                raise ParseError(f"{fname}:{lineno}: duplicate 'title:' line")
            title = stripped[len("title:"):].strip()
            if not title:
                raise ParseError(f"{fname}:{lineno}: 'title:' is empty")
            in_corridors = False
            continue

        if low.startswith("baked:"):            # Brief #A
            if baked_dir is not None:
                raise ParseError(f"{fname}:{lineno}: duplicate 'baked:' line")
            rel = stripped[len("baked:"):].strip()
            if not rel:
                raise ParseError(f"{fname}:{lineno}: 'baked:' is empty")
            baked_dir = rel if os.path.isabs(rel) else os.path.normpath(
                os.path.join(base_dir, rel)
            )
            in_corridors = False
            continue

        if low == "corridors:" or low.startswith("corridors:"):
            # Allow `corridors:` alone (paths follow) — reject inline content,
            # to keep the format unambiguous.
            trailing = stripped[len("corridors:"):].strip()
            if trailing:
                raise ParseError(
                    f"{fname}:{lineno}: put corridor paths on their own indented "
                    f"lines, not after 'corridors:'"
                )
            in_corridors = True
            continue

        # Any other non-blank, non-comment line:
        if in_corridors:
            # Treat as a corridor path entry.
            rel = stripped
            resolved = rel if os.path.isabs(rel) else os.path.normpath(
                os.path.join(base_dir, rel)
            )
            corridor_paths.append(resolved)
        else:
            raise ParseError(
                f"{fname}:{lineno}: unexpected line before 'corridors:': {stripped!r}"
            )

    if title is None:
        raise ParseError(f"{fname}: missing 'title:' line")
    if not corridor_paths:
        raise ParseError(f"{fname}: 'corridors:' lists no corridor files")

    return title, (baked_dir or ""), corridor_paths


# ---------------------------------------------------------------------------
# Public: load a level
# ---------------------------------------------------------------------------

def load_level(path: str) -> Level:
    """Load a LEVEL from a manifest file (Option A).

    path: a level manifest file (e.g. levels/intro.txt).

    Returns a Level whose .corridors is the ORDERED list of CorridorData,
    one per manifest entry, parsed by the EXISTING content_parser.parse_corridor.

    ERROR BEHAVIOR (explicit, never silent):
      - missing manifest / missing listed fixture -> ParseError.
      - a corridor path listed more than once in one manifest -> ParseError
        (we do NOT silently de-dupe and we NEVER clone to pad N).
      - any structural error inside a corridor fixture propagates as the
        ParseError raised by content_parser.parse_corridor (with that file's
        own file:line), unchanged.
    """
    if not os.path.isfile(path):
        raise ParseError(f"load_level: not a file: {path!r}")

    title, baked_dir, corridor_paths = _read_manifest(path)   # Brief #A
    manifest_name = os.path.basename(path)

    # Reject duplicates by resolved absolute path — distinctness is a hard rule.
    seen: set[str] = set()
    for p in corridor_paths:
        key = os.path.abspath(p)
        if key in seen:
            raise ParseError(
                f"{manifest_name}: corridor listed more than once: {p!r} "
                f"(a level's corridors must be DISTINCT; refusing to clone)"
            )
        seen.add(key)

    corridors: list[CorridorData] = []
    for p in corridor_paths:
        if not os.path.isfile(p):
            raise ParseError(
                f"{manifest_name}: listed corridor fixture not found: {p!r}"
            )
        # Delegate ALL single-corridor parsing to the existing layer.
        cd = parse_corridor(p)
        cd.understanding_dir = baked_dir            # Brief #A
        for r in cd.robots:                          # propagate to each RobotData
            r.understanding_dir = baked_dir
        corridors.append(cd)

    return Level(title=title, corridors=corridors)


# ---------------------------------------------------------------------------
# Public: discovery (mirrors discover_corridors' style)
# ---------------------------------------------------------------------------

def discover_levels(folder: str = "levels") -> list[str]:
    """Scan `folder` for level manifest files (*.txt), sorted by filename,
    and return their paths. Mirrors content_parser.discover_corridors in
    style: returns paths (the COUNT is derived, never hard-coded).

    Note: this returns PATHS (callers then load_level each), whereas
    discover_corridors returns parsed objects. We return paths here because a
    caller usually wants to pick ONE level to play, not parse them all.
    """
    if not os.path.isdir(folder):
        raise ParseError(f"discover_levels: not a directory: {folder!r}")

    names = sorted(
        n for n in os.listdir(folder)
        if _LEVEL_FILE_RE.match(n) and os.path.isfile(os.path.join(folder, n))
    )
    return [os.path.join(folder, n) for n in names]