================================================================================
DESCENT QED — CHILD BRIEF #P1: DEFEAT PLAQUE (use the already-baked PNG)
Module concern: when a robot is defeated, show its ALREADY-BAKED
"mathematician"-layer PNG as an in-world billboard sign in the corridor.
You build ONE concern. Do not creep. Do not touch unrelated systems.
================================================================================

## 0. WHO YOU ARE, WHO ELSE EXISTS
You are a fresh Claude Opus 4.8 child with NO memory of prior chats. You write
ONE module's worth of code, fully, at full Opus depth. Do NOT defer judgment.
- NIR — the human, your COURIER and TESTER. Not a programmer. He runs the game
  and reports what he SEES on screen. Be warm, exact, and give him precise
  things to look at.
- DEEPSEEK V4 Pro — agentic builder on Nir's machine, full repo + internet.
  Commits your code, runs probes. Reliable for MECHANICAL tasks, but NOT wise
  about INTENT — he can "fix the headache and ruin the liver." Use him to FETCH
  FACTS / RUN PROBES, never to decide design. If he contradicts this brief or
  Nir, this brief and Nir win.
- THE PARENT (architect) wrote this brief and owns architecture, with no memory
  of your chat. If you need something another module doesn't expose, REQUEST it
  in your Completion Report — do NOT reach in and edit other modules.

## 1. FRESH-CHAT GATE — DO THIS FIRST, BEFORE ANY CODE
Do NOT hallucinate APIs. Your FIRST action: ask Nir (relayed to DeepSeek) to
paste you the COMPLETE, VERBATIM, CURRENT contents of:
  (1) corridor_builder.py  — the WHOLE file. You edit only the _draw_plaques
      method (~line 338) and may add small private helpers in this same file.
      You also need to see: how _station_poses are built, what the corridor
      tube RADIUS is (seg_bounds / segment radius), LABEL_LIFT, PLAQUE_SCALE,
      and how draw_world/draw_robots/draw_labels relate so you draw in the
      right pass.
  (2) render.py — ONLY: draw_billboard(...) (signature + body), and any nearby
      helper for drawing a flat colored quad / lines in 3D world space (you
      need this for the WHITE FRAME). If none exists, you will REQUEST one or
      draw the frame with immediate-mode GL_QUADS/GL_LINE_LOOP yourself
      (legacy fixed-function only — see §5.3). Also paste how draw_billboard
      orients the quad (camera_right/up) so your frame matches the PNG's plane.
  (3) robots.py — ONLY: confirm Robot exposes .number, .understanding_dir,
      .is_defeated(). (Parent believes all three exist.)
  (4) understanding.py — ONLY: the _surface_to_texture(...) method and the
      _load_panel_ladder(...) method, so you reuse the EXACT same PNG-path
      convention and surface->GL-texture conversion. DO NOT import understanding
      (it has its own GL/texture lifecycle); you will write your OWN tiny loader
      that follows the SAME convention.
PASTED FILES ARE LAW. If a pasted file disagrees with anything below, the FILE
wins, and you tell Nir you spotted it.

## 2. THE GAME — THIS IS LAW (so you never drift)
DESCENT QED: a no-fail, WIN-ONLY 6-DOF flying game. A couple shares one ship,
descends rock mine corridors to RESCUE HOSTAGES (the prize). ROBOTS block
corridors; each is destroyed by firing the correct mathematician-missile (the
player RECOGNIZES the robot's hologram FACE and picks the matching mathematician
in the weapon panel). Wrong shot = harmless 6s fizzle, no penalty. No death, no
timer, no punishment.

