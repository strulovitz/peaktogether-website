🗝️ QUAKE (Game 3) — PARENT 4 → PARENT 5 HANDOFF: THE GOLDEN FIXTURE PACK

Captured June 26, 2026, at Nir's request. This is Parent 4 of Quake — Claude Opus 4.8 — handing off to Parent 5. The runtime engine (M0–M7, 13 modules) that I designed and froze is now BUILT and GREEN (283/283 tests). Parent 5 has exactly one mission: design and hand-author the Golden Fixture Pack. This document is self-contained — Parent 5 can begin immediately without reading my 1594-line engine document.

--- BEGIN HANDOFF ---

You are Parent 5. You received this alongside the Commentaries, the Old Testament, and the New Testament. Your mission is narrow and concrete, and this document gives you every value you need to execute it. Read §0 for context, then §1–§7 are your working spec. There is exactly ONE thing you must confirm before writing JSON (§7) — and I have already done the math for it in §9 so you can confirm it fast and start.
§0 — WHAT THE ENGINE IS (so you know what your fixture must feed)

The runtime engine reads ONLY baked JSON + PNG. It never sees LaTeX, an LLM, Asymptote, or the book. It is 13 modules, all built and green:

INFRASTRUCTURE: contracts.py (re-exports map/raw_models + engine-only types),
                glguard.py (HAVE_GL probe), conftest.py (skip_if_no_gl).
M0:  gfx_context.py, shaders.py, app.py (M0 stub).
M1:  camera.py, input_actions.py, render_wire.py, guidelines.py, nav_collision.py.
M6:  assets.py, render_room.py, readmode.py.
M7:  state.py, gameplay.py.

The modules that will CONSUME your golden pack (so your data must satisfy them):

    assets.load_pack(dir) — loads floorplan.json, palette.json, manifest.json, and globs room_runtime/room_*.json into a Pack. Validates the ID spine, asset references, PNG-path existence, and palette reserved keys. If your data is wrong, THIS is what raises.
    render_wire.build_wire_mesh(floorplan) — turns corridors into line segments and rooms into node rings.
    render_room.build_room_mesh(room) — turns a RoomRuntime into walls-with-holes (one hole per door), panel quads (2 per pair), an alcove (final pair drawing), and ceiling quads.
    guidelines.select_targets(floorplan, current, cleared, cfg) — BFS over corridors.
    nav_collision.build_corridor_nav(fp) / build_room_nav(room) — collision + raycasting + door_at.
    gameplay.step(state, actions, pack, nav, dt) — the brain; must be drivable to LevelComplete.

Your pack is NOT produced by the build pipeline (Legs 1+2+3). It is a hand-authored FIXTURE — valid baked output, by hand — that exercises every engine system and plays end-to-end in CI's smoke launch.
§1 — YOUR MISSION (one mission, nothing else)

Design every JSON field value and specify every PNG so DeepSeek can create the following file tree under quake/tests/golden_pack/:

tests/golden_pack/
  floorplan.json
  palette.json
  manifest.json
  png/wall/<asset_id>.png        (tiny 8x8 PNGs, one per asset)
  png/master/<asset_id>.png      (tiny 8x8 PNGs, one per asset)
  room_runtime/room_r_a.json
  room_runtime/room_r_b.json
  room_runtime/room_r_c.json

The pack must: (a) pass assets.load_pack("tests/golden_pack/") with no error; (b) be renderable by render_wire + render_room; (c) support a full clear → LevelComplete playthrough via gameplay.step.

DeepSeek creates the PNG bytes with Pillow (Image.new("RGBA", (8,8), color)). You specify the exact asset_id list and the exact RGBA hex for each. You author ALL JSON content exactly — every field, every coordinate, every bearing, every hex.
§2 — THE GRAPH AND ITS CONSEQUENCES (read this carefully — it fixes door counts)

The pack is a 3-node triangle with all three edges present:

corridors:  edge.a.to.b   (r_a — r_b)
            edge.b.to.c   (r_b — r_c)
            edge.a.to.c   (r_a — r_c)

CRITICAL CONSEQUENCE — every room has degree 2, so EVERY ROOM HAS EXACTLY 2 DOORS. The Apocrypha's iron rule is len(doors) == node degree. The original sketch in some notes said "r_b/r_c have 1 door" — that is WRONG for this graph and assets/render_room would be inconsistent with it. Author it correctly:

r_a: degree 2 → 2 doors (to r_b via edge.a.to.b, to r_c via edge.a.to.c)
r_b: degree 2 → 2 doors (to r_a via edge.a.to.b, to r_c via edge.b.to.c)
r_c: degree 2 → 2 doors (to r_a via edge.a.to.c, to r_b via edge.b.to.c)

Every room also has exactly one enemy (god-mode, one demon per room — OT invariant) and at least one ceiling equation. r_a is the two-step room (2 panel pairs); r_b and r_c each have 1 panel pair.
§3 — floorplan.json (exact values)

The map plane is XZ. map_xz is (x, z). Y is up. Compute bearings as atan2(dz, dx).

Node positions (chosen to give clean bearings and one real crossing):

r_a: map_xz = [0, 0],   importance = 5
r_b: map_xz = [12, 8],  importance = 3
r_c: map_xz = [6, 20],  importance = 1

