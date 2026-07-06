"""
bench_transport.py — the VLC-style transport + timeline. [BONE M2]

Scripture: BIBLE par.3 (Scrubbing is a PILLAR) + New Testament par.II.
This widget is scrub surface #1 (the graph is #2). It emits COMMANDS;
the wiring applies them to the Conductor — the widget never holds one.

FATTEN ME LIKE THIS (M2 parent): extract m1_demo.py's proven inline
logic (click-vs-drag threshold, bar<->beats mapping, release=paused)
into this class, unchanged in behavior. m1_demo then shrinks to a
thin harness — behavior is already ear-approved by Nir; keep it exact.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TransportCommand(Enum):
    PLAY_PAUSE = auto(); STOP = auto()
    JUMP = auto(); SCRUB_BEGIN = auto(); SCRUB_TO = auto(); SCRUB_END = auto()


@dataclass(frozen=True)
class TransportEvent:
    command: TransportCommand
    beats: float = 0.0          # for JUMP / SCRUB_TO


class TransportWidget:
    """Frozen interface."""

    def __init__(self, rect) -> None:
        raise NotImplementedError("M2")

    def handle_event(self, pygame_event, total_beats: float) -> list[TransportEvent]:
        raise NotImplementedError("M2")

    def draw(self, surface, frame, total_beats: float) -> None:
        raise NotImplementedError("M2")
