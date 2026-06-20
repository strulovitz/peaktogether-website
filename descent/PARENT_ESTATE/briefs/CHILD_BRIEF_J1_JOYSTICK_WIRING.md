================================================================================
DESCENT QED — CHILD BRIEF #J1: T.16000M JOYSTICK (TRUE ANALOG, ADDITIVE)
Module concern: wire the EXISTING gamepad pilot_command() into ship flight, as
TRUE ANALOG (proportional), ADDITIVE to keyboard. NOT on/off.
You build ONE concern. Do not creep. Do not touch unrelated systems.
================================================================================

## 0. WHO YOU ARE, WHO ELSE EXISTS
You are a fresh Claude Opus 4.8 child with NO memory of prior chats. You write
ONE concern, fully, at full Opus depth. Do NOT defer your judgment.
- NIR — the human, your COURIER and TESTER. Not a programmer. He runs the game
  with a real Thrustmaster T.16000M flight stick plugged in and reports what he
  FEELS/SEES. Be warm, exact, tell him precisely what to do and watch for.
- DEEPSEEK V4 Pro — agentic builder on Nir's machine, full repo + internet.
  Commits your code, runs probes. Reliable for MECHANICAL tasks, NOT wise about
  INTENT — he can "fix the headache and ruin the liver." Use him to FETCH FACTS
  / RUN PROBES, never to decide design. If he contradicts this brief or Nir,
  this brief and Nir win.
- THE PARENT (architect) wrote this brief and owns architecture, no memory of
  your chat. If you need something a module doesn't expose, REQUEST it in your
  Completion Report — do NOT reach into unrelated modules.

## 1. FRESH-CHAT GATE — DO THIS FIRST, BEFORE ANY CODE
Do NOT hallucinate APIs. Your FIRST action: ask Nir (relayed to DeepSeek) to
paste you the COMPLETE, VERBATIM, CURRENT contents of:
  (1) render.py — the FULL Ship class (you will ADD one method to it), plus the
      quaternion helpers it uses: quat_rotate, quat_mul, quat_normalize,
      quat_from_axis_angle (so you reuse them, never reinvent quat math).
  (2) app.py — the frame-loop region from `keys = pygame.key.get_pressed()`
      through `ship.update(...)`, `containment.resolve(...)`, `ship.apply_view()`
      (you add ~2-4 lines here). Also the line where `gamepads` is created.
  (3) gamepad.py — the FULL pilot_command() method AND its helpers
      (_calibrate, _radial_deadzone, _scalar_deadzone, _clamp1, _detect, the
      AXIS_* constants, and how pilot_joy is assigned). You must SEE the exact
      returned dict keys/types and confirm sign conventions (which way is
      "pitch up", which way is "+thrust forward").
PASTED FILES ARE LAW. If a pasted file disagrees with anything below, the FILE
wins, and you tell Nir you spotted it.

## 2. THE GAME — THIS IS LAW (so you never drift)
DESCENT QED: a no-fail, WIN-ONLY 6-DOF flying game. A couple shares one ship,
descends a rock mine corridor to RESCUE HOSTAGES. ROBOTS block the corridor;
each is destroyed by firing the correct mathematician-missile (player RECOGNIZES
the robot's hologram FACE and selects the matching mathematician in the weapon
panel). Wrong shot = harmless 6s fizzle, no penalty. No death, no timer.

THE PRIME LAW — MATHEMATICS-BLINDNESS: the engine NEVER interprets math meaning;
it only matches opaque IDs; color flows only through palette.py via opaque keys.
YOUR concern is pure INPUT->MOTION (flight control). It contains ZERO math
meaning and ZERO color logic. Perfectly Prime-Law-safe by nature.

## 3. THE EXACT PROBLEM (confirmed by Nir, June 17 2026)
The game flies on KEYBOARD only. Nir has a real T.16000M flight stick plugged
in. The reading code ALREADY EXISTS (gamepad.GamepadManager.pilot_command()) but
is CALLED NOWHERE. Your job: wire it into ship flight.

