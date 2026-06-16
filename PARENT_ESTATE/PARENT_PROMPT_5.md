# 🚀 PARENT 5 PROMPT — THE TRUTH + WHAT TO BUILD

> **TO:** Claude Opus 4.8 — You are PARENT #5.
> **FROM:** Nir (strulovitz) + DeepSeek V4 Pro (OpenCode)
> **PASTE THIS ENTIRE DOCUMENT** into a fresh Claude conversation.

---

## 0. THE TRUTH (read this first — no sugarcoating)

Everyone on this project — parents, children, and DeepSeek — told Nir things were built that were never built. We nodded and said "ok" while the screen showed nothing that Nir asked for.

**WHAT NIR WAS TOLD HE HAS:** "Understanding Mode shows kindergarten mixing — each part of the equation has a different colored BACKGROUND, so you can see which concept is which."

**WHAT ACTUALLY EXISTS ON SCREEN RIGHT NOW:** White text on a dark background. Every single part of every equation looks identical. There are ZERO colored backdrops. The text color is fine — the problem is that the BACKDROPS are completely missing.

**CONCRETE EXAMPLE — what robot 3 (Faraday) SHOULD look like in Understanding Mode:**

The equation $\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$ should appear as three side-by-side segments:
```
┌─────────────┐     ┌──────────────────┐
│   ∇ × E     │  =  │    -∂B/∂t        │
│ (RED bg)    │     │ (PURPLE bg)      │
└─────────────┘     └──────────────────┘
```
- "∇×E" → RED backdrop rectangle (field_e primary)
- "=" → NO backdrop, just white text (NEUTRAL)
- "-∂B/∂t" → PURPLE backdrop rectangle (coupling = field_e + field_b blend)

**What actually shows right now:** three white text pieces on a dark background. No red. No purple. Just white. Indistinguishable.

**WHAT EXISTS IN DATA (parsed correctly, never used):**
- `Segment(latex, ledger_key)` objects ✅
- `palette.tint(key)` → RGBA backdrop color (e.g. red, blue, purple) ✅  
- `palette.text_color_on(key)` → readable text color on that backdrop ✅

**WHAT WAS NEVER BUILT:**
- Drawing a colored rectangle behind a math expression
- Matching inline $...$ math to its SEGMENTS entry
- Any renderer that calls `palette.tint()` or `palette.text_color_on()`

Nir discovered today that the kindergarten mixing he designed months ago has never appeared on screen. Do not repeat this.

---

## 1. THE GAME — LAW (from PARENT_HANDOFF_V3.md §1)

DESCENT QED is a 6-DOF flying game themed around MATHEMATICAL PROOF.
A COUPLE pilots a single SPACESHIP through CORRIDORS to rescue HOSTAGES.
ROBOTS block the way. Each requires a SPECIFIC MATHEMATICIAN'S TECHNIQUE to destroy.

**THE KINDERGARTEN MIXING:**
- Equations are split into SEGMENTS — each segment has a LEDGER KEY
- PRIMARY keys = basic concepts (red = field_e, blue = field_b)
- BLEND keys = combinations (purple = coupling = field_e + field_b)
- NEUTRAL = glue like `=` signs — no color backdrop
- Each segment gets a COLORED BACKDROP (`palette.tint(key)`) with readable text on top (`palette.text_color_on(key)`)

This is the **core educational visual**. Without it, the game is meaningless.

---

## 2. WHAT IS ALREADY BUILT

### World Tier (complete):
| Module | File | Status |
|--------|------|--------|
| content_parser | `content_parser.py` | ✅ Parses SEGMENTS + ledger |
| palette | `palette.py` | ✅ `tint()`, `text_color_on()`, `eye()` |
| render | `render.py` | ✅ Ship, TexCache, quat helpers, fog, billboards, render_rich |
| robots | `robots.py` | ✅ Robot class (hull, scanner, hologram portrait, explosion) |
| corridor_builder | `corridor_builder.py` | ✅ Bent corridors, stations, cavern |
| hub_builder | `hub_builder.py` | ✅ Atrium + Fibonacci doors + inside() |
| level_parser | `level_parser.py` | ✅ Level manifests |
| app | `app.py` | ✅ Main loop, canonical frame order |

