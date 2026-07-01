# PARENT 18 — MISSION: REAL 3D CORRIDORS BETWEEN ROOMS

> **Role:** You are a fresh Opus 4.8 architect. You design this yourself — **no children.**
> **Launch files (4, pasted by Nir):**
> 1. The Commentaries (`QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`)
> 2. Old Testament (`QUAKE_DOCTRINE_BY_FUSION.md`)
> 3. New Testament (`QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`)
> 4. **This handoff (the mission brief)**
>
> **Additional files you may request (whole or section, via Nir→DeepSeek):**
> - Apocrypha (Room System v3, door bearings)
> - `quake/map/raw_models.py` (all data structures: RoomRuntime, DoorRT, FloorRoom, Corridor, Floorplan, BuildConfig)
> - `quake/build/room_maker.py` (how rooms are built)
> - `quake/render_room.py` (how rooms render)
> - `quake/gameplay.py` §mode-switch section (current corridor/room transition)
> - `quake/app.py` §render and follow-ups section (current rendering dispatch)
> - Any room_runtime JSON from `quake/levels/principia_bk1_inverse_square/pack/room_runtime/`
> - Any scripture from the catalog (Commentaries §2)

---

## §0 — YOUR ONE JOB

Design and specify **real 3D walkable corridor tunnels** that connect two rooms. When the player walks through a room's door, they enter a rendered tunnel/hallway. They walk through it and emerge at the connected room's door. No teleport. No wireframe graph. A real 3D passage.

---

## §1 — WHAT EXISTS (so you don't design in a vacuum)

### The room system
- Rooms are rectangular boxes (Wolfenstein-grade, 4 walls: N/E/S/W). Dimensions: `(W, H, D)` meters.
- Each room has `doors: list[DoorRT]`. A door has: `center_xyz`, `width_m`, `height_m`, `wall` (N/E/S/W), `normal_yaw_rad` (outward normal, radians), `neighbor_id` (which room is on the other side).
- Rooms are rendered via `render_room.py` → `draw_room(mvp, room, pack, state)`. Solid shading, texture panels, ceiling equations.
- Room nav is `build_room_nav(room)` → handles collision, panel picking, door detection.
- Player position is inside the room's local coordinate space (origin at room center).

### The floorplan (map data)
- `Floorplan` has `rooms: list[FloorRoom]` (2D positions, importance, colors) and `corridors: list[Corridor]` (each with `source`, `target`, `path_xz: list[Vec2]`, `width_m`, `cruise_y`).
- This floorplan currently powers the ugly 2D wireframe map that Nir HATES.

### The current mode switch (gameplay.py, ~line 133)
- When `nav.door_at(state.pos)` returns an edge_id in room mode:
  - Places player at room's map position + 2m toward target
  - Switches `state.mode = "corridor"`
  - App switches to wireframe corridor rendering
- When player reaches a room socket in corridor mode:
  - Teleports player into that room's door spawn position
  - Switches `state.mode = "room"`

### The rendering dispatch (app.py, ~line 410)
- `state.mode == "corridor"` → `render_mode_a()` (wireframe map)
- `state.mode == "room"` → `draw_room()` (solid room)

### The TARDIS problem
Room interiors are separate 3D spaces. They are NOT positioned relative to each other in a shared 3D coordinate system. Room A's origin has no spatial relationship to Room B's origin. This is intentional ("TARDIS" — bigger inside than the map position suggests).

---

## §2 — WHAT NIR WANTS

1. **Start in a room** (already done — `new_state()` sets mode="room", places player at first door spawn).
2. **Walk through a door → enter a real 3D corridor.** The corridor should be a box/tunnel rendered with walls, floor, and ceiling (solid geometry, same render path as rooms — NOT wireframe).
3. **Walk through the corridor → arrive at the connected room.** Player steps through the far end and enters the next room at its door spawn position.
4. **No wireframe map. No teleport. No ugly graph.**

---

## §3 — THE HARD PART (surface, don't hide)