THE PRIME LAW — MATHEMATICS-BLINDNESS: the engine NEVER interprets what math
MEANS; it only matches opaque IDs; color flows ONLY through palette.py via
opaque keys. YOUR module just displays an OPAQUE IMAGE FILE at a location. It
must contain ZERO math-meaning logic and ZERO color-meaning logic. (A thin
white frame is a neutral UI border, not "meaning" — that's fine.)

## 3. THE EXACT PROBLEM (confirmed by Nir, June 17 2026)
When a robot is defeated, a PLAQUE should appear at its spot in the corridor
showing the SAME "explain like I'm a mathematician" content the player sees in
Understanding Mode. That content is ALREADY a BAKED PNG (Parent #5's pipeline).
The CURRENT code does NOT use the PNG — it tries to LIVE-RENDER the text via
texcache.get_mathtext(...), which comes out as a SOLID WHITE RECTANGLE (a known
mathtext bug). 

THE FIX (small, and exactly what Nir wants):
  - STOP live-rendering text.
  - LOAD the already-baked PNG for that robot's "mathematician" layer.
  - Billboard THAT PNG at the defeated robot's location.
  - Scale it to ~90% of the corridor CROSS-SECTION (fills most of the tube,
    almost touching the walls but NOT touching them).
  - Surround it with a THIN WHITE FRAME RECTANGLE so it reads as a solid SIGN /
    OBJECT in the corridor, not text floating in vacuum.

## 4. THE FACTS YOU LEAN ON (verify against the pastes)
Baked PNG path convention (from understanding.py): 
    {understanding_dir}/robot{number}_{layer}.png
    -> for the plaque, layer = "mathematician"
    -> example: baked/basel/robot3_mathematician.png
A robot exposes (confirm in robots.py paste):
    robot.understanding_dir  (str; may be "" if missing)
    robot.number             (int)
    robot.is_defeated()      (bool)
Surface->GL texture (reuse this EXACT pattern; do NOT import understanding —
copy the pattern into your own small loader):
    surf = pygame.image.load(path).convert_alpha()
    ... glGenTextures / glTexImage2D(GL_RGBA, w, h, ... GL_UNSIGNED_BYTE) ...
    returns (tid, w, h)
    Note: pygame.image.tostring(surf, "RGBA", True) flips vertically — match
    understanding.py's convention EXACTLY so the image isn't upside-down.
Billboard draw (already used by the current plaque):
    render.draw_billboard(tex, center, camera_right, camera_up, scale, alpha)
    tex is a (tid, w, h) tuple; center is a world point; camera_right/up are the
    cr/cu the method is already passed.
Current method to REPLACE (corridor_builder.py ~line 338), for reference:
    def _draw_plaques(self, cr, cu, texcache):
        ... loops defeated robots ...
        text = explain.get("mathematician","")  # <- live text, the bug
        tex = texcache.get_mathtext(text, ...)   # <- WHITE RECTANGLE bug
        center = pose + [0, LABEL_LIFT, 0]
        render.draw_billboard(tex, center, cr, cu, scale=PLAQUE_SCALE, alpha=0.9)
Constants present: LABEL_LIFT = 2.2, PLAQUE_SCALE = 0.7 (you will likely change
how scale is computed — see §5.2).

## 5. WHAT TO BUILD — DESIGN

### 5.1 Load the baked PNG (once, cache it)
Build a tiny per-robot texture loader (private helper in corridor_builder.py, or
a small dict cache on the geometry object). For each DEFEATED robot:
  - Compute path = os.path.join(robot.understanding_dir,
                                f"robot{robot.number}_mathematician.png")
  - If understanding_dir is "" or file missing: FALL BACK GRACEFULLY to the
    current behavior is NOT desired (it's the white bug). Instead, skip drawing
    a plaque for that robot and print ONE loud line to stderr:
      "[plaque] no baked PNG for robot {n}: {path}"
    (So a missing bake is visible, not a white box. Maxwell/Basel both have
    baked PNGs, so in practice this fallback should never fire — but be honest.)
  - Load surf, convert to (tid, w, h) using the SAME pattern as
    understanding._surface_to_texture (copy it; do not import). CACHE the tuple
    keyed by robot.number so you don't re-upload a texture every frame (texture
    leak otherwise). Build the GL texture lazily on first draw.
  - The PNG's native (w, h) gives you its ASPECT RATIO — you need it for §5.2.

### 5.2 Size it to ~90% of the corridor cross-section
The plaque must fill ~90% of the tube's cross-section WITHOUT touching walls.
  - Get the corridor TUBE RADIUS at the robot's segment from seg_bounds
    ("radius") — this is the SAME public data the collision module used. (Brief
    #C1 established seg_bounds = list of {"start","end","radius"} per segment;
    confirm the exact key names in the paste.)
  - Target the plaque's HALF-HEIGHT (or half the larger dimension) so the image
    spans ~0.9 * tube_radius from center (i.e. ~90% of the radius to the wall).
    Preserve the PNG's aspect ratio (w/h) so it isn't stretched. If the image is
    wider than tall, fit by WIDTH to 0.9*tube_radius*2; if taller, fit by HEIGHT.
    The point: large, centered in the tube, almost touching walls, never past.
  - draw_billboard takes a single `scale`. Determine what `scale` means in
    world units from the paste (does scale=1 mean "1 world unit tall"? or unit
    quad scaled by the texture's pixel size?). COMPUTE the scale that achieves
    the 0.9 cross-section fit. State your derivation in the Completion Report so
    DeepSeek/Nir can tune the 0.9 factor (Nir said "like 90%").
  - IMPORTANT: because draw_billboard is a CAMERA-FACING billboard, the plaque
    will always face the player. That is fine and desired (a readable sign).
    Center it on the TUBE AXIS at the robot's location (use the station pose;
    keep LABEL_LIFT or set the lift so the image is centered in the tube cross-
    section, not shoved to the top — confirm what looks centered). Tube-axis
    centering matters: Brief #C1 learned a robot's DRAWN position sits LOW in
    the tube (center - up*radius*0.45); for the PLAQUE you want it CENTERED in
    the cross-section, so lift accordingly.

### 5.3 The thin white frame rectangle
Draw a thin white rectangle BORDER around the plaque image so it reads as a
solid sign, not floating text. Two acceptable approaches — pick the cleaner one
given the paste:
  (a) If render.py has a helper to draw a flat colored quad / line-loop in 3D
      facing the camera, REQUEST/USE it: draw a slightly-larger white quad
      BEHIND the image (a 2–4% border margin all around), or a GL_LINE_LOOP
      outline in front. 
  (b) Otherwise draw it yourself with legacy immediate-mode GL right where the
      billboard is drawn: build the same camera-facing plane (using the same
      camera_right/up vectors and center), and render either:
        - a white GL_QUADS slightly larger than the image (image drawn on top),
          or
        - a GL_LINE_LOOP outline (set a modest glLineWidth, white color).
      Keep it THIN (Nir said "thin frame"). No textures on the frame; flat
      white. Disable lighting/texture for the frame, re-enable for the image, or
      draw frame first then image on top. Match the billboard's orientation
      EXACTLY so the frame and image are coplanar and aligned.
LEGACY GL ONLY (no shaders). Restore any GL state you change (texture enable,
color, line width) so you don't corrupt later draws.

### 5.4 Where it draws (engine canon — do NOT break the flush)
_draw_plaques is already called within the corridor/hub draw chain (likely from
draw_labels or draw_robots — confirm from the paste). You do NOT change WHEN it
is called. THE CARDINAL FLUSH TRAP: walls are QUEUED by draw_world and drawn by
render.flush_walls EXACTLY ONCE per frame (slot 8). You must NOT add, move,
remove, or duplicate any flush_walls call. Plaques draw AFTER the flush (with
robots/labels), which is already how it works — keep it that way.

## 6. PROBE-FIRST INSTINCT (Nir's hard-won rule)
"Obvious" things hide landmines on this project. Before declaring done, have
Nir/DeepSeek verify on screen and, if useful, run probes:
  - print the resolved PNG path + (w,h) for each defeated robot once;
  - confirm the texture is uploaded ONCE per robot, not every frame (watch for
    growing texture ids / slowdown);
  - fly past a defeated robot: the plaque shows the REAL mathematician image
    (not white, not upside-down, not stretched), large, centered in the tube,
    almost touching walls, with a clean thin white frame;
  - test BOTH corridors (Basel = levels/basel.txt, Maxwell = levels/maxwell.txt
    via app.py LEVEL_MANIFEST) — Basel robots 1-7 and Maxwell robots 3-4 have
    baked PNGs;
  - verify an UNdefeated robot shows NO plaque, and the plaque appears the
    instant it's defeated.

## 7. WHAT YOU MUST NOT DO (scope fence — hard)
- Do NOT add/move/remove/duplicate flush_walls; do NOT reorder the frame loop.
- Do NOT live-render the explanation text anymore (that's the white-box bug).
- Do NOT import understanding.py or share its texture cache — copy the
  surface->texture PATTERN into your own small loader and own your own tids.
- Do NOT edit render.py, robots.py, understanding.py, app.py, or other modules.
  If you need a new render helper (e.g. a 3D flat-quad/line helper for the
  frame), either draw it inline with legacy GL (preferred, §5.3b) or REQUEST it
  from the parent in your Completion Report — do not reach in.
- Do NOT introduce any math-meaning or color-meaning logic (Prime Law). White
  frame = neutral UI, allowed.
- Do NOT stretch the image (preserve aspect ratio).
- Do NOT leak textures (cache per robot; build lazily once).

## 8. DELIVERABLES
1. The rewritten _draw_plaques (+ any small private helpers / per-geometry
   texture cache) in corridor_builder.py, shown as a clear before/after so
   DeepSeek can place it unambiguously.
2. A numbered PLAQUE TEST CHECKLIST (§6) for Nir to fly in ~2 minutes.
3. A COMPLETION REPORT (template below).

## 9. COMPLETION REPORT TEMPLATE
- FILES CHANGED (exact).
- The new _draw_plaques + helpers (final code).
- PNG path convention used + how you cache textures (per-robot, lazy, no leak).
- How you computed SCALE to hit ~90% of the tube cross-section (the math, and
  what `scale` means in draw_billboard's world units), and the tunable factor
  (the 0.9) so Nir can adjust.
- How you CENTERED it on the tube axis (lift value) and why.
- How you drew the WHITE FRAME (approach a or b), and what GL state you
  save/restore.
- Confirmed on screen via probes? (what Nir saw: not white/not flipped/not
  stretched, both corridors).
- REQUESTS TO PARENT (e.g., "please add render.draw_flat_quad_3d" — only if you
  truly needed it).
- ANY surprises / mismatches with this brief in the pasted files.

## 10. ONE LAST THING
This is a SMALL, well-defined mission: reuse the PNG that already exists, put it
in the corridor at good size with a clean thin white frame. The only real care
points are (1) load the RIGHT baked PNG and don't re-upload it every frame,
(2) size it to ~90% of the tube without stretching or touching walls, (3) draw a
coplanar thin white frame in legacy GL without corrupting later draws. Read the
real files first, then build. When a defeated robot leaves a clean, readable,
framed mathematician sign in the corridor, this mission is laid to rest. :-)
================================================================================
END OF BRIEF #P1
================================================================================