### Gameplay Tier (complete):
| Brief | What | Status |
|-------|------|--------|
| #9 Combat | Fire missiles, match/fizzle, projectiles | ✅ |
| #10 Arsenal | Per-corridor weapons, face panel, Xbox/mouse | ✅ |
| #11 Understanding | 4-layer panels **but WRONG** — no colors | 🔴 NEEDS REBUILD |
| #12 Hostages | Two 3D humanoid figures | ✅ |
| #13 Game State | Rescue, WIN-ONLY, level progression | ✅ |
| #15 Cockpit | Descent-style polygon HUD | ✅ |

---

## 3. THE DATA THAT ALREADY EXISTS (verbatim)

### Segment dataclass (content_parser.py:38):
```python
@dataclass
class Segment:
    latex: str                          # mathtext, surrounding $...$ stripped
    ledger_key: str                     # a ledger key, or "NEUTRAL"
    exemplify: list = field(default_factory=list)  # list[ValueArc]; [] for SEGMENTS
```

### RobotData.segments (content_parser.py:51):
```python
segments: list  # list[Segment], in file order
```

### palette.tint() (palette.py:182):
```python
def tint(self, key: str) -> tuple[float, float, float, float]:
    """RGBA backdrop tint for an equation segment.
    NEUTRAL -> (0,0,0,0): caller draws NO backdrop quad.
    PRIMARY -> that primary's tint at BACKDROP_BASE_ALPHA.
    BLEND   -> blended tint of its two parents at BACKDROP_BASE_ALPHA."""
```

### palette.text_color_on() (palette.py:195):
```python
def text_color_on(self, key: str) -> tuple[float, float, float]:
    """Black text on LIGHT tints, white text on dark tints (by luminance).
    NEUTRAL -> white (text floats on the dark world)."""
```

### Example SEGMENTS from maxwell.txt robot 3 (Faraday):
```
SEGMENTS {
  $\nabla \times \mathbf{E}$                              | field_e
  $=$                                                     | NEUTRAL
  $-\frac{\partial \mathbf{B}}{\partial t}$               | coupling
}
```
Three segments:
- "∇×E" → red backdrop (field_e primary)
- "=" → no backdrop (NEUTRAL)
- "-∂B/∂t" → purple backdrop (coupling = field_e + field_b blend)

---

## 4. WHAT NIR WANTS — THE REAL UNDERSTANDING MODE

When the player presses U near a robot, they see the 4-layer depth panels:
1. MATHEMATICIAN (deepest)
2. PHYSICIST (middle)
3. BIOLOGIST (shallow)
4. ENGINEER (front, CTRL-locked)

Each layer shows the EXPLAIN text (e.g., `EXPLAIN_MATHEMATICIAN`). **Within each layer's text, inline $...$ math expressions should be matched against the robot's SEGMENTS data and rendered with their corresponding ledger-colored backdrops.**

### Visual specification:
- **Prose** (English text): white or light grey, NO backdrop
- **Inline math** ($...$): rendered with a **colored backdrop rectangle** behind it
  - Backdrop color = `palette.tint(segment.ledger_key)` (red, blue, purple, etc.)
  - Text color = `palette.text_color_on(segment.ledger_key)` (black on light, white on dark)
  - NEUTRAL segments (like `=`) get NO backdrop
- **Value arcs** ([[ expr | value ]]): arc + value rendered as before, but with appropriate segment color
- **Multi-line wrapping**: wrapped lines should still show correct per-segment colors
- **Depth blur**: blur applies to the entire layer, including colored backdrops
- **Pan/scroll**: works exactly as it does now

### Matching logic:
For each inline `$...$` expression in the EXPLAIN text, look it up in the robot's SEGMENTS list. The match should be by the LaTeX content (the text between `$` signs). If a match is found, use that segment's `ledger_key` for coloring. If no match, use NEUTRAL (no backdrop).

### Current (broken) Understanding Mode code (understanding.py:124-129):
```python
render.render_rich(cache, title, px, py - fs*1.6,
                    color=(0.55,0.7,0.95), fontsize=max(10,int(fs*0.8)),
                    alpha=alpha)
render.render_rich(cache, text, px, py,
                    color=(0.95,0.96,0.98), fontsize=max(10,fs),
                    scale=1.0, alpha=alpha, blur=blur)
```
This draws white text on the dark background. The text is readable — the color is NOT the problem. The problem is that `render_rich` has no concept of segments, no concept of backdrops, and never calls `palette.tint()`. It can only draw text in ONE flat color with no backdrop rectangles at all.

