"""
m3_demo.py — Milestone 3: the Echo answers back. [demo scaffolding]

Run (from anywhere):
    python m3_demo.py                       <- violin line, grow mode
    python m3_demo.py --mode whole          <- full melody, answer all slots
    python m3_demo.py --spell fixtures/spells/fixture_bench20.json
    python m3_demo.py --library "D:/somewhere/philharmonia"
    python m3_demo.py --beeps               <- EXPLICIT fallback only

DEMO TEXTS ONLY: the intro/hint/success strings below are placeholders;
in the real game every word comes from pack.json (intro_text,
hint_higher, hint_lower, success_text) — M7's pack loader.

GROW-MODE ROUND EDGE (design decision, flagged for Nir's ear): while a
grow puzzle is unfinished, the playable/scrubbable world ends at the
current round's last note — the transport cannot wander into notes the
game has not revealed yet. Whole mode (and the COMPLETE celebration)
roam the full melody. If Nir prefers total freedom even in grow,
boundary_beats() below shrinks to one line.

NIR'S ACCEPTANCE SCRIPT (printed on startup):
  1. The first violin note plays by itself; its key, graph segment and
     staff slot light together. Then it is YOUR turn.
  2. Click any piano key: it SOUNDS (audition) and a hollow notehead
     appears at YOUR guess on the staff. OK wakes up.
  3. Commit a WRONG key: nothing harsh happens - the hollow note fades
     and a gentle hint says which way to go. Try as often as you like.
  4. Commit the RIGHT key: a soft, quieter echo of that same note; the
     notehead turns SOLID; the melody replays one note longer.
  5. Scrub or replay at ANY time - your answered slots never move. In
     grow mode the timeline ends at the round's edge.
  6. Enter = OK, Backspace = Cancel (except while typing in the BPM
     box). Space = play/pause. Everything also works mouse-only.
  7. Land the last note: the whole melody replays in celebration.
  8. The only question: does it feel like the game answering back?
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOOM_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from core.spell_model import load_spell                      # noqa: E402
from core.tuning import load_tuning                          # noqa: E402
from core.conductor import Conductor, ConductorState         # noqa: E402
from core.notation import NotationTable                      # noqa: E402
from core.echo_logic import EchoLogic, EchoPhase             # noqa: E402
from m1_demo import (resolve_real_samples, resolve_beeps,    # noqa: E402
                     note_name, DEFAULT_LIBRARY)
from m2_demo import resolve_keyboard_coverage                # noqa: E402

DEFAULT_SPELL = os.path.join(LOOM_DIR, "fixtures", "spells",
                             "fixture_bench8.json")
TUNING_PATH = os.path.join(HERE, "data", "scrub_tuning.json")
NOTATION_PATH = os.path.join(HERE, "data", "notation_table.json")
MAPPING_PATH = os.path.join(HERE, "data", "input_mapping.json")
ECHO_TUNING_PATH = os.path.join(HERE, "data", "echo_tuning.json")

# ---- demo stand-ins for pack.json texts (the real ones arrive in M7) ----
INTRO_TEXT = ("Listen: the violin climbs a steady staircase. "
              "Echo each note back on the piano.")
ECHO_PROMPT = "Your turn: click the key you heard, then OK."
GROW_TEXT = "Lovely! Listen - one note longer now..."
# NOTE THE CROSSED NAMES (echo_logic docstring): kind "too_low" shows the
# pack's hint_higher text; kind "too_high" shows the pack's hint_lower.
HINT_WHEN_TOO_LOW = ("Yours was a little low - listen once more, "
                     "or drag through it slowly.")
HINT_WHEN_TOO_HIGH = ("Yours was a little high - listen once more, "
                      "or drag through it slowly.")
SUCCESS_TEXT = ("You heard it! You played the whole line by ear. "
                "Hear it once more, beautifully.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spell", default=DEFAULT_SPELL)
    ap.add_argument("--mode", default="grow", choices=("grow", "whole"))
    ap.add_argument("--library", default=DEFAULT_LIBRARY)
    ap.add_argument("--beeps", action="store_true",
                    help="EXPLICIT test-tone fallback (never the default)")
    args = ap.parse_args()

    spell = load_spell(args.spell)
    tuning = load_tuning(TUNING_PATH)
    table = NotationTable.load(NOTATION_PATH)
    with open(ECHO_TUNING_PATH, "r", encoding="utf-8") as f:
        etune = json.load(f)
    print(f"Loaded spell {spell.spell_id!r}: {len(spell.notes)} notes, "
          f"reveal mode {args.mode!r}.")

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
    from ui.bench_buttons import BenchButton
    from ui.graph_view import GraphView

    init_mixer()
    pygame.init()
    screen = pygame.display.set_mode((layout.WINDOW.w, layout.WINDOW.h))
    pygame.display.set_caption(f"LOOM M3 - {spell.spell_id} ({args.mode})")
    font = pygame.font.SysFont("consolas", 16)
    clock = pygame.time.Clock()

    audio = PygameAudioEngine()
    audio.preload("", sorted(set(resolved.values()) | set(coverage.values())))
    conductor = Conductor(spell, tuning)
    mapper = InputMapper.load(MAPPING_PATH)
    echo = EchoLogic(spell, args.mode)

    keyboard = KeyboardWidget(layout.KEYBOARD, base_midi, octaves)
    staff = StaffWidget(layout.STAFF, table)
    transport = TransportWidget(layout.TRANSPORT, initial_bpm=spell.bpm)
    graph = GraphView(layout.GRAPH)
    ok_btn = BenchButton(layout.OK_BUTTON, "OK", accent=True)
    cancel_btn = BenchButton(layout.CANCEL_BUTTON, "Cancel")

    flash_ms = [0.0] * len(spell.notes)
    ui_state = {"pressed": None}
    state = {"listen": False, "message": INTRO_TEXT, "pending": None}

    def schedule(ms, fn):
        """A lead-in before a replay, never a gameplay timer."""
        state["pending"] = [float(ms), fn]

    def boundary_beats() -> float:
        """Grow mode: the world ends at the round's edge (see docstring)."""
        if args.mode == "grow" and echo.phase() is not EchoPhase.COMPLETE:
            last = echo.notes_to_play()[-1]
            return spell.notes[last].end_beat
        return spell.total_beats

    def clamp_b(b: float) -> float:
        return min(b, max(0.0, boundary_beats() - 0.001))

    def take_over_listening():
        """The player grabbed the transport: the courtesy auto-play ends
        (free re-listening is eternal anyway — Forgiving Forever)."""
        if state["listen"]:
            state["listen"] = False
            echo.listening_finished()
            if echo.phase() is EchoPhase.ECHOING:
                state["message"] = ECHO_PROMPT

    def start_round_playback():
        conductor.stop()
        conductor.play()
        state["listen"] = True

    def apply(events):
        for te in events:
            c = te.command
            if c in (TransportCommand.PLAY_PAUSE, TransportCommand.STOP,
                     TransportCommand.JUMP, TransportCommand.SCRUB_BEGIN):
                take_over_listening()
            if c is TransportCommand.PLAY_PAUSE:
                if conductor.state is ConductorState.PLAYING:
                    conductor.pause()
                else:
                    if conductor.playhead_beats >= boundary_beats() - 0.01:
                        conductor.jump_to_beats(0.0)   # Play always plays
                    conductor.play()
            elif c is TransportCommand.STOP:
                conductor.stop()
                audio.stop_all(tuning.steal_fade_ms)
            elif c is TransportCommand.JUMP:
                conductor.jump_to_beats(clamp_b(te.beats))
            elif c is TransportCommand.SCRUB_BEGIN:
                conductor.begin_scrub()
            elif c is TransportCommand.SCRUB_TO:
                conductor.scrub_to_beats(clamp_b(te.beats))
            elif c is TransportCommand.SCRUB_END:
                conductor.end_scrub()
            elif c is TransportCommand.SET_BPM:
                conductor.set_bpm(te.bpm)
                print(f"(tempo -> {int(te.bpm)} BPM)")

    def do_ok():
        if not ok_btn.enabled:       # Enter path shares the same guard
            return
        result = echo.commit()
        print(f"(commit: {result.kind} on slot {result.target_index})")
        if result.kind == "correct":
            n = spell.notes[result.target_index]
            # the confirm = the note's OWN voice, quieter (NT par.II.2;
            # the optional fifth-below garnish stays parked for now)
            audio.trigger(resolved[result.target_index],
                          n.gain * etune["confirm_gain_factor"])
            if result.puzzle_done:
                state["message"] = SUCCESS_TEXT
                schedule(etune["complete_replay_delay_ms"],
                         start_round_playback)
            elif echo.phase() is EchoPhase.LISTENING:   # grow: next round
                state["message"] = GROW_TEXT
                schedule(etune["grow_replay_delay_ms"],
                         start_round_playback)
            else:                                       # whole: next slot
                state["message"] = ECHO_PROMPT
        elif result.kind == "too_high":
            state["message"] = HINT_WHEN_TOO_HIGH       # no sound: never harsh
        else:
            state["message"] = HINT_WHEN_TOO_LOW

    def do_cancel():
        if echo.phase() is EchoPhase.ECHOING:
            echo.cancel()
            state["message"] = ECHO_PROMPT

    print(__doc__.split("printed on startup):")[-1])
    schedule(etune["intro_lead_in_ms"], start_round_playback)

    running = True
    while running:
        dt_ms = clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            # rev 3: while the BPM box is focused, the keyboard belongs to it
            for action in (mapper.map_event(ev) if not transport.typing else []):
                if action is Action.QUIT:
                    running = False
                elif action is Action.PLAY_PAUSE:
                    apply([TransportEvent(TransportCommand.PLAY_PAUSE)])
                elif action is Action.STOP:
                    apply([TransportEvent(TransportCommand.STOP)])
                elif action in (Action.NUDGE_LEFT, Action.NUDGE_RIGHT):
                    take_over_listening()
                    ph = conductor.playhead_beats
                    bound = boundary_beats()
                    if action is Action.NUDGE_RIGHT:
                        nxt = [n.start_beat for n in spell.notes
                               if ph + 1e-9 < n.start_beat < bound - 1e-9]
                        if nxt:
                            conductor.jump_to_beats(nxt[0])
                    else:
                        prv = [n.start_beat for n in spell.notes
                               if n.start_beat < ph - 1e-9]
                        if prv:
                            conductor.jump_to_beats(prv[-1])
                elif action is Action.OK:
                    do_ok()
                elif action is Action.CANCEL:
                    do_cancel()
            # pointer events flow raw to the widgets:
            apply(transport.handle_event(ev, spell.total_beats))
            apply(graph.handle_event(ev, spell))
            if ok_btn.handle_event(ev):
                do_ok()
            if cancel_btn.handle_event(ev):
                do_cancel()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                midi = keyboard.hit_test(ev.pos)
                if midi is not None:
                    ui_state["pressed"] = midi
                    if midi in coverage:                # audition, always
                        audio.trigger(coverage[midi],
                                      midi_gain.get(midi, 0.9))
                    else:
                        print(f"(no recording for {note_name(midi)})")
                    echo.preview(midi)   # no-op outside ECHOING, on purpose
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                ui_state["pressed"] = None

        # ---- delayed one-shot lead-ins (replays; never gameplay timers) ----
        if state["pending"] is not None:
            state["pending"][0] -= dt_ms
            if state["pending"][0] <= 0:
                fn = state["pending"][1]
                state["pending"] = None
                fn()

        # ---- the wiring loop (conductor.py doctrine + the round edge) ----
        dt = dt_ms / 1000.0
        frame = None
        if conductor.state is ConductorState.PLAYING:
            bound = boundary_beats()
            if bound < spell.total_beats:
                remaining_s = ((bound - conductor.playhead_beats)
                               * 60.0 / conductor.bpm - 0.002)
                if dt >= remaining_s:
                    # land just inside the round's last note, never on the
                    # next note's fire-line, then rest
                    frame = conductor.update(max(0.0, remaining_s))
                    conductor.pause()
                    if state["listen"]:
                        state["listen"] = False
                        echo.listening_finished()
                        state["message"] = ECHO_PROMPT
        if frame is None:
            frame = conductor.update(dt)
            if frame.completed and state["listen"]:
                state["listen"] = False
                echo.listening_finished()     # no-op once COMPLETE
                if echo.phase() is EchoPhase.ECHOING:
                    state["message"] = ECHO_PROMPT

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

        ok_btn.enabled = (echo.phase() is EchoPhase.ECHOING
                          and echo.preview_midi is not None)
        cancel_btn.enabled = echo.phase() is EchoPhase.ECHOING

        # ---- draw ----
        screen.fill((12, 12, 16))
        graph.draw(screen, spell, frame, levels)
        pygame.draw.rect(screen, (18, 18, 22), layout.HELIX)
        pygame.draw.rect(screen, (70, 70, 80), layout.HELIX, 1)
        img = font.render("pitch helix - reserved (M4)", True,
                          (120, 120, 130))
        screen.blit(img, img.get_rect(center=layout.HELIX.center))
        staff.draw(screen, spell, frame, levels, echo=echo)
        keyboard.draw(screen, lit, echo.preview_midi, ui_state["pressed"])
        transport.draw(screen, frame, spell.total_beats)
        ok_btn.draw(screen)
        cancel_btn.draw(screen)
        # demo-only message band (its real home is the Scene Stage, M5)
        band = pygame.Rect(0, 0, layout.WINDOW.w, 26)
        pygame.draw.rect(screen, (24, 24, 30), band)
        screen.blit(font.render(state["message"], True, (235, 225, 200)),
                    (12, 5))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
