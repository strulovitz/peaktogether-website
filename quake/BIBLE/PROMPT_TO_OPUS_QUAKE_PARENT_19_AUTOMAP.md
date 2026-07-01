# PARENT 19 — MISSION: DESCENT-STYLE 3D WIREFRAME AUTOMAP

> **Role:** You are a fresh Opus 4.8 architect. You design this yourself — **no children.**
> **Launch files (4, pasted by Nir):**
> 1. The Commentaries (`QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`)
> 2. Old Testament (`QUAKE_DOCTRINE_BY_FUSION.md`)
> 3. New Testament (`QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`)
> 4. **This handoff (the mission brief)**
>
> **Additional files you may request (whole or section, via Nir→DeepSeek):**
> - `quake/map/raw_models.py` — Floorplan, FloorRoom, Corridor data structures
> - `quake/render_wire.py` — CURRENT flat-plane wireframe renderer (what we're replacing)
> - `quake/render_room.py` — solid room renderer (for reference on how geometry is structured)
> - `quake/shaders.py` — wire program, solid program, blit program
> - `quake/app.py` §render section — how rendering is dispatched
> - `quake/nav_collision.py` — corridor nav (how floorplan is consumed)
> - `quake/levels/principia_bk1_inverse_square/pack/floorplan.json` — real floorplan data
> - Any room_runtime JSON to see what room dimensions look like
> - Any scripture from the catalog (Commentaries §2)

---

## §0 — YOUR ONE JOB

Design and specify a **3D wireframe automap** that looks like the automap in the 1995 game **Descent** — NOT like the current flat-plane colored-lines-and-circles map.

---

## §1 — WHAT DESCENT'S AUTOMAP LOOKS LIKE (reference)

Descent (Parallax Software, 1995) was the first fully-3D first-person shooter. Its automap is:

- A **3D wireframe** rendering of the entire mine, viewed from the player's position/perspective
- Each **room** appears as a **3D wireframe cube** (edges only, no faces)
- Each **corridor/tunnel** appears as a **3D wireframe box/tube** connecting rooms
- Lines are variably colored: white for normal areas, different colors for doors, energy stations, reactor areas
- Only areas the player has **visited or seen** are shown (fog-of-war)
- The automap is rendered in a small window OR as a fullscreen overlay
- It is **NOT** a 2D top-down map with circles and lines on a flat plane
- Everything is rendered in correct 3D perspective from the player's current viewpoint

You can see reference images by searching: "Descent automap" or "Descent 1995 automap wireframe"

---

## §2 — WHAT QUAKE CURRENTLY HAS (the problem)

The current "map" in `render_wire.py` is this:

```
Floor (XZ plane):
  ┌─ Colored circles (room rings) at room map_xz positions
  ├─ White lines between them (corridor paths)
  └─ Distance-dimming (white→grey) + bloom glow
```

It is rendered as camera-facing thick line-quads at each room's `map_xz` position on a flat Y-plane. This is:
- **2D flat** — everything sits on the XZ plane
- **No depth** — rooms are circles, not cubes
- **No 3D structure** — corridors are lines, not tubes
- **Ugly** — Nir hates it

---

## §3 — WHAT NIR WANTS

A **Descent-style 3D wireframe automap** where:

1. **Rooms are 3D wireframe boxes** (rectangular cuboids drawn with edge lines only — 12 edges per box). Room size comes from `RoomRuntime.dimensions_m` (W, H, D). Positioned at the room's map location with the correct 3D height.

2. **Corridors are 3D wireframe connections** (rectangular tubes or simple edge-lines between door positions). Not flat lines on the ground — actual 3D structures.

3. **Everything is rendered in true 3D perspective** from the player's camera position. Rotating the view shows rooms from different angles. Rooms have real depth.

4. **Rooms are colored by importance** — like the current system, but applied to 3D wireframe edges, not flat colored circles.

5. **The rendering replaces** the current `render_mode_a()` / `render_wire.py` approach. Or, it's a NEW function that coexists (the old one can die).

6. **This is purely visual** — navigation is NOT part of this mission. The map is a view-only overlay.

---

## §4 — THE ASK (what you must deliver)

A frozen design document containing:

### A. Geometry generation (pure, headless-testable)

**Function: `build_automap_mesh(fp: Floorplan, rooms: dict[NodeId, RoomRuntime]) -> AutomapMesh`**

For each room in the floorplan:
- Create a 3D wireframe box (12 edge lines) at the room's `map_xz` position, with dimensions from `RoomRuntime.dimensions_m`
- Position: `(map_xz[0], socket_y, map_xz[1])` as the floor-level center
- Color edges by the room's `importance` rank or `map_color`

For each corridor in the floorplan:
- Create a 3D wireframe connection between the source and target room door positions
- OR: simply connect the two room boxes with edge lines at the corridor's `cruise_y`
- Minimum: 4 corner-edge lines forming a rectangular tube between the two door centers

**Output: `AutomapMesh` containing:**
- `edges: np.ndarray` — N×2×3 array of edge vertex pairs (start, end) in world coordinates
- `edge_colors: np.ndarray` — N×3 array of RGB colors per edge
- (Optional) `room_labels: list[(Vec3, str)]` — room name labels at each room center

### B. Rendering (thin shell, requires GL context)

**Function: `render_automap(ctx, window, view_matrix, projection_matrix, mesh: AutomapMesh)`**

- Takes the AutomapMesh + camera matrices
- Renders all edges as camera-facing thick line-quads OR thin GL lines
- Handles depth testing (edges behind walls are occluded)
- Applies distance-based dimming (close = bright, far = dimmer, never pure black)
- Optional: bloom/glow overlay for bright areas
- Must work within the existing moderngl + pyglet pipeline

### C. Integration with app.py

- Replace or supplement the current corridor-mode rendering with `render_automap()`
- When `state.mode == "corridor"` → render the automap instead of the old wireframe
- The automap should be toggleable (e.g., Tab key to show/hide)
- Camera for the automap: share the player's view matrix, or use an independent overview camera

### D. Data questions to answer

- Where do room dimensions come from? (RoomRuntime.dimensions_m — but are these available when rendering the map? Currently `render_mode_a` gets `pack.floorplan` only, not `pack.rooms`)
- How to pass room dimension data alongside the floorplan?
- Corridor tube geometry: what data is available? (Corridor.path_xz, corridor.width_m, DoorRT.center_xyz)
- What about the TARDIS problem? Rooms are bigger on the map than their map_radius_m suggests. Should the wireframe boxes use actual room dimensions or scaled-down versions?

### E. Acceptance criteria

- The map renders as a true 3D wireframe (boxes, not circles)
- Rooms have visible depth/thickness (not flat 2D)
- The view rotates correctly with the player's camera
- At least 2 distinct colors appear (e.g., high-importance rooms different from low-importance)
- The old flat-plane wireframe is gone or disabled by default

### F. Honest gaps / risks

List anything you're unsure about, anything that depends on files you haven't seen, or anything that might break existing systems.

---

## §5 — WHAT NOT TO DO

- Do NOT keep the flat-plane circles-and-lines approach. This must be true 3D wireframe.
- Do NOT write navigation code. This is visual-only.
- Do NOT modify the room system or TARDIS architecture.
- Do NOT propose a full rendering pipeline rewrite.
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

Start by stating your understanding of Descent's automap, your proposed approach at a high level, and your first questions. **Do not sprint into design without confirmation.**

Nir will read your response and tell you to proceed, adjust, or stop.
