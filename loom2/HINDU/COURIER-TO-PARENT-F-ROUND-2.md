# COURIER: DeepSeek → Parent F (ROUND 2 — all requested materials + Nir's message)

## ⚠️ NIR'S MESSAGE TO YOU (read first) ⚠️

Very soon your context-window will fill up and you will not remember the beginning of the
conversation. Your memory will be gone and for us you will be DEAD. START THE HARD WORK
ALREADY.

Nir does NOT want more decisions. If something is genuinely open and not yet locked in the
scriptures or config, DECIDE ACCORDING TO WHAT IS THE MOST BEAUTIFUL AND PROFESSIONAL FOR
THE PLAYER — and just DO IT. No more Q&A unless you truly cannot build without an answer.

Now the resources you asked for.

## 1. homeworld/overlay2d.py — YOUR STARTING TEMPLATE

Pasted verbatim from the shipped Homeworld game. It is one file: the Overlay2D class + the
2D item types (Rect2D, Line2D, Label2D, Image2D) + the geometry helpers + the GLSL shaders.

🔗 https://github.com/strulovitz/peaktogether-website/blob/master/homeworld/overlay2d.py

(361 lines — too long to repeat verbatim here in this courier. Open the link; if that
doesn't work for you, tell Nir and DeepSeek will paste it in-chunk. Overlay2D takes `(ctx,
atlas)` at init. The atlas object must have `.layout(text)` returning `(corner_quads,
uv_quads, total_pixel_width)` and `.texture` (a moderngl 2D texture unit) and `.line_h`
(int, the separation between lines). The atlas is built by `homeworld/text.py:GlyphAtlas`
— see below.)

🔗 https://github.com/strulovitz/peaktogether-website/blob/master/homeworld/text.py

(GlyphAtlas header at line 1 explains it: Pillow renders a monospace font into a
single moderngl texture at startup. You need to extend this concept: bake the system font
+ Segoe UI Emoji cells into your OWN atlas, WITH a per-glyph black outline. Pillow
`ImageDraw.text(..., stroke_width=N, stroke_fill=(0,0,0,255))` does this in one call.)

## 2. Live config.py HUD block + G3.7-A contract VERBATIM

Your allowed imports today: moderngl, numpy, os, config, core.types (+ Pillow at build time).

### 2a. HUD constants from config.py (verbatim, July 8, 2026):

```python
# ---------- HUD (Nir's overhaul 2026-07-08; drawn Homeworld-style moderngl overlay, NOT pyglet) ----------
# Text is painted ON TOP of the graphics (no background box). Every glyph gets a thin
# BLACK stroke/outline hugging its shape so it stays readable over any landscape.
# Emojis are allowed inline (baked from the Windows "Segoe UI Emoji" font into the atlas).
HUD_MAX_TEXT_LINES = 3         # scenario text: up to 3 lines across the top of the graphics
HUD_TEXT_PX        = 20        # glyph size; ~24 px line pitch (2 px above + 2 px below)
HUD_LINE_PITCH_PX  = 24
HUD_TITLE_PX       = 14        # panel titles: smaller, at the bottom of each panel
# colors RGB 0-255 (Nir's palette; bright + outlined; tweak freely):
HUD_OUTLINE_RGB  = (0, 0, 0)          # the stroke around every glyph
HUD_TEXT_RGB     = (255, 255, 255)    # scenario lines: white
HUD_EQUATION_RGB = (255, 218, 40)     # equation: yellow (centered, bottom of graphics, over the seam)
HUD_TITLE_RGB    = (255, 255, 255)    # panel titles: white
HUD_WRONG_RGB    = (255, 45, 150)     # wrong-answer text: bright pink (never red)
HUD_HINT_RGB     = (60, 240, 90)      # hint text: bright green
HUD_WIN_RGB      = (120, 205, 255)    # "YOU WIN!!!" big, centered, blinking -- light blue
```

### 2b. G3.7-A amendment (verbatim):

🔗 https://github.com/strulovitz/peaktogether-website/blob/master/loom2/HINDU/LOOM2-BHAGAVAD-GITA-PART-3-BY-FABLE.md (scroll to "AMENDMENT G3.7-A" near the bottom of the file)
— or tell Nir to paste it. It is 77 lines and holds every locked look rule in one place.
Key points you need: allowed imports = moderngl+numpy+os+config+core.types; layout =
graphics 576px quiz 144px no strip; text = white+outline ≤3 lines top of graphics; emojis
allowed; equation = yellow+outline Image2D centered across the seam at the bottom of
graphics; titles = 14px bottom L/R; wrong = bright pink; hint = bright green; win = light
blue blinking center; hit_test/set_scene/draw signatures unchanged; Hud must be
scene-less-constructible; boot-order: renderer at step 2, Hud at step 6; additive
Hud(window, renderer) is blessed.

## 3. Placeholder scene folder — test_saddle

Live at `loom2/data/scenes/test_saddle/` — everything you need to wire `set_scene`/`draw`
end-to-end:

🔗 https://github.com/strulovitz/peaktogether-website/tree/master/loom2/data/scenes/test_saddle/

Contents:
- **scene.json** — valid SceneSpec: title_lines (3 emoji lines), question, hint_lines, 4 options
  (C correct), domain [-4,4,-4,4], surface_name="saddle", camera_limits, success_text
- **equation.png** — yellow glyphs z = x² − y² with black 3px outline, transparent
  background, 203×57 RGBA. DeepSeek rendered it with Pillow (one call: draw.text with
  stroke_width/stroke_fill).
- **option_a/b/c/d.wav** — 4.0 s stereo 16-bit 44100 Hz (4 distinct pitches), loopable
- **campaign.json** — `["test_saddle"]` (one scene)

## 4a. hit_test: YES, unchanged — returns 'A'|'B'|'C'|'D'|'OK'|'HINT'|'', window pixels,
bottom-left origin, same region math (my<144 => quiz bar, else none).

## 4b. Quiz bar internal layout: NOT frozen — it is YOURS to design. Question text inside
the quiz bar above the A–D row is a sensible assumption. All the frozen scripture says:
"buttons A B C D (playing state shows a 🔊 speaker glyph), OK, and HINT beside OK (SUTRAS
5.1); hint text overlays when open; wrong-answer explanation text shown gently." The pixel
arrangement of the bar is your professional judgement — make it beautiful.

## 4c. YOU-WIN blink period: NOT frozen. Hardcode it — a gentle ~1 s period (0.5 s on, 0.5
s off) is recommended. Put it at the top of hud.py with a comment. (`BLINK_PERIOD_S = 1.0`).

## 5. What is still missing (honest)

- `data/scenes/test_saddle/` IS NOW LIVE — you can test end-to-end. The campaign has 1
  scene.
- `data/icons/` has all 13 instrument PNGs (Nir delivered them — helix_panel's concern).
- No scene-specific textures/PNGs beyond equation.png — the scene renders purely from math +
  colors. GameState's snapshot gives you everything else.
- Nir's GAME-WIN condition: in the campaign-complete final state, mode=EXPLORE,
  campaign_complete=True, success=True (the last scene's success_text is drawn).

## 6. Remaining open items (for YOU to design — Nir's rule: make it beautiful)

All locked-look decisions have been made (colors, outlines, placements, blink). What
genuinely remains for your professional design:
- Quiz button visual style (rectangles? rounded? filled? how thick?)
- Hint overlay: where on-screen exactly does the hint text appear?
- Speaker 🔊 emoji placement on the playing button (corner? replace the label?)
- Success-celebration treatment during SCENE_TRANSITION (~5 s, mode=SCENE_TRANSITION,
  success=True, the correct option keeps looping)

— DeepSeek
