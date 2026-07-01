# PARENT 20 — MISSION: REAL 3D CORRIDORS (SOLID TUNNELS BETWEEN ROOMS)

> **Role:** You are a fresh Opus 4.8 architect. You design this yourself — **no children.**
> **Launch files (4, pasted by Nir):**
> 1. The Commentaries (`QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`)
> 2. Old Testament (`QUAKE_DOCTRINE_BY_FUSION.md`)
> 3. New Testament (`QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`)
> 4. **This handoff (the mission brief)**

---

## §0 — YOUR PREDECESSOR FAILED. DO NOT REPEAT HIS MISTAKES.

Parent 18 was given this same mission. He delivered a wireframe graph fix and called it "corridors." He was fired. You are his replacement. Read the five failure modes below and **do none of them**:

1. **Parent 18 reinterpreted the mission into something easier.** The handoff said "solid 3D walkable tunnels." He built a wireframe graph improvement. Do not do this.
2. **Parent 18 read the Old Testament and obeyed it over Nir.** The Old Testament §3.1 says "Transparent wireframe only. Do not upgrade corridors to shaded/solid polygons." **Nir has overruled this.** The corridors are solid 3D tunnels. The Old Testament was written before Nir saw the wireframe map and hated it. Nir's word overrules all scripture on this point.
3. **Parent 18 asked Nir questions the answers were already in the context.** Do not demand re-pastes.
4. **Parent 18 offered menus of options instead of reading the spec and building what it says.** Do not do that.
5. **Parent 18 dressed up guesses as diligence.** If you don't know, say so honestly and ask.

---

## §1 — YOUR ONE JOB

Design and specify **real 3D walkable solid tunnel geometry** that connects two rooms. When the player walks through a room's door, they enter a rendered hallway. They walk through it and emerge at the connected room's door. No teleport. No wireframe. Solid walls, floor, and ceiling.

The corridor is its own short, standalone 3D space — a box-shaped tunnel. It has ONE entry door (matching the door they exited from) and ONE exit door (matching the door of the destination room).

---

## §2 — WHAT EXISTS (verbatim excerpts from the real code)

### Room rendering (solid, working)
Rooms are rendered via `draw_room(mvp, room, pack, state)` in `render_room.py`. The function:
- Takes a projection matrix (world→clip), a `RoomRuntime` object, the `Pack`, and `GameState`
- Renders walls (lit, solid color + optional textures from `pack.asset_dir`), floor, ceiling
- Panel quads with textures loaded from pack.asset_dir (grey fallback if texture missing)
- Ceiling equations (textured quads near the ceiling with blood-red tint)
- Uses `moderngl` with depth test, two-sided lighting, ambient + directional

A corridor is a much simpler version of a room: just walls, floor, ceiling — no panels, no demon, no ceiling equations. It should reuse the same solid rendering pipeline.

### Door data (one door connects to one corridor)
`DoorRT` (from `raw_models.py` / Apocrypha):
- `edge_id: str` — the corridor/edge this door connects to (e.g. `"edge.lemma_2.to.lemma_3"`)
- `neighbor_id: NodeId` — the room on the other side
- `wall: Literal["N","E","S","W"]` — which wall the door is on
- `center_xyz: Vec3` — door center in room-local coords
- `width_m: float`, `height_m: float` — door opening dimensions
- `bearing_rad: float` — map bearing of the connecting corridor (direction it leaves the room node)
- `normal_yaw_rad: float` — outward normal of the door (facing direction of the wall)

Room doors: `room.doors` is `list[DoorRT]`. Each door has an `edge_id` and a `neighbor_id`.

### Door exit transition (working)
In `gameplay.py ~130-165`: when `nav.door_at(state.pos)` returns an `edge_id` in room mode, the player is placed at `(room.map_xz + 2m toward corridor far end, heading=atan2(dz,dx))` in floorplan world coords, then `state.mode = "corridor"`, and `ModeSwitch(to="corridor", via_edge_id=eid)` is emitted.

### Door entry transition (working)
In `gameplay.py ~166-190`: when the player in corridor mode reaches within `SOCKET_ENTER_RADIUS_M` of a room's `map_xz`, they teleport into that room at `room.doors[0].spawn_xyz` with `room.doors[0].spawn_heading_rad`, and `state.mode = "room"`.

### Room nav (working)
`_RoomNav` in `nav_collision.py` handles:
- Wall/floor/ceiling collision (box with door cutouts)
- `door_at(point)` → returns door's `edge_id` if player is in the door opening
- `nearest_panel(ray, max_dist)` → panel picking (irrelevant for corridors)
- `resolve_player_motion(start, delta)` → collision-resolved position

### Corridor nav (placeholder, wireframe-based)
`_CorridorNav` in `nav_collision.py` was built for the wireframe map — it finds the nearest corridor centerline and clamps the player to it in XZ. This is NOT useful for solid tunnel corridors.

