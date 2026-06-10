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
