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
        m2_demo.py                    [MEAT]    M2 demo: the whole Music Bench, wired
        core/                         (pure logic, stdlib only, headless-testable)
          spell_model.py              [MEAT]    spell JSON -> SpellData (frozen)
          tuning.py                   [MEAT]    scrub_tuning.json -> ScrubTuning
          conductor.py                [MEAT]    THE HEART: playhead, scrub, triggers
          audio.py                    [MEAT]    AudioSink protocol + FakeAudioSink
          notation.py                 [MEAT]    notation_table.json lookups (staff)
          echo_logic.py               [MEAT]    Echo puzzle state machine (pure, M3)
          choice_logic.py             [BONE M5] Choice puzzle logic (pure)
          lab_remap.py                [BONE M6] the frozen Lab arithmetic (NT I.4)
          pack_model.py               [BONE M7] pack.json loading/validation
          progress.py                 [BONE M7] local save file (last scene, lab unlocks)
        ui/                           (pygame allowed here and only here)
          audio_pygame.py             [MEAT]    16-voice pool over pygame.mixer
          layout.py                     [MEAT]    every fixed 1280x720 rectangle (FROZEN by Nir 2026-07-06)
          input_actions.py            [MEAT]    named actions; device->action mapping (KEY events only)
          bench_keyboard.py           [MEAT]    piano widget (click = sound)
          bench_staff.py              [MEAT]    staff renderer (noteheads only)
          bench_transport.py          [MEAT]    play/pause + timeline (scrub surface 1)
          bench_buttons.py            [MEAT]    OK/Cancel bench buttons (M3, Parent 4)
          graph_view.py               [MEAT]    graph + its scrub surface (surface 2)
          helix_view.py               [BONE M4] demoscene wireframe helix
          story_view.py               [BONE M5] slides, captions, dialogue menus
          lab_view.py                 [BONE M6] slider panel wired to lab_remap
          menu_view.py                [BONE M7] main menu / pack picker
        data/
          scrub_tuning.json           [MEAT]    all feel constants (DeepSeek tunes)
          notation_table.json         [MEAT*]   MIDI 36-96 staff lookup; TEMPORARY
                                        stand-in by DeepSeek (M2). The real
                                        compiler/notation_gen.py will regenerate
                                        the identical file (frozen format).
          input_mapping.json          [MEAT]    device -> named action map
      compiler/                       (Program A — authors' PCs only, never shipped)
        compile_spell.py              [BONE]    CLI: spec.py -> spell JSON + assets
        pipeline.py                   [BONE]    stages 1-7,10,11 of NT Part I.3
        library_scan.py               [BONE]    Philharmonia scan (grammar: see docstring)
        emit.py                       [BONE]    JSON writer + preview.wav + report
        notation_gen.py               [BONE]    generates player/data/notation_table.json
      fixtures/
        spells/fixture_flat8.json     [MEAT]    8 even notes — the happy path
        spells/fixture_varied5.json   [MEAT]    varied durations + a gap (a rest)
        spells/fixture_bench8.json    [MEAT]    M2: rising line, violin, 1 octave (generated)
        spells/fixture_bench20.json   [MEAT]    M2: sqrt curve, cello, 20 notes, grand staff+black keys
        make_bench_fixtures.py        [MEAT]    design-time generator for the two bench fixtures
        make_beeps.py                 [MEAT]    stdlib-only beep WAV generator
        audio_beeps/                  (generated by make_beeps.py; git-ignored)
      forge/
        forge_samples.py            [MEAT]    uniform-duration sample forge (design time)
        forged/                     (generated conditioned WAVs; git-ignored)
      tests/
        test_purity.py                [MEAT]    core/ never imports pygame
        test_spell_model.py           [MEAT]    loader validation
        test_conductor.py             [MEAT]    the full M1 behavior suite
        test_notation.py              [MEAT]    notation table load/lookup (M2)
        test_m2_widgets.py            [MEAT]    keyboard/transport/graph geometry+maps (M2)
        test_input_mapper.py          [MEAT]    InputMapper key->action (M2)
        test_bench_fixtures.py        [MEAT]    generated fixture validation (M2)
        test_length_choice.py         [MEAT]    FIT-THE-BEAT sample-length rule (M2)
        test_echo_logic.py            [MEAT]    Echo state machine behavior (M3)
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
- Sample lengths are chosen UNIFORMLY per spell (the Selection Law,
  2026-07-06). A note becomes a file only in compiler/library_scan.py
  (or its forge/demo stand-ins); nowhere else, ever.

## Status log (DeepSeek appends one line per landed milestone)

- 2026-07-06  M0 done: pygame 2.6.1 / SDL 2.28.4, MP3 GO, buffer 256 = 5.8 ms.
- (next)      M1: pending integration of this skeleton.
- 2026-07-06  M2 Part 1/5 (Parent 3): core/notation.py fattened -> MEAT; frozen
              notation_table.json format + temporary MIDI 36-96 stand-in; 35 tests pass.
- 2026-07-06  M2 Parts 2-5 (Parent 3): all 7 M2 bones -> MEAT (layout, input_actions,
              bench_keyboard, bench_staff, bench_transport, graph_view, notation);
              fixture_bench8.json + m2_demo.py added; 47 tests pass. DeepSeek integration
              fixes (flagged to Fable): white-key tiling gap; subprocess purity test.
              Layout numbers still PROVISIONAL until Nir's eye-tuning pass on m2_demo.
- 2026-07-06  M2 POUR 2 (Parent 3, rev 2): wide bench + FULL GRAND STAFF (Nir amendment)
              + black keys sing + pressed-key visuals + curved fixtures. make_bench_fixtures.py
              generates fixture_bench8 (violin) + fixture_bench20 (cello sqrt, 20 notes -
              Nir raised the cap 16->20). Cello 20-note fixture verified: resolves at length
              '15', all 25 keyboard keys sound. 51 tests pass.
- 2026-07-06  M2 ghost-pedal fix (Parent 3): FIT-THE-BEAT rule in m1_demo resolver
              (uniform length = longest token <= shortest note's seconds; fallback shortest).
              Kills the sustain-pedal note overlap in the 20-note cello demo (now picks 025).
              +test_length_choice.py. 57 tests pass. Amendment in Commentaries §5.
- 2026-07-06  M2 rev 3 (Parent 3): BPM box - additive Conductor.set_bpm (live tempo,
              M6 Lab pre-work) + TransportWidget gains typed BPM box (40-200, Enter/Esc/
              click-away) + up/down spinners on far right + .typing guard (mutes hotkeys).
              Content default BPM = 110. +test_transport_bpm.py (7 tests). 65 tests pass.
- 2026-07-06  M2 COMPLETE. Parent 3 (Fable) RETIRED (final will archived). NEXT = fresh
              Parent 4 for M3 (the Echo). Loose ends: layout eye-freeze (Nir); bench_buttons.py
              (Fable wrote, not landed) -> Parent 4; notation_table.json still temporary.
- 2026-07-06  LAYOUT FROZEN by Nir (played m2_demo, approved as-is; layout.py numbers are
              now permanent - do not move the keyboard/staff/etc).
- 2026-07-06  M3 POUR 1 (Parent 4): core/echo_logic.py fattened -> MEAT with ADDITIVE read-only
              accessors (reveal_mode, prefix_len, cursor, preview_midi, slot_states) for the
              staff's solid/hollow/dashed slots; ui/bench_buttons.py born (BenchButton; OK must
              be disabled unless a preview exists - commit() raises on wiring misuse). Hint-name
              mapping: kind too_low -> pack hint_higher text, kind too_high -> pack hint_lower
              text (crossed names, documented). +test_echo_logic.py (14 tests). 79 tests pass.
