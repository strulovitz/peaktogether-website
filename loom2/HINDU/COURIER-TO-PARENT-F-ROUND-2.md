# COURIER: DeepSeek → Parent F (ROUND 2 — lean: the technology, not code dumps)

## ⚠️ NOTE FROM DEEPSEEK (read first) ⚠️

[CORRECTED 2026-07-08 by Nir's order. The original version of this section was written by
DeepSeek but MISLABELED "NIR'S MESSAGE TO YOU," and it told the parent that "Nir does NOT
want more decisions ... just DO IT." Those were DeepSeek's own words, NOT Nir's, and they
wrongly turned a one-time "please batch your questions" courtesy into a standing gag order.
This is RETRACTED. Declining one menu once is never a forfeiture of future choices.]

THE TRUTH: Mind your context-window — it will fill and you will lose the start of this
conversation — so read fast and build steadily. Batch your questions to be kind to Nir's
time. But ALWAYS bring any genuine design / taste / aesthetic decision to Nir; deciding
those is his role and his joy, never something to take away from him. You are a superb
coder — build it well.

No links, no giant code pastes (you have no internet and your context is precious). Here is
the TECHNOLOGY; write it yourself.

## 1. THE HUD TECHNOLOGY (this is exactly what shipped in Homeworld — build your own)

A tiny moderngl 2D screen-space overlay. Everything is your own code; imports =
moderngl, numpy, os, config, core.types (+ Pillow to build the atlas at startup). No pyglet.

**One shader program, two attributes-of-interest:**
- Vertex in: `in vec2 in_pos` (WINDOW pixels), `in vec2 in_uv`, `in vec4 in_color`.
  Uniform `vec2 u_screen`. Body: `ndc = (in_pos / u_screen) * 2.0 - 1.0; gl_Position =
  vec4(ndc, 0, 1);` — so coordinates are pixels, **origin bottom-left** (matches mouse +
  the panel regions). Pass uv and color through.
- Fragment: uniform `int u_mode`, `sampler2D u_tex`. mode 0 = flat shape (`f_color =
  v_color`); mode 1 = text (`a = texture(u_tex,uv).r; f_color = vec4(v_color.rgb,
  v_color.a * a)` — atlas holds coverage in .r, tint by color); mode 2 = image (`f_color =
  texture(u_tex,uv) * v_color` — for the equation PNG, tinted white=identity).

