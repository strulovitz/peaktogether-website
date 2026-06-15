BUG REPORT -- Brief #16 plaque (child Opus 4.8)

Your plaques FAIL in 3 ways visible on screen:
1. VICTORY #1 appears far ahead of the robot, stretched into an unreadable
   horizontal strip.
2. It flickers against the walls.
3. Backing card renders opaque, hiding the text.
4. GL state leaked after draw (GL_TEXTURE_2D left disabled).

ROOT CAUSES you must fix:
(a) tw,th are PIXELS (560x14), not world units. pixel_aspect = 560/14 = 40.
    draw_billboard(scale=0.7, aspect=40) makes a quad 28 world-units WIDE
    and 0.7 tall -- unreadable. ADD a PLAQUE_MAX_WORLD_WIDTH constant (e.g.
    4.0) and CLAMP: corrected_scale = min(PLAQUE_SCALE, max_width/max(aspect,1))
    Use corrected_scale for BOTH the backing card AND draw_billboard calls.
(b) The backing card uses glDisable(GL_TEXTURE_2D) but does NOT
    glEnable(GL_BLEND). Without alpha blending, the card is opaque and the
    text billboards on top fail. Add glEnable(GL_BLEND) before the
    backing card quad.
(c) No glDisable(GL_DEPTH_TEST) / glDepthMask(GL_FALSE) before the
    billboard. Nearby walls cause z-fighting flicker. Disable depth for
    the whole plaque draw (like holograms in robots.py do).
(d) glEnable(GL_TEXTURE_2D) must be called at the end of _draw_plaques
    (not just glColor4f restore).

DeepSeek already applied these fixes. Read corridor_builder.py _draw_plaques
for the corrected pattern. Use it as reference for your next attempt.

These edits are in corridor_builder.py lines 352-422.