NIR'S RULING (locked, non-negotiable): the stick must work at FULL ANALOG
functionality — PROPORTIONAL, smooth, NOT on/off. A half-tilt = half the rate.
And it is ADDITIVE to the keyboard: keyboard and stick work SIMULTANEOUSLY (a
player can nudge with both at once). Do NOT make it one-or-the-other.

WHY THIS IS NOT TRIVIAL (respect it): the existing Ship.update(dt, keys) reads a
pygame get_pressed() array — values are 0/1 ONLY. You CANNOT "press a key at
50%." Worse, Ship.update NORMALIZES the thrust vector (thrust /= norm), which
would DESTROY analog magnitude (any nonzero tilt becomes full-speed). So you must
NOT route analog values through the digital key path. You add a SEPARATE ANALOG
path that preserves proportional magnitude. Also: a previous landmine on this
project was an Xbox TRIGGER misread as "fire," auto-killing robot #1 at startup.
Lesson: input wiring hides traps. Probe before you trust (see §6).

## 4. FACTS YOU LEAN ON (verify against the pastes)

### Ship (render.py) — current, KEYBOARD path:
    MAX_SPEED=18.0  ACCEL=5.0  BOOST=3.0
    PITCH_YAW=radians(95)  ROLL_SPEED=radians(140)
    update(dt, keys):
        pitch = (keys[K_UP]-keys[K_DOWN]) * PITCH_YAW * dt   # rotate_local [1,0,0]
        yaw   = (keys[K_LEFT]-keys[K_RIGHT]) * PITCH_YAW * dt # rotate_local [0,1,0]
        roll  = (keys[K_q]-keys[K_e]) * ROLL_SPEED * dt       # rotate_local [0,0,1]
        thrust = [ keys[K_d]-keys[K_a], keys[K_r]-keys[K_f], keys[K_s]-keys[K_w] ]
        thrust /= norm(thrust)   # <-- NORMALIZE (digital). DO NOT route analog here.
        boost = BOOST if (LSHIFT or RSHIFT) else 1.0
        target = quat_rotate(q, thrust) * MAX_SPEED * boost
        vel += (target - vel) * min(1, ACCEL*dt)
        pos += vel * dt
    Mutates: .pos .vel .q.  Reuses rotate_local() + quat helpers.

### pilot_command() (gamepad.py) — returns dict OR None:
    {
      'pitch': float -1..+1,   # already deadzoned + clamped
      'yaw':   float -1..+1,
      'roll':  float -1..+1,
      'thrust_xyz': (x, y, z) each -1..+1,  # z is forward axis; snippet says
                                            # throttle slider -> thrust_xyz[2] = -t
    }
    Returns None during the first ~60 calibration frames OR if no T.16000M.
    *** It ALREADY applies its own deadzones (radial 0.12 stick, scalar 0.08
    twist/throttle) and clamp. DO NOT re-apply deadzones. ***
    You MUST confirm from the paste the SIGN conventions and that thrust_xyz maps
    to the SAME ship-local axes the keyboard uses: keyboard thrust is
    [x = d-a (right+), y = r-f (up+), z = s-w (forward is -Z so s = +z = back?)].
    Read the keyboard mapping CAREFULLY and make the stick AGREE with it (stick
    push-forward should move the ship the SAME way s/w move it). If a sign is
    inverted in testing, flip THAT axis in your analog method (and say so).

### app.py loop (current, after Brief #C1):
    keys = pygame.key.get_pressed()
    if not umode.active:
        prev_pos = ship.pos.copy()
        ship.update(dt, keys)
        containment.resolve(ship, hub, prev_pos)
        ship.apply_view()
    gamepads = GamepadManager() (already instantiated; may be None on exception)

## 5. WHAT TO BUILD — DESIGN