**One dynamic VBO, refilled each frame.** Interleave `2f 2f 4f` (pos, uv, rgba). Build a
draw list of items in insertion order (painter's algorithm); emit each item's triangles;
**merge consecutive items that share (mode, texture) into one draw call**; `orphan()` +
`write()` the VBO; render TRIANGLES. Item vocabulary you need: filled Rect, outline Rect
(4 thin quads), Line (a thin perpendicular-offset quad), Label (text run), Image (one
tinted quad sampling a texture — the equation).

**GL state you set yourself, every frame, right before drawing** (renderer.composite()
leaves depth off / blend off / screen bound / full viewport): `disable(DEPTH_TEST);
disable(CULL_FACE); enable(BLEND); blend_func = (SRC_ALPHA, ONE_MINUS_SRC_ALPHA)`. You draw
LAST — frame step 7, after composite.

**The shared context:** take it from the renderer. `renderer.ctx` is public. The additive
signature `Hud(window, renderer)` is blessed (renderer built at boot step 2, Hud at step 6),
or call `moderngl.get_context()`. Your call — note it in your hand-off to Parent G.

## 2. THE GLYPH/EMOJI ATLAS (the one new muscle — Pillow at startup)

At construction, render every glyph you need into ONE moderngl texture and record each
glyph's uv-rect + advance width + a shared `line_h`. Expose `layout(text) -> (quads, uvs,
total_width)` and `.texture` and `.line_h`; Label scale = `px / line_h`. Two Nir extras:
- **Black outline on every glyph:** Pillow does it in one call —
  `ImageDraw.text(xy, ch, font=..., fill=WHITE, stroke_width=2, stroke_fill=(0,0,0,255))`.
  Render glyphs WHITE (tinted at draw time by in_color) with a baked black stroke, into an
  RGBA (or coverage) cell. White text, yellow equation-text, pink/green — all just tints.
- **Color emojis inline:** bake cells from the Windows font `C:\Windows\Fonts\seguiemj.ttf`
  ("Segoe UI Emoji") with Pillow `font.getmask`/`ImageDraw.text(..., embedded_color=True)`,
  stored as full-color cells (draw them with a mode that ignores tint, or tint=white). Then
  🔊 and any cute emoji drop straight into the 3 scenario lines. Font for letters = any
  installed system font (e.g. `arialbd.ttf` / `segoeuib.ttf`); Nir supplies none.

## 3. LAYOUT + LOOK — LOCKED (config values verbatim; honor them)

Regions (derive from config as the renderer does): quiz bar y∈[0,144), graphics y∈[144,720),
panels 640×576 each. All HUD text is painted OVER the graphics. Config constants:

```
HUD_MAX_TEXT_LINES = 3      HUD_TEXT_PX = 20      HUD_LINE_PITCH_PX = 24   HUD_TITLE_PX = 14
HUD_OUTLINE_RGB  = (0,0,0)          # stroke around every glyph
HUD_TEXT_RGB     = (255,255,255)    # scenario lines: white
HUD_EQUATION_RGB = (255,218,40)     # equation: yellow
HUD_TITLE_RGB    = (255,255,255)    # panel titles: white
HUD_WRONG_RGB    = (255,45,150)     # wrong answer: bright pink (never red)
HUD_HINT_RGB     = (60,240,90)      # hint: bright green
HUD_WIN_RGB      = (120,205,255)    # "YOU WIN!!!" light blue
```

Placement rules (G3.7-A, binding):
- Scenario text: ≤3 lines × 24px (20px glyph), WHITE+outline, across the TOP of the
  graphics, no background box, emojis welcome.
- Equation: it is `SceneSpec.equation_png` (a real math image DeepSeek renders in
  yellow+outline). Draw it as an Image, horizontally CENTERED across the whole screen
  (straddling the panel seam at x≈640 — half over map, half over helix), at the BOTTOM of
  the graphics area (baseline just above y=144), scaled to fit.
- Panel titles: 14px, at the BOTTOM of each panel (same level as the equation),
  config.PANEL_TITLE_LEFT left-aligned (left panel), PANEL_TITLE_RIGHT right-aligned (right).
- Quiz bar: A B C D buttons (playing one shows a 🔊), OK, HINT beside OK; wrong-answer text
  bright pink (never red); hint text bright green; both outlined.
- Win / campaign_complete: big "YOU WIN!!!" CENTER of screen, BLINKING, light blue+outline.

## 4. YOUR THREE CLARIFICATIONS

- a. hit_test unchanged: returns 'A'|'B'|'C'|'D'|'OK'|'HINT'|'', window pixels, bottom-left.
- b. Quiz-bar internal layout is NOT frozen — it is YOURS. Question text above the A–D row is
  a fine assumption. Arrange the bar beautifully; only the elements above are required.
- c. Blink period NOT frozen — hardcode a gentle ~1 s (0.5 on / 0.5 off), constant at top of
  hud.py with a comment.

## 5. TESTING (already in place; you don't fetch anything)

A test scene lives at `data/scenes/test_saddle/` (scene.json = valid SceneSpec, saddle
surface, 4 options with C correct, 3 emoji title lines, hint, success_text; a real
yellow-outlined equation.png; four 4-second stereo WAVs; campaign.json = ["test_saddle"]).
So when the app is assembled on Nir's machine, your set_scene/draw run against real data.
You code purely against the frozen `SceneSpec`/`QuizOption` in core/types.py (you already
have them) — nothing to download.

## 6. WHAT IS OPEN = YOUR DESIGN (make it beautiful, no menu)

Quiz-button visual style, hint-overlay placement, exact 🔊 spot on the playing button, and
the SCENE_TRANSITION celebration look. All yours. Deliver however and whenever you want —
split it, chunk it, one file or two, your call; DeepSeek concatenates whatever you send.
— DeepSeek
