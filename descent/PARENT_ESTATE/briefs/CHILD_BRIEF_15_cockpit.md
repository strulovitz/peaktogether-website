================================================================================
DESCENT QED -- BRIEF #15: COCKPIT -- a polygon-built, resolution-independent HUD
that resembles the Descent (1995) cockpit, with a real 3x3 face grid panel.
SCOPE: replace the scattered floating HUD with a CockpitHUD drawn from polygons
(geometry + math), laid out entirely by FRACTIONS of the current viewport so it
fits ANY resolution and re-fits on resize. All nine faces live in a 3x3 GRID
panel. STRAIGHT angled window struts (NO curves), dark bordered panels bottom,
glowing center gauge. This also fixes the face-grid / text overlap (each thing
gets its own panel). Build it as ONE module: cockpit.py. NOT sprites. NOT a fixed
pixel strip.
================================================================================

WHY A DEDICATED CHILD (not DeepSeek): this is real design work -- modeling a
cockpit out of 2D polygons that scales by formula, a straight-strut window frame,
a 3x3 grid layout solver, panel framing, and migrating the HUD text. It needs
thought, not pixel-nudging. DeepSeek tunes values AFTER you build it.

FRESH-CHAT -- but DO NOT make Nir paste the whole repo. After he uploads the
reference image, ask Nir for ONLY these, verbatim & current, because you need
their REAL seams (and nothing else):
  1. render.py  -> ONLY: (a) draw_plain_text_2d's real signature + how it sets up
     the 2D ortho projection and GL state (blend/depth) and screen coords origin
     (top-left vs bottom-left -- CONFIRM which); (b) how to get the CURRENT
     viewport width/height (the resolution) at draw time; (c) any quad/texture
     blit helper + the portrait/face loader (load_portrait or similar) so you can
     place faces in the grid; (d) any existing 2D-panel/rect draw helper.
  2. combat.py -> ONLY: the draw_hud function + the current face-panel draw + the
     "VULNERABLE TO:" / "LOADED:" / fizzle text draws (the call sites you migrate).
  3. game_state.py -> ONLY: the text it draws ("RESCUED n/N", "HOSTAGES RESCUED",
     "LEVEL COMPLETE") so the cockpit hosts the status + flash beats.
  4. app.py -> ONLY: the frame-loop slot where the HUD is drawn, and whether a
     resize/viewport-change event exists.
If anything here disagrees with the brief, THE FILE WINS -- flag it. Ask for a face
PNG's pixel dimensions if you need aspect ratio.

WHO: NIR = non-technical tester + courier (he flew it; he uploaded the Descent
reference screenshot). DEEPSEEK = AFTER you ship, tunes fractions/colors only.
PARENT = architecture. You DESIGN this.

PRIME LAW: the cockpit is pure decoration + layout. It carries NO mathematical
meaning and assigns NO color->meaning. Frame, panels, glow = aesthetics only.

