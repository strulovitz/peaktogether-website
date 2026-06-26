🗝️ QUAKE (Game 3) — PARENT 3 → PARENT 4 HANDOFF: THE RUNTIME ENGINE

Captured June 26, 2026, at Nir's request, VERBATIM / word-for-word, AS-IS. This is Parent 3 of Quake — Claude Opus 4.8, at "normal" reasoning effort — delivering its final handoff to Parent 4. Nothing below is edited.

--- BEGIN VERBATIM ---

You are Parent 4. You received this alongside the Commentaries, the Old Testament, and the New Testament. Read those three first; this handoff orients you and sets your mission.

The entire content pipeline is built (Legs 1–3, 186/186 tests green). What does not exist yet is the thing all of it feeds: the runtime graphics engine — the game you actually walk around in. That is your mission, and it is the hardest remaining work.
§1 — THE WORKING MODEL (how this whole project operates)

    You (architect) write documents — design, frozen contracts, child briefs. You never write running code.
    Fresh "child" chats implement one module each to your frozen contract + tests, then are discarded.
    DeepSeek integrates, runs tests, pushes to git.
    Nir decides everything and carries text between chats. Nir knows no code and no math. Never design anything requiring Nir to understand code, math, or a proof. Nir's runtime role is: run the game, press keys, look, report what he sees.

