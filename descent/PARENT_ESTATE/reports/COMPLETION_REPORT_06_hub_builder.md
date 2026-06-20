COMPLETION REPORT — hub_builder — 2026-06-13

FILES: hub_builder.py, hub_demo.py — screenshot-verified? N (written against the verified signatures Nir relayed; I did not run it. Needs Nir/DeepSeek to flythrough N=1,3,7,12. See DEEPSEEK TODOS.)
FINAL SIGNATURES (locked for app/game_state)

build_hub(level_data, atrium_center=(0,0,0)) -> HubGeometry
    # level_data: iterable of CorridorData (each has .title)

HubGeometry.corridors            -> list[CorridorGeometry]
HubGeometry.door_poses()         -> list[((x,y,z),(nx,ny,nz))]   # center + OUTWARD normal
HubGeometry.inside(point, margin=0.0) -> bool   # atrium interior OR any corridor
HubGeometry.spawn_pose()         -> ((x,y,z),(yaw,pitch))   # RADIANS, see below
HubGeometry.update(dt, ship_position) -> None
HubGeometry.draw_world(cr, cu, texcache)  -> None   # QUEUES walls; NO flush
HubGeometry.draw_robots(cr, cu, texcache) -> None
HubGeometry.draw_labels(cr, cu, texcache) -> None

    spawn_pose orientation form: ((x,y,z), (yaw, pitch)) in radians, computed from the first Fibonacci direction d0​ as yaw=atan2(dx​,−dz​), pitch=asin(dy​) (convention: forward = −Z, yaw about +Y, pitch about +X). Returned because no quat_look_along exists in render. ⚠️ game_state must convert (yaw,pitch)→quaternion itself (or request a helper from the parent — see REQUESTS). My demo currently seats the ship at the spawn position only.
    door_poses shape: list of ((x,y,z),(nx,ny,nz)) — door center (world) + OUTWARD unit normal (== Fibonacci direction). The normal points out of the atrium, opposite each corridor's entrance_pose() normal.

ATTACHMENT METHOD CHOSEN

Option 1 (build-at-pose). Verified from relayed corridor_builder contract: build_corridor(corridor_data, origin, direction) places the corridor start at origin and extrudes along direction (forward = into corridor, away from hub), and entrance_pose()'s normal points back toward the hub. So building with origin=door_center_i, direction=dir_i lands the mouth on the doorway, aimed outward — no post-hoc transforms (no transforming seg_bounds / robots / hostages / labels). This is the clean, non-fragile path.
FIBONACCI

Implemented exactly per brief (golden =π(3−5
​), y=1−2(i+0.5)/N). Door spread for N=1,3,7,12 NOT yet screenshot-confirmed (demo not run). The N=1 case yields a single direction at y=0 (equator) — single door is fine. No anti-collision constraint added (proof honored); corridors bend freely.
FRAME ORDER

Demo obeys draw_world -> flush_walls(ship.pos) -> draw_robots -> draw_labels; flush_walls called exactly once per frame. draw_world only QUEUES (atrium shell + door frames) then delegates to each corridor's draw_world so all walls land in the single shared queue. Mathtext label ids are not display-listed.
LEVEL INPUT

No level container exists in content_parser. build_hub accepts a plain list[CorridorData] (uses .title for door labels). Demo uses discover_corridors("corridors") and duplicates the single fixture 01_dummy.txt to reach N>1 — flagged for when real fixtures/level parser arrive.
KEY DECISIONS / DEVIATIONS / TRAPS

    Shell = lat/long faceted hollow sphere; facets whose center falls inside a door opening are omitted (doorways left OPEN, not sealed). Opening angular radius derived from DOOR_OPENING_SCALE * TUBE_RADIUS.
    Door frames = short cylindrical collar extruded DOOR_FRAME_DEPTH along the normal — the "a tunnel begins here" rim.
    ⚠️ FIT constraint (not anti-collision): ATRIUM_RADIUS must be large enough that radius-6 mouths don't overlap at N=12 (min sep ~63°). Default ATRIUM_RADIUS=34.0 is a guess — DeepSeek must verify visually.
    No chroma added to grey world (door chevrons use WORLD_EDGE/WORLD_WALL_FILL only). Hue-family door hints left as a parent-gated option I did NOT take.
    WORLD_WALL_FILL is RGBA; I split it into (rgb, alpha) for queue_wall(quad, fill, edge, alpha).

REQUESTS TO PARENT

    (Optional) quat_look_along(dir, up) in render — so spawn_pose can return a quaternion the Ship/game_state consumes directly. Without it, game_state must convert (yaw,pitch). I did not add it (don't touch render). Please decide where the conversion lives.
    Confirm spawn_pose form — is (yaw,pitch) radians acceptable to game_state, or do you want a quaternion (needs req #1)?
    Level parser — if/when you add a level container exposing ordered corridors + titles, tell me the shape and I'll switch build_hub from list[CorridorData] to it.
    N>12 is explicitly out of scope per the proof — flagged, not solved.

OLD-CODE REUSE

None from Fable. All geometry helpers (_basis_for, _ring_points, shell builder) written fresh for this module.
DEEPSEEK TODOS

    Tune ATRIUM_RADIUS (34.0), ATRIUM_FACETS (10), DOOR_FRAME_DEPTH (5.0), DOOR_OPENING_SCALE (1.10) — acceptance tests are inline at each constant.
    Run flythrough at N=1, 3, 7, 12. Confirm: doors spread over the whole sphere (poles + between, not a ring); grey rock visibly separates every door pair at N=12; corridors don't punch into each other (proof); fog reveals gracefully; door title labels readable. Send screenshots.