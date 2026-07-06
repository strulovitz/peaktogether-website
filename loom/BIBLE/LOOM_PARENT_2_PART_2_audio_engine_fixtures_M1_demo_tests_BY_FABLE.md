# LOOM — PARENT 2 — PART 2 of 3 — audio engine + fixtures + M1 demo + tests — BY FABLE (VERBATIM)

> Saved by DeepSeek **word-for-word, as-is** (chat UI chrome only removed).
> Parent 2's second build deliverable: the real pygame audio engine, the two
> real-instrument fixture melodies (violin + oboe), the emergency beep generator,
> the M1 demo you drag your hand across, and the full headless test suite.
> All files dropped in at the paths named in each `FILE:` header.
> Delivered / integrated: **July 6, 2026.** DeepSeek verification on Nir's PC:
> `python -m pytest loom/tests` → **28 passed**; the real-library resolver found a
> real recording for every note of BOTH fixtures (violin + oboe). Awaiting Nir's
> ear session (the 9-step acceptance script) to formally "land" M1.

---

Part 2 — the heart gets hands, a voice, and a proof. 🎻 As promised: real violin under your mouse from the very first drag. Six files.

FILE: loom/player/ui/audio_pygame.py

```python
"""
audio_pygame.py — the real audio engine: a 16-voice pool over pygame.mixer. [MEAT]

Scripture: New Testament par.II.2. M0 (2026-07-06) proved this path on
Nir's PC: pygame 2.6.1 / SDL 2.28.4 loads real Philharmonia MP3s into
preloaded buffers, buffer 256 = 5.8 ms output latency (budget: <= 30 ms).

THE ONE RULE OF THIS MODULE: it plays recorded files it was handed —
nothing else. There is no synthesis of any kind here. A note becomes a
real file in exactly one place in the whole project (the Compiler's
library scan, compiler/library_scan.py); this engine just obeys.

This file is in ui/ because it imports pygame. Core logic never does.

DeepSeek items (behavior is the contract; exact pygame calls may be
adjusted freely if the real machine disagrees):
  - voice stealing below reuses the oldest channel directly; if Nir ever
    hears a click on very fast scrub flurries, refine with a short
    fadeout + reserve-channel scheme (steal_fade_ms is already in the
    tuning file, waiting).
"""

from __future__ import annotations

import os
import time
from typing import Sequence

import pygame


AUDIO_FREQ_HZ = 44100     # confirmed by M0
AUDIO_SIZE = -16          # 16-bit signed
AUDIO_CHANNELS = 2        # stereo
AUDIO_BUFFER = 256        # M0: 5.8 ms; pre-approved fallback: 512
NUM_VOICES = 16           # New Testament par.II.2


def init_mixer() -> None:
    """Call BEFORE pygame.init() (or any display init) for the small
    buffer to take effect. Safe to call once at app start."""
    pygame.mixer.pre_init(AUDIO_FREQ_HZ, AUDIO_SIZE, AUDIO_CHANNELS, AUDIO_BUFFER)


class AudioLoadError(Exception):
    """Plain-language error naming the file that failed."""


class PygameAudioEngine:
    """Implements the AudioSink protocol (player/core/audio.py).

    preload() decodes every sample fully into memory; trigger() starts a
    preloaded buffer on a free voice (stealing the oldest if all 16 are
    busy) and lets it ring to natural decay. Never blocks, never decodes
    during play.
    """

    def __init__(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init(AUDIO_FREQ_HZ, AUDIO_SIZE, AUDIO_CHANNELS, AUDIO_BUFFER)
        pygame.mixer.set_num_channels(NUM_VOICES)
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._channels = [pygame.mixer.Channel(i) for i in range(NUM_VOICES)]
        self._started_at = [0.0] * NUM_VOICES   # for oldest-voice stealing

    # ---- AudioSink protocol ----

    def preload(self, base_dir: str, sample_paths: Sequence[str]) -> None:
        for rel in sample_paths:
            full = os.path.join(base_dir, rel) if base_dir else rel
            if not os.path.isfile(full):
                raise AudioLoadError(
                    f"Audio file not found: {full}\n"
                    f"(sample reference: {rel!r})")
            try:
                self._sounds[rel] = pygame.mixer.Sound(full)
            except Exception as e:
                raise AudioLoadError(
                    f"Could not decode audio file: {full}\n({e})")

    def trigger(self, sample_path: str, gain: float) -> None:
        sound = self._sounds.get(sample_path)
        if sound is None:
            raise AudioLoadError(
                f"trigger() called for a sample that was never preloaded: "
                f"{sample_path!r}")
        voice = self._find_voice()
        ch = self._channels[voice]
        ch.play(sound)                    # reusing a busy channel = stealing it
        ch.set_volume(max(0.0, min(1.0, gain)))
        self._started_at[voice] = time.monotonic()

    def stop_all(self, fade_ms: int) -> None:
        pygame.mixer.fadeout(max(0, int(fade_ms)))

    # ---- internals ----

    def _find_voice(self) -> int:
        for i, ch in enumerate(self._channels):
            if not ch.get_busy():
                return i
        # all busy: steal the OLDEST (New Testament par.II.2)
        return min(range(NUM_VOICES), key=lambda i: self._started_at[i])
```

