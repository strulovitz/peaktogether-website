# PARENT PROMPT — Brief #9 Post-Flight: Two Architecture Issues

## ISSUE 1: No "plain English text" renderer exists in the engine

**What happened:**
The combat child needed to show English labels on the HUD (like
"VULNERABLE TO: Gauss" and fizzle prose). The engine only has
`draw_text_mathtext_2d()` which expects LaTeX math syntax. So the
child wrote a hack function `_mt()` that manually escapes/processes
plain English into `\mathrm{...}` syntax.

This function was too aggressive (deleted apostrophes, hyphens, etc.),
causing the HUD to look broken. The child submitted a fix, but the fix
is still a per-child band-aid.

**The real problem:**
Every future child who needs to show English words on screen (HUD,
panels, menus, briefing screens) will have to REINVENT their own
text-escape hack. This is fragile, inconsistent, and a waste of child
time.

**What the engine needs:**
A proper `draw_plain_text_2d(cache, text, x, y, ...)` function in
render.py that accepts normal English strings. It handles escaping
internally once, correctly, for all children forever.

**Parent's action:**
Write a small brief or parent-authored patch to add this to render.py.
The function signature should mirror `draw_text_mathtext_2d` but
accept a plain (non-LaTeX) string. All special char escaping happens
inside the function. Children then call this instead of reinventing
`_mt()`.

After this is added, update Brief #9's completion report: remove
`_mt()` from combat.py and call the new engine function instead.

---

## ISSUE 2: Ship flies through corridor walls — containment missing

**What happened:**
Nir flew the Maxwell corridor. The ship passes straight through the
walls into empty space. The child says this is "out of scope" and
recommends a 3-line demo patch in app.py.

**Why the child's recommendation is WRONG:**
Walls-that-block-you is NOT a per-demo feature. It is a PERMANENT
property of every corridor ever built. The engine already has
`HubGeometry.inside(point, margin)` — it knows whether you're inside
the world. What's missing is: the corridor/hub should actively KEEP
the ship inside.

If we "patch" app.py for this demo, we will have to do it AGAIN for
every Wikipedia corridor. That's the kind of ad-hoc hack that breaks
the whole modular architecture.

**What the engine needs:**
The corridor and/or hub should own ship containment. Options for the
parent to decide:

Option A — CorridorGeometry gains:   .clamp_ship(ship_pos, margin) -> new_pos
Option B — HubGeometry gains:        .clamp_ship(ship_pos, margin) -> new_pos
Option C — A new tiny "physics" module that owns containment

The key principle: after this is built, EVERY corridor in EVERY level
automatically blocks the ship. No per-demo patches. The app.py frame
loop calls ONE function that already exists.

**The gentle-design behavior:**
Nir requires no punishment, no failure, no confusing physics. The
simplest correct behavior: if the ship position is outside the world,
teleport it back to the last position that was inside. Like an
invisible soft cushion. No momentum math, no bouncing.

**Parent's action:**
Decide where containment lives (module), write the brief or parent
patch, and ensure clip_ship/clamp is called once per frame. This
should be a small, focused task — NOT a full Brief #10-sized thing.

---

## SUMMARY FOR PARENT

Both issues are the same root cause: **engine infrastructure that
every future corridor/demo will need, but doesn't exist yet.** The
children are inventing per-module hacks because the engine is missing
these two small but universal functions:

  1. render.draw_plain_text_2d(...)     — show English words on HUD
  2. hub.clamp_ship(ship_pos) -> pos    — walls block the ship

Build them once in the engine. Then all children use them forever.
No more hacks.
