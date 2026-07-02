Wonderful! 🙂 Here is Part 5 — the NEW TESTAMENT: the deep technical design of the two riskiest systems. It is a companion to BIBLE v1.1 (which remains the supreme authority — this document adds depth and never contradicts it; the few small additions it introduces are declared explicitly in "Addendum A" so nothing is hidden).

# 📖 THE LOOM NEW TESTAMENT — v1.0

Deep design of the two riskiest systems: (I) the Spell Compiler & sonification engine, and (II) the Player's playhead, scrubbing, audio, and Music Bench.
Companion to the LOOM BIBLE v1.1. Written by Claude Fable. Intended readers: the Opus parent chats that will own these areas, the child chats that implement modules, and DeepSeek. All Iron Rules of the BIBLE apply here (no tables, honesty first, OPEN engineering items assigned to DeepSeek's test loop, nothing requiring Nir to code).

Why these two are the riskiest: everything else in LOOM (slides, dialogue trees, menus, PNG blitting) is well-trodden ground that child chats can implement from the BIBLE alone. These two systems are where the project can genuinely fail: the Compiler is where all mathematics and all audio decisions live, and the Player's scrub/playhead engine is the beating heart of the "Wandering Ear" pillar — it is latency-sensitive, feel-sensitive, and touches audio, visuals, and input at once.

## ADDENDUM A — small additions to the BIBLE (declared deltas, not contradictions)

    A global notation table asset. To keep the Player free of music theory, the compiler toolchain generates once, offline, a static data file player/data/notation_table.json covering MIDI 36–96. For each MIDI number it stores: canonical note name (sharps convention: C, Cs, D, Ds, E, F, Fs, G, Gs, A, As, B + octave), the staff step (vertical diatonic position) in treble and in bass clef, and whether a sharp accidental glyph is needed. The Player renders notation purely by lookup. This also makes the Laboratory's live remapping able to draw any note without per-spell data.
    Compiler audition outputs. For every compiled spell, the Compiler also writes a preview.wav (the melody rendered by naive concatenation of the chosen samples) and a human-readable compile_report.txt, so Nir can audition and approve each spell without launching the game, and paste the report to DeepSeek if something sounds wrong.
    Fixture library convention. The repo carries a tiny fake sample library (fixtures/fakelib/) of generated, correctly-named audio files, so all compiler and player tests run on any machine without the real Philharmonia download.

# PART I — THE SPELL COMPILER (Program A)

## I.1 Shape of the tool

A command-line Python tool, run by Nir mechanically or by DeepSeek:

```
python compile_spell.py <spec_file.py> --library <path to Philharmonia root> --out <pack folder>
```

Outputs into the pack folder: spells/<spell_id>.json, copied verbatim MP3s into audio/, preview/<spell_id>_preview.wav, compile_report.txt (appended per spell), and LATEX_SNIPPETS.txt (appended: spell_id + LaTeX string, for Nir's MiKTeX step).

Determinism requirement (binding): identical spec + identical library ⇒ byte-identical JSON (stable key order, fixed float formatting at 6 decimal places). This makes golden-file testing and hand-tuning trustworthy.

Error policy (binding): the Compiler never silently degrades. Every failure (missing sample, span overflow, empty scale set…) halts with a plain-language message a non-programmer can paste to DeepSeek, e.g. ERROR: instrument 'flute' has no sample for note Gs5 at dynamic 'forte'. Nearest existing: G5, A5. Fix: change base_note, reduce target_span_semitones, or pick another instrument.

## I.2 The spec file format

A spec is a tiny Python file — because the function itself must be real executable math, and because Story Weaver child chats can write Python. Canonical shape:

```python
# spec for LOOM Spell Compiler
import math

def f(x):
    return math.sqrt(x)

SPEC = {
    "spell_id": "sqrt_basic",
    "display_name": "The Rope-Stretcher's Melody",
    "function_text": "f(x) = sqrt(x) on [0, 9]",
    "latex": r"f(x) = \sqrt{x}",
    "x_min": 0.0, "x_max": 9.0,
    "num_notes": 8,
    "sample_points": "uniform",          # or an explicit list of x values
    "dense_points": 200,
    "conditioning": [],                   # ordered: ["clamp", lo, hi] | ["shift", c] | ["log1p"] | ["smooth", k]
    "base_note": "C4",
    "target_span_semitones": 12,          # OR "pitch_scale_a": 15.0 (exactly one of the two)
    "scale": "pentatonic_major",
    "bpm": 90,
    "rhythm_mode": "flat",
    "dynamics_mode": ["fixed", "forte"],
    "instrument": "flute",
    "articulation": "normal",
    "lab_enabled": True,
    "lab_instruments": ["flute", "clarinet", "cello"],
    "lab_ranges": {
        "span_semitones": [4, 24],
        "bpm": [40, 160],
        "base_note": ["C3", "C5"],
        "num_notes": [4, 16]
    },
    "notes_for_humans": "Rising staircase with shrinking steps."
}
```

The Compiler imports the spec in a fresh process, validates every field against the BIBLE §7.2 knob list, and refuses unknown keys (typo protection).

## I.3 The pipeline, stage by stage (exact algorithms)

Stage 1 — Sampling. If sample_points == "uniform": xi = xmin + i·(xmax − xmin)/(N−1) for i = 0..N−1 (endpoints included). If explicit: use the list verbatim (must be sorted, inside the domain). Independently, the dense pass computes M = dense_points uniform samples for the graph polyline and Lab values. Evaluation failures (domain errors, NaN, infinity) at any point halt with a message naming the offending x.

Stage 2 — Conditioning. Applied in listed order to both the note samples and the dense pass (they must always agree):

    ["clamp", lo, hi]: y ← min(max(y, lo), hi)
    ["shift", c]: y ← y + c
    ["log1p"]: y ← sign(y)·ln(1 + |y|)
    ["smooth", k]: centered moving average, window k (odd), edges use shrunken windows

Stage 3 — Mapping to semitones. Let ymin, ymax be the min/max of the conditioned dense pass (not just the N notes — so Lab resampling can never escape the planned range). If target_span_semitones given: a = span/(ymax − ymin), and θi = a(yi − ymin), so θ ∈ [0, span]. Edge case: constant function (ymax = ymin) ⇒ all θi = 0, with a report warning. If explicit pitch_scale_a: θi = a·yi, then the whole set is rigidly shifted so min θi = 0; if the resulting span exceeds 24, halt with the fix-suggestions message.

Stage 4 — Scale quantization. Build the extended scale set: all values s = 12q + d for octaves q = 0..2 and degrees d in the chosen scale, keeping s ≤ span (always include 0). Snap: θi ← argmin_s |θi − s|; ties break downward (toward the lower note) — a fixed convention so builds are deterministic.

Stage 5 — MIDI and notation. midi_i = midi(base_note) + round(θ_i). Note names and staff data come from the same generator that builds notation_table.json (single source of truth for notation). Keyboard window rule: low_note = the C at or below the lowest note; high_note = low_note + 12 if everything fits in one octave, else low_note + 24; if even that fails, halt. Staff rule: clef grand iff any midi < 60 (below C4), else treble.

Stage 6 — Rhythm. flat: start_beat_i = i, duration_beats_i = 1.0. duration_from_magnitude: normalize |yi| over the notes to [0,1], quantize to {0.5, 1.0, 2.0} beats by thirds of that range; start_beat is the running sum. (Zero-crossing rests are a documented extension, not v1 default.)

Stage 7 — Dynamics. fixed(d): all notes get d. from_magnitude / from_derivative: normalize the driving quantity to [0,1] over the notes (derivative estimated by central differences on the dense pass, sampled at the xi), then quantize onto the ordered list of dynamics actually available for this instrument in the scanned library (Stage 8 supplies availability). Canonical dynamic order, for reference: pianissimo, piano, mezzo-piano, mezzo-forte, forte, fortissimo — but only the subset found on disk is ever used.

Stage 8 — Library scan and sample selection. On startup the Compiler walks --library, indexing every audio file by a tolerant filename parse:

```
Expected shape (to be confirmed on real files by DeepSeek):
<instrument>_<note><octave>_<token>_<dynamic>_<articulation>.mp3
e.g. bass-clarinet_A2_1_forte_normal.mp3

Parse rules (binding conventions for OUR index, whatever the files turn out to mean):
- instrument: leading segment up to first underscore (may contain hyphens)
- note: letter A-G, optional 's'/'#' for sharp (accept both spellings), then octave digit
- token: kept opaque as a string; its meaning (likely a length/variant code) is
  confirmed empirically by DeepSeek; the index stores all variants
- dynamic and articulation: trailing segments
- files that do not parse are logged to the report and skipped, never fatal
```

Selection per needed (instrument, midi, dynamic): filter to articulation == "normal" (or the spec's choice); among variants, prefer the one DeepSeek's empirical check marks as the standard sustained variant (this preference is a single ranked list in a config file, library_profile.json, produced once by DeepSeek by listening/inspection — the Compiler never guesses). Missing note ⇒ halt with the fix-suggestions message. Never pitch-shift.

Stage 9 — Gain computation. Each selected file is decoded once at compile time; compute RMS over its first second (post 10 ms); gain = clamp(target_rms / rms, 0.25, 1.0) with a fixed target_rms constant tuned once by ear against a reference sample. Gains are baked into the JSON; files ship verbatim.

Stage 10 — Visual precompute. Graph: dense polyline normalized to the unit box with 5% padding on y (x fills [0,1]). Per-note graph_segment: boundaries are midpoints between consecutive xi in normalized x (first segment starts at 0, last ends at 1) — so segments tile the plot exactly and double as the scrub map. Helix: angle_deg = 30 × (round(θ_i) mod 12), z = round(θ_i)/12; helix_geometry.turns = ceil(span/12).

Stage 11 — Lab data. lab.dense_values: the conditioned dense pass, x normalized to [0,1], y normalized so [ymin, ymax] → [0,1]. required_samples superset: for every Lab instrument, every chromatic MIDI from midi(lowest base_note) to midi(highest base_note) + max span, at the Lab's fixed dynamic forte (binding: the Lab always uses forte, to bound the superset). Halt if any Lab instrument lacks a reachable note; the message suggests narrowing lab_ranges.

Stage 12 — Emit and audition. Write the JSON (BIBLE §8 schema), copy MP3s, render preview.wav (samples placed at their start times, gains applied, truncated at next-note start + 1.5 s tail, peak-limited), append the report: every note as a line i=0  x=0.00  y=0.000  theta=0.0  -> C4 (midi 60, forte, gain 0.90, file flute_C4_1_forte_normal.mp3), plus warnings. Nir's approval loop is: listen to preview.wav, look at nothing else, say yes/no.

## I.4 The Lab remap contract (the arithmetic the Player is allowed)

This is the exact procedure the Player's Laboratory performs live; it is frozen here so both programs agree forever. Inputs: dense_values (list of [xnorm, v], v ∈ [0,1]), sliders num_notes N, span S, base_midi B, scale, instrument.

```
1. indices: pick N evenly spaced indices over dense_values (first and last included)
2. for each picked value v:  theta = S * v
3. snap theta to the extended scale set of `scale` within [0, S]  (ties downward)
4. midi = B + theta_snapped
5. sample key = (instrument, midi, "forte")  -> lookup in loaded pack audio
6. start_beat = i ; duration_beats = 1.0 ; visuals: angle = 30*(theta mod 12), z = theta/12,
   graph segments = uniform tiling by N, staff via notation_table.json
```

No other computation is permitted in the Player. (This is multiplication, rounding, snapping, and lookup — the BIBLE §10 doctrine.)

## I.5 Compiler testing strategy

    Fixture library: fixtures/fakelib/ mimics the real folder structure with tiny generated tones named exactly per the filename convention (a child chat generates them with a script; they can be sine beeps — they exist to test plumbing, not beauty).
    Golden files: 3–4 reference specs (line, sine, damped sine, sqrt) compiled against the fixture library, with the resulting JSONs committed; tests assert byte-identity.
    Property checks: every emitted midi within keyboard window; segments tile [0,1]; θ within span; all required_samples exist in output; report contains one line per note.
    The real-library smoke test (parse rate of the actual Philharmonia folders, selection sanity) is DeepSeek's, run on Nir's PC, results pasted back as library_profile.json + a summary.

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
