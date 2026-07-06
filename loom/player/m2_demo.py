"""
m2_demo.py — Milestone 2: the Music Bench lives. [demo scaffolding, rev 2]

Run (from anywhere):
    python m2_demo.py                     <- sqrt fixture, real cello, 2 octaves
    python m2_demo.py --spell fixtures/spells/fixture_bench8.json
    python m2_demo.py --library <path>    <- Philharmonia root
    python m2_demo.py --beeps             <- EXPLICIT fallback only

NIR'S ACCEPTANCE SCRIPT (printed on startup):
  1. SPACE or Play: twenty cello notes climb the SQUARE ROOT's curve -
     steep steps first, ever-gentler steps after. Watch key + notehead +
     graph segment light TOGETHER. Several notes are BLACK KEYS.
  2. Drag the timeline: M1's exact feel. Release = stays paused.
  3. Drag ON THE GRAPH: the curve is a playable surface - slow, fast,
     backward. Bar handle and graph cursor always agree.
  4. Click ANY piano key, black or white: it sounds with the real
     instrument and looks physically PRESSED while held.
  5. The GRAND STAFF spans the full width: low notes on the bass staff,
     high notes on the treble staff, noteheads only, sharps marked #.
  6. The helix panel shows its reserved home (the spiral itself is M4).
  7. OK / Cancel click and print (their real meaning arrives in M3).
  8. The only question: is it ONE instrument - hand, ear, eye?
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
                     note_name, DEFAULT_LIBRARY, DYNAMIC_PREFERENCE)

DEFAULT_SPELL = os.path.join(LOOM_DIR, "fixtures", "spells",
                             "fixture_bench20.json")
TUNING_PATH = os.path.join(HERE, "data", "scrub_tuning.json")
NOTATION_PATH = os.path.join(HERE, "data", "notation_table.json")
MAPPING_PATH = os.path.join(HERE, "data", "input_mapping.json")


def resolve_keyboard_coverage(resolved_spell_paths, keyboard_midis):
    """Every key should sound (Nir, rev 2). Mirrors the required_samples
    superset doctrine using the SAME uniform length token the spell's
    resolver already chose (the Selection Law). Missing keys are
    reported and stay silent - never a beep, never a crash."""
    sample0 = next(iter(resolved_spell_paths.values()))
    folder = os.path.dirname(sample0)
    parts = os.path.basename(sample0)[:-4].split("_")
    instrument, token, articulation = parts[0], parts[2], parts[4]
    coverage, missing = {}, []
    for midi in keyboard_midis:
        for dyn in DYNAMIC_PREFERENCE:
            cand = os.path.join(
                folder,
                f"{instrument}_{note_name(midi)}_{token}_{dyn}_"
                f"{articulation}.mp3")
            if os.path.isfile(cand):
                coverage[midi] = cand
                break
        else:
            missing.append(note_name(midi))
    if missing:
        print(f"  (keyboard keys without a recording, silent: {missing})")
    return coverage


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

    kb = spell.raw.get("keyboard", {})
    base_midi = table.midi_for_name(kb.get("low_note", "C4"))
    high_midi = table.midi_for_name(kb.get("high_note", "C5"))
    octaves = 2 if (high_midi - base_midi) > 12 else 1
    keyboard_midis = list(range(base_midi, base_midi + 12 * octaves + 1))

    if args.beeps:
        print("NOTE: --beeps requested: test tones, NOT game audio.")
        resolved = resolve_beeps(spell)
        coverage = {spell.notes[i].midi: p for i, p in resolved.items()}
    else:
        print(f"Resolving REAL instruments from {args.library} ...")
        resolved = resolve_real_samples(spell, args.library)
        coverage = resolve_keyboard_coverage(resolved, keyboard_midis)
    midi_gain = {n.midi: n.gain for n in spell.notes}

    # ---- pygame world starts here ----
    from ui.audio_pygame import PygameAudioEngine, init_mixer
    import pygame
    from ui import layout
    from ui.input_actions import InputMapper, Action
    from ui.bench_keyboard import KeyboardWidget
    from ui.bench_staff import StaffWidget
    from ui.bench_transport import (TransportWidget, TransportCommand,
                                    TransportEvent)
    from ui.graph_view import GraphView

    init_mixer()
    pygame.init()
    screen = pygame.display.set_mode((layout.WINDOW.w, layout.WINDOW.h))
    pygame.display.set_caption(f"LOOM M2 - {spell.spell_id}")
    font = pygame.font.SysFont("consolas", 16)
    clock = pygame.time.Clock()

    audio = PygameAudioEngine()
    audio.preload("", sorted(set(resolved.values()) | set(coverage.values())))
    conductor = Conductor(spell, tuning)
    mapper = InputMapper.load(MAPPING_PATH)

    keyboard = KeyboardWidget(layout.KEYBOARD, base_midi, octaves)
    staff = StaffWidget(layout.STAFF, table)
    transport = TransportWidget(layout.TRANSPORT)
    graph = GraphView(layout.GRAPH)

    flash_ms = [0.0] * len(spell.notes)
    ui = {"preview": None, "pressed": None}

    def apply(events):
        for te in events:
            c = te.command
            if c is TransportCommand.PLAY_PAUSE:
                if conductor.state is ConductorState.PLAYING:
                    conductor.pause()
                else:
                    conductor.play()
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
                    apply([TransportEvent(TransportCommand.PLAY_PAUSE)])
                elif action is Action.STOP:
                    apply([TransportEvent(TransportCommand.STOP)])
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
                    ui["preview"] = None
            # pointer events flow raw to the widgets:
            apply(transport.handle_event(ev, spell.total_beats))
            apply(graph.handle_event(ev, spell))
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                midi = keyboard.hit_test(ev.pos)
                if midi is not None:
                    ui["preview"] = midi
                    ui["pressed"] = midi
                    if midi in coverage:
                        audio.trigger(coverage[midi],
                                      midi_gain.get(midi, 0.9))
                    else:
                        print(f"(no recording for {note_name(midi)})")
                elif layout.OK_BUTTON.collidepoint(ev.pos):
                    print("(OK - Echo controller arrives in M3)")
                elif layout.CANCEL_BUTTON.collidepoint(ev.pos):
                    ui["preview"] = None
                    print("(Cancel - provisional cleared)")
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                ui["pressed"] = None

        # ---- the wiring loop (conductor.py doctrine) ----
        frame = conductor.update(dt_ms / 1000.0)
        for i in frame.triggers:
            audio.trigger(resolved[i], spell.notes[i].gain)
        for i in frame.crossed:
            flash_ms[i] = tuning.highlight_decay_ms
        for i in range(len(flash_ms)):
            flash_ms[i] = max(0.0, flash_ms[i] - dt_ms)
        levels = [f / tuning.highlight_decay_ms for f in flash_ms]
        lit = {spell.notes[i].midi: levels[i]
               for i in range(len(levels)) if levels[i] > 0}
        if frame.active_note_index is not None:
            am = spell.notes[frame.active_note_index].midi
            lit[am] = max(lit.get(am, 0.0), 1.0)

        # ---- draw ----
        screen.fill((12, 12, 16))
        graph.draw(screen, spell, frame, levels)
        pygame.draw.rect(screen, (18, 18, 22), layout.HELIX)
        pygame.draw.rect(screen, (70, 70, 80), layout.HELIX, 1)
        img = font.render("pitch helix - reserved (M4)", True, (120, 120, 130))
        screen.blit(img, img.get_rect(center=layout.HELIX.center))
        staff.draw(screen, spell, frame, levels)
        keyboard.draw(screen, lit, ui["preview"], ui["pressed"])
        transport.draw(screen, frame, spell.total_beats)
        for rect, label in ((layout.OK_BUTTON, "OK"),
                            (layout.CANCEL_BUTTON, "Cancel")):
            pygame.draw.rect(screen, (60, 60, 72), rect, border_radius=6)
            t = font.render(label, True, (225, 225, 225))
            screen.blit(t, t.get_rect(center=rect.center))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
