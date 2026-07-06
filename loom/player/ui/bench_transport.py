"""
bench_transport.py — the VLC-style transport + timeline + BPM box.
[M2 — Parent 3, rev 3]

Scripture: BIBLE par.1 pillar 3 + par.3.2 + NT par.II.4. Scrub surface
#1. Emits TransportEvents; never holds a Conductor.

REV 3 (Nir's BPM feature, July 2026): a BPM cluster on the FAR RIGHT
(opposite side from play/pause, per Nir — no adjacent triangles):
  [bpm] [ 110 ] [▲/▼]
- Click the box -> it focuses (empties); type digits; ENTER commits,
  ESC cancels, clicking elsewhere commits. Commit clamps to 40..200.
- The spinners step +/-1 and clamp; events fire only on real change.
- While the box is focused, .typing is True: the wiring MUST skip the
  InputMapper hotkeys (Space etc.) so typing is safe.
- Tempo default for new content: 110 (recorded in the Commentaries).

EXTRACTION NOTE (unchanged): 3 px click-vs-drag threshold, pixel<->
beats mapping, release=paused, click=jump — m1_demo's ear-approved
logic, verbatim.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import pygame

_DRAG_THRESHOLD_PX = 3                 # m1_demo's proven constant, verbatim
BPM_MIN, BPM_MAX = 40, 200
_GLOW = (255, 196, 64)
_HANDLE = (240, 220, 120)
_GROOVE = (50, 50, 60)
_BTN = (60, 60, 72)
_BTN_ICON = (225, 225, 225)
_TEXT = (170, 170, 180)
_BOX_BG = (28, 28, 34)
_FOCUS = (240, 220, 120)


class TransportCommand(Enum):
    PLAY_PAUSE = auto(); STOP = auto()
    JUMP = auto(); SCRUB_BEGIN = auto(); SCRUB_TO = auto(); SCRUB_END = auto()
    SET_BPM = auto()                                   # rev 3 (additive)


@dataclass(frozen=True)
class TransportEvent:
    command: TransportCommand
    beats: float = 0.0          # for JUMP / SCRUB_TO
    bpm: float = 0.0            # for SET_BPM (rev 3, additive)


def _clamp_bpm(v: int) -> int:
    return max(BPM_MIN, min(BPM_MAX, v))


class TransportWidget:
    """Frozen interface (+ additive rev-3 members)."""

    def __init__(self, rect, initial_bpm: float = 110.0) -> None:
        self.rect = pygame.Rect(rect)
        pad = 6
        btn = self.rect.h - 2 * pad
        self._play_rect = pygame.Rect(self.rect.x + pad,
                                      self.rect.y + pad, btn, btn)
        self._stop_rect = pygame.Rect(self._play_rect.right + pad,
                                      self.rect.y + pad, btn, btn)
        # --- BPM cluster, far right (opposite side from play/pause) ---
        spin_w = 16
        spin_h = (self.rect.h - 8) // 2
        self._spin_up = pygame.Rect(self.rect.right - pad - spin_w,
                                    self.rect.y + 3, spin_w, spin_h)
        self._spin_down = pygame.Rect(self._spin_up.x,
                                      self._spin_up.bottom + 2,
                                      spin_w, spin_h)
        box_w = 58
        self._bpm_box = pygame.Rect(self._spin_up.x - 4 - box_w,
                                    self.rect.y + pad, box_w, btn)
        label_w = 34
        groove_x = self._stop_rect.right + 2 * pad
        groove_end = self._bpm_box.x - label_w - 2 * pad
        self._groove = pygame.Rect(groove_x, self.rect.centery - 5,
                                   groove_end - groove_x, 10)
        self._down_pos = None
        self._dragging = False
        self._font = None
        self._bpm = _clamp_bpm(int(round(initial_bpm)))
        self._focused = False
        self._buffer = ""

    # ---- rev-3 public read-only state --------------------------------
    @property
    def typing(self) -> bool:
        """True while the BPM box is focused: wiring must mute hotkeys."""
        return self._focused

    @property
    def bpm(self) -> int:
        return self._bpm

    # ---- internals ----------------------------------------------------
    def _bar_to_beats(self, px: int, total_beats: float) -> float:
        return (px - self._groove.x) / self._groove.w * total_beats

    def _set_bpm(self, value: int) -> list[TransportEvent]:
        value = _clamp_bpm(value)
        if value != self._bpm:
            self._bpm = value
            return [TransportEvent(TransportCommand.SET_BPM,
                                   bpm=float(value))]
        return []

    def _commit(self) -> list[TransportEvent]:
        self._focused = False
        buf, self._buffer = self._buffer, ""
        if buf:
            return self._set_bpm(int(buf))
        return []                                     # empty -> revert

    def _cancel(self) -> None:
        self._focused = False
        self._buffer = ""

    # ---- the frozen surface -------------------------------------------
    def handle_event(self, pygame_event, total_beats: float) -> list[TransportEvent]:
        ev = pygame_event
        out: list[TransportEvent] = []
        if ev.type == pygame.KEYDOWN and self._focused:
            if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                out += self._commit()
            elif ev.key == pygame.K_ESCAPE:
                self._cancel()
            elif ev.key == pygame.K_BACKSPACE:
                self._buffer = self._buffer[:-1]
            elif ev.unicode.isdigit() and len(self._buffer) < 3:
                self._buffer += ev.unicode
            return out
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self._bpm_box.collidepoint(ev.pos):
                if not self._focused:
                    self._focused = True
                    self._buffer = ""
                return out
            if self._focused:                          # click-away commits
                out += self._commit()
            if self._spin_up.collidepoint(ev.pos):
                out += self._set_bpm(self._bpm + 1)
            elif self._spin_down.collidepoint(ev.pos):
                out += self._set_bpm(self._bpm - 1)
            elif self._play_rect.collidepoint(ev.pos):
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
        # play/pause + stop buttons (unchanged)
        pygame.draw.rect(surface, _BTN, self._play_rect, border_radius=4)
        pygame.draw.rect(surface, _BTN, self._stop_rect, border_radius=4)
        p = self._play_rect
        playing = (frame is not None and frame.state.name == "PLAYING")
        if playing:
            w = p.w // 5
            pygame.draw.rect(surface, _BTN_ICON,
                             (p.x + w, p.y + w, w, p.h - 2 * w))
            pygame.draw.rect(surface, _BTN_ICON,
                             (p.right - 2 * w, p.y + w, w, p.h - 2 * w))
        else:
            m = p.w // 4
            pygame.draw.polygon(surface, _BTN_ICON,
                                [(p.x + m, p.y + m),
                                 (p.x + m, p.bottom - m),
                                 (p.right - m, p.centery)])
        s = self._stop_rect
        m = s.w // 4
        pygame.draw.rect(surface, _BTN_ICON,
                         (s.x + m, s.y + m, s.w - 2 * m, s.h - 2 * m))
        # groove + handle + readout (unchanged)
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
        # --- BPM cluster (rev 3) ---
        lbl = self._font.render("bpm", True, _TEXT)
        surface.blit(lbl, (self._bpm_box.x - lbl.get_width() - 6,
                           self._bpm_box.centery - lbl.get_height() // 2))
        pygame.draw.rect(surface, _BOX_BG, self._bpm_box, border_radius=3)
        pygame.draw.rect(surface, _FOCUS if self._focused else _BTN,
                         self._bpm_box, 2 if self._focused else 1,
                         border_radius=3)
        shown = (self._buffer + "_") if self._focused else str(self._bpm)
        img = self._font.render(shown, True, _BTN_ICON)
        surface.blit(img, img.get_rect(center=self._bpm_box.center))
        for r, up in ((self._spin_up, True), (self._spin_down, False)):
            pygame.draw.rect(surface, _BTN, r, border_radius=2)
            mx, quarter = r.centerx, max(3, r.h // 4)
            if up:
                pts = [(mx, r.y + quarter), (r.x + 3, r.bottom - quarter),
                       (r.right - 3, r.bottom - quarter)]
            else:
                pts = [(mx, r.bottom - quarter), (r.x + 3, r.y + quarter),
                       (r.right - 3, r.y + quarter)]
            pygame.draw.polygon(surface, _BTN_ICON, pts)
