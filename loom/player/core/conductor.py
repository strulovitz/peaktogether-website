"""
conductor.py — THE HEART of the LOOM Player. [MEAT — frozen interface]

Scripture: New Testament par.II.1-II.4 ("playback is scrubbing at constant
speed"). One authoritative playhead (a float, in beats) owned by this one
class. Pressing Play just makes the Conductor advance its own playhead at
constant velocity; scrubbing makes the pointer drive it. Audio triggering
and every visual (graph glow, helix marker, key lights, timeline handle)
are pure functions of the ConductorFrame returned once per rendered frame
— the "sync bus" (par.II.7). One code path; perfect sync by construction.

HOW FIRING WORKS (the exact rules, so future readers never guess):

  Note i occupies the half-open beat region [start_i, end_i). Its guard is
  g_i = boundary_guard_fraction * duration_i. Its fire-lines are:
      forward:  start_i + g      (crossed moving right)
      backward: end_i   - g      (crossed moving left)
  where g = g_i while SCRUBBING, but g = 0 while PLAYING: the guard exists
  to defeat pointer jitter, and a constant-velocity playhead has none —
  playback must trigger exactly on the beat, never a guard-width late.

  Each note has an 'armed' flag. A note fires only if armed, and firing
  disarms it; it re-arms only when the playhead is outside its region.
  So: lingering inside a region never retriggers (the note rings and
  decays naturally); leaving and re-entering fires again — but never
  sooner than retrigger_min_ms since that same note's last fire (which
  protects against violent micro-wiggles; a suppressed fire is fully
  suppressed: no sound AND no visual flash).

  The flurry cap trims AUDIO only: if one frame crosses many regions,
  ConductorFrame.crossed carries them all (the eye can follow) while
  .triggers keeps just the LAST max_triggers_per_frame in traversal
  order (a fast swipe is a gesture ending where the hand stops).

  A jump (timeline click) is teleportation, not travel: no sweep, all
  notes re-arm, and only the region you land inside fires (a click into
  a rest fires nothing). Ending a scrub always leaves the Conductor
  PAUSED — never auto-resume; the wine taster decides when to sip again.

WIRING (the app loop does exactly this, nothing more):

    frame = conductor.update(dt_seconds)
    for i in frame.triggers:
        note = spell.notes[i]
        audio.trigger(note.sample, note.gain)
    # ...then hand `frame` to every renderer.

Imports: standard library ONLY (see tests/test_purity.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from .spell_model import SpellData
from .tuning import ScrubTuning


class ConductorState(Enum):
    STOPPED = auto()    # at rest (playhead may be anywhere; stop() rewinds it)
    PLAYING = auto()    # playhead advances at dt * bpm / 60 per update
    PAUSED = auto()     # playhead holds still
    SCRUBBING = auto()  # the pointer drives the playhead via scrub_to_beats


@dataclass(frozen=True)
class ConductorFrame:
    """The sync bus: everything the rest of the game may know per frame."""
    state: ConductorState
    playhead_beats: float
    playhead_seconds: float
    active_note_index: Optional[int]  # region containing the playhead, or None (a rest)
    crossed: tuple[int, ...]          # notes fired this frame, traversal order — VISUALS
    triggers: tuple[int, ...]         # = crossed capped to the last K — AUDIO
    completed: bool                   # True exactly on the update that reached the end


class Conductor:
    """Owns the one playhead of one loaded spell. Pure logic, no I/O."""

    def __init__(self, spell: SpellData, tuning: ScrubTuning) -> None:
        self._spell = spell
        self._tuning = tuning
        self._state = ConductorState.STOPPED
        self._playhead = 0.0
        self._now_s = 0.0                       # internal clock, advanced by update()
        n = len(spell.notes)
        self._armed = [True] * n
        self._last_fired_s = [float("-inf")] * n
        self._pending: list[int] = []           # fires since the last update() flush

    # ---------------- read-only conveniences ----------------

    @property
    def state(self) -> ConductorState:
        return self._state

    @property
    def playhead_beats(self) -> float:
        return self._playhead

    @property
    def spell(self) -> SpellData:
        return self._spell

    # ---------------- transport commands ----------------

    def play(self) -> None:
        """Start (or resume) playback. If the playhead already sits at the
        end, rewind to 0 first so Play always plays something."""
        if self._playhead >= self._spell.total_beats:
            self._playhead = 0.0
            self._rearm_all()
        self._state = ConductorState.PLAYING

    def pause(self) -> None:
        if self._state is not ConductorState.STOPPED:
            self._state = ConductorState.PAUSED

    def stop(self) -> None:
        """Full stop: rewind to 0. The wiring should also call
        audio.stop_all(steal_fade_ms) — the Conductor itself is silent."""
        self._state = ConductorState.STOPPED
        self._playhead = 0.0
        self._rearm_all()
        self._pending.clear()

    def jump_to_beats(self, beat: float) -> None:
        """Timeline click = teleport. No crossing sweep; every note re-arms;
        the landing region (full region, no guard — a click is deliberate)
        fires, still honoring retrigger_min_ms. State is unchanged: a click
        while PLAYING keeps playing from the new spot."""
        self._playhead = self._clamp(beat)
        self._rearm_all()
        idx = self._active_index()
        if idx is not None:
            self._try_fire(idx)

    def begin_scrub(self) -> None:
        """The pointer takes the playhead (from any state)."""
        self._state = ConductorState.SCRUBBING

    def scrub_to_beats(self, beat: float) -> None:
        """Move the playhead to the pointer's position, firing every note
        whose fire-line the movement crosses. Honored only while SCRUBBING
        (stray pointer events in other states are ignored on purpose)."""
        if self._state is ConductorState.SCRUBBING:
            self._sweep(self._clamp(beat), guarded=True)

    def end_scrub(self) -> None:
        """Releasing the handle always leaves us PAUSED where the hand
        stopped. LOCKED: never auto-resume (BIBLE par.3.2)."""
        self._state = ConductorState.PAUSED

    # ---------------- the per-frame heartbeat ----------------

    def update(self, dt_s: float) -> ConductorFrame:
        """Advance the clock (always) and the playhead (if PLAYING), then
        flush every fire since the last update into one frame. The wiring
        calls this exactly once per rendered frame."""
        self._now_s += dt_s
        completed = False
        if self._state is ConductorState.PLAYING and dt_s > 0.0:
            target = self._playhead + dt_s * self._spell.bpm / 60.0
            if target >= self._spell.total_beats:
                self._sweep(self._spell.total_beats, guarded=False)
                self._state = ConductorState.STOPPED
                completed = True
            else:
                self._sweep(target, guarded=False)

        crossed = tuple(self._pending)
        self._pending.clear()
        cap = self._tuning.max_triggers_per_frame
        triggers = crossed[-cap:] if len(crossed) > cap else crossed
        return ConductorFrame(
            state=self._state,
            playhead_beats=self._playhead,
            playhead_seconds=self._playhead * 60.0 / self._spell.bpm,
            active_note_index=self._active_index(),
            crossed=crossed,
            triggers=triggers,
            completed=completed,
        )

    # ---------------- internals ----------------

    def _clamp(self, beat: float) -> float:
        return min(max(beat, 0.0), self._spell.total_beats)

    def _guard_beats(self, duration_beats: float) -> float:
        return self._tuning.boundary_guard_fraction * duration_beats

    def _active_index(self) -> Optional[int]:
        for n in self._spell.notes:
            if n.start_beat <= self._playhead < n.end_beat:
                return n.index
        return None

    def _rearm_all(self) -> None:
        for i in range(len(self._armed)):
            self._armed[i] = True

    def _rearm_outside(self) -> None:
        """A note re-arms whenever the playhead is outside its region."""
        for n in self._spell.notes:
            if not (n.start_beat <= self._playhead < n.end_beat):
                self._armed[n.index] = True

    def _try_fire(self, i: int) -> None:
        if not self._armed[i]:
            return
        if (self._now_s - self._last_fired_s[i]) < self._tuning.retrigger_min_ms / 1000.0:
            return
        self._armed[i] = False
        self._last_fired_s[i] = self._now_s
        self._pending.append(i)

    def _sweep(self, new_beat: float, guarded: bool) -> None:
        """Move the playhead from where it is to new_beat, firing every
        armed note whose fire-line lies on the traversed span, in
        traversal order. Fire-line comparisons are inclusive on both
        ends; the armed flags make that safe (a note that just fired is
        disarmed until the playhead leaves its region)."""
        old = self._playhead
        new = new_beat
        if new > old:
            for n in self._spell.notes:  # sorted by start -> fire-lines sorted
                g = self._guard_beats(n.duration_beats) if guarded else 0.0
                if old <= n.start_beat + g <= new:
                    self._try_fire(n.index)
        elif new < old:
            for n in reversed(self._spell.notes):
                g = self._guard_beats(n.duration_beats) if guarded else 0.0
                if new <= n.end_beat - g <= old:
                    self._try_fire(n.index)
        self._playhead = new
        self._rearm_outside()
