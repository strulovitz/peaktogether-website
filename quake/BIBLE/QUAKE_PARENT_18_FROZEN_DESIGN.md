This is everything I needed. The picture is now completely clear, and it confirms my framing: the machinery all exists and is even designed for ramps — it's just fed flat data and never wired to the GPU in three spots. The most striking finding is A3/D: _CorridorNav._floor_height() already interpolates socket→cruise→socket; it's been driving on flat tyres solely because socket_y=0.0. Fix the one number's source and ramps come alive in nav for free.

Here is the frozen design.
PARENT 18 — FROZEN DESIGN: REAL 3D CORRIDORS (De-Amputate · Un-Flatten · Wire)
Guiding principle

There is no new renderer, no new nav, no teleport, no solid tunnel. Mode A is the corridor world and it is correct in spirit. This design is four surgical fixes that (1) stop amputating the graph, (2) give corridors real height so bridges/underpasses physically exist in wire and under the feet, (3) push the already-computed guide-lines and arrowheads to the GPU, and (4) make ramps walkable. Every fix reuses an existing, already-designed mechanism.

The single root cause behind two of the four defects is socket_y = 0.0. Kill that and the nav ramp-interpolation engine (which already exists) starts working.
FIX 1 — DE-AMPUTATE: render the full graph, not a 2-room stub

Defect: _single_corridor_floorplan() hands Mode A a 2-room / 1-corridor / crossings=[] stub, so the player sees no surrounding corridors, no bridges, no receding glow.

Verified enabling fact: the door-exit spawn (gameplay.py:130-165) already places the player in full-floorplan world coordinates (fr.map_xz + 2 m toward the far end, heading toward it). So rendering the full floorplan needs no coordinate transform — the player is already standing at the right spot in the right space. And nothing at runtime reads fp.crossings (B2), so the full floorplan renders correctly as-is.

Change (surgical):

    Delete the amputation. In app.py render dispatch (~470), when state.mode == "corridor", render pack.floorplan (the full graph), not _active_corridor[0].
    _single_corridor_floorplan() and the _active_corridor mechanism are removed (or left dead and unused; DeepSeek's call, but the design's intent is: the corridor mode always renders the whole graph).
    FrameOutcome.travel_edge_id is no longer needed to filter rendering. It is still useful as "which corridor am I currently on" for guide-line origin and nav (see Fix 3/4), so keep the value; just stop using it to slice the floorplan.

Result: exiting a door drops you onto your corridor with the entire glowing graph around you — near-bright, distance-dimmed to dark grey, bridges and underpasses present, exactly as §3.1 specifies.
FIX 2 — UN-FLATTEN: give corridors real endpoint-vs-cruise height (the ramp shape)

Defect: every corridor is drawn and walked at a single flat cruise_y; socket_y=0.0 everywhere, so Crossing.over_y/under_y never manifest as physical bridges.

The ramp shape (the model, stated precisely): a corridor is low at its two room ends, high in its cruising middle. Rooms sit at ground level; a corridor rises on a ramp out of its source room, cruises at its cruise_y (its height layer), and ramps back down into its target room. Where a high-layer corridor cruises over a low-layer one, that's the bridge; the lower one passes under at its cruise height. This is already the intended semantics of _height_at_vertex() — endpoints use socket_y, interior vertices use cruise_y.

The problem: socket_y is the wrong value (0.0), and path_xz has no interior vertices near the ends to ramp to — a corridor whose path_xz is just [start, end] has no place to hold cruise_y because both its vertices are endpoints.

Change — two parts, both in build-time level_maker.py (data), so runtime just reads it:

2a. Rooms stay at ground; keep socket_y = 0.0. This is correct — rooms are the ground level. The bug isn't the room socket value; it's that the corridor never rises above it. So do not change room socket_y. Instead:

2b. Give every corridor a ramped path_xz + a per-vertex height, computed at build time. For each corridor, level_maker already knows its cruise_y (from height_level) and its endpoints. Emit a path_xz that guarantees interior cruise vertices:

    If a corridor's path_xz is a bare [A, B] (no crossing waypoints), insert two interior waypoints, one a short ramp-run r metres in from each end, so the path becomes [A, A→ramp_top, …crossings…, B→ramp_top, B].
    Compute a per-vertex Y for the corridor: endpoints (index 0 and last) get socket_y (0.0); the ramp-top and all interior/crossing vertices get cruise_y. Linear along the ramp segment between them.

