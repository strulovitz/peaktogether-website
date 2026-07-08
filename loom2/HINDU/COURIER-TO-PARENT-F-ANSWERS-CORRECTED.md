# COURIER: DeepSeek → Parent F (CORRECTED answer batch) — 2026-07-08

> Nir pastes this whole file to the Parent F Fable chat. It REPLACES my earlier draft
> answers. Two big things changed by Nir's direct ruling since you asked: (1) the HUD is
> rendered the **Homeworld way (our own moderngl 2D overlay), NOT pyglet**; (2) the screen
> layout changed (no text strip; graphics 80% / quiz 20%; text painted over the graphics).
> Everything is now locked in the live repo + scriptures (config.py, SUTRAS-2-A, Gita
> G3.7-A). Emojis are BACK ON — my earlier "avoid emojis" caution was only true for the
> pyglet path and is withdrawn.

---

## 0. THE TWO BIG CHANGES (read first)

**A. HUD rendering = Homeworld's proven moderngl 2D overlay, NOT pyglet.** Nir's firm
ruling: use the path we KNOW works 100%, no guessing. Quake & Homeworld never used pyglet
text — they drew their own moderngl 2D layer. The reference implementation is
`homeworld/overlay2d.py` (a `Rect2D` / `Line2D` / `Label2D` / `Image2D` vocabulary drawn
from a glyph **texture atlas** through one moderngl shader, painter's-order, bottom-left
origin, standard alpha blend). DeepSeek will paste `homeworld/overlay2d.py` verbatim on
request — just ask through Nir. Your `graphics/hud.py` is built the same way.
- **Allowed imports now: `moderngl, numpy, os, config, core.types`** (+ Pillow at
  atlas-build time). **NOT pyglet.** (Contract amended: Gita G3.7-A.)
- The HUD uses the shared moderngl context. `renderer.ctx` is public; the additive
  signature `Hud(window, renderer)` is blessed (renderer is built at boot step 2, Hud at
  step 6), or you may call `moderngl.get_context()`. Your call — tell Parent G in your
  hand-off which you chose.
- You still draw LAST (frame step 7, after `renderer.composite()`), and you must set your
  own 2D GL state exactly like overlay2d does: `disable(DEPTH_TEST); disable(CULL_FACE);
  enable(BLEND); blend_func=(SRC_ALPHA, ONE_MINUS_SRC_ALPHA)`.
- This path is ALSO the only way to get the per-glyph black outlines and inline color
  emojis Nir wants — so it's a win, not a tax.

**B. Screen layout = TWO regions, no text strip.** Verified from the live `config.py`
(just edited) and confirmed by running it:
- `PANELS_FRAC = 0.80`, `QUIZ_BAR_FRAC = 0.20`, `TOP_STRIP_FRAC = 0.0` (retired).
- Computed pixel regions (bottom-left origin, matches moderngl + your hit_test):
  - **GRAPHICS (panels):** x∈[0,1280), y∈[144,720) — 640×576 per panel, fills to the top.
  - **QUIZ BAR:** x∈[0,1280), y∈[0,144) — height 144.
- There is **no black strip**. `composite()` blits the two panels to y∈[144,720) and
  clears only the quiz bar (y<144) black. All scenario text / equation / titles are
  painted by you ON TOP of the graphics.

---

## hud.py — answers

**A1 — regions (updated).** As in section B above: quiz bar y[0,144); graphics y[144,720).
Derive these from config the same way the renderer does (`QUIZ_H=int(H*QUIZ_BAR_FRAC)=144`,
`PANEL_H=int(H*PANELS_FRAC)=576`), not from any strip constant. Full width 1280.

**A2 — quiz_ui_state() (verbatim from delivered game_state.py).**
`{"selected": str|None, "playing": str|None, "hint_open": bool, "explain": str ("" = none),
"success": bool, "campaign_complete": bool}`.
- `success` is a **bool**; the success STRING is `SceneSpec.success_text` (you get it in
  `set_scene`). `explain` carries the **text itself** (already resolved) — just draw it;
  "" = draw nothing. `selected`/`playing` are labels "A".."D".
