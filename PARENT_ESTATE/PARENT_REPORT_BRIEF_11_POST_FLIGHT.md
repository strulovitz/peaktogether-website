# PARENT REPORT — Brief #11 Post-Flight (all changes after child code landed)

## 1. INITIAL FIXES (DeepSeek corrected child's code before committing)

The child's code had three structural errors that were fixed during
integration:

A) **gamepad.py** — the brief demanded the VERBATIM Bible GamepadManager
   class (with name-based detection, 60-frame calibration, radial/scalar
   deadzones). The child rebuilt a stripped version without calibration.
   DeepSeek used the canonical class from the working Bible code instead.

B) **RobotData access** — `combat.blocking_robot(hub)` returns a `Robot`
   object, but `understanding.py` accesses `self.robot.explain` which
   requires a `RobotData`. The child wrote `umode.open(combat.blocking_robot(hub))`.
   DeepSeek changed to: `robot = combat.blocking_robot(hub); umode.open(robot._robot_data)`.

C) **World suspend gating** — when `umode.active`, the child gated world
   updates but NOT 3D draws. The 3D draw calls use `cr/cu` which are only
   set inside the gated update block. This would crash. DeepSeek added
   `if not umode.active:` around all 3D draw calls as well.

---

## 2. BUGS FIXED AFTER NIR'S FLIGHT (10 commits)

### Bug 1 — `combat.blocking_robot` AttributeError
- Child wrote: `combat.blocking_robot(hub)` (module-level call)
- Fixed: `combat.Combat.blocking_robot(hub)` (static method)
- Commit: `648f6de`

### Bug 2 — Scroll wheel direction reversed
- Scroll UP should go forward (mathematician→physicist→biologist→engineer)
- Old: `self.target -= ev.y * DEPTH_SPEED_WHEEL`
- Fixed: `self.target += ev.y * DEPTH_SPEED_WHEEL`
- Commit: `718faea`

### Bug 3 — Value arcs opened upward (smile) instead of downward (frown)
- Old formula: `py = arc_top + arc_height * (1.0 - 4.0 * (t - 0.5)**2)` — smile ∪
- Fixed: `py = arc_top + arc_height * (4.0 * (t - 0.5)**2)` — arch/frown ∩
- Commit: `2b98136`

### Bug 4 — CTRL only worked when already scrolled to engineer panel
- Old: CTRL only unblurred engineer IF focus was already near it
- Fixed: CTRL now SNAPS focus to engineer (`self.target = 3`) from ANY layer
- Commit: `2ae5fa5`

### Bug 5 — CTRL detection too narrow
- Old: only checked `keys[K_LCTRL] or keys[K_RCTRL]`
- Fixed: added `pygame.key.get_mods() & KMOD_CTRL` as third check
- Commit: `568f19c`

### Bug 6 — Arcs too high, covering value numbers
- Old: `arc_top = arc_band * 0.45`
- Fixed: `arc_top = arc_band * 0.75` (lowered twice at Nir's request)
- Commits: `5c01c3b`, `0a5e61d`

### Bug 7 — Xbox right-stick axis indices wrong
- Nir's debug line showed: a2=left/right, a3=forward/back
- Old: XBOX_RSTICK_X=3, XBOX_RSTICK_Y=4
- Fixed: XBOX_RSTICK_X=2, XBOX_RSTICK_Y=3
- Commits: `c0d58f5`, `450779c`

### Bug 8 — Xbox right-stick directions inverted
- Nir requested left/right and up/down swapped
- Fixed: changed `pan_x += rx ...` to `pan_x -= rx ...` (same for y)
- Commit: `004d8f7`

---

## 3. JOYSTICK — NOT YET WIRED FOR SHIP FLIGHT

The `GamepadManager` class in `gamepad.py` already has a `pilot_command()`
method that reads the T.16000M joystick (pitch/yaw/roll/thrust). But
`app.py` only feeds keyboard keys to `ship.update(dt, keys)` — nobody
calls `gamepads.pilot_command()` and adds its output to the ship controls.

This IS working code (from the Bible, already in gamepad.py). It just
needs to be WIRED in app.py:

    # In the frame loop, near ship.update:
    if not umode.active:
        gp = gamepads.pilot_command() if gamepads else None
        # gp is a dict: {'pitch','yaw','roll','thrust_xyz'} or None
        # Add gp values to keyboard inputs before calling ship.update

The exact wiring was done in the old math-flyer Bible code — copy the
pattern from there.

---

## 4. SUMMARY OF ALL CHANGED FILES

| File | Changes |
|------|---------|
| `gamepad.py` | Verbatim Bible class, axis indices X=2/Y=3 |
| `understanding.py` | Scroll direction, CTRL jump+detection, Xbox swap+invert |
| `render.py` | Arc formula flip (smile→frown), arc_top 0.45→0.75 |
| `app.py` | RobotData access fix, world suspend gating, blocking_robot call |

**Untouched:** combat.py, hub_builder.py, content_parser.py, robots.py

## 5. NIR'S CONFIRMED WORKING BEHAVIOR

- U near robot → 4 depth panels (mathematician/physicist/biologist/engineer)
- Scroll UP = deeper, scroll DOWN = back/shallower; scroll past front = exit
- Mouse pan works
- CTRL from ANY layer jumps to engineer, unlocks value-arcs
- Value arcs are downward-opening arches with visible value numbers
- Xbox right stick pans (axis 2=left/right, axis 3=forward/back, inverted to taste)
- ESC exits cleanly
- T.16000M joystick: code exists but not yet wired to ship flight
