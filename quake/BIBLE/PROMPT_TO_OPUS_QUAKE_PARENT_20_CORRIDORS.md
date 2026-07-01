# PARENT 20 — MISSION: REAL 3D WIREFRAME CORRIDORS (BOX TUNNELS YOU WALK THROUGH)

> **Role:** You are a fresh Opus 4.8 architect. You design this yourself — **no children.**
> **Launch files (4, pasted by Nir):**
> 1. The Commentaries (`QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`)
> 2. Old Testament (`QUAKE_DOCTRINE_BY_FUSION.md`)
> 3. New Testament (`QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`)
> 4. **This handoff (the mission brief)**

---

## §0 — THE CURRENT FAILURE (why you are here)

There is currently NO real corridor between rooms. When the player exits a door, they see a 2D flat top-down map of circles and lines on the XZ plane — what Nir calls "the ugly map." This is completely wrong. A corridor IS a 3D wireframe box tunnel that the player walks through — the edges of the walls/floors/ceiling drawn as lines in 3D space, meeting the Old Testament spec exactly. The "ugly map" was a rendering mistake (drawing the floorplan from above), not a problem with the wireframe concept.

Your predecessor (Parent 18) failed because he interpreted "wireframe" as "fix the 2D map" instead of "build 3D box tunnels drawn as wireframe edges."

---

## §1 — THE SPEC (verbatim from the Old Testament §3.1)

This IS the corridor. Read every word:

> *"The player walks the concept graph as a live, glowing, see-through 3D map. Pure transit: no enemies, no panels, no shooting targets, no reading."*

> *"Wireframe only. Lines and node rings; no shaded polygons. 'Transparent' here means empty faces with visible edges, not alpha translucency."*

> *"Depth-tested, NO alpha blending. Depth test on, depth write on, blend off, depthFunc = LEQUAL. Near geometry occludes far. This is the single most important rendering decision."*

> *"Distance-dimming in the line shader: the current section renders near pure white, fading with view-space distance toward dark grey — never pure black (so far structure stays a faint felt presence; vanishing into black is what disorients)."*

> *"Crossings visible as true 3D over/under passes."*

> *"~3 floor guide-lines (Half-Life style), procedural, on the felt floor, with arrowheads, pointing to the selected destinations (rule in §8). They do double duty: navigation and vertigo mitigation (a committed 'floor' in a mode that otherwise has no ground plane)."*

**TRANSLATION FOR YOU:**
A corridor IS:
- A 3D box tunnel (walls, floor, ceiling) drawn as wireframe EDGES only — no filled surfaces, no shaded polygons
- The player stands INSIDE this 3D box, looking through its transparent edges
- The edges are pure white up close, dimming to dark grey far away (NEVER black)
- The floor has ≤3 colored guide-lines with arrowheads, painted onto the floor, one color per destination room
- Crossings: a corridor at height layer 2 passes physically OVER one at layer 1 — 3D over/under, edges drawn at true heights
- Depth-tested: the near edge of the box you're in occludes the far edge of a different corridor
- No blending, no alpha, no translucency — depth test is how occlusion works

A corridor is NOT:
- A 2D flat top-down map of circles and lines on the XZ plane (the current "ugly map")
- Filled solid surfaces (no shaded walls, no textured polygons)
- A teleport from one door to another

### Floor guide-lines (Old Testament §8.2)

> *"From the player's current/nearest node c, over uncleared reachable rooms: Slot 1 (always): the single nearest uncleared room (min graph_dist; tie → lowest id). Slots 2–3: by descending score with W_imp = 0.6, W_dist = 0.4, excluding slot 1. Fewer than 3 candidates → fewer lines (never invent lines)."*

> *"Each line follows the actual corridor route to its target, ends in an arrowhead, and is colored by the target's importance color (matching its map ring)."*

The guide-lines ALREADY EXIST in code. `select_targets()` in `guidelines.py` works and has 8 passing tests. `_arrowhead_xz()` builds correct arrowhead geometry. The routes are computed in `_route_xz()` using BFS through the corridor graph. The draw function `_gl_draw_strip()` is currently stubbed (returns immediately, does nothing). **You need to un-stub it** so the colored lines and arrowheads actually reach the GPU.

### Movement (Old Testament §8.3)

> *"Free walk with gentle rail assist. The Mover walks normally inside an invisible corridor collision volume (floor + soft side boundaries + ramps + platforms + room sockets) — you cannot fall through the wireframe."*