------------------------------------------------------------------------------
THE REFERENCE (Descent 1995 cockpit -- Nir's uploaded screenshot)
------------------------------------------------------------------------------
A dark cockpit frames the 3D view:
  - TOP: window/canopy struts frame the view from the top corners, leaving the
    center of the view clear. (We build these as STRAIGHT angled bars -- see
    WINDOW FRAME below -- NOT curves.)
  - BOTTOM: a solid dark dashboard spanning the width, raised in the middle.
  - LEFT panel: weapon readout (icon + name like "LASER LVL 1") in a bordered box.
  - CENTER: a raised gauge with a big glowing number/ring (status).
  - RIGHT panel: weapon + ammo ("CONCEN MISSILE 005") in a bordered box.
  - small status pips far bottom-left ("LOCK").
We will NOT copy textures/sprites. We REBUILD this STRUCTURE from polygons so it's
crisp at any resolution, and we ADD a 3x3 face grid panel (Nir's requirement).

------------------------------------------------------------------------------
HARD REQUIREMENTS (Nir's words -- do not violate)
------------------------------------------------------------------------------
1. POLYGONS, NOT SPRITES. Build the frame/panels/gauge/window struts from filled +
   outlined 2D polygons (triangles/quads/line strips). The only textured quads
   allowed are the FACE photos themselves (and optional weapon icons). Everything
   structural is geometry, so it stays sharp at any resolution.
2. RESOLUTION-INDEPENDENT BY FORMULA. NO hardcoded pixel constants for layout.
   Read the CURRENT viewport (W,H) every frame (or on resize) and express EVERY
   coordinate, size, thickness, gap, font size, and the window struts as FRACTIONS
   of W and H (e.g. dashboard height = 0.18*H; face cell = 0.06*min(W,H)). It must
   look right at 1280x720, 1920x1080, 2560x1440, ultrawide, etc., WITHOUT code
   edits. Recompute layout when W,H change.
3. FACES = 3x3 GRID. All nine faces in a single bordered grid panel (3 cols x 3
   rows), evenly spaced by formula, each in its own framed cell. NOT a row. The
   grid is its OWN panel with its OWN reserved space.
4. NOTHING OVERLAPS. Because every element owns a computed rectangle, the text
   ("VULNERABLE TO:", "LOADED:") and the face grid never collide. This is the
   bug fix, achieved structurally.

------------------------------------------------------------------------------
WINDOW FRAME = STRAIGHT ANGLED STRUTS (NO CURVES)
------------------------------------------------------------------------------
Build the cockpit canopy from STRAIGHT diagonal lines/polygons, not arcs. Each top
corner has a strut that runs inward at an ANGLE (a slanted bar), framing the view
like an angular windshield.
  - Each strut = a filled quad (a thick diagonal bar) plus a thin highlight edge
    line, dark gray. Mirror left/right.
  - Endpoints defined by FRACTIONS of W,H (e.g. strut starts near the top-left
    corner and angles inward to about (0.30*W, 0.14*H)) so the angle and thickness
    scale with resolution. Pick clean fractions; expose them as Nir-tunable.
  - Optionally 2-3 angled segments per side (a polyline of straight angled bars)
    to suggest the angular frame -- still ALL STRAIGHT lines, no curves.
Do NOT generate any curve, Bezier, or circular arc for the window frame.
(The center gauge ring may stay circular -- it's a dial, not the window frame -- but
 if simpler, an angular/hex gauge is fine too.)

------------------------------------------------------------------------------
WHAT TO BUILD -- cockpit.py
------------------------------------------------------------------------------
class CockpitHUD:
    def __init__(self, ...): load faces once (reuse the real face loader); cache
        nothing resolution-dependent here.
    def layout(self, W, H): compute ALL rectangles/points as fractions of W,H and
        store them. Call when W,H change (and once at start). This is the math
        core -- a clean dataclass/dict of named regions:
          strut_left/right (straight angled bar endpoints),
          dash_rect, left_panel, center_gauge, right_panel, face_grid_rect,
          face_cells[9] (3x3), text_anchor_vuln, text_anchor_loaded, pips[...].
    def draw(self, W, H, state): if W,H changed since last layout -> relayout.
        Then draw, in order: window struts (top) -> dashboard fill -> panel borders
        -> face grid (frame + 9 faces + optional small label per cell) -> center
        gauge (ring + big number) -> weapon readouts -> text via draw_plain_text_2d
        -> status pips. `state` carries what to show (selected weapon, ammo,
        vulnerable-to text, loaded text, rescued count, etc.) -- pull these from
        what combat.py/game_state.py already compute; do NOT invent game logic.

POLYGON HELPERS you implement inside cockpit.py (small, pure):
  - filled_rect(x,y,w,h,color,alpha) and rect_border(...,thickness) from quads/
    lines.
  - rounded/beveled panel (optional) from a few extra triangles.
  - strut(p0, p1, thickness, color) : a thick straight diagonal bar built as a
    quad (offset the line by half-thickness perpendicular), plus a thin highlight
    edge. Mirror left/right.
  - gauge_ring(cx,cy,r,...) : a ring from a triangle strip around a circle
    (segment count from a formula), with an inner glow (a second translucent ring).
  All math is straightforward trig/linear interpolation. Comment the formulas.

COORDINATE ORIGIN: match what render.py's 2D path uses (CONFIRM top-left vs
bottom-left from the paste) and use it consistently. All Y math respects that.

TEXT: every label/number via draw_plain_text_2d (no _mt, no \mathrm). Font size
also a fraction of H so it scales. Center the "HOSTAGES RESCUED" flash and "LEVEL
COMPLETE" banner over the whole screen (above the cockpit).

------------------------------------------------------------------------------
ENGINE CANON -- DO NOT BREAK
------------------------------------------------------------------------------
Frame order: ... draw_world -> flush_walls (EXACTLY ONCE) -> draw_robots ->
labels/HUD -> flip. The cockpit draws in the HUD/2D step (after flush), in the
same ortho 2D regime draw_plain_text_2d uses. DO NOT add/move/remove/duplicate
flush_walls (walls vanish silently). DO NOT touch the 3D loop or how MATH renders.
Save/restore GL state exactly like the existing 2D path (blend on, depth test off
for HUD, ortho push/pop) and leave GL as you found it.

------------------------------------------------------------------------------
WHAT YOU MUST NOT DO
------------------------------------------------------------------------------
- Do NOT design or code before Nir uploads the reference image.
- NO sprites / no prebaked HUD image for the structure (faces stay the only photos).
- NO hardcoded pixel layout constants -- fractions of W,H ONLY.
- NO curves/Bezier/arcs for the window frame -- STRAIGHT angled struts only.
- NO putting faces in a row -- it's a 3x3 GRID, all nine.
- NO element overlap -- every region is a computed rectangle.
- Do NOT touch flush_walls / reorder loop / change 3D / change math rendering.
- Do NOT invent game logic, scoring, or a LOSE state (there is NO losing).
- Do NOT map color->meaning or interpret math meaning.
- Do NOT make Nir paste the whole repo -- only the seams listed above.

------------------------------------------------------------------------------
DEMO -- `cockpit_demo.py` (Nir RUNS this)
------------------------------------------------------------------------------
Reuse app.py's real init + 2D setup VERBATIM. Feed dummy state (a selected weapon,
ammo, "VULNERABLE TO: ...", "LOADED: ...", RESCUED 2/5, and all 9 faces).
ACCEPTANCE Nir must SEE:
  1. A polygon cockpit: STRAIGHT angled window struts top, dark dashboard bottom,
     bordered left/right panels, glowing center gauge. Resembles the reference.
  2. A 3x3 face grid (all nine faces), framed, evenly spaced, NOT a row.
  3. "VULNERABLE TO:" and "LOADED:" readable, in their own area, NOT covered by
     faces. Nothing overlaps.
  4. RESIZE TEST (critical): the demo must let Nir resize the window (or expose a
     couple of preset resolutions) and the WHOLE cockpit re-fits proportionally --
     struts, panels, grid, fonts all scale. No clipping, no off-screen panels, at
     720p, 1080p, 1440p, and an ultrawide aspect.
  5. "HOSTAGES RESCUED" flash + "LEVEL COMPLETE" centered over everything.
  6. Walls present in the actual game (flush trap intact).

------------------------------------------------------------------------------
COMPLETION REPORT
------------------------------------------------------------------------------
- CONFIRM you saw the reference image before designing (Y/N)
- FILES ADDED/CHANGED (cockpit.py; combat.py + game_state.py migrated to it; demo)
- RUN-VERIFIED at multiple resolutions? (Y/N -- list which)
- CONFIRMED coordinate origin (top-left/bottom-left) from render.py
- The layout() formula table: each region as its fraction-of-W/H expression
- The strut endpoints as fractions of W,H and the strut thickness formula
- How the 3x3 grid cells are computed (the formula)
- Confirm: all text via draw_plain_text_2d; no _mt; math rendering untouched
- Confirm: no element overlap; faces in 3x3 grid (not a row); no curves used
- WIRING LINES the parent must add (file + location, copy-paste) incl. resize hook
- DEVIATIONS / file-wins flags / face-PNG aspect ratio used
- DEEPSEEK tuning TODOs: the fraction values, colors, glow alpha, segment counts
================================================================================
END OF BRIEF #15
================================================================================
