🗝️ QUAKE (Game 3) — PROMPT TO OPUS: PARENT 7 HANDOFF v2 (M8 FIRST PRINCIPIA LEVEL)

Written June 26, 2026 by DeepSeek (Runner). Updated June 28, 2026 (v2 — added DIGESTED PRINCIPIA + material-request protocol). Parents 1–6 are DONE. The full engine (13 modules, 285 tests) is built and wired; the Golden Fixture Pack (3 hand-authored rooms) proves the entire runtime stack works end-to-end. Parent 7 has exactly ONE mission: design the FIRST REAL Principia level — transforming Quake from a tech demo with dummy rooms into an actual game powered by Newton's text.

⚠️ CRITICAL — HOW YOU GET INFORMATION ⚠️
You are an Opus chat inside OpenRouter. You have NO internet access, NO GitHub access, NO file system access. You CANNOT browse, download, or read anything on your own. The only text you have is what is pasted into this chat — this handoff + the Commentaries + the OT + the NT + the DIGESTED PRINCIPIA below.
If you need ANYTHING else (full text of a proposition, a figure image, a format specification, a scripture section), you must ASK NIR to copy-paste it for you. Nir is your hands and eyes — he can fetch things from GitHub, Wikisource, or the local filesystem.
→ HOW TO ASK: Say "Nir, please paste [exactly what file/section/URL] so I can [what you need it for]." Be specific with filenames.

--- BEGIN HANDOFF ---

You are Parent 7. You received this alongside the Commentaries, the Old Testament, the New Testament, and the DIGESTED PRINCIPIA (below). Your mission is to design the first real level — choosing Newton propositions, defining the content pipeline run, and specifying the audio atmosphere. Read §0–§3 for context, §4 is your design space, §5–§6 are frozen constraints, and §8 is your deliverable format.

