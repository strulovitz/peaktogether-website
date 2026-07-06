"""
bench_transport.py — the VLC-style transport + timeline. [M2 — Parent 3]

Scripture: BIBLE par.1 pillar 3 + par.3.2 (Scrubbing) + NT par.II.4.
Scrub surface #1 (the graph is #2). The widget EMITS TransportEvents;
the wiring applies them to the Conductor — the widget never holds one.

EXTRACTION NOTE (on the record): the click-vs-drag threshold (3 px),
the pixel<->beats mapping, release=paused and click=jump are lifted
from m1_demo.py UNCHANGED IN BEHAVIOR — that feel is already
ear-approved by Nir. If the threshold ever needs tuning it should
migrate to scrub_tuning.json via Nir + a Commentaries note.

Internal layout (derived from the rect passed in; layout.py stays the
only owner of the rect itself): a square Play/Pause button at the
left, a Stop button beside it, then the timeline groove filling the
rest, with a small beats/seconds readout above the groove.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import pygame

_DRAG_THRESHOLD_PX = 3                 # m1_demo's proven constant, verbatim
_GLOW = (255, 196, 64)
_HANDLE = (240, 220, 120)
_GROOVE = (50, 50, 60)
_BTN = (60, 60, 72)
_BTN_ICON = (225, 225, 225)
_TEXT = (170, 170, 180)


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
        self.rect = pygame.Rect(rect)
        pad = 6
        btn = self.rect.h - 2 * pad
        self._play_rect = pygame.Rect(self.rect.x + pad,
                                      self.rect.y + pad, btn, btn)
        self._stop_rect = pygame.Rect(self._play_rect.right + pad,
                                      self.rect.y + pad, btn, btn)
        groove_x = self._stop_rect.right + 2 * pad
        self._groove = pygame.Rect(groove_x,
                                   self.rect.centery - 5,
                                   self.rect.right - pad - groove_x, 10)
        self._down_pos = None
        self._dragging = False
        self._font = None

    # ---- m1_demo's mapping, verbatim in behavior ---------------------
    def _bar_to_beats(self, px: int, total_beats: float) -> float:
        return (px - self._groove.x) / self._groove.w * total_beats

    def handle_event(self, pygame_event, total_beats: float) -> list[TransportEvent]:
        ev = pygame_event
        out: list[TransportEvent] = []
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self._play_rect.collidepoint(ev.pos):
                out.append(TransportEvent(TransportCommand.PLAY_PAUSE))
            elif self._stop_rect.collidepoint(ev.pos):
                out.append(TransportEvent(TransportCommand.STOP))
            elif self._groove.inflate(0, 24).collidepoint(ev.pos):
                self._down_pos = ev.pos
                self._dragging = False
        elif ev.type == pygame.MOUSEMOTION and self._down_pos is not None:
            if (not self._dragging
                    and abs(ev.pos[0] - self._down_pos[0]) > _DRAG_THRESHOLD_PX):
                self._dragging = True
                out.append(TransportEvent(TransportCommand.SCRUB_BEGIN))
            if self._dragging:
                out.append(TransportEvent(
                    TransportCommand.SCRUB_TO,
                    self._bar_to_beats(ev.pos[0], total_beats)))
        elif (ev.type == pygame.MOUSEBUTTONUP and ev.button == 1
              and self._down_pos is not None):
            if self._dragging:
                out.append(TransportEvent(TransportCommand.SCRUB_END))
            else:
                out.append(TransportEvent(
                    TransportCommand.JUMP,
                    self._bar_to_beats(self._down_pos[0], total_beats)))
            self._down_pos, self._dragging = None, False
        return out

    def draw(self, surface, frame, total_beats: float) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont("consolas", 14)
        # buttons
        pygame.draw.rect(surface, _BTN, self._play_rect, border_radius=4)
        pygame.draw.rect(surface, _BTN, self._stop_rect, border_radius=4)
        p = self._play_rect
        playing = (frame is not None and frame.state.name == "PLAYING")
        if playing:                                   # pause icon: two bars
            w = p.w // 5
            pygame.draw.rect(surface, _BTN_ICON,
                             (p.x + w, p.y + w, w, p.h - 2 * w))
            pygame.draw.rect(surface, _BTN_ICON,
                             (p.right - 2 * w, p.y + w, w, p.h - 2 * w))
        else:                                         # play icon: triangle
            m = p.w // 4
            pygame.draw.polygon(surface, _BTN_ICON,
                                [(p.x + m, p.y + m),
                                 (p.x + m, p.bottom - m),
                                 (p.right - m, p.centery)])
        s = self._stop_rect
        m = s.w // 4
        pygame.draw.rect(surface, _BTN_ICON,
                         (s.x + m, s.y + m, s.w - 2 * m, s.h - 2 * m))
        # groove + handle (m1_demo's look, relocated)
        pygame.draw.rect(surface, _GROOVE, self._groove)
        if total_beats > 0 and frame is not None:
            px = (self._groove.x
                  + self._groove.w * frame.playhead_beats / total_beats)
            pygame.draw.rect(surface, _HANDLE,
                             (int(px) - 2, self._groove.y - 8,
                              4, self._groove.h + 16))
            txt = (f"{frame.state.name:9s} beat {frame.playhead_beats:5.2f}  "
                   f"{frame.playhead_seconds:5.2f}s")
            surface.blit(self._font.render(txt, True, _TEXT),
                         (self._groove.x, self._groove.y - 24))
