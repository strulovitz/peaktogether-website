# LOOM2 — PROJECT WORKFLOW & MEMORY (for DeepSeek / OpenCode)

> ⭐ **ON RESTART, READ THIS FIRST.** LOOM2 is the reboot of the sonification game.
> LOOM (v1, folder `loom/`) is **deprecated but kept** — do NOT build on it; its
> design flattened the book into a 1D pitch melody. LOOM2 restores the true vision
> of Nir's book *Sounding the Unknown* (the Helical Sonification System, HSS).
>
> Scripture lives in `loom2/HINDU/` (Hindu-themed names, Nir's choice, "to amuse
> himself"). Save every Fable output **VERBATIM**. Commit + push after each step.
> Give Nir GitHub **blob (view)** links. Emojis + warmth always. He is "Nir".

---

## 0. WHAT LOOM2 IS (in one breath)

A two-player, one-screen game where players **hear multivariable calculus**. A
mathematical surface z = f(x, y) becomes music via the **Helical Sonification
System (HSS)**. The core invention (the UPANISHADS/MAHABHARATA breakthrough): **a
surface is not a melody — it is an ORCHESTRA.** You plant a **Listening Totem** in
the landscape; every "musician" seated on the grid inside its hearing circle plays
at once, so you hear a whole *neighborhood* as one chord/groove — never a 1D siren
sweep. Moving the totem re-orchestrates the whole song.

The HSS mapping (Nir's true vision, restored):
- **height z → pitch** (A4 = 440 Hz at z = 0; the helix is centered on the origin,
  so valleys sound BELOW the reference — negative numbers are first-class).
- **angle θ → timbre** (the orchestra circle: brass at 12 o'clock, strings at 4,
  woodwinds at 8; continuous Fourier-recipe morph between families).
- **radius r → rhythm** (concentric rings: ring n = n pulses per measure; the axis
  = one calm sustained tone; fractional radius crossfades adjacent rings).

Peak Together lineage (each game teaches a foundational topic as a '90s co-op
remake): Descent QED (Basel), Quake: Principia (Calculus), Homeworld: A Good Basis
(Linear Algebra), **LOOM2 (Multivariable Calculus)**.

---

## 1. THE SCRIPTURE (`loom2/HINDU/`, all by Claude Fable, saved VERBATIM)

- **`LOOM2-VEDAS-BY-FABLE.md`** — the foundational vision (identity, the mountain =
  multivariable calculus, the HSS three-coordinate system, players, spells, screen,
  tech, what-it-is-NOT, open questions).
- **`LOOM2-MAHABHARATA-BY-FABLE.md`** — the breakthrough: *a surface is an
  orchestra*; the **Listening Totem**; why it teaches the math (level curves =
  unison; critical points = chord quality; gradient = transposition); feasibility
  guardrails. *(Originally saved as "UPANISHADS", renamed at Nir's request —
  "UPANISHADS" is reserved for a later document Fable will give.)*
- **`LOOM2-RAMAYANA-BY-FABLE.md`** — the **Listening Prototype** ("The Listening
  Totem"): the complete one-file ear-test program + how to run it + tomorrow's
  ear checklist. The code is also extracted to a runnable file (see §3).
- **`LOOM2-UPANISHADS-BY-FABLE.md`** — the **plot & game structure** (v1.0, July 7,
  2026): the one-principle ("the game IS the technology"), the orchestra (trumpet/
  violin/flute, A-major pentatonic, ~60–75 shipped files), the one screen layout
  (Land + Loom + Question), controls, the data-driven scene JSON format, and the
  full **7-stage / 12-scene campaign** (Roman Road → Hannibal's Saddle → Tartaglia's
  Cannon → the Fog Summit finale). Ends with two items for Nir: (a) scene 10 (Ocean
  Swell) uses a slightly richer "match each groove" format — keep or flatten to plain
  A/B/C/D (Nir's call, zero cost); (b) next doc proposed = the **SUTRAS** (impl spec).

Naming: Fable's docs get Hindu scripture names. The **SUTRAS** (the implementation
spec) is the next document proposed by Fable — **still to come**.

---

## 2. LOCKED DECISIONS / NIR'S ANSWERS (July 6, 2026)

- **Tech stack (Nir overrides the VEDAS "no OpenGL"):** **use OpenGL** —
  **moderngl + pyglet** (the modern shader stack of Quake & Homeworld: moderngl
  5.12.0 / pyglet 2.1.14), NOT pure-software, NOT PyOpenGL (that was Descent's older
  flavor). **Audio is KING: real-time additive synthesis on numpy buffers via
  `sounddevice`** (PortAudio callback), fully independent of graphics. Rationale in
  full: pygame.mixer is a file-player, primitive for real-time synthesis; sounddevice
  is the correct tool; input→shared-state→audio is our own code, not a library
  feature; pyglet already handles all controllers (proven in Quake/Homeworld).
- **Reference note:** **A4 = 440 Hz at z = 0** (universal, mathematically clean:
  f(z) = 440·2^(z/z_oct); octaves = exact doublings). NOT middle C. **Pitch range:
  clamp to ±3 octaves** (~55–3520 Hz), soft-limit beyond.
- **Title = LOOM2** (no subtitle). **No mountain:** multivariable calculus is
  foundational bedrock shared beneath many mountains — present it as a foundational
  subject on the website, not a single peak.
- **Curriculum order:** (1) functions of two variables / surfaces → (2) level
  curves / contour maps → (3) partial derivatives → (4) directional derivatives &
  gradient → (5) critical points (max/min/saddle) → (6) second-derivative test →
  (7) optimization by ear. **Double integrals / volume DROPPED** (no good way to
  hear volume without cacophony — Nir agreed).
- **Spells (seed for plot):** each mastered concept grants a spell that reshapes /
  crosses the landscape (gradient spell points uphill; saddle spell opens a pass;
  optimization spell reveals the summit). Spell = both the ear-test AND the means of
  progressing. Full plot → the UPANISHADS.
- **Measure length / tempo:** **fixed 2.0 s per measure (120 BPM, four beats),
  constant during play.** Grounded in all three families (strings' slow attack
  stays clean at ≥0.33 s/pulse up to ~5–6 rings; the calm center = a 2.0 s whole
  note). The old LOOM "1.3 s" was a per-note *sample* length (Forge), never a
  measure — and LOOM2 synthesizes, so note length is uncapped. Optional global
  tempo slider for accessibility, but fixed within a level.
- **Guardrails (from the MAHABHARATA):** ~12–30 musicians in the hearing circle
  (not hundreds — the ear tops out); heights snap to **pentatonic** (chords stay
  beautiful); ≤ ~4 occupied rhythm rings at once; **build the Listening Prototype
  FIRST** and validate by ear before anything else.

---

## 3. CURRENT SITUATION (July 7, 2026)

- ✅ **LOOM2 folder created;** LOOM (v1) left intact but deprecated.
- ✅ **Scripture saved verbatim + pushed:** VEDAS, MAHABHARATA, RAMAYANA, **UPANISHADS**.
- ✅ **The Listening Prototype PASSED THE EAR TEST.** `sounddevice` installed
  (0.5.5, 2026-07-07). Nir ran `loom2/listening_totem.py` on headphones — the
  invention works: he can hear Bowl vs. Saddle, level curves, partials, negatives.
- ✅ **PHILHARMONIA EDITION built + pushed (July 7, 2026):**
  **`loom2/listening_totem_philharmonia.py`** — a copy of the prototype that swaps
  the synthesized wavetables for **real Philharmonia recordings** (Brass = trumpet,
  Strings = violin, Woodwinds = flute). Octave-accurate: each note is resampled to
  the EXACT target pitch (height→pitch preserved, negatives included); per-pulse
  retrigger of the real sample per rhythm ring; equal-ish family crossfade by angle;
  persistent per-musician playback across audio blocks; ~1.2% of the realtime CPU
  budget. **Nir's verdict: "it actually sounds like I'm creating MUSIC, not just
  sounds"** — this validated the sample-based orchestra Fable then locked into the
  UPANISHADS §2. Run: `python loom2/listening_totem_philharmonia.py`.
- 📋 **Orchestra roster finalized with Nir (for Fable), from the Philharmonia folders:**
  STRINGS = violin(high)/viola(med)/cello(low)/double bass(very low); WOODWINDS =
  flute(high)/oboe(med-high)/clarinet(med)/bass clarinet+bassoon(low)/contrabassoon
  (very low); BRASS = trumpet(high)/french horn+trombone(med)/tuba(low). Deliberately
  DROPPED (not orchestral / distracting): banjo, guitar, mandolin, saxophone, cor
  anglais, percussion. (The prototype uses violin+trumpet+flute — one per family.)

### 🎧 EAR TEST — PASSED (was the make-or-break of the whole invention)
The Listening Prototype checklist (Bowl vs Saddle, Ridge partials, Ramp transpose,
negative lake) all confirmed by Nir on headphones. The invention is real. ✅

---

## 4. WHAT'S STILL NEEDED (the road ahead)

1. ✅ **Nir's ear-test verdict** — PASSED (both synth + Philharmonia editions). Relayed
   to Fable, who locked the sample-based orchestra into the UPANISHADS.
2. ✅ **The UPANISHADS** (Fable) — plot/progression LANDED + saved verbatim + pushed
   (`loom2/HINDU/LOOM2-UPANISHADS-BY-FABLE.md`). 7 stages, 12 scenes.
   - 🟡 **Two OPEN items Fable left for Nir:** (a) scene 10 (Ocean Swell) format —
     keep the richer "match each groove" or flatten to plain A/B/C/D (Nir's call);
     (b) next document proposed = the **SUTRAS** (implementation spec), OR go straight
     to building. **Awaiting Nir's direction.**
3. 📜 **The SUTRAS** (Fable, proposed next) — the implementation spec. Open items it
   should nail (from UPANISHADS §9): exact ~60–75 sample list + per-instrument ranges
   (DeepSeek scans the folders); the Totem 3D model; groove-recording format for quiz
   options (pre-rendered WAV vs live-synth at hidden coords); terrain mesh resolution
   & camera limits; Xbox/joystick button mapping.
4. 🏗️ **The real game build** (after SUTRAS or Nir's go): split screen (Left = the
   Land, moderngl shaded terrain + contour coloring; Right = the Loom, origin-centered
   wireframe helix + orchestra symbols + rhythm rings + note-dot constellation),
   two-player controls (P1 keyboard/joystick sweeps x; P2 mouse/Xbox sweeps y), the
   auditory 4-option quiz, packaging to a single Windows EXE (PyInstaller). Reuse
   Quake/Homeworld's moderngl+pyglet software-3D + bloom + EXE recipe.
5. 🧰 **Stack setup** when building: `moderngl + pyglet + numpy + sounddevice`
   (+ Pillow, PyInstaller for packaging).
6. 🌐 **Website:** add multivariable calculus as a foundational subject (NOT a
   single mountain) once the game ships.

---

## 5. RESTART PROTOCOL

1. Read this file first.
2. Read the scripture in `loom2/HINDU/` as needed (VEDAS → MAHABHARATA → RAMAYANA →
   UPANISHADS; SUTRAS when it arrives).
3. Sanity: `python -m py_compile loom2/listening_totem.py` and
   `python -m py_compile loom2/listening_totem_philharmonia.py` should pass;
   `sounddevice` (0.5.5) is installed. Both prototypes run + passed Nir's ear test.
4. Ask Nir where we are: the two UPANISHADS OPEN items (scene-10 format; SUTRAS vs
   build straight away).
5. **The source book** *Sounding the Unknown* is at `loom/book/chapter_00.txt …
   chapter_10.txt` — the authoritative HSS reference (LOOM v1 lost its soul by
   planning from summaries; LOOM2 must stay grounded in the book + Nir's true helix
   in `loom/HELIX_AND_REBOOT_NIRS_TRUE_VISION.md`).
6. ⚠️ AGENTS.md still routes startup to older games; LOOM2's authoritative memory
   is THIS file. Never modify AGENTS.md. Save Fable outputs VERBATIM; commit + push
   every meaningful step; GitHub blob links; emojis + warmth; he is "Nir".