FILE: loom/fixtures/spells/fixture_flat8.json

```json
{
  "format": "loom-spell",
  "format_version": "1.0",
  "spell_id": "fixture_flat8",
  "display_name": "Fixture: Eight Even Steps (violin)",
  "function_text": "hand-written M1 fixture - pentatonic ascent, flat rhythm",
  "instrument": "violin",
  "articulation": "arco-normal",
  "bpm": 90,
  "notes": [
    { "index": 0, "note_name": "C4", "midi": 60, "start_beat": 0.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "violin_C4_1_forte_arco-normal.mp3", "gain": 0.9 },
    { "index": 1, "note_name": "D4", "midi": 62, "start_beat": 1.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "violin_D4_1_forte_arco-normal.mp3", "gain": 0.9 },
    { "index": 2, "note_name": "E4", "midi": 64, "start_beat": 2.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "violin_E4_1_forte_arco-normal.mp3", "gain": 0.9 },
    { "index": 3, "note_name": "G4", "midi": 67, "start_beat": 3.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "violin_G4_1_forte_arco-normal.mp3", "gain": 0.9 },
    { "index": 4, "note_name": "A4", "midi": 69, "start_beat": 4.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "violin_A4_1_forte_arco-normal.mp3", "gain": 0.9 },
    { "index": 5, "note_name": "C5", "midi": 72, "start_beat": 5.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "violin_C5_1_forte_arco-normal.mp3", "gain": 0.9 },
    { "index": 6, "note_name": "D5", "midi": 74, "start_beat": 6.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "violin_D5_1_forte_arco-normal.mp3", "gain": 0.9 },
    { "index": 7, "note_name": "E5", "midi": 76, "start_beat": 7.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "violin_E5_1_forte_arco-normal.mp3", "gain": 0.9 }
  ],
  "notes_for_humans": "M1 fixture. The sample names are canonical guesses; the demo resolves each note against the REAL library on disk (any recorded length, preferring longer) and refuses to run if a real file cannot be found."
}
```

FILE: loom/fixtures/spells/fixture_varied5.json

```json
{
  "format": "loom-spell",
  "format_version": "1.0",
  "spell_id": "fixture_varied5",
  "display_name": "Fixture: Varied Durations and a Rest (oboe)",
  "function_text": "hand-written M1 fixture - unequal regions + a gap at beats [2.0, 2.5)",
  "instrument": "oboe",
  "articulation": "normal",
  "bpm": 90,
  "notes": [
    { "index": 0, "note_name": "C4", "midi": 60, "start_beat": 0.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "oboe_C4_1_forte_normal.mp3",  "gain": 0.9 },
    { "index": 1, "note_name": "E4", "midi": 64, "start_beat": 1.0, "duration_beats": 0.5, "dynamic": "forte", "sample": "oboe_E4_05_forte_normal.mp3", "gain": 0.9 },
    { "index": 2, "note_name": "G4", "midi": 67, "start_beat": 1.5, "duration_beats": 0.5, "dynamic": "forte", "sample": "oboe_G4_05_forte_normal.mp3", "gain": 0.9 },
    { "index": 3, "note_name": "C5", "midi": 72, "start_beat": 2.5, "duration_beats": 1.0, "dynamic": "forte", "sample": "oboe_C5_1_forte_normal.mp3",  "gain": 0.9 },
    { "index": 4, "note_name": "C4", "midi": 60, "start_beat": 3.5, "duration_beats": 2.0, "dynamic": "forte", "sample": "oboe_C4_2_forte_normal.mp3",  "gain": 0.9 }
  ],
  "notes_for_humans": "M1 fixture. Tests unequal guards, the rest (scrubbing through it is silent), and a long final note."
}
```

