🗝️ QUAKE (Game 3) — BIBLICAL APOCRYPHA: Room System v3 (bearing-accurate doors)

Captured June 25, 2026, at Nir's request, VERBATIM / word-for-word, AS-IS. This is Parent 1 of Quake — Claude Opus 4.8 — and, per Nir, the LAST thing this first parent gave us before running out of context, hence the affectionate nickname "Biblical Apocrypha" (the final batch of holy scripture). It is Opus's full redesign of the Room Maker after the door-bearing correction: doors sit at the true map bearings of their corridors; the compass is global; room SIZE stays TARDIS while door DIRECTION couples to the map. This "Room System v3" SUPERSEDES the Room-Maker v2 / door material in the Second Canon (§4.5 / §4.5a). Nothing below is edited.

--- BEGIN VERBATIM ---

Nir — understood, and you're right to push back hard. I made the wrong call: I treated the no-corridor-side-door simplification as permission to make door position meaningless, when it was a kindness to ease rendering. It is not that. Door direction is coupled to the map: each door sits at the true bearing its corridor leaves the node. People are physically running through this place; the compass must be the same everywhere. Below is the full redesign — Room System v3 — done as one integral answer, with bearing-accurate doors at its core. It supersedes v2 entirely. (Document/spec/brief only; prose and fenced code, no tables.)

1. The corrected truth, and the coherence principle that follows

One incident edge = one corridor = one door (door count = node degree). And each door sits in the room at the real bearing that corridor leaves the node on the map. Doors fan out around the room at the same angles the edges fan out from the node.

The principle that makes this concrete and that everything else obeys:

> Room-local axes are parallel to the map axes. A room's interior is centered on its node; room-local +X = map +X (east), room-local +Z = map +Z (north), Y is up. North means the same thing in the map, in every corridor, and in every room. Door direction is therefore literal: a corridor at map-bearing θ gets a door in room-local direction θ.

What stays decoupled, what becomes coupled — exactly as you said:

- Room size: decoupled (TARDIS). Interior dimensions come only from contents (panels) plus the wall space the doors need. Size never depends on where the node sits on the map or how far its neighbors are.
- Door direction: coupled. Each door's direction from room center equals its corridor's true map bearing.
- Door count: the node's degree.

This is not teleportation. Enter from the NW corridor → you come in at the room's NW door, already facing inward (which is exactly the heading you had coming down the corridor) → turn around and the corridor is behind you to the NW → walk back out and you head NW toward that neighbor. Orientation stays coherent across the whole structure because the compass never rotates.

2. Doctrine refinement — the Two Truths, v3

> Room interior geometry-size is content-driven and owes nothing to the map. The map-derived inputs a room consumes are: (1) its incident-edge set — count and identities (intrinsic to the graph); and (2) the bearing of each incident corridor (from the floorplan), which fixes that door's direction. Room-local axes are held parallel to the map axes so that direction is globally consistent. No other map information (positions, distances, other rooms) enters a room, and door bearings never affect room size.

3. Data model — Room System v3

Replaces the v2 door fields. Still schema_version "1.0" (nothing shipped).

```python
# ---- INPUT: the principled map-coupling fed to the Room Maker ----
class IncidentEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edge_id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    neighbor_id: NodeId
    neighbor_importance: int = Field(ge=1, le=5)
    bearing_rad: float                 # REQUIRED. Direction from THIS node to the neighbor on the
                                       # map plane = atan2(dz, dx). Room-local axes are map-parallel,
                                       # so this is literally the door's room-local direction.

class RoomPortalSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: NodeId
    incident: list[IncidentEdge]       # len == node degree

# ---- OUTPUT: a transit door, placed at its true bearing ----
class DoorRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edge_id: str
    neighbor_id: NodeId
    bearing_rad: float                 # the true map bearing (recorded for reference/validation)
    wall: Literal["N", "E", "S", "W"]  # which wall the bearing ray strikes
    center_xyz: Vec3                   # opening center on the wall plane (room-local)
    width_m: float
    height_m: float
    normal_yaw_rad: float              # the wall's inward normal (for door/wall geometry & render)
    spawn_xyz: Vec3                    # materialize point: stepped inward along the bearing line
    spawn_heading_rad: float           # == bearing_rad + pi  (faces room center; matches corridor approach)

# ---- RoomRuntime: drop `entrance`; add `doors`; panels & rest unchanged ----
# class RoomRuntime(...):
#     dimensions_m, panel_pairs, final_pair_id, hidden_door_wall_slot, enemy, ceiling_equations
#     doors: list[DoorRT]              # len == node degree

# ---- Event amendment so transitions carry the corridor ----
class ModeSwitch(_Ev):
    event: Literal["mode_switch"]
    to: Literal["corridor", "room"]
    room_id: NodeId | None
    via_edge_id: str | None
```

