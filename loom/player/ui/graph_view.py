"""
graph_view.py — the function's picture, and scrub surface #2. [BONE M2]

Scripture: BIBLE par.4 + par.10: the Player never evaluates f(x) — it
draws the POLYLINE the Compiler precomputed (spell raw: dense graph
points + per-note segment mapping). Dragging ON the graph scrubs, via
the precompiled x<->beats note regions (lookup, not math). The active
segment glows; crossed notes flash (highlight_decay_ms).

FATTEN ME LIKE THIS (M2 parent): same command pattern as
bench_transport (emit TransportEvents); share its click-vs-drag feel
constants. Pixel mapping = linear interpolation over precompiled
points — that is "simple arithmetic on precompiled numbers", allowed.
"""

from __future__ import annotations


class GraphView:
    """Frozen interface."""

    def __init__(self, rect) -> None:
        raise NotImplementedError("M2")

    def handle_event(self, pygame_event, spell) -> list:   # list[TransportEvent]
        raise NotImplementedError("M2")

    def draw(self, surface, spell, frame, flash_levels) -> None:
        raise NotImplementedError("M2")