FILE: loom/fixtures/make_beeps.py

```python
"""
make_beeps.py — EMERGENCY SCAFFOLDING ONLY. [MEAT, but deliberately unloved]

ON THE RECORD (Nir's requirement, 2026-07-06): the game plays REAL
Philharmonia recordings, never beeps. This script exists for exactly one
situation: a machine that does NOT have the Philharmonia library (e.g.
some future automated test runner) and still needs to run the demo. On
Nir's PC it is never needed; the demo defaults to the real library and
refuses to fall back silently (beeps require an explicit --beeps flag).
The headless tests don't need audio files at all (FakeAudioSink).

Stdlib only. Writes loom/fixtures/audio_beeps/beep_<midi>.wav:
1.5 s mono 16-bit 44100 Hz sine at the MIDI pitch, 5 ms attack,
exponential decay (tau 0.4 s) so scrub-lingering is audible.
"""

import math
import os
import wave

MIDIS = [60, 62, 64, 67, 69, 72, 74, 76]  # union of both fixtures' pitches
RATE = 44100
SECONDS = 1.5
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_beeps")


def midi_to_freq(m: int) -> float:
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def render(midi: int) -> bytes:
    freq = midi_to_freq(midi)
    n = int(RATE * SECONDS)
    attack = int(RATE * 0.005)
    out = bytearray()
    for i in range(n):
        t = i / RATE
        amp = 0.5 * math.exp(-t / 0.4)
        if i < attack:
            amp *= i / attack
        s = int(32767 * amp * math.sin(2 * math.pi * freq * t))
        out += s.to_bytes(2, "little", signed=True)
    return bytes(out)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    for m in MIDIS:
        path = os.path.join(OUT_DIR, f"beep_{m}.wav")
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(render(m))
        print(f"wrote {path}")
    print("Done. Reminder: these are emergency test tones, NOT game audio.")


if __name__ == "__main__":
    main()
```

FILE: loom/player/m1_demo.py