§0 — WHAT EXISTS (so you know what you're building on top of)

Engine (285/285 green):
  M-1: contracts.py, glguard.py, conftest.py
  M0:  gfx_context.py, shaders.py, app.py (full §5.4 per-frame loop)
  M1:  camera.py, input_actions.py, render_wire.py, guidelines.py, nav_collision.py
  M6:  assets.py, render_room.py, readmode.py
  M7:  state.py, gameplay.py

Content pipeline (Legs 1+2+3, 186/186 green):
  Leg 1 (MAP):   9 modules — concept graph extraction, force layout, level_maker → floorplan.json
  Leg 2 (WALLS): 8 modules — Asymptote figure pipeline, text baking, overlay-diff → manifest.json + PNGs
  Leg 3 (ROOMS): 5 modules — Room Maker v3 with bearing-accurate doors → room_runtime/*.json

Golden Fixture Pack (tests/golden_pack/):
  3 hand-authored rooms (r_a, r_b, r_c), 3 corridors with bridge/underpass crossing,
  19 assets (16 panel + 3 ceiling), 38 PNGs. load_pack passes, full loop smokes.

App.py:
  Full §5.4 per-frame loop wired — event-driven save, Read-Mode overlay,
  mode switching corridor↔room, smoke test runs 60 frames with golden pack.

The Principia data (NEW — v2):
  We now have the COMPLETE 1729 Motte translation of Book 1 from Wikisource —
  14 sections, 148 items (29 lemmas, 98 propositions, 21 scholia), ~548 KB of clean text.
  The full text is stored on GitHub at: quake/principia/book_1/section_01.txt through section_14.txt
  The DIGESTED PRINCIPIA (below) summarizes every single item in one sentence with figure counts.
  YOU have the DIGEST. Use it to choose propositions. Ask Nir to paste the full text
  of any section when you need the details.

What does NOT exist yet (your mission):
  - A real level with real Newton propositions (r_a/r_b/r_c are hand-authored dummies)
  - Audio — no SFX, no music, no atmosphere
  - Figure background transparency (deferred)
  - Mode A text labels in the wireframe (deferred, post-M7 polish)

§1 — YOUR MISSION (one mission, nothing else)

Design the first real Principia level. This means:

(a) Choose a SMALL subset of Newton propositions — 3 to 5 — that form a
    coherent dependency chain. The first level should be achievable. Think:
    Lemma I → Lemma II → Prop. I (or similar). The golden pack's 3 rooms
    already prove the full loop; the first real level can be 3–5 rooms.

(b) Define the concept graph — which nodes exist, what edges connect them
    (citations from the text), importance ratings, the dependency structure.

(c) Specify exactly what the Leg 1+2+3 build pipeline will produce:
    - nodes_raw.json → concept_graph.json → floorplan.json (Leg 1)
    - recipe + Asymptote figures → baked PNGs + manifest.json (Leg 2)
    - room_source → room_runtime (Leg 3, Room Maker v3)

(d) Design the audio SFX layer — what sounds play when, what format,
    how they integrate into app.py's event system. God-mode means no
    player death sounds. Think: footstep loop (corridor), panel-flip click,
    demon growl/spawn, demon hit, demon death, room-cleared chime,
    door-open rumble, ceiling blood-red hum.

(e) Define the level's palette (color groups for the figure elements) —
    pick 3–5 group names with hi/ink hex pairs.

(f) The output of your design feeds DeepSeek and the build pipeline —
    NOT a child. The AI pipeline (Legs 1+2+3) is already built; DeepSeek
    runs it with your specs as input.

§2 — THE BUILD PIPELINE (what DeepSeek will run from your spec)

Your deliverable is a SPECIFICATION. DeepSeek then:

  1. Runs STRUCTURE AI → nodes_raw.json (from your chosen propositions)
  2. Runs CITATION AI → citations_raw.json
  3. Runs INFERENCE AI → inference_raw.json
  4. Runs merge.py → concept_graph.json + provenance.json
  5. Runs level_maker → floorplan.json
  6. For each node: READER AI → recipe.figure_id.json
  7. For each node: EMITTER AI → figure.figure_id.asy
  8. Runs asy_compile + baker_figure + baker_text → PNGs + manifest.json
  9. Runs portal_spec + room_maker → room_runtime/*.json
  10. DeepSeek places all outputs under a level directory and tests

You do NOT design the AI prompts (those are frozen in the Second Canon §3).
You DO choose: which propositions, which pages, what importance, what
color groups, what audio cues.

§3 — HOW TO GET MORE INFORMATION (the material-request protocol)

You have the DIGESTED PRINCIPIA (below) which summarizes every lemma,
proposition, and scholium in one sentence with figure counts. Use it FIRST
to decide what you need.

If you need the FULL TEXT of a section, ask Nir to paste it:
  → "Nir, please paste section_02.txt from GitHub so I can read Props I-VIII in full."
  The files live at: https://github.com/strulovitz/peaktogether-website/blob/master/quake/principia/book_1/section_NN.txt
  (NN = 01 through 14)

If you need FIGURE IMAGES from the original Principia plates, ask Nir:
  → "Nir, please fetch the scan for Plate 2 Figure 5 from Wikisource."
  The scans are at: https://en.wikisource.org/wiki/The_Mathematical_Principles_of_Natural_Philosophy_(1729)

If you need more scripture sections beyond what you have (Commentaries + OT + NT), ask Nir:
  → "Nir, please paste §3.A.5 from the Second Canon (the Op→Asymptote mapping)."
  or: "Nir, please paste the Apocrypha §3 (RoomRuntime v3, DoorRT)."
  Nir will ask DeepSeek (the Runner) to fetch the exact section from the BIBLE files on disk.

If you need the EXACT PYDANTIC SCHEMAS (contracts), ask:
  → "Nir, please paste the relevant models from contracts.py."
  Nir will ask DeepSeek to extract them.

If you need the GOLDEN FIXTURE PACK for reference (the 3 hand-authored rooms):
  → "Nir, please paste floorplan.json and one room_runtime file from the golden pack."
  The golden pack is at: quake/tests/golden_pack/

RULES:
  1. Always use the DIGEST first to decide WHAT to ask for.
  2. Be specific — give the exact filename or scripture section.
  3. Don't ask for everything at once — one or two sections at a time.
  4. The full text sections are large (20-70 KB each). Only request what you truly need to design the level.
  5. Remember: Nir knows no math and no code. Describe what you need in plain language.

§4 — YOUR DESIGN SPACE (open questions to resolve)

A. Which propositions? Choose 3–5 that form a dependency chain where
   A depends on nothing (axiom/law), B depends on A, C depends on B, etc.
   The golden pack proved 3 rooms work end-to-end; start similar.
   SUGGESTED STARTING POINTS from the DIGEST:
   - Section I (Lemmas I-XI): The mathematical toolbox. Lemma II (limits) → Lemma X (s∝t²)
   - Section II (Props I-VIII): Centripetal forces, Kepler's 2nd law, v²/r
   - Section III (Props XI-XVII): Inverse-square law for conic sections (the famous result)
   - The Laws of Motion (Axioms) are also available as nodes

B. Which figures? Each proposition may have one or more figures. The DIGEST
   tells you how many drawings each item has. Pick items WITH DRAWINGS —
   the figure is the visual centerpiece of each room.

C. What proof steps? Each figure's construction is segmented into steps
   (the "Stabilo" highlighting layers). For each proposition, define
   how many steps the proof has and a one-line gloss per step.

D. Importance 1–5 per node? What's central to the section (importance 5)
   vs. supporting (importance 3) vs. peripheral (importance 1)?

E. Audio design: Footsteps, panel flip, demon spawn/hit/kill, room cleared,
   door open, level complete. Format? .wav? .ogg? Separate audio.py module?

F. Palette: Choose 3–5 group names + hi/ink hex pairs.

G. Level structure: level_id convention e.g. "principia_bk1_sec1".

§5 — FROZEN FORMATS (the pipeline's inputs/outputs)

Your spec produces data that feeds these exact formats (Second Canon §3–§4):

INPUTS to the pipeline (you specify):
  - Which pages to feed to STRUCTURE/CITATION/INFERENCE AI
  - Which figure scans to feed to READER AI
  - The color groups + hi/ink pairs for palette.json
  - The level_id, edition string, seed

OUTPUTS from the pipeline (generated, you verify the plan):
  - nodes_raw.json (§3.A.1) — one RawNode per proposition
  - citations_raw.json (§3.A.2) — verbatim citations linking nodes
  - inference_raw.json (§3.A.3) — AI's understanding-based edge guesses
  - concept_graph.json (§4.2) — merged DAG, nodes + edges
  - floorplan.json (§4.4) — force-directed layout, rooms + corridors + crossings
  - recipe.figure_id.json (§3.A.4) — coordinate-free Asymptote construction ops
  - figure.figure_id.asy (§3.A.5) — 4-zone Asymptote file
  - manifest.json (§4.6) — baked asset index
  - room_runtime/room_node_id.json (Apocrypha §3 + Second Canon §4.5) — v3 doors
  - palette.json (§3.A.7) — all hex, group colors, map_importance 1–5

§6 — FROZEN CONSTRAINTS (do not violate)

- Room System v3 (Apocrypha): door count = node degree, door direction = corridor bearing, room-local axes parallel to map, spawn heading = bearing + π.
- God-mode: player cannot die, infinite ammo.
- One demon per room, behind the final-proof wall.
- Correctness = fidelity to the printed page (overlay-diff tool judges).
- Color: all hex in palette.json; group names are the keys.
- ID spine: node_id flows unchanged through every format.
- schema_version "1.0", extra="forbid" on all JSON.
- Audio is ADDITIVE — a new audio.py module plus app.py wiring. Do NOT change engine modules.
- The level is built by the existing pipeline; you do NOT redesign the pipeline.

§7 — WHAT YOU ALREADY HAVE + WHAT TO PULL FROM THE BIBLE

You have:
  ✓ The Commentaries (BIBLE INDEX + locked decisions)
  ✓ The Old Testament (Fusion's master doctrine)
  ✓ The New Testament (The Two Legs — MAP + WALLS)
  ✓ THIS handoff (mission brief)
  ✓ The DIGESTED PRINCIPIA (below — summaries of all 14 sections + 148 items)

Before finalizing your design, you SHOULD also pull and design against (ask Nir):
  - Second Canon §3.A.1–§3.A.7 (AI-emitted formats — the schema of every pipeline output)
  - Second Canon §4.2–§4.8 (generated data formats — concept_graph, floorplan, room_runtime)
  - Second Canon §5.2 (build module signatures — to understand what each pipeline step does)
  - The Apocrypha §3 (RoomRuntime v3, DoorRT — to verify your room design is coherent)
  - The app.py event system (ask for contracts.py Events class or Parent 6 handoff §5.3)

§8 — YOUR DELIVERABLE FORMAT

Produce a single document containing:

1. Level plan: level_id, edition string, which book/section, which 3–5 propositions, their page numbers, importance ratings, and the dependency chain (which cites which).

2. Concept graph specification: a directed graph with node names, local_labels, kinds, importance 1–5, pages, one-line summaries, and edges with verbatim citation phrases and page_seen.

3. Figure plan: per proposition, which figure from the printed text to use, how many proof steps, a one-line gloss per step, and which color groups tag which elements.

4. Palette: group names + hi/ink hex pairs + map_importance hexes for 1–5.

5. Audio design: every SFX with trigger condition, emotional intent, and technical integration notes (format, looping, how to wire into app.py's event system). Recommend whether audio lives in its own module (audio.py) or inline in app.py.

6. Build order: the exact sequence of AI passes + scripts DeepSeek runs, with their inputs and expected outputs.

7. Acceptance gates:
   - Gate 1: Full 285-test suite still green (no regressions)
   - Gate 2: New level's load_pack(dir) returns a valid Pack
   - Gate 3: Floorplan produced by level_maker is a valid DAG with crossings
   - Gate 4: At least one figure passes asy_compile + overlay-diff fidelity check
   - Gate 5: app.py runs the new level, 60-frame smoke test exits 0
   - Gate 6: All rooms have doors[].spawn_xyz/spawn_heading_rad matching bearings

8. Format: prose + fenced code blocks, NO Markdown tables (Nir copy-pastes; tables lose cells).

§9 — RISK FLAGS

- The AI pipeline (Legs 1+2+3) is built but has NEVER been run on real Principia data. The first run WILL uncover integration issues.
- Asymptote compilation is the highest-risk step.
- The overlay-diff tool (human verification) is what judges figure correctness — NOT mathematical truth. Nir eyeballs two images side by side.
- Audio integration is new territory — no audio module exists. Design the interface cleanly.
- Figure background transparency: for the first level, bake on bg_key (#FF00FF) and key it out.

§10 — CONVENTIONS (frozen)

- All IDs lowercase ASCII: node_id ^[a-z][a-z0-9_]*$, pair_id .s[0-9]+, etc.
- Wall literals: "N","E","S","W" uppercase only.
- Hex: ^#[0-9a-fA-F]{6}$.
- Coordinates: XZ map plane, Y up.
- schema_version "1.0" on every JSON.
- extra="forbid" on every pydantic model.
- All types imported from contracts (never directly from map/raw_models).

§11 — AFTER YOU

DeepSeek runs the pipeline. If any AI pass fails, DeepSeek reports the failure. Your spec feeds the integration loop. You do NOT need to design for integration failures — that's DeepSeek's job.

This is the milestone that turns Quake from a wireframe shell into a real game with Newton's own words and drawings on the walls. The DIGESTED PRINCIPIA is your map. Design boldly. 🔥📖

--- END HANDOFF ---
--- BEGIN DIGESTED PRINCIPIA ---

# 📖 DIGESTED PRINCIPIA — Book 1 (1729 Motte Translation)

> **Parent-safe summary.** Each lemma, proposition, scholium gets one sentence + figure count.
> Use this to choose propositions for the concept graph without reading the full text.
> Source: Wikisource — https://en.wikisource.org/wiki/The_Mathematical_Principles_of_Natural_Philosophy_(1729)

---

## ❖ INTRODUCTORY MATERIAL (before the Sections)

### DEFINITIONS (Definitions I–VIII)

- **Def I** — Quantity of matter is the measure arising from density and bulk conjunctly (mass). — 0 drawings
- **Def II** — Quantity of motion is the measure arising from velocity and quantity of matter conjunctly (momentum). — 0 drawings
- **Def III** — The vis insita (innate force of matter / inertia) is a power of resisting, by which every body perseveres in its present state of rest or uniform rectilinear motion. — 0 drawings
- **Def IV** — An impressed force is an action exerted upon a body to change its state of rest or uniform rectilinear motion. — 0 drawings
- **Def V** — A centripetal force is that by which bodies are drawn, impelled, or any way tend towards a point as to a centre (includes gravity, magnetism, planetary forces). — 0 drawings
- **Def VI** — The absolute quantity of a centripetal force is the measure proportional to the efficacy of the cause that propagates it from the centre. — 0 drawings
- **Def VII** — The accelerative quantity of a centripetal force is the measure proportional to the velocity it generates in a given time. — 0 drawings
- **Def VIII** — The motive quantity of a centripetal force is the measure proportional to the motion it generates in a given time (weight). — 0 drawings

### SCHOLIUM (after Definitions)

- **Absolute vs Relative** — Time, space, place, and motion are distinguished into absolute/relative, true/apparent, mathematical/common; the rotating bucket experiment proves absolute motion exists. — 0 drawings

### AXIOMS / LAWS OF MOTION

- **Law I** — Every body perseveres in its state of rest or uniform rectilinear motion unless compelled to change by impressed forces (inertia). — 0 drawings
- **Law II** — The alteration of motion is proportional to the motive force impressed and is made in the direction of the right line in which that force is impressed (F=ma). — 0 drawings
- **Law III** — To every action there is always opposed an equal reaction: the mutual actions of two bodies upon each other are always equal and directed to contrary parts. — 0 drawings
- **Corollary I** — A body by two forces conjoined describes the diagonal of a parallelogram in the same time it would describe the sides by those forces apart. — WITH 1 DRAWING
- **Corollary II** — Composition and resolution of forces; explains mechanical powers (balance, lever, wheel, wedge, screw, pully). — WITH 1 DRAWING
- **Corollary III** — The quantity of motion (sum of conspiring, difference of contrary) suffers no change from the action of bodies among themselves (conservation of momentum). — 0 drawings
- **Corollary IV** — The common centre of gravity of bodies does not alter its state of motion or rest by their mutual actions. — 0 drawings
- **Corollary V** — The motions of bodies in a given space are the same whether that space is at rest or moves uniformly forward (Galilean relativity). — 0 drawings
- **Corollary VI** — Equal accelerative forces in parallel directions do not change the relative motions of bodies among themselves. — 0 drawings

### SCHOLIUM (after Laws)

- **Experimental confirmation** — Galileo's law of falling bodies, parabolic projectiles; Wren, Wallis, Huygens on collision rules; pendulum experiments confirm Law III; mutual gravitation of Earth and its parts; loadstone experiment. — WITH 2 DRAWINGS

---

## BOOK 1: THE MOTION OF BODIES

---

### SECTION I: Of the method of first and last ratios (Lemmas I–XI)

> **The mathematical toolbox:** limits, ultimate ratios, the geometry of evanescent quantities. These lemmas justify treating curves as limits of polygons — the foundation for all subsequent propositions.

- **Lemma I** — Quantities and ratios of quantities which converge continually to equality in any finite time become ultimately equal. — 0 drawings
- **Lemma II** — The inscribed, circumscribed, and curvilinear figures under diminishing parallelograms have ultimate ratios of equality (justifies the "method of exhaustion"). — WITH 1 DRAWING (Pl.1 Fig.6)
- **Lemma III** — Same as Lemma II but with unequal breadths of the parallelograms — the result still holds. — 0 drawings
- **Lemma IV** — If corresponding parallelograms in two figures have the same ultimate ratio, the whole figures are in that same ratio. — WITH 1 DRAWING (Pl.1 Fig.7)
- **Lemma V** — In similar figures, homologous sides are proportional and areas are in the duplicate ratio of the homologous sides. — WITH 1 DRAWING (Pl.2 Fig.1)
- **Lemma VI** — The angle between the chord and tangent at any point of an arc vanishes as the points approach each other. — WITH 1 DRAWING (Pl.2 Fig.1)
- **Lemma VII** — The ultimate ratio of the arc, chord, and tangent to one another is the ratio of equality (arc ≈ chord ≈ tangent at the limit). — WITH 1 DRAWING (Pl.2 Fig.1)
- **Lemma VIII** — Three triangles formed by the arc, chord, tangent, and a radius ultimately become similar and equal to each other. — 0 drawings
- **Lemma IX** — If ordinates to a curve meet a right line at given angles, the areas of the resulting triangles are ultimately in the duplicate ratio of the sides. — 0 drawings
- **Lemma X** — Spaces described by a body under any finite force in the very beginning of motion are in the duplicate ratio of the times (s ∝ t²). — 0 drawings
  - Cor. 2 — Errors generated by proportional forces are as the forces and squares of the times conjunctly.
  - Cor. 4 — Forces are as the spaces described directly and squares of the times inversely.
- **Lemma XI** — In curves of finite curvature, the evanescent subtense of the angle of contact is ultimately in the duplicate ratio of the subtense of the conterminate arc. — WITH 1 DRAWING (Pl.2 Fig.4)
- **Scholium (after Lemma X)** — Explains the meaning of "directly" and "inversely" proportional language for indeterminate quantities. — 0 drawings
- **Scholium (after Lemma XI)** — On infinite series of angles of contact; the method of first and last ratios is equivalent to indivisibles but uses limits of divisible quantities; an ultimate ratio is the ratio WITH WHICH quantities vanish, not before or after. — 0 drawings

---

### SECTION II: Of the invention of centripetal forces (Propositions I–X)

> **The core of orbital mechanics:** Kepler's laws geometrically derived, the inverse-square law emerges.

- **Prop I (Th I)** — Areas described by radii to an immovable centre are in immovable planes and proportional to the times (Kepler's Second Law, geometric proof). — WITH 1 DRAWING (Pl.2 Fig.5)
- **Prop II (Th II)** — Conversely: every body describing areas proportional to times about a point is urged by a centripetal force directed to that point. — 0 drawings
- **Prop III (Th III)** — Generalization to two bodies: a body describing equal areas about a moving centre is urged by a compound centripetal force. — 0 drawings
- **Prop IV (Th IV)** — For uniform circular motion, centripetal forces tend to the centres and are as v²/r (or as r/T²). — 0 drawings
  - Cor. 6 — The case of inverse-square force obtains in the celestial bodies (as observed by Wren, Hooke, Halley).
- **Prop V (Pr I)** — Given the velocity of a body describing a figure about a centre of force, find that centre geometrically. — WITH 1 DRAWING (Pl.3 Fig.1)
- **Prop VI (Th V)** — The centripetal force in the middle of a nascent arc is as the versed sine directly and the square of the time inversely. — WITH 1 DRAWING (Pl.3 Fig.2)
  - Cor. 1 — Force ∝ 1/[(SP² × QT²)/QR] — the key formula for computing force laws from orbits.
- **Prop VII (Pr II)** — For a body revolving in a circle, find the law of centripetal force directed to ANY given point (not just the centre). — WITH 2 DRAWINGS (Pl.3 Fig.3,4)
  - Cor. 1 — If force tends to a point on the circumference: force ∝ 1/(distance^5).
- **Prop VIII (Pr III)** — For a body in a semicircle with force tending to a point so remote all lines are parallel: force ∝ 1/(altitude³). — WITH 1 DRAWING (Pl.3 Fig.5)
- **Prop IX (Pr IV)** — For a body in an equiangular spiral: the centripetal force is reciprocally as the cube of the distance. — WITH 1 DRAWING (Pl.3 Fig.6)
- **Lemma XII** — All parallelograms circumscribed about conjugate diameters of a given ellipse or hyperbola are equal. — 0 drawings
- **Prop X (Pr V)** — For a body in an ellipse with force to the CENTRE: force is directly as the distance from centre (harmonic oscillator). — WITH 1 DRAWING (Pl.4 Fig.1)
  - Cor. 2 — All periodic times about the same centre are equal.
  - Scholium — If centre recedes infinitely, ellipse→parabola, force becomes constant (Galileo); if centre reverses, force becomes centrifugal.

---

### SECTION III: Of the motion of bodies in eccentric conic sections (Propositions XI–XVII)

> **The inverse-square law for ellipses, hyperbolas, and parabolas** — the mathematical heart of the Principia.

- **Prop XI (Pr VI)** — For a body in an ELLIPSE with force to the FOCUS: centripetal force ∝ 1/(distance²). — WITH 1 DRAWING (Pl.4 Fig.2)
- **Prop XII (Pr VII)** — For a body in a HYPERBOLA with force to the focus: force ∝ 1/(distance²). — WITH 1 DRAWING (Pl.5 Fig.1)
- **Lemma XIII** — The latus rectum of a parabola at any vertex is quadruple the distance from vertex to focus. — 0 drawings
- **Lemma XIV** — The perpendicular from the focus of a parabola to its tangent is a mean proportional between the distances from focus to point of contact and to vertex. — WITH 1 DRAWING (Pl.5 Fig.2)
- **Prop XIII (Pr VIII)** — For a body in a PARABOLA with force to the focus: force ∝ 1/(distance²). — WITH 1 DRAWING (Pl.5 Fig.3)
  - Cor. 1 — A body under reciprocal-square force moves in one of the three conic sections with focus at force centre.
- **Prop XIV (Th VI)** — For bodies about a common centre with inverse-square force, the principal latera recta are in the duplicate ratio of areas described in equal times. — WITH 1 DRAWING (Pl.6 Fig.1)
- **Prop XV (Th VII)** — Periodic times in ellipses under inverse-square force are in the sesquiplicate ratio (T ∝ a^(3/2)) of their greater axes (Kepler's Third Law). — 0 drawings
- **Prop XVI (Th VIII)** — Under inverse-square force, velocities relate to perpendiculars from focus to tangent and to latera recta. — WITH 1 DRAWING (Pl.6 Fig.2)
  - Cor. 4 — At mean distance in ellipse, velocity equals circular orbit velocity ∝ 1/√r.
  - Cor. 7 — In parabola, velocity at any distance is √2 × circular velocity; less in ellipse, greater in hyperbola.
- **Prop XVII (Pr IX)** — Given initial position, velocity, and direction under a known inverse-square force, determine the orbit (ellipse/parabola/hyperbola). — WITH 1 DRAWING (Pl.6 Fig.3)
  - Scholium — Method to find centripetal force law for any conic section with force to any given point. — WITH 1 DRAWING (Pl.6 Fig.4)

---

### SECTION IV: Of the finding of orbits from the focus given (Props XVIII–XXI)

> **Orbit construction problems:** given a focus and some points/tangents, construct the conic trajectory.

- **Lemma XV** — If from two foci of an ellipse/hyperbola, lines to V have HV = axis and SV bisected by perpendicular TR, then TR touches the conic. — WITH 1 DRAWING (Pl.7 Fig.1)
- **Prop XVIII (Pr X) [*sic — actually Lemma XVI in source*]** — From a given focus and axis, describe elliptical or hyperbolic trajectories through given points and touching given lines. — WITH 1 DRAWING (Pl.7 Fig.2)
- **Prop XIX (Pr XI) [*sic*]** — About a given focus, describe a parabolic trajectory through given points and touching given lines. — WITH 1 DRAWING (Pl.7 Fig.3)
- **Prop XX (Pr XII) [*sic*]** — About a given focus, describe any trajectory given in species (shape fixed, scale variable) through given points and touching given lines. — WITH 5 DRAWINGS (Pl.7 Fig.4–7B)
- **Lemma XVI [*sic — actually Lemma XIX*]** — From three given points, find a fourth point such that differences of lines drawn to it are given. — WITH 1 DRAWING (Pl.8 Fig.1)
- **Prop XXI (Pr XIII) [*sic*]** — About a given focus, describe a trajectory passing through given points and touching given lines; the other focus H is found. — WITH 1 DRAWING (Pl.8 Fig.2)
  - Scholium — Shortcut for three given points; De la Hire's solution referenced. — WITH 1 DRAWING (Pl.8 Fig.3)

---

### SECTION V: How the orbits are to be found when neither focus is given (Lemmas XVII–XXVII, Props XXII–XXIX)

> **Projective geometry and the "Problem of Four Lines":** constructing conics from points and tangents using the method of transformation.

- **Lemma XVII** — For any point P on a conic through a trapezium's vertices, the rectangle of lines to one pair of opposite sides has a given ratio to the rectangle of lines to the other pair. — WITH 3 DRAWINGS (Pl.8 Fig.4–6)
- **Lemma XVIII** — Converse of Lemma XVII: if the rectangle ratio holds, P lies on a conic through the trapezium. — WITH 1 DRAWING (Pl.8 Fig.7)
- **Lemma XIX** — Given four lines by position, find point P such that lines drawn at given angles produce rectangles in a given ratio (solves the ancient "Problem of Four Lines"). — WITH 2 DRAWINGS (Pl.8 Fig.8, Pl.9 Fig.1)
- **Lemma XX** — If two opposite vertices of a parallelogram touch a conic and the sides meet the conic again, segments on the other two sides from a fifth conic point have a given ratio. — WITH 1 DRAWING (Pl.9 Fig.2)
  - Cor. 2 — One conic section cannot cut another in more than FOUR points.
- **Lemma XXI** — If two movable lines through fixed poles trace a right line, and two other lines make given angles with them, their intersection traces a conic. — WITH 2 DRAWINGS (Pl.9 Fig.3,4)
- **Prop XXII (Pr XIV)** — Describe a trajectory through FIVE given points. — WITH 2 DRAWINGS (Pl.9 Fig.5,6)
- **Prop XXIII (Pr XV)** — Describe a trajectory through FOUR given points and touching one given line. — WITH 3 DRAWINGS (Pl.10 Fig.1–3)
- **Prop XXIV (Pr XVI)** — Describe a trajectory through THREE given points and touching TWO given lines. — WITH 1 DRAWING (Pl.10 Fig.4)
- **Lemma XXII** — Any figure can be transformed into another of the same analytical order (conics to circles, converging lines to parallels) by projective transformation. — WITH 1 DRAWING (Pl.10 Fig.5)
- **Prop XXV (Pr XVII)** — Describe a trajectory through TWO given points and touching THREE given lines. — WITH 1 DRAWING (Pl.10 Fig.6)
- **Prop XXVI (Pr XVIII)** — Describe a trajectory through ONE given point and touching FOUR given lines. — WITH 1 DRAWING (Pl.11 Fig.1)
- **Lemma XXIII** — If two lines AC, BD given in position and terminating at given points have a given ratio, and CD is cut at K in a given ratio, K lies on a given right line. — WITH 1 DRAWING (Pl.11 Fig.2)
- **Lemma XXIV** — If three lines touch a conic and two are parallel, the semi-diameter parallel to them is a mean proportional between the intercepted segments. — WITH 1 DRAWING (Pl.11 Fig.3)
- **Lemma XXV** — If four sides of a parallelogram touch a conic and are cut by a fifth tangent, segments on conterminous sides follow a given proportion. — WITH 1 DRAWING (Pl.11 Fig.4)
  - Cor. 3 — The line through midpoints of Eq and eQ passes through the centre of the conic.
- **Prop XXVII (Pr XIX)** — Describe a trajectory touching FIVE given right lines. — WITH 1 DRAWING (Pl.11 Fig.5)
  - Scholium — Extends to cases with given centres or asymptotes; finds axes and foci of described trajectory. — WITH 1 DRAWING (Pl.12 Fig.1)
- **Lemma XXVI** — Place a given triangle so its three angles touch three given lines (using circular segments of given angles). — WITH 1 DRAWING (Pl.12 Fig.2)
- **Prop XXVIII (Pr XX)** — Describe a trajectory given in kind and magnitude whose given parts are intercepted between three given lines. — WITH 1 DRAWING (Pl.12 Fig.3)
- **Lemma XXVII** — Place a given trapezium so its four angles touch four given lines. — WITH 1 DRAWING (Pl.12 Fig.4)
- **Prop XXIX (Pr XXI)** — Describe a trajectory given in kind that is cut by four given lines into parts given in order, kind, and proportion. — WITH 1 DRAWING (Pl.13 Fig.1)

---

### SECTION VI: How the motions are to be found in given orbits (Props XXX–XXXI)

> **Kepler's Problem:** find the position of a body in its orbit at any given time.

- **Prop XXX (Pr XXII)** — Find the place of a body at any assigned time in a PARABOLIC trajectory. — WITH 1 DRAWING (Pl.14 Fig.1)
- **Lemma XXVIII** — No oval figure exists whose area cut off by arbitrary lines can be found by any finite equation (Kepler's equation has no closed-form solution; requires infinite series). — 0 drawings
- **Prop XXXI (Th XXIII)** — Find the place of a body in an ELLIPTIC trajectory at any assigned time, using a cycloid construction. — WITH 1 DRAWING (Pl.14 Fig.2)
  - Scholium — Approximation methods: converging infinite series for ellipse; logarithmic method for hyperbola; astronomical shortcut for small eccentricities. — WITH 3 DRAWINGS (Pl.14 Fig.3–5)

---

### SECTION VII: Concerning the rectilinear ascent and descent of bodies (Props XXXII–XXXIX)

> **Free fall under inverse-square force:** bodies falling directly toward a centre.

- **Prop XXXII (Pr XXIV)** — Under inverse-square force, the space fallen in a given time is found by making an auxiliary area (on a semicircle) proportional to the time. — WITH 3 DRAWINGS (Pl.15 Fig.1–3)
- **Prop XXXIII (Th IX)** — Under inverse-square force, velocity at any place during rectilinear fall is compared to circular orbit velocity. — WITH 1 DRAWING (Pl.15 Fig.4)
- **Prop XXXIV (Th X)** — For parabolic fall under inverse-square force, velocity at any place equals circular velocity at half the distance. — WITH 1 DRAWING (Pl.15 Fig.5)
- **Prop XXXV (Th XI)** — The area described by the auxiliary radius SD equals the area described in the same time by uniform circular motion. — WITH 2 DRAWINGS (Pl.16 Fig.1,2)
- **Prop XXXVI (Pr XXV)** — Determine the time of descent from a given place A (by equating sectors to auxiliary areas). — WITH 1 DRAWING (Pl.16 Fig.3)
- **Prop XXXVII (Pr XXVI)** — Determine times of ascent/descent for a body projected with any velocity from a given place. — WITH 1 DRAWING (Pl.16 Fig.4)
- **Prop XXXVIII (Th XII)** — When centripetal force is proportional to distance (harmonic): times, velocities, spaces are proportional to arcs, right sines, and versed sines. — WITH 1 DRAWING (Pl.17 Fig.1)
  - Cor. 2 — All bodies falling to the centre from ANY distance take the SAME time (isochronous).
- **Prop XXXIX (Pr XXVII)** — For ANY centripetal force law (granting quadratures): velocity is as √(area under force curve), and time as area under reciprocal velocity curve. — WITH 1 DRAWING (Pl.17 Fig.2)

---

### SECTION VIII: Of the invention of orbits for any centripetal force (Props XL–XLII)

> **General orbit-finding:** for arbitrary force laws, using quadratures.

- **Prop XL (Th XIII)** — If a body moves in any curve and another falls rectilinearly, and their velocities are equal at one equal altitude, they are equal at ALL equal altitudes. — WITH 1 DRAWING (Pl.17 Fig.3)
- **Prop XLI (Pr XXVIII)** — For any centripetal force (granting quadratures), find both the trajectory and the time of motion. — WITH 1 DRAWING (Pl.18 Fig.1)
  - Cor. 5 — For inverse-CUBE force, the trajectory relates to a conic section; body descends to centre if conic is hyperbola, recedes infinitely if ellipse.
- **Prop XLII (Pr XXIX)** — Given the force law and initial conditions (place, velocity, direction), determine the entire motion. — WITH 1 DRAWING (Pl.18 Fig.2)

---

### SECTION IX: Of the motion of bodies in movable orbits; and of the motion of the apsides (Props XLIII–XLV)

> **Revolving orbits and precession:** what happens when the orbit itself rotates.

- **Prop XLIII (Pr XXX)** — A body can be made to move in a trajectory that REVOLVES about the centre of force. — WITH 1 DRAWING (Pl.18 Fig.1)
- **Prop XLIV (Th XIV)** — The difference of forces for motion in a revolving vs. quiescent orbit is in the triplicate ratio of altitudes inversely. — WITH 1 DRAWING (Pl.18 Fig.2)
  - Cor. 2 — For an ellipse with inverse-square force, the revolving-orbit force = 1/r² + (something)/r³.
- **Prop XLV (Pr XXXI)** — The motion of the APSIDES in nearly circular orbits: apsidal angle = 180°/√n where force ∝ 1/rⁿ. — 0 drawings
  - Exam. 1 — Uniform centripetal force: apsidal angle ≈ 103°55′.
  - Exam. 2 — Force ∝ 1/rⁿ: apsidal angle = 180°/√n.
  - Cor. 1 — From apsidal motion, the force law can be deduced; force must decrease faster than 1/r³ for body to reach an apsis.

---

### SECTION X: Of the motion of bodies in given superficies; and of the reciprocal motion of funependulous bodies (Props XLVI–LVI)

> **Constrained motion:** pendulums, cycloids, isochronous oscillations.

- **Prop XLVI (Pr XXXII)** — Motion of a body on a given surface about a centre of force is determined by resolving the force. — WITH 1 DRAWING (Pl.18 Fig.4)
- **Prop XLVII (Th XV)** — If centripetal force ∝ distance, all bodies in any planes describe ellipses and complete revolutions in equal times. — 0 drawings
- **Prop XLVIII (Th XVI)** — Cycloid on the OUTSIDE of a globe: its length relates to the versed sine of the contacted arc. — WITH 2 DRAWINGS (Pl.19 Fig.1,2)
- **Prop XLIX (Th XVII)** — Cycloid on the INSIDE of a globe: analogous relation with difference of diameters. — 0 drawings
- **Prop L (Pr XXXIII)** — Make a pendulum oscillate in a given cycloid by suspending it from the cusp of an exterior cycloid (cycloidal cheeks → isochronous pendulum). — WITH 1 DRAWING (Pl.19 Fig.3)
- **Prop LI (Th XVIII)** — If centripetal force ∝ distance on a body oscillating in a cycloid, all oscillations are ISOCHRONOUS (equal time regardless of amplitude). — WITH 1 DRAWING (Pl.19 Fig.4)
- **Prop LII (Pr XXXIV)** — Velocities and times of pendulums in cycloids; time of oscillation relates to semi-periphery. — WITH 1 DRAWING (Pl.20 Fig.1)
- **Prop LIII (Pr XXXV)** — Find forces that make oscillations isochronous in any given curve (force ∝ TZ where TY = arc TR). — WITH 1 DRAWING (Pl.20 Fig.2)
  - Cor. 1 — For a circular arc, make downward force ∝ arc/sine of arc for isochronism. — WITH 1 DRAWING (Pl.20 Fig.3)
- **Prop LIV (Pr XXXVI)** — Time of descent/ascent in any curve under any force found by making curvilinear area proportional to time. — WITH 1 DRAWING (Pl.20 Fig.4)
- **Prop LV (Th XIX)** — If a body moves on any curve surface whose axis passes through the centre of force, its projection on a perpendicular plane sweeps equal areas in equal times. — WITH 1 DRAWING (Pl.20 Fig.5)
- **Prop LVI (Pr XXXVII)** — Given force law and surface, find the trajectory from initial conditions using orthographic projection. — WITH 1 DRAWING (Pl.20 Fig.6)

---

### SECTION XI: Of the motions of bodies tending to each other with centripetal forces (Props LVII–LXIX)

> **The N-body problem:** mutual attractions, the three-body problem, lunar theory preview.

- **Prop LVII (Th XX)** — Two bodies attracting each other describe similar figures about their common centre of gravity and about each other. — 0 drawings
- **Prop LVIII (Th XXI)** — With any forces, two bodies revolving about their common centre of gravity describe equal figures around either body considered unmoved. — WITH 1 DRAWING (Pl.20 Fig.7)
  - Cor. 1 — If force ∝ distance: concentric ellipses about common centre of gravity.
  - Cor. 2 — If force ∝ 1/r²: conic sections with focus at the centre about which figures are described.
- **Prop LIX (Th XXII)** — Periodic time of two bodies about their common centre is to the time of one about the other fixed as √(S/(S+P)). — 0 drawings
- **Prop LX (Th XXIII)** — Principal axis of two-body ellipse relates to the one-body-about-fixed case by a mean proportional. — 0 drawings
- **Prop LXI (Th XXIV)** — Motions of two mutually attracting bodies are the same as if a third body at their common centre of gravity attracted both with the same force law. — 0 drawings
- **Prop LXII (Pr XXXVIII)** — Determine motions of two bodies with inverse-square forces let fall from given places. — 0 drawings
- **Prop LXIII (Pr XXXIX)** — Determine motions of two bodies with inverse-square forces going off from given places with given velocities and directions. — 0 drawings
- **Prop LXIV (Pr XL)** — If mutual attractions ∝ distance, motion of SEVERAL bodies: all describe ellipses with equal periods about common centre of gravity. — WITH 1 DRAWING (Pl.21 Fig.1)
- **Prop LXV (Th XXV)** — Bodies with inverse-square forces may move in ellipses VERY NEARLY when one body is vastly greater or vastly more distant. — 0 drawings
- **Prop LXVI (Th XXVI)** — THE THREE-BODY PROBLEM: if three bodies attract with inverse-square forces and two less revolve about the greatest, the innermost describes areas more proportional to times and a more nearly elliptical figure when the great body is agitated. — WITH 1 DRAWING (Pl.21 Fig.2)
  - Cor. 1–22 — Detailed analysis of perturbations: apsidal motion, eccentricity changes, nodal regression, latitude variation, ebb and flow of the sea, precession of equinoxes.
- **Prop LXVII (Th XXVII)** — The exterior body describes areas more proportional to times about the common centre of gravity than about the innermost. — WITH 1 DRAWING (Pl.21 Fig.3)
- **Prop LXVIII (Th XXVIII)** — Orbits approach ellipses more nearly when forces are mutual and foci are at common centres of gravity. — 0 drawings
- **Prop LXIX (Th XXIX)** — In a system of mutually attracting inverse-square bodies, the absolute attractive forces are proportional to the bodies themselves (mass ∝ gravitational "charge"). — 0 drawings

---

### SECTION XII: Of the attractive forces of sphærical bodies (Props LXX–LXXXIV)

> **The Shell Theorem and its consequences:** spherical bodies attract as if all mass were at the centre.

- **Prop LXX (Th XXX)** — A corpuscle INSIDE a spherical surface feels NO net attraction (forces cancel). — WITH 1 DRAWING (Pl.21 Fig.4)
- **Prop LXXI (Th XXXI)** — A corpuscle OUTSIDE a spherical surface is attracted toward the centre with force ∝ 1/(distance²). — WITH 1 DRAWING (Pl.21 Fig.5)
- **Prop LXXII (Th XXXII)** — For a homogeneous sphere, the force on an external corpuscle ∝ (semi-diameter)³/(distance²) = ∝ mass/(distance²). — 0 drawings
- **Prop LXXIII (Th XXXIII)** — A corpuscle INSIDE a homogeneous sphere is attracted with force ∝ distance from centre. — WITH 1 DRAWING (Pl.21 Fig.6)
- **Prop LXXIV (Th XXXIV)** — A corpuscle OUTSIDE a homogeneous sphere: force ∝ 1/(distance²) (the full Shell Theorem, proven by integration). — 0 drawings
- **Prop LXXV (Th XXXV)** — One similar sphere attracts ANOTHER with force ∝ 1/(distance²) between centres. — 0 drawings
  - Cor. 3 — All results about conic-section orbits hold when an attracting sphere is placed at the focus.
- **Prop LXXVI (Th XXXVI)** — Same for spheres with radially varying but spherical-symmetrical density. — WITH 1 DRAWING (Pl.22 Fig.1)
- **Prop LXXVII (Th XXXVII)** — If particle forces ∝ distance: mutual force between two spheres ∝ distance between centres. — WITH 2 DRAWINGS (Pl.22 Fig.2,3)
- **Prop LXXVIII (Th XXXVIII)** — Same for spheres with radial variation when particle force ∝ distance. — 0 drawings
- **Lemma XXIX** — Auxiliary lemma for evanescent arcs and ratios (Pl.22 Fig.4). — WITH 1 DRAWING
- **Prop LXXIX (Th XXXIX)** — Force of an evanescent spherical concavo-convex solid on a corpuscle. — WITH 1 DRAWING (Pl.22 Fig.5)
- **Prop LXXX (Th XL)** — General method: the whole force on corpuscle P is proportional to the area ANB under a constructed curve. — WITH 1 DRAWING (Pl.22 Fig.6)
  - Cor. 1–4 — Cases for constant force, 1/r, 1/r³, and general V.
- **Prop LXXXI (Pr XLI)** — Measuring area ANB for specific force laws (examples: 1/r, 1/r³, 1/r⁴). — WITH 3 DRAWINGS (Pl.23 Fig.1–3)
- **Prop LXXXII (Th XLI)** — Relation of attraction inside vs. outside a sphere where SI, SA, SP are continually proportional. — WITH 1 DRAWING (Pl.23 Fig.4)
- **Prop LXXXIII (Pr XLII)** — Force on a corpuscle at the CENTRE of a sphere toward any SEGMENT of it. — WITH 1 DRAWING (Pl.23 Fig.5)
- **Prop LXXXIV (Pr XLIII)** — Force on a corpuscle on the AXIS of a segment but NOT at the centre. — WITH 1 DRAWING (Pl.23 Fig.6)

---

### SECTION XIII: Of the attractive forces of non-sphærical bodies (Props LXXXV–XCIII)

> **Irregular bodies:** contact forces, attraction of planes, cylinders, spheroids.

- **Prop LXXXV (Th XLII)** — If a body's attraction is vastly stronger at contact than at any separation, particle forces decrease faster than 1/r². — 0 drawings
- **Prop LXXXVI (Th XLIII)** — If particle forces decrease as 1/r³ or faster, attraction is vastly stronger at contact than at finite separation. — 0 drawings
- **Prop LXXXVII (Th XLIV)** — For similar bodies of equally attractive matter, accelerative attractions toward whole bodies are as those toward corresponding particles. — 0 drawings
- **Prop LXXXVIII (Th XLV)** — If particle forces ∝ distance, the whole body's force tends to its centre of gravity and equals a globe of similar matter there. — WITH 1 DRAWING (Pl.23 Fig.7)
- **Prop LXXXIX (Th XLVI)** — Same for SEVERAL bodies: compounded force tends to common centre of gravity. — 0 drawings
- **Prop XC (Pr XLIV)** — Force with which a corpuscle is attracted toward a CIRCLE (for any force law varying with distance). — WITH 1 DRAWING (Pl.24 Fig.1)
  - Cor. 3 — For an infinite plane with n > 1, attraction ∝ 1/PA^(n−2).
- **Prop XCI (Pr XLV)** — Attraction of a corpuscle on the AXIS of a round solid (cylinder, spheroid). — WITH 3 DRAWINGS (Pl.24 Fig.2–5)
  - Cor. 1 — For inverse-square cylinder: attraction ∝ AB − PE + PD.
  - Cor. 2 — For a spheroid on an external axial corpuscle.
  - Cor. 3 — Corpuscle WITHIN a spheroid on its axis: attraction ∝ distance from centre.
- **Prop XCII (Pr XLVI)** — Experimentally determine the force law of an attracting body by measuring attractions at several distances. — 0 drawings
- **Prop XCIII (Th XLVII)** — For an infinite plane solid with particle forces ∝ 1/rⁿ (n ≥ 3): whole attraction ∝ 1/d^(n−3). — WITH 2 DRAWINGS (Pl.24 Fig.6,7)

---

### SECTION XIV: Of the motion of very small bodies (Props XCIV–XCVIII)

> **Optical analogy:** tiny corpuscles deflected by forces — Newton's corpuscular theory of light.

- **Prop XCIV (Th XLVIII)** — If a body passes between two parallel-plane mediums with perpendicular attraction equal at equal distances, the sine of incidence: sine of emergence is in a given ratio (Snell's Law analog). — WITH 2 DRAWINGS (Pl.25 Fig.1,2)
- **Prop XCV (Th XLIX)** — Velocity before incidence : velocity after emergence = sine of emergence : sine of incidence. — WITH 1 DRAWING (Pl.25 Fig.3)
- **Prop XCVI (Th L)** — If incidence is swift enough and the ray is continually inclined, the body will be reflected with angle of reflexion = angle of incidence. — WITH 1 DRAWING (Pl.25 Fig.4)
  - Scholium — These attractions resemble the reflexions and refractions of light (Snellius, Descartes); the inflection of light rays near bodies. — WITH 2 DRAWINGS (Pl.25 Fig.6,7)
- **Prop XCVII (Pr XLVII)** — Given a fixed sine ratio, find the surface that makes all corpuscles from one place converge to another (focusing). — WITH 1 DRAWING (Pl.25 Fig.8)
  - Cor. 1 — Produces all of Descartes's refraction figures.
- **Prop XCVIII (Pr XLVIII)** — Given a first attractive surface about an axis, find a second surface to make rays converge (compound lens analog). — WITH 1 DRAWING (Pl.25 Fig.10)

---

## 📊 SUMMARY STATISTICS

| Section | Lemmas | Propositions | Scholia | Total Items | Distinct Figures |
|---------|--------|-------------|---------|-------------|-------------------|
| I (First & last ratios) | 11 | 0 | 3 | 14 | 6 |
| II (Centripetal forces) | 1 | 10 | 4 | 15 | 8 |
| III (Eccentric conics) | 2 | 7 | 1 | 10 | 8 |
| IV (Orbits from focus) | 2 | 4 | 1 | 7 | 11 |
| V (Orbits, no focus) | 11 | 8 | 3 | 22 | 17 |
| VI (Motions in orbits) | 1 | 2 | 1 | 4 | 5 |
| VII (Rectilinear fall) | 0 | 8 | 0 | 8 | 11 |
| VIII (Any force orbits) | 0 | 3 | 0 | 3 | 3 |
| IX (Movable orbits) | 0 | 3 | 0 | 3 | 3 |
| X (Pendulums, surfaces) | 0 | 11 | 1 | 12 | 11 |
| XI (Mutual attraction) | 0 | 13 | 1 | 14 | 4 |
| XII (Spherical bodies) | 1 | 15 | 3 | 19 | 15 |
| XIII (Non-spherical) | 0 | 9 | 1 | 10 | 8 |
| XIV (Small bodies/light) | 0 | 5 | 2 | 7 | 9 |
| **TOTAL** | **29** | **98** | **21** | **148** | **119** |

### Depends-on chains (for concept graph design):
- **Section I** — foundation for ALL subsequent math (limits, ultimate ratios)
- **Section II** — builds on §I; Props I–III establish equal-area → centripetal; Prop IV gives v²/r
- **Section III** — builds on §I–II; Props XI–XIII prove inverse-square for all conics; Prop XV = Kepler's Third Law
- **Sections IV–V** — orbit construction geometry, independent of dynamics
- **Sections VI–VII** — time-in-orbit problems, builds on §III
- **Sections VIII–IX** — general force laws, builds on §I–III
- **Sections X** — pendulums, builds on §I–III + Laws
- **Sections XI** — N-body, builds on §I–III (the heart of celestial mechanics)
- **Section XII** — Shell Theorem, builds on §I
- **Sections XIII–XIV** — applications (optics, irregular bodies)

---

*Generated from Wikisource 1729 Motte translation. Full text in `book_1/section_*.txt`. Use this digest to design the concept graph for Parent 7.*
