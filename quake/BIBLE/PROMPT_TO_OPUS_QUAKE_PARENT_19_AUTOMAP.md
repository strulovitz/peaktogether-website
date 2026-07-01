# PARENT 19 — MISSION: DESCENT-STYLE 3D WIREFRAME AUTOMAP

> **Role:** You are a fresh Opus 4.8 architect. You design this yourself — **no children.**
> **Launch files (4, pasted by Nir):**
> 1. The Commentaries (`QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`)
> 2. Old Testament (`QUAKE_DOCTRINE_BY_FUSION.md`)
> 3. New Testament (`QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`)
> 4. **This handoff (the mission brief)**

---

## §0 — WHAT CURRENTLY EXISTS (the problem)

The game currently has no real automap. There is a 2D top-down map (`render_wire.py`) that draws flat colored circles and lines on the XZ plane — what Nir calls "the ugly map." This is the exact opposite of what the Old Testament specifies.

The Old Testament §3.1 defines the wireframe world. It applies to BOTH the corridor mode and the automap. The corridor mode and the automap are the SAME visual language — 3D wireframe geometry — used in two contexts: walking inside a tunnel vs. flying above the graph.

---

## §1 — THE SPEC (verbatim from the Old Testament §3.1)

> *"Wireframe only. Lines and node rings; no shaded polygons. 'Transparent' here means empty faces with visible edges, not alpha translucency."*

> *"Depth-tested, NO alpha blending. Depth test on, depth write on, blend off, depthFunc = LEQUAL. Near geometry occludes far."*

> *"Distance-dimming in the line shader: the current section renders near pure white, fading with view-space distance toward dark grey — never pure black (so far structure stays a faint felt presence; vanishing into black is what disorients)."*

> *"Crossings visible as true 3D over/under passes."*

**TRANSLATION FOR THE AUTOMAP:**
- Every room is a 3D wireframe box (12 edges — 4 bottom, 4 top, 4 vertical)
- Every corridor is a 3D wireframe tube/box (edges connecting room door positions)
- Edges are lines ONLY — no filled faces, no shaded surfaces
- Edges are white up close, dimming to dark grey far away (NEVER black)
- Depth-tested: near edges of one box occlude far edges of a box behind it
- Crossings show as true 3D: a high-layer corridor passes visibly OVER a low-layer one
- No alpha blending — occlusion comes from depth test
- Room box edges are colored by the room's importance (its `map_color`)