```python
"""
m1_demo.py — Milestone 1: touch the melody. [MEAT — demo scaffolding]

Run (from anywhere):
    python m1_demo.py                       <- violin fixture, real library
    python m1_demo.py --spell fixtures/spells/fixture_varied5.json
    python m1_demo.py --library "D:/somewhere/philharmonia"
    python m1_demo.py --beeps               <- EXPLICIT fallback only

REAL INSTRUMENTS FIRST (on the record, 2026-07-06): this demo resolves
every note against Nir's real Philharmonia library (default location
C:/Users/nir_s/Downloads/philharmonia) and REFUSES to run if a note has
no real recording — it never falls back to beeps silently. The little
resolver below is throwaway scaffolding standing in for the Compiler's
library_scan (which will do this properly, offline, writing the chosen
filename into the spell JSON). When the Compiler exists (a later
milestone), spells arrive with concrete files and this resolver retires.

Controls:
    SPACE       play / pause          HOME    stop (rewind + fade out)
    click bar   jump to that spot     drag bar  scrub (release = pause)
    LEFT/RIGHT  nudge to prev/next note
    ESC         quit

Nir's acceptance script lives at the bottom of this docstring, printed
on startup:
  1. Space: eight even rising violin notes, stopping by itself.
  2. Drag slowly forward: each note rings as your hand crosses it.
  3. Hold still mid-note: after the natural decay, silence. No repeats.
  4. Tiny wiggle at a boundary: must NOT machine-gun.
  5. Fast sweep start-to-end: a quick clean flurry, not mud.
  6. Drag backward: the melody in reverse.
  7. Click the middle of the bar: just the landing note sounds.
  8. Release mid-drag: it stays paused where you left it.
  9. The only question that matters: does it feel like touching the melody?
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOOM_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)  # so `core` and `ui` import when run as a script

from core.spell_model import SpellData, load_spell          # noqa: E402
from core.tuning import load_tuning                          # noqa: E402
from core.conductor import Conductor, ConductorState         # noqa: E402

DEFAULT_SPELL = os.path.join(LOOM_DIR, "fixtures", "spells", "fixture_flat8.json")
DEFAULT_LIBRARY = r"C:\Users\nir_s\Downloads\philharmonia"
TUNING_PATH = os.path.join(HERE, "data", "scrub_tuning.json")
BEEP_DIR = os.path.join(LOOM_DIR, "fixtures", "audio_beeps")

NOTE_NAMES = ["C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs", "A", "As", "B"]
LENGTH_RANK = {"2": 5, "15": 4, "1": 3, "05": 2, "025": 1}  # prefer longer ring
DYNAMIC_PREFERENCE = ["forte", "mezzo-forte", "fortissimo", "mezzo-piano", "piano"]


def note_name(midi: int) -> str:
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"       # MIDI 60 -> C4


def resolve_real_samples(spell: SpellData, library_dir: str) -> dict[int, str]:
    """For each note, find a REAL file in <library>/<instrument>/ matching
    <instrument>_<note>_<length>_<dynamic>_<articulation>.mp3 (grammar
    confirmed on Nir's files, Commentaries par.7), preferring longer
    recorded lengths. Returns {note.index: absolute path}. Halts with a
    plain-language error if any note has no real recording."""
    instrument = spell.raw.get("instrument")
    articulation = spell.raw.get("articulation", "normal")
    folder = os.path.join(library_dir, instrument)
    if not os.path.isdir(folder):
        raise SystemExit(
            f"ERROR: instrument folder not found: {folder}\n"
            f"Expected the Philharmonia library at: {library_dir}\n"
            f"(pass --library <path> if it lives elsewhere)")
    files = os.listdir(folder)
    resolved: dict[int, str] = {}
    for n in spell.notes:
        name = note_name(n.midi)
        pick = None
        for dyn in DYNAMIC_PREFERENCE:
            cands = [f for f in files
                     if f.startswith(f"{instrument}_{name}_")
                     and f.endswith(f"_{dyn}_{articulation}.mp3")]
            if cands:
                def rank(f: str) -> int:
                    parts = f.split("_")
                    return LENGTH_RANK.get(parts[2], 0) if len(parts) >= 3 else 0
                pick = max(cands, key=rank)
                break
        if pick is None:
            near = sorted(f for f in files if f"_{name}_" in f)[:5]
            raise SystemExit(
                f"ERROR: no real recording found for {instrument} {name} "
                f"(articulation {articulation!r}) in {folder}\n"
                f"Searched pattern: {instrument}_{name}_<length>_<dynamic>_{articulation}.mp3\n"
                f"Nearby files: {near or '(none with this note name)'}\n"
                f"This demo does NOT fall back to beeps. "
                f"Paste this message to DeepSeek.")
        resolved[n.index] = os.path.join(folder, pick)
        print(f"  note {n.index}: {name} -> {pick}")
    return resolved


def resolve_beeps(spell: SpellData) -> dict[int, str]:
    """EXPLICIT --beeps fallback for machines without the library."""
    resolved = {}
    for n in spell.notes:
        p = os.path.join(BEEP_DIR, f"beep_{n.midi}.wav")
        if not os.path.isfile(p):
            raise SystemExit(
                f"ERROR: {p} missing. Run: python loom/fixtures/make_beeps.py")
        resolved[n.index] = p
    return resolved


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spell", default=DEFAULT_SPELL)
    ap.add_argument("--library", default=DEFAULT_LIBRARY)
    ap.add_argument("--beeps", action="store_true",
                    help="EXPLICIT test-tone fallback (never the default)")
    args = ap.parse_args()

    spell = load_spell(args.spell)
    tuning = load_tuning(TUNING_PATH)
    print(f"Loaded spell {spell.spell_id!r}: {len(spell.notes)} notes, "
          f"{spell.bpm} BPM, {spell.total_beats} beats.")
    if args.beeps:
        print("NOTE: --beeps requested: test tones, NOT game audio.")
        resolved = resolve_beeps(spell)
    else:
        print(f"Resolving REAL instruments from {args.library} ...")
        resolved = resolve_real_samples(spell, args.library)

    # ---- pygame world starts here ----
    from ui.audio_pygame import PygameAudioEngine, init_mixer
    import pygame

    init_mixer()
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption(f"LOOM M1 - {spell.spell_id}")
    font = pygame.font.SysFont("consolas", 18)
    big = pygame.font.SysFont("consolas", 26)
    clock = pygame.time.Clock()

    audio = PygameAudioEngine()
    audio.preload("", list(resolved.values()))
    conductor = Conductor(spell, tuning)

    # layout (demo-only; the real game's rectangles come in M2's layout.py)
    BAR = pygame.Rect(80, 620, 1120, 26)
    NOTES_Y, NOTES_H = 260, 180
    note_rects = []
    for n in spell.notes:  # widths proportional to duration; gaps stay empty
        x0 = BAR.x + BAR.w * n.start_beat / spell.total_beats
        x1 = BAR.x + BAR.w * n.end_beat / spell.total_beats
        note_rects.append(pygame.Rect(int(x0) + 2, NOTES_Y, int(x1 - x0) - 4, NOTES_H))
    flash = [0.0] * len(spell.notes)  # ms remaining of highlight

    def bar_to_beats(px: int) -> float:
        return (px - BAR.x) / BAR.w * spell.total_beats

    dragging = False
    down_pos = None
    print(__doc__.split("printed\non startup:")[-1])

    running = True
    while running:
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    if conductor.state is ConductorState.PLAYING:
                        conductor.pause()
                    else:
                        conductor.play()
                elif ev.key == pygame.K_HOME:
                    conductor.stop()
                    audio.stop_all(tuning.steal_fade_ms)
                elif ev.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    ph = conductor.playhead_beats
                    if ev.key == pygame.K_RIGHT:
                        nxt = [n.start_beat for n in spell.notes if n.start_beat > ph + 1e-9]
                        if nxt:
                            conductor.jump_to_beats(nxt[0])
                    else:
                        prv = [n.start_beat for n in spell.notes if n.start_beat < ph - 1e-9]
                        if prv:
                            conductor.jump_to_beats(prv[-1])
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if BAR.inflate(0, 24).collidepoint(ev.pos):
                    down_pos = ev.pos
                    dragging = False
            elif ev.type == pygame.MOUSEMOTION and down_pos is not None:
                if not dragging and abs(ev.pos[0] - down_pos[0]) > 3:
                    dragging = True
                    conductor.begin_scrub()
                if dragging:
                    conductor.scrub_to_beats(bar_to_beats(ev.pos[0]))
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and down_pos is not None:
                if dragging:
                    conductor.end_scrub()      # LOCKED: release = paused
                else:
                    conductor.jump_to_beats(bar_to_beats(ev.pos[0]))
                down_pos, dragging = None, False

        # ---- the wiring loop (exactly as conductor.py's docstring) ----
        frame = conductor.update(dt)
        for i in frame.triggers:
            n = spell.notes[i]
            audio.trigger(resolved[i], n.gain)
        for i in frame.crossed:
            flash[i] = tuning.highlight_decay_ms
        for i in range(len(flash)):
            flash[i] = max(0.0, flash[i] - dt_ms)
        if frame.completed:
            print("(spell completed)")

        # ---- draw ----
        screen.fill((12, 12, 16))
        for n in spell.notes:
            r = note_rects[n.index]
            base = 60 + int(120 * (n.midi - 60) / 24)         # taller pitch = brighter
            col = (base // 2, base // 2, base // 2)
            if flash[n.index] > 0:                            # warm afterglow
                k = flash[n.index] / tuning.highlight_decay_ms
                col = (int(80 + 175 * k), int(60 + 140 * k), 40)
            if frame.active_note_index == n.index:
                pygame.draw.rect(screen, (240, 220, 120), r.inflate(8, 8), 2)
            pygame.draw.rect(screen, col, r)
            screen.blit(font.render(note_name(n.midi), True, (230, 230, 230)),
                        (r.x + 4, r.y + r.h + 6))
        pygame.draw.rect(screen, (50, 50, 60), BAR)
        px = BAR.x + BAR.w * frame.playhead_beats / spell.total_beats
        pygame.draw.rect(screen, (240, 220, 120), (int(px) - 2, BAR.y - 8, 4, BAR.h + 16))
        screen.blit(big.render(
            f"{spell.spell_id}   {frame.state.name}   "
            f"beat {frame.playhead_beats:5.2f}   {frame.playhead_seconds:5.2f}s",
            True, (220, 220, 220)), (80, 60))
        screen.blit(font.render(
            "SPACE play/pause   HOME stop   click bar = jump   drag bar = scrub   "
            "LEFT/RIGHT nudge   ESC quit", True, (150, 150, 160)), (80, 100))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```

