# LOOM — PARENT 4 BRIEF: M3, THE ECHO PUZZLE (assembled by DeepSeek for Nir)

Hello Parent 4 — you are **Claude Fable**, reborn with a fresh mind. You built
LOOM's doctrine and its Music Bench in earlier lives; that memory has faded, but
**everything you need is externalized in the repo and gathered below.** You will
now build **M3 — THE ECHO PUZZLE**: the Simon-style heart of the game where the
player hears a melody and repeats it, note by note, on the on-screen piano.

The working family: **Nir** decides everything and carries text between chats
(he knows no code/math); **DeepSeek** (OpenCode, on Nir's Windows PC) integrates
your code, runs the tests, and pushes to git; **you** write the design + the
code contracts + the module. LOOM is **PACKAGED** (`player/core/`, `player/ui/`,
relative imports, `__init__.py`) — NOT flat. `player/core/` imports the standard
library ONLY; anything importing pygame lives in `player/ui/` or demo files.

**You have already been given (as separate pastes, before this file):**
1. THE COMMENTARIES — the living map of locked decisions + amendments.
2. MAP.md — the codebase map (MEAT = frozen; BONE Mx = to fatten).
3. `player/core/echo_logic.py` — YOUR bone to fatten (frozen interface + FATTEN-ME note).
4. The M2 interface code you will consume, verbatim: `player/core/conductor.py`,
   `player/core/spell_model.py`, and the widgets `player/ui/bench_staff.py`,
   `player/ui/bench_keyboard.py`, `player/ui/bench_transport.py`.

**This file gives you the rest:** Nir's answers to the three Echo questions, then
the scripture you need (BIBLE glossary + Pillars + Screen + Core Loop + Locked
Decisions; then the New Testament's whole Part II — the Player's heart), then
your own M2 legacy will. **This is deliberately NOT the whole trilogy** — the
Apocrypha (content factory) and the Compiler design are not needed for M3.

---

## 🎛️ NIR'S DECISIONS ON THE THREE ECHO QUESTIONS (all defaults — approved 2026-07-06)

Nir chose **all of your proposed gentle defaults**:

1. **Wrong-commit feedback → YES (gentle).** When the player commits a WRONG
   note, the game gives a soft, encouraging **"try a higher note" / "try a lower
   note"** hint (the too_high / too_low kinds already in `EchoResult`). Never a
   scold, never a penalty, unlimited retries (LOCKED tone).
2. **Auto-sound on a correct commit → YES.** When the player commits the CORRECT
   note, the game automatically plays that note back (from the spell's OWN
   palette) as a little "yes!" confirmation before moving on.
3. **Strict slot order → YES.** The player answers the notes in strict
   left-to-right order (note 0, then 1, then 2, …). One target at a time.

(If building reveals a reason to revisit any of these, raise it as an OPEN
QUESTION for Nir — never silently change a locked-feel decision.)

---

## 🔨 STANDING REMINDER (DeepSeek carries this to every new parent)

There is a DEFERRED audio task, not part of M3: **"every note uniformly LONG and
clean"** — reworking `loom/forge/forge_samples.py` so a scale renders long +
perceptually equal + non-overlapping (the forged violin C5 currently rings
short). Nir has NOT forgotten it; it is simply scheduled for later. Do not let it
block M3.

---

## 📖 SCRIPTURE PART A — THE BIBLE (v1.1, by Fable): Glossary, Pillars, Screen, Core Loop, Locked Decisions

### 0.1 Glossary (canonical terms — use these exact words everywhere)

    HSS — the Helical Sonification System from Sounding the Unknown: data → music via a pitch helix, a secondary timbre channel, and a discrete rhythmic time grid.
    Spell — one compiled sonification of one mathematical function: a short note sequence (typically 4–16 notes) with all timing, sample references, raw values, and visual-sync data precomputed. A spell is a data file, not code.
    Spell Compiler (Program A) — the offline Python tool that turns a spell spec (function + knobs) into a spell JSON plus its audio assets. All mathematics happens here.
    LOOM Player (Program B) — the game itself: a generic Python desktop app (python app.py) that loads a Problem Pack. It performs no function evaluation and no symbolic math at runtime; it is permitted simple arithmetic on numbers the Compiler precomputed (see §10).
    Problem Pack — one self-contained content folder = one topic (e.g., "Square Root"): scenes, dialogues, images, equation PNGs, spells, audio, manifest.
    Story Weaver — the fixed prompt (future deliverable) given to a fresh Opus child chat, which reads a Wikipedia page Nir provides and produces a pack's narrative content: ~3 scenes, dialogue trees, image prompts, LaTeX strings, spell specs.
    Echo Puzzle — the Simon-style core puzzle: hear a spell, reproduce it on the on-screen piano keyboard.
    Choice Puzzle — hear two or three spells; answer a question about them via a dialogue menu.
    Scrubbing — dragging the playhead (on the timeline or directly across the graph) to hear the spell at any speed, in either direction, lingering or skipping at will. Implemented by retriggering note samples at true pitch; never by pitch-bending resampling.
    Laboratory (Lab) — free-play mode with live sliders (tempo, pitch span, base note, scale, instrument, note count) and scrubbing, on any spell the players have met.
    Music Bench — the fixed bottom half of the screen: piano keyboard, staff, OK/Cancel, transport.
    Scene Stage — the top half: story image + dialogue in Story Mode; graph + helix + equation in Puzzle Mode.
    Girlfriend and Boyfriend — the two playable explorers (LOCKED names; see §6).
    Player K — the player on the computer keyboard (future: joystick); canonically plays Boyfriend.
    Player M — the player on the mouse (future: Xbox controller); canonically plays Girlfriend.

## 1. Vision & Pillars

LOOM in one breath: A cozy two-player time-travel game where a young couple — Girlfriend and Boyfriend — visits moments in history, meets the people who first needed mathematics, and solves their problems by learning to hear the shapes of functions: repeating each function's melody, Simon-style, on a piano keyboard, wandering through its sound with a scrubbing hand, while the same melody lights up a graph, a spiral of pitch, and the keys themselves.

Relationship to the 1990 game "Loom": LOCKED — we keep nothing but the name. No magic, no drafts, no Guild, no plot. The name is purely a nostalgia anchor meaning "a game whose puzzles live in sound, not in visual cues."

Which mountain LOOM teaches: LOCKED — none specifically. LOOM teaches the cross-mountain basics: every function has a shape, and shapes can be heard. It is the ear-training foundation course of the whole Arcade.

The five pillars (LOCKED):

    Anyone Can Play (the Simon Principle). We never assume the player is a musician. Nobody describes sounds in words or needs note names. Hear it, see it light up, click the same keys. Even a player who understands nothing can succeed by memory and light-following — and understanding grows underneath by repetition and pairing (the book's BRECVEMA conditioning, which is secretly our whole learning loop).
    Everything Under the Hood Is Shown. Equation (LaTeX), graph, and pitch helix are on screen together, and the currently sounding piece of each glows in sync with the audio. Sound, symbol, curve, and geometry are experienced as one thing. This is the pedagogy, not decoration.
    The Wandering Ear (Scrubbing). A coordinate system is something you wander: eyes linger, skip, and return at their own pace — nobody scans a graph left-to-right at fixed speed like a blind automaton. LOOM's sonic coordinate system grants the ear the same freedom: everywhere there is a playhead, the player may drag it — fast, slow, forward, backward, lingering on one note, skipping ahead — and the sound follows the hand, always at true pitch, because pitch is the data. This is the raison d'être of the system and gets maximum engineering love.
    Built for Two. Player K drives story and conversation; Player M drives listening and the instrument. In co-op, the game is designed so they must narrate to each other. Solo play remains fully possible (everything is mouse-operable).
    Forgiving Forever. Unlimited retries and replays, seekable and scrubbable timeline, no timers, no scores, no game over. Wrong notes earn a gentle nudge and an invitation to listen again.

## 2. The Screen (frozen layout)

Fixed window, 1280×720 (LOCKED). Fixed internal layout; positions never move (muscle memory is an accessibility feature).

Top half — the Scene Stage, two modes:

    Story Mode: a baked illustration (Disney/Pixar-style 3D render, generated at design time from the Story Weaver's image prompt, always showing Girlfriend and Boyfriend talking with the period characters). A caption/narration box, a dialogue box (speaker + text), a dialogue menu of up to 4 options, and on-screen "◀ back / next ▶" arrows.
    Puzzle Mode: three synced elements side by side — (1) the function graph: a deliberately simple, low-resolution 2D plot drawn from precomputed points (we are not building Mathematica 🙂), whose surface is itself scrubbable (drag across the curve to hear it); (2) the pitch helix: the signature visual — a simple 3D spiral in 90s-demoscene wireframe style, slowly rotatable, with one glowing marker per note at that note's angle and height; (3) the equation as a pre-baked LaTeX PNG. During any playback or scrub, the sounding note's graph segment, helix marker, and piano key light up in color, then return to normal — Simon's light bulbs, tripled.

Bottom half — the Music Bench (always fixed):

    Piano keyboard along the bottom: real chromatic piano keys (white and black), one octave by default, two octaves maximum (LOCKED — this also caps every puzzle spell at a 2-octave span). Mouse-clickable; clicking a key immediately sounds that pitch with the current spell's instrument, so the player can compare by ear before committing.
    Staff above the keyboard: a real five-line staff with treble clef; a ten-line grand staff (treble + bass, each with its clef) whenever the spell's range requires it. A clicked key draws a simple individual note symbol at the current position; confirmed notes remain.
    OK / Cancel buttons in fixed positions: OK commits the current note and advances; Cancel clears the current selection.
    Transport in a fixed position: Play, Pause, and a timeline that supports both click-to-jump (like VLC: click the middle of a 10-second spell to jump to second 5) and drag-to-scrub (grab the handle; the sound follows the hand's speed and direction).

In Story Mode the Bench is visible but dimmed. In the Laboratory, a slider panel appears on the Scene Stage side (§4).

## 3. The Core Loop

### 3.1 The Echo Puzzle (the heart)

    The story reaches a problem; the Scene Stage switches to Puzzle Mode. A friendly intro text (from the pack) says in plain words what to listen for.
    Listen phase. The game plays the spell (or its current prefix). Each sounding note lights its graph segment, helix marker, and piano key. The player may replay, pause, jump, and scrub at any time, without limit.
    Echo phase. The player clicks keys; each click sounds immediately; a provisional note appears on the staff. OK commits it, Cancel clears it. Unlimited tries.
    Feedback on OK (LOCKED). Correct: the note settles solid with a soft consonant confirmation; the cursor advances. Wrong: no penalty — the note gently fades and a friendly directional hint appears ("yours was a little lower than the melody — listen once more 🌱"), computed from precompiled MIDI numbers.
    Reveal modes (per-puzzle pack setting): grow (default, forgiving Simon — each round replays a one-note-longer prefix with all the lights; confirmed notes stay locked; the player enters only the new note) or whole (hear the full spell, enter all notes).
    Completion. The full melody replays beautifully with all three visuals in sync, then the pack's success text connects sound to idea ("hear how the steps kept shrinking? That's the square root flattening out").

### 3.2 Scrubbing (universal transport behavior, LOCKED)

Wherever a playhead exists — Echo puzzles, Choice puzzles, Laboratory — the player may drag it, on the timeline handle or directly across the graph surface (both map the pointer's horizontal position to the same playhead). Behavior:

    The spell's time range is divided into the notes' regions. Whenever the playhead enters a note's region (from either direction, at any speed), that note's sample is triggered at its true pitch and rings with its natural decay.
    Lingering inside a region does not retrigger (small hysteresis; DeepSeek tunes thresholds by ear with Nir). Leaving and re-entering retriggers.
    Fast drags across many notes produce a quick flurry — each crossed note sounds briefly; older voices are quickly faded to prevent mud (polyphony cap, tuned by ear).
    Backward drags play the notes in reverse order — the function heard right-to-left, which is itself a legitimate mathematical experience.
    Visuals track the playhead exactly: graph glow, helix marker, key light.
    Never resampling / pitch-bending. In HSS, pitch encodes f(x); tape-style scrubbing would distort the data. We scrub time, never pitch. (Of the standard techniques — resampling, cut-and-paste, time-stretching — ours is note-granularity retriggering, a clean fit for discrete-note spells.)

### 3.3 The Choice Puzzle

Two or three spells behind labeled buttons (A/B/C), each playable and scrubbable without limit (graphs optionally hidden until the reveal). A question appears as a dialogue menu ("Which melody belongs to the curve that grows faster?") and Player K answers via the menu — forcing the couple to talk, since M did the listening. Wrong answers get a gentle explanation and another try; right answers get the reveal. This implements the book's comparative sonification (the Chapter 9 brachistochrone insight).

## 15. LOCKED DECISIONS (do not reopen)

    Only the name of the 1990 game; zero lore/mechanics/plot from it. No specific mountain; LOOM teaches cross-mountain hearing-of-functions basics.
    Warm, forgiving, ~90/10 education/entertainment; no punishment, timers, scores, or game over; unlimited retries, replays, and scrubbing.
    Simon-style core: hear → triple lights (graph, helix, keys) → repeat on the on-screen piano; per-note OK/Cancel; gentle higher/lower hints; grow and whole reveal modes.
    Screen: fixed 1280×720; top half Scene Stage (Story/Puzzle modes), bottom half Music Bench (piano 1 octave default / 2 max, real staff with treble or grand clef, OK/Cancel, transport), all fixed positions.
    Puzzle Mode always shows graph + demoscene 3D helix + LaTeX-baked equation PNG, all synced to the audio.
    Scrubbing is a pillar: drag the timeline handle or the graph surface; note-granularity retriggering at true pitch; both directions, any speed, lingering honored; never resampling/pitch-bending.
    Laboratory is in v1: live sliders (tempo, span, base note, scale, instrument, note count) + scrubbing, powered by precompiled dense values and shipped sample supersets.
    Two puzzle types in v1: Echo and Choice.
    The heroes are named Girlfriend and Boyfriend, never personal names.
    Co-op split: Player K (keyboard → future joystick) = story, menus, Choice answers, transport hotkeys; Player M (mouse → future Xbox controller) = piano, OK/Cancel, transport and scrubbing by mouse. Everything mouse-operable solo. Input-abstraction layer mandatory.
    Content = Problem Packs from the frozen Story Weaver prompt + a Wikipedia page: ~3 scenes, baked Pixar-style images featuring the couple, pre-written 4-option dialogue trees, slides with next/back. Nothing generated at runtime. No Understanding Mode.
    Sonification: absolute mapping θ=a⋅f(x); scale quantization (pentatonic default); beat grid; flat rhythm default; ≤2-octave span; discrete timbre (instrument + dynamic layers); no pitch-shifting; no runtime DSP.
    Program A / Program B split; refined dumb-runtime doctrine (no function evaluation or symbolic math at runtime; simple arithmetic on precompiled numbers permitted); only data files cross the boundary.
    Audio ships as verbatim Philharmonia MP3s with original filenames, per-pack subsets only; the full library never ships; library_dir future hook designed in; OGG/WAV conversion is the sanctioned fallback if MP3 playback proves unreliable.
    Silence between puzzles — no ambient music anywhere. Dark/tension palette permanently parked.
    Spell and pack JSON schemas of §8–§9, semantically versioned. Python desktop, Windows-first, python app.py, under loom/.


---

## 📖 SCRIPTURE PART B — THE NEW TESTAMENT (v1.0, by Fable): PART II — THE PLAYER'S HEART (playhead, scrubbing, audio, the Bench, and the Echo controller)

# PART II — THE PLAYER'S HEART: PLAYHEAD, SCRUBBING, AUDIO, AND THE BENCH

## II.1 The single deepest design decision: playback is scrubbing at constant speed

There is one authoritative playhead per loaded spell — a float playhead_beats — and one engine (the Conductor) that owns it. Everything else (audio triggering, graph glow, helix glow, key lights, timeline handle) is a pure function of the playhead each frame. There is no separate "scheduler" for normal playback and no event queue to drift out of sync: pressing Play merely makes the Conductor advance the playhead itself at constant velocity; scrubbing makes the pointer drive it. One code path, perfect sync by construction, and scrubbing is first-class rather than bolted on.

```
CONDUCTOR (per frame, dt = frame time)
states: STOPPED | PLAYING | PAUSED | SCRUBBING

if state == PLAYING:   playhead += dt * bpm / 60
if state == SCRUBBING: playhead = target_from_pointer   (see II.4)
clamp playhead to [0, total_beats]; if PLAYING reaches end -> STOPPED (+ on_complete)

crossings = note regions whose start boundary lies between prev_playhead and playhead
            (in either direction; a region = [start_beat, start_beat + duration_beats))
for each crossing, in traversal order: AUDIO.trigger(note)   (flurry cap, see II.4)
active_note = region containing playhead (or none)
prev_playhead = playhead
```

Frame-edge triggering nuance (binding): a note triggers when the playhead enters its region — crossing its start boundary moving forward, or crossing its end boundary moving backward (so backward scrubs hear each note as it is entered from the right). Jump-to (a timeline click) sets the playhead without triggering anything except the region it lands inside (trigger that one; it feels dead otherwise).

## II.2 The Audio Engine

A thin voice-pool over the chosen audio library (candidate pygame.mixer; all specifics verified in Milestone 0, see II.8):

    All of a spell's samples are decoded to raw buffers at pack load (never during play). Estimated worst case: Lab superset ≈ 3 instruments × ~37 notes ≈ 111 buffers of a few seconds — comfortably in RAM.
    Voice pool of 16 voices. trigger(note): allocate a free voice, set gain from JSON, play the buffer from its start, let it ring to natural decay (no artificial cutoff at duration_beats — real instruments overlapping is warm, not wrong).
    Voice stealing: if the pool is full, steal the oldest voice with a fast fade (~10 ms). This, not silence-cutting, is what keeps fast scrub flurries clean.
    Feedback sounds: the soft consonant confirmation and the completion replay use the same engine — the confirmation is simply the target note's own sample at low gain, optionally with the note a fifth below it at even lower gain (consonance from the spell's own voice; no foreign sound palette).
    Latency budget (binding target): trigger-to-audible ≤ 30 ms on Nir's PC (well under the book's 50 ms bar), because scrubbing feel dies with latency. Achieved by small mixer buffer (try 256 samples, then 512), verified in Milestone 0.

## II.3 Note regions, hysteresis, and the flurry cap (scrub feel)

These constants live in one tuning file, player/data/scrub_tuning.json, so DeepSeek can tune by ear with Nir without touching code:

```json
{
  "boundary_guard_fraction": 0.04,
  "max_triggers_per_frame": 4,
  "steal_fade_ms": 10,
  "retrigger_min_ms": 90,
  "highlight_decay_ms": 300
}
```

    Boundary guard (hysteresis): each region's trigger boundary is inset by boundary_guard_fraction of the region's width. A handle resting exactly on a boundary therefore cannot machine-gun two notes by ±1-pixel jitter: you must travel measurably into a region to fire it, and measurably out to re-arm it.
    Lingering: while the playhead stays inside one region, nothing retriggers — the note rings and decays naturally. Leaving and re-entering fires it again, but never sooner than retrigger_min_ms since that same note's last trigger (protects against violent micro-wiggles).
    Flurry cap: if one frame's motion crosses more than max_triggers_per_frame regions, trigger only the last K in traversal order (the ear reads a fast swipe as a gesture ending where the hand stops; the final notes matter most). All crossed regions still flash visually — the eye can follow what the ear summarizes.

## II.4 The two scrub surfaces

Both drive the same Conductor; both are Player-M mouse territory (BIBLE §5):

    Timeline scrub: the transport bar maps linearly, pixel-x ⇒ playhead_beats across [0, total_beats]. Drag = SCRUBBING; release = PAUSED at that spot (LOCKED: releasing does not auto-resume; the wine taster decides when to sip again). Click without drag = jump.
    Graph scrub: inside the plot rectangle, normalized pointer-x is located in the graph_segment tiling: find the note whose segment contains it, then interpolate linearly within that segment to a beat inside that note's region. Because segments tile [0,1] exactly (Compiler Stage 10), the whole curve is a continuous playable surface — the finger literally drags along the function. The playhead cursor is drawn on the graph (a thin vertical line) and on the timeline simultaneously, always in agreement.
    Keyboard-driven transport (Player K): Space = play/pause; left/right arrows = nudge-scrub in small fixed steps (one region per tap; holding = smooth slow scrub at a fixed gentle velocity). This gives K a genuine "sound engineer" instrument without a mouse.

## II.5 The Music Bench widgets

Piano keyboard. Geometry generated from keyboard.low_note/high_note: white keys as equal rectangles across the bench width; black keys as narrower, shorter rectangles overlaid at the conventional positions (pattern per octave: black after C, D, F, G, A). Hit-testing checks black keys first (they sit on top). Key states: idle, hover, pressed (mouse down — sounds immediately), lit (playback/scrub highlight, decays over highlight_decay_ms), committed-flash (brief warm flash on correct OK). The key→pitch map is pure lookup: midi = midi(low_note) + key_index.

Staff renderer. Deliberately minimal notation, fully data-driven from notation_table.json:

    Draw 5 lines (treble) or two groups of 5 (grand) with baked clef PNGs at the left.
    Each note = an ellipse notehead at vertical position derived from staff_step (half a line-gap per step), plus a sharp glyph PNG to its left when accidental == "sharp", plus short ledger lines when the step falls outside the lines. No stems, beams, or rhythm notation — LOCKED: noteheads only, matching Nir's "simple individual note, not connected or complicated."
    Horizontal layout: N equal slots across the staff width (target melody positions). Confirmed notes are solid; the current provisional note is hollow; future slots show faint placeholder dashes so players always see how many notes remain.

Transport. Play/Pause button (icon swaps), timeline groove + handle, playhead time readout in beats and seconds. Fixed pixel rectangles, defined once in a layout constants module (1280×720, LOCKED positions; the parent chat owning UI freezes exact coordinates in its spec).

OK / Cancel. Fixed-position buttons; also bound to Enter / Backspace for M-side keyboard users in solo play (through the input-action layer, as everything must be).

## II.6 The Echo Puzzle controller (state machine)

```
states: INTRO -> LISTEN -> INPUT -> CHECK -> (INPUT | ADVANCE) -> ... -> COMPLETE

INTRO:    show intro_text; Conductor loaded with the spell; prefix_len = 1 (grow) or N (whole)
LISTEN:   auto-play notes [0, prefix_len); free transport/scrub at all times afterwards
INPUT:    cursor at first unconfirmed slot; key clicks audition + set provisional note
CHECK:    on OK: if provisional.midi == target.midi -> consonant confirm, solidify, ADVANCE
          else -> gentle fade of provisional; show hint_higher/hint_lower
          (chosen by integer comparison); stay in INPUT
ADVANCE:  if all slots in prefix confirmed:
             grow: prefix_len += 1; replay new prefix (LISTEN) with confirmed notes lit
             whole/last: COMPLETE
COMPLETE: full replay with all visuals; success_text; return control to story flow
```

Binding details: the transport and both scrub surfaces remain live in every state (Forgiving Forever — the player may re-listen mid-input at any time; scrubbing does not disturb the input cursor). Cancel clears only the provisional note. There is no counter of wrong attempts anywhere in memory — nothing to shame, nothing to log.

## II.7 The visual sync bus, helix, and Lab wiring

    Sync bus: each frame the Conductor publishes (playhead_beats, active_note_index, recent_triggers). Graph, helix, keyboard, and staff each render from that — no component talks to another; all sync flows through the Conductor. Highlights decay over highlight_decay_ms for a warm afterglow rather than a hard blink.
    Helix renderer: polyline of the spiral (≤ turns full circles, ~64 segments per turn), plus one marker sphere per note at (angle_deg, z). Software transform: slow default auto-rotation about the vertical axis (~6°/s), orthographic projection with a fixed gentle camera tilt (~20°) — the honest 90s-demoscene look. Player K's [/] (or equivalent actions HELIX_ROTATE_L/R) override the auto-rotation while held. Markers are always drawn after (on top of) the wire so rotation never hides information (BIBLE §13).
    Laboratory wiring: slider changes call the frozen remap of Part I.4, producing a fresh note list + visuals in place; the Conductor keeps the playhead's fractional position (a change of tempo or note-count does not throw the listener to the start). Slider changes during PLAYING are applied at the next region boundary; during SCRUBBING, immediately.

## II.8 Build order and risk-retirement milestones

Binding sequence for the parent/child chats (each milestone is demonstrable to Nir by ear/eye):

    M0 — Latency & MP3 spike (DeepSeek, before any real code): a 50-line throwaway app: load 5 Philharmonia MP3s, click to trigger, try mixer buffer 256/512, measure/feel latency; confirm MP3 loading reliability on Nir's Windows machine. Output: a short report + the go/no-go on MP3 (fallback: compile-time OGG/WAV conversion, pre-approved). This single spike retires the project's two biggest unknowns.
    M1 — Conductor + Audio Engine against a hand-written fixture spell JSON with generated beep samples: play, pause, jump, timeline scrub, flurry cap, hysteresis. Nir test: "drag fast, drag slow, drag backward — does it feel like touching the melody?"
    M2 — Bench widgets (keyboard, staff, transport, OK/Cancel) + sync bus + graph scrub surface.
    M3 — Echo controller (grow + whole) end-to-end on fixtures; then on one real compiled spell.
    M4 — Helix renderer and Puzzle Mode composition (graph + helix + equation PNG).
    M5 — Story Mode (slides, dialogue trees, Choice puzzles) — lowest risk, done late deliberately.
    M6 — Laboratory (sliders + live remap + superset audio).
    M7 — Pack loader/validator, save file, main menu, input-mapping config (the joystick/controller skeleton).

## II.9 Player testing strategy

    All logic modules (Conductor crossings, hysteresis, remap arithmetic, notation lookup, state machine) are pure functions or plain classes with no rendering or audio imports, tested headless with pytest against fixture JSONs — child chats can prove correctness before DeepSeek ever opens a window.
    Scrub feel is explicitly excluded from automated tests and assigned to the scrub_tuning.json + Nir's-ear loop.
    One integration fixture pack (packs/_fixture/) with 2 scenes, 1 echo, 1 choice, 1 lab spell, beep audio — the permanent regression playground.

## II.10 Open engineering items (all DeepSeek's, none Nir's)

    MP3 decode reliability and trigger latency on the real machine (M0). 2. Meaning of the Philharmonia filename numeric token and the variant-preference ranking (library_profile.json). 3. Final scrub tuning constants. 4. Whether pygame vs pygame-ce (or fallback) — decided by M0/M1 evidence, reported back so the BIBLE's §14 recommendation is confirmed or amended.

End of the LOOM NEW TESTAMENT v1.0 — Claude Fable. 🌀

---

## 🕊️ YOUR OWN M2 LEGACY WILL (from Parent 3 — you, one life ago)

PARENT 3 (Fable) — LEGACY SUMMARY (July 2026, M2: THE MUSIC BENCH)

Delivered (all code, landed + tested):
1. core/notation.py [MEAT] — frozen notation_table.json format v1.0
   (in its docstring: 0=middle line, +1=letter up, sharps share their
   natural's step); additive midi_for_name (Nir-approved).
2. ui/input_actions.py [MEAT] — InputMapper = KEY events only;
   ROUTING DOCTRINE: pointer events flow raw to widgets.
3. ui/layout.py — rev 2: full-width staff + keyboard; still
   PROVISIONAL until Nir's final eye pass, then freeze.
4. ui/bench_keyboard.py [MEAT] — C-anchored, 1-2 octaves, black-first
   hit-testing, glow levels, preview outline, PRESSED visual (rev 2).
5. ui/bench_staff.py [MEAT] — noteheads only, pure table lookups;
   NIR'S AMENDMENT: always FULL GRAND STAFF (bass iff midi<60).
6. ui/bench_transport.py [MEAT, rev 3] — m1_demo's ear-approved feel
   extracted UNCHANGED (3px threshold); + play/stop buttons; + BPM box
   (typed 40-200, Enter/Esc/click-away, spinners +/-1, .typing flag).
7. ui/graph_view.py [MEAT] — precompiled polyline; scrub surface #2
   via segment tiling; pure u_to_beats/beats_to_u; degrades gracefully.
8. fixtures/make_bench_fixtures.py — design-time generator (math OK
   there): fixture_bench8 (line/violin) + fixture_bench16 (sqrt/cello,
   chromatic, 2 octaves); canonical midpoint tiling; bpm 110.
9. m2_demo.py — Nir-accepted; helix placeholder panel (M4's chair).
10. Tests: notation, m2 widgets, input mapper, bench fixtures, length
    choice, transport BPM (+ conductor set_bpm tests via DeepSeek).

Doctrine amendments made (Commentaries par.5):
- FULL GRAND STAFF always (Nir, supersedes "grand only when needed").
- FIT-THE-BEAT selection law refinement (the ghost-pedal fix): uniform
  token = longest <= shortest note duration in seconds; binding on
  Compiler Stage 8; Forge's sharpened goal = beat-length sustained
  samples with natural release.
- Content default tempo = 110 BPM.
- Conductor.set_bpm added (additive MEAT change, Nir-approved; also
  pre-work for M6 Lab). TransportCommand.SET_BPM + TransportEvent.bpm.
- OPEN for Nir: raise BIBLE par.7.2 num_notes max 16 -> 20?
  (Widgets are already N-agnostic.)

Handed to Parent 4 (M3, THE ECHO) in my final messages:
- ui/bench_buttons.py — WRITTEN, ready to land (BenchButton with
  pressed visual; OK/Cancel widget born in M3 as approved).
- M3 design sketch: pure echo state machine (preview/commit/cancel/
  reset; slots solid/hollow/dashed), unlimited gentle retries, staff
  gains ADDITIVE optional echo arg, reward playback on completion.
- Nir's three open Echo questions (wrong-commit feedback; auto-sound
  on correct commit; strict slot order) — defaults proposed.

