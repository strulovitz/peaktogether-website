# PROMPT TO OPUS — QUAKE PARENT 23: ADD JOYSTICK + XBOX CONTROLLER SUPPORT

> You are **Parent 23** — a fresh Opus 4.x architect on the **Quake** game (Game 3 of the
> "Peak Together" platform). This mission is **code-first: YOU write the actual Python code
> yourself, in full. NOT a design document. NOT delegated to children.** DeepSeek (a runner
> AI in OpenCode on Nir's Windows PC) will drop your code into the repo, run the tests, and
> Nir will play-test with the real controllers.

---

## §0 — GROUND RULES (read first)

1. **You write real, complete, runnable code.** Not prose, not a plan, not TODOs. When you're
   ready, deliver full files (or full, drop-in functions) in fenced code blocks.
2. **Honesty is absolute.** If something is uncertain, say so plainly. Never claim a thing
   works because "it compiles" or "the tests pass" — controller feel is judged by Nir playing
   the actual game. Do not invent facts about any library API you are not sure of; state the
   uncertainty and let the run loop confirm it.
3. **No invented constraints.** Every requirement here traces to Nir's explicit instruction or
   a confirmed fact. Do not add your own "rules," "phases," or "defer this to later" escape
   hatches. If you think something extra is needed, ASK Nir first.
4. **Talk-first.** Do not sprint. State your plan and your questions, and WAIT for Nir's
   confirmation before you write the final code.
5. **How you get more information:** you have no internet and no file access. DeepSeek can read
   the entire Quake + Descent codebase. **Ask DeepSeek precise questions** (batch them) and you
   will get back exact, verbatim excerpts. Ask for whole files only when you truly need them.
6. **Nir cannot code or read code.** He is the play-tester and the boss. He carries text between
   you and DeepSeek. Keep explanations to him in plain, warm language.

---

## §1 — THE MISSION (Nir's exact words, paraphrased faithfully)

Quake currently plays with **keyboard + mouse only**. Nir wants to add controller support
**exactly like the finished, shipped Descent game already has**, so his game can be played by a
couple on the couch:

- **The boyfriend controls the "Mover"** (walks the body + turns/looks) with **either the
  keyboard OR a Thrustmaster T.16000M joystick.**
- **The girlfriend controls the "Shooter"** (moves the on-screen reticle + fires) with **either
  the mouse OR an Xbox controller.**
- **Both input methods must work at the same time (ADDITIVE).** The controller does not replace
  keyboard/mouse; it adds on top. If no controller is present, the game plays exactly as it does
  today on keyboard+mouse (zero regression).

This is the *same co-op split Descent uses* (one player flies, one player points), applied to
Quake's Mover/Shooter roles.

---

## §2 — CONFIRMED HARDWARE FACTS (measured THIS session on Nir's actual PC)

These are real readings from Nir's machine today — not guesses:

- **OS:** Windows. **Python 3.12.11.** Installed: **pygame 2.6.1 (SDL 2.28.4)** and
  **pyglet 2.1.14**. Quake's window/GL is built on **pyglet**. Descent's window/GL is built on
  **pygame**.
- **Both controllers are plugged in and detected.**

**Via pygame** (`pygame.joystick`):
```
COUNT: 2
  [0] name='Xbox 360 Controller'  axes=6  buttons=11  hats=1
  [1] name='T.16000M'             axes=4  buttons=16  hats=1
```
- On the Xbox, **pygame axes 4 and 5 rest at -1.00** (the two analog triggers at rest). This is
  the exact resting convention behind the Descent auto-fire bug (see §5).

**Via pyglet** (`pyglet.input`):
```
pyglet.input.get_joysticks()   -> ['T.16000M']         # the joystick (DirectInput)
pyglet.input.get_controllers() -> ['XInput0']           # the Xbox (XInput, standardized)
# NOTE: this pyglet version has get_controllers() and ControllerManager,
#       but does NOT have get_game_controllers().
```

**⚠️ A CRITICAL, CONFIRMED TECHNICAL FINDING (this is the whole puzzle):**
- **pygame reads controllers ONLY when a pygame window exists to pump SDL events.** In Descent
  this is satisfied by `pygame.display.set_mode(...)`. We measured that in Quake, calling
  `pygame.joystick` + `pygame.event.pump()`/`get()` **with no pygame display window returns
  frozen values** (axes never change when the sticks move — only the initial state is read).
  So Descent's controller code works *because pygame owns Descent's window*.
- **Quake does NOT have a pygame window.** Quake's window is a **pyglet** window, and Quake's
  frame loop already calls `window.dispatch_events()` every frame (so *pyglet's* own input
  events already flow each frame — see §3).
- Therefore: **the core problem you must solve is how to read these two controllers from inside
  a pyglet-windowed process.** Two proven-available paths exist (both confirmed present on this
  machine). **YOU decide which is best** — see §6. Do not let DeepSeek pre-decide this for you.

---

## §3 — QUAKE'S INPUT ARCHITECTURE (the code you'll extend)

Quake has a clean, well-tested input layer: `quake/input_actions.py`. It is **pure core +
thin shell**. The pure core (`build_actions`, `RawSample`, `EdgeTracker`) is fully unit-tested
and must not be broken (currently **468/468 tests green**). Controllers should be read in the
**thin shell** and folded into the same `RawSample`, so the pure core is untouched.

### 3.1 — The frozen `Actions` contract (from `quake/contracts.py`, verbatim)
```python
class Actions(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    # MOVER (owns the body) ---------------------------------------------------
    move_x: float = 0.0          # [-1,1] strafe (right +)
    move_y: float = 0.0          # [-1,1] forward (+) / back (-)
    heading_delta: float = 0.0   # radians this frame (yaw). MOVER ONLY.
    pitch_delta: float = 0.0     # radians this frame, pre-clamp. MOVER ONLY.
    # SHOOTER (owns the reticle) ---------------------------------------------
    aim_x: float = 0.0           # [-1,1] reticle x within cone
    aim_y: float = 0.0           # [-1,1] reticle y within cone
    fire: bool = False           # edge: true only on the frame fire is pressed
    fire_held: bool = False
    # SHARED ------------------------------------------------------------------
    read_toggle: bool = False    # edge
    interact: bool = False       # edge
    pause: bool = False          # edge
```

### 3.2 — How those fields are consumed by gameplay (from `quake/gameplay.py`, verbatim excerpts)
```python
# heading/pitch are RATES accumulated per frame (Mover only):
state.heading_rad += actions.heading_delta
raw_pitch = state.pitch_rad + actions.pitch_delta   # then clamped to +/-PITCH_CLAMP_RAD (1.2217 rad, ~70 deg)

# movement is a direct [-1,1] vector times walk speed:
fwd_x = cos(state.heading_rad); fwd_z = sin(state.heading_rad)
str_x = -sin(state.heading_rad)   # right strafe (move_x=+1 -> right)
str_z =  cos(state.heading_rad)
dx = (fwd_x * actions.move_y + str_x * actions.move_x) * WALK_SPEED_M_S * dt
dz = (fwd_z * actions.move_y + str_z * actions.move_x) * WALK_SPEED_M_S * dt

# the SHOOTER's reticle is an ABSOLUTE offset inside a 17-degree cone (AIM_CONE_RAD = 0.30 rad):
#   aim_x/aim_y in [-1,1] place the reticle within the cone; aim_y positive = look UP.
def reticle_ray(eye, heading, pitch, aim_x, aim_y) -> Ray:
    forward = (cos(pitch)*cos(heading), sin(pitch), cos(pitch)*sin(heading))
    right   = (sin(heading), 0.0, -cos(heading))
    # ... ray direction = forward + aim_x*AIM_CONE_RAD*right - aim_y*AIM_CONE_RAD*pitch_up
```
**Key implication for the Shooter:** because `aim_x/aim_y` are used as an **absolute** position
inside the cone, an **absolute analog stick** (Xbox right stick, value held at some deflection)
maps to them *directly and naturally* — push the stick, the reticle sits there while held. The
existing **mouse** feeds `aim_x/aim_y` from per-frame mouse deltas instead. When you add the
stick, ADD the stick's absolute value to whatever the mouse contributed this frame.

**Key implication for the Mover:** `heading_delta`/`pitch_delta` are **rates** (per-frame
deltas). A held joystick **twist**/axis is a natural rate source (held = keeps turning). The
current mover build multiplies its "yaw rate" source by a sensitivity and by `dt`. Movement
`move_x/move_y` are direct [-1,1] and add on top of WASD.

### 3.3 — `quake/input_actions.py` — the exact seam (verbatim, the parts that matter)
```python
DEFAULT_YAW_SENS = 2.2     # rad/s per unit input
DEFAULT_PITCH_SENS = 1.8

@dataclass
class RawSample:
    # mover
    mover_axis_x: float
    mover_axis_y: float
    mover_yaw_rate: float
    mover_pitch_rate: float
    # shooter
    shooter_aim_x: float
    shooter_aim_y: float
    shooter_fire_down: bool
    # shared buttons (CURRENT down-state, level not edge)
    read_down: bool
    interact_down: bool
    pause_down: bool

# EdgeTracker.edges(sample) turns fire/read/interact/pause down-states into ONE-FRAME edges
# (True only on the False->True transition). fire_held stays level. build_actions() clamps and
# assembles the frozen Actions. NONE of this pure core should change.

def poll(window, bindings) -> Actions:
    # maintains a module-level EdgeTracker + dt clock, then:
    sample = _read_raw_sample(window, bindings)     # <-- THE SHELL: add controllers HERE
    return build_actions(sample, _SHELL_TRACKER, dt, DEFAULT_YAW_SENS, DEFAULT_PITCH_SENS)
```
`_read_raw_sample(window, bindings)` currently reads keyboard + mouse from the pyglet window via
tiny helpers (`_key_down`, `_mouse_delta`, `_mouse_left_down`). **This is where controller values
get ADDED into the RawSample.** `poll(window, bindings)` is called once per frame from `app.py`.
You may change `poll`'s signature (e.g. add an optional `gamepad=None`) **as long as existing
callers/tests that call `poll(window, bindings)` still work** — keep a default so the pure-core
tests and the smoke test don't break.

### 3.4 — The window object (from `quake/gfx_context.py`)
The window is a **pyglet `Window`** created in `make_window(...)`. It runs with
`set_exclusive_mouse(True)`. DeepSeek attached custom helpers to it:
`window._quake_keystate` (a `set` of pressed key symbols), `window._quake_mousedx()` (returns
accumulated `(dx,dy)` and resets), `window._quake_mouseleft()` (bool). The main loop calls
`window.dispatch_events()` and `window.flip()` every frame (in `app.py`'s `_window_present`).
**So any pyglet input device opened against this window will be pumped every frame for free.**

---

## §4 — DESCENT'S PROVEN CONTROLLER CODE (verbatim — this is known-good on Nir's exact hardware)

Descent is finished and shipped. Its controller support was written by an earlier Opus and
works perfectly on Nir's T.16000M + Xbox. It uses **pygame**. Here is the real, verbatim code.
Use it as the authoritative source of the *behavior* Nir wants (calibration, deadzones, the
additive model, the fire edge). The mapping constants (which axis is which) were **verified on
Nir's hardware**.

### 4.1 — `descent/gamepad.py` (VERBATIM, complete)
```python
import math
import numpy as np
import pygame


class GamepadManager:
    """Full gamepad support: T.16000M -> PILOT, Xbox 360 -> MANIPULATOR.
    Deadzones: radial for 2D sticks (0.12), scalar for twist/throttle (0.08)."""

    CALIB_FRAMES    = 60
    STICK_DZ_RADIAL = 0.12
    SCALAR_DZ       = 0.08

    # T.16000M FCS axis mapping (verified on Nir's hardware via Anniversary project)
    AXIS_ROLL     = 0   # stick X
    AXIS_PITCH    = 1   # stick Y (forward push = axis negative = dive)
    AXIS_YAW      = 2   # stick Z twist
    AXIS_THROTTLE = 3   # throttle slider

    # Xbox right-stick axis indices (confirmed from Nir's test: a2=left/right, a3=forward/back)
    XBOX_RSTICK_X = 2
    XBOX_RSTICK_Y = 3

    def __init__(self):
        pygame.joystick.init()
        self.pilot_joy = None
        self.manip_joy = None
        self._calib_sum    = {}
        self._calib_frames = {}
        self._calib_done   = {}
        self._calib_rest   = {}
        self._slider_idx = 0
        self._slider_switch_cooldown = 0.0
        self._detect()

    def _detect(self):
        """Assign connected devices: T.16000M -> pilot, Xbox gamepad -> manipulator."""
        count = pygame.joystick.get_count()
        for i in range(count):
            joy = pygame.joystick.Joystick(i)
            name = joy.get_name()
            is_t16  = "T.16000" in name or "Thrustmaster" in name
            is_xbox = "Xbox" in name or "360" in name or "XInput" in name
            if is_t16 and self.pilot_joy is None:
                joy.init(); self.pilot_joy = joy; self._start_calibration(joy)
            elif is_xbox and self.manip_joy is None:
                joy.init(); self.manip_joy = joy; self._start_calibration(joy)

    def _start_calibration(self, joy):
        jid = joy.get_instance_id(); n = joy.get_numaxes()
        self._calib_sum[jid] = np.zeros(n); self._calib_frames[jid] = 0
        self._calib_done[jid] = False; self._calib_rest[jid] = np.zeros(n)

    @staticmethod
    def _clamp1(v):
        return max(-1.0, min(1.0, v))

    def _scalar_deadzone(self, v):
        if abs(v) < self.SCALAR_DZ:
            return 0.0
        sign = 1.0 if v > 0 else -1.0
        return sign * (abs(v) - self.SCALAR_DZ) / (1.0 - self.SCALAR_DZ)

    def _radial_deadzone(self, x, y):
        mag = math.sqrt(x * x + y * y)
        if mag < self.STICK_DZ_RADIAL:
            return 0.0, 0.0
        scale = ((mag - self.STICK_DZ_RADIAL) / (1.0 - self.STICK_DZ_RADIAL)) / mag
        return x * scale, y * scale

    def _calibrate(self, joy):
        """Run one calibration frame. Returns calibrated axes array or None if still calibrating."""
        jid = joy.get_instance_id()
        if self._calib_done.get(jid, False):
            rest = self._calib_rest[jid]
            return np.array([joy.get_axis(i) - rest[i] for i in range(joy.get_numaxes())])
        if jid in self._calib_sum:
            n = min(joy.get_numaxes(), len(self._calib_sum[jid]))
            for i in range(n):
                self._calib_sum[jid][i] += joy.get_axis(i)
            self._calib_frames[jid] += 1
            if self._calib_frames[jid] >= self.CALIB_FRAMES:
                self._calib_rest[jid] = self._calib_sum[jid] / self.CALIB_FRAMES
                self._calib_done[jid] = True
        return None

    def pilot_command(self):
        """Returns dict {pitch, yaw, roll, thrust_xyz} in -1..+1, or None if no pilot device.
        App.update() must ADD these to keyboard values (simultaneous use)."""
        joy = self.pilot_joy
        if joy is None:
            return None
        cal = self._calibrate(joy)
        if cal is None:
            return None  # still calibrating
        n = joy.get_numaxes()
        roll = pitch = yaw = 0.0
        thrust_xyz = [0.0, 0.0, 0.0]
        if n > max(self.AXIS_ROLL, self.AXIS_PITCH):
            sx = self._clamp1(cal[self.AXIS_ROLL]); sy = self._clamp1(cal[self.AXIS_PITCH])
            sx, sy = self._radial_deadzone(sx, sy)
            roll = sx; pitch = sy
        if n > self.AXIS_YAW:
            yaw = self._scalar_deadzone(self._clamp1(cal[self.AXIS_YAW]))
        if n > self.AXIS_THROTTLE:
            t = self._scalar_deadzone(self._clamp1(cal[self.AXIS_THROTTLE]))
            thrust_xyz[2] = -t
        if joy.get_numhats() >= 1:
            hx, hy = joy.get_hat(0)
            thrust_xyz[0] += float(hx); thrust_xyz[1] += float(hy)
        thrust_xyz = [self._clamp1(v) for v in thrust_xyz]
        return {'pitch': pitch, 'yaw': yaw, 'roll': roll, 'thrust_xyz': tuple(thrust_xyz)}

    def manipulator_right_stick(self):
        """Returns (rx, ry) calibrated + radial-deadzoned from Xbox right stick,
        or (0.0, 0.0) if no manipulator connected or still calibrating."""
        joy = self.manip_joy
        if joy is None:
            return (0.0, 0.0)
        cal = self._calibrate(joy)
        if cal is None:
            return (0.0, 0.0)
        n = joy.get_numaxes()
        if n <= max(self.XBOX_RSTICK_X, self.XBOX_RSTICK_Y):
            return (0.0, 0.0)
        rx = self._clamp1(cal[self.XBOX_RSTICK_X]); ry = self._clamp1(cal[self.XBOX_RSTICK_Y])
        rx, ry = self._radial_deadzone(rx, ry)
        return (rx, ry)
```

### 4.2 — How Descent's main loop wires the PILOT (T.16000M) into movement (from `descent/app.py`, verbatim)
```python
from gamepad import GamepadManager
try:
    gamepads = GamepadManager()
except Exception:
    gamepads = None   # no controller -> mode runs on mouse+keyboard

# ... each frame:
cmd = gamepads.pilot_command() if gamepads is not None else None
ship.update6dof(dt, keys, cmd)      # keyboard + analog joystick, ADDITIVE
```

### 4.3 — How Descent maps the Xbox RIGHT STICK to a 2D pan (from `descent/understanding.py`, verbatim)
This is the closest analog to Quake's Shooter reticle — an analog stick driving a 2D screen
position, ADDED on top of the mouse:
```python
# mouse contribution:
self.pan_x -= dx * PAN_SPEED
self.pan_y -= dy * PAN_SPEED
# ADD the Xbox right stick on top:
if gamepads is not None:
    rx, ry = gamepads.manipulator_right_stick()
    self.pan_x -= rx * STICK_SPEED * dt
    self.pan_y -= ry * STICK_SPEED * dt
```

---

## §5 — THE AUTO-FIRE BUG (the exact trap Nir warned about — do NOT reintroduce it)

In Descent, controller fire took ~5 debugging passes to get right. The final, verbatim comment
and fix from `descent/combat.py`:
```python
# triggers -> FIRE.
# Xbox/XInput analog triggers REST at -1.0 (released) and read +1.0 fully
# pressed; some drivers rest at 0.0 instead. Using abs() (old bug) treated the
# -1.0 resting state as "fully pressed", auto-firing on frame 1 and silently
# destroying the first robot in every corridor. Test the SIGNED value crossing
# into the clearly-pressed positive region — false for BOTH resting conventions
# (-1.0 and 0.0), true only for a real pull.
FIRE_TH = 0.5
try:
    lt = joy.get_axis(4); rt = joy.get_axis(5)
except Exception:
    lt = rt = 0.0
trigger_now = (lt > FIRE_TH) or (rt > FIRE_TH)   # signed, not abs()
```
Two more verbatim lessons from Descent's `app.py` about fire:
```python
# fire_edge = SPACE (keyboard) OR pilot trigger, each rising-edged and ADDITIVE:
fire_edge = bool((keys[K_SPACE] and not prev_keys[K_SPACE])
                 or (pilot_fire_now and not prev_pilot_fire))
# Snapshots for next frame's rising edges — computed UNCONDITIONALLY every frame
# so edge state never goes stale (this is what stops the trigger phantom-firing).
```
**Takeaways you must honor:**
1. **Never use `abs()` on a trigger axis.** Test the **signed** value `> FIRE_TH` (e.g. 0.5),
   which is false at both -1.0 and 0.0 rest.
2. **Fire is a rising edge, ADDITIVE with the mouse.** In Quake, the mouse-left already becomes
   `fire` via `EdgeTracker`. Fold the controller-fire down-state into the same `shooter_fire_down`
   so the existing `EdgeTracker` produces one clean edge. (Note: whether the Xbox "fire" is a
   trigger axis (pygame axis 4/5, or pyglet `righttrigger` 0..1) or a face button (A) is a
   mapping choice — see §7. Whatever you pick, use the signed/threshold-safe test.)
3. Startup calibration on the T.16000M means the stick reads neutral for ~1 second (60 frames)
   at launch; keyboard/mouse must keep working during that window.

---

## §6 — THE CORE DECISION YOU MUST MAKE (do not let anyone pre-decide it)

You must choose **how to read the two controllers from inside Quake's pyglet-windowed process.**
Both options below are **confirmed available on Nir's machine** (see §2). Weigh them and decide;
explain your choice honestly to Nir; ask DeepSeek for anything you need to decide well.

- **Option A — pyglet-native input.** Use `pyglet.input.get_joysticks()` for the T.16000M and
  `pyglet.input.get_controllers()` for the Xbox, opened against Quake's existing window. Pro:
  no new dependency; events are already pumped by the existing `window.dispatch_events()`; the
  Xbox comes in as a *standardized* XInput Controller (named sticks/triggers/buttons, no
  axis-index guessing). Con: it is **not** the literal Descent code; you must re-express
  calibration/deadzone/edge behavior against pyglet's API, and confirm the T.16000M's DirectInput
  axis attributes on Nir's hardware by a quick live probe.
- **Option B — pygame joystick alongside pyglet.** Reuse Descent's `gamepad.py` almost verbatim.
  Con: **pygame only updates joystick state when a pygame window pumps SDL events, and Quake has
  no pygame window** (confirmed §2). You would need a mechanism that reliably pumps SDL in this
  process (e.g. a hidden/second SDL window, or a background helper). This risk is real and you
  must design it explicitly and prove it live — do not hand-wave it.

Whatever you choose, the **behavior contract is fixed by Descent + Nir**: additive with
keyboard/mouse, startup calibration, radial deadzone 0.12 (sticks) / scalar 0.08 (twist/throttle),
signed trigger fire, rising-edge fire, zero regression with no controller attached.

---

## §7 — MAPPING (propose these to Nir; he confirms by feel in-game — NOT pre-frozen)

The exact control mapping is a **feel decision for Nir**, who will play-test. Propose a first
mapping and let him tune it live. A sensible starting proposal (state it, don't assume it's
final):

- **Boyfriend / Mover — T.16000M (added on top of WASD + mouse-look):**
  - stick X (axis 0) → strafe `move_x`
  - stick Y (axis 1) → walk `move_y` (push forward = axis negative = forward +1)
  - twist (axis 2) → turn `mover_yaw_rate` (a rate)
  - pitch look (`mover_pitch_rate`): a rate source such as the **hat** up/down, or the throttle —
    propose one, let Nir judge. (Quake's Mover needs some up/down look to face high/low panels.)
- **Girlfriend / Shooter — Xbox (added on top of the mouse):**
  - right stick → `aim_x`, `aim_y` (absolute within the cone; note `aim_y` positive = look UP, so
    invert the stick's Y if needed)
  - fire → the signed-safe trigger test `> 0.5` **and/or** the **A** button — propose, let Nir pick.
- **Nice-to-have (ask Nir if he wants them now or later):** a controller button for **Read Mode**
  (currently `R`) and for **pause/quit**. Not required for the core mission.

---

## §8 — ACCEPTANCE / HOW THIS GETS JUDGED

1. **No regression:** with no controller attached, the game plays identically to today
   (keyboard+mouse), and **all 468 existing tests stay green.** The pure core of
   `input_actions.py` (`build_actions`/`RawSample`/`EdgeTracker`) must remain intact; controllers
   live in the shell.
2. **Live play-test by Nir:** boyfriend walks + turns + looks with the T.16000M while the
   girlfriend aims the reticle + fires with the Xbox — simultaneously with keyboard/mouse.
3. **No auto-fire:** the first demon/panel is never destroyed on frame 1; the reticle does not
   drift on its own; nothing fires while triggers are at rest.
4. Any GL/window/headless code stays import-safe (Quake guards GL so the test suite runs
   headless). Controller reading must degrade gracefully to "no controller" if devices are
   absent or still calibrating.

---

## §9 — WHAT TO DO RIGHT NOW

State (a) which option in §6 you're leaning toward and **why**, (b) your proposed §7 mapping,
and (c) any precise questions for DeepSeek (e.g. "paste the full current `_read_raw_sample` and
`poll`", "paste `app.py`'s frame-loop input section", "run a live pyglet probe reading
`T.16000M` attributes x/y/z/rz/hat_x/hat_y while Nir moves each control and report the peak per
attribute"). Then WAIT for Nir before writing the final code.

DeepSeek can, on request, run **live controller probes on Nir's hardware** and report exact
per-axis/per-button readings — use this to nail the T.16000M's pyglet attribute names or to
confirm the Xbox trigger convention before you commit to a mapping.
