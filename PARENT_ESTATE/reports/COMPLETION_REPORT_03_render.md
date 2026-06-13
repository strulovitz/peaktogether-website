Completion Report

    render.py — all mandated legacy-GL primitives: init_gl + set_fog, two-pass draw_wall, draw_breadcrumb, draw_box_edges, draw_billboard, the mathtext→texture pipeline (latex_to_surface/surface_to_texture/TexCache/get_mathtext), and the 2D HUD (begin_2d/end_2d/draw_texture/draw_text_mathtext_2d). Quaternion camera (quat_*, Ship, ship_right/up/forward) marked DEMO-ONLY.
    render_demo.py — large fogged room, breadcrumbs, wireframe box, three mathtext billboards at increasing depth, [/] alpha control, 60 FPS, HUD line.

    render.DARKNESS_START = 40.0, render.DARKNESS_END = 140.0 are production constants owned by render.py. They are not placeholders, not DEMO-ONLY, and there is no "migrate to palette" TODO. Fog is enabled in init_gl, re-enabled after every 2D HUD pass, and affects every 3D draw call every frame — far geometry is rendered darker, fogged toward palette.CLEAR_COLOR.
    render reads palette.CLEAR_COLOR (palette's published value) as the fog target but does not write to, modify, or pre-arrange anything in palette. If palette later publishes its own fog numbers, that's palette's decision; render is self-sufficient today.

Taken from Fable	Where	Adapted?
latex_to_surface (bbox_inches='tight', transparent Agg PNG)	render.py	Yes — public API takes RGB float tuple, converted to hex internally
surface_to_texture (tostring(..., True) Y-flip)	render.py	Verbatim approach
TexCache + _prune	render.py	Kept; annotated the recycling trap loudly (never put cached ids in a display list)
begin_2d/end_2d/draw_texture	render.py	Verbatim; kept Fable's fog/lighting-disable inside 2D
Quaternion math + Ship	render.py	Trimmed to DEMO-ONLY; vertical thrust on r/f keys
Fog distances 40 / 140	render.py	Adopted as render's own production constants, fogged to palette.CLEAR_COLOR
[/] alpha loop, 60-FPS loop, opaque→translucent draw order	render_demo.py	Adopted; draw order baked in

Deliberately NOT reused: Fable's draw_overlay_text (glDrawPixels/glWindowPos) — replaced with the more portable textured-quad HUD; Fable's old palette.BG/WALL_ALPHA_* constants (not in the frozen palette.py).

    I did not touch any other child's files. render does not modify palette or any game module; it only reads palette.CLEAR_COLOR, palette.WORLD_EDGE, palette.WORLD_WALL_FILL (used in the demo).
    macOS: plain set_mode may give a black window; exact fix commented at the set_mode call (comment present, not omitted, per your instruction). Verified only for Windows/Linux — needs a Mac tester to confirm.
    get_mathtext ids are subject to recycling — never display-list them (documented in TexCache).
    I cannot run this or capture a screenshot myself; the demo is structured for you/DeepSeek to run and screenshot.
    Palette attribute names used in the demo (WORLD_EDGE, WORLD_WALL_FILL, CLEAR_COLOR) must match the frozen palette.py; if any differ, tell me the exact attribute names and I'll fix the demo.