**What the automap does NOT have that corridor mode has:**
- No floor plane (the player is flying, not walking)
- No floor guide-lines or arrowheads (no felt floor — you're in free-flight)
- No rail assist / collision (free movement)

---

## §2 — WHAT DESCENT'S AUTOMAP LOOKS LIKE (the reference)

Descent (Parallax Software, 1995) was the first fully-3D FPS. Its automap:
- Renders the ENTIRE mine as a 3D wireframe from the player's perspective
- Each room = 3D wireframe cube (edges only, no faces)
- Each tunnel = 3D wireframe box connecting rooms
- Lines colored by room type / function
- Rendered in free-flight mode (player can fly through the wireframe)
- Correct 3D perspective — rotate and see rooms from any angle

---

## §3 — WHAT NIR WANTS

A Descent-style 3D wireframe automap, toggled with a key (e.g. Tab), where:
1. Rooms are 3D wireframe boxes positioned at their floorplan locations
2. Corridors are 3D wireframe tubes/edges between room door positions
3. Everything rendered in true 3D perspective, free-fly camera
4. Room edges colored by importance (matching `map_color`)
5. Distance-dimming: near = bright, far = darker grey, never black
6. Depth-tested: near geometry occludes far
7. No floor guide-lines, no arrowheads, no felt floor
8. Pure wireframe edges — no filled surfaces, no alpha

---

## §4 — THE DESIGN YOU MUST DELIVER

### A. Geometry generation (pure, headless-testable)

**Function: `build_automap_mesh(fp: Floorplan, rooms: dict[NodeId, RoomRuntime]) -> AutomapMesh`**

For each room in the floorplan:
- Build a 3D wireframe box: 12 edge lines (4 bottom, 4 top, 4 vertical)
- Position: `(map_xz[0], socket_y, map_xz[1])` as floor-level center
- Dimensions from `RoomRuntime.dimensions_m` which is `(W, H, D)` — or use `map_radius_m` scaled up if RoomRuntime not available
- Edge color = room's `map_color` (hex → RGB)

For each corridor in the floorplan:
- Build a 3D wireframe connection between the source and target room boxes
- Uses `Corridor.path_xz`, `Corridor.width_m`, and `Corridor.cruise_y`
- Minimum: 4 edge lines forming a rectangular tube from source door to target door at the corridor's true `cruise_y` height
- Edge color = white (corridors are transit, importance color belongs to rooms)

**Output: `AutomapMesh`:**
- `edges: np.ndarray` — N×2×3 edge vertex pairs in world coordinates
- `edge_colors: np.ndarray` — N×3 RGB colors per edge

### B. Rendering (thin GL shell)

**Function: `render_automap(ctx, window, view, proj, mesh)`**

- Renders all edges using the EXISTING `wire_quad_program` (thick camera-facing line-quads) or the simpler `wire_program` (both from `shaders.py`)
- Depth test ON, no blend — exactly like the current `_draw_wire()`
- Distance-dimming: all edges dim from white→grey with view-space distance (reuse the existing shader's `u_dim_near`/`u_dim_far`/`u_grey_floor` uniforms)
- For colored room edges, multiply the dimmed white by the room's color
- Camera: free-fly — WASD movement + mouse look, detached from the player's body
- Bloom post-pass optional (reuse the existing bloom from `render_mode_a`)

### C. Integration

- Toggle with Tab key (or assignable key)
- When active: draw the automap to screen (replaces or overlays the current view)
- When inactive: normal game rendering
- Shares the existing moderngl context and FBO pipeline
- Does NOT modify room rendering, room navigation, or the TARDIS architecture

### D. Data questions to answer

- Where do room dimensions come from? `pack.rooms[room_id].dimensions_m` gives (W, H, D). This data IS available at runtime (it's in the loaded Pack).
- TARDIS: room interiors are bigger than their map footprint. For the automap, use the ACTUAL room dimensions (they represent real physical space) or a scaled-down version? Surface this question to Nir.
- Corridor tube endpoints: `DoorRT.center_xyz` gives the door's position inside the room. But rooms don't share a coordinate system. For the automap, corridor endpoints are the room's `map_xz` position (the corridor edge starts at the room box edge, not inside it). Surface how to handle this.

### E. Acceptance criteria
- Map renders as true 3D wireframe (boxes for rooms, tubes for corridors)
- Rooms have visible depth (not flat circles)
- View rotates in 3D (free-fly camera)
- Room edges colored by importance
- Distance-dimming: near bright, far grey, never black
- Depth-tested: near boxes occlude far boxes
- No floor guide-lines, no arrowheads
- Toggleable

### F. Honest gaps
List anything you're unsure about.

---

## §5 — WHAT NOT TO DO

- Do NOT make a 2D flat top-down map (circles and lines on XZ plane). This is 3D boxes.
- Do NOT fill boxes with solid shaded surfaces. Wireframe edges only.
- Do NOT use alpha blending. Depth test is the occlusion mechanism.
- Do NOT add floor guide-lines, arrowheads, or a felt floor. The automap has none of these.
- Do NOT make edges fade to pure black. Dark grey floor only.
- Do NOT reinterpret the mission into something easier. Read the spec, build what it says.
- Do NOT offer Nir menus of options when the spec already answers the question.
- Do NOT tell Nir you lost his text and demand re-pastes.
- Do NOT write code. Design document only. DeepSeek implements.
- **"Tests pass" is NOT visual success.** Render and show a PNG.

---

## §6 — HOW TO GET MORE INFORMATION

Ask DeepSeek (via Nir) for exact verbatim sections. Useful files:
- `quake/render_wire.py` — existing wireframe renderer (thick quads, dimming, bloom)
- `quake/shaders.py` — wire_quad_program, wire_program, uniforms
- `quake/map/raw_models.py` — Floorplan, FloorRoom, Corridor, Crossing
- `quake/render_room.py` — how solid room boxes are built (reference)
- `quake/app.py` — render dispatch
- `quake/levels/principia_bk1_inverse_square/pack/floorplan.json` — real data

---

## §7 — TALK FIRST

State your understanding of the automap, your proposed approach, and your first questions. **Wait for Nir's confirmation before designing.**