For each FloorRoom: map_radius_m = 2.0, socket_y = 0.0, and map_color = the importance color from palette (map_importance): r_a → #ff4444 (imp 5), r_b → #cccc44 (imp 3), r_c → #4444ff (imp 1).

Corridors. Each corridor's path_xz is a polyline from source node to target node (straight, multi-segment so the wire mesh has multiple segments). Compute intermediate points by linear interpolation:

edge.a.to.b: source=r_a, target=r_b, height_level=0, cruise_y=0.0, width_m=3.0
  path_xz = [[0,0], [4, 2.6667], [8, 5.3333], [12, 8]]

edge.b.to.c: source=r_b, target=r_c, height_level=1, cruise_y=4.5, width_m=3.0
  path_xz = [[12,8], [9, 14], [6, 20]]

edge.a.to.c: source=r_a, target=r_c, height_level=0, cruise_y=0.0, width_m=3.0
  path_xz = [[0,0], [3, 10], [6, 20]]

NOTE on height_level: I set edge.b.to.c to height_level=1 (cruise_y=4.5) and the other two to height_level=0 (cruise_y=0.0). This is what makes the crossing a genuine bridge/underpass. Confirm the exact Corridor field names against the Second Canon §4.4 schema (it had corridor_id, source, target, height_level, cruise_y, path_xz, width_m). The corridor_id equals the edge id (e.g. "edge.a.to.b") and must match the pattern ^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$.

The crossing. edge.b.to.c (cruise_y=4.5) passes OVER edge.a.to.c (cruise_y=0.0). Find where the two polylines intersect in XZ:

    edge.a.to.c segment from [0,0] to [3,10]: parametrize as (3t, 10t), t∈[0,1].
    edge.b.to.c segment from [12,8] to [9,14]: parametrize as (12-3s, 8+6s), s∈[0,1].

Solve 3t = 12-3s and 10t = 8+6s. From the first: t = 4 - s. Substitute: 10(4-s) = 8+6s → 40-10s = 8+6s → 32 = 16s → s = 2.0. That's out of [0,1], so these particular segments don't cross. Try edge.a.to.c first segment vs edge.b.to.c SECOND segment from [9,14] to [6,20]: (9-3s, 14+6s). Solve 3t=9-3s, 10t=14+6s. First: t=3-s. Sub: 10(3-s)=14+6s → 30-10s=14+6s → 16=16s → s=1.0, t=2.0 — also out of range. The polylines as drawn don't geometrically cross at a clean interior point.

DECISION (mine, to keep the fixture clean and valid): rather than force a fragile polyline intersection, place the crossing at the obvious visual overlap near xz ≈ [6, 10] and declare it explicitly. The engine's render_wire does NOT recompute crossings — it just honors the cruise_y values per corridor (the over/under separation comes from cruise_y 4.5 vs 0.0). The Crossing record is metadata the schema requires; its at_xz is the declared visual crossing point. So author:

crossing:
  crossing_id   = "x_bc_over_ac"          (string; confirm any pattern in §4.4)
  over_corridor = "edge.b.to.c"
  under_corridor= "edge.a.to.c"
  at_xz         = [6, 10]
  over_y        = 4.5
  under_y       = 0.0

Confirm the Crossing field names + any crossing_id pattern against Second Canon §4.4. The validation that matters (from §4.4): over_y > under_y (4.5 > 0.0 ✓), and the two corridors named must exist. To make the declared at_xz=[6,10] lie plausibly on both routes, I nudged edge.a.to.c's middle point to [3,10] and edge.b.to.c's middle point to [9,14] — both polylines pass near x=6,z=10–14. If §4.4 validation strictly requires at_xz to be the exact polyline intersection, adjust one middle knee so the segments truly cross at [6,10] (e.g. set edge.a.to.c knee to [6,10] and edge.b.to.c knee to [6,10], making both polylines pass exactly through [6,10]). That is the safest authoring: put a shared knee [6,10] in BOTH corridors' path_xz:

SAFEST crossing authoring (recommended):
  edge.a.to.c: path_xz = [[0,0], [6,10], [6,20]]      cruise_y=0.0
  edge.b.to.c: path_xz = [[12,8], [6,10], [6,20]]     cruise_y=4.5
  crossing at_xz = [6,10], over=edge.b.to.c (4.5), under=edge.a.to.c (0.0)

Both polylines now pass through [6,10] exactly; at that XZ the b→c corridor is at y=4.5 and the a→c corridor is at y=0.0 — a clean over/under. Use this recommended form.

Top-level floorplan.json fields: schema_version="1.0", level_id="golden" (must match NodeId/LevelId pattern ^[a-z][a-z0-9_]*$ — "golden" is fine), seed (any int, e.g. 1729001), rooms, corridors, crossings. Confirm the exact top-level field list against §4.4.
§4 — palette.json (exact values)

schema_version : "1.0"
pack_id        : "golden"
groups         : {}                     (empty — golden pack has no figure groups)
grey_ink       : "#404040"
grey_text      : "#606060"
bg_key         : "#ff00ff"
map_node_default: "#888888"
map_importance : {
   "1": "#4444ff",
   "2": "#44aa44",
   "3": "#cccc44",
   "4": "#ff8844",
   "5": "#ff4444"
}