The player walks INSIDE the 3D box. The box has collision — walls, floor, ceiling keep the player contained. When the player reaches the far end, the existing door-entry transition fires (walking onto a room's socket teleports you into that room at its door spawn).

### Distance-dimming (how far corridors are seen)

> *"the current section renders near pure white, fading with view-space distance toward dark grey — never pure black."*

Every wireframe edge uses the dimming shader. The corridor the player is CURRENTLY IN is bright white up close. Other corridors in the distance are darker grey — visible, felt, never vanishing. The segments OF the current corridor that are farther from the player ALSO dim slightly — this creates the sense of depth within the tunnel itself.

---

## §2 — WHAT ALREADY EXISTS (verbatim from the real code)

### The wireframe renderer (Parent 11 — works, renders correctly)
`render_wire.py` already has:
- `build_wire_mesh(fp)` — builds line segments from the floorplan (corridor paths + room rings)
- `render_mode_a(ctx, window, view, proj, fp, state, guidelines_fn, targets)` — full Mode A pipeline: draws wireframe to offscreen FBO → bloom → composite to screen
- The shader (`wire_quad_program`) does thick camera-facing quads with distance-dimming (white→grey, never black), depth-tested, no blend
- `_draw_wire(ctx, fp, view, proj, aspect)` — the actual GL draw

**The problem:** this renderer draws the FLOORPLAN DATA (which is a 2D top-down graph — room rings at socket_y=0, corridor lines at cruise_y). It draws a MAP. What Nir wants is a 3D BOX TUNNEL the player is INSIDE. The tunnel's wireframe edges are the 12 edges of a rectangular box (4 bottom edges for the floor, 4 top edges for the ceiling, 4 vertical edges for the walls).

### Room rendering (solid — reference for "box" concept)
`draw_room(mvp, room, pack, state)` in `render_room.py` renders a solid room box. It knows how to build wall quads, floor, ceiling — with dimensions from `RoomRuntime.dimensions_m` which is `(W, H, D)`.

### Door data
`DoorRT` has: `edge_id`, `neighbor_id`, `wall` (N/E/S/W), `center_xyz`, `width_m`, `height_m`, `bearing_rad`, `normal_yaw_rad`.

### Door exit (gameplay.py ~130-165)
In room mode, `nav.door_at(state.pos)` returns the door's `edge_id`. Code finds the corridor in the floorplan, places player at room's `map_xz + 2m toward corridor`, heading toward far end. Emits `ModeSwitch(to="corridor", via_edge_id=eid)`.

### Door entry (gameplay.py ~166-190)
In corridor mode, player within `SOCKET_ENTER_RADIUS_M` of a room's `map_xz` → teleports into room at `room.doors[0].spawn_xyz`, heading `room.doors[0].spawn_heading_rad`.

### App dispatch (app.py ~468-480)
```python
if state.mode == "corridor":
    # currently calls render_mode_a() with the floorplan wireframe map
else:
    # draw_room() for room mode
```

### Guidelines code (guidelines.py)
- `select_targets(fp, current, cleared, cfg)` → list of ≤3 NodeId targets (WORKS, 8 tests green)
- `_route_xz(fp, current, target)` → XZ polyline along corridor path (WORKS)
- `_arrowhead_xz(p_prev, p_tip, size)` → left/tip/right barb points (WORKS)
- `draw_guidelines(view, fp, targets)` → orchestrates route + arrowhead — (WORKS for logic)
- `_gl_draw_strip(...)` → STUBBED, just `return` (DOES NOTHING — needs un-stubbing with real `wire_program(ctx)` GL draw)

### Floorplan data
`Floorplan` has: `rooms` (list of FloorRoom), `corridors` (list of Corridor with `source`, `target`, `path_xz`, `cruise_y`, `width_m`, `height_level`), `crossings` (list of Crossing with `over_corridor`, `under_corridor`, `at_xz`, `over_y`, `under_y`).

### TARDIS
Rooms don't share a coordinate system. A corridor is ALSO its own independent space — it does NOT live in the floorplan coordinate system. It's a standalone 3D box you walk through between two rooms.

---

## §3 — THE DESIGN YOU MUST DELIVER

### A. What IS the corridor?
A single 3D rectangular box (a tunnel). The player stands inside it. Its 12 edges are drawn as wireframe lines — thick, glowing, white-to-grey-with-distance. The floor has ≤3 colored guide-lines with arrowheads showing which way to walk. Reaching the far end triggers the existing room-entry mechanic.

### B. How the tunnel relates to doors
The player exits room A through door D_A (which is a rectangular opening on wall W_A). The corridor's entry face matches D_A's dimensions. The corridor runs straight for a length L (configurable, e.g. 8m). The corridor's exit face matches the destination door D_B's dimensions. The player walks through and arrives at room B.

Because of TARDIS, the corridor is its OWN coordinate space. It does not need to "be between" the two rooms in world space. It's a standalone 3D box you teleport into when you exit a room door, and teleport out of into the next room.

### C. Rendering
The corridor renders the 12 edges of its box (4 bottom, 4 top, 4 vertical) using the EXISTING wireframe shader (`wire_quad_program` — thick camera-facing quads, distance-dimming white→grey, depth-tested, no blend). No filled faces. No alpha. No shaded surfaces. Wireframe edges only.

In addition: the distant graph (other corridors, room rings) IS visible through the transparent box — the full floorplan wireframe renders faintly beyond the tunnel walls. This is the "see-through" promise of §3.1: the player sees the tunnel edges they're inside AND the rest of the glowing graph receding into grey distance.

### D. Guide-lines
The ≤3 colored guide-lines on the corridor floor. They follow BFS routes from the player's current/nearest node through the corridor graph to the selected target rooms. They ride the walkable floor height. Colored by target room's importance. Arrowheads at the tip. Rendered using the simple `wire_program(ctx)` (bright line strip, no dimming).

### E. Navigation
Box collision: walls, floor, ceiling constrain the player. At the far end, `door_at(point)` returns the destination door's `edge_id`, and the existing gameplay.py door-entry code handles the rest. Player walks inside the box toward the far end. Gentle rail assist toward the centerline.

### F. Crossings (bridges/underpasses) — THIS IS WHY THE GAME IS TRUE 3D

The floorplan already has full crossing data. Every corridor crossing has been detected and resolved at build time by `level_maker.py`. Here is the exact mechanism:

**How bridges and underpasses work:**

1. The force-directed graph layout produces corridors that cross each other in 2D (XZ plane).
2. `detect_crossings()` finds every pair of corridors whose paths intersect in XZ.
3. `assign_heights()` gives each corridor a `height_level` (0, 1, 2, ...). Crossing corridors get DIFFERENT levels. The higher one is the bridge; the lower one is the underpass.
4. `cruise_y = base_y + height_level * delta_y` — each corridor has its own cruising height in world Y.
5. The `crossings` list in Floorplan records: `over_corridor` (bridge), `under_corridor`, `at_xz` (where they cross in XZ), `over_y` (bridge height), `under_y` (underpass height). Assertion: `over_y > under_y`.
6. At a crossing, the bridge corridor edges are drawn at `over_y` (higher). The underpass edges are drawn at `under_y` (lower). The player sees in 3D: one tunnel passing physically OVER the other — the whole point of true-3D Quake, not flat Doom.

**Ramps:** A corridor starts at its room's floor level (`socket_y = 0.0`), ramps UP to its `cruise_y`, cruises, then ramps back DOWN to the destination room's floor. The edges of the corridor tunnel follow these ramp heights. The player walks the ramp — collision/floor tracks the rising height.

**What this means for your corridor design:** The 3D box tunnel edges must be drawn at the corridor's TRUE height (its `cruise_y` for the cruising section, linearly interpolated down to `socket_y` at the room ends). A bridge corridor's edges are several meters higher than the underpass corridor's edges. The player in the current tunnel sees the bridge's edges above them, the underpass's edges below — through the transparent wireframe box they stand inside.

**Concrete example from the real Principia floorplan:**
- `crossing_0`: `edge.prop_4.to.lemma_7` (bridge, `over_y=3.00m`) passes OVER `edge.lemma_11.to.lemma_6` (underpass, `under_y=0.00m`)
- The player walking `edge.prop_4.to.lemma_7` ramps up from 0m to 3m, cruises across the bridge at 3m, then ramps back down. Through the wireframe floor they see the underpass corridor 3m below.
- The player walking the underpass stays at ~0m and sees the bridge corridor 3m above them.

The Floorplan data you need: `Floorplan.corridors[i].cruise_y`, `Floorplan.crossings[i].over_y`, `Floorplan.crossings[i].under_y`, `FloorRoom.socket_y` (always 0.0).

### G. Acceptance criteria
- Exit door → player stands inside a 3D wireframe box tunnel (edges drawn, walls visible as lines)
- Floor has ≤3 colored guide-lines with arrowheads
- Edges dim with distance (near=white, far=grey, never black)
- Distant graph (other corridors, room rings) faintly visible through the box
- Walk through tunnel → reach far end → enter destination room at door spawn
- Crossings visible as 3D over/under wireframe passes
- Works for ANY connected room pair in the Principia pack

### H. Honest gaps
List anything you're unsure about.

---

## §4 — WHAT NOT TO DO

- Do NOT make a 2D top-down map. The corridor is a 3D box the player stands inside.
- Do NOT fill the box with solid shaded surfaces. Wireframe edges only.
- Do NOT use alpha blending. Depth test is the occlusion mechanism.
- Do NOT make edges fade to pure black. Dark grey floor only.
- Do NOT offer menus of options to Nir. Read the spec, build what it says.
- Do NOT tell Nir you lost his text and demand re-pastes.
- Do NOT write code. Design document only. DeepSeek implements.
- Do NOT ask questions the scripture already answers (all of §1 above).
- **"Tests pass" is NOT visual success.** Render and show a PNG.

---

## §5 — HOW TO GET MORE INFORMATION

Ask DeepSeek (via Nir) for exact verbatim sections. Useful files:
- `quake/render_wire.py` — the existing wireframe renderer (Parent 11, works)
- `quake/render_room.py` — how solid room boxes are built (reference for "box geometry")
- `quake/guidelines.py` — select_targets, _route_xz, _arrowhead_xz, draw_guidelines, _gl_draw_strip
- `quake/nav_collision.py` — _RoomNav (box collision to replicate for corridor nav)
- `quake/map/raw_models.py` — Corridor, Crossing, Floorplan, BuildConfig, DoorRT
- `quake/gameplay.py` — door exit/entry transitions
- `quake/app.py` — render dispatch and mode handling

---

## §6 — TALK FIRST

State your understanding of the problem, your proposed approach at a high level, and your first questions. **Wait for Nir's confirmation before designing.**