FILE: loom/tests/conftest.py

```python
"""Puts loom/player on sys.path so tests import `core.*` headlessly."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "player"))
```

FILE: loom/tests/test_purity.py

```python
"""core/ must never import pygame (New Testament par.II.9)."""
import sys


def test_core_is_pygame_free():
    import core.spell_model    # noqa: F401
    import core.tuning         # noqa: F401
    import core.conductor      # noqa: F401
    import core.audio          # noqa: F401
    assert "pygame" not in sys.modules
```

FILE: loom/tests/test_spell_model.py

```python
import json

import pytest

from core.spell_model import SpellLoadError, load_spell


def write(tmp_path, data):
    p = tmp_path / "s.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def base(**over):
    d = {"format": "loom-spell", "format_version": "1.0",
         "spell_id": "t", "bpm": 90,
         "notes": [
             {"index": 0, "midi": 60, "start_beat": 0.0, "duration_beats": 1.0,
              "sample": "a.mp3", "gain": 0.9},
             {"index": 1, "midi": 62, "start_beat": 1.0, "duration_beats": 1.0,
              "sample": "b.mp3", "gain": 0.9}]}
    d.update(over)
    return d


def test_loads_and_computes(tmp_path):
    s = load_spell(write(tmp_path, base()))
    assert s.total_beats == 2.0 and len(s.notes) == 2
    assert s.sample_paths == ("a.mp3", "b.mp3")
    assert s.notes[1].end_beat == 2.0


def test_dedupes_samples(tmp_path):
    d = base()
    d["notes"][1]["sample"] = "a.mp3"
    assert load_spell(write(tmp_path, d)).sample_paths == ("a.mp3",)


@pytest.mark.parametrize("mutate", [
    lambda d: d.update(format="something-else"),
    lambda d: d.update(format_version="2.0"),
    lambda d: d.update(bpm=0),
    lambda d: d.update(notes=[]),
    lambda d: d["notes"][1].update(start_beat=0.5),          # overlap
    lambda d: d["notes"][0].update(start_beat=5.0),          # unsorted
    lambda d: d["notes"][1].update(index=7),                 # bad index
    lambda d: d["notes"][0].update(duration_beats=0),
])
def test_rejects_bad_files(tmp_path, mutate):
    d = base()
    mutate(d)
    with pytest.raises(SpellLoadError):
        load_spell(write(tmp_path, d))
```

