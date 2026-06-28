# PROMPT TO OPUS — QUAKE PARENT 12: REGULAR-POLYGON ROOMS (replace the rectangular box)

> DeepSeek-authored handoff. Written June 28, 2026 (night) to be launched tomorrow. Baseline launch files for this parent = the Commentaries + the Old Testament + the Apocrypha (Room System v3 — the room design you are revising) + this handoff. Uses the question-first material protocol; ends WITHOUT "GO."

---

You are Parent 12. Welcome. Your mission is a focused, high-quality redesign of the **room interior shape**.

------------------------------------------------------------
0) THE WORKING MODEL + A STANDING RULE THAT GOVERNS THIS MISSION
- You are the ARCHITECT. You write design + frozen contracts + child briefs — OR corrected code directly if cleaner. Children build; DeepSeek integrates, runs the regression suite, RENDERS-and-looks (not just "it compiles"), and pushes. Nir decides everything; Nir knows NO code and NO math.
- You have NO internet / file access, but DeepSeek can see the whole codebase and every scripture and will answer your QUESTIONS with exact verbatim excerpts (see §8). You never need whole files dumped on you.
- ⚠️ **STANDING RULE (the reason this mission exists):** Do NOT silently pick the easy implementation and freeze it as "the design." When a choice trades QUALITY for EASE, name BOTH options and SURFACE the tradeoff to Nir before anything is frozen. This whole mission exists because a cheap rectangular room got frozen as the de-facto standard, and Nir rejects it. The bar here is Doom-or-better, not Wolfenstein.

------------------------------------------------------------
1) WHAT NIR WANTS (his requirement — capture it exactly)
The room's **floor and ceiling are a REGULAR POLYGON** (equal edges, equal angles). The walls rise vertically from each edge (a regular-N-gon prism). The number of edges N is **not fixed** — it is computed per room:

    N  =  2 × P  +  D

  - **P** = the number of explanation **step-pairs** in this room. Each step-pair is ONE geometry **drawing** panel + ITS neighboring **LaTeX** panel that explains that drawing. Each step-pair therefore contributes **2 edges** (one for the drawing, one for its LaTeX) — that's the "× 2".
  - **D** = the number of **doors** in this room (= the node's degree = how many corridors connect it to neighbor rooms). Each door is **1 edge**.

So **every edge of the polygon holds exactly ONE "block": a drawing panel, a LaTeX panel, or a door.** Nothing else lives on a wall; there is one block per edge.

Adjacency requirement: a step-pair's **drawing edge and its LaTeX edge are ADJACENT** (side by side), so the reader sees a drawing next to the text that explains it.

N varies per room: more explanation steps → more edges; more connections to other rooms → more edges. (Concrete examples: a room with 3 step-pairs and 2 doors → N = 2·3 + 2 = **8** edges. The existing golden-pack room `r_a` has 2 step-pairs and 2 doors → N = 2·2 + 2 = **6** edges, a hexagon.)

This is the visible realization of the original vision: a room is a **circle on the map**; a regular N-gon echoes that circle; and its size is **TARDIS** (driven by contents, never by the map).

------------------------------------------------------------
2) WHY (the stakes)
The current rooms are axis-aligned rectangular boxes with 4 walls (N/E/S/W) and doors snapped to those 4 walls — **Wolfenstein-3D-grade** geometry, below Doom (1993), which already had arbitrary-angle walls and non-rectangular sectors. There is NO engine limitation (moderngl draws arbitrary 3D fine); the box was chosen purely because it is easy. Nir is (rightly) unwilling to ship that. This redesign brings room geometry up to the project's actual ambition.

------------------------------------------------------------
3) FROZEN — DO NOT TOUCH (the load-bearing structure)
None of these change; they are the foundation and they are proven by ~252 tests that must stay green:
- The MAP layer: `concept_graph`, `level_maker`, `layout_force` / `layout_height`, `floorplan`, corridors, crossings, and `render_wire` (Mode A wireframe). Rooms are circles/points on the map; corridors connect node-centers, never room walls.
- The CONTENT/BAKE pipeline (Legs 1–2) and the ID-spine grammar.
- **THE MAP→ROOM SEAM stays EXACTLY as-is.** This is the one real coupling between the outside and the room, and you keep it unchanged: `portal_spec(floorplan, graph, node_id) -> RoomPortalSpec` hands the room a list of **door bearings**, one per incident corridor: `IncidentEdge.bearing_rad = atan2(neighborZ − nodeZ, neighborX − nodeX)`. The room CONSUMES these bearings to orient its doors; nothing flows back to the map. Keep this input contract identical.

