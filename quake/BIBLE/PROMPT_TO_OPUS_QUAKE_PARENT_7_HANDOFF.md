🗝️ QUAKE (Game 3) — PROMPT TO OPUS: PARENT 7 HANDOFF v2 (M8 FIRST PRINCIPIA LEVEL)

Written June 26, 2026 by DeepSeek (Runner). Updated June 28, 2026 (v2 — added DIGESTED PRINCIPIA + material-request protocol). Parents 1–6 are DONE. The full engine (13 modules, 285 tests) is built and wired; the Golden Fixture Pack (3 hand-authored rooms) proves the entire runtime stack works end-to-end. Parent 7 has exactly ONE mission: design the FIRST REAL Principia level — transforming Quake from a tech demo with dummy rooms into an actual game powered by Newton's text.

⚠️ CRITICAL — HOW YOU GET INFORMATION ⚠️
You are an Opus chat inside OpenRouter. You have NO internet access, NO GitHub access, NO file system access. You CANNOT browse, download, or read anything on your own. The only text you have is what is pasted into this chat — this handoff + the Commentaries + the OT + the NT + the DIGESTED PRINCIPIA below.
If you need ANYTHING else (full text of a proposition, a figure image, a format specification, a scripture section), you must ASK NIR to copy-paste it for you. Nir is your hands and eyes — he can fetch things from GitHub, Wikisource, or the local filesystem.
→ HOW TO ASK: Say "Nir, please paste [exactly what file/section/URL] so I can [what you need it for]." Be specific with filenames.

--- BEGIN HANDOFF ---

You are Parent 7. You received this alongside the Commentaries, the Old Testament, the New Testament, and the DIGESTED PRINCIPIA (below). Your mission is to design the first real level — choosing Newton propositions and defining the content pipeline run. Read §0–§3 for context, §4 is your design space, §5–§6 are frozen constraints, and §8 is your deliverable format.

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

(d) Define the level's palette (color groups for the figure elements) —
    pick 3–5 group names with hi/ink hex pairs.

(e) The output of your design feeds DeepSeek and the build pipeline —
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
color groups.

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

E. Palette: Choose 3–5 group names + hi/ink hex pairs.

F. Level structure: level_id convention e.g. "principia_bk1_sec1".

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

5. Build order: the exact sequence of AI passes + scripts DeepSeek runs, with their inputs and expected outputs.

6. Acceptance gates:
   - Gate 1: Full 285-test suite still green (no regressions)
   - Gate 2: New level's load_pack(dir) returns a valid Pack
   - Gate 3: Floorplan produced by level_maker is a valid DAG with crossings
   - Gate 4: At least one figure passes asy_compile + overlay-diff fidelity check
   - Gate 5: app.py runs the new level, 60-frame smoke test exits 0
   - Gate 6: All rooms have doors[].spawn_xyz/spawn_heading_rad matching bearings

7. Format: prose + fenced code blocks, NO Markdown tables (Nir copy-pastes; tables lose cells).

§9 — RISK FLAGS

- The AI pipeline (Legs 1+2+3) is built but has NEVER been run on real Principia data. The first run WILL uncover integration issues.
- Asymptote compilation is the highest-risk step.
- The overlay-diff tool (human verification) is what judges figure correctness — NOT mathematical truth. Nir eyeballs two images side by side.
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
