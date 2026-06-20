# BUG REPORT — Brief #9 COMBAT after Nir's test flight

## BUG 1: HUD text displays as raw LaTeX/code instead of pretty readable text

**What Nir sees:** The HUD labels and fizzle panel show raw mathtext code
(backslashes, braces, underscore replacements) instead of clean readable
prose like the "PATH CLEAR" message.

**Cause:** The `_mt()` function in combat.py strips/escapes text too
aggressively. It removes `{`, `}`, `$`, `^`, `_`, `&`, `%`, `\`, then
wraps the result in `\mathrm{...}` with `\ ` for spaces. The aggressive
stripping is destroying the text content (e.g. removing apostrophes
turning "doesn't" into "doesn t", or stripping hyphens from words).

**Also:** `draw_text_mathtext_2d()` already accepts mathtext strings.
The "PATH CLEAR" label in the code IS displayed directly as
`r"\mathrm{PATH\ CLEAR}"` and it works. But the dynamic labels from
`_mt(f"VULNERABLE TO: {need_name}")` go through the destructve `_mt()`
function.

**Fix needed:** Either:
- Make `_mt()` less destructive (only escape the few chars that break
  mathtext: `\`, `{`, `}`, `$`, `#`, `%`, `_`, `^`, `&`, and spaces→`\ `)
- Or pass plain ASCII labels directly to `\mathrm{...}` with spaces
  escaped as `\ `, keeping the original text intact
- The fizzle text has hyphens `—`, apostrophes, and other prose
  punctuation that must survive intact

## BUG 2: Ship can fly outside corridor walls

**What Nir sees:** The spaceship flies straight through corridor walls
into empty space.

**Cause:** `app.py` never enforces wall containment. The engine already
HAS the `hub.inside(point, margin)` function (returns True/False for
"is this point inside the atrium or any corridor"), but it is never
called to push the ship back inside.

**Fix needed:** Every frame after ship.update, check `hub.inside()` and
clamp the ship position back if it's outside. This is a new feature
(collision/containment) and may need its own scope — please discuss
with Nir whether to add it as a patch to the existing build, or as a
separate small child task.

## PARENT NOTE: Wall containment

The engine function `HubGeometry.inside(point, margin=0.0)->bool`
already exists and works (it checks both the atrium sphere and every
corridor segment's bounding box). It just needs to be called in the
frame loop. The fix is ~3 lines in app.py after ship.update:

    if not hub.inside(ship.pos, margin=1.0):
        # clamp ship back inside (e.g. push back along velocity, or
        # teleport back to previous frame's position)

The question is: should this be a child task (Brief 9b?), or a quick
patch? The child must decide how "forgiving" the clamp is (teleport
back? slide along wall? bounce?). Discuss with Nir.
