COMPLETION REPORT — hostages — June 15, 2026

FILES ADDED/CHANGED: hostages.py (new), hostages_demo.py (new). app.py and corridor_builder.py UNCHANGED (I only request wiring lines below).

RUN-VERIFIED? N — I have no execution environment here. The code is written strictly against the pasted file signatures and the canonical loop. Nir runs python hostages_demo.py from repo root to verify acceptance.

FINAL LOCKED SIGNATURES:

    Hostage(world_pos, facing, color_id, variant=0, size=HOSTAGE_SIZE)
    Hostage.update(dt)
    Hostage.draw(camera_right, camera_up, texcache) — wrapper; also draw_opaque(...) / draw_emissive(...)
    Hostage.position (property), Hostage.base_pos
    build_hostages(corridor_geom, color_id=None, size=HOSTAGE_SIZE, spacing=COUPLE_SPACING) -> [Hostage, Hostage]
    near_hostages(hostage_list, ship_pos, radius=NEAR_RADIUS) -> bool

HOW I MIRRORED THE ROBOT CLASS (verbatim):

    Geometry assembly: Robot builds _build_hull() from _box/_prism/_wedge_snout returning triangle lists (a,b,c), then self._hull_cols = [_shade(t, self._hull_base) for t in self._hull_tris] and self._hull_verts = np.array([v for t in self._hull_tris for v in t]). I mirror this in _build_body(variant) with _box/_taper_box/_octa_sphere, baking colors via _shade and a flattened self._verts.
    Shading: _shade(tri, base_rgb) — I copied it (normal from cross product, _AMBIENT + _DIFFUSE*|n.L|, spec term, clamp).
    Draw: Robot has draw() = draw_opaque() + draw_emissive(); opaque does glPushMatrix; glTranslatef(cx,cy,cz); glRotatef(yaw,0,1,0); glScalef(size...); _draw_hull is glBegin(GL_TRIANGLES) with one glColor3f per pre-shaded triangle. Emissive uses glBlendFunc(GL_SRC_ALPHA, GL_ONE), glDepthMask(GL_FALSE), draws additive glow (its _disk fan), then restores glDepthMask(GL_TRUE), glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA), glDisable(GL_BLEND). I mirror all of this exactly.
    Animate: Robot update: self._t += dt; self._bob_y = BOB_AMPLITUDE*math.sin(self._t*BOB_SPEED). Mine adds a sway sinusoid; no player tracking (they wait).
    Position: Robot's _world_center() = base_pos + [0, _bob_y, 0] and position property. Copied.

WHAT I CONSUMED + HOW:

    CorridorGeometry.hostage_positions() -> list[(x,y,z)] — three floor anchors at (-3.5,0,3.5) (from _build_cavern_anchors). I derive a tight couple from them: midpoint = anchors[1], right = unit(anchors[2]-anchors[0]), two people at midpoint +/- right*(spacing/2). I do NOT use three figures.
    CorridorGeometry.entrance_pose() -> ((x,y,z),(nx,ny,nz)) — mouth position; couple faces from midpoint toward the mouth (back up the corridor toward the ship). yaw = atan2(dx, -dz), the same convention as _build_stations and hub.spawn_pose().
    render.ship_right(q)/ship_up(q) -> cr,cu passed to draw (used by the camera-facing aura disk, like Robot's _disk).
    palette opaque constants: HOSTAGE_BLUE (the cavern tint I deliberately AVOID matching), and I prefer palette.HOSTAGE_GLOW if present, else a local warm decoration default. No meaning-color APIs (eye/tint/blend_rgb) used.
    Canonical loop slot order from app.py (flush in slot 8, robots in slot 9). The demo reproduces it verbatim.

THE EXACT WIRING LINES THE PARENT MUST ADD (and WHERE) — in corridor_builder.py:

    Import at top (with the other imports):

    from hostages import build_hostages

    In CorridorGeometry.__init__, right after self._build_cavern_anchors():

    self._hostages = build_hostages(self)

    In CorridorGeometry.update, inside the method (alongside the robot update loop):

    for h in self._hostages:
        h.update(dt)

    In CorridorGeometry.draw_robots (the slot AFTER flush_walls), append after the robot loop:

    for h in self._hostages:
        h.draw(camera_right, camera_up, texcache)

    No change to
    app.py is needed -- hub.draw_robots already delegates to corridor.draw_robots, and hub.update already delegates to corridor.update.

DEVIATIONS / REQUESTS TO PARENT:

    Palette color request: palette.py has HOSTAGE_BLUE (cavern tint) but no warm figure-glow key. I REQUEST an official opaque key:

    HOSTAGE_GLOW: tuple[float, float, float] = (1.00, 0.78, 0.45)  # warm prize-figure glow (DECORATION, not meaning)

    build_hostages already prefers palette.HOSTAGE_GLOW if it exists, else falls back to the in-module warm default -- so it works today and upgrades cleanly. The figures are warm so they POP against the blue cavern (blue figures would vanish into HOSTAGE_BLUE walls).
    Placement decision I made: the three (-3.5,0,3.5) anchors are too far apart and skip center for "standing together," so I compute a tight couple (COUPLE_SPACING = 2.2) centered on the middle anchor, using the lateral axis from the outer anchors. Pure public-interface geometry.
    update has no dt in draw_robots -- correct: the parent wires h.update(dt) into corridor.update(dt, ship_position) (which already runs robot updates), and h.draw(...) into draw_robots. Two separate hooks, both spelled out above.

DEEPSEEK TODOs (mechanical tuning only -- current values):

    HOSTAGE_SIZE = 1.6 -- overall figure scale.
    COUPLE_SPACING = 2.2 -- center-to-center distance between the two people.
    BOB_AMPLITUDE = 0.10, BOB_SPEED = 1.1 -- breathing bob.
    SWAY_AMPLITUDE = 0.045, SWAY_SPEED = 0.7 -- weight-shift sway.
    NEAR_RADIUS = 14.0 -- rescue/near radius for near_hostages.
    GLOW_AURA_DIAM = 5.5, GLOW_AURA_ALPHA = 0.30, GLOW_AURA_SEG = 22 -- ground-glow aura.
    GLOW_EDGE_ALPHA = 0.55 -- warm additive body-halo strength (the POP).
    _GLOW_WARM = (1.0, 0.78, 0.45) -- fallback glow color (until palette.HOSTAGE_GLOW).
    _VARIANTS -- the two people's skin/cloth tints + height (1.00 vs 0.92). Variant difference between the couple.

One flag for the parent (file-vs-brief discrepancy, per "the file wins"): the brief proposed hostages might draw entirely after the flush as one call. The real CorridorGeometry.draw_robots calls r.draw(cr,cu,tc) (the full wrapper) after the flush -- so my Hostage.draw is the same full wrapper, drawing the opaque body (depth-write on) then the additive glow (depth-write off) in that single post-flush slot. This matches how the Robot's own hull+scanner draw together in that slot today, and respects the cardinal flush trap (I never call flush_walls).