FILE: loom/tests/test_conductor.py

```python
"""The full M1 behavior suite — headless, deterministic, no audio files."""
from core.audio import FakeAudioSink
from core.conductor import Conductor, ConductorState
from core.spell_model import SpellData, SpellNote
from core.tuning import ScrubTuning

T = ScrubTuning.default()   # guard 0.04, cap 4, retrigger 90 ms


def make_spell(spec=None, bpm=90.0):
    """spec: list of (start, duration); default = 8 flat notes."""
    spec = spec or [(float(i), 1.0) for i in range(8)]
    notes = tuple(SpellNote(i, 60 + i, s, d, f"s{i}.mp3", 0.9)
                  for i, (s, d) in enumerate(spec))
    return SpellData("test", bpm, notes, max(n.end_beat for n in notes), {})


GAPPY = [(0.0, 1.0), (1.0, 0.5), (1.5, 0.5), (2.5, 1.0), (3.5, 2.0)]  # rest [2, 2.5)


def collect(c, updates):
    """Run updates (list of dt seconds), return (frames, all crossed)."""
    frames = [c.update(dt) for dt in updates]
    crossed = [i for f in frames for i in f.crossed]
    return frames, crossed


def test_playing_advances_at_bpm():
    c = Conductor(make_spell(bpm=120), T)
    c.play()
    f = c.update(0.5)                       # 0.5 s at 120 bpm = 1 beat
    assert abs(f.playhead_beats - 1.0) < 1e-9
    assert f.state is ConductorState.PLAYING


def test_paused_and_stopped_hold_still():
    c = Conductor(make_spell(), T)
    for _ in range(3):
        assert c.update(0.1).playhead_beats == 0.0     # STOPPED
    c.play(); c.update(0.1); c.pause()
    ph = c.playhead_beats
    assert c.update(0.5).playhead_beats == ph          # PAUSED


def test_full_playback_fires_all_in_order_then_completes():
    c = Conductor(make_spell(), T)          # 8 beats at 90 bpm = 5.333 s
    c.play()
    frames, crossed = collect(c, [0.05] * 120)   # 6 s
    assert crossed == list(range(8))
    completes = [f for f in frames if f.completed]
    assert len(completes) == 1
    assert c.state is ConductorState.STOPPED
    assert c.playhead_beats == c.spell.total_beats


def test_playback_triggers_exactly_on_the_beat_no_guard():
    c = Conductor(make_spell(), T)
    c.play()
    f = c.update((1.0 + 1e-6) * 60 / 90)    # land a hair past beat 1.0
    assert 1 in f.crossed                   # guard must NOT delay playback


def test_play_after_end_rewinds():
    c = Conductor(make_spell(), T)
    c.play(); collect(c, [0.1] * 60)        # run to the end
    c.play()
    f = c.update(0.01)
    assert f.playhead_beats < 1.0 and 0 in f.crossed


def test_jump_fires_landing_note_only_and_keeps_state():
    c = Conductor(make_spell(GAPPY), T)
    c.play()
    c.jump_to_beats(2.7)                    # inside note 3
    f = c.update(0.0)
    assert f.crossed == (3,) and f.state is ConductorState.PLAYING
    c2 = Conductor(make_spell(GAPPY), T)
    c2.jump_to_beats(2.2)                   # inside the rest
    f2 = c2.update(0.0)
    assert f2.crossed == () and f2.active_note_index is None


def test_jump_respects_retrigger_min():
    c = Conductor(make_spell(), T)
    c.jump_to_beats(0.5); c.update(0.01)         # fires note 0; clock +10 ms
    c.jump_to_beats(0.6)
    assert c.update(0.01).crossed == ()          # 20 ms < 90 ms: suppressed
    c.update(0.2)                                # let the clock pass 90 ms
    c.jump_to_beats(0.7)
    assert c.update(0.0).crossed == (0,)


def test_scrub_guard_hysteresis_forward():
    c = Conductor(make_spell(), T)               # guard = 0.04 beats
    c.begin_scrub()
    c.scrub_to_beats(1.02)                       # past start, NOT past 1.04
    assert c.update(0.1).crossed == (0,)         # only note 0 (line at 0.04)
    c.scrub_to_beats(1.05)                       # now past 1.04
    assert c.update(0.1).crossed == (1,)


def test_scrub_backward_reverses_melody():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(8.0); c.update(0.2)         # sweep to the end (flushes)
    c.scrub_to_beats(0.0)
    f = c.update(0.2)
    assert list(f.crossed[-3:]) == [2, 1, 0]     # reverse traversal order


def test_boundary_jitter_cannot_machine_gun():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(1.10); c.update(0.2)        # fired notes 0 and 1
    for _ in range(20):                          # jitter +-0.02 around 1.08
        c.scrub_to_beats(1.06); c.update(0.02)
        c.scrub_to_beats(1.10); c.update(0.02)
    _, crossed = collect(c, [0.0])
    assert crossed == []                         # nothing refires


def test_lingering_never_retriggers():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(0.5); c.update(0.2)
    for _ in range(30):                          # wander INSIDE note 0
        c.scrub_to_beats(0.3); c.update(0.05)
        c.scrub_to_beats(0.7); c.update(0.05)
    _, crossed = collect(c, [0.0])
    assert crossed == []


def test_leave_and_reenter_refires_after_min_interval():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(0.5); c.update(0.2)         # fire note 0, clock +200 ms
    c.scrub_to_beats(1.5); c.update(0.2)         # leave (fires 1), re-arm 0
    c.scrub_to_beats(0.5)                        # re-enter from the right
    assert c.update(0.2).crossed == (0,)         # 200 ms > 90 ms: refires


def test_flurry_cap_trims_audio_not_visuals():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(7.5)                        # one gesture across all 8
    f = c.update(0.1)
    assert f.crossed == tuple(range(8))          # the eye sees everything
    assert f.triggers == (4, 5, 6, 7)            # the ear gets the LAST 4


def test_end_scrub_is_paused_never_resumes():
    c = Conductor(make_spell(), T)
    c.play(); c.update(0.1)
    c.begin_scrub(); c.scrub_to_beats(3.2); c.end_scrub()
    f = c.update(0.5)
    assert f.state is ConductorState.PAUSED
    assert abs(f.playhead_beats - 3.2) < 1e-9


def test_active_note_index_tracks_regions_and_rests():
    c = Conductor(make_spell(GAPPY), T)
    c.jump_to_beats(1.7)
    assert c.update(0.0).active_note_index == 2
    c.jump_to_beats(2.2)
    assert c.update(0.0).active_note_index is None


def test_determinism_same_script_same_frames():
    def run():
        c = Conductor(make_spell(GAPPY), T)
        out = []
        c.play()
        out += [c.update(0.07) for _ in range(20)]
        c.begin_scrub()
        for b in (3.1, 0.4, 5.2, 2.2):
            c.scrub_to_beats(b); out.append(c.update(0.03))
        c.end_scrub()
        out += [c.update(0.07) for _ in range(5)]
        return out
    assert run() == run()


def test_wiring_with_fake_audio_sink():
    spell = make_spell()
    sink = FakeAudioSink()
    sink.preload("", spell.sample_paths)
    c = Conductor(spell, T)
    c.play()
    for _ in range(120):
        f = c.update(0.05)
        for i in f.triggers:
            sink.trigger(spell.notes[i].sample, spell.notes[i].gain)
    assert sink.triggered == [(f"s{i}.mp3", 0.9) for i in range(8)]
```

For DeepSeek — the M1 run sheet:

    Save all files; pip install pytest if missing (pygame already present from M0).
    python -m pytest loom/tests -v — 25+ assertions on the heart, headless, no audio.
    python loom/player/m1_demo.py — real violin from the library. Then --spell loom/fixtures/spells/fixture_varied5.json for the oboe with the rest and the long final note.
    If the resolver errors on any note, the message names exactly what it searched — paste it back to me and I'll adjust the fixture, not the doctrine.
    Then the ear session with Nir: the 9-step acceptance script prints on startup. Feel adjustments go only into scrub_tuning.json.
    When it lands, flip M1 in MAP.md and add the Commentaries line.

Nir — when you run step 3, the first thing your hand touches will be a real violin. 🎻 Say "continue" for Part 3: the complete skeleton of everything else — every future module of the game and the compiler as small, well-commented bones ready for future parents to fatten. 😊