------------------------------------------------------------
4) WHAT YOU REDESIGN (the room "wing" only)
- **Room contract(s)** (currently in `map/raw_models.py`, surfaced via `contracts.py`): replace the box shape with a polygon shape. Today `RoomRuntime.dimensions_m: Vec3` is a (W,H,D) box; `DoorRT.wall: Literal["N","E","S","W"]` and `PanelPlacementRT.wall` lock blocks to 4 cardinal walls. Re-define these for a regular N-gon: an edge count / circumradius (or edge length) + height, and per-block **edge index** instead of `wall`. Re-freeze cleanly (still `schema_version "1.0"`, `extra="forbid"`).
- **`room_maker`** (BUILD): build the regular N-gon with N = 2P + D; assign door-edges to honor their true bearings (see §5); place each step-pair's drawing + LaTeX on two adjacent edges; TARDIS-size it (regular ⇒ all edges equal; edge length from the widest block + margins); materialize panels, doors, the hidden-door alcove (final pair's drawing edge), and ceiling equations.
- **`render_room`** (RUNTIME): draw the N-gon prism — floor + ceiling polygons, a vertical wall per edge, with a door hole on door-edges and the panel flush on panel-edges, lit. (NOTE: DeepSeek already fixed culling, two-sided lighting, texture resolution, panel-flatness, and ceiling z-fight in the current box renderer — carry those fixes forward.)
- **room `nav_collision`** (RUNTIME): player collision against the polygon walls; passable door intervals; `door_at(point)`.

------------------------------------------------------------
5) THE ONE REAL TENSION — RECONCILE IT, DON'T SILENTLY DECIDE
A **regular** polygon has edges at fixed angular positions (360°/N apart). Door **bearings are arbitrary** angles. You therefore CANNOT make a regular polygon AND place every door at its exact bearing — they conflict. With many edges, the per-door angular error is small. You must decide HOW to reconcile this (e.g., choose the polygon's rotation to minimise total bearing error; assign each door to the edge whose outward direction is nearest its bearing; possibly reserve specific edges for doors). **Design your approach, state its tradeoff plainly, and surface it to Nir BEFORE freezing.** (This is exactly the kind of quality-vs-ease fork the standing rule in §0 is about — the rectangle "solved" it by brutally snapping to 4 walls; you can do far better with N edges, but say how.)

------------------------------------------------------------
6) DELIVERABLE
- Design + the re-frozen room contracts + child briefs (or corrected code), plus a **golden polygon-room fixture** and acceptance criteria.
- DeepSeek will: integrate; keep the ~252 foundation tests (content pipeline + layout) GREEN — they never touch rooms, so they prove the foundation didn't move; and **render the room and look at it** (offscreen pixel check + Nir's eyeball), not merely run headless tests.

------------------------------------------------------------
7) DE-RISK PATH (prove-before-commit — strongly preferred)
There is an isolated tool, `tools/room_viewer.py`, that loads ONE room and lets a human fly inside it — it touches nothing else. **Prototype the polygon room there FIRST** (a hand-made polygon fixture is fine), render it, and let Nir SEE it BEFORE any frozen contract changes. Only after Nir approves the look do we propagate the new shape into the real contracts + room_maker. This converts "pull a card and pray" into "prove it in isolation, then commit."

------------------------------------------------------------
8) HOW YOU GET INFORMATION (keeps your context alive)
Ask DeepSeek precise QUESTIONS (batched, cross-cutting welcome); you get back EXACT VERBATIM excerpts. Think "what do I need to know," not "which file." Likely things to request: the current `RoomRuntime` / `DoorRT` / `PanelPlacementRT` / `BuildConfig` definitions; the current `room_maker` algorithm; `render_room`'s draw shell; the room `nav` builder; Second Canon §4.5 (room source/runtime) and the panel-sizing BuildConfig fields; a golden-pack room JSON. Whole-file only for a small file you'll rewrite end to end.

------------------------------------------------------------
9) IRON RULES
- Design against VERBATIM contracts, never paraphrases. Surface (don't silently resolve) any conflict with a frozen decision. Honesty: invent nothing; mark gaps. No Markdown tables in copy-paste material. Don't assert GL/library names from memory.

------------------------------------------------------------
10) HOW WE START (the rhythm — no "GO")
Do not start designing yet. First reply with (a) your understanding of this mission in your own words, and (b) your first batch of precise questions. We confirm, you design in small confirmed steps; we prototype in the viewer; Nir eyeballs; only then do we touch the contracts.

When you're ready, send your understanding and your first batch of questions.
