Thank you, Nir! 🙂 These answers change the design significantly — and for the better. The Simon insight is genuinely brilliant (it removes the "you must be a musician" barrier completely), and the generic Problem-Pack pipeline makes LOOM not one game but a game factory. Everything below reflects your answers faithfully. Here is the BIBLE.

# 📜 THE LOOM BIBLE — v1.0

The founding doctrine of LOOM, a Peak Together Arcade title.
Written by Claude Fable (founding architect). Every future architect (Opus parent chat) must read this document in full before designing anything. Where this document says LOCKED, do not reopen the decision. Where it says OPEN QUESTION, ask Nir — never invent an answer.

## 0. How to read this document, and the Iron Rules you inherit

LOOM is built by an assembly line: Nir (the human boss, who does not read code or math — he pastes, runs, and judges by eye and ear), Claude Fable (founding architect, documents only), Opus "parent" chats (deep design of one area each, starting from this BIBLE), "child" chats (implement one frozen module each), and DeepSeek (agentic access to Nir's Windows PC and the GitHub repo github.com/strulovitz/peaktogether-website; it stitches code, runs tests, fixes bugs, pushes).

Every future architect inherits these Iron Rules:

    Honesty first. Invent nothing. Mark undecided things as OPEN QUESTIONS. Never assert external library or file-format details from memory as certain — define our own conventions and let DeepSeek's compile/test loop confirm externals on the real machine.
    Never use Markdown tables in anything that will be copy-pasted between chats (tables lose their cells in transit). Use prose, bullet lists, and fenced code blocks.
    Nothing may require Nir to understand code or math. His actions are mechanical: paste, run, install, generate images, render LaTeX, listen, look, approve.
    Tone: warm, friendly, romantic, encouraging. Wrong answers are never punished; they earn a gentle explanation. No timers that end the game, no "game over," no scores that shame.
    Priority split: roughly 90% education, 10% entertainment. When in doubt, choose the option that teaches better, not the option that is more "gamey."

### 0.1 Glossary (canonical terms — use these exact words everywhere)

    HSS — the Helical Sonification System from the book Sounding the Unknown: data → music via a pitch helix, a secondary timbre channel, and a discrete rhythmic time grid.
    Spell — one compiled sonification of one mathematical function: a short sequence of notes (typically 4–16) with all timing, sample references, and visual-sync data precomputed. A spell is a data file, not code.
    Spell Compiler (Program A) — the offline Python tool that turns a spell spec (function + knobs) into a spell JSON file plus its audio assets. All math happens here.
    LOOM Player (Program B) — the game itself: a generic Python desktop app (python app.py) that loads a Problem Pack and plays it. It performs zero mathematics at runtime (no function evaluation, no sonification math, no MP3 decoding, no LaTeX).
    Problem Pack — one self-contained content folder = one topic (e.g., "Square Root"). Contains scenes, dialogues, images, equation PNGs, spells, audio, and a manifest. The Player can load any pack; packs are made forever by anyone using the frozen tools and prompts.
    Story Weaver — the fixed prompt (a future deliverable) given to a fresh Opus child chat, which reads a Wikipedia page Nir provides and produces a pack's narrative content: ~3 scenes, dialogue trees, image-generation prompts, and LaTeX strings.
    Echo Puzzle — the core Simon-style puzzle: hear a spell, reproduce it on the on-screen piano keyboard.
    Choice Puzzle — the secondary puzzle type: hear two or three spells and answer a question about them via a dialogue menu (e.g., "which one grows faster?").
    Music Bench — the fixed bottom half of the screen: piano keyboard, musical staff, OK/Cancel, transport controls.
    Scene Stage — the top half of the screen: story image + dialogue in Story Mode, or graph + helix + equation in Puzzle Mode.
    Player K — the player on the computer keyboard (in Nir's canonical couple: the boyfriend). Future: joystick.
    Player M — the player on the mouse (canonically: the girlfriend). Future: Xbox controller.

## 1. Vision & Pillars

LOOM in one breath: A cozy two-player time-travel game where a young couple visits moments in history, meets the people who first needed mathematics, and solves their problems by learning to hear the shapes of functions — repeating each function's melody, Simon-style, on a piano keyboard, while watching the same melody light up a graph and a spiral of pitch.

Relationship to the 1990 game "Loom": LOCKED — we keep nothing but the name. No magic, no drafts, no Guild, no plot elements. The name is purely a nostalgia anchor meaning "a game whose puzzles live in sound, not in visual cues." Do not import lore, mechanics, or characters from the original, and do not design around it.

Which mountain LOOM teaches: LOCKED — LOOM is not tied to any specific Peak Together mountain. It teaches the basics used by many mountains: that every function has a shape, and that shapes can be heard — linear vs. exponential, periodic vs. damped, fast oscillation vs. slow. It is the ear-training foundation course of the whole Arcade.

The four pillars (LOCKED):

    Anyone Can Play (the Simon Principle). We never assume the player is a musician. Nobody is asked to describe a sound in words or to know note names. The interface is: hear it, see it light up, click the same keys. Even a player who understands nothing can succeed by memory and light-following — and the understanding grows underneath, by conditioning, exactly as the book's BRECVEMA framework predicts.
    Everything Under the Hood Is Shown. The equation (LaTeX-rendered), the graph, and the pitch helix are all on screen, and the currently sounding piece of each lights up in sync with the audio. Sound, symbol, curve, and geometry are one thing, experienced simultaneously. This is not decoration; it is the pedagogy.
    Built for Two. Player K drives the story and conversations; Player M drives the listening and the instrument. Neither can finish alone comfortably in co-op — the game is designed so they narrate to each other. Solo play remains fully possible (everything is also mouse-operable).
    Forgiving Forever. Unlimited retries, unlimited replays, a seekable timeline like a video player, no timers, no scores, no game over. A wrong note earns a gentle nudge ("a little higher — listen once more") and the offer to hear it again.

The player fantasy: you and your partner are two curious modern explorers (~18 years old, in modern clothes) who step into painted moments of history — Babylon, Egypt, Rajasthan, Greece — talk with kings, builders, and sages, and give them the gift of a function, learned by ear.

## 2. The Screen (frozen layout)

The window is a fixed-layout 16:9 desktop window (reference resolution 1280×720; see §14). LOCKED structure:

Top half — the Scene Stage. It has two modes:

    Story Mode: a full-width baked illustration (Disney/Pixar-style 3D render, generated at design time by an image AI from the Story Weaver's prompt, always showing the two explorers talking with the scene's historical characters). Below or over the image: a caption/narration text box, a dialogue box (speaker name + text), and a dialogue menu of up to 4 options. On-screen "◀ back" and "next ▶" arrows for slides.
    Puzzle Mode: three side-by-side elements — (1) the function graph: a low-resolution, deliberately simple 2D plot drawn from precomputed points (we are not building Mathematica 🙂); (2) the pitch helix: the signature visual of the game — a simple 3D spiral (90s-demoscene style, or wireframe if simpler), slowly rotatable, with one glowing marker per note of the spell placed at that note's angle and height; (3) the equation, displayed as a pre-baked PNG rendered from LaTeX at design time on Nir's PC. During playback, the sounding note's graph segment, helix marker, and piano key all light up in color and then return to normal — Simon's light bulbs, tripled.

Bottom half — the Music Bench (always in fixed positions):

    The piano keyboard along the bottom edge: a real chromatic piano-style keyboard (white and black keys), spanning one octave by default, two octaves maximum (LOCKED cap — this also caps every puzzle spell's pitch range at 2 octaves, which matches the book's guidance). Mouse-clickable. Clicking a key immediately plays that pitch with the same instrument as the current spell, so the player can compare by ear before committing.
    The staff above the keyboard: a real musical staff — five lines with a treble clef by default; when a spell's range requires it, a ten-line grand staff (treble + bass, each with its clef symbol on the left). When the player clicks a key, the corresponding note is drawn as a simple individual note symbol (no beams, no complexity) at the current position. Target-melody notes already confirmed remain visible.
    OK and Cancel buttons in fixed positions. OK commits the currently selected note and advances to the next position; Cancel clears the current selection.
    The transport ("remote control") in a fixed position: Play, Pause, and a seekable timeline — the player can click anywhere on the timeline to jump to that moment of the current spell's sound, exactly like VLC.

In Story Mode the Music Bench is visible but dimmed/inactive. LOCKED: nothing in the bench ever moves position; muscle memory is part of accessibility.

## 3. The Core Loop

### 3.1 The Echo Puzzle (the heart of the game)

    The story reaches a problem. The Scene Stage switches to Puzzle Mode: equation PNG, graph, and helix appear. A short intro text (from the pack) frames what to listen for, in plain friendly language.
    Listen phase. The game plays the spell (or its current prefix — see reveal modes below). As each note sounds: its segment of the graph glows, its marker on the helix glows, and its piano key glows — then all return to normal. The player may replay, pause, and seek freely at any time using the transport. There is no limit.
    Echo phase. The player clicks piano keys. Each click sounds immediately (audition). A provisional note appears on the staff at the current position. Clicking OK commits it; clicking Cancel clears it and the player tries another key. Unlimited tries.
    Feedback on OK (LOCKED behavior). If correct: the note settles solid on the staff with a soft, consonant confirmation sound, and the cursor advances. If wrong: no penalty — the note gently fades, and a friendly hint appears ("yours was a little lower than the melody — press play to hear it again 🌱"), with directional help (higher/lower) computed by the Player from precompiled data. The player simply tries again.
    Reveal modes (a per-puzzle setting in the pack):
        grow (default, the forgiving Simon): round 1 plays note 1; the player echoes it. Round 2 replays notes 1–2 with all the lights; already-confirmed notes stay locked on the staff, and the player enters only the new note. And so on until the whole spell stands on the staff.
        whole: the full spell plays, and the player enters all notes in order (for short spells and confident players).
    Completion. The full melody plays back once, beautifully, with all three visuals dancing in sync, followed by the pack's success text — which always connects the sound back to the idea ("hear how the steps got smaller and smaller? That's the square root flattening out").

### 3.2 The Choice Puzzle (the second puzzle type, LOCKED in)

The game presents two or three spells behind labeled buttons (A / B / C) on the bench. The players may play each any number of times (graphs may be hidden until the reveal, per pack setting). A question appears as a dialogue menu ("Which melody belongs to the curve that grows faster?") and Player K answers via the menu — which forces the couple to talk, because M has been doing the listening. Wrong answers get a gentle explanation and another try; right answers get the reveal (graphs shown, both spells replayed with visuals). This puzzle type directly implements the book's "comparative sonification" (the brachistochrone insight from Chapter 9).

### 3.3 Free Play (the laboratory, minimal v1)

From the main menu: any spell from any installed pack that the players have already met can be replayed freely — transport, keyboard, and visuals all live, no goal. This is the calm "study island." (Interactive sliders for pitch-scale/tempo are a parked stretch idea, not v1.)

## 4. Co-op & Solo

The division of labor (LOCKED, per Nir):

    Player K (keyboard; future joystick): drives the plot. Next/back slides, navigating dialogue menus (arrow keys + Enter), answering Choice Puzzles. Also owns keyboard bindings for the transport (Space = play/pause, arrow keys = seek) — so during Echo Puzzles, K becomes the "sound engineer": M says "play it again from the middle," and K seeks. This keeps K useful during puzzles and forces conversation.
    Player M (mouse; future Xbox controller): drives the education. The piano keyboard, OK/Cancel, and the transport by mouse.

Why you must talk to win (design intent, LOCKED): dialogue and story context (K's domain) contain the hints about what to listen for; the listening and playing (M's domain) contain the answers to Choice Puzzles (K's questions). Pack authors (Story Weavers) are instructed to weave at least one moment per scene where each player needs something only the other has.

Solo play (LOCKED): every single control is mouse-operable (on-screen arrows, on-screen transport, clickable menus), so one person with a mouse can play the entire game. Keyboard bindings are a mirror, not a requirement.

Input abstraction (LOCKED architecture requirement): the Player must route all input through a named-action layer (e.g., STORY_NEXT, MENU_UP, MENU_SELECT, TRANSPORT_PLAYPAUSE, SEEK_FORWARD, plus pointer events), with device→action mapping in one config file. DeepSeek will later add joystick (K) and Xbox controller (M) by editing only that mapping layer. No input handling may be scattered through game logic.

## 5. The Content Model: Problem Packs and the Assembly Line

LOOM is generic. The Player is a frozen black box; all content lives in Problem Packs. LOCKED: we are not building one campaign — we are building the process, prompts, and tools so that one pack or a million packs can be made, by Nir now and by anyone on GitHub later.

How one pack is born (the frozen pipeline):

    Nir opens a fresh Opus child chat with the fixed Story Weaver prompt (a future deliverable of this project — the BIBLE defines its output contract, §9). The prompt instructs the child to ask Nir for a Wikipedia page. Nir pastes one (e.g., Square root).
    The Story Weaver reads the page — especially the history section (Babylonians, Egyptians, ancient India, Greeks…) and the properties/uses section (real, intuitive applications, e.g., "the square root maps the area of a square to its side length") — and invents a short, warm, fictional-but-plausible everyday story in that historical setting (a ruler commissions a building; the builders hit a constraint on site; the local sage reveals the function). About 3 scenes. In every scene image, our two modern young explorers are present, talking with the period characters; everything else is period-authentic. Static images only — this is a slide presentation, not animation.
    For each scene the Story Weaver outputs: the caption/narration, a dialogue tree (menus of ~4 options, all pre-written — no AI at runtime, ever), an image-generation prompt (cute Disney/Pixar 3D style) that Nir pastes into an image-AI chat, the LaTeX strings for the equations, and the spell specs (function + knobs) for the puzzles.
    Nir generates the images (paste prompt → save PNG) and renders the LaTeX to PNGs with his local MiKTeX installation (he has done this in previous games).
    Nir (or DeepSeek) runs the Spell Compiler on the spell specs. It computes the notes, precomputes all visuals, and copies/converts exactly the needed audio samples.
    DeepSeek assembles the pack folder, validates it against the schemas, tests it in the Player, and pushes to GitHub.

Understanding Mode: LOCKED OUT. LOOM does not include the four-level explanation feature from other Peak Together games. The teaching lives in the story, the dialogue, the synced visuals, and the success texts.

## 6. The Sonification Engine (the heart)

This is the precise, implementable definition of how a function becomes a spell. All of this runs inside the Spell Compiler, offline. The Player only ever sees the finished note list.

### 6.1 The pipeline (LOCKED, adapted from the book)

Given a function f and the knobs below:

    Sample the domain. Choose [xmin, xmax] and N notes (4 ≤ N ≤ 16; default 8). Default sampling is uniform: xi = xmin + i·Δx. An explicit list of sample points may be given instead when a function's most characteristic stretch needs hand-picked moments (e.g., the damped sine needs to show both oscillation and decay).
    Condition the values. Optional, in this order as configured: clamp to [lo, hi]; shift; compress blow-ups with sign(y)·log(1+|y|); smooth (moving average) for wiggly data. (Book §5.2 rules.)
    Map to semitones (absolute mapping, LOCKED). θi = a·f(xi), where θ is in semitones relative to the base note. The compiler accepts either an explicit pitch_scale_a or (friendlier, recommended) a target_span_semitones: it auto-computes a so the conditioned values span exactly that many semitones. Default span 12; hard maximum 24 (the two-octave keyboard cap).
    Quantize to a scale. θi ← argmin over s ∈ ScaleSet of |θi − s|, where ScaleSet is the chosen scale extended across the allowed range. Canonical scales: pentatonic_major = {0, 2, 4, 7, 9} (default — no dissonant pairs, kindest to untrained ears), major = {0, 2, 4, 5, 7, 9, 11}, natural_minor = {0, 2, 3, 5, 7, 8, 10}, chromatic (advanced tiers only). Guideline: prefer a base note of C so the staff needs no accidentals for beginners; the compiler warns otherwise.
    Place on the rhythmic grid. Default: flat rhythm — equal notes, one per beat, at the spell's BPM (default 90). Flat rhythm is the beginner standard (pure pitch contour = maximal memorability). Optional advanced layers: duration_from_magnitude (longer notes for larger |f|, quantized to eighth/quarter/half) and rest insertion at zero crossings.
    Dynamics. Default: one fixed dynamic layer (e.g., forte). Optional: dynamics_from_magnitude or dynamics_from_derivative, quantized to the dynamic layers that actually exist in the sample library for that instrument (so an exponential spell genuinely gets louder as it leaps — the book's velocity channel, for free, with zero DSP).
    Timbre. LOCKED principle: timbre is discrete and secondary, never continuous. With Philharmonia samples our timbre axis is: (a) the choice of instrument for the whole spell (default), (b) dynamic layers as a brightness proxy, and (c) for advanced multi-voice spells, different instruments per voice, separated by register and family per the book's Ch. 6/8 rule. No filter DSP in v1.
    Choose samples. For every note, the compiler picks one concrete file from the local Philharmonia library — the exact recorded pitch (no pitch-shifting needed; the library covers essentially every note of every instrument), the nearest available dynamic, articulation normal by default.
    Precompute all visuals. For every note i the compiler emits: the graph highlight segment (as normalized fractions of the plot width); the helix marker (angle = 30°×(θi mod 12); height z = θi/12, so one octave = 1.0 of height, matching the book's z = θ/(2π) normalization); and the keyboard key index (midi − midi(low_note)). The compiler also emits the full graph polyline (the curve as a list of points normalized to a unit box) so the Player never evaluates f, and the helix wireframe geometry.

### 6.2 The knobs (canonical names — every future doc uses these)

```
SPELL SPEC — compiler input knobs
--------------------------------------------------
spell_id                unique snake_case id
display_name            human name shown in-game
function                human-readable description; implemented in Python inside the spec by the pack's child chat
latex                   LaTeX string for the equation (Nir renders it to PNG)
x_min, x_max            domain
num_notes               4..16, default 8
sample_points           "uniform" (default) or explicit list of x values
conditioning            ordered list from: clamp(lo,hi) | shift(c) | log1p | smooth(k) | none
base_note               e.g. "C4" (prefer C-based; compiler warns otherwise)
pitch_scale_a           explicit a, OR:
target_span_semitones   auto-fit span, default 12, max 24
scale                   pentatonic_major (default) | major | natural_minor | chromatic
bpm                     default 90
rhythm_mode             flat (default) | duration_from_magnitude
dynamics_mode           fixed(<dynamic>) (default fixed(forte)) | from_magnitude | from_derivative
instrument              Philharmonia instrument folder name, e.g. "flute"
articulation            "normal" (default)
reveal_mode             grow (default) | whole      [per-puzzle, may live in the pack instead]
```

### 6.3 The sample library and the download-size strategy (LOCKED)

Facts (per Nir): the Philharmonia library (free, philharmonia.co.uk) is organized as instrument folders (Woodwind, Brass, Percussion, Strings families) containing 600–1300 MP3 files each, named like bass-clarinet_A2_1_forte_normal.mp3 — per note, per dynamic, per articulation, with ~20 variants per note. Full quality, every pitch recorded. Total size is far too large to ship (Woodwind alone is a 260 MB zip).

The strategy (LOCKED): ship only what each pack uses.

    The full library lives only on Nir's PC (and any future pack-author's PC). It is a compile-time resource, like MiKTeX.
    The Spell Compiler scans the actual files on disk (never trusts a remembered list) and parses filenames with a tolerant pattern: instrument, note+octave, a numeric token (meaning to be confirmed empirically by DeepSeek — likely a length/variant code), dynamic, articulation. It selects one file per needed note.
    Selected MP3s are converted at compile time into short, trimmed, loudness-normalized WAV files (44.1 kHz, 16-bit) named by our own canonical convention <instrument>_<note><octave>_<dynamic>.wav, and copied into the pack's audio/ folder. A typical pack needs a few dozen samples — a handful of megabytes, not hundreds.
    The Player therefore plays plain WAV files only: dead simple, low latency, no decoders. (If pack sizes ever balloon, OGG is the fallback — see Open Questions.)

## 7. The Spell Format (canonical data model)

A spell is one JSON file. This schema is the contract between Compiler and Player. Versioned with semantic versioning; the Player refuses files with a newer major version than it knows.

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
      "sample": "audio/flute_C4_forte.wav",
      "key_index": 0,
      "graph_segment": { "x_from": 0.0, "x_to": 0.125 },
      "helix": { "angle_deg": 0.0, "z": 0.0 }
    }
  ],
  "graph": {
    "points": [[0.0, 0.0], [0.02, 0.14]],
    "x_label": "x",
    "y_label": "f(x)"
  },
  "helix_geometry": { "turns": 2, "markers_only": false },
  "required_samples": ["audio/flute_C4_forte.wav"],
  "compiler_version": "1.0",
  "notes_for_humans": "Rising staircase with shrinking steps — the ear hears the flattening."
}
```

Field meanings (binding definitions):

    notes is the complete melody in playback order. start_beat/duration_beats are in beats at bpm; the Player converts to seconds with seconds = beats × 60/bpm and nothing more.
    midi is the unambiguous pitch (MIDI note number); note_name is for the staff renderer and humans.
    key_index = midi − midi(keyboard.low_note); the keyboard draws all chromatic keys from low_note to high_note inclusive.
    staff.clef is treble or grand (rule: grand whenever any note is below C4).
    graph.points are the precomputed curve, normalized to a unit box; graph_segment gives each note's highlight span as fractions of plot width.
    helix.angle_deg and helix.z place each note's glowing marker on the spiral (30° per semitone of chroma; z rises 1.0 per octave).
    required_samples is the shipping manifest for that spell's audio.

## 8. The Pack Format (scenes, dialogues, puzzles)

One folder per pack, self-contained. Canonical layout and manifest:

```
packs/square_root/
    pack.json          <- manifest: scenes, dialogue trees, puzzles
    spells/*.json      <- compiled spells
    audio/*.wav        <- only the samples these spells need
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
      "caption": "Babylon, long ago. The king wants a square garden of a given area...",
      "dialogue": {
        "start": "n1",
        "nodes": {
          "n1": {
            "speaker": "The King",
            "text": "My garden must cover exactly this much land. But how long is its side?",
            "options": [
              { "text": "O King, tell us more about your garden.", "goto": "n2" },
              { "text": "Perhaps your scribes can help?", "goto": "n3" },
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
      "hint_higher": "Yours was a little low — press play and listen again.",
      "hint_lower": "Yours was a little high — press play and listen again."
    },
    {
      "puzzle_id": "sqrt_vs_line",
      "type": "choice",
      "spells": ["spells/sqrt_basic.json", "spells/line_basic.json"],
      "labels": ["A", "B"],
      "show_graphs_before_answer": false,
      "question": "Which melody keeps climbing at the same steady pace?",
      "answers": [
        { "text": "Melody A", "correct": false, "explain": "A's steps kept shrinking — that gentleness is the square root." },
        { "text": "Melody B", "correct": true,  "explain": "Yes! Steady, even steps — that is the straight line." }
      ]
    }
  ]
}
```

The Story Weaver prompt (future deliverable) must be written to emit exactly these structures (plus image prompts and LaTeX strings as separate labeled blocks for Nir to carry to the image AI and MiKTeX). Story Weaver content rules (binding): ~3 scenes; every image shows the two modern explorers talking with period characters; dialogue menus of up to 4 options; every scene contains at least one hook that makes the couple talk to each other; historical settings drawn from the Wikipedia page's actual history section; the fiction is invented but never claims to be historical fact — success texts may gently note "our story is imagined, but the mathematics is real."

## 9. The Two-Program Architecture

    Program A — Spell Compiler (offline, on the author's PC): evaluates functions (numpy allowed), conditions, maps, quantizes, selects and converts samples, precomputes graph/helix/keyboard sync data, writes spell JSON + WAVs, and emits a plain-text list of LaTeX strings for Nir to render. It may be slow, verbose, and dependency-heavy; only authors run it.
    Program B — LOOM Player (the game every visitor downloads): reads pack.json and spell JSONs, blits PNGs, draws the bench, plays WAVs at precomputed times, lights precomputed highlights, walks dialogue trees, compares the player's clicked midi to the target note's midi. That comparison — an integer equality and a greater/less for the higher/lower hint — is the entire mathematics of the runtime. (Rotating the helix wireframe on screen is presentation geometry, permitted.)

Why the runtime stays dumb (LOCKED rationale): determinism (every spell can be auditioned and hand-tuned by ear at design time), robustness (no math bugs can exist where there is no math), performance (triggering preloaded WAVs is cheap and comfortably under the book's 50 ms interactivity bar), and pipeline fit (child chats can implement the Player against frozen JSON fixtures without ever touching sonification theory).

What crosses the boundary: only files — spell JSONs, pack.json, WAVs, PNGs. No code, no formulas, no network.

## 10. Curriculum: the Ear-Training Ladder

There is no fixed campaign, so this section is binding guidance for pack authors plus a reference spellbook shipped in the repo as demos and test fixtures.

The ladder (maximally different → subtly different):

    Tier 1 — Contour families. Straight line (steady staircase) vs. sine (even arcs) vs. exponential (runaway leaps). Any two Tier-1 spells differ in gross contour; no one can confuse them after one listen.
    Tier 2 — Within-family cousins. Parabola vs. exponential (both rise, but differently); square root vs. logarithm vs. line (three flavors of climbing); sine vs. damped sine e−xsin(10x) (the book's own signature example — arcs that quicken, fade, and settle).
    Tier 3 — Parameters by ear. sin(x) vs. sin(2x) (frequency); ex vs. e2x (growth rate); amplitude differences. Rhythm/dynamics layers may be enabled here.
    Tier 4 — Advanced (stretch, post-v1). Two-channel spells (cycloid: height → pitch, and a second stream in dynamics); two-voice spells (f and f′ in counterpoint, ≤ 2 voices, separated by register and instrument family); co-op polyrhythm encounters (the 3:4 orbital-resonance idea). Flagged, not designed here.

The confusability rule (binding): two spells required within the same scene or same Choice Puzzle must differ audibly in at least one gross feature — contour class (up / down / arch / oscillation), or number of direction changes, or total span — unless the puzzle's explicit teaching goal is that subtle distinction, in which case the intro text must tell the players exactly what tiny difference to listen for. Never spring an un-signposted subtle distinction on the player.

Reference spellbook v1 (ships with the engine repo): line, parabola, square root, logarithm, sine, damped sine, exponential — each with tuned knobs, each documented with one sentence of "what the ear learns."

## 11. Emotional & Audio Design

The aesthetic: warm, acoustic, unhurried — real orchestral instruments playing simple melodies in pleasant scales, more "cozy museum at dusk" than "video game." The book's emotional toolbox is used at low, tasteful intensity:

    Feedback is consonance. Correct note → a soft consonant confirmation; completed spell → the full melody replayed with a warm final chord. Wrong note → no harsh sound, no buzzer, ever — just the gentle text nudge. (We deliberately do not use dissonance as punishment; this inverts the usual game grammar in favor of kindness.)
    Mode as data, sparingly. A pack may render a function that dips negative in a minor scale — the mode shift itself carries meaning (book Ch. 7). Use only when it teaches.
    Tempo as mood. Spells live in the calm-to-moderate band (roughly 70–110 BPM). The high-BPM tension tiers and the horror/roughness palette from the book's Chapter 7 Part C are documented in my chapter summaries but are out of scope for v1 (see Open Questions — parked, not deleted).
    Between puzzles: quiet or a very soft ambient bed (Open Question). Silence is acceptable and even fitting; the spells should be the loudest thing in the room.

## 12. Accessibility

    Dual coding everywhere (LOCKED): everything audible has a synchronized visual (graph glow + helix glow + key glow), and everything visual has a sound (clicking any key always sounds it). A player with weak pitch discrimination can lean on the lights; a player with weak vision can lean on the ears; the game remains meaningful either way — exactly the Simon promise: "even if the user does not understand anything, he can still play."
    Unlimited replays, seekable timeline, no timers, no fail states — accessibility and kindness are the same feature here.
    Highlights use both color and brightness change (color-blind safe); the "returns to normal black and white" resting state Nir described gives maximal contrast for the lit element.
    Fixed layout, large click targets (piano keys sized for imprecise mice), readable fonts.
    The helix rotation (if K rotates it) never hides information — markers stay visible from every angle or the rotation is limited.

## 13. Tech Stack & Repository Architecture

Recommendation (to be confirmed by DeepSeek's compile/test loop on Nir's actual Windows PC — per the Iron Rules I do not assert external APIs as certain):

    Language: Python 3.11+, Windows-first, launched as python app.py, matching Descent QED and the rest of the Arcade.
    Player framework: pygame (or its maintained fork pygame-ce) as the primary candidate — one library gives us the window, 2D drawing, PNG blitting, WAV playback with a multi-channel mixer, mouse/keyboard, and native joystick/gamepad support (which serves the future controller work through our input-abstraction layer). Fallback candidates if testing reveals blockers: pyglet, arcade. The Player should need no other heavy dependencies — no numpy, no matplotlib, no audio DSP.
    Helix rendering: software 3D — a precomputed spiral polyline rotated by a simple rotation matrix and projected to 2D, drawn as anti-aliased lines (authentic 90s-demoscene wireframe, exactly the requested aesthetic). No OpenGL dependency.
    Compiler stack: Python + numpy for evaluation; MP3→WAV conversion via a compile-time tool (candidate: pydub + ffmpeg, or ffmpeg CLI directly — DeepSeek picks whatever actually works on Nir's PC; this dependency never touches players' machines).
    Reference resolution: 1280×720 window, fixed internal layout, integer-scaled to larger windows if easy; do not spend effort on responsive layout.
    Repo layout: everything under loom/ in the existing repo — loom/player/ (the game, with app.py at its root), loom/compiler/, loom/packs/<pack_id>/, loom/docs/ (this BIBLE and its successors), loom/prompts/ (the frozen Story Weaver prompt when it exists).
    Saving: a small local JSON progress file (last scene per pack; spells unlocked for Free Play). Nothing else persists. No network access of any kind at runtime.

## 14. LOCKED DECISIONS (do not reopen)

    LOOM keeps only the name of the 1990 game; zero lore, mechanics, or plot from it.
    LOOM teaches the cross-mountain basics of hearing functions; it is tied to no specific mountain.
    Audience: curious young adults / couples; tone warm and forgiving; ~90% education / 10% entertainment; no punishment, no timers, no scores, no game over, unlimited retries and replays.
    Simon-style core: hear → lights on graph, helix, and keys → repeat on the on-screen piano; per-note OK/Cancel commit; gentle higher/lower hints; grow and whole reveal modes.
    Screen: top half Scene Stage (Story Mode / Puzzle Mode), bottom half Music Bench (piano keyboard of 1 octave default / 2 octaves max, real staff with treble or grand clef, OK/Cancel, VLC-style transport), all in fixed positions.
    Puzzle Mode shows all three synced visuals: low-res graph, 3D-demoscene pitch helix (the signature visual), and the LaTeX-baked equation PNG.
    Two puzzle types in v1: Echo and Choice.
    Co-op split: Player K (keyboard → future joystick) = story, dialogue menus, Choice answers, transport hotkeys; Player M (mouse → future Xbox controller) = piano, OK/Cancel, transport by mouse. Everything mouse-operable for solo. Input-abstraction layer mandatory.
    Content = Problem Packs, generated by the frozen Story Weaver prompt from a Wikipedia page: ~3 scenes, baked Pixar-style images always featuring the two modern explorers, pre-written 4-option dialogue trees, slides with next/back. Nothing generated at runtime.
    No Understanding Mode in LOOM.
    Sonification: absolute mapping θ = a·f(x); scale quantization (pentatonic default); beat grid; flat rhythm default; ≤ 2-octave span; discrete timbre (instrument choice + dynamic layers); no pitch-shifting (Philharmonia covers every note); no runtime DSP.
    Program A / Program B split; the Player performs no mathematics beyond comparing MIDI numbers; only data files cross the boundary.
    Ship only per-pack sample subsets, converted at compile time from the local Philharmonia MP3 library to trimmed, normalized WAVs; the full library never ships.
    Spell and pack JSON schemas of §7–§8, with semantic versioning.
    Python desktop, Windows-first, python app.py, under loom/ in the existing repo.

## 15. OPEN QUESTIONS (for Nir)

    The two explorers: should they be the same fixed couple across every pack (with names — perhaps ones you'd like to choose 😉), or generic and unnamed? Fixed named characters make image prompts more consistent. My recommendation: fixed pair, you pick the names.
    Ambient sound between puzzles: silence, or a very soft optional ambient loop per pack? My recommendation: silence in v1 (simplest, and it makes the spells feel precious).
    The dark/tension palette (high BPM, dissonance, roughness — Ch. 7 Part C): permanently out, or parked for a possible future "advanced tier"? My recommendation: parked, out of v1.
    WAV vs. OGG for shipped audio: WAV is simplest and per-pack sizes should be a few tens of MB at most. If a future pack grows too large, we switch to OGG. Acceptable to lock WAV for v1?
    Window behavior: fixed 1280×720 window acceptable, or do you want fullscreen/scaling from day one? My recommendation: fixed window v1.
    Free Play sliders (the "spell laboratory" with live pitch-scale/tempo knobs): parked for post-v1? My recommendation: yes, parked — it would break the "no math at runtime" rule and needs its own design.

## 16. Parked ideas (recorded so they are not lost, not designed here)

Co-op 3:4 polyrhythm "orbital resonance" encounters; f + f′ two-voice counterpoint spells; the brachistochrone race-by-ear as a flagship Choice Puzzle; microtonal "detuned" renderings; stereo-panned per-player voices; adaptive difficulty escalation; user-CSV sonification sandbox.

End of the LOOM BIBLE v1.0 — Claude Fable, founding architect. 🌀