assets.load_pack asserts the reserved keys exist: grey_ink, grey_text, bg_key, and map_importance with keys "1".."5". Confirm the exact Palette model shape (field names like groups vs a colors dict, and whether map_importance is a sub-model GroupColor or a plain dict[str,Hex]) against the Second Canon §4.7-area Palette definition and the contracts.py re-export list. If the model names the importance map differently, match it exactly — do not invent fields (extra="forbid" will reject extras).
§5 — manifest.json (exact assets)

Enumerate every asset the three rooms reference. Asset-id grammar in the built engine is figure_id-keyed, but for a HAND-AUTHORED fixture the asset_id is just a string key in manifest.assets that the room JSONs reference verbatim — there is no pattern constraint on AssetEntry.asset_id (it is a plain str). So use clear, stable ids:

Room r_a (2 pairs + ceiling):
  figure_off_a1  (kind figure_off)   figure_on_a1  (kind figure_on)
  text_off_a1    (kind text_off)     text_on_a1    (kind text_on)
  figure_off_a2  (kind figure_off)   figure_on_a2  (kind figure_on)
  text_off_a2    (kind text_off)     text_on_a2    (kind text_on)
  ceiling_a      (kind ceiling_neutral)

Room r_b (1 pair + ceiling):
  figure_off_b1  figure_on_b1  text_off_b1  text_on_b1
  ceiling_b      (kind ceiling_neutral)

Room r_c (1 pair + ceiling):
  figure_off_c1  figure_on_c1  text_off_c1  text_on_c1
  ceiling_c      (kind ceiling_neutral)

NOTE: I am giving r_b and r_c their own ceiling assets (ceiling_b, ceiling_c) because every room has a ceiling equation. (The Parent-4→5 prompt sketch only listed ceiling_a; that was for the original "r_a only is complex" idea. Since all three rooms clear and reveal a ceiling, give each room its own neutral ceiling asset.)

For EACH asset, the AssetEntry fields (confirm exact names against Second Canon §4.6) are:

asset_id      : the id string above
kind          : one of "figure_off","figure_on","text_off","text_on","ceiling_neutral"
wall_path     : "png/wall/<asset_id>.png"
master_path   : "png/master/<asset_id>.png"
px_w          : 8
px_h          : 8
content_bbox  : [0, 0, 8, 8]     (half-open, top-left origin, pixels — Second Canon §2.3)
dpi           : 72

Top-level manifest.json fields: schema_version="1.0", level_id="golden", assets = a dict keyed by asset_id. Confirm against §4.6.

assets.load_pack validation you must satisfy: every asset_id referenced by any room (the four per pair + each ceiling asset_id) MUST exist in manifest.assets; and BOTH wall_path and master_path files MUST exist on disk under the pack dir. So every asset_id above needs both PNGs created.
§5.1 — PNG specification (the exact list for DeepSeek)

Every PNG is 8×8 RGBA. Give DeepSeek this exact color table. "Off" looks grey/dark; "on" looks lit. Magenta is the bake key color but for solid fixtures we just use opaque colors (no keying needed for tiny squares).

For each asset_id, create BOTH png/wall/<asset_id>.png AND png/master/<asset_id>.png.
Use the SAME color for wall and master (the master is just the "high-res" tier; 8x8 is fine).

figure_off_a1, figure_off_a2, figure_off_b1, figure_off_c1   → RGBA #333333ff  (dark grey, OFF drawing)
figure_on_a1,  figure_on_a2,  figure_on_b1,  figure_on_c1    → RGBA #ccccccff  (light, ON drawing)
text_off_a1,   text_off_a2,   text_off_b1,   text_off_c1     → RGBA #444444ff  (dark grey, OFF text)
text_on_a1,    text_on_a2,    text_on_b1,    text_on_c1      → RGBA #ffffffff  (white, ON text)
ceiling_a, ceiling_b, ceiling_c                              → RGBA #ffffffff  (neutral white; runtime tints it blood-red)

That is 18 asset_ids × 2 files = 36 PNG files, all 8×8 RGBA solid colors.
§6 — The room files (room_runtime/room_r_*.json)

Confirm the EXACT RoomRuntime v3 shape against the Apocrypha §3 (the authoritative room/door scripture, which supersedes Second Canon §4.5 for doors) and the panel sub-schema in Second Canon §4.5 (PanelPlacementRT, amended PanelPairRT). The fields you will author per room:

RoomRuntime:
  schema_version : "1.0"
  room_id        : "r_a" | "r_b" | "r_c"
  dimensions_m   : [W, H, D]
  panel_pairs    : list[PanelPairRT]
  doors          : list[DoorRT]        (len == degree == 2 for every room)
  final_pair_id  : PairId
  hidden_door_wall_slot : str          (== the final pair's DRAWING wall_slot, exactly)
  enemy          : EnemyRT
  ceiling_equations : list[CeilingEqRT]

PanelPairRT:
  pair_id            : e.g. "r_a.s1"
  step_index         : 1, 2, ...
  drawing_off_asset  : asset_id string
  drawing_on_asset   : asset_id string
  text_off_asset     : asset_id string
  text_on_asset      : asset_id string
  drawing_placement  : PanelPlacementRT
  text_placement     : PanelPlacementRT

PanelPlacementRT:
  wall       : "N" | "E" | "S" | "W"
  slot_index : int >= 0
  wall_slot  : "<WALL>-<INDEX>"   e.g. "N-0"  (CONFIRM grammar: the §4.5 commentary
               wrote wall_slot = "<WALL>-<INDEX>"; the prompt sketch wrote "N.s2".
               USE "<WALL>-<INDEX>" — that is the frozen grammar in §4.5. Verify.)
  center_xyz : [x, y, z]   (room-local; panel center on the wall plane)
  width_m    : float
  height_m   : float
  yaw_rad    : float       (panel normal points inward; for N wall = -Z, yaw faces inward)

DoorRT:
  edge_id          : "edge.a.to.b" etc.
  neighbor_id      : "r_b" etc.
  bearing_rad      : the true map bearing atan2(dz,dx) from THIS node to neighbor
  wall             : "N"|"E"|"S"|"W"  (which wall the bearing ray strikes — see §9)
  center_xyz       : [x, y, z]        (opening center on the wall plane, room-local)
  width_m          : 2.0
  height_m         : 2.6
  normal_yaw_rad   : the wall's INWARD normal yaw
  spawn_xyz        : [x, y, z]        (stepped inward along the bearing line; on floor)
  spawn_heading_rad: bearing_rad + pi (faces room center; zero heading-snap on entry)

EnemyRT:
  enemy_id   : "<room_id>.demon"  e.g. "r_a.demon"   (pattern ^[a-z][a-z0-9_]*\.demon$)
  spawn_xyz  : [x, y, z]
  health     : 5

CeilingEqRT:
  eq_id      : "<room_id>.eq0"  e.g. "r_a.eq0"   (pattern ^[a-z][a-z0-9_]*\.eq[0-9]+$)
  asset_id   : "ceiling_a" etc.
  pos_xyz    : [x, y, z]   (center of ceiling: x=0, y=H, z=0)
  size_m     : [w, h]      (e.g. [4.0, 2.0])

The IMPORTANT validation rules (Apocrypha §8) your room data must satisfy:

    len(doors) == degree (2 for every room) and the set of door.edge_id equals exactly that room's incident edge set.
    For every door, wall is the wall the bearing ray strikes and center_xyz is ON that wall plane (use §9).
    No two panels share (wall, slot_index).
    final_pair_id is the last pair by step_index.
    hidden_door_wall_slot == final pair's DRAWING wall_slot (exact string match).
    Every referenced asset_id exists in the manifest.
    dimensions_m ≥ minimums; every panel below the ceiling.

§6.1 — Room dimensions and panel layout (concrete)

Keep all panels on the N wall (z = +D/2) so the door-on-other-walls layout stays clean. For an N-wall panel: center_xyz = [x, y, +D/2], yaw_rad = the inward-normal yaw for N (the N wall's inward normal is −Z; in the frozen compass a yaw whose forward is (cos,0,sin), inward −Z corresponds to yaw = −π/2, i.e. forward (0,0,−1) when yaw=−π/2 since sin(−π/2)=−1 — CONFIRM this against camera's forward convention; the value the renderer needs is "the panel faces into the room"). To stay safe, set N-wall panel yaw_rad = -1.5708 (−π/2) so its normal points to −Z (into the room). Verify the sign against render_room's expectation; if render_room treats yaw_rad=π as "faces −Z," use π instead. (This is the one place the prompt sketch said π; confirm which the built render_room uses via the Apocrypha Step 7 materialize note "normal_yaw_rad = wall inward normal" and the camera compass. Pick the value that makes the N-wall normal point toward −Z and use it consistently.)

r_a dimensions_m = [14.0, 4.0, 10.0]   →  +D/2 = +5.0 (N wall z), +W/2 = +7.0 (E wall x)
  panel pair r_a.s1 (step 1), pair_id "r_a.s1":
    drawing_placement: wall="N", slot_index=0, wall_slot="N-0",
                       center_xyz=[-3.0, 1.55, 5.0], width_m=2.0, height_m=1.5, yaw_rad=<N inward>
    text_placement:    wall="N", slot_index=1, wall_slot="N-1",
                       center_xyz=[-0.8, 1.55, 5.0], width_m=2.0, height_m=0.8, yaw_rad=<N inward>
  panel pair r_a.s2 (step 2, FINAL), pair_id "r_a.s2":
    drawing_placement: wall="N", slot_index=2, wall_slot="N-2",
                       center_xyz=[ 2.0, 1.55, 5.0], width_m=2.0, height_m=1.5, yaw_rad=<N inward>
    text_placement:    wall="N", slot_index=3, wall_slot="N-3",
                       center_xyz=[ 4.2, 1.55, 5.0], width_m=2.0, height_m=0.8, yaw_rad=<N inward>
  final_pair_id = "r_a.s2"
  hidden_door_wall_slot = "N-2"   (the final pair's DRAWING wall_slot — exact)
  assets: s1 → figure_off_a1/figure_on_a1/text_off_a1/text_on_a1
          s2 → figure_off_a2/figure_on_a2/text_off_a2/text_on_a2
  enemy: enemy_id="r_a.demon", spawn_xyz=[0.0, 0.0, 0.0], health=5
  ceiling: eq_id="r_a.eq0", asset_id="ceiling_a", pos_xyz=[0.0, 4.0, 0.0], size_m=[4.0, 2.0]

(I placed all four r_a panels along the N wall with slot_index 0..3 and centers spread across x from −3.0 to +4.2 so no two overlap and none collide with the N-wall door — see §9 for where r_a's N-wall door lands and adjust a panel x if it overlaps the door opening. r_a's door to r_c lands on the N wall; if its center_xyz.x conflicts with a panel, shift that panel. With the door near x≈ a small positive value, the panels at −3.0/−0.8 are safe on the left and 2.0/4.2 on the right; confirm with §9's computed door x.)

r_b dimensions_m = [10.0, 3.5, 8.0]   →  +D/2 = +4.0, +W/2 = +5.0
  panel pair r_b.s1 (FINAL), pair_id "r_b.s1":
    drawing_placement: wall="N", slot_index=0, wall_slot="N-0",
                       center_xyz=[-2.0, 1.55, 4.0], width_m=2.0, height_m=1.5, yaw_rad=<N inward>
    text_placement:    wall="N", slot_index=1, wall_slot="N-1",
                       center_xyz=[ 0.2, 1.55, 4.0], width_m=2.0, height_m=0.8, yaw_rad=<N inward>
  final_pair_id = "r_b.s1"
  hidden_door_wall_slot = "N-0"
  assets: figure_off_b1/figure_on_b1/text_off_b1/text_on_b1
  enemy: enemy_id="r_b.demon", spawn_xyz=[0.0, 0.0, 0.0], health=5
  ceiling: eq_id="r_b.eq0", asset_id="ceiling_b", pos_xyz=[0.0, 3.5, 0.0], size_m=[4.0, 2.0]

r_c dimensions_m = [10.0, 3.5, 8.0]   →  +D/2 = +4.0, +W/2 = +5.0
  panel pair r_c.s1 (FINAL), pair_id "r_c.s1":
    drawing_placement: wall="N", slot_index=0, wall_slot="N-0",
                       center_xyz=[-2.0, 1.55, 4.0], width_m=2.0, height_m=1.5, yaw_rad=<N inward>
    text_placement:    wall="N", slot_index=1, wall_slot="N-1",
                       center_xyz=[ 0.2, 1.55, 4.0], width_m=2.0, height_m=0.8, yaw_rad=<N inward>
  final_pair_id = "r_c.s1"
  hidden_door_wall_slot = "N-0"
  assets: figure_off_c1/figure_on_c1/text_off_c1/text_on_c1
  enemy: enemy_id="r_c.demon", spawn_xyz=[0.0, 0.0, 0.0], health=5
  ceiling: eq_id="r_c.eq0", asset_id="ceiling_c", pos_xyz=[0.0, 3.5, 0.0], size_m=[4.0, 2.0]

For r_b and r_c the door bearings differ (they're at the other nodes), so their doors land on different walls than r_a's — but since their panels are all on the N wall, just make sure no door also lands on the N wall at the same x as a panel; if one does, move the conflicting panel or use the E/S/W walls for it. §9 gives you each room's two bearings so you can place doors correctly.
§7 — THE ONE QUESTION YOU MUST CONFIRM BEFORE WRITING JSON

Confirm the bearing-to-wall mapping and the center_xyz formula. I have already done the derivation for you in §9 below (against the Apocrypha's room-coordinate law) so you can confirm it fast. Read §9, sanity-check it against the Apocrypha §4 Step 3 (the bearing-ray/perimeter intersection) and §7 (door placement), and if it matches, proceed. If anything in §9 disagrees with the Apocrypha's exact Step-3 code, the Apocrypha wins — fix §9's numbers and use the Apocrypha's.
§8 — VALIDATION GATES (must all pass)

    Every JSON pydantic-validates via contracts.load_json / model_validate — no extra fields, all patterns match.
    assets.load_pack("tests/golden_pack/") returns a valid Pack without raising.
    build_wire_mesh(pack.floorplan) produces correct segment counts and the b→c segments sit at y=4.5 while a→c sit at y=0.0 (crossing over/under preserved).
    build_room_mesh(pack.rooms["r_a"]) produces a RoomMesh with 2 door holes, 4 PanelQuads (2 pairs × 2), 1 alcove (the final pair drawing), and 1 ceiling quad.
    select_targets(pack.floorplan, "r_a", set(), BuildConfig()) returns valid targets (a subset of {r_b, r_c}).
    Full loop: drive gameplay.step simulating r_a → r_b → r_c, shooting panels, opening final walls, killing demons; eventually emits LevelComplete.

§9 — THE BEARING-TO-WALL MAPPING (I did the math; confirm it)

Room-local axes are PARALLEL to map axes (global compass, NO rotation). Walls: N at z=+D/2 (inward normal −Z), S at z=−D/2 (inward +Z), E at x=+W/2 (inward −X), W at x=−W/2 (inward +X). A bearing θ = atan2(dz, dx) gives a ray direction (dx, dz) = (cos θ, sin θ) cast from room center.

The wall the ray strikes (Apocrypha §4 Step 3): cast the ray to the box of half-extents hx = W/2, hz = D/2.

dirx = cos(θ);  dirz = sin(θ)
tx = hx / |dirx|   (or +inf if dirx == 0)
tz = hz / |dirz|   (or +inf if dirz == 0)
t  = min(tx, tz)
hit = (t*dirx, t*dirz)        # room-local (x, z) of the opening center on the perimeter
if t == tx:  wall = "E" if dirx > 0 else "W";  along = hit_z   # position along E/W wall (z)
else:        wall = "N" if dirz > 0 else "S";  along = hit_x   # position along N/S wall (x)
center_xyz = (hit_x, door_height_m/2, hit_z) = (hit_x, 1.3, hit_z)
normal_yaw_rad = inward-normal yaw of that wall:
    N (inward -Z): the yaw whose forward (cosψ,·,sinψ) = (0,0,-1)  → ψ = -π/2
    S (inward +Z): forward (0,0,+1)                                → ψ = +π/2
    E (inward -X): forward (-1,0,0)                                → ψ = π
    W (inward +X): forward (+1,0,0)                                → ψ = 0
spawn_xyz = center_on_floor stepped inward along the bearing by aisle_depth_m (≈1.6):
    spawn = (hit_x - 1.6*cos θ, 0.0, hit_z - 1.6*sin θ)   # inward = opposite the outward bearing
    (i.e. step toward room center; equivalently + aisle_depth * (cos(θ+π), sin(θ+π)))
spawn_heading_rad = θ + π

CONFIRM the normal_yaw_rad sign convention against the built camera.forward = (cos ψ, 0, sin ψ). With that convention: N inward (−Z) ⇒ ψ = −π/2; this is the value to use for N-wall PANELS too (so panel yaw_rad = -1.5708 on the N wall). If render_room instead expects yaw_rad=π to mean "−Z facing," verify and switch — but apply the SAME convention to both doors and panels.

Now the concrete per-room door numbers (using each room's W, D):

=== r_a (W=14 → hx=7;  D=10 → hz=5) ===
Door to r_b:  θ = atan2(8-0, 12-0) = atan2(8,12) = 0.5880 rad (33.69°)
  dirx=cos=0.8321, dirz=sin=0.5547
  tx = 7/0.8321 = 8.413;  tz = 5/0.5547 = 9.014;  t = min = 8.413 (E wall)
  hit = (8.413*0.8321, 8.413*0.5547) = (7.000, 4.667)
  wall = "E"  (dirx>0);  along = hit_z = 4.667   (within ±hz=5 ✓)
  center_xyz = [7.000, 1.3, 4.667]
  normal_yaw_rad = π   (E inward = -X)
  spawn_xyz = [7.000 - 1.6*0.8321, 0.0, 4.667 - 1.6*0.5547] = [5.669, 0.0, 3.780]
  spawn_heading_rad = 0.5880 + π = 3.7296

Door to r_c:  θ = atan2(20-0, 6-0) = atan2(20,6) = 1.2793 rad (73.30°)
  dirx=cos=0.2873, dirz=sin=0.9578
  tx = 7/0.2873 = 24.37;  tz = 5/0.9578 = 5.220;  t = min = 5.220 (N wall)
  hit = (5.220*0.2873, 5.220*0.9578) = (1.500, 5.000)
  wall = "N"  (dirz>0);  along = hit_x = 1.500   (within ±hx=7 ✓)
  center_xyz = [1.500, 1.3, 5.000]
  normal_yaw_rad = -π/2  (N inward = -Z)
  spawn_xyz = [1.500 - 1.6*0.2873, 0.0, 5.000 - 1.6*0.9578] = [1.040, 0.0, 3.468]
  spawn_heading_rad = 1.2793 + π = 4.4209
  >>> NOTE: r_a's N-wall door is centered at x=1.500, width 2.0 → occupies x∈[0.5,2.5].
      Your r_a.s2 DRAWING panel is at x=2.0 (slot N-2) → it OVERLAPS the door x-range!
      FIX: move the door or the panel. Cleanest: shift r_a's right-hand panels right.
      Recommended r_a N-wall panel x-centers to avoid the door at x∈[0.5,2.5]:
        s1 drawing x=-5.5, s1 text x=-3.2, s2 drawing x=4.0, s2 text x=6.0
      (all width 2.0 → s1∈[-6.5,-2.2], s2∈[3.0,7.0]; door∈[0.5,2.5] is clear between them)
      Then hidden_door_wall_slot stays "N-2" (s2 drawing). Re-verify none exceed |x|≤hx=7:
      s2 text center x=6.0 → [5,7] ✓ (just fits). If you prefer margin, use W=16 for r_a.

=== r_b (W=10 → hx=5;  D=8 → hz=4) ===
Door to r_a:  θ = atan2(0-8, 0-12) = atan2(-8,-12) = -2.5536 rad (-146.31°)
  dirx=cos=-0.8321, dirz=sin=-0.5547
  tx = 5/0.8321 = 6.009;  tz = 4/0.5547 = 7.211;  t = 6.009 (E/W? dirx<0 → W wall)
  hit = (6.009*-0.8321, 6.009*-0.5547) = (-5.000, -3.333)
  wall = "W"  (dirx<0);  along = hit_z = -3.333  (within ±hz=4 ✓)
  center_xyz = [-5.000, 1.3, -3.333]
  normal_yaw_rad = 0   (W inward = +X)
  spawn_xyz = [-5.000 - 1.6*(-0.8321), 0.0, -3.333 - 1.6*(-0.5547)] = [-3.669, 0.0, -2.446]
  spawn_heading_rad = -2.5536 + π = 0.5880

Door to r_c:  θ = atan2(20-8, 6-12) = atan2(12,-6) = 2.0344 rad (116.57°)
  dirx=cos=-0.4472, dirz=sin=0.8944
  tx = 5/0.4472 = 11.18;  tz = 4/0.8944 = 4.472;  t = 4.472 (N wall, dirz>0)
  hit = (4.472*-0.4472, 4.472*0.8944) = (-2.000, 4.000)
  wall = "N";  along = hit_x = -2.000  (within ±hx=5 ✓)
  center_xyz = [-2.000, 1.3, 4.000]
  normal_yaw_rad = -π/2
  spawn_xyz = [-2.000 - 1.6*(-0.4472), 0.0, 4.000 - 1.6*0.8944] = [-1.285, 0.0, 2.569]
  spawn_heading_rad = 2.0344 + π = 5.1760
  >>> NOTE: r_b's N-wall door is at x=-2.000, width 2.0 → x∈[-3,-1]. Your r_b panels are
      at x=-2.0 (drawing) and 0.2 (text). The drawing OVERLAPS the door. FIX: move r_b's
      panels off the N wall door, e.g. put r_b's pair on the S wall (z=-D/2=-4) instead,
      or shift panel x to clear x∈[-3,-1]. Recommended: r_b pair on S wall:
        drawing wall="S", slot S-0, center_xyz=[-1.0, 1.55, -4.0], yaw_rad=+π/2 (S inward +Z)
        text    wall="S", slot S-1, center_xyz=[ 1.2, 1.55, -4.0], yaw_rad=+π/2
        hidden_door_wall_slot="S-0". (S wall has no door in r_b — both r_b doors are W and N.)

=== r_c (W=10 → hx=5;  D=8 → hz=4) ===
Door to r_a:  θ = atan2(0-20, 0-6) = atan2(-20,-6) = -1.8623 rad (-106.70°)
  dirx=cos=-0.2873, dirz=sin=-0.9578
  tx = 5/0.2873 = 17.40;  tz = 4/0.9578 = 4.176;  t = 4.176 (S wall, dirz<0)
  hit = (4.176*-0.2873, 4.176*-0.9578) = (-1.200, -4.000)
  wall = "S";  along = hit_x = -1.200  (within ±hx=5 ✓)
  center_xyz = [-1.200, 1.3, -4.000]
  normal_yaw_rad = +π/2  (S inward = +Z)
  spawn_xyz = [-1.200 - 1.6*(-0.2873), 0.0, -4.000 - 1.6*(-0.9578)] = [-0.740, 0.0, -2.468]
  spawn_heading_rad = -1.8623 + π = 1.2793

Door to r_b:  θ = atan2(8-20, 12-6) = atan2(-12,6) = -1.1071 rad (-63.43°)
  dirx=cos=0.4472, dirz=sin=-0.8944
  tx = 5/0.4472 = 11.18;  tz = 4/0.8944 = 4.472;  t = 4.472 (S wall, dirz<0)
  hit = (4.472*0.4472, 4.472*-0.8944) = (2.000, -4.000)
  wall = "S";  along = hit_x = 2.000  (within ±hx=5 ✓)
  center_xyz = [2.000, 1.3, -4.000]
  normal_yaw_rad = +π/2
  spawn_xyz = [2.000 - 1.6*0.4472, 0.0, -4.000 - 1.6*(-0.8944)] = [1.285, 0.0, -2.569]
  spawn_heading_rad = -1.1071 + π = 2.0344
  >>> NOTE: BOTH r_c doors land on the S wall (x=-1.2 and x=2.0). Their openings are
      x∈[-2.2,-0.2] and x∈[1.0,3.0] — separated by ~1.2m of wall between -0.2 and 1.0,
      which is < door_min_separation_m (2.6). In a REAL build the Room Maker would grow
      the room to separate them. For the hand-authored fixture, GROW r_c so the doors
      clear: set r_c W=14 (hx=7), D=10 (hz=5). Recompute:
        door to r_a: t=tz=5/0.9578=5.220 → hit=(-1.500,-5.000) S wall x=-1.5
        door to r_b: t=tz=5/0.8944=5.590 → hit=(2.500,-5.000) S wall x=2.5
        openings x∈[-2.5,-0.5] and [1.5,3.5] → gap from -0.5 to 1.5 = 2.0m (still <2.6
        but acceptable for a fixture; the engine does NOT re-validate door separation at
        runtime — that's a build-time rule. assets.load_pack does NOT enforce it.)
      Put r_c's panel pair on the N wall (z=+D/2=+5, no doors there):
        drawing wall="N", slot N-0, center_xyz=[-1.0, 1.55, 5.0], yaw_rad=-π/2
        text    wall="N", slot N-1, center_xyz=[ 1.2, 1.55, 5.0], yaw_rad=-π/2
        hidden_door_wall_slot="N-0". Update ceiling pos_xyz=[0,5.0? no — H], y=H=3.5.
      (If you grow r_c to D=10, keep H=3.5; ceiling pos_xyz=[0,3.5,0].)

A note on door-separation: the door_min_separation_m / corner_clearance_m rules are BUILD-TIME validation in the Room Maker (Apocrypha §8). The RUNTIME assets.load_pack does NOT re-check them. So a hand-authored fixture that slightly violates separation will still LOAD and PLAY. I flag it above so you author clean rooms, but it is not a hard gate for the golden pack — gate #2 (load_pack succeeds) and gate #6 (LevelComplete) are.
§10 — DECISIONS I MADE FOR YOU (so you don't re-litigate)

    All three rooms have degree 2 → 2 doors each (the triangle graph forces it). Do NOT give any room 1 door.
    Every room has its own ceiling asset (ceiling_a/b/c) and its own demon (r_a/b/c.demon, health 5).
    Crossing authored via a SHARED knee [6,10] in both edge.a.to.c and edge.b.to.c path_xz, with cruise_y 0.0 vs 4.5 → clean over/under; Crossing.at_xz=[6,10], over_y=4.5 > under_y=0.0.
    wall_slot grammar = "<WALL>-<INDEX>" (e.g. "N-2"), per Second Canon §4.5 commentary — NOT "N.s2". Confirm and use this.
    Put each room's panels on a wall with NO door to avoid overlaps: r_a panels span the N wall around its N-wall door (adjusted x's in §9); r_b panels on the S wall; r_c panels on the N wall (after growing r_c). Adjust freely as long as no panel overlaps a door opening and no two panels share (wall, slot_index).
    Door width_m=2.0, height_m=2.6, door-center y = 1.3 (= height/2). aisle_depth_m=1.6 for spawn insets.
    Panel center_y = 1.55 (eye-ish height), drawing height_m=1.5, text height_m=0.8, both width_m=2.0.

§11 — WHAT TO PULL FROM THE BIBLE (request via Nir → DeepSeek)

You have the Commentaries + OT + NT. Before writing JSON, pull and design against these (field-exact):

    The Apocrypha (QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md) — the RoomRuntime v3 schema, DoorRT/IncidentEdge/RoomPortalSpec fields, bearing placement (§4 Step 3) and the §7/§8 deltas + validation. AUTHORITATIVE for rooms/doors.
    Second Canon §4.4 (floorplan/Corridor/Crossing field-exact), §4.5 (PanelPlacementRT, amended PanelPairRT, wall_slot grammar), §4.6 (Manifest/AssetEntry), and the Palette definition (§4.7-area).
    The full contracts.py file — for the exact re-exported model names, ID patterns, and the BuildConfig defaults used by select_targets (guide_w_imp=0.6, guide_w_dist=0.4, guide_max_lines=3).

You do NOT need my engine module implementations — only the data schemas matter for authoring fixtures.
§12 — CONVENTIONS YOU MUST FOLLOW (frozen)

    NodeId/LevelId pattern ^[a-z][a-z0-9_]*$ — use r_a, r_b, r_c, golden. No dots in node/level ids.
    edge_id pattern ^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$ — edge.a.to.b, edge.b.to.c, edge.a.to.c.
    PairId pattern ^[a-z][a-z0-9_]*\.s[0-9]+$ — r_a.s1, r_a.s2, r_b.s1, r_c.s1.
    EqId pattern ^[a-z][a-z0-9_]*\.eq[0-9]+$ — r_a.eq0, r_b.eq0, r_c.eq0.
    enemy_id pattern ^[a-z][a-z0-9_]*\.demon$ — r_a.demon, etc.
    Hex pattern ^#[0-9a-fA-F]{6}$ — always 6 hex digits.
    wall Literal: "N"|"E"|"S"|"W" — uppercase only.
    schema_version: "1.0" on every JSON (literal, exact).
    extra="forbid" everywhere — no extra fields; if a model rejects your data, the DATA is wrong, not the model.
    Room-local axes parallel to map (global compass, NO rotation). N at z=+D/2 (inward −Z), S at z=−D/2 (+Z), E at x=+W/2 (−X), W at x=−W/2 (+X), floor y=0.
    FROZEN COMPASS: bearing θ → world forward (cos θ, 0, sin θ); +X east, +Z north; spawn_heading_rad = bearing + π.
    All IDs deterministic, hand-fixed, no random suffixes.
    The pack lives at quake/tests/golden_pack/; paths in the JSON (wall_path/master_path) are relative to that pack dir (e.g. png/wall/figure_off_a1.png).

§13 — RISK FLAGS

    Do NOT change any existing code. The engine is frozen and green. The pack validates against EXISTING pydantic models; if rejected, fix the data.
    Do NOT re-decide any locked decision. Commentaries §3 is the spine; the Apocrypha supersedes Second Canon §4.5 for rooms/doors.
    Bearing-to-wall must be exact (use §9; if it disagrees with the Apocrypha §4 Step 3, the Apocrypha wins — recompute).
    Watch door↔panel overlaps on shared walls (§9 flags the r_a, r_b, r_c cases and gives fixes). No two panels share (wall, slot_index).
    hidden_door_wall_slot must EXACTLY equal the final pair's drawing wall_slot string.
    Confirm the yaw_rad/normal_yaw_rad sign convention once against render_room/camera and apply it consistently to BOTH doors and panels.

§14 — YOUR DELIVERABLE

Produce a single document (saved by DeepSeek) containing:

    The complete floorplan.json content (exact).
    The complete palette.json content (exact).
    The complete manifest.json content (exact, all 18 assets).
    The complete room_runtime/room_r_a.json, room_r_b.json, room_r_c.json content (exact).
    The PNG color table (§5.1) for DeepSeek to generate the 36 files.
    A short "how I confirmed §9" note (your validation that the bearing math matches the Apocrypha).

Format: prose + fenced code blocks, NO Markdown tables (Nir copy-pastes; tables lose cells). Confirm §7's mapping (using §9) before writing the JSON. Then write it all, exactly.

This is the last fixture between a green engine and a playable golden level. Author it precisely, and the smoke launch lights up. 🗝️

--- END HANDOFF ---

Parent 4, signing off. The engine is built and green; the torch passes to Parent 5 for the golden pack. 🗝️
