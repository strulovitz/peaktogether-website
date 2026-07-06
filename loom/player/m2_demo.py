"""
m2_demo.py — Milestone 2: the Music Bench lives. [demo scaffolding]

Run (from anywhere):
    python m2_demo.py                        <- bench fixture, real violin
    python m2_demo.py --spell <path>         <- any spell JSON
    python m2_demo.py --library <path>       <- Philharmonia root
    python m2_demo.py --beeps                <- EXPLICIT fallback only

Reuses m1_demo's ear-approved resolver (real instruments first, uniform
length, hard error over silent fallback) and wires the M2 widgets:
layout rects, InputMapper, KeyboardWidget, StaffWidget, TransportWidget,
GraphView, notation table.

NIR'S ACCEPTANCE SCRIPT (printed on startup):
  1. SPACE (or click Play): eight rising violin notes; watch the piano
     key, the staff notehead, and the graph segment light TOGETHER.
  2. Drag the timeline: identical feel to M1 (it is the same logic,
     extracted). Release = stays paused.
  3. Drag ON THE GRAPH: the curve itself is a playable surface — slow,
     fast, backward. The bar's handle and the graph cursor always agree.
  4. Click piano keys: each sounds instantly with the real violin (keys
     belonging to this spell), and gets a bright preview outline.
  5. The staff shows 8 noteheads (no stems - noteheads only); the
     sounding one glows and fades warmly.
  6. Click OK / Cancel: they print to the console (their real meaning
     arrives with M3's Echo controller).
  7. The only question that matters: is it ONE instrument now — hand,
     ear, and eye touching the same melody?
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOOM_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from core.spell_model import load_spell                      # noqa: E402
from core.tuning import load_tuning                          # noqa: E402
from core.conductor import Conductor, ConductorState         # noqa: E402
from core.notation import NotationTable                      # noqa: E402
from m1_demo import (resolve_real_samples, resolve_beeps,    # noqa: E402
                     note_name, DEFAULT_LIBRARY)

DEFAULT_SPELL = os.path.join(LOOM_DIR, "fixtures", "spells",
                             "fixture_bench8.json")
TUNING_PATH = os.path.join(HERE, "data", "scrub_tuning.json")
NOTATION_PATH = os.path.join(HERE, "data", "notation_table.json")
MAPPING_PATH = os.path.join(HERE, "data", "input_mapping.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spell", default=DEFAULT_SPELL)
    ap.add_argument("--library", default=DEFAULT_LIBRARY)
    ap.add_argument("--beeps", action="store_true")
    args = ap.parse_args()

    spell = load_spell(args.spell)
    tuning = load_tuning(TUNING_PATH)
    table = NotationTable.load(NOTATION_PATH)
    print(f"Loaded spell {spell.spell_id!r}: {len(spell.notes)} notes.")
    if args.beeps:
        print("NOTE: --beeps requested: test tones, NOT game audio.")
        resolved = resolve_beeps(spell)
    else:
        print(f"Resolving REAL instruments from {args.library} ...")
        resolved = resolve_real_samples(spell, args.library)
    midi_to_sample = {spell.notes[i].midi: p for i, p in resolved.items()}
    midi_gain = {n.midi: n.gain for n in spell.notes}

    # ---- pygame world starts here ----
    from ui.audio_pygame import PygameAudioEngine, init_mixer
    import pygame
    from ui import layout
    from ui.input_actions import InputMapper, Action
    from ui.bench_keyboard import KeyboardWidget
    from ui.bench_staff import StaffWidget
    from ui.bench_transport import TransportWidget, TransportCommand
    from ui.graph_view import GraphView

    init_mixer()
    pygame.init()
    screen = pygame.display.set_mode((layout.WINDOW.w, layout.WINDOW.h))
    pygame.display.set_caption(f"LOOM M2 - {spell.spell_id}")
    font = pygame.font.SysFont("consolas", 16)
    clock = pygame.time.Clock()

    audio = PygameAudioEngine()
    audio.preload("", list(resolved.values()))
    conductor = Conductor(spell, tuning)
    mapper = InputMapper.load(MAPPING_PATH)

    kb = spell.raw.get("keyboard", {})
    base_midi = table.midi_for_name(kb.get("low_note", "C4"))
    high_midi = table.midi_for_name(kb.get("high_note", "C5"))
    octaves = 2 if (high_midi - base_midi) > 12 else 1
    keyboard = KeyboardWidget(layout.KEYBOARD, base_midi, octaves)
    staff = StaffWidget(layout.STAFF, table)
    transport = TransportWidget(layout.TRANSPORT)
    graph = GraphView(layout.GRAPH)

    flash_ms = [0.0] * len(spell.notes)
    preview_midi = None

    def apply(events):
        for te in events:
            c = te.command
            if c is TransportCommand.PLAY_PAUSE:
                (conductor.pause() if conductor.state is ConductorState.PLAYING
                 else conductor.play())
            elif c is TransportCommand.STOP:
                conductor.stop()
                audio.stop_all(tuning.steal_fade_ms)
            elif c is TransportCommand.JUMP:
                conductor.jump_to_beats(te.beats)
            elif c is TransportCommand.SCRUB_BEGIN:
                conductor.begin_scrub()
            elif c is TransportCommand.SCRUB_TO:
                conductor.scrub_to_beats(te.beats)
            elif c is TransportCommand.SCRUB_END:
                conductor.end_scrub()

    print(__doc__.split("printed on startup):")[-1])
    running = True
    while running:
        dt_ms = clock.tick(60)
        for ev in pygame.event.get():
            for action in mapper.map_event(ev):
                if action is Action.QUIT:
                    running = False
                elif action is Action.PLAY_PAUSE:
                    (conductor.pause()
                     if conductor.state is ConductorState.PLAYING
                     else conductor.play())
                elif action is Action.STOP:
                    conductor.stop(); audio.stop_all(tuning.steal_fade_ms)
                elif action in (Action.NUDGE_LEFT, Action.NUDGE_RIGHT):
                    ph = conductor.playhead_beats
                    if action is Action.NUDGE_RIGHT:
                        nxt = [n.start_beat for n in spell.notes
                               if n.start_beat > ph + 1e-9]
                        if nxt:
                            conductor.jump_to_beats(nxt[0])
                    else:
                        prv = [n.start_beat for n in spell.notes
                               if n.start_beat < ph - 1e-9]
                        if prv:
                            conductor.jump_to_beats(prv[-1])
                elif action is Action.OK:
                    print("(OK - Echo controller arrives in M3)")
                elif action is Action.CANCEL:
                    preview_midi = None
            # pointer events flow raw to the widgets:
            apply(transport.handle_event(ev, spell.total_beats))
            apply(graph.handle_event(ev, spell))
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                midi = keyboard.hit_test(ev.pos)
                if midi is not None:
                    preview_midi = midi
                    sample = midi_to_sample.get(midi)
                    if sample:
                        audio.trigger(sample, midi_gain.get(midi, 0.9))
                    else:
                        print(f"(no sample for {note_name(midi)} in this "
                              "demo - real packs ship full keyboard "
                              "coverage via required_samples)")
                elif layout.OK_BUTTON.collidepoint(ev.pos):
                    print("(OK - Echo controller arrives in M3)")
                elif layout.CANCEL_BUTTON.collidepoint(ev.pos):
                    preview_midi = None
                    print("(Cancel - provisional cleared)")

        # ---- the wiring loop (conductor.py doctrine, as in m1_demo) ----
        frame = conductor.update(dt_ms / 1000.0)
        for i in frame.triggers:
            n = spell.notes[i]
            audio.trigger(resolved[i], n.gain)
        for i in frame.crossed:
            flash_ms[i] = tuning.highlight_decay_ms
        for i in range(len(flash_ms)):
            flash_ms[i] = max(0.0, flash_ms[i] - dt_ms)
        levels = [f / tuning.highlight_decay_ms for f in flash_ms]
        lit = {spell.notes[i].midi: levels[i]
               for i in range(len(levels)) if levels[i] > 0}
        if frame.active_note_index is not None:
            lit[spell.notes[frame.active_note_index].midi] = max(
                lit.get(spell.notes[frame.active_note_index].midi, 0.0), 1.0)

        # ---- draw ----
        screen.fill((12, 12, 16))
        graph.draw(screen, spell, frame, levels)
        staff.draw(screen, spell, frame, levels)
        keyboard.draw(screen, lit, preview_midi)
        transport.draw(screen, frame, spell.total_beats)
        for rect, label in ((layout.OK_BUTTON, "OK"),
                            (layout.CANCEL_BUTTON, "Cancel")):
            pygame.draw.rect(screen, (60, 60, 72), rect, border_radius=6)
            img = font.render(label, True, (225, 225, 225))
            screen.blit(img, img.get_rect(center=rect.center))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