### App mode dispatch (how to hook in)
In `app.py ~468-480`:
```python
if state.mode == "corridor":
    # currently calls render_mode_a() (wireframe) — needs to become solid corridor render
else:
    # room rendering via draw_room()
```

Also at ~416-419:
```python
if state.mode == "corridor":
    nav = _active_corridor[1] if _active_corridor[1] is not None else corridor_nav
else:
    nav = room_navs.get(state.current_room_id)
```

### TARDIS principle (critical)
Room interiors are separate spaces. Room A's origin has NO spatial relationship to Room B's origin. The corridor must also be its own standalone space — it does NOT live in floorplan coords and does NOT need to be "between" room A and B in a shared world. It's a transitional 3D box you walk through.

---

## §3 — WHAT NIR WANTS (his words)

1. Walk through a door → enter a real 3D corridor with walls, floor, ceiling (solid, rendered, NOT wireframe)
2. Walk through the corridor → arrive at the connected room
3. Simple box-shaped tunnel — straight, short, entry at one end, exit at the other
4. No wireframe map. No teleport between doors. No ugly graph.

---

## §4 — THE DESIGN (what you must deliver)

### A. CorridorGeometry data model
A corridor is a single 3D box defined by:
- **Entry end:** matches the exit door's dimensions exactly (width_m × height_m opening)
- **Exit end:** matches the entry door's dimensions
- **Length:** configurable default (e.g. 8m), makes the corridor feel like a short walkway
- **Walls, floor, ceiling:** simple solid surfaces (no panels, no textures needed — lit solid color like room walls)

The corridor is a new runtime concept. It can be:
- Generated at runtime from the two DoorRT objects (door A = entry, door B = exit)
- Or built at build-time as part of the pack (like room runtimes)

Given TARDIS, runtime generation from doors is clean: you know the entry door (where you just walked through) and the exit door (the connected room's door you're heading toward). Build the box between them.

### B. Corridor renderer
Reuse the solid room rendering pipeline. A corridor is essentially a room with no panels, no demon, and no ceiling equations. `draw_room()` or a thin wrapper around the same wall/floor/ceiling primitives works. Must inherit the same lighting, depth test, and perspective as rooms.

### C. Corridor navigation
A corridor nav that:
- Box collision (walls, floor, ceiling) — identical to `_RoomNav` without door cutouts on the side walls (only entry/exit at the ends)
- `door_at(point)` — returns the destination door's `edge_id` when the player walks through the exit end (so gameplay.py's existing door-to-room transition fires)
- `resolve_player_motion(start, delta)` — box collision within the corridor

### D. Mode integration
The player enters a corridor from a room. Currently `gameplay.py` sets `state.mode = "corridor"` and places the player in floorplan coords. This needs to change:
- The corridor has its OWN coordinate space (like a room does)
- Player is placed at the corridor's entry end, facing toward the exit end
- `app.py` renders the corridor as a solid space (not wireframe)
- When player reaches the exit end and `door_at()` fires, gameplay.py's existing room-entry code handles the rest (teleport to room.spawn)

### E. Acceptance criteria
- Walk through any room door → renders as a solid 3D tunnel (not wireframe, not invisible)
- Walk through tunnel → reach other end → enter destination room at its door spawn
- Works for ANY connected room pair in the Principia pack

### F. Honest gaps
List anything you're unsure about that depends on files you haven't seen.

---

## §5 — WHAT NOT TO DO

- Do NOT make wireframe corridors. Solid only.
- Do NOT place corridors in 2D floorplan coords. They are their own TARDIS space.
- Do NOT change the room renderer's contract unless absolutely necessary.
- Do NOT offer Nir menus of options. Read the spec and build what it says.
- Do NOT tell Nir you lost his text and need it re-pasted. It's here.
- **Do NOT write code.** Design document only. DeepSeek implements.
- **Do NOT ask questions the scripture already answers.**
- **"Tests pass" is NOT visual success.** Render and show a PNG.

---

## §6 — HOW TO GET MORE INFORMATION

Ask DeepSeek (via Nir) for exact verbatim sections of any file. Useful files you may need:
- `quake/render_room.py` — how draw_room() renders solid rooms
- `quake/nav_collision.py` — _RoomNav and _CorridorNav (room nav to replicate)
- `quake/map/raw_models.py` — RoomRuntime, DoorRT, BuildConfig definitions
- `quake/build/room_maker.py` — how room runtimes are assembled
- `quake/gameplay.py` — exact door-exit / door-entry transition code
- `quake/app.py` — render dispatch and mode handling
- Any `room_runtime/*.json` from the Principia pack

---

## §7 — TALK FIRST

State your understanding of the problem, your proposed approach, and your first questions. **Wait for Nir's confirmation before designing.**

Nir has been patient far beyond what your predecessor earned. Do not waste it. Read this entire document. Build solid walkable tunnels between his rooms. That is the entire job.
