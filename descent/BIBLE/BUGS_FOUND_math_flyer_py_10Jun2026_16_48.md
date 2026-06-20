# 🐛 Bugs Found in Bible (Claude Fable's math_flyer.py)

**For:** Claude Fable — for awareness before next batch of demos  
**Found by:** DeepSeek V4 Pro (running inside OpenCode, Nir's Windows PC)  
**Date:** 2026-06-10

---

## Bug #1: `\tfrac` crashes matplotlib mathtext (LaTeX rendering)

### Problem
The `overlay_latex()` method in `HarmonicSeriesPage` uses `\tfrac` for small fractions:

```python
terms = (r"1 + \tfrac{1}{2} + \tfrac{1}{3} + \tfrac{1}{4} + "
         r"\cdots + \tfrac{1}{%d}" % N)
```

### Crash
```
ValueError: Unknown symbol: \tfrac, found '\'
```

### Why
`\tfrac` is an **AMSMath** command (`\usepackage{amsmath}`). matplotlib's built-in `mathtext` parser (used via `matplotlib.use("Agg")`) does **not** have a full LaTeX installation — it only supports standard LaTeX math commands like `\frac`, `\sum`, `\int`, etc.

AMSMath commands (`\tfrac`, `\dfrac`, `\binom`, etc.) require either:
- A full LaTeX installation on the user's machine + `matplotlib.rcParams['text.usetex'] = True`, **or**
- Using the standard `\frac` instead

### Solution
Replaced all `\tfrac` with `\frac` (standard LaTeX, universally supported):

```python
terms = (r"1 + \frac{1}{2} + \frac{1}{3} + \frac{1}{4} + "
         r"\cdots + \frac{1}{%d}" % N)
```

The visual difference is minimal (slightly larger fraction) and the program now runs.

---

## Bug #2: Texture index error in render() — `t[0][1]` should be `t[1]`

### Problem
In `App.render()`, the LaTeX panel layout code iterates over `latex_items` which is a list of `((tid, w, h), latex_string)` tuples. The loop variable `t` is the `(tid, w, h)` texture tuple:

```python
latex_items = [(self.tex.latex(s, fs), s) for s, fs in page.overlay_latex()]
if latex_items:
    pw = max(t[0][1] for t, _ in latex_items) * 0.5 + 28   # BUG
    ph = sum(t[0][2] * 0.5 + 10 for t, _ in latex_items) + 18  # BUG
```

### Crash
```
IndexError: invalid index to scalar variable
```

### Why
`t = (tid, w, h)` — a 3-tuple. `t[0]` is the integer `tid`. Trying `t[0][1]` indexes into an integer, which fails.

Note: The *lower* loop in the same block correctly uses `t[2]` (height):
```python
for t, _ in latex_items:
    draw_texture(t, 24, ty, scale=0.5)
    ty += t[2] * 0.5 + 10     # correct: t[2] = height
```

### Solution
Replace `t[0][1]` with `t[1]` (width) and `t[0][2]` with `t[2]` (height):

```python
pw = max(t[1] for t, _ in latex_items) * 0.5 + 28
ph = sum(t[2] * 0.5 + 10 for t, _ in latex_items) + 18
```

### Note
This bug was masked by Bug #1 — the `\tfrac` crash happened *before* this code was reached. It surfaced immediately after Bug #1 was fixed.

---

## Workflow Note (for Claude Fable)

- You (Claude Fable) = architect, providing the "Bible" skeleton
- DeepSeek V4 Pro = builder, fills in details on a COPY, never touches the Bible
- Bugs found in the Bible → reported here → Nir shows you → you fix the Bible for next batch
- The working copy is `math_flyer.py` in repo root; Bible is `BIBLE/math_flyer.py`

---

## What was built on top (beyond these fixes)

- Full `GamepadManager` with T.16000M joystick (pilot) + Xbox 360 controller (manipulator) using pygame.joystick
- Startup calibration (60-frame sampling, drift subtraction)
- Radial deadzones for sticks (0.12), scalar deadzones for twist/throttle (0.08)
- Axis mappings verified from Nir's hardware (Anniversary C++ project)
- Keyboard/mouse and controllers work simultaneously (additive)
- Error logging: crashes append to `math_flyer.log` with timestamp
