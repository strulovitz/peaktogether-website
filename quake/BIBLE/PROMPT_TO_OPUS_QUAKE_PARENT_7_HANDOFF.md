🗝️ QUAKE (Game 3) — PROMPT TO OPUS: PARENT 7 HANDOFF (M8 FIRST PRINCIPIA LEVEL)

Written June 26, 2026 by DeepSeek (Runner). Parents 1–6 are DONE. The full engine (13 modules, 285 tests) is built and wired; the Golden Fixture Pack (3 hand-authored rooms) proves the entire runtime stack works end-to-end. Parent 7 has exactly ONE mission: design the FIRST REAL Principia level — transforming Quake from a tech demo with dummy rooms into an actual game powered by Newton's text. This handoff is self-contained — Parent 7 can begin immediately with the four baseline documents (Commentaries + OT + NT + this handoff) and the on-demand pulls listed in §7.

--- BEGIN HANDOFF ---

You are Parent 7. You received this alongside the Commentaries, the Old Testament, and the New Testament. Your mission is to design the first real level — choosing Newton propositions, defining the content pipeline run, and specifying the audio atmosphere. Read §0–§3 for context, §4 is your design space, §5–§6 are frozen constraints, and §8 is your deliverable format.

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

The Principia source data:
  We have a clean OCR text file of the 1846 Andrew Motte English translation
  (_djvu.txt), per-page scans (leaf_*.png), and a page-numbers JSON mapping
  leaf_index → printed page label. Nir has these files — ask him where they
  live and he or DeepSeek will give you the exact paths and formats.

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

