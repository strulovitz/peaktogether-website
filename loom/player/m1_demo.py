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
