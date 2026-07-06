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

Naming: Fable's docs get Hindu scripture names. "UPANISHADS" (the plot/progression
doc) is **still to come** from Fable.

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

## 3. CURRENT SITUATION (July 6, 2026, ~1:30 AM Israel — Nir went to bed)

- ✅ **LOOM2 folder created;** LOOM (v1) left intact but deprecated.
- ✅ **Scripture saved verbatim + pushed:** VEDAS, MAHABHARATA, RAMAYANA.
- ✅ **The Listening Prototype code is landed and runnable:**
  **`loom2/listening_totem.py`** (extracted verbatim from the RAMAYANA). It
  **py_compiles clean.**
  - ⚠️ **Dependency:** needs `pip install sounddevice` before running (numpy +
    pygame already present on Nir's PC; sounddevice is NOT yet installed —
    confirmed missing on 2026-07-06). Full command: `pip install numpy pygame sounddevice`.
  - Run: `python loom2/listening_totem.py` — Arrows/WASD move the totem, keys 1–6
    switch surfaces (Ramp/Bowl/Hill/Ridge/Saddle/Egg-carton), +/- hearing radius,
    Esc quits.

### 🎧 IMMEDIATE NEXT (Nir's ear test tomorrow morning — the pass/fail of the whole invention)
Put on headphones and run the prototype. The checklist (from the RAMAYANA):
1. **Bowl (key 2)**, totem at center: each ring sings ONE unison note, rising
   outward → hearing level curves.
2. **Saddle (key 5)**, totem at center: stretched chord, notes above AND below →
   clearly different from the Bowl. **If you can tell Bowl from Saddle with eyes
   closed, the invention works.**
3. **Ridge (key 4):** move left–right vs up–down — one changes the music, the other
   doesn't → partial derivatives.
4. **Ramp (key 1):** the groove transposes but keeps its shape → slope.
5. **Bowl's lake:** blue center sounds below A440 → negative numbers via the
   origin-centered helix.

If it passes → tell Fable; if anything needs tuning, tune it in the prototype
(days, not months). This is the "anti-stuck insurance."

---

## 4. WHAT'S STILL NEEDED (the road ahead)

1. 🎧 **Nir's ear-test verdict** on the Listening Prototype (above). Relay to Fable;
   tune constants in `listening_totem.py` if needed (measure, radius, scale,
   family recipes, grid density).
2. 📜 **The UPANISHADS** (Fable) — the plot/progression: the couple's journey, how
   spell-weaving drives it, what woven spells do, level design. (Fable will author.)
3. 🏗️ **The real game build** (after the ear test passes + UPANISHADS): the split
   screen (Left = the Land, a moderngl shaded terrain + contour coloring; Right =
   the Loom, a wireframe helix centered on origin with the orchestra symbols +
   rhythm rings + the current-point vector), two-player controls (P1 keyboard/
   joystick sweeps x; P2 mouse/Xbox sweeps y), the auditory multiple-choice
   spell-weaving mechanic, packaging to a single Windows EXE (PyInstaller).
4. 🧰 **Stack setup** when building: `moderngl + pyglet + numpy + sounddevice`
   (+ Pillow, PyInstaller for packaging) — reuse Quake/Homeworld's software-3D +
   bloom + EXE recipe.
5. 🌐 **Website:** add multivariable calculus as a foundational subject (NOT a
   single mountain) once the game ships.

---

## 5. RESTART PROTOCOL

1. Read this file first.
2. Read the scripture in `loom2/HINDU/` as needed (VEDAS → MAHABHARATA → RAMAYANA;
   UPANISHADS when it arrives).
3. Sanity: `python -m py_compile loom2/listening_totem.py` should pass; running it
   needs `pip install sounddevice` first.
4. Ask Nir where we are with the ear test / whether Fable sent the UPANISHADS.
5. **The source book** *Sounding the Unknown* is at `loom/book/chapter_00.txt …
   chapter_10.txt` — the authoritative HSS reference (LOOM v1 lost its soul by
   planning from summaries; LOOM2 must stay grounded in the book + Nir's true helix
   in `loom/HELIX_AND_REBOOT_NIRS_TRUE_VISION.md`).
6. ⚠️ AGENTS.md still routes startup to older games; LOOM2's authoritative memory
   is THIS file. Never modify AGENTS.md. Save Fable outputs VERBATIM; commit + push
   every meaningful step; GitHub blob links; emojis + warmth; he is "Nir".
