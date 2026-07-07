"""
LOOM2 -- core/game_state.py
THE CONDUCTOR OF EVERYTHING: mode state machine, totem, quiz, slice walk.
Owns all mutable game state; graphics draws it, audio receives it.
Allowed imports: math, config, core.types, core.scene, core.surfaces,
audio.musicians. (Receives engine & camera as constructor args -- does NOT
import their modules: dependency injection keeps the seams thin.)

IMPLEMENTATION NOTES (bodies only; frozen contracts untouched):

* Intent pattern. handle_action() (called before update() in main's frozen
  frame order) only RECORDS input intents; update(dt) integrates them with
  real time. This is how "handle_action moves the totem" and "update does
  smooth analog motion" are both honored: one records, the other enacts.
  Held axes are re-asserted by input_map.poll() every frame, so intents are
  cleared at the end of every update().
* Quiz exit gesture. The GITA defines entry to QUIZ_LISTEN (an option plays,
  the land falls silent) but not the exit; the natural gesture chosen here:
  TOUCH THE TOTEM. Any totem movement in QUIZ_LISTEN stops the option and
  the land sings again. Camera orbit/zoom stay allowed while listening
  (view-only; the option WAV is fixed stereo by design, SUTRAS 5.3).
* Slice transect. The walk itinerary implements the IDENTICAL definition as
  GlassBlade.intersection_path (G3.6): a straight line in (x,y) through
  (cx, cy) along yaw, clipped to the scene domain. It is duplicated here
  (~20 lines of pure math) because graphics imports are forbidden in core.
  DeepSeek: keep both implementations literally in sync -- same definition,
  deterministic, so drawn curve == walked road. Walk stops are spaced one
  RING_WIDTH apart, so each measure advances the totem by one rhythm ring:
  a procession of neighborhoods, NEVER a siren (VEDAS law, preserved).
* Celebration. On a correct answer the winning groove keeps looping through
  the SCENE_TRANSITION celebration -- the players hear the sound they just
  understood while reading why they were right.
* scene_changed is read-and-clear: snapshot() is main's once-per-frame read,
  and consuming the flag there guarantees exactly one rebuild (G4.5).
* After the final scene the campaign completes into free play on the last
  map, with success_text (the closing line of LOOM1's soul) left on screen.
"""
import math

import config
from core.types import Mode, Action, TotemState, SlicePlane
from core import scene as scene_mod
from core import surfaces
from audio import musicians

# --- conductor's tuning (implementation detail; config stays frozen) -------
_TOTEM_SPEED = 3.0        # world units / s at full stick
_VEL_SMOOTH = 10.0        # 1/s exponential ease toward commanded velocity
_ORBIT_SPEED = 60.0       # camera deg / s (azimuth)
_ELEV_SPEED = 40.0        # camera deg / s (elevation)
_ZOOM_PER_SEC = 1.6       # zoom factor applied per held second
_PLANE_YAW_SPEED = 45.0   # blade deg / s
_PLANE_TILT_SPEED = 30.0  # blade fine-tilt deg / s
_TILT_LIMIT = 45.0        # blade tilt clamp (visual only)
_WALK_STEP = config.RING_WIDTH   # one ring of neighborhoods per measure
_TRANSITION_SEC = 5.0     # celebration length before the next scene
_MOVE_EPS = 1e-5
_ANSWER_ACTIONS = {}      # filled below (Action -> label)