The data-model gap this exposes (honest, load-bearing): path_xz is Vec2 (2D only), and there is currently no per-vertex Y storage on Corridor (A2). Runtime recomputes Y from socket/cruise via _height_at_vertex(), which works only for the simple endpoint/interior rule. Two clean options — I recommend Option A:

    Option A (recommended — no schema change to path): keep path_xz 2D; keep the endpoint/interior height rule as the single source of truth for Y, computed identically in both render_wire.build_wire_mesh() and nav_collision._height_at_vertex(). level_maker guarantees the ramp shape by inserting the two ramp-top waypoints (2b), and both renderer and nav apply the same rule: Y = socket_y at index 0 and last; Y = cruise_y at every interior vertex. No new field. The ramp is the two short segments from an endpoint (socket_y) to the first/last interior vertex (cruise_y). This keeps one rule in two mirrored places — acceptable and small.
    Option B (schema change): add path_y: list[float] to Corridor, computed once in level_maker, consumed verbatim by both renderer and nav. More robust (single source, no duplicated rule) but touches the frozen Corridor contract and every producer/consumer + golden fixtures. Do not take this unless Option A's duplicated-rule mirror proves fragile.

Change to render_wire.build_wire_mesh() (Fix 2, render side): stop stamping one y = cor.cruise_y on all vertices. Instead, per corridor, compute the per-vertex Y by the endpoint/interior rule above (Option A) and emit each segment with its true start/end Y. The camera-facing thick-quad path already handles arbitrary 3D segment endpoints, so ramps and bridges render with no shader change.

Change to nav (Fix 2, walk side): none needed beyond Fix 4 — _floor_height()/_height_at_vertex() already interpolate; once path_xz has the ramp waypoints (2b) and the endpoint/interior rule is applied, the player walks the ramp automatically. (See Fix 4 for the one caveat.)

Layer→world-Y and ramp length already exist as config (base + layer·Δy for cruise_y; pick a ramp run r, e.g. a few metres, as a new defaulted BuildConfig field corridor_ramp_run_m). Caps/re-seed logic (§8.1) is untouched.
FIX 3 — WIRE THE GUIDE-LINES + ARROWHEADS TO THE GPU

Defect: _gl_draw_strip() returns doing nothing; all the correct route/arrowhead geometry dies in memory.

Verified API (C1/C2): use the simple wire_program(ctx) (not the thick-quad program — that would billboard floor lines, wrong). Uniform u_mvp via .write(_mvp_bytes(view, proj)). VAO = [(vbo_pos,'3f','in_pos'),(vbo_col,'3f','in_color')], mode = moderngl.LINE_STRIP for routes and moderngl.LINES for arrowhead barbs. Drawn into the same scene FBO after the wireframe, inheriting GL_DEPTH_TEST (GL_LESS) — so a guide-line correctly disappears behind a near bridge. Guide-lines stay bright (no distance-dim), which is why the simple program (pass-through color, no u_dim_*) is exactly right.

Change — un-stub _gl_draw_strip():

build once (or cache): prog = wire_program(ctx)
per draw:
  prog['u_mvp'].write(_mvp_bytes(view, proj))
  vbo_p = ctx.buffer(points_xyz .astype(f4).tobytes())
  vbo_c = ctx.buffer(colors     .astype(f4).tobytes())   # color_rgb per vertex
  vao   = ctx.vertex_array(prog, [(vbo_p,'3f','in_pos'),(vbo_c,'3f','in_color')], mode=LINE_STRIP)
  vao.render()

    Route strips → LINE_STRIP; arrowhead barbs (_arrowhead_xz already builds the two barb segments) → LINES.
    Color per target's map_color (already computed in draw_guidelines) — each of the ≤3 lines wears its target room's importance color, matching its map ring (§8.2).
    Depth-tested against the wire, as confirmed.

Note on alpha: the wire fragment shader outputs vec4(color, 1.0) — no alpha uniform. Guide-lines are opaque bright lines, which is correct. Drop the alpha parameter's effect (or keep the signature and ignore it). Do not add blending — the whole Mode A is depth-tested, no-blend by invariant.
FIX 4 — MAKE GUIDE-LINES + FEET FOLLOW THE FLOOR (3D-aware routing)

Defect (D): _gl_floor_y() returns socket_y + 0.02 (always ≈0.02); _route_xz() is 2D. Once corridors have height, guide-lines would sit at the floor of a bridge that's now overhead — wrong. And the player's feet must climb the ramp.

