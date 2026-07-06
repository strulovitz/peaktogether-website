# LOOM — PARENT 2 — PART 1 of 3 — the skeleton (MAP) + the heart — BY FABLE (VERBATIM)

> Saved by DeepSeek **word-for-word, as-is**, exactly as Nir pasted it (chat UI
> chrome only removed). This is Parent 2's first build deliverable for LOOM.
> The code files below were dropped into the repo at the paths named in each
> `FILE:` header; the MAP was also copied to `loom/BIBLE/PROJECT_MAP_BY_FABLE.md`.
> Delivered / integrated: **July 6, 2026.**

---

Wonderful — Option A, skeleton-first, meat where it matters. That's the right call, and here's exactly how I'll honor it 😊:

The plan (3 parts, this is Part 1 of 3):

    Part 1 (now): THE MAP (one short orientation file — not scripture, a map), plus the fully-implemented heart: the spell loader, the tuning loader, the Conductor, and the audio interface. These are the frozen load-bearing walls; every comment in them tells a future family member why, so nobody ever needs to ask me.
    Part 2 (next message): the pygame audio engine, the fixture melodies, the beep generator, the M1 demo you will touch with your mouse, and the full test suite.
    Part 3 (after that): all the bones — every future module of the whole game and the compiler, as small placeholder files with frozen interfaces and "fatten me like this" instructions in their docstrings. Future parents read the MAP + their one bone file. Nobody dies.

