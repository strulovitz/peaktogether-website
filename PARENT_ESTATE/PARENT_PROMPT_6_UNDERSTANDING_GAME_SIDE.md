# 🚀 PARENT 6 PROMPT — Understanding Mode: game-side PNG integration

> **TO:** Claude Opus 4.8 — You are PARENT #6.
> **FROM:** Nir (strulovitz) + DeepSeek V4 Pro (OpenCode)
> **PASTE THIS ENTIRE DOCUMENT** into a fresh Claude conversation.

---

## 0. WHAT CHANGED (one paragraph)

The old Understanding Mode rendered explanations LIVE using matplotlib's mathtext — a crippled LaTeX subset that cannot color individual symbols. We replaced it with a PRE-BAKE pipeline: a standalone baker (`deu/bake_corridor.py`) compiles full-LaTeX explanations into transparent, colored PNGs offline. Those PNGs are shipped with the game. The game just loads + stacks + fades them. The baker works perfectly (28/28 layers bake with zero failures). The game-side swap has NOT been built yet.

---

## 1. THE GAME — LAW (from PARENT_HANDOFF_V3.md §1)

DESCENT QED is a 6-DOF flying game. A couple pilots a spaceship through corridors. ROBOTS block the way. Pressing U near a robot opens Understanding Mode: 4 layered explanation panels at 4 depths (mathematician / physicist / biologist / engineer) that the player fades between with the mouse wheel.

---

## 2. WHAT ALREADY EXISTS AND WORKS

### Baker (standalone, proven):
- `deu/bake_corridor.py` — reads a corridor `.txt` file, compiles via pdflatex → pdftocairo → transparent PNGs
- Output: `baked/<name>/robot<N>_<layer>.png` (e.g. `baked/maxwell/robot3_mathematician.png`)
- All 4 layers per robot: `mathematician`, `physicist`, `biologist`, `engineer`

### Level manifest wiring (already built):
The level manifest format now supports a `baked:` line:

```
title: Maxwell Test Corridor
baked: baked/maxwell
corridors:
  ../corridors/maxwell_old.txt
```

`level_parser.py` parses this and propagates it to every `RobotData` object:

```python
# RobotData already has:
understanding_dir: str = ""   # e.g. "baked/maxwell" — Brief #11d
```

So `robot._robot_data.understanding_dir` = `"baked/maxwell"` and `robot._robot_data.number` = `3`.

### How Understanding Mode is triggered (in app.py):
```python
# U key opens it:
elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_u and not umode.active:
    robot = combat.Combat.blocking_robot(hub)
    if robot is not None:
        umode.open(robot._robot_data)   # passes RobotData

# When active, world update/draw is gated:
if umode.active:
    umode.handle_input(events, keys, gamepads, dt)

# Drawing (between begin_2d/end_2d):
render.begin_2d(*WIN_SIZE)
combat_state.draw_hud(texcache, WIN_SIZE)
game_state.draw_hud(texcache, WIN_SIZE)
umode.draw(texcache, WIN_SIZE)
render.end_2d()
```

### Existing Understanding Mode (understanding.py — needs replacing):
The current `understanding.py` (~130 lines) renders via `render_rich()` — live mathtext, single color, no backdrops. It has working:
- 4-layer depth with smooth `focus` animation
- Mouse wheel = depth, mouse = pan, right stick = pan
- CTRL = engineer unlock, ESC = exit
- `open(robot_data)` / `close()` / `handle_input()` / `draw()` interface

All the gamepad/mouse/keyboard plumbing works. Only the RENDERING needs to change.

### 2D rendering primitives available:
```python
# Loading a PNG as a GL texture (pattern from robots.py):
surf = pygame.image.load(path).convert_alpha()
data = pygame.image.tostring(surf, "RGBA", True)  # flip for GL
tid = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, tid)
glTexParameteri(...)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

# Drawing a texture in 2D (render.py):
render.draw_texture(tex, x, y, scale=1.0, alpha=1.0)
# tex = (tid, w, h)

# Blur (render.py):
render.blur_surface(surf, radius)  # returns blurred pygame Surface
```

---

## 3. WHAT TO BUILD

Replace `understanding.py` to use pre-baked PNGs instead of live `render_rich()`.

### Core idea:
- On `open(robot_data)`: load 4 PNGs from `baked/<dir>/robot<N>_<layer>.png` into GL textures
- On `draw()`: stack the 4 PNGs far-to-near, with size/blur varying by depth
- The player "flies" through the signs with the mouse wheel
- Mouse + right stick pan the focused sign

### Physics metaphor (Nir's design):
- Each layer is a **glass sign** hanging in space. Its transparency is baked into the PNG.
- Distance creates **fog** (washes out far signs) and **blur** (far signs out of focus).
- Flying closer = sign grows larger + comes into focus.
- The focused sign can be panned around when it's larger than the screen.
- A small **minimap** in the corner when the focused sign overflows the screen.

### What must stay exactly the same:
- `LAYER_KEYS = ["mathematician", "physicist", "biologist", "engineer"]`
- `LAYER_TITLE` dict
- `open(robot_data)` / `close()` / `handle_input(events, keys, gamepads, dt)` / `draw(cache, win_size)` signatures
- Mouse wheel = depth, mouse = pan, right stick = pan, CTRL = engineer unlock, ESC = exit
- Smooth `focus` animation toward `target`
- CTRL-locked engineer layer (extra blur until CTRL held)
- Backing out past mathematician (focus < -0.6) exits

### Fallback:
If a baked PNG is missing for any layer, fall back to the old behavior: render the `robot_data.explain[layer]` text via `render_rich()`.

### Texture cleanup:
Delete GL textures in `close()` to avoid leaks.

---

## 4. SCOPE FENCE

- Do NOT touch `app.py`, `combat.py`, `gamepad.py`, `robots.py`, `corridor_builder.py`, `hub_builder.py`, `level_parser.py`, `content_parser.py`
- Do NOT touch the baker (`deu/bake_corridor.py`)
- Do NOT touch corridor `.txt` files or level manifests
- Do NOT change the `open()`/`close()`/`handle_input()`/`draw()` signatures
- The existing `understanding.py` is the ONLY file you replace
- Do NOT build a standalone demo — the real `app.py` uses it directly

---

## 5. HOW TO TEST

```
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Fly into the Maxwell corridor, approach robot 3 (Faraday) or 4 (Ampère), press U.

Expected: 4 glass-sign PNGs with red/blue/purple stains, fog between layers, smooth depth flying.

---

## 6. COMPLETION REPORT

When the child is done, report:
1. What was changed (file + line numbers)
2. How to test (same as §5)
3. Any tradeoffs or decisions made

---

**END OF PROMPT**