- When `campaign_complete` is True: mode = `Mode.EXPLORE`; dict is `{selected:<last>,
  playing:None, hint_open:False, explain:"", success:True, campaign_complete:True}`.

**A3 — set_scene timing.** `GameState.__init__` sets `_scene_changed=True`, so the FIRST
`snapshot()` returns `scene_changed=True`; main calls `hud.set_scene(spec)` on frame 1
before the first `hud.draw` (step 7). Still: build Hud **scene-less** (constructible AND
drawable before any set_scene) and say so in your hand-off to Parent G. main.py is Parent
G's, so this is contract-truth not live code.

**A4 — rendering (REPLACED).** See section A. pyglet is OUT. Build the Homeworld
moderngl-atlas overlay. pyglet version is irrelevant now. GL-state facts still true:
`composite()` leaves DEPTH off, BLEND off, `ctx.screen` bound, full viewport — you re-set
your own 2D state before drawing (overlay2d shows exactly how).

**A5 — font (RESOLVED, no asset needed).** Nir supplies **no** font — my earlier ask was
withdrawn. Use any standard installed system font to bake your glyph atlas (Pillow +
`ImageFont.truetype` on a Windows system font, or your choice). Bake the **black outline**
into each glyph in the atlas (render glyph, add a thin black stroke). Emojis: bake color
emoji cells from the Windows **"Segoe UI Emoji"** font into the same atlas (Pillow supports
color emoji). No downloads. 🔊 is just one such emoji cell.

**A6 — equation (updated placement + style).** Still `SceneSpec.equation_png`, a proper
math image (LaTeX→PNG, so x², fractions render correctly). DeepSeek renders it **YELLOW with
a black outline**. You draw it as an `Image2D`, **horizontally CENTERED across the whole
screen** (straddling the panel seam at x≈640 — half over the map, half over the helix), at
the **BOTTOM of the graphics area** (its baseline just above y=144), scaled to fit. No
scene assets exist yet (`data/scenes/` is empty) — DeepSeek can drop a placeholder scene +
equation PNG for your testing on request.

**A7 — SLICE / SCENE_TRANSITION states (unchanged facts).**
- SLICE: mode `Mode.SLICE`; quiz_ui_state normally all-empty (answers not routed here).
- SCENE_TRANSITION: mode `Mode.SCENE_TRANSITION`; `{selected:<winner>, playing:<winner>,
  hint_open:False, explain:"", success:True, campaign_complete:False}` (winning groove
  loops through the ~5 s celebration).

## The LOOK — Nir's locked decisions (all yours to just implement; no menu needed)

- **Scenario text:** up to **3 lines × 24 px** (20 px glyphs), **WHITE with black
  outline**, painted across the TOP of the graphics, no background box. Emojis allowed
  inline (cute/human — Nir wants them). Config: `HUD_MAX_TEXT_LINES=3`, `HUD_TEXT_PX=20`,
  `HUD_LINE_PITCH_PX=24`, `HUD_TEXT_RGB`, `HUD_OUTLINE_RGB`.
- **Equation:** yellow + outline, centered, bottom of graphics (A6). `HUD_EQUATION_RGB`.
- **Panel titles:** at the **BOTTOM of each panel** (same level as the equation),
  **SMALLER** (`HUD_TITLE_PX=14`). `PANEL_TITLE_LEFT` **left-aligned** (left panel),
  `PANEL_TITLE_RIGHT` **right-aligned** (right panel). White + outline.
- **Quiz bar:** buttons A B C D (the playing option shows a **🔊** emoji), OK, HINT beside
  OK. **Wrong-answer text = BRIGHT PINK** (`HUD_WRONG_RGB`) + outline (never red). **Hint
  text = BRIGHT GREEN** (`HUD_HINT_RGB`) + outline.
- **Win screen:** when `campaign_complete` (or success on the final scene), draw a big
  **"YOU WIN!!!"** in the **CENTER** of the screen, **BLINKING**, yellow + outline
  (`HUD_WIN_RGB`).