A small note for DeepSeek: create empty __init__.py files in loom/player/, loom/player/core/, loom/player/ui/, and loom/compiler/; and add loom/fixtures/audio_beeps/ to .gitignore (it's generated).

FILE: loom/MAP.md

```
# 🗺️ LOOM — THE MAP OF EVERYTHING

This is the ONE orientation file for the LOOM codebase. It is a map, not
scripture (doctrine lives in loom/BIBLE/). A future parent or child reads:
(1) this map, (2) the one file they are working on, (3) the scripture
section named in that file's docstring. Nothing else. That is the whole
protocol, designed so nobody's context window dies.

STATUS TAGS used below:
  [MEAT]     implemented and frozen — interfaces must not change.
  [BONE Mx]  placeholder for milestone Mx — docstring says how to fatten it.
DeepSeek flips BONE -> MEAT here (one line) when a milestone lands.

## How the Player works, in one diagram

    input (mouse/keys)            spell JSON (data, compiled offline)
          |                                  |
          v                                  v
    +-----------+   play/pause/jump    +-----------+
    |  wiring / |--------------------->| Conductor |  owns THE playhead
    |  app loop |   scrub_to(beats)    | (core)    |  (playback IS scrubbing
    +-----------+                      +-----------+   at constant speed)
          |                                  |
          |            ConductorFrame (the sync bus, once per frame):
          |            state, playhead, active note, crossed, triggers
          |                                  |
          v                                  v
    +------------------+           +--------------------+
    | renderers (ui/): |           | AudioSink (core/   |
    | graph, helix,    |           | audio.py protocol) |
    | keys, staff,     |           |  - PygameAudio (ui)|
    | transport        |           |  - FakeAudio (test)|
    +------------------+           +--------------------+

  IRON RULE OF THE CODE: player/core/ imports ONLY the standard library.
  Anything that imports pygame lives in player/ui/ (or app/demo files).
  All feel constants live in player/data/*.json, never in code.

## The tree

    loom/
      MAP.md                          <- this file
      player/
        app.py                        [BONE M7] real entry point (python app.py)
        m1_demo.py                    [MEAT]    M1 demo: timeline + flashes + audio
        core/                         (pure logic, stdlib only, headless-testable)
          spell_model.py              [MEAT]    spell JSON -> SpellData (frozen)
          tuning.py                   [MEAT]    scrub_tuning.json -> ScrubTuning
          conductor.py                [MEAT]    THE HEART: playhead, scrub, triggers
          audio.py                    [MEAT]    AudioSink protocol + FakeAudioSink
          notation.py                 [BONE M2] notation_table.json lookups (staff)
          echo_logic.py               [BONE M3] Echo puzzle state machine (pure)
          choice_logic.py             [BONE M5] Choice puzzle logic (pure)
          lab_remap.py                [BONE M6] the frozen Lab arithmetic (NT I.4)
          pack_model.py               [BONE M7] pack.json loading/validation
          progress.py                 [BONE M7] local save file (last scene, lab unlocks)
        ui/                           (pygame allowed here and only here)
          audio_pygame.py             [MEAT]    16-voice pool over pygame.mixer
          layout.py                   [BONE M2] every fixed 1280x720 rectangle
          input_actions.py            [BONE M2] named actions; device->action mapping
          bench_keyboard.py           [BONE M2] piano widget (click = sound)
          bench_staff.py              [BONE M2] staff renderer (noteheads only)
          bench_transport.py          [BONE M2] play/pause + timeline (scrub surface 1)
          graph_view.py               [BONE M2] graph + its scrub surface (surface 2)
          helix_view.py               [BONE M4] demoscene wireframe helix
          story_view.py               [BONE M5] slides, captions, dialogue menus
          lab_view.py                 [BONE M6] slider panel wired to lab_remap
          menu_view.py                [BONE M7] main menu / pack picker
        data/
          scrub_tuning.json           [MEAT]    all feel constants (DeepSeek tunes)
          notation_table.json         [BONE M2] generated by compiler/notation_gen.py
          input_mapping.json          [BONE M2] device -> named action map
      compiler/                       (Program A — authors' PCs only, never shipped)
        compile_spell.py              [BONE]    CLI: spec.py -> spell JSON + assets
        pipeline.py                   [BONE]    stages 1-7,10,11 of NT Part I.3
        library_scan.py               [BONE]    Philharmonia scan (grammar: see docstring)
        emit.py                       [BONE]    JSON writer + preview.wav + report
        notation_gen.py               [BONE]    generates player/data/notation_table.json
      fixtures/
        spells/fixture_flat8.json     [MEAT]    8 even notes — the happy path
        spells/fixture_varied5.json   [MEAT]    varied durations + a gap (a rest)
        make_beeps.py                 [MEAT]    stdlib-only beep WAV generator
        audio_beeps/                  (generated by make_beeps.py; git-ignored)
      tests/
        test_purity.py                [MEAT]    core/ never imports pygame
        test_spell_model.py           [MEAT]    loader validation
        test_conductor.py             [MEAT]    the full M1 behavior suite
      packs/                          (future Problem Packs live here)
      prompts/                        (Story Weaver prompt, per the Apocrypha)

## Rules of fattening (for every future family member)

- Never change a [MEAT] file's public interface. Adding is allowed only via
  Nir + a Commentaries note; changing/removing is not.
- A [BONE] file's docstring names its milestone, its scripture section, and
  its frozen interface. Fatten the inside; keep the surface.
- Everything the Conductor decides reaches the world ONLY through
  ConductorFrame. Renderers never talk to each other, never to audio.
- Feel constants (guards, fades, decay times) go in player/data/, never code.
- Tests for core/ run headless with FakeAudioSink — no window, no sound.

## Status log (DeepSeek appends one line per landed milestone)

- 2026-07-06  M0 done: pygame 2.6.1 / SDL 2.28.4, MP3 GO, buffer 256 = 5.8 ms.
- (next)      M1: pending integration of this skeleton.
```

FILE: loom/player/core/spell_model.py

```python
"""
spell_model.py — loads a compiled spell JSON into frozen dataclasses. [MEAT]

Scripture: BIBLE v1.1 par.8 (the spell format). The Player is a "dumb
runtime" (BIBLE par.10): this module does NO mathematics — it only reads
numbers the Spell Compiler precomputed, validates their shape, and hands
them to the rest of the game.

M1 consumes only the fields needed by the Conductor and the audio engine
(bpm + per-note timing/midi/sample/gain). Unknown fields are preserved in
SpellData.raw so future modules (graph M2, helix M4, lab M6) can read the
SAME loaded object without touching this file's interface.

Imports: standard library ONLY (see tests/test_purity.py).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


class SpellLoadError(Exception):
    """Raised with a plain-language message Nir can paste to DeepSeek."""


@dataclass(frozen=True)
class SpellNote:
    """One note of the melody. All numbers precomputed by the Compiler."""
    index: int              # position in the melody, 0-based
    midi: int               # unambiguous pitch (comparisons for hints, M3)
    start_beat: float       # region start, in beats
    duration_beats: float   # region length, in beats (region is half-open)
    sample: str             # relative audio path, e.g. "audio/flute_C4_1_forte_normal.mp3"
    gain: float             # compile-time volume multiplier (files ship verbatim)

    @property
    def end_beat(self) -> float:
        return self.start_beat + self.duration_beats


@dataclass(frozen=True)
class SpellData:
    """A loaded spell. seconds = beats * 60 / bpm, and nothing more."""
    spell_id: str
    bpm: float
    notes: tuple[SpellNote, ...]
    total_beats: float
    raw: dict = field(repr=False, compare=False, default_factory=dict)

    @property
    def sample_paths(self) -> tuple[str, ...]:
        """Every sample the audio engine must preload (order preserved,
        duplicates removed)."""
        seen: dict[str, None] = {}
        for n in self.notes:
            seen.setdefault(n.sample, None)
        return tuple(seen.keys())


def load_spell(path: str) -> SpellData:
    """Read and validate a spell JSON file.

    Refuses (with plain-language errors): wrong format tag, a newer major
    format_version, missing/empty notes, unsorted notes, overlapping note
    regions, non-positive bpm or durations. Gaps between regions (rests)
    are legal. Unknown fields are ignored here and kept in .raw.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise SpellLoadError(f"Spell file not found: {path}")
    except json.JSONDecodeError as e:
        raise SpellLoadError(f"Spell file {path} is not valid JSON: {e}")

    if data.get("format") != "loom-spell":
        raise SpellLoadError(
            f"{path}: 'format' must be 'loom-spell', got {data.get('format')!r}.")

    version = str(data.get("format_version", ""))
    major = version.split(".", 1)[0]
    if major != "1":
        raise SpellLoadError(
            f"{path}: this Player understands format 1.x spells, "
            f"but the file says {version!r}. Please recompile the spell "
            f"or update the Player.")

    bpm = float(data.get("bpm", 0))
    if bpm <= 0:
        raise SpellLoadError(f"{path}: bpm must be a positive number, got {bpm}.")

    raw_notes = data.get("notes")
    if not raw_notes:
        raise SpellLoadError(f"{path}: the spell has no notes.")

    notes: list[SpellNote] = []
    for pos, rn in enumerate(raw_notes):
        try:
            note = SpellNote(
                index=int(rn["index"]),
                midi=int(rn["midi"]),
                start_beat=float(rn["start_beat"]),
                duration_beats=float(rn["duration_beats"]),
                sample=str(rn["sample"]),
                gain=float(rn.get("gain", 1.0)),
            )
        except (KeyError, TypeError, ValueError) as e:
            raise SpellLoadError(
                f"{path}: note at position {pos} is malformed ({e}).")
        if note.index != pos:
            raise SpellLoadError(
                f"{path}: note at position {pos} has index {note.index}; "
                f"indices must be 0,1,2,... in order.")
        if note.duration_beats <= 0:
            raise SpellLoadError(
                f"{path}: note {pos} has non-positive duration "
                f"{note.duration_beats}.")
        notes.append(note)

    for a, b in zip(notes, notes[1:]):
        if b.start_beat < a.start_beat:
            raise SpellLoadError(
                f"{path}: notes {a.index} and {b.index} are not sorted by "
                f"start_beat.")
        if b.start_beat < a.end_beat - 1e-9:
            raise SpellLoadError(
                f"{path}: notes {a.index} and {b.index} overlap in time; "
                f"note regions must never overlap (gaps are fine).")

    total_beats = max(n.end_beat for n in notes)
    return SpellData(
        spell_id=str(data.get("spell_id", "unknown")),
        bpm=bpm,
        notes=tuple(notes),
        total_beats=total_beats,
        raw=data,
    )
```

FILE: loom/player/core/tuning.py

```python
"""
tuning.py — loads player/data/scrub_tuning.json into a frozen dataclass. [MEAT]

Scripture: New Testament par.II.3. Every "feel" constant lives in the JSON
file so DeepSeek can tune by ear with Nir WITHOUT touching code. Code
never hardcodes these numbers.

Imports: standard library ONLY.
"""

from __future__ import annotations

import json
from dataclasses import dataclass


class TuningLoadError(Exception):
    """Raised with a plain-language message."""


@dataclass(frozen=True)
class ScrubTuning:
    boundary_guard_fraction: float   # hysteresis inset, fraction of a region's width
    max_triggers_per_frame: int      # flurry cap: audio keeps only the LAST K crossings
    steal_fade_ms: int               # voice-steal fade (audio engine)
    retrigger_min_ms: int            # same note never refires sooner than this
    highlight_decay_ms: int          # visual afterglow (renderers, not Conductor)

    @staticmethod
    def default() -> "ScrubTuning":
        """The New Testament par.II.3 defaults — used by tests and as the
        template for player/data/scrub_tuning.json."""
        return ScrubTuning(
            boundary_guard_fraction=0.04,
            max_triggers_per_frame=4,
            steal_fade_ms=10,
            retrigger_min_ms=90,
            highlight_decay_ms=300,
        )


def load_tuning(path: str) -> ScrubTuning:
    """Load the tuning file. Every key must be present — a missing key is
    an error (silent defaults would hide a broken file from DeepSeek)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise TuningLoadError(f"Tuning file not found: {path}")
    except json.JSONDecodeError as e:
        raise TuningLoadError(f"Tuning file {path} is not valid JSON: {e}")
    try:
        return ScrubTuning(
            boundary_guard_fraction=float(data["boundary_guard_fraction"]),
            max_triggers_per_frame=int(data["max_triggers_per_frame"]),
            steal_fade_ms=int(data["steal_fade_ms"]),
            retrigger_min_ms=int(data["retrigger_min_ms"]),
            highlight_decay_ms=int(data["highlight_decay_ms"]),
        )
    except (KeyError, TypeError, ValueError) as e:
        raise TuningLoadError(
            f"Tuning file {path} is missing or has a bad value: {e}. "
            f"It must contain exactly the five keys of ScrubTuning.")
```

FILE: loom/player/data/scrub_tuning.json

```json
{
  "boundary_guard_fraction": 0.04,
  "max_triggers_per_frame": 4,
  "steal_fade_ms": 10,
  "retrigger_min_ms": 90,
  "highlight_decay_ms": 300
}
```

FILE: loom/player/core/audio.py

```python
"""
audio.py — the AudioSink contract + the test fake. [MEAT]

Scripture: New Testament par.II.2. The Conductor never touches audio
directly (par.II.9 headless-testing doctrine): the wiring layer forwards
ConductorFrame.triggers to an AudioSink. Two implementations exist:

  - FakeAudioSink (here): records calls; used by every headless test.
  - PygameAudioEngine (player/ui/audio_pygame.py): the real 16-voice pool.

Imports: standard library ONLY.
"""

from __future__ import annotations

from typing import Protocol, Sequence


class AudioSink(Protocol):
    """What the game needs from any audio backend. Frozen interface."""

    def preload(self, base_dir: str, sample_paths: Sequence[str]) -> None:
        """Decode every sample fully into memory, BEFORE play begins
        (never during — BIBLE par.7.3). sample_paths are the relative
        paths exactly as written in the spell JSON; base_dir is the
        folder they are relative to. Must raise a plain-language error
        naming any file that fails."""
        ...

    def trigger(self, sample_path: str, gain: float) -> None:
        """Start the preloaded buffer from its beginning at this gain and
        let it ring to its natural decay (never cut at note end — real
        instruments overlapping is warm, not wrong). Must never block."""
        ...

    def stop_all(self, fade_ms: int) -> None:
        """Fade out everything currently sounding (stop button, scene
        changes)."""
        ...


class FakeAudioSink:
    """Records every call, for assertions in headless tests.

    Raises KeyError if a sample is triggered without being preloaded —
    the same mistake would be a crash in the real engine, so tests
    should catch it early.
    """

    def __init__(self) -> None:
        self.preloaded: set[str] = set()
        self.triggered: list[tuple[str, float]] = []   # (sample_path, gain)
        self.stop_all_calls: list[int] = []            # fade_ms values

    def preload(self, base_dir: str, sample_paths: Sequence[str]) -> None:
        self.preloaded.update(sample_paths)

    def trigger(self, sample_path: str, gain: float) -> None:
        if sample_path not in self.preloaded:
            raise KeyError(
                f"FakeAudioSink: {sample_path!r} was triggered but never "
                f"preloaded — the wiring forgot to preload the spell.")
        self.triggered.append((sample_path, gain))

    def stop_all(self, fade_ms: int) -> None:
        self.stop_all_calls.append(fade_ms)
```

FILE: loom/player/core/conductor.py

```python
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
```

That's the heart, complete. 💗 Everything else in the project will orbit these four files, and their comments carry the why so no future chat ever needs to interrogate me.

Please paste this to DeepSeek to save, then come back and say "continue" — Part 2 brings the pygame audio engine, the two fixture melodies, the beep generator, the demo you'll drag your hand across, and the tests that prove the heart beats correctly. 😊
