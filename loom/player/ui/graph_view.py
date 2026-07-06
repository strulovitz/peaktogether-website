"""
graph_view.py — the function's picture, and scrub surface #2.
[M2 — Parent 3]

Scripture: BIBLE par.2 + par.10 (dumb runtime): the Player never
evaluates f(x) — it draws the POLYLINE the Compiler precomputed
(spell.raw["graph"]["points"], unit-box normalized) and scrubs via the
precompiled per-note segments (spell.raw["notes"][i]["graph_segment"],
which tile [0,1] exactly — Compiler Stage 10). All mapping below is
linear interpolation over those precompiled numbers.

Emits the SAME TransportEvents as bench_transport (one command
vocabulary, one Conductor, one feel) and shares its 3 px
click-vs-drag threshold verbatim.

Graceful degradation (binding): a spell without a graph block (the M1
fixtures) draws an honest "no graph data" panel and emits nothing —
never crashes.
"""

from __future__ import annotations

import pygame

from .bench_transport import TransportCommand, TransportEvent

_DRAG_THRESHOLD_PX = 3                 # shared with bench_transport, verbatim
_GLOW = (255, 196, 64)
_CURVE = (200, 200, 210)
_ACTIVE = (240, 220, 120)
_BG = (18, 18, 22)
_FRAME_C = (70, 70, 80)
_TEXT = (120, 120, 130)
_PAD = 14


# ---- pure mapping helpers (headless-testable) ------------------------

def segments_of(spell):
    """[(index, x_from, x_to), ...] from raw; [] if the spell has none."""
    raw_notes = spell.raw.get("notes", [])
    out = []
    for n in spell.notes:
        if n.index < len(raw_notes) and "graph_segment" in raw_notes[n.index]:
            seg = raw_notes[n.index]["graph_segment"]
            out.append((n.index, float(seg["x_from"]), float(seg["x_to"])))
    return out if len(out) == len(spell.notes) else []


def u_to_beats(spell, u: float) -> float:
    """Normalized plot x (0..1) -> playhead beats, via the segment tiling."""
    segs = segments_of(spell)
    u = min(1.0, max(0.0, u))
    for idx, x_from, x_to in segs:
        if x_from <= u <= x_to:
            note = spell.notes[idx]
            frac = 0.0 if x_to <= x_from else (u - x_from) / (x_to - x_from)
            return note.start_beat + frac * note.duration_beats
    # outside every segment (non-tiling data): clamp to nearest boundary
    if segs and u < segs[0][1]:
        return spell.notes[segs[0][0]].start_beat
    if segs:
        last = spell.notes[segs[-1][0]]
        return last.start_beat + last.duration_beats
    return 0.0


def beats_to_u(spell, beats: float) -> float:
    """Playhead beats -> normalized plot x; gaps interpolate linearly."""
    segs = segments_of(spell)
    if not segs:
        return 0.0
    first = spell.notes[segs[0][0]]
    if beats <= first.start_beat:
        return segs[0][1]
    for k, (idx, x_from, x_to) in enumerate(segs):
        note = spell.notes[idx]
        end = note.start_beat + note.duration_beats
        if note.start_beat <= beats <= end:
            frac = (0.0 if note.duration_beats <= 0
                    else (beats - note.start_beat) / note.duration_beats)
            return x_from + frac * (x_to - x_from)
        if k + 1 < len(segs):
            nxt = spell.notes[segs[k + 1][0]]
            if end < beats < nxt.start_beat:            # inside a rest
                frac = (beats - end) / (nxt.start_beat - end)
                nxt_from = segs[k + 1][1]
                return x_to + frac * (nxt_from - x_to)
    return segs[-1][2]


class GraphView:
    """Frozen interface."""

    def __init__(self, rect) -> None:
        self.rect = pygame.Rect(rect)
        self._plot = self.rect.inflate(-2 * _PAD, -2 * _PAD)
        self._down_pos = None
        self._dragging = False
        self._font = None

    def _px_to_u(self, px: int) -> float:
        return (px - self._plot.x) / self._plot.w

    def _to_screen(self, pt):
        x = self._plot.x + pt[0] * self._plot.w
        y = self._plot.bottom - pt[1] * self._plot.h
        return (x, y)

    def handle_event(self, pygame_event, spell) -> list:
        if not segments_of(spell):
            return []
        ev = pygame_event
        out: list[TransportEvent] = []
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self._plot.inflate(0, 24).collidepoint(ev.pos):
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
                    u_to_beats(spell, self._px_to_u(ev.pos[0]))))
        elif (ev.type == pygame.MOUSEBUTTONUP and ev.button == 1
              and self._down_pos is not None):
            if self._dragging:
                out.append(TransportEvent(TransportCommand.SCRUB_END))
            else:
                out.append(TransportEvent(
                    TransportCommand.JUMP,
                    u_to_beats(spell, self._px_to_u(self._down_pos[0]))))
            self._down_pos, self._dragging = None, False
        return out

    def draw(self, surface, spell, frame, flash_levels) -> None:
        pygame.draw.rect(surface, _BG, self.rect)
        pygame.draw.rect(surface, _FRAME_C, self.rect, 1)
        points = spell.raw.get("graph", {}).get("points")
        segs = segments_of(spell)
        if not points or not segs:
            if self._font is None:
                self._font = pygame.font.SysFont("consolas", 16)
            img = self._font.render("(no graph data in this spell)",
                                    True, _TEXT)
            surface.blit(img, img.get_rect(center=self.rect.center))
            return
        scr = [self._to_screen(p) for p in points]
        if len(scr) >= 2:
            pygame.draw.lines(surface, _CURVE, False, scr, 2)
        # per-note glow: active segment + crossed-flash afterglow
        for idx, x_from, x_to in segs:
            k = 0.0
            if flash_levels is not None and idx < len(flash_levels):
                k = min(1.0, max(0.0, flash_levels[idx]))
            active = (frame is not None and frame.active_note_index == idx)
            if k <= 0.0 and not active:
                continue
            sub = [self._to_screen(p) for p in points
                   if x_from - 1e-9 <= p[0] <= x_to + 1e-9]
            if len(sub) >= 2:
                col = _ACTIVE if active else (
                    int(_BG[0] + (_GLOW[0] - _BG[0]) * k),
                    int(_BG[1] + (_GLOW[1] - _BG[1]) * k),
                    int(_BG[2] + (_GLOW[2] - _BG[2]) * k))
                pygame.draw.lines(surface, col, False, sub, 4)
        # playhead cursor: thin vertical line, in agreement with the bar
        if frame is not None:
            u = beats_to_u(spell, frame.playhead_beats)
            px = self._plot.x + u * self._plot.w
            pygame.draw.line(surface, _HANDLE_COLOR,
                             (px, self.rect.y + 4),
                             (px, self.rect.bottom - 4), 1)


_HANDLE_COLOR = (240, 220, 120)