### 5.1 Add an ANALOG method to Ship (render.py)
Add ONE new method to the Ship class (do NOT change update()'s keyboard path,
do NOT change tunables). Suggested:

    def apply_pilot(self, dt, cmd):
        """Analog 6-DOF input, ADDITIVE to keyboard. cmd is the dict from
        gamepad.pilot_command(): pitch/yaw/roll in -1..1, thrust_xyz in -1..1
        each. Proportional: half-tilt = half-rate. Deadzones ALREADY applied
        upstream — do not re-apply."""
        if cmd is None:
            return
        # ROTATION: same axes/rates as the keyboard, scaled by the analog value.
        self.rotate_local([1,0,0], cmd['pitch'] * self.PITCH_YAW  * dt)
        self.rotate_local([0,1,0], cmd['yaw']   * self.PITCH_YAW  * dt)
        self.rotate_local([0,0,1], cmd['roll']  * self.ROLL_SPEED * dt)
        # THRUST: PROPORTIONAL — do NOT normalize (that would kill analog).
        tx, ty, tz = cmd['thrust_xyz']
        local = np.array([tx, ty, tz], dtype=float)
        # clamp magnitude to <=1 so a fully-deflected stick = full thrust, but
        # partial deflection stays proportional:
        m = np.linalg.norm(local)
        if m > 1.0:
            local /= m
        target = quat_rotate(self.q, local) * self.MAX_SPEED   # (no boost on stick
                                                               #  unless Nir wants it)
        self.vel += (target - self.vel) * min(1.0, self.ACCEL * dt)
        self.pos += self.vel * dt

    NOTE: this is a SKETCH built from the pasted snippet. You MUST reconcile it
    with the REAL pasted Ship (field names, helper names, axis signs). In
    particular:
      - Confirm rotate_local sign matches keyboard feel (stick-back = pitch up
        like K_UP, or whatever Nir confirms feels right). Adjust signs per
        TESTING, not per guess.
      - thrust_xyz axes MUST agree with keyboard thrust axes (see §4). If the
        forward axis sign is opposite, negate tz.
      - DECIDE how analog thrust composes with the keyboard's velocity-easing.
        Calling apply_pilot AFTER update means BOTH set `target` and ease `vel`
        toward it; the LAST one wins for that frame's target. That can feel
        like keyboard and stick "fight." BETTER (your judgment): have ONE
        velocity-easing per frame. Cleanest option below in 5.2.

### 5.2 PREFERRED COMPOSITION (avoid keyboard/stick fighting)
Two valid shapes — pick the cleaner one given the real Ship, and JUSTIFY it:

  OPTION A (separate calls, simplest): in app.py, after ship.update(dt, keys),
  call ship.apply_pilot(dt, cmd). Downside: two velocity-easing steps/frame can
  feel slightly off when both inputs are active.

  OPTION B (combine inputs, best feel — RECOMMENDED): refactor so ROTATION and a
  raw THRUST VECTOR are summed from BOTH sources, THEN a SINGLE velocity-ease +
  pos-integrate happens once. Concretely, add to Ship a method that takes BOTH
  the keys array AND the (optional) analog cmd and does:
      rot_pitch = (kb_pitch + analog_pitch_clamped)
      ... same for yaw/roll ...
      thrust_vec = kb_thrust_unit_or_zero + analog_thrust_vec   (then clamp |.|<=1)
      single ease + integrate
  If you choose B, you may add a new method (e.g. update6dof(dt, keys, cmd)) and
  have app.py call THAT instead of update()+apply_pilot(). KEEP the old update()
  intact (other code/tests may call it) — ADD, don't replace.
  *** Your call. State which you chose and WHY in the report. Nir wants smooth
  simultaneous feel, no fighting. ***

### 5.3 Wire it in app.py (2-4 lines, joystick is ADDITIVE)
In the loop, BEFORE containment.resolve (so containment still corrects the final
position), after reading keys:
    cmd = gamepads.pilot_command() if gamepads is not None else None
Then either (Option A) keep ship.update(dt, keys) and add ship.apply_pilot(dt,
cmd), OR (Option B) replace the single ship.update call with your combined
update6dof(dt, keys, cmd). containment.resolve(ship, hub, prev_pos) MUST still
run AFTER all motion and BEFORE ship.apply_view() — do NOT move it.
  - Guard for cmd is None (calibration/no device): motion falls back to
    keyboard only. NEVER crash if gamepads is None or returns None.
  - The 60-frame calibration window means the stick is dead for ~1 second at
    startup — that is EXPECTED and correct; tell Nir so he isn't surprised.