class GameState:
    def __init__(self, engine, camera, first_scene_id: str):
        """engine: AudioEngine. camera: OrbitCamera. Loads the scene, seats
        the grid (musicians.seat_grid), plants totem at totem_start, mode
        EXPLORE, pushes initial voices to engine."""
        self._engine = engine
        self._camera = camera
        # campaign position
        self._order = scene_mod.campaign_order()
        self._scene_index = (self._order.index(first_scene_id)
                             if first_scene_id in self._order else None)
        # input intents (recorded by handle_action, enacted by update)
        self._ax_x = 0.0
        self._ax_y = 0.0
        self._orbit_az = 0.0
        self._orbit_el = 0.0
        self._zoom_dir = 0.0
        self._vel_x = 0.0
        self._vel_y = 0.0
        # quiz state
        self._selected = None
        self._playing = None
        self._hint_open = False
        self._explain = ""
        self._success = False
        self._campaign_complete = False
        # slice state
        self._plane = SlicePlane(0.0, 0.0, 0.0, 0.0, False)
        self._walk_path = []
        self._walk_idx = 0
        self._walking = False
        self._return_xy = None
        # bookkeeping
        self._transition_timer = 0.0
        self._scene_changed = False
        self._quit = False
        self._prev_phase = 0.0
        self._mode = Mode.EXPLORE
        self._load_scene(first_scene_id)

    # ------------------------------------------------------- scene loading
    def _load_scene(self, scene_id: str) -> None:
        self._spec = scene_mod.load_scene(scene_id)
        self._surface = surfaces.get(self._spec.surface_name)
        self._grid = musicians.seat_grid(self._spec.domain)
        sx, sy = self._spec.totem_start
        self._totem = TotemState(float(sx), float(sy), config.HEARING_R)
        self._zoct = self._spec.z_per_octave
        # fresh page: quiz, slice, motion all reset
        self._selected = None
        self._playing = None
        self._hint_open = False
        self._explain = ""
        self._success = False
        self._plane = SlicePlane(sx, sy, 0.0, 0.0, False)
        self._walk_path = []
        self._walking = False
        self._return_xy = None
        self._vel_x = self._vel_y = 0.0
        self._engine.set_quiz_wav(None)
        self._push_voices()
        self._scene_changed = True
        # NOTE: camera limits change per scene; main owns camera rebuilding
        # on scene_changed if it chooses (G4.5 step 9).

    def _push_voices(self) -> None:
        """Rebuild the seated orchestra around the totem and hand it to the
        engine. self._voices is THE list helix_panel draws and the engine's
        flash indices refer to (stable order guaranteed by musicians)."""
        self._voices = musicians.build_voices(
            self._totem, self._surface, self._grid, self._zoct)
        self._engine.set_voices(self._voices)

    def _clamp_domain(self, x: float, y: float) -> tuple:
        xmin, xmax, ymin, ymax = self._spec.domain
        return (min(max(x, xmin), xmax), min(max(y, ymin), ymax))

    # ------------------------------------------------------ input routing
    def handle_action(self, action: Action, value: float) -> None:
        """THE ONLY INPUT ENTRY POINT. Routing by mode (G4.3). Discrete
        actions arrive once per press; held axes arrive every frame."""
        if action is Action.QUIT:
            self._quit = True
            return
        if self._mode is Mode.SCENE_TRANSITION:
            return                       # the celebration is sacred
        if action is Action.HINT:        # free forever, never counted (5.1)
            self._hint_open = not self._hint_open
            return

        if self._mode is Mode.EXPLORE:
            self._route_explore(action, value)
        elif self._mode is Mode.QUIZ_LISTEN:
            self._route_quiz_listen(action, value)
        elif self._mode is Mode.SLICE:
            self._route_slice(action, value)

    def _route_explore(self, action, value):
        if action is Action.TOTEM_X:
            self._ax_x = value
        elif action is Action.TOTEM_Y:
            self._ax_y = value
        elif action is Action.ORBIT_AZ:
            self._orbit_az = value
        elif action is Action.ORBIT_EL:
            self._orbit_el = value
        elif action is Action.ZOOM_IN:
            self._zoom_dir = 1.0
        elif action is Action.ZOOM_OUT:
            self._zoom_dir = -1.0
        elif action is Action.CAM_RESET:
            self._camera.reset()
            self._engine.set_camera_azimuth(self._camera.state().azimuth_deg)
        elif action is Action.SLICE_TOGGLE:
            self._enter_slice()
        elif action in _ANSWER_ACTIONS:
            self._quiz_select(_ANSWER_ACTIONS[action])
        elif action is Action.CONFIRM and self._selected is not None:
            self._quiz_confirm()

    def _route_quiz_listen(self, action, value):
        if action in _ANSWER_ACTIONS:                # switch options freely
            self._quiz_select(_ANSWER_ACTIONS[action])
        elif action is Action.CONFIRM:
            self._quiz_confirm()
        elif action in (Action.TOTEM_X, Action.TOTEM_Y):
            if abs(value) > 0.1:                     # touch the totem:
                self._resume_land()                  # the land sings again
                if action is Action.TOTEM_X:
                    self._ax_x = value
                else:
                    self._ax_y = value
        elif action is Action.ORBIT_AZ:
            self._orbit_az = value                   # view-only, allowed
        elif action is Action.ORBIT_EL:
            self._orbit_el = value
        elif action is Action.ZOOM_IN:
            self._zoom_dir = 1.0
        elif action is Action.ZOOM_OUT:
            self._zoom_dir = -1.0
        elif action is Action.CAM_RESET:
            self._camera.reset()
            self._engine.set_camera_azimuth(self._camera.state().azimuth_deg)

    def _route_slice(self, action, value):
        if action is Action.TOTEM_X:                 # WASD drives the blade
            self._ax_x = value
        elif action is Action.TOTEM_Y:
            self._ax_y = value
        elif action is Action.ORBIT_AZ:              # arrows rotate/tilt it
            self._orbit_az = value                   # (camera stays frozen,
        elif action is Action.ORBIT_EL:              #  SUTRAS Part 6)
            self._orbit_el = value
        elif action in (Action.SLICE_PLAY, Action.CONFIRM):
            self._start_walk()                       # Enter: the procession
        elif action is Action.SLICE_TOGGLE:
            self._exit_slice()

    # ------------------------------------------------------------- update
    def update(self, dt: float) -> None:
        """Per frame: smooth analog totem motion; during slice auto-walk,
        advance one path stop per measure (downbeat edge of the engine's
        measure phase); scene transition timer; then clear intents."""
        phase = self._engine.get_measure_phase()
        downbeat = phase < self._prev_phase          # phase wrapped: strike!
        self._prev_phase = phase

        if self._mode is Mode.SCENE_TRANSITION:
            self._transition_timer -= dt
            if self._transition_timer <= 0.0:
                self._advance_scene()
            return

        # camera enacts in EXPLORE and QUIZ_LISTEN; frozen in SLICE
        if self._mode in (Mode.EXPLORE, Mode.QUIZ_LISTEN):
            if self._orbit_az != 0.0 or self._orbit_el != 0.0:
                self._camera.orbit(self._orbit_az * _ORBIT_SPEED * dt,
                                   self._orbit_el * _ELEV_SPEED * dt)
                self._engine.set_camera_azimuth(
                    self._camera.state().azimuth_deg)   # azimuth ONLY (3.1)
            if self._zoom_dir != 0.0:                   # visual only; the
                self._camera.zoom(_ZOOM_PER_SEC ** (dt * self._zoom_dir))
                # engine is NOT called: zoom never touches audio (SUTRAS 3.1)

        if self._mode is Mode.EXPLORE:
            k = min(1.0, dt * _VEL_SMOOTH)              # ease, don't jerk
            self._vel_x += (self._ax_x * _TOTEM_SPEED - self._vel_x) * k
            self._vel_y += (self._ax_y * _TOTEM_SPEED - self._vel_y) * k
            nx, ny = self._clamp_domain(self._totem.x + self._vel_x * dt,
                                        self._totem.y + self._vel_y * dt)
            if (abs(nx - self._totem.x) > _MOVE_EPS
                    or abs(ny - self._totem.y) > _MOVE_EPS):
                self._totem.x, self._totem.y = nx, ny
                self._push_voices()                     # ears follow hands

        elif self._mode is Mode.SLICE:
            editing = (self._ax_x or self._ax_y
                       or self._orbit_az or self._orbit_el)
            if editing:
                p = self._plane
                p.cx, p.cy = self._clamp_domain(
                    p.cx + self._ax_x * _TOTEM_SPEED * dt,
                    p.cy + self._ax_y * _TOTEM_SPEED * dt)
                p.yaw_deg = (p.yaw_deg
                             + self._orbit_az * _PLANE_YAW_SPEED * dt) % 360.0
                p.tilt_deg = min(_TILT_LIMIT, max(
                    -_TILT_LIMIT,
                    p.tilt_deg + self._orbit_el * _PLANE_TILT_SPEED * dt))
                self._walking = False                   # blade moved: stale
            if self._walking and downbeat:
                if self._walk_idx < len(self._walk_path):
                    x, y = self._walk_path[self._walk_idx]
                    self._totem.x, self._totem.y = x, y
                    self._push_voices()   # this neighborhood, then the next
                    self._walk_idx += 1
                else:
                    self._walking = False               # procession complete

        # intents are per-frame: held inputs re-assert via poll() next frame
        self._ax_x = self._ax_y = 0.0
        self._orbit_az = self._orbit_el = 0.0
        self._zoom_dir = 0.0

    # ---------------------------------------------------------- quiz flow
    def _option(self, label: str):
        for o in self._spec.options:
            if o.label == label:
                return o
        return None

    def _quiz_select(self, label: str) -> None:
        """Select + play that option's wav (looping) THROUGH THE ENGINE
        (engine.set_voices([]) first: the land falls silent while an option
        plays -- options and live terrain never sound together)."""
        opt = self._option(label)
        if opt is None:
            return
        self._selected = label
        self._playing = label
        self._explain = ""                 # a fresh listen, a fresh mind
        self._success = False
        self._engine.set_voices([])        # the land falls silent (G4.3)
        self._voices = []
        self._engine.set_quiz_wav(opt.wav_path)     # approved amendment
        self._mode = Mode.QUIZ_LISTEN

    def _quiz_confirm(self) -> None:
        """Correct: success_text, celebration, advance via campaign order.
        Wrong: show that option's 'explain' gently, stay, retry allowed
        forever. Hint used: no penalty, no record (SUTRAS 5.1/5.2)."""
        opt = self._option(self._selected) if self._selected else None
        if opt is None:
            return
        if opt.correct:
            self._success = True
            self._explain = ""
            self._hint_open = False
            self._mode = Mode.SCENE_TRANSITION
            self._transition_timer = _TRANSITION_SEC
            # the winning groove keeps looping through the celebration
        else:
            self._explain = opt.explain    # teaching, never scolding (5.2)
            # stay in QUIZ_LISTEN: the sound keeps playing so their ears
            # can follow the kind words describing it

    def _resume_land(self) -> None:
        self._engine.set_quiz_wav(None)
        self._playing = None
        self._mode = Mode.EXPLORE
        self._push_voices()

    def _advance_scene(self) -> None:
        self._engine.set_quiz_wav(None)
        self._playing = None
        if (self._scene_index is not None
                and self._scene_index + 1 < len(self._order)):
            self._scene_index += 1
            self._mode = Mode.EXPLORE
            self._load_scene(self._order[self._scene_index])
        else:
            # the Fog Summit was climbed: free play on the final map,
            # success_text (the closing line) stays on screen
            self._campaign_complete = True
            self._mode = Mode.EXPLORE
            self._push_voices()

    # ---------------------------------------------------------- slice flow
    def _enter_slice(self) -> None:
        self._return_xy = (self._totem.x, self._totem.y)
        self._plane = SlicePlane(self._totem.x, self._totem.y,
                                 0.0, 0.0, True)
        self._walk_path = []
        self._walking = False
        self._mode = Mode.SLICE

    def _exit_slice(self) -> None:
        self._plane.visible = False
        self._walking = False
        self._walk_path = []
        if self._return_xy is not None:    # the Totem returns to the players
            self._totem.x, self._totem.y = self._clamp_domain(
                *self._return_xy)
        self._push_voices()
        self._mode = Mode.EXPLORE

    def _start_walk(self) -> None:
        self._walk_path = self._build_slice_path()
        self._walk_idx = 0
        self._walking = bool(self._walk_path)

    def _build_slice_path(self) -> list:
        """SAME transect definition as GlassBlade.intersection_path (G3.6):
        straight line in (x,y) through (cx,cy) along yaw, clipped to the
        domain by slab intersection, one stop per RING_WIDTH."""
        p = self._plane
        xmin, xmax, ymin, ymax = self._spec.domain
        dx = math.cos(math.radians(p.yaw_deg))
        dy = math.sin(math.radians(p.yaw_deg))
        tmin, tmax = -1e18, 1e18
        for c, d, lo, hi in ((p.cx, dx, xmin, xmax),
                             (p.cy, dy, ymin, ymax)):
            if abs(d) < 1e-9:
                if not lo <= c <= hi:
                    return []
                continue
            t0, t1 = (lo - c) / d, (hi - c) / d
            if t0 > t1:
                t0, t1 = t1, t0
            tmin, tmax = max(tmin, t0), min(tmax, t1)
        if tmax <= tmin:
            return []
        path = []
        t = tmin
        while t < tmax - 1e-9:
            path.append((p.cx + t * dx, p.cy + t * dy))
            t += _WALK_STEP
        path.append((p.cx + tmax * dx, p.cy + tmax * dy))
        return path

    # ------------------------------------------------------- read seams
    def quiz_ui_state(self) -> dict:
        """Everything hud.draw needs: selected label, playing label,
        hint_open, explanation text, success state."""
        return {
            "selected": self._selected,
            "playing": self._playing,
            "hint_open": self._hint_open,
            "explain": self._explain,
            "success": self._success,
            "campaign_complete": self._campaign_complete,
        }

    def snapshot(self) -> dict:
        """Read-only bundle for main's draw calls: mode, totem, voices,
        slice plane, current SceneSpec. scene_changed is read-and-clear:
        main calls snapshot() exactly once per frame (G4.5)."""
        changed = self._scene_changed
        self._scene_changed = False
        return {
            "mode": self._mode,
            "totem": self._totem,
            "voices": self._voices,
            "slice_plane": self._plane,
            "scene": self._spec,
            "scene_changed": changed,
            "quit": self._quit,
            "campaign_complete": self._campaign_complete,
        }


_ANSWER_ACTIONS.update({
    Action.ANSWER_A: "A", Action.ANSWER_B: "B",
    Action.ANSWER_C: "C", Action.ANSWER_D: "D",
})