(e) Define the level's palatte (color groups for the figure elements) —
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
  6. For each node: READER AI → recipe.<figure_id>.json
  7. For each node: EMITTER AI → figure.<figure_id>.asy
  8. Runs asy_compile + baker_figure + baker_text → PNGs + manifest.json
  9. Runs portal_spec + room_maker → room_runtime/*.json
  10. DeepSeek places all outputs under a level directory and tests

You do NOT design the AI prompts (those are frozen in the Second Canon §3).
You DO choose: which propositions, which pages, what importance, what
color groups, what audio cues.

§3 — THE PRINCIPIA DATA (what Nir has)

Nir has:
  - A _djvu.txt file — clean OCR of the full Motte 1846 translation,
    split by page (form-feed characters separate pages)
  - Leaf PNGs — one scanned page image per leaf (leaf_0001.png, etc.)
  - A page-numbers JSON — maps leaf_index (0-based) to printed page label
    (e.g. leaf 74 → "55") in the format:
    {"pages": [{"leafNum": 1, "pageNumber": ""}, ...]}
    (This is the Archive.org hocr-pages format v2, fed to page_map_adapter.py)

Nir also knows the Principia structure: which lemmas/propositions appear
on which pages. Ask him for: (a) the file paths, (b) what book/section to
start with, and (c) any specific propositions he wants featured.

FOR NOW: assume Book I, Section I (the method of first and last ratios,
Lemmas I–XI) or Section II (centripetal forces, Prop. I–IV). These are
the most famous and figure-rich sections.

§4 — YOUR DESIGN SPACE (open questions to resolve)

A. Which propositions? Choose 3–5 that form a dependency chain where
   A depends on nothing (axiom/law), B depends on A, C depends on B, etc.
   The golden pack proved 3 rooms work end-to-end; start similar.

B. Which figures? Each proposition may have one or more figures in the
   printed text. Pick the single most iconic figure per proposition as
   the room's figure. Newton's own engravings are the source of truth.
   The READER AI will produce the Asymptote construction recipe from
   the figure scan; the overlay-diff tool verifies fidelity.

C. What proof steps? Each figure's construction is segmented into steps
   (the "Stabilo" highlighting layers). For each proposition, define
   how many steps the proof has and a one-line gloss per step. The
   TEXT AI produces the LaTeX explaining-text block per step.

D. Importance 1–5 per node? What's central to the section (importance 5)
   vs. supporting (importance 3) vs. peripheral (importance 1)? This
   drives room size on the map and map color.

E. Audio design:
   - Footsteps: looped corridor SFX (how many variants? stereo panning?)
   - Panel flip: click/snap when a panel is lit
   - Demon spawn: growl/roar from behind the hidden wall
   - Demon hit: grunt/pain (1–3 variants)
   - Demon kill: death cry
   - Room cleared: chime / tone that transitions to blood-red ceiling hum
   - Door open: rumble / stone grind
   - Level complete: fanfare
   - Music: ambient drone for corridors? or silent?
   What format? .wav? .ogg? How integrated — pyglet's media player?
   A separate audio.py module?

F. Palette: Choose 3–5 group names for the figure elements (e.g. "path",
   "radius", "construction", "orbit", "force") and assign hi/ink hex pairs.
   These group names couple figure color to prose color via \cg{group}{text}.

G. Level structure: Should the first level be a self-contained "chapter"
   or a slice of a larger book? The level_id convention is e.g.
   "principia_bk1_sec1". Decide the scope.

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
  - recipe.<figure_id>.json (§3.A.4) — coordinate-free Asymptote construction ops
  - figure.<figure_id>.asy (§3.A.5) — 4-zone Asymptote file
  - manifest.json (§4.6) — baked asset index
  - room_runtime/room_<node_id>.json (Apocrypha §3 + Second Canon §4.5) — v3 doors
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

§7 — WHAT TO PULL FROM THE BIBLE (request via Nir → DeepSeek)

You have the Commentaries + OT + NT. Before designing, pull and design against:
- Second Canon §3.A.1–§3.A.7 (AI-emitted formats — the schema of every pipeline output)
- Second Canon §4.2–§4.8 (generated data formats — concept_graph, floorplan, room_runtime)
- Second Canon §5.2 (build module signatures — to understand what each pipeline step does)
- The Apocrypha §3 (RoomRuntime v3, DoorRT — to verify your room design is coherent)
- The PROMPT_TO_OPUS_QUAKE_PARENT_6_HANDOFF.md (§5.3 — the app.py event system audio will hook into)

You also need from Nir: the Principia file paths, the book/section to start with, and any proposition preferences.

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

- The AI pipeline (Legs 1+2+3) is built but has NEVER been run on real Principia data. The first run WILL uncover integration issues. Expect them. Design your spec to be exact enough that failures are clearly diagnosed.
- Asymptote compilation is the highest-risk step — the Op→Asymptote translation table (§3.A.5) marks Asymptote function names as ⟨confirm-from-docs⟩. The compile loop is how we confirm them.
- The overlay-diff tool (human verification) is what judges figure correctness — not mathematical truth, not AI confidence. Nir eyeballs two images side by side. If the figure looks wrong, the recipe needs adjustment.
- Audio integration is new territory — no audio module exists. Design the interface cleanly so it doesn't couple to engine internals.
- Figure background transparency is still an open choice (Second Canon closing notes). For the first level, bake on bg_key (#FF00FF) and key it out — the simpler path.

§10 — CONVENTIONS (frozen)

- All IDs lowercase ASCII: node_id ^[a-z][a-z0-9_]*$, pair_id ^[a-z][a-z0-9_]*\.s[0-9]+$, etc.
- Wall literals: "N","E","S","W" uppercase only.
- Hex: ^#[0-9a-fA-F]{6}$.
- Coordinates: XZ map plane, Y up.
- schema_version "1.0" on every JSON.
- extra="forbid" on every pydantic model.
- All types imported from contracts (never directly from map/raw_models).

§11 — THE NEXT THING AFTER YOU

After your spec is frozen, DeepSeek runs the pipeline. If any AI pass fails, DeepSeek reports the failure and Nir re-runs the AI with adjusted prompts. The output feeds DeepSeek's integration loop — build, test, fix wiring, push. You do NOT need to design for integration failures — that's DeepSeek's job.

This is the milestone that turns Quake from a wireframe shell into a real game with Newton's own words and drawings on the walls. Design it boldly. The pipeline is waiting. 🗝️📚✨

--- END HANDOFF ---

DeepSeek (Runner). Parent 7 — the Principia awaits. 🔥📖