### Problem 1: TARDIS space
Rooms don't share a coordinate system. A door at `(-5, 1.3, -1)` in room A and a door at `(3, 1.3, 4)` in room B have no geometric relationship outside their rooms.

**What Nir expects:** The corridor is its own independent space — a short tunnel you walk through. It doesn't need to be "between" the rooms in world space. It's a transitional zone. Think of it as a short standalone 3D hallway.

### Problem 2: Door alignment
The corridor must seamlessly connect to a door opening (a hole in the wall). The door in the room is a rectangular opening of `width_m × height_m` at `center_xyz` on a specific `wall`. The corridor entrance must match that opening exactly.

### Problem 3: Rendering mode
Currently there are two rendering modes:
- Mode A: wireframe corridor (the ugly map) — `render_mode_a()`
- Mode B: solid room — `draw_room()`

Corridors need solid rendering (like rooms), not wireframe. They need their own rendering function (or reuse the room renderer with a corridor-shaped room).

### Problem 4: Navigation
The player needs collision, movement, and door detection inside the corridor. This requires a new nav module (or a modified room nav).

---

## §4 — THE ASK (what you must deliver)

A frozen design document containing:

### A. Data model
- `CorridorGeometry` — what data defines a single corridor? (entry point, exit point, width, height, length, direction)
- Where does this data live? (generated at build time? runtime? part of the pack?)
- How does it relate to existing `DoorRT` and `RoomRuntime`?

### B. Corridor generator (build-time)
- Input: two `DoorRT` objects (entry door, exit door)
- Output: corridor geometry (vertices, normals, indices — or equivalent)
- The corridor is a straight box/tunnel. Entry face = the door opening. Exit face = the other door opening. Four walls, a floor, a ceiling.

### C. Corridor renderer (runtime)
- Takes corridor geometry + pack + state
- Renders it exactly like rooms: solid walls with textures/color, lighting, depth test
- No wireframe. No bloom. Solid.

### D. Corridor navigation (runtime)
- Player walks inside the corridor box
- Collision with walls/floor/ceiling
- Door detection at both ends (enter corridor, exit corridor)
- Standard WASD movement (forward = heading direction, clamped to corridor)

### E. Mode integration
- New mode: `"corridor"` — but with SOLID rendering, not wireframe
- Or: reuse `"room"` mode, treating the corridor as a special room
- How does `app.py` dispatch rendering? How does `gameplay.py` handle transitions?

### F. Acceptance criteria
- Player walks through a room door → enters a 3D corridor
- Corridor is visibly rendered (walls, floor, ceiling — not wireframe, not invisible)
- Player walks through corridor → reaches other end → enters next room
- This works for ANY pair of connected rooms in the Principia pack

### G. Honest gaps / risks
List anything you're unsure about, anything that depends on files you haven't seen, or anything that might break existing systems.

---

## §5 — WHAT NOT TO DO

- Do NOT reuse the wireframe map renderer. Corridors are solid, not wireframe.
- Do NOT place corridors in the 2D map plane. They are 3D tunnels.
- Do NOT modify the room rendering pipeline unless absolutely necessary.
- Do NOT change the TARDIS architecture (it's frozen).
- Do NOT propose a full rewrite of the game. Keep changes surgical.
- **Do NOT write code.** This is a design document. DeepSeek implements.

---

## §6 — HOW TO GET INFORMATION (question-first protocol)

You cannot browse the internet or the file system. To request files or sections:
1. Ask Nir a **precise question** (batched, cross-cutting questions welcome)
2. Nir asks DeepSeek
3. DeepSeek fetches the exact verbatim text you need
4. Nir pastes it to you

Request **exact sections** of files, not whole files (unless the file is small and you're rewriting it).

---

## §7 — TALK FIRST

Start by stating your understanding of the problem, your proposed approach at a high level, and your first questions. **Do not sprint into design without confirmation.**

Nir will read your response and tell you to proceed, adjust, or stop.