### Current render_rich (render.py:791):
```python
def render_rich(cache, text, x, y, color=(0.95, 0.96, 0.98),
                fontsize=15, scale=1.0, alpha=1.0, blur=0.0):
```
Single-color text renderer. No segments. No backdrops. No palette.

---

## 5. WHAT YOU MUST BUILD

### A. A new colored-segment rich text renderer

Either:
- Extend `render_rich` to accept `segments: list[Segment]` and `palette` parameters, OR
- Write a NEW function (e.g., `render_rich_colored`) that takes segments + palette

The renderer must:
1. Parse the text for `$...$` math spans (same tokenizer as render_rich)
2. For each math span, look up its LaTeX in the robot's `segments` list
3. Draw a colored backdrop rectangle behind matched spans using `palette.tint(key)`
4. Draw the math text on top using `palette.text_color_on(key)`
5. Prose outside `$...$` gets no backdrop, rendered in white/light grey
6. Multi-line wrapping must preserve per-line segment colors
7. Support alpha, blur, and scale (same as current render_rich)
8. Cache textures per (text, segments, colors, blur) key

### B. Wire it into Understanding Mode

Modify `understanding.py`:
- Pass `self.robot.segments` and the corridor's `ColorLedger` to the new renderer
- Each of the 4 layers uses the SAME segments data (coloring comes from the robot's equation, not the layer)

### C. Test fixture

Use the Maxwell corridor (`maxwell.txt`) which has the richest SEGMENTS data:
- Robot 3 (Faraday): segments with field_e, NEUTRAL, coupling keys
- Robot 5 (Maxwell): segments with field_b, NEUTRAL, coupling keys

---

## 6. ENGINE CANON (obey strictly)

### Frame order (PARENT_HANDOFF_V3.md §2):
```
 1. glClear
 2. ship.update(dt, keys)
 3. ship.apply_view()
 4. render.set_fog(...)
 5. cr, cu
 6. hub.update(dt, ship.pos)
 7. hub.draw_world(cr, cu, tc)       # QUEUES walls only
 8. render.flush_walls(ship.pos)     # EXACTLY ONCE
 9. hub.draw_robots(cr, cu, tc)
10. hub.draw_labels(cr, cu, tc)
11. combat HUD + overlays (begin_2d/end_2d)
12. pygame.display.flip()
```

### CARDINAL FLUSH TRAP:
`flush_walls` called EXACTLY ONCE per frame, after `draw_world`, before robots.
Omit/duplicate → BLACK SCREEN.

### Mathtext-only rule:
`\frac`, `\sum`, `\geq` ALLOWED. `\tfrac`, `\dfrac`, `\binom`, `\underbrace` FORBIDDEN.

---

## 7. SCOPE FENCE — What NOT to build

- Do NOT touch the defeat plaque (corridor_builder.py:_draw_plaques) — that's a SEPARATE future task
- Do NOT change how robots look
- Do NOT change the cockpit, combat, game state, or hostages
- Do NOT touch corridor `.txt` files or the parser
- Do NOT remove or change `render_rich` — the new renderer is ADDITIVE
- Do NOT break the 4-layer depth system (blur, pan, CTRL unlock must still work)

---

## 8. COMPLETION REPORT

When done, the child must report:
1. What functions were added/changed (file + line numbers)
2. How to test: `python app.py`, fly into Maxwell corridor, press U near robot 3 (Faraday), verify:
   - "∇×E" has RED backdrop
   - "=" has NO backdrop (NEUTRAL)
   - "-∂B/∂t" has PURPLE backdrop
   - Prose between math is plain white
   - All 4 layers (mathematician/physicist/biologist/engineer) show the SAME segment colors
   - Blur, pan, depth, CTRL unlock all still work
3. Any decisions or tradeoffs made

---

## 9. HOW TO RUN

```
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Controls: WASD/RF move, arrows rotate, Q/E roll, SPACE fire, U = Understanding Mode, ESC quit.

---

**END OF PROMPT — Nir will paste this to Claude Opus 4.8 as Parent #5.**