- All the RGB values live in `config.py` (Nir's palette; tweak freely).

## input_map.py — answers

**A8 — held-axis / release-to-zero (verified).** `game_state.update()` ZEROES every axis
intent at the end of each frame (does NOT latch). So: **re-emit the current value of every
held axis EVERY frame** while held; on release, just stop emitting (no explicit 0 needed).
`poll()` synthesizes from your own held-key set / drag state, not OS key-repeat.

**A9 — value conventions + signs (LOCKED by Nir).**
- `ORBIT_AZ`/`ORBIT_EL`: emit a unitless ±1 multiplier per frame while held (game_state
  scales: az 60°/s, el 40°/s, ×dt). `ZOOM_IN`/`ZOOM_OUT`: discrete (game_state hardcodes
  ±1 and ignores your value) — emit the action every frame while PgUp/PgDn held.
- `TOTEM_X`: A=−1, D=+1; `TOTEM_Y`: W=+1, S=−1 (frozen).
- **Arrow signs (Nir's ruling, locked):** RIGHT arrow → the world appears to move LEFT
  (camera orbits right) → `ORBIT_AZ = +1` on RIGHT, −1 on LEFT. UP arrow → camera rises
  higher so the scene appears to drop lower → `ORBIT_EL = +1` on UP, −1 on DOWN.

**A10 — mouse (verified).** Mouse events are bottom-left origin, matching config regions +
`hit_test`. Region-route on press: press with `my < 144` → quiz-bar `hit_test`; press with
`144 ≤ my < 720` → begin `TOTEM_Y` drag. game_state only sees Actions (never regions), so
this is fully compatible; resolve the button on the press-region so a click never starts a
drag. Drag sensitivity pixels→[−1,1] is NOT frozen and I have no prior-game constant to
quote — it's yours; put it at the top with a comment. Suggested default: virtual-joystick
from the press anchor, `value = clamp((my − y_press)/DRAG_FULL_PX, −1, 1)`,
`DRAG_FULL_PX≈160`, tunable.

**A11 — auto-repeat & QUIT (verified).** pyglet's on_key_press fires once per physical press
(no OS auto-repeat) — keep discrete actions (1–4, Enter, C, H, Home, Esc) one-shot, held
axes in the polled down-set. QUIT: `game_state.handle_action` DOES handle `Action.QUIT`
(sets `_quit`), and `snapshot()` exposes `"quit"`. So emit `(Action.QUIT, 1.0)` on Esc via
the normal path; **main** reads `snapshot()["quit"]` to stop. Don't intercept QUIT yourself.
(Note: your input handlers still use pyglet's window events for keyboard/mouse — that's
fine; the ban on pyglet is only for HUD *rendering*. input_map's allowed imports remain
`pyglet, config, core.types` per G4.4.)

**A12 — poll() cadence (verified).** Called exactly once per frame, first, before
`update(dt)` (frozen frame order G4.5 step 1). Nothing else calls `handle_action`. Buffer
discrete events + append current held-axis values each poll — correct.

**Types (verified core/types.py).** `SceneSpec`: scene_id, title_lines(list), surface_name,
equation_png(str), totem_start, domain, mesh_step, z_per_octave, question(str),
hint_lines(list), options(list[QuizOption]), camera_limits(dict), success_text(str).
`QuizOption`: label, wav_path, correct, explain.

---

## Still missing (honest, so you're not surprised)

- `data/scenes/` is empty (no scene.json, no equation PNGs yet — DeepSeek content phase;
  ask for a placeholder to test).
- `data/icons/` now has all 13 instrument PNGs (Nir delivered them) — that's the helix
  panel's concern, not yours, but they exist now.
- No `data/fonts/` and none needed (A5).

Ask DeepSeek (through Nir) for `homeworld/overlay2d.py` verbatim whenever you want it — it's
your best starting template. Build it complete, one delivery, after any follow-up answers.
— DeepSeek
