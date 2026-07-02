Nir, your text arrived perfectly this time! 🙂 And I have to tell you honestly: your answer to question 6 corrected a real mistake of mine. I parked the laboratory out of caution about my own "no math at runtime" rule — but your Descartes argument is exactly right, and it exposes that my rule was drawn slightly in the wrong place. The point of a coordinate system is that you wander it — your eyes linger, skip, return. A sonification you can only hear at one fixed speed, in one direction, is a horse in blinders. So scrubbing is now a pillar, not a feature. (One honest note: my chapter summaries of Sounding the Unknown don't explicitly record the scrubbing passage — my memory of the book is only those summaries — but it doesn't matter: it's now doctrine by your decision, and it fits the book's interactivity chapter perfectly.)

One important design consequence I want you to know about, because I chose deliberately: of Wikipedia's three scrubbing techniques, we must not use resampling (the tape/vinyl style that bends pitch), because in our system pitch IS the data — a chipmunk-pitched scrub would literally lie about the mathematics. Instead we scrub by retriggering the real notes as the playhead crosses them (a note-level cousin of "cut-and-paste" scrubbing). Drag slowly and each note rings and lingers; drag fast and the melody flutters by; drag backward and you hear the function right-to-left. Pitch — the meaning — is always true.

Since the changes touch many sections, I'm reissuing the complete BIBLE as v1.1. This document fully replaces v1.0 — please save only this one and hand only this one to future parents.

# 📜 THE LOOM BIBLE — v1.1

The founding doctrine of LOOM, a Peak Together Arcade title.
Written by Claude Fable (founding architect). This version fully replaces v1.0. Every future architect (Opus parent chat) must read this document in full before designing anything. Where it says LOCKED, do not reopen the decision. Where it says OPEN QUESTION, ask Nir — never invent an answer.