§2 — THE IRON RULE (the #1 thing this system exists to enforce)

Never re-decide a frozen contract. Before designing anything that touches an existing format, signature, or protocol, request that exact section verbatim (via Nir → DeepSeek) and design against it. Do not assume or reinvent it. Silent contradiction of a pinned format is the failure mode that kills this project. When in doubt, pull the verbatim text.

Two corollaries from honesty: never invent facts (mark gaps as gaps); refuse to assert external-library API names (moderngl/pyglet/GLSL specifics) from memory — define your own module conventions fully and let the integration loop confirm the externals.
§3 — WHAT'S BUILT (the frozen formats your engine READS)

The engine loads only baked JSON + PNG. It never sees LaTeX, an LLM, Asymptote, Tectonic, or the book. Three legs produce your inputs:

Leg 1 — MAP (built, 94 tests):

    concept_graph.json → ConceptGraph (nodes[] with id/name/kind/importance/pages/summary/tags; edges[] with id/source/target/kind/weight/label).
    floorplan.json → Floorplan (rooms[] with room_id/map_xy/importance/map_radius_m/map_color_role; corridors[] with height_level/cruise_z/path_xy; crossings[] with over/under z). Coordinates are map-plane XZ; Y is up.

Leg 2 — WALLS (built, 51 tests):

    manifest.json → Manifest (assets dict keyed by asset_id; each AssetEntry has kind ∈ {figure_off, figure_on, text_off, text_on, ceiling_neutral}, wall_path, master_path, px_w, px_h, content_bbox, dpi). Two DPI tiers: wall_path (in-world) and master_path (Read Mode).
    Baked off/on PNGs (transparent, trimmed, magenta-keyed). Asset-id grammar is figure_id-keyed: prop_1.f1.off, prop_1.f1.on.3, prop_1.s3.txt.off, prop_1.s3.txt.on.

Leg 3 — ROOMS (built, 41 tests — my deliverable):

    room_runtime/room_<id>.json → RoomRuntime:
        dimensions_m: Vec3 (W, H, D) — TARDIS, content-driven.
        panel_pairs: list[PanelPairRT] — each has the four asset_ids (drawing_off_asset/drawing_on_asset/text_off_asset/text_on_asset) + drawing_placement & text_placement (PanelPlacementRT: wall∈{N,E,S,W}, slot_index, wall_slot, center_xyz, width_m, height_m, yaw_rad — panel normal points inward).
        doors: list[DoorRT] (len == node degree) — each: edge_id, neighbor_id, bearing_rad, wall, center_xyz, width_m, height_m, normal_yaw_rad (wall inward normal), spawn_xyz, spawn_heading_rad (== bearing_rad + π, faces room center, matches corridor approach → zero heading-snap on entry).
        final_pair_id, hidden_door_wall_slot (the final pair's drawing wall_slot — a shallow alcove, NOT a transit door), enemy: EnemyRT (enemy_id, spawn_xyz, health=5), ceiling_equations: list[CeilingEqRT] (eq_id, asset_id, pos_xyz, size_m).

Two critical spatial facts your engine MUST honor:

    Room-local axes are parallel to map axes (global compass, NO rotation). North means the same in the map, every corridor, and every room. Door direction is literal: a corridor at map-bearing θ has its door in room-local direction θ. Walls: N at z=+D/2 (inward normal −Z), S at z=−D/2 (+Z), E at x=+W/2 (−X), W at x=−W/2 (+X), floor y=0.
    Corridors leave each node at their true bearings, so Mode A wireframe and Mode B door directions agree by construction — you never reconcile them.

§4 — LOCKED DECISIONS (you CANNOT re-decide these)

Tech stack: all-Python, Windows-first. moderngl (OpenGL 3.3+ core — you write GLSL, you issue draw calls) + pyglet 2.1.x (window, input, audio; no external compiled deps → clean PyInstaller freeze) + NumPy + Pillow + pydantic v2 (extra="forbid", schema_version "1.0"). PyInstaller one-folder Windows build. moderngl-window may bootstrap M0 only, then you drop it and own your window/input behind a semantic layer. NEVER a hide-the-pipeline engine (no Unity/Unreal/Godot/Ursina/Panda3D).

Two render modes (OT §3), switched at the door, never drawn in the same frame:

    Mode A (corridor): wireframe only, lines + node rings, depth-tested, NO alpha blend, depthFunc LEQUAL, distance-dimming white→dark-grey (never pure black — far structure stays a faint presence). Crossings render as true 3D over/under. ~3 Half-Life-style procedural floor guide-lines with arrowheads (navigation + vertigo mitigation). Subtle screen-space bloom for the neon glow (NOT real blending). Pure transit: no enemies, no panels, no shooting targets.
    Mode B (room): solid, textured, first-person. Walls built as quads around door holes at bearing-placed DoorRT positions; recessed doorways via normal_yaw_rad; baked PNG panels on walls (off=grey / on=colored); hidden-door alcove at hidden_door_wall_slot; ceiling equations hidden until demon dies, then fade blood-red via a shader tint uniform (one neutral texture, runtime-tinted).
    Switch: teleport-snap at the door (NO blend — a blended A↔B transition is nauseating). Entering hides the graph + loads the room; exiting unloads + returns.

Co-op (OT §10) — the make-or-break for comfort:

    MOVER owns translation + body heading. Only the Mover changes world yaw. This is the central anti-nausea decision.
    SHOOTER owns a free-aim reticle in a cone in front of the body. The Shooter NEVER rotates the camera.
    Camera follows Mover heading with a critically-damped spring (no overshoot). Pitch clamp + smoothing, no head-bob by default, narrow-FOV default (~70–75°), motion-vignette option, slow default walk.
    God-mode: cannot die, infinite ammo, exactly one enemy per room, no level boss.

Verbs: walk, look, shoot, read. No quizzes, timers, lives, scoring, fail states, pedagogy. Reward is aesthetic.

Read Mode target rule (LOCKED, Second Canon §5.3 commentary): the panel the reticle ray hits (hit distance ≤ READ_MAX_DIST = 6.0 m); else the panel whose center is within READ_CONE_HALF_ANGLE = 35° of view-forward and nearest (≤ 6.0 m); else no-op. Read Mode shows the master-DPI PNG, world paused, and does NOT flip panel state — shooting is the only thing that flips off→on.

Door logic (LOCKED, OT §3.2):

final pair OFF        → shot flips it ON
final pair ON, closed → shot OPENS the hidden door, spawns demon
door OPEN             → shot has no extra door effect (hits enemy/panels normally)

§5 — YOUR MISSION: FREEZE + CHILD-BRIEF THE RUNTIME ENGINE

Map to OT §13 milestones. The natural grouping (refine it if your validation justifies it — but justify, don't guess):

Group A — Pixels + Wireframe (M0–M1):

    gfx_context.py — make_window(width, height, title) -> (window, gl_context); OT §11.4 GPU check (OpenGL ≥3.3, FBO, max texture size; plain error window + exit on failure).
    shaders.py — wire_program(ctx), solid_program(ctx), blit_program(ctx), ceiling_tint_uniform(prog, red). You write the GLSL.
    render_wire.py — draw_graph(view, floorplan, state). No-blend depth, distance-dim, camera-facing line-quads + depth bias (the fix for thin-line dropout at crossings), bloom post-pass.
    camera.py — Camera.update(heading_rad, pitch_rad, pos, dt) -> ViewMatrix. Damped, decoupled, pitch-clamped.
    input_actions.py — poll(window, bindings) -> Actions. Device-agnostic semantic layer (MOVE_X/Y, HEADING [Mover], AIM_X/Y [Shooter], FIRE, READ, INTERACT, PAUSE); two-player split; raw device events never leak past this module.
    guidelines.py — select_targets(floorplan, current, cleared, cfg) -> list[NodeId] (≤3, the OT §8.2 scoring + hysteresis: recompute only on junction-crossing or room-clear) + draw_guidelines(view, floorplan, targets).
    app.py — main() -> int. Thin per-frame loop (OT §12.4 wiring order); owns no logic.

Group B — Rooms + Read Mode (M6):

    assets.py — load_pack(dir) -> Pack. Loads baked JSON+PNG, asserts schema_version on every file.
    render_room.py — draw_room(view, room, pack, state). Walls-with-holes at DoorRT positions, recessed doorways via normal_yaw_rad, baked panel textures (sample off or on per panel state), hidden-door alcove, ceiling tint post-kill.
    nav_collision.py — build_corridor_nav(fp) -> NavQuery, build_room_nav(room) -> NavQuery, ray→nearest_panel, and door_at(point) -> edge_id | None for transition triggering. Door intervals passable; rest solid; corridor floor + soft side boundaries + ramps.
    readmode.py — draw_read(asset_master_path, zoom, pan). (Target-selection raycast/cone helper is a gameplay/nav_collision detail; the §4 locked rule governs it.)

Group C — Gameplay loop (M7):

    gameplay.py — step(state, actions, pack, nav, dt) -> list[Event]. Shoot→flip panel (persist), final-wall→open→spawn demon→kill→ceiling bleeds red→room cleared; god-mode; mode-switch events (ModeSwitch(to, room_id, via_edge_id)); spawn at doors[edge_id].spawn_xyz/spawn_heading_rad on room entry.
    state.py — new_state(pack, profile_id), load(path, pack), save(state, path) (atomic: temp→flush→rename). Tracks per-room panel_pairs_on, hidden_door_open, enemy_defeated, room_cleared, level_complete.

The frozen runtime signatures already exist in Second Canon §5.1 (contracts/Actions/Events) and §5.3 (runtime signatures) + the §5.4 per-frame wiring. Pull those verbatim — they are your contracts, not suggestions.
§6 — YOUR VERBATIM PULL LIST (request these FIRST, via Nir → DeepSeek)

Per the iron rule, get these exact before designing. Suggested order:

    Second Canon §5.1 — runtime contracts: Actions, the full Event union (incl. ModeSwitch), ViewMatrix, NavQuery, Pack, GameState. Your core types.
    Second Canon §5.3 — runtime module signatures with the Read-Mode inline commentary (the READ_MAX_DIST/READ_CONE_HALF_ANGLE lock). I have a transcription, but pull it fresh for the exact GameState/Actions field lists.
    Second Canon §5.4 — per-frame wiring order (also OT §12.4). Your app.py skeleton.
    Second Canon §4.4 — floorplan.json full schema (Floorplan/rooms/corridors/crossings field-exact). Mode A reads this directly; the OT §9.4 sketch is not field-exact.
    Second Canon §4.7 — savegame schema. Your state.py contract.
    Second Canon §4.2 — concept_graph (node ring labels/importance for Mode A styling).
    Apocrypha §7 — downstream deltas (render_room walls-with-holes, nav_collision door triggers, gameplay spawns). I've summarized them in §3/§4/§5; pull verbatim before freezing render_room.
    RoomRuntime/DoorRT/PanelPlacementRT/PanelPairRT/CeilingEqRT/EnemyRT — already in contracts.py (Apocrypha §3 + Second Canon §4.5 commentary). Pull if you want the field-exact pydantic; I've given the fields in §3 above.
    Manifest/AssetEntry §4.6 — the texture index you sample. Pull for the exact content_bbox pixel convention (top-left origin, half-open — Second Canon §2.3).

You likely do not need the build-side legs (Recipe, Asymptote, baker internals) — the engine never touches them. Pull only if a boundary surprises you.
§7 — KEY RISK FLAGS (designed-for, not hoped-for)

    Headless CI for a GPU game (R14): headless-first design. Pure logic (camera math, guideline selection, gameplay state transitions, nav queries, ray-panel intersection) is fully unit-testable with fixtures and must be. GPU/display tests skip gracefully without a context (pyglet headless helps). Structure every module so the math is a pure function and the GL call is a thin shell.
    Thin-line dropout at dense crossings (R9): camera-facing line-quads (consistent width) + small depth bias; depth-only prepass available as a config toggle for dense graphs.
    Wireframe vertigo (R8): never-black horizon (distance-dim to dark grey, not black) + the guide-line felt floor (a committed ground plane in a mode with no real floor).
    Co-op true-3D nausea (R7): the structural fixes are locked (single-owner heading, decoupled damped camera). Honor them exactly — do not let the Shooter touch yaw.
    Wall legibility at distance/angle (R12): Read Mode is the escape hatch. Build it in M6 (not deferred). The locked target rule is in §4.
    Mode switch: teleport-snap, never blend. The door is an occlusion boundary — Mode A and Mode B never draw in the same frame (don't pay for the world you can't see).
    Walls-with-holes: render_room builds each wall as quads around its door hole(s) at the bearing-placed DoorRT.center_xyz; recessed doorway via normal_yaw_rad; the hidden-door alcove is separate (a shallow recess at hidden_door_wall_slot, not a transit door).
    Spatial invariants: room-local axes map-parallel (global compass); floorplan is XZ-plane, Y up; spawn heading = bearing+π (zero snap). The engine must not rotate room-local space.
    Audio (OT §11.3, [GAP]): simple SFX via pyglet built-in (gunshot, panel-flip, demon, glyph-spray). Music/atmosphere unspecified — flag it; due ~M8, not blocking your engine freeze.

§8 — YOUR THREE-STEP DISCIPLINE (same as Parent 2 and I followed)

    Pull the verbatim contracts (§6) before designing. Confirm or expand the list once you've read OT + NT + Commentaries holistically — the whole-body view may surface more (it did for me).
    Validate holistically against those verbatim contracts. Where the algorithm/spec is under-specified for a child to build deterministically, pin the missing constant/rule concretely (as I pinned the angular-nudge tolerance and grow-factor) — and flag genuine contract conflicts to Nir rather than silently resolving them.
    Produce frozen child briefs: exact signatures, pure-function contracts wherever possible (math separated from GL so it tests headless), golden fixtures with an anti-regression clause, a dependency-sorted build order, a test plan, and acceptance gates mapped to OT milestones (M0, M1, M6, M7). Front-load M0 ("our pixels" — one shaded triangle + one wireframe line, depth on, blend off) so the GPU path is proven ours before anything else.

§9 — WHAT "DONE" LOOKS LIKE

The engine is done when, from baked content alone:

    M0: a moderngl window draws one shaded triangle + one wireframe line (depth on, blend off). The GPU path is ours.
    M1: you walk a hardcoded wireframe graph (Mode A), distance-dimming, comfortable (Mover heading only).
    M6: enter a real RoomRuntime room through a bearing-correct door (zero heading-snap), see baked panels on walls, doors at true bearings, press R to Read a pin-sharp master-DPI panel.
    M7: the full loop — shoot a panel off→on (persisted atomically), shoot the lit final wall → it opens → the demon emerges → kill it (god-mode) → the ceiling bleeds blood-red → room cleared. Co-op: Mover walks, Shooter aims, the camera never lurches from aiming.
    Across all: pure logic fully unit-tested green; GPU tests skip gracefully headless; the golden fixture pack (OT §12.5 — 3 rooms, 1 crossing, 1 two-step room, 1 demon, 1 ceiling equation) plays end-to-end in CI's smoke launch.

M8 (one full real Principia level + audio) and M9 (second pack) follow, but M0–M7 is the engine and is your charge.

You have a fully built, fully tested content pipeline beneath you and a locked doctrine around you. The hard part left is real-time 3D done comfortably for two people sharing one body — designed structurally, not hopefully. Pull the verbatim runtime contracts, honor the compass and the decoupled camera, keep the math pure so it tests headless, and front-load M0.

Pass it on when you're done. 🗝️

--- END VERBATIM ---
