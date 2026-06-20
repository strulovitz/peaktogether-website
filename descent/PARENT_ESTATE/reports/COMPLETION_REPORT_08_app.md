Completion Report — app (minimal integration) — 2026-06-14

Deliverable: app.py — the minimal integration entry point. python app.py from repo root loads levels/intro.txt (3 distinct corridors → 3 doors), builds the atrium hub, spawns the ship facing door 0, and flies. ESC/window-close quits.

The cardinal trap is handled: render.flush_walls(ship.pos) is called exactly once, immediately after hub.draw_world(...) and before draw_robots/draw_labels. Both hub.draw_world and the corridors it delegates to are queue-only (verified in the pasted hub_builder.py), so a missing or duplicated flush would silently drop every wall. It is present, once, in the canonical slot.

Prime Law upheld: app.py constructs no Palette and no ColorLedger, imports neither for use, and passes only (cr, cu, texcache) to all three hub draw calls — exactly matching the verified hub_builder signatures. Color/meaning never enters this module.

Copied verbatim from the working hub_demo.py (so it can't introduce a black-window regression):

    pygame.init() → set_mode(WIN_SIZE, pygame.OPENGL | pygame.DOUBLEBUF) → render.init_gl(WIN_SIZE) → render.TexCache()
    WIN_SIZE = (1280, 800)
    Fog: render.set_fog(start=40, end=140, color=palette.CLEAR_COLOR) — these equal render's own DARKNESS_START/END defaults; not invented.
    dt = clock.tick(60) / 1000.0; pygame.QUIT + K_ESCAPE to quit; glClearColor(*palette.CLEAR_COLOR, 1.0) + clear.

Two deliberate deviations, each justified by a pasted file (which is law):

    Level loading via level_parser.load_level("levels/intro.txt") instead of hub_demo's discover_corridors + duplicate shim. The brief mandates the level path, and level_parser refuses clones — so the demo's duplication trick is exactly what we must not do. build_hub receives the Level directly (it's iterable and yields CorridorData).
    Aiming the ship via render.quat_look_along(fwd) (PATH 1). hub_demo.py carries a stale comment, "(No quat_look_along exists.)", and seats the ship at identity orientation — which would spawn the player staring at a random patch of shell. The pasted render.py does define quat_look_along (NaN-safe, with the guarantee ship_forward(quat_look_along(d)) == normalize(d)). File beats stale comment, so we aim at door 0's outward normal. The ship now spawns facing a doorway, satisfying the acceptance criterion.

    Bad/missing manifest: load_level raises ParseError (or OSError); _load_level_or_die prints one readable line to stderr and exits code 2. A content problem will never masquerade as a GL/black-screen bug.
    Zero-corridor level: door_poses() would be empty; _make_ship leaves the ship at render.Ship's default orientation. (Not the case for intro.txt, which has 3 doors, but the guard is there.)
    Spawn position uses hub.spawn_pose()[0], not a hardcoded (0,0,0), so it survives any future atrium_center change.
    macOS: a one-line comment beside set_mode points at render.py's documented black-window/legacy-GL note, in case Nir is on a Mac.

    DeepSeek (visual tuning): screenshots from this flight exercise the hub_builder TODOs — ATRIUM_RADIUS, ATRIUM_FACETS, DOOR_FRAME_DEPTH, DOOR_OPENING_SCALE (acceptance criteria are in hub_builder.py). With N=3 the three door rings should read as clearly separated on the shell.
    Debug overlay: SHOW_HUD = False. Flip to True for an fps + ship-pos line via render's existing 2D path — zero gameplay, no new infrastructure. (If begin_2d/draw_text_mathtext_2d/end_2d ever differ from what render.py exposed, that path is the only thing to re-check; the default path doesn't touch it.)
    Out of scope (by brief): no reading system, no combat/rules, no level select. Single hardcoded manifest, one ship, fly-through proof only.

Ready to run: python app.py from the repo root. Expected: a dark fogged atrium with 3 grey rock doorways radiating corridors, ship spawned at center facing the first door, full WASD/RF/QE/arrow flight, ESC to quit.

Thank you for the careful, complete handoff — having every consumed file in hand is exactly why this is one pass and not three. 🙂