Changelog v1.0 → v1.1 (all by Nir's decision): the two heroes are named Girlfriend and Boyfriend; silence between puzzles is locked; the dark/tension palette is permanently parked; shipped audio is MP3, verbatim Philharmonia files with original filenames; window locked at 1280×720; the Laboratory is IN for v1, with live sliders; Scrubbing is added as a core pillar and a universal transport feature; the "dumb runtime" doctrine is refined to permit simple arithmetic on precompiled numbers (still no function evaluation at runtime); spell schema extended accordingly.

## 0. How to read this document, and the Iron Rules you inherit

LOOM is built by an assembly line: Nir (the human boss; he does not read code or math — he pastes, runs, installs, generates images, renders LaTeX, and judges by eye and ear), Claude Fable (founding architect; output is documents), Opus "parent" chats (each designs one area in depth, starting from this BIBLE), "child" chats (each implements one frozen module), and DeepSeek (agentic access to Nir's Windows PC and the repo github.com/strulovitz/peaktogether-website; stitches code, runs tests, fixes bugs, pushes).

Iron Rules, inherited by every future document:

    Honesty first. Invent nothing. Mark undecided things as OPEN QUESTIONS. Never assert external library or file-format details from memory as certain — define our own conventions and let DeepSeek's compile/test loop confirm externals on the real machine.
    Never use Markdown tables in anything copy-pasted between chats (cells get destroyed in transit). Use prose, bullet lists, and fenced code blocks.
    Nothing may require Nir to understand code or math. His actions are mechanical.
    Tone: warm, friendly, romantic, encouraging. Wrong answers are never punished; they earn a gentle explanation. No game over, no shaming scores, no timers.
    Priority split: ~90% education, ~10% entertainment. When in doubt, choose what teaches better.

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

## 4. The Laboratory (LOCKED IN for v1)

From the main menu (and offered after puzzles), any spell the players have met opens in the Lab: the full Puzzle Mode visuals plus a slider panel. Everything responds live:

    Tempo (BPM) — continuous.
    Pitch span (target_span_semitones, up to 24) — continuous; the melody stretches or squashes vertically, and the graph/helix markers move with it.
    Base note — stepped.
    Scale — cycles pentatonic major / major / natural minor / chromatic.
    Instrument — among the instruments the pack ships for Lab use.
    Number of notes (4–16) — resamples the melody from the spell's dense precompiled values: fewer notes = the gist; more notes = finer detail. This is "zooming the graph, by ear."
    Plus the transport and full scrubbing, always.

How this respects the architecture: the Compiler ships, inside each Lab-enabled spell, a dense array of already-conditioned raw values (lab.dense_values, e.g., 200 points). Moving a slider re-derives the note list by simple arithmetic on those numbers — multiply by the span factor, snap to the scale set, look up the sample. No function is ever evaluated at runtime (see §10 for the refined doctrine). The Compiler also ships every sample any slider combination can reach (bounded: at most a couple of octaves, chromatic, per Lab instrument).

The Lab is silent between interactions, has no goals, no scores, and no wrong answers. It is the wine-taster's quiet room.

## 5. Co-op & Solo

Division of labor (LOCKED):

    Player K (keyboard; future joystick) — canonically Boyfriend: drives the plot. Slide next/back, dialogue menus (arrows + Enter), Choice Puzzle answers. Also owns keyboard bindings for the transport (Space = play/pause, arrow keys = seek/nudge-scrub), so during Echo puzzles K is the "sound engineer": M says "again, slower, from the middle," and K obliges.
    Player M (mouse; future Xbox controller) — canonically Girlfriend: drives the education. Piano keys, OK/Cancel, transport by mouse, and — especially — scrubbing is M's instrument: her hand's speed is the performance.

Why you must talk to win (design intent, LOCKED): the story and dialogue (K's domain) carry the hints about what to listen for; the listening (M's domain) carries the answers to K's Choice menus. Story Weavers must build at least one moment per scene where each player needs something only the other has.

Solo play (LOCKED): every control is mouse-operable (on-screen arrows, menus, transport), so one person with a mouse can play everything. Keyboard bindings are a mirror, not a requirement.

Input abstraction (LOCKED architecture requirement): all input routes through a named-action layer (STORY_NEXT, MENU_UP, MENU_SELECT, TRANSPORT_PLAYPAUSE, SEEK_FORWARD, …, plus pointer events), with device→action mapping in one config file, so DeepSeek can later add joystick (K) and Xbox controller (M) by editing only that layer.

## 6. The Content Model: Problem Packs and the Assembly Line

LOOM is generic: the Player is a frozen black box; all content lives in Problem Packs, produced forever by anyone using the frozen tools and prompts. Nir will make a few packs as website examples.

The two heroes (LOCKED): they are named, on screen and in all dialogue, simply Girlfriend and Boyfriend — never given personal names. Rationale (binding for tone decisions): named characters ("Alice and Bob") make players watch somebody else; "Girlfriend and Boyfriend" lets every real couple at home pour themselves into the roles — and gently nudges a shy pair on a Peak Together date night toward seeing each other romantically. Image prompts describe them physically (two ~18-year-old explorers in modern clothes, warm and friendly) consistently across scenes, but text never names them.

How one pack is born (the frozen pipeline):

    Nir opens a fresh Opus child chat with the fixed Story Weaver prompt (future deliverable; this BIBLE defines its output contract, §9). The prompt makes the child ask Nir for a Wikipedia page; Nir pastes one (e.g., Square root).
    The child reads the page — especially its history section (Babylonians, Egyptians, ancient India, Greeks…) and its properties/uses section (real intuitive applications, e.g., "the square root maps the area of a square to its side length") — and invents a short, warm, fictional-but-plausible everyday story in a historical setting (a ruler commissions a building; the site hits a constraint; the local sage reveals the function). About 3 scenes, slide-presentation style, static images only.
    Per scene it outputs: caption/narration; a dialogue tree (~4 options per node, all pre-written — no AI at runtime, ever); an image prompt (cute Disney/Pixar 3D style, Girlfriend and Boyfriend talking with period characters, everything else period-authentic); LaTeX strings; spell specs for the puzzles.
    Nir generates images (paste prompt into an image-AI chat → save PNG) and renders LaTeX to PNGs with his local MiKTeX (as in previous games).
    The Spell Compiler is run on the spell specs (by Nir mechanically or by DeepSeek): it computes notes, precomputes visuals and dense Lab values, and copies exactly the needed audio.
    DeepSeek assembles the pack folder, validates against the schemas, tests in the Player, pushes to GitHub.

Understanding Mode: LOCKED OUT. LOOM does not include the four-level explanation feature from other Peak Together games. Teaching lives in story, dialogue, synced visuals, scrubbing, and success texts.

## 7. The Sonification Engine (the heart)

All of this runs inside the Spell Compiler, offline. The Player only ever sees the finished data.

### 7.1 The pipeline (LOCKED, adapted from the book)

    Sample the domain. [xmin, xmax], N notes (4 ≤ N ≤ 16, default 8), uniform by default (xi = xmin + iΔx) or an explicit point list when a function's characteristic stretch needs hand-picked moments (the damped sine must show both oscillation and decay). Additionally, a dense pass (default 200 points) is always computed for the graph polyline and the Lab.
    Condition. Optional, in configured order: clamp to [lo, hi]; shift; compress blow-ups with sign(y)·log(1+|y|); smooth (moving average). (Book §5.2 rules.)
    Map to semitones (absolute mapping, LOCKED). θi = a·f(xi), semitones relative to the base note; either explicit pitch_scale_a or (recommended) target_span_semitones (auto-fits a; default 12, hard max 24 — the keyboard cap).
    Quantize to a scale. θi ← argmin over s ∈ ScaleSet of |θi − s|. Canonical scales: pentatonic_major {0,2,4,7,9} (default — no dissonant pairs, kindest to untrained ears), major {0,2,4,5,7,9,11}, natural_minor {0,2,3,5,7,8,10}, chromatic (advanced). Prefer base note C so the staff needs no accidentals; the Compiler warns otherwise.
    Rhythmic grid. Default flat rhythm — equal notes on the beat at the spell's BPM (default 90); flat = maximal memorability for beginners. Optional advanced layers: duration_from_magnitude (quantized to eighth/quarter/half) and rests at zero crossings.
    Dynamics. Default one fixed layer (forte). Optional from_magnitude / from_derivative, quantized to the dynamic layers that actually exist for that instrument in the sample library — an exponential spell genuinely swells as it leaps, with zero DSP.
    Timbre. LOCKED principle: discrete and secondary, never continuous. Our timbre axis = instrument choice per spell (default), dynamic layers as brightness proxy, and (advanced, post-v1) different instruments per voice separated by register and family. No filter DSP.
    Choose samples. For every note, one concrete file from the local Philharmonia library — the exact recorded pitch (no pitch-shifting ever; the library covers essentially every note of every instrument), nearest available dynamic, articulation normal by default. The Compiler also computes a per-note gain (volume multiplier) at compile time so notes are balanced, since files ship verbatim.
    Precompute all visuals and Lab data. Per note: graph highlight segment (normalized fractions of plot width); helix marker (angle = 30°×(θi mod 12); height z = θi/12, one octave = 1.0, matching the book's z = θ/(2π) normalization); keyboard key_index (= midi − midi(low_note)). Plus: the dense graph polyline (unit-box normalized) and the dense conditioned values for the Lab, so the Player never evaluates f.

### 7.2 The knobs (canonical names)

```
SPELL SPEC — compiler input knobs
--------------------------------------------------
spell_id                unique snake_case id
display_name            human name shown in-game
function                human-readable description; implemented in Python inside the spec
latex                   LaTeX string (Nir renders to PNG)
x_min, x_max            domain
num_notes               4..16, default 8
sample_points           "uniform" (default) or explicit x list
dense_points            default 200 (graph polyline + Lab values)
conditioning            ordered list: clamp(lo,hi) | shift(c) | log1p | smooth(k) | none
base_note               e.g. "C4" (prefer C-based)
pitch_scale_a           explicit a, OR:
target_span_semitones   auto-fit span, default 12, max 24
scale                   pentatonic_major (default) | major | natural_minor | chromatic
bpm                     default 90
rhythm_mode             flat (default) | duration_from_magnitude
dynamics_mode           fixed(forte) (default) | from_magnitude | from_derivative
instrument              Philharmonia instrument folder name, e.g. "flute"
articulation            "normal" (default)
lab_enabled             true (default) | false
lab_instruments         instruments available in the Lab for this spell
```

### 7.3 The sample library and the download-size strategy (LOCKED, revised)

Facts (per Nir): the Philharmonia library (free even for commercial use, philharmonia.co.uk) is organized as family zips (Woodwind, Brass, Percussion, Strings) containing instrument folders of 600–1300 MP3 files each, named like bass-clarinet_A2_1_forte_normal.mp3 — per note, per dynamic, per articulation, ~20 variants per note, essentially every pitch recorded at superb quality. Far too large to ship whole (Woodwind alone: 260 MB zipped).

The strategy:

    Ship only what each pack uses, as verbatim Philharmonia MP3 files with their original filenames (LOCKED). No transcoding, no renaming, no trimming. Rationale (Nir): our GitHub must never become a mirror of Philharmonia; and in a future "full orchestra" expansion, players can download the official zips themselves and drop them in — original filenames make our packs and their library speak the same language. A typical pack needs a few dozen files — a few MB.
    The full library lives only on the pack author's PC — a compile-time resource, like MiKTeX. The Compiler scans the actual files on disk (never trusts a remembered list), parsing names with a tolerant pattern: instrument, note+octave, numeric token (meaning to be confirmed empirically by DeepSeek — likely a length/variant code), dynamic, articulation. Selection rule: prefer normal articulation and a sustained-enough variant, confirmed by ear.
    The Player decodes MP3 at load time (not during play). If the chosen audio library proves unreliable with MP3 on Windows, the sanctioned fallback (pre-approved by Nir) is compile-time conversion to OGG or WAV — DeepSeek decides by testing, MP3-first.
    Future hook (design in the skeleton, minimal in v1): an optional library_dir setting pointing at a player's own downloaded Philharmonia folder, from which the Player can satisfy sample references that a slimmed pack doesn't bundle.

## 8. The Spell Format (canonical data model)

One JSON file per spell — the contract between Compiler and Player. Semantic versioning; the Player refuses newer major versions.

```json
{
  "format": "loom-spell",
  "format_version": "1.0",
  "spell_id": "sqrt_basic",
  "display_name": "The Rope-Stretcher's Melody",
  "function_text": "f(x) = sqrt(x) on [0, 9]",
  "equation_png": "latex/eq_sqrt_basic.png",
  "instrument": "flute",
  "bpm": 90,
  "scale": "pentatonic_major",
  "base_note": "C4",
  "keyboard": { "low_note": "C4", "high_note": "C5" },
  "staff": { "clef": "treble" },
  "notes": [
    {
      "index": 0,
      "note_name": "C4",
      "midi": 60,
      "start_beat": 0.0,
      "duration_beats": 1.0,
      "dynamic": "forte",
      "sample": "audio/flute_C4_1_forte_normal.mp3",
      "gain": 0.9,
      "key_index": 0,
      "graph_segment": { "x_from": 0.0, "x_to": 0.125 },
      "helix": { "angle_deg": 0.0, "z": 0.0 }
    }
  ],
  "graph": {
    "points": [[0.0, 0.0], [0.005, 0.07]],
    "x_label": "x",
    "y_label": "f(x)"
  },
  "helix_geometry": { "turns": 2 },
  "lab": {
    "enabled": true,
    "dense_values": [[0.0, 0.0], [0.045, 0.212]],
    "instruments": ["flute", "clarinet", "cello"],
    "span_semitones_range": [4, 24],
    "bpm_range": [40, 160],
    "base_note_range": ["C3", "C5"],
    "num_notes_range": [4, 16]
  },
  "required_samples": ["audio/flute_C4_1_forte_normal.mp3"],
  "compiler_version": "1.0",
  "notes_for_humans": "Rising staircase with shrinking steps — the ear hears the flattening."
}
```

Binding field meanings:

    notes is the melody in order; seconds = beats × 60/bpm and nothing more. midi is the unambiguous pitch; note_name feeds the staff renderer. gain is a compile-time-computed volume multiplier (files ship verbatim, so balancing happens here).
    key_index = midi − midi(keyboard.low_note); the keyboard draws all chromatic keys from low_note to high_note inclusive. staff.clef is treble or grand (rule: grand whenever any note is below C4).
    graph.points = the dense precomputed curve, unit-box normalized; graph_segment = each note's highlight span as fractions of plot width; also the scrub map (pointer x on plot ↔ playhead time).
    helix.angle_deg / helix.z: 30° per semitone of chroma; z rises 1.0 per octave.
    lab.dense_values = conditioned raw values, normalized to [0,1] vertically, on which the Lab's live arithmetic operates. required_samples covers everything reachable by any Lab slider combination, not just the default melody.

## 9. The Pack Format (scenes, dialogues, puzzles)

```
packs/square_root/
    pack.json          <- manifest: scenes, dialogue trees, puzzles
    spells/*.json      <- compiled spells
    audio/*.mp3        <- verbatim Philharmonia files, only those needed
    images/*.png       <- baked scene illustrations
    latex/*.png        <- baked equation images
```

```json
{
  "format": "loom-pack",
  "format_version": "1.0",
  "pack_id": "square_root",
  "title": "The Square Root",
  "source_url": "https://en.wikipedia.org/wiki/Square_root",
  "scenes": [
    {
      "scene_id": "scene_1",
      "image": "images/scene_1.png",
      "caption": "Babylon, long ago. The king dreams of a perfectly square garden...",
      "dialogue": {
        "start": "n1",
        "nodes": {
          "n1": {
            "speaker": "The King",
            "text": "My garden must cover exactly this much land. But how long is its side?",
            "options": [
              { "text": "O King, tell us more about your garden.", "goto": "n2" },
              { "text": "Perhaps your scribes have measured such things before?", "goto": "n3" },
              { "text": "May we hear the shape of this problem?", "goto": "END" }
            ]
          }
        }
      },
      "puzzle_after": "sqrt_echo_1"
    }
  ],
  "puzzles": [
    {
      "puzzle_id": "sqrt_echo_1",
      "type": "echo",
      "spell": "spells/sqrt_basic.json",
      "reveal_mode": "grow",
      "intro_text": "Listen: each step up is a little smaller than the last...",
      "success_text": "You heard it! The square root climbs forever, but ever more gently.",
      "hint_higher": "Yours was a little low - press play, or drag through it slowly.",
      "hint_lower": "Yours was a little high - press play, or drag through it slowly."
    },
    {
      "puzzle_id": "sqrt_vs_line",
      "type": "choice",
      "spells": ["spells/sqrt_basic.json", "spells/line_basic.json"],
      "labels": ["A", "B"],
      "show_graphs_before_answer": false,
      "question": "Which melody keeps climbing at the same steady pace?",
      "answers": [
        { "text": "Melody A", "correct": false, "explain": "A's steps kept shrinking - that gentleness is the square root." },
        { "text": "Melody B", "correct": true,  "explain": "Yes! Steady, even steps - that is the straight line." }
      ]
    }
  ]
}
```

Story Weaver content rules (binding): ~3 scenes; every image shows Girlfriend and Boyfriend (never otherwise named) talking with period characters, everything else period-authentic; dialogue menus of up to 4 options; at least one hook per scene that makes the couple talk to each other; historical settings drawn from the Wikipedia page's real history section; the fiction is invented and may gently say so ("our story is imagined, but the mathematics is real").

## 10. The Two-Program Architecture (refined doctrine)

    Program A — Spell Compiler (offline, author's PC): evaluates functions (numpy allowed), conditions, maps, quantizes, selects samples, computes gains, precomputes graph/helix/keyboard sync data and dense Lab values, writes spell JSON, copies verbatim MP3s, and emits a plain-text list of LaTeX strings for Nir. May be slow and dependency-heavy; only authors run it.
    Program B — LOOM Player (what every visitor downloads): reads the pack, blits PNGs, draws the Bench, plays samples at precomputed times, follows the scrub playhead, lights precomputed highlights, walks dialogue trees, and compares MIDI integers.

The refined "dumb runtime" rule (LOCKED): the Player performs no function evaluation and no symbolic mathematics, ever. It is permitted simple arithmetic on numbers the Compiler precomputed — beat-to-seconds conversion, MIDI equality/ordering for hints, playhead↔note-region lookup for scrubbing, helix rotation (presentation geometry), and the Laboratory's live remapping of dense_values (multiply by span, snap to a scale set, look up a sample). The forbidden thing is meaning-creation: the mathematics of what the function is lives only in the Compiler; the Player only rearranges numbers it was handed.

Why (unchanged rationale): determinism (every default spell is auditioned and hand-tuned at design time), robustness, performance (triggering preloaded samples sits comfortably under the book's 50 ms interactivity bar — which scrubbing makes even more important), and pipeline fit (child chats implement the Player against frozen JSON fixtures without touching sonification theory).

What crosses the boundary: only files — spell JSONs, pack.json, MP3s, PNGs. No code, no formulas, no network.

## 11. Curriculum: the Ear-Training Ladder

Binding guidance for pack authors, plus a reference spellbook shipped in the repo as demos and test fixtures.

    Tier 1 — Contour families: line (steady staircase) vs. sine (even arcs) vs. exponential (runaway leaps). Unconfusable after one listen.
    Tier 2 — Within-family cousins: parabola vs. exponential; square root vs. logarithm vs. line; sine vs. damped sine e−xsin(10x) (the book's signature example — arcs that quicken, fade, settle).
    Tier 3 — Parameters by ear: sin(x) vs. sin(2x); ex vs. e2x; amplitudes. Rhythm/dynamics layers may join here. The Lab's sliders are the natural teacher for this tier.
    Tier 4 — Advanced (post-v1, flagged only): two-channel spells (cycloid); two-voice f with f′ counterpoint (≤2 voices, separated by register and instrument family); co-op 3:4 polyrhythm "orbital resonance" encounters.

The confusability rule (binding): two spells required within the same scene or the same Choice Puzzle must differ audibly in at least one gross feature — contour class (up/down/arch/oscillation), number of direction changes, or total span — unless the puzzle's explicit teaching goal is that subtle distinction, in which case the intro text must say exactly what tiny difference to listen for. Never spring an un-signposted subtlety on the player.

Reference spellbook v1: line, parabola, square root, logarithm, sine, damped sine, exponential — tuned knobs, each with one sentence of "what the ear learns."

## 12. Emotional & Audio Design

The aesthetic: warm, acoustic, unhurried — real orchestral instruments playing simple melodies in pleasant scales; more "cozy museum at dusk" than "video game."

    Silence between puzzles (LOCKED). No ambient music, no background beds, anywhere. Rationale (Nir's, binding): this is a game of acute auditory perception — you don't put flashing lights between scenes of a game about optical illusions. The players are wine tasters; the spells must be the only wine on the table. All engineering love goes to the unique things, not run-of-the-mill game furniture.
    Feedback is consonance. Correct note → soft consonant confirmation; completed spell → the melody replayed warmly. Wrong note → no harsh sound, no buzzer, ever — only the gentle text nudge. We deliberately refuse dissonance-as-punishment.
    Mode as data, sparingly. A pack may render a negative-dipping function in a minor scale — the mode shift carries meaning (book Ch. 7). Only when it teaches.
    Tempo: spells live in the calm-to-moderate band (~70–110 BPM by default; the Lab lets players push wider themselves).
    The dark/tension palette (book Ch. 7 Part C — roughness, tritones, high-BPM dread): permanently parked (LOCKED). Documented in the chapter summaries for posterity; not part of LOOM.

## 13. Accessibility

    Dual coding everywhere (LOCKED): everything audible has a synchronized visual (graph + helix + key glow) and everything visual has a sound (any clicked key always sounds; any scrubbed position always sounds). Weak pitch discrimination → lean on the lights; weak vision → lean on the ears. "Even if the user does not understand anything, he can still play."
    Scrubbing is itself an accessibility feature: every listener gets the melody at their pace — slow it with your own hand, linger on the note you missed, replay two notes a hundred times. No one is dragged along at machine speed.
    Unlimited replays, no timers, no fail states.
    Highlights use color and brightness change (color-blind safe); the resting state is calm black-and-white for maximal contrast when something lights.
    Fixed layout, generous click targets (piano keys sized for imprecise mice), readable fonts. Helix rotation never hides markers.

## 14. Tech Stack & Repository Architecture

Recommendation (to be confirmed by DeepSeek's compile/test loop on Nir's actual Windows PC — per the Iron Rules, no external API is asserted as certain):

    Language: Python 3.11+, Windows-first, launched as python app.py, matching the rest of the Arcade.
    Player framework: pygame (or pygame-ce) as primary candidate — window, 2D drawing, PNG blitting, audio mixer, mouse/keyboard, and native joystick/gamepad support (serving the future controller work through the input-abstraction layer). Fallbacks if testing reveals blockers: pyglet, arcade.
    Audio: samples decoded at pack-load into memory; playback = triggering preloaded buffers (scrubbing demands consistently low trigger latency — this is the one performance-critical path and deserves early prototyping; see §16). MP3 loading to be verified; sanctioned fallback = compile-time OGG/WAV conversion.
    Helix rendering: software 3D — precomputed spiral polyline, simple rotation matrix, 2D projection, anti-aliased lines. Authentic 90s-demoscene wireframe. No OpenGL dependency.
    Compiler stack: Python + numpy; sample-library scanning; per-note gain analysis (any needed decoding at compile time only).
    Window: fixed 1280×720 (LOCKED). No responsive-layout effort.
    Repo layout: everything under loom/ — loom/player/ (with app.py), loom/compiler/, loom/packs/<pack_id>/, loom/docs/ (this BIBLE and successors), loom/prompts/ (the Story Weaver prompt when frozen).
    Saving: a small local JSON progress file (last scene per pack; spells unlocked for the Lab). No network access of any kind at runtime.

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

## 16. OPEN QUESTIONS

None requiring Nir's decision right now. 🎉 Two engineering uncertainties are assigned to DeepSeek's test loop, not to Nir: (1) reliable MP3 loading in the chosen Python audio library on Windows (fallback pre-approved), and (2) scrub-trigger latency and feel (hysteresis, polyphony cap, fade times — to be tuned by ear, with Nir listening).

## 17. Parked ideas (recorded, not designed)

Co-op 3:4 polyrhythm "orbital resonance" encounters; f+f′ two-voice counterpoint; brachistochrone race-by-ear flagship Choice Puzzle; microtonal detuned renderings; stereo-panned per-player voices; adaptive difficulty escalation; user-CSV sonification sandbox; the full-orchestra library_dir expansion; the dark palette (permanently).

End of the LOOM BIBLE v1.1 — Claude Fable, founding architect. 🌀