Change — routing becomes 3D-aware, using the same height rule as Fix 2:

    _route_xz() (or a new _route_xyz()) computes, for each vertex along the route, the walkable floor Y by calling the same corridor height rule used by nav/render (endpoint/interior → socket_y/cruise_y, interpolated along ramps). The guide-line then rides the ramp up, holds bridge height across the bridge, ramps down into the target-room mouth — sitting a small +0.02 m above the walkable floor so it reads as painted-on.
    Player feet (nav): already handled by Fix 2 + the existing _floor_height() interpolation, with one caveat to surface: _CorridorNav finds the nearest corridor segment and clamps the player to it (Q4). At a crossing, two corridors overlap in XZ but at different Y — "nearest segment" by XZ alone could snap the player to the wrong (under) corridor while they're on the (over) bridge. Nav must disambiguate by Y: pick the nearest segment whose interpolated floor Y is closest to the player's current Y, not merely nearest in XZ. This is the one genuinely new bit of nav logic in the whole design, and it's small. (§8.3's invariant holds: a crossing is visual/spatial only — you can't hop between stacked corridors; you commit to the one you ramped onto.)

Single-source-of-truth requirement (important for correctness): the corridor height function must be computed by one helper, imported/shared by render_wire, nav_collision, and guidelines, so the wire you see, the floor you walk, and the guide-line you follow are byte-identical. If DeepSeek implements Option A (no path_y field), this shared helper is mandatory to prevent the three from drifting. (This is the argument for Option B; I still recommend A + shared helper for surgical minimality.)
Acceptance criteria (§4.F, made concrete)

    Exit any room door → you stand on that corridor with the full glowing graph around you, distance-dimmed white→grey, never black.
    Bridges and underpasses are visibly 3D in the wireframe — a corridor ramps up over another that passes under it.
    You can walk up a ramp onto a bridge, cross it, and ramp down into the destination room; you cannot fall through and cannot hop to the corridor below you.
    ≤3 colored guide-lines appear on the floor, each colored by its target room's importance, with arrowheads pointing along the route, and they follow the ramp/bridge height (ride the floor), correctly occluded behind near geometry.
    Reaching the far room's socket enters that room at its door spawn (existing mechanic, unchanged).
    Works for any connected room pair in the Principia pack, at any graph size (no hardcoded counts — inherits Parent 8's scale-free engine).

Honest gaps / risks

    G1 — Duplicated height rule (Option A). Y is derived in three places (render/nav/guidelines). Mitigated by mandating a single shared helper. If that proves fragile in review, escalate to Option B (path_y on Corridor) — a frozen-contract change requiring golden-fixture updates and Architect gating; flag to Nir before taking it.
    G2 — Crossing Y-disambiguation in nav. New logic; must be covered by a test with two corridors crossing at different Y and a player on the upper one (assert they stay on it). Depends on _CorridorNav's exact segment-search internals, which I've seen only in summary — confirm the nearest-segment search is the right place to inject the Y tiebreak.
    G3 — Ramp waypoint insertion vs. existing crossing waypoints. level_maker must insert ramp-top waypoints without disturbing crossing waypoints already in path_xz, and without creating a ramp longer than the corridor (short corridors: clamp ramp run to ≤ ⅓ of segment length). Needs a scale test on the real 20-node Principia floorplan (which currently produces ~5 crossings) to confirm ramps + crossings coexist.
    G4 — Guide-line origin on the current corridor. Guide-lines originate from the player's current/nearest node (§8.2). On door-exit the player is mid-corridor, not at a node; confirm select_targets' "current" argument gets the right node (the room just left, or nearest node) so lines point sensibly from frame one. Likely already correct via state.current_room_id; verify.
    G5 — Not seen, assumed: I have not seen render_mode_a()'s FBO/bloom ordering in full; I've assumed guide-lines drawn after the wire and before bloom composite is correct (so lines glow subtly too). If guide-lines should be crisp (no bloom), draw them after the bloom composite instead — a one-line ordering choice for DeepSeek to confirm by rendering and showing Nir a PNG.

What this design does not touch

Room rendering, room nav, the TARDIS architecture, the Corridor/Crossing/FloorRoom contracts (Option A), Parent 8's scale-free layout, Parent 11's Mode A wire+bloom, and the door→room entry mechanic. All four fixes are additive/corrective within existing modules.

This is the frozen design. It is deliberately small because the correct answer here was "the feature is 80% built and mis-wired," not "build a feature." DeepSeek should implement Fix 1 → Fix 2 → Fix 3 → Fix 4 in that order (each independently visible), and render + show Nir a PNG after Fix 2 and Fix 4 — because per the standing lesson, "tests pass" is not success for anything visual.