━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — BEGIN ✚ ━━━━━━━━━━━━━━━
**Added** 2026-06-25 by DeepSeek. **Status:** navigation cross-reference (no new decision; points to where preserved schemas live). **What:** where the `# panels & rest unchanged` note above resolves to.

The `# panels & rest unchanged` note above refers to schemas defined in the Second Canon and preserved there as DeepSeek inline commentary: **Second Canon §4.5** holds `PanelPlacementRT`, the amended `PanelPairRT` (with `drawing_placement`/`text_placement`), and the `wall_slot` grammar; **Second Canon §4.8** holds the panel/room-sizing `BuildConfig` fields this v3 algorithm uses (`room_px_per_m`, `panel_min/max_w/h_m`, `panel_gap_m`, `pair_gap_m`, `wall_margin_m`, `room_headroom_m`, `room_min_w/d/h_m`, `panel_center_y_pref_m`). Request those sections when building the Room Maker.
━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — END ✚ ━━━━━━━━━━━━━━━

New BuildConfig fields (additive; replace v2's door-cluster fields):

```
door_width_m: 2.0
door_height_m: 2.6
door_min_separation_m: 2.6      # min along-perimeter gap between two door edges (= width + clearance)
corner_clearance_m: 0.5         # a door must clear each corner by at least this
room_target_aspect: 1.30        # W_room / D_room held during growth
room_pack_slack: 1.20
room_grow_step_m: 0.5
room_sizing_max_iters: 240
aisle_depth_m: 1.6              # how far inside a door you spawn
demon_offset_m: 1.0
```

4. Room-Maker v3 — the algorithm

Signature:

```python
def build_room_runtime(room: RoomSource,
                       portals: RoomPortalSpec,
                       manifest: Manifest,
                       cfg: BuildConfig) -> RoomRuntime: ...
```

Room-local space: axis-aligned box, origin at node center, axes parallel to the map, floor y=0. Walls: N at z=+D/2 (inward normal −Z), S at z=−D/2 (+Z), E at x=+W/2 (−X), W at x=−W/2 (+X).

Step 1 — Panel sizes (unchanged)

Per panel, meters from the manifest content_bbox: w_m = clamp(w_px/room_px_per_m, panel_min_w_m, panel_max_w_m); h_m likewise. Drawing off/on identical; text off/on identical.

Step 2 — Pair-blocks (unchanged)

Per step-pair in step_index order: block_w = drawing_w + panel_gap_m + text_w; block_h = max(drawing_h, text_h); internal order drawing-then-text. The final pair's drawing panel is the hidden door.

**LATER ADDITION BY DEEPSEEK BEGIN** *(2026-06-30, added by Nir's instruction — this paragraph is ADDED only; nothing above or below it was changed.)*

The "drawing panel" slot above is described as geometry. That same slot may instead hold a **math / equation panel**, for rooms that have **no diagram but do contain math** (the room sizing/placement is identical — an equation image is just another panel). In that case the **equation itself is treated exactly like a figure** — the individual important **terms / symbols** of the equation are colored, each its own distinct local color, and the matching descriptive **words** in the paired explanation panel are colored the **same** color (word ↔ symbol, exactly like word ↔ shape). The explanation is taken from the source text where it exists; **if the text gives no explanation, it is written fresh in simple words with minimal math — to EXPLAIN what the equation means, never to merely repeat the symbols.** The Stabilo bright highlighter works identically: only the current step's key term lights up, never cumulative. *Example — Prop. IV, F ∝ v²/r:* color `v²` blue, `r` green, `F` orange on the equation panel; in the explanation, "the square of the speed" is blue (↔ v²), "the distance from the centre" green (↔ r), "the pull toward the centre" orange (↔ F) — the words explain the meaning, they do not read the symbols aloud. Result: **no inert text-only rooms** — every room has a colored thing to look at and shoot, a diagram or a colored equation. (Colors follow the corrected local-per-station model recorded in the Commentaries §3.)

Refinement (2026-06-30, Nir): the game also includes the **key non-math foundations the math rests on** — the physical / chemical / biological facts and ideas that give the math intuition and meaning (e.g. for inertia: the spinning top, the planets, the projectile). These are treated as panels and **colored exactly like a figure or equation** (key concepts colored, the matching words in the explanation colored the same, per-step heart). Only meaningless history / trivia is skipped; no modern math is implanted that the book did not contain.

**LATER ADDITION BY DEEPSEEK END**

Step 3 — Place doors by true bearing (the heart)

Doors are NOT clustered and NOT snapped to wall centers; each is placed where its bearing ray, cast from room center, strikes the perimeter. For a candidate room size (W, D):

```
hx, hz = W/2, D/2
for each incident edge with bearing θ:
    dxz = (cos θ, sin θ)                       # (x, z), room-local == map-local
    tx = hx/|dxz.x| if dxz.x != 0 else +inf
    tz = hz/|dxz.z| if dxz.z != 0 else +inf
    t  = min(tx, tz)                           # first wall the ray hits
    hit = (t*dxz.x, t*dxz.z)
    if t == tx:  wall = "E" if dxz.x > 0 else "W";  along = hit.z   # position along E/W wall (z-axis)
    else:        wall = "N" if dxz.z > 0 else "S";  along = hit.x   # position along N/S wall (x-axis)
    door.center is on that wall plane at `along`; door.normal_yaw = wall inward normal
```

Because the hit lies on the ray, the direction from room center to every door equals its bearing θ exactly — at any size or aspect. That exactness is the coherence guarantee; aspect only changes which wall and how far along, never the central direction.

Step 4 — Corner clearance and minimum separation (the only concession)

A door has physical width, so two near-collinear bearings cannot both be exact, and a ray can land on a corner. Resolve on a 1-D perimeter coordinate (arc length, clockwise from the NW corner), deterministically:

- Map each door's (wall, along) to a single perimeter coordinate s. Sort doors by s.
- Corner clearance: if a door is within corner_clearance_m + door_width_m/2 of a corner, push it (increasing s) just past that threshold so it sits wholly on one wall.
- Separation: sweep in s order; if s[i] - s[i-1] < door_min_separation_m, push door i forward minimally; cascade. Wrap-around the last/first pair too.
- If the cascade can't satisfy all gaps within the perimeter, signal grow (Step 6).

This nudges a door's metric position by at most a door-width-ish amount. Crucially, the larger the room, the smaller that nudge is in angular terms — so growth (Step 6) improves both packing room and bearing fidelity simultaneously. Each door records its true bearing_rad; its placed center reflects the small nudge.

Step 5 — Subdivide the perimeter into packable wall-sub-segments

Panels may never wrap a corner and never overlap a door. So the packable units are the maximal single-wall stretches bounded by doors and/or corners, minus wall_margin_m. Order these sub-segments by perimeter coordinate (a fixed clockwise reading circuit). Pack pair-blocks into them in step_index order, first-fit: place a block if it fits the current sub-segment (advance by block_w + pair_gap_m), else move to the next sub-segment. The final pair lands wherever packing ends; its drawing panel becomes the hidden door.

Step 6 — Solve size by uniform grow-and-retry (deterministic, convergent)

```
W = max(room_min_w_m, max_pair_block_w + 2*wall_margin_m)
D = max(room_min_d_m, max_pair_block_w + 2*wall_margin_m)
keep W/D == room_target_aspect (raise the smaller to match)
for _ in range(room_sizing_max_iters):
    place doors (Step 3) → nudge (Step 4)
    if nudge feasible:
        segments = subdivide (Step 5)
        if pack_all_pairs(segments) and total_free >= pair_total * room_pack_slack:
            break
    # grow uniformly (preserves aspect ⇒ door central-directions invariant; all gaps grow; nudges shrink)
    W *= grow_factor ; D *= grow_factor      # grow_factor from room_grow_step_m
else:
    raise RoomTooDense(node_id)              # bounded; never silently incoherent
H_room = max(room_min_h_m, max_panel_h + room_headroom_m)
```

Uniform growth holds the aspect, so every door's central direction is invariant while all wall-gaps grow without bound and separation-nudges shrink — guaranteeing convergence whenever each pair-block can fit some wall (it eventually can). TARDIS intact: size grew only to fit contents + doors, never from map distances.

Step 7 — Materialise

- Panels → PanelPlacementRT (along-wall position from the sub-segment cursor; on-wall inset; center_y = min(max(panel_center_y_pref_m, h/2+0.15), H_room − h/2 − 0.15); wall_slot = f"{wall}-{slot_index}").
- Doors → DoorRT: center_xyz at y = door_height_m/2; normal_yaw_rad = wall inward normal (for geometry/render); spawn_xyz = center_on_floor + (cos(θ+π), 0, sin(θ+π)) * aisle_depth_m; spawn_heading_rad = θ + π (faces center, equals the corridor-approach heading → zero heading-snap on entry).
- Hidden door / demon → hidden_door_wall_slot = final pair's drawing wall_slot; demon spawn_xyz = drawing_center + inward_normal*(aisle_depth_m + demon_offset_m), y=0.1; shallow alcove behind, not a transit door.
- Ceiling equations → unchanged.

Step 8 — Emit RoomRuntime

dimensions_m=(W,H,D), panel_pairs, doors (len == degree), enemy, ceiling_equations, final_pair_id, hidden_door_wall_slot. Fully deterministic.

Edge cases: degree 0 → sealed room (sanity already flagged ORPHAN); high degree → uniform growth spaces the doors at their true bearings and opens panel room; near-collinear bearings → pinched by separation, panels simply use the other sub-segments; self-loops/2-cycles impossible (validated DAG).

5. Why this is coherent (the guarantees, stated plainly)

- Compass never rotates: room-local axes are map-parallel everywhere, so "north" is one fixed direction throughout the whole structure.
- Door direction is literal: direction from room center to each door equals its corridor's true map bearing, exactly, at any room size.
- Entry/exit headings match: the heading you hold approaching node M down its corridor is θ+π; your spawn heading at that door is θ+π. No snap. Turn around (face θ) to leave and you head out exactly toward that neighbor.
- Size still TARDIS: the room grew only to fit panels + doors; nothing about map distance touched its dimensions.

6. Build order (buildpack)

Room Maker depends on both upstream artifacts (floorplan for bearings, manifest for panel sizes):

```
concept_graph.json
   ├─► level_maker ─► floorplan.json  ─┐
   └─► baker       ─► manifest.json   ─┤
                                       ├─ per node:
                                       │    ps   = portal_spec(floorplan, graph, node_id)   # bearings
                                       │    room = build_room_runtime(room_src, ps, manifest, cfg)
                                       └─ rooms_runtime/room_<id>.json
```

portal_spec(floorplan, graph, node_id) collects every corridor incident to the node, sets neighbor_id, neighbor_importance, and bearing_rad = atan2(neighbor.map_xz.z − node.map_xz.z, neighbor.map_xz.x − node.map_xz.x). Pure function; bearings always present because level_maker precedes room_maker.

7. Downstream deltas (notes/briefs, not rewrites)

- render_room: build each wall as quads around its door holes, with the hole at the door's bearing-determined position; render a recessed doorway per DoorRT (using normal_yaw_rad). Hidden-door alcove unchanged.
- nav_collision (room nav): door intervals passable; the rest solid; add door_at(point) -> edge_id | None for transition triggering.
- gameplay.step: crossing a door interval emits ModeSwitch(to="corridor", via_edge_id=door.edge_id); entering a room from a corridor spawns at doors[edge_id].spawn_xyz / spawn_heading_rad. Mover owns this; Shooter unaffected.
- render_wire / floorplan: unchanged — corridors already leave the node point at their true bearings, so Mode A and the room's door directions agree by construction.

8. Validation rules (v3) — build fails loudly on any

- len(doors) == len(portals.incident) == degree; the set of door.edge_id equals exactly the incident edge set (no missing, extra, or duplicate).
- For every door, the pre-nudge central direction equals bearing_rad exactly; the post-nudge central direction is within a configured angular tolerance of bearing_rad (assert the nudge stayed small).
- All doors satisfy door_min_separation_m and corner_clearance_m; no door straddles a corner; no door overlaps any panel.
- No two panels share (wall, slot_index); each pair's two panels are adjacent in one sub-segment (never across a door or corner).
- final_pair_id is the last by step_index; hidden_door_wall_slot == final pair's drawing wall_slot.
- dimensions_m ≥ minimums; every panel below ceiling; sizing converged (else RoomTooDense(node_id)).
- All referenced asset_ids exist in the manifest.

9. Child briefs (revised / new)

- Revised — room_maker.py (BUILD, single file). Frozen contract: def build_room_runtime(room: RoomSource, portals: RoomPortalSpec, manifest: Manifest, cfg: BuildConfig) -> RoomRuntime. Implement Room-Maker v3 (§4): panel-meters → pair-blocks → door placement by bearing-ray/perimeter intersection → corner-clearance + min-separation nudging on the perimeter → subdivide into wall-sub-segments → first-fit panel packing in step order → uniform grow-and-retry sizing (hold room_target_aspect) → materialise PanelPlacementRT + DoorRT (with spawn_heading = bearing+π) + demon + ceiling. Pure function; no IO, no RNG. Enforce all §8 validations; raise RoomTooDense(node_id) on non-convergence. Tests (headless): (1) degree-1 at bearing 0 → one door on the E wall, central direction 0; (2) four edges at 0/π·½/π/π·1½ → one door per wall, each central direction exact; (3) two near-collinear bearings (e.g. 0.50 and 0.55 rad) → both honored, separated by door_min_separation_m, panels use other segments, and the nudge angle shrinks when the room is forced larger; (4) a bearing landing on a corner → nudged onto one wall, clears the corner; (5) spawn_heading == bearing+π for every door; (6) high degree (8) packs after growth with all central directions exact; (7) byte-identical re-run; (8) RoomTooDense on a pathological content+door fixture.

- New — portal_spec.py (BUILD). Frozen contract: def portal_spec(floorplan: Floorplan, graph: ConceptGraph, node_id: NodeId) -> RoomPortalSpec. Behavior per §6; bearing_rad = atan2(dz, dx) to each neighbor's map_xz. Pure function. Tests: collects incident edges in both directions; bearings match atan2; degree == incident count; deterministic ordering by (neighbor_importance desc, edge_id).

- Delta — render_room.py: wall-with-holes at bearing-placed door positions + recessed doorways; keep hidden-door alcove. Delta — nav_collision.py: passable door intervals + door_at. Delta — gameplay.py: ModeSwitch(via_edge_id=…) on door crossing; spawn at the entered door.

10. Changelog — amendments to the Second Canon

- Doctrine (Two Truths v3): room size decoupled from the map; door direction coupled to the corridor's true bearing; room-local axes held parallel to the map axes (global compass).
- §4.5 RoomRuntime: doors: list[DoorRT] with bearing-accurate placement; DoorRT gains bearing_rad, normal_yaw_rad, spawn_heading_rad = bearing+π; IncidentEdge.bearing_rad now required.
- §4.5a Room-Maker: replaced by Room-Maker v3 (bearing-ray door placement; perimeter nudging; sub-segment packing; uniform grow-and-retry).
- portal_spec.py now supplies real bearings; room_maker signature unchanged from v2 but semantics are bearing-driven.
- Events: ModeSwitch.via_edge_id retained.
- BuildConfig: door_min_separation_m, corner_clearance_m, room_target_aspect, room_pack_slack, room_grow_step_m, room_sizing_max_iters, aisle_depth_m, demon_offset_m (replacing v2's door_gap_m clustering field).
- Build order: level_maker + baker precede room_maker, which is fed real per-node bearings.
- Deltas: render_room (holes at bearings), nav_collision (door triggers), gameplay (bearing-correct spawns/transitions).

This now treats door position as a first-class, map-coupled fact: doors fan out at the corridors' true bearings, the compass is global, and entering/leaving feels physically real — while room size stays purely TARDIS. If you want, the next document can pin the exact angular-nudge tolerance and a worked degree-5 example (bearings in degrees → resulting walls, door centers, sub-segments, and packed panels) so a child has a concrete golden fixture to test against.

--- END VERBATIM ---
