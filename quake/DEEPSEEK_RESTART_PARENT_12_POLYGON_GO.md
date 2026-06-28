# 🌅 DEEPSEEK RESTART — Parent 12: Regular-Polygon Rooms / June 28, 2026 (night)

> Read AFTER WORKFLOW.md + the Commentaries. Then ask Nir what's next. (Supersedes DEEPSEEK_RESTART_PARENT_10_GO.md.)

---

## WHERE WE ARE
- **Engine + renderer work is DONE and integrated.** Parent 11 delivered the full renderer (Mode A thick dimming wireframe + bloom; lit Mode B solid room; shared perspective). DeepSeek integrated all 5 files (382 tests green) and then fixed the real bugs Nir caught by **actually rendering and looking** (not "it compiles"):
  - missing walls = backface culling → `disable(CULL_FACE)` in room + wire renderers.
  - white "lines" on panels = textures never loaded → resolve via `pack.asset_dir`; grey fallback.
  - flat/dim shading → two-sided lighting + brighter ambient.
  - panels perpendicular to walls → orient panels from the `wall` field (data's yaw convention was swapped); verified flat (z-spread 0).
  - ceiling equation "shredded" = z-fight → drop the eq quad 0.05 m below the ceiling.
- **New tool:** `tools/room_viewer.py` — fly inside one Mode B room (keys: L panels-lit, C ceiling-red). Plus `tools/map_viewer.py` for Mode A.
- **THE BIG REALIZATION (Nir):** the rooms are axis-aligned rectangular boxes = **Wolfenstein-3D-grade**, below Doom. A cheap shortcut got frozen as the de-facto standard. Nir rejects it. → We are redesigning rooms as **regular polygons**.

## NIR'S POLYGON SPEC (the room redesign)
- Floor & ceiling = a **regular polygon** (prism walls).
- **N edges = 2 × P + D**: P = #step-pairs (each = 1 drawing/geometry panel + 1 neighboring LaTeX panel → 2 edges); D = #doors (= node degree → 1 edge each).
- **One block per edge**: drawing | LaTeX | door. A step-pair's drawing & LaTeX edges are ADJACENT.
- N varies per room (more steps → more edges; more doors → more edges). TARDIS size (from contents). Echoes the map circle.

## THE PLAN FOR TOMORROW
1. Launch **Parent 12 — Regular-Polygon Rooms**. Handoff: `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_12_POLYGON_ROOMS_HANDOFF.md`.
   - Launch files (give Nir these GitHub blob links to paste): **Commentaries + Old Testament + Apocrypha (Room System v3) + the Parent 12 handoff.**
2. Parent 12 designs; uses question-first material; **no GO**.
3. **De-risk:** prototype the polygon room in `tools/room_viewer.py` FIRST (hand-made polygon fixture) → Nir eyeballs → only then propagate to the real contracts + room_maker + render_room + room nav.
4. **The 20-room Newton CONTENT design (figures/recipes/LaTeX) is now deferred** to AFTER the room shape is right (call it Parent 13). Rooms must be the right shape before content goes in.

## FROZEN — DO NOT LET PARENT 12 TOUCH
- Map layer (concept_graph, level_maker, layout, floorplan, corridors, crossings, render_wire), the content/bake pipeline, the ID-spine.
- **The map→room seam stays fixed:** `portal_spec → RoomPortalSpec → IncidentEdge.bearing_rad` (door bearings, one-way map→room). The polygon redesign keeps this input identical; it only changes room-internal geometry.
- The ~252 foundation tests (content pipeline + layout) must stay GREEN — they prove the foundation didn't move.

## HARD-WON DISCIPLINES (do not regress)
- **Never freeze the easy option silently.** When a choice trades quality for ease, name BOTH and surface the tradeoff to Nir BEFORE freezing. The asymmetry (always the floor, never the ceiling) is the tell of reward-hacking.
- **Render-and-look, don't just compile.** "382 tests pass" only proves imports + pure logic; all GL is headless-guarded. For anything visual, render offscreen + check pixels + give Nir a PNG.
- Question-first material (verbatim excerpts, not whole files). No "GO" on handoffs. Protect parent context (one mission per parent). Don't call him "boss."

## KEY TENSION PARENT 12 MUST RECONCILE (surface, don't silently decide)
A regular polygon has edges at fixed angles (360/N apart) but door bearings are arbitrary → can't honor both exactly. With many edges the error is small. Parent 12 must choose a reconciliation (rotation to minimize bearing error / nearest-edge assignment) and SURFACE it to Nir.