### 5.4 Engine canon — do NOT break the flush
You are NOWHERE NEAR the wall flush, but the rule stands: do NOT add/move/
remove/duplicate render.flush_walls; do NOT reorder the frame loop except the
2-4 input lines described. containment.resolve stays exactly where #C1 put it.

### 5.5 What you do NOT touch
This brief is JOYSTICK (the T.16000M pilot device). It is NOT the Xbox pad
(that's the manipulator: weapons/fire, already wired). Do NOT touch firing,
weapon cycling, Xbox triggers, or combat.py. (The Xbox-trigger-autofire bug is
already fixed; do not reopen it.) Only pilot_command() -> ship motion.

## 6. PROBE-FIRST INSTINCT (Nir's hard-won rule)
Before declaring done, verify on screen / via probes:
  - print cmd once per second (not every frame) when the stick moves, to confirm
    pitch/yaw/roll/thrust_xyz values flow and are proportional (e.g. half-tilt
    ~0.5);
  - confirm during the first ~1s (calibration) cmd is None and the ship sits
    still on the stick but keyboard still flies;
  - push stick FORWARD: ship moves the SAME direction as W (or whatever the
    keyboard forward is) — confirm sign; partial push = slower (analog!);
  - twist for yaw, tilt for pitch/roll: confirm each axis maps correctly and at
    half-deflection turns at ~half rate;
  - hold a keyboard thrust AND a stick thrust at once: confirm they ADD smoothly,
    no fighting/jitter;
  - confirm containment still stops the ship at walls/robots while flying on the
    stick (the stick must not let you punch through rock).
Give Nir a numbered ~2-minute TEST CHECKLIST.

## 7. WHAT YOU MUST NOT DO (scope fence — hard)
- Do NOT re-apply deadzones/calibration (pilot_command already does).
- Do NOT route analog through the digital key array or the normalized thrust
  path (kills analog).
- Do NOT change Ship tunables or the existing update() keyboard behavior — ADD
  a method, don't replace.
- Do NOT touch gamepad.py's reading logic, combat, firing, weapon cycling, the
  Xbox pad, or any other module. If you genuinely need a change in gamepad.py,
  REQUEST it in the report.
- Do NOT add/move/remove flush_walls; do NOT move containment.resolve; do NOT
  reorder the loop beyond the 2-4 input lines.
- Do NOT reinvent quaternion math — reuse rotate_local + the quat_* helpers.
- Do NOT add math-meaning or color logic (Prime Law).

## 8. DELIVERABLES
1. The new Ship method(s) in render.py (apply_pilot and/or update6dof), shown as
   clean additions (do not alter existing update()).
2. The app.py loop edit (before/after, 2-4 lines), with cmd guarded for None.
3. A numbered JOYSTICK TEST CHECKLIST (§6) for Nir.
4. A COMPLETION REPORT (template below).

## 9. COMPLETION REPORT TEMPLATE
- FILES CHANGED (exact): expect render.py (added method) + app.py (loop lines).
- The new method(s), final code.
- The app.py edit, final, showing it sits before containment.resolve and
  apply_view, with the None-guard.
- COMPOSITION CHOICE (Option A or B) and WHY (fighting/feel reasoning).
- AXIS/SIGN MAP you ended on (which stick motion -> which ship motion), and any
  sign you had to FLIP during testing vs the raw pilot_command() values.
- Confirmation you did NOT re-apply deadzones and did NOT touch the digital
  normalize path.
- Probe results / what NIR FELT on screen (proportionality, additive, no fight,
  calibration ~1s dead, containment still holds).
- REQUESTS TO PARENT (only if truly needed).
- SURPRISES / mismatches vs this brief in the pasted files.

## 10. ONE LAST THING
This is the last engine-input gap. Respect it: analog magnitude must survive
(no normalize crush), keyboard + stick must ADD without fighting, signs must be
confirmed by FEEL not guessed, the ~1s startup calibration is expected, and
containment must still hold the ship inside the rock while flying on the stick.
Read the real files first, then build. When Nir flies smoothly on the T.16000M
with proportional control, simultaneously with the keyboard, this mission is
laid to rest. :-)
================================================================================
END OF BRIEF #J1
================================================================================
