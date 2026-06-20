# Completion Report — Brief #U1: Understanding Mode Conveyor Belt Fix

**Date:** June 18, 2026
**Child:** Claude Opus 4.8 (child instance)
**Brief:** CHILD_BRIEF_U1_UNDERSTANDING_CONVEYOR_FIX.md

## FILES CHANGED
- `understanding.py` — ONLY file changed. No other file touched. app.py already gated ESC with `and not umode.active`, so no second-file edit was needed.

## ROOT CAUSE (confirmed)
The parent's diagnosis (Brief #U1 §4) was correct. `abs(self.focus - i)` (in both the sort key and `d`) made a passed sign look identical to an approaching one — the conveyor belt. No culling existed. Entry overflowed because `CLOSEUP_FILL=1.30` and `focus=0` placed sign 0 at `d=0` (max size). One refinement: size/blur/fog were all three driven by `d`, and size was a symmetric Gaussian peaking at `d=0` — so the curve was replaced with a monotonic perspective law, not just the input.

## NEW SIGNED-DISTANCE MODEL
Each sign has `s_i = i - f`. Signs with `s_i >= 0` are drawn (size/blur/fog all monotonic in s); signs with `s_i < 0` are culled entirely — that single rule kills the conveyor belt. The car starts at `f = -1` so sign 0 sits at `s = 1` (fits-with-margin); driving forward raises f, growing the front sign past the screen and revealing/sharpening the next. Reverse falls out for free; exit happens only by reversing past sign 0 by 1/3 of a spacing.

## ENTRY-FOCUS CHOICE
`ENTRY_FOCUS = -1.0`. The "fits" framing lives at `s = 1`, so placing the car one full spacing behind sign 0 makes `s_0 = 1` on entry — whole sign, tiny margin, no jump on the first forward click.

## NEW/CHANGED CONSTANTS
- `ENTRY_FOCUS = -1.0`, `FITS_S = 1.0`, `EXIT_THRESHOLD = 1/3 ≈ 0.333`
- `FITS_FILL = 0.90`, `FAR_FILL = 0.42` (kept), `NEAR_K = 9.0` (derived), `PAN_OVERFILL = 0.55`
- `BLUR_PER_S = 4.0`, `FOG_PER_S = 0.34`, `FOG_MAX = 0.92` (kept)
- Removed: `CLOSEUP_FILL`, `SIZE_FALLOFF`, `PEAK_BLUR`, `BLUR_PER_D`, `FOG_PER_D`
- Blur-rung mapping unchanged (`_rung_for_blur`, `BLUR_RUNGS=10`, `BLUR_STEP=1.2`).

## DISAGREEMENTS WITH BRIEF (file won)
- (a) app.py already blocks ESC-quit while `umode.active`, so making ESC inert needed only deleting the in-file `ESC→close()` — no app.py edit.
- (b) Size was a Gaussian, not a plain falloff; replaced the whole curve, not just its input.

## REQUEST TO PARENT
None. The fix fit entirely in understanding.py using existing render.py signatures.

## DEEPSEEK TODOs (pure by-eye tuning after test flight)
- `FITS_FILL` — raise toward 0.95 if the entry margin feels too wide, lower toward 0.85 if anything clips.
- `PAN_OVERFILL` — raise for more dramatic overflow as you reach a sign.
- `FOG_PER_S` / `BLUR_PER_S` — raise if the next-sign-behind still competes; lower if it's too dark/blurry to sense as "a presence."
- Confirm with Nir whether CTRL should yank to engineer (current) or just reveal-in-place.

## FLAG FOR NIR
Holding CTRL now drives the car forward through signs 1 and 2 — they grow, you pass them, they vanish — until you reach the engineer. Releasing CTRL leaves you parked at the engineer (it doesn't drive you back). This is consistent with "forward = deeper" but it's a fast trip. If you'd rather CTRL only un-blur the engineer sign in place without flying the car, that's a small change — tell the child/parent.
