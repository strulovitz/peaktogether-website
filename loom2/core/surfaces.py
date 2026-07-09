"""
LOOM2 -- core/surfaces.py
The Surface Catalog as code. PURE MATH, vectorization-friendly (floats or
numpy arrays in, same shape out). Allowed imports: numpy, math, config.
Child chat scope: implement all bodies. ~120 lines expected.

------------------------------------------------------------------------------
IMPLEMENTATION NOTES (Parent G, 2026-07-08)

WHO CALLS THESE FUNCTIONS, AND WITH WHAT:
  * graphics/terrain.py (TerrainMesh)  -- 2-D numpy meshgrid arrays (the whole
    land in one call). Vectorization is LOAD-BEARING here, not a nicety.
  * graphics/totem.py / slice draping  -- 1-D numpy arrays (rings, cut paths).
  * core/game_state.py via audio/musicians.py -- plain Python float scalars,
    one musician seat at a time (musicians.build_voices coerces with float(),
    verified by DeepSeek: musicians.py:74, so np.float64 out is fine).
  * core/slicing.py (marching squares over g(x,y)) -- 2-D arrays again.

THE CONTRACT, RESTATED PLAINLY:
  floats in  -> float-like scalar out (builtin float or np.float64, both fine)
  arrays in  -> array of the SAME SHAPE out
  No file access, no state, no randomness, no imports beyond the header.
  Every function is a pure mathematical field z = f(x, y) over the plane.

STYLE DECISIONS (reported for transparency, per Nir's honesty ruling):
  * Only numpy is imported. `math` and `config` are ALLOWED by the header but
    NOT NEEDED (numpy ufuncs handle scalars and arrays uniformly; no config
    constant is consumed here) -- unused imports would be clutter, so they
    are deliberately omitted.
  * The frozen formula coefficients appear as LITERALS in each body, matching
    the scripture comments character-for-character where possible, so a reader
    can verify body-against-comment at a glance.
  * `ridge` ignores y mathematically, but the shape contract still demands
    "arrays in, same shape out" even when ONLY y is an array. A `+ 0.0 * y`
    shape-keeper term (mathematically zero) guarantees correct numpy
    broadcasting in every input combination. See ridge's docstring.
  * K_CANNON and the scene-12 design domain were delegated to Parent G by Nir
    (DeepSeek Q11 answer, 2026-07-08); the full reasoning is in the comment
    block above cannon_range.

A NOTE ON WHAT THE PLAYERS HEAR (why the docstrings talk about gradients):
  In LOOM2, height IS pitch (z = 0 is the A4 = 440 Hz line; one octave per
  scene.z_per_octave world units). So for every surface below:
      the VALUE  f(x, y)          is the note a musician seated there plays;
      the GRADIENT (df/dx, df/dy) is how fast the music climbs as the totem
                                   walks -- the steeper the land, the faster
                                   the melody rises under the players' hands.
  Each docstring therefore records the value, the gradient, the critical
  points, and the sonic character. These are teaching surfaces; the file
  should teach too.
------------------------------------------------------------------------------
"""

import numpy as np


# =============================================================================
# ACT I SURFACES -- planes and bowls: the first sounds of slope and depth
# =============================================================================

def ramp(x, y):
    """z = 0.55x + 0.30y  -- an inclined plane, the simplest singing land.

    Mathematics:
      * Linear in both variables: a flat tilted sheet, no curvature at all.
      * Gradient is CONSTANT everywhere: (0.55, 0.30). Steepest ascent points
        in that fixed direction (about 28.6 degrees north of east); the slope
        magnitude is sqrt(0.55^2 + 0.30^2) ~= 0.626 world units of height per
        unit walked.
      * No critical points anywhere -- the land rises forever one way and
        falls forever the other.
      * Level curves: parallel straight lines 0.55x + 0.30y = c.

    What the players hear: walk east and the pitch climbs steadily, almost
    twice as fast as walking north (0.55 vs 0.30). Walk along a level line
    and the whole orchestra holds one chord, unmoving. Slope made audible.
    """
    return 0.55 * x + 0.30 * y


def bowl(x, y):
    """z = 0.16(x^2 + y^2) - 1.0  -- a circular paraboloid: the lake!

    Mathematics:
      * Radially symmetric: z depends only on r^2 = x^2 + y^2, so
        z = 0.16 r^2 - 1.0.
      * Gradient (0.32x, 0.32y) always points straight AWAY from the origin:
        every direction out of the bottom is uphill.
      * Unique critical point at (0, 0): a strict GLOBAL MINIMUM, z = -1.0.
        Hessian is 0.32 * I (positive definite) -- textbook pit.
      * Level curves: concentric circles. The waterline z = 0 is the circle
        r = 2.5 -- inside it the land dips BELOW the A4 line ("lake!" per the
        scripture comment: the low notes live underwater).

    What the players hear: at the exact bottom, the deepest chord of the
    scene; step ANY direction and the pitch rises identically. A pit sounds
    the same all around -- that symmetry is the lesson.
    """
    return 0.16 * (x ** 2 + y ** 2) - 1.0


def hill(x, y):
    """z = 3.4*exp(-(x^2+y^2)/7) - 0.6  -- a Gaussian mountain on a low plain.

    Mathematics:
      * Radially symmetric bump: z = 3.4 exp(-r^2 / 7) - 0.6.
      * Unique critical point at (0, 0): a strict GLOBAL MAXIMUM, z = +2.8
        (3.4 - 0.6). Far from the peak, the land flattens toward the plain
        level z -> -0.6 (asymptote, never quite reached).
      * Gradient: (-(2/7) * 3.4 * exp(-r^2/7)) * (x, y) -- it always points
        back toward the summit when negated; the mountain "pulls uphill"
        toward the origin from every direction.
      * The steepest ring of the mountainside sits at r = sqrt(7/2) ~= 1.87
        (the inflection ring of the Gaussian profile); beyond it the slope
        gentles out into the plain.

    What the players hear: a soaring summit note at the center (+2.8, well
    above A4), sliding down through the mountainside into a low, broad plain
    hum (-0.6, below A4) -- the only Act surface where the melody has both a
    clear top AND an endless quiet skirt.
    """
    return 3.4 * np.exp(-(x ** 2 + y ** 2) / 7) - 0.6


def ridge(x, y):
    """z = 1.8 - 0.22x^2  (no y!)  -- a parabolic mountain ridge running north-south.

    Mathematics:
      * A CYLINDER surface: y does not appear. Every cross-section at constant
        y is the same downward parabola; the crest is the entire LINE x = 0,
        at constant height z = 1.8.
      * Gradient: (-0.44x, 0). Walking parallel to the ridge (constant x)
        changes NOTHING -- df/dy = 0 identically. The crest line is a
        degenerate critical SET (not an isolated point): maximum across,
        flat along.
      * Level curves: pairs of straight lines x = +/- const.

    What the players hear: THE HELD NOTE. Walk north-south anywhere and the
    orchestra freezes on one pitch forever; turn east-west and the melody
    arcs over the crest and falls away. One direction is music standing
    still -- that is what "no y" sounds like.

    Vectorization note (shape contract): because y is mathematically absent,
    a naive body would return a SCALAR when x is a float but y is an array,
    violating "same shape out". The `+ 0.0 * y` term is exactly zero
    everywhere yet forces numpy to broadcast the result to the full input
    shape in every scalar/array combination. It is a shape-keeper, not math.
    """
    return 1.8 - 0.22 * x ** 2 + 0.0 * y


def ridge_y(x, y):
    """z = 1.8 - 0.22y^2  (no x!)  -- mirror of ridge: x is absent.

    The eastern sibling of the ridge. Every east-west row is frozen at one
    pitch; the staircase runs north-south. Exists so the quiz can play
    ∂f/∂x=0 right next to ∂f/∂y=0 — the mirror IS the lesson (Parent H).
    """
    return 1.8 - 0.22 * y ** 2 + 0.0 * x


# =============================================================================
# ACT II SURFACES -- saddles: where "which way you walk" changes everything
# =============================================================================

def saddle(x, y):
    """z = 0.16(x^2 - y^2)  -- the canonical saddle point at the origin.

    Mathematics:
      * Critical point at (0, 0) with z = 0: gradient (0.32x, -0.32y)
        vanishes there, but it is neither peak nor pit.
      * Hessian diag(0.32, -0.32): one positive, one negative eigenvalue --
        the textbook SADDLE. Along the x-axis the origin is a minimum
        (land rises both ways); along the y-axis it is a maximum (land falls
        both ways).
      * Level curves: hyperbolas x^2 - y^2 = const; the level set z = 0 is
        the crossed pair of lines y = +/- x, meeting at the saddle itself.

    What the players hear: stand at the origin -- silence on the A4 line.
    Walk east: the pitch RISES. Walk north: the pitch FALLS. Same starting
    point, opposite melodies. This is the whole quiz of test_saddle in one
    sentence: "up one way, down the other." (data/scenes/test_saddle is the
    live ground-truth scene for this surface.)
    """
    return 0.16 * (x ** 2 - y ** 2)


def field(x, y):
    """z = 0.16*x*y  (Babylon; rotated saddle)  -- the same saddle, turned 45 degrees.

    Mathematics:
      * Substituting the 45-degree rotation u = (x+y)/sqrt(2),
        v = (x-y)/sqrt(2) into 0.16(u^2 - v^2) yields exactly 0.32*x*y --
        so 0.16*x*y IS the saddle surface rotated 45 degrees (at half
        amplitude): same animal, new clothes.
      * Critical point at (0, 0), z = 0; gradient (0.16y, 0.16x); Hessian
        off-diagonal (eigenvalues +/-0.16) -- a saddle whose up-valleys lie
        along the DIAGONAL y = x (quadrants I and III rise, II and IV fall).
      * Level set z = 0 is the coordinate AXES themselves: walk due east
        from the origin and the pitch holds; walk diagonally and it moves.

    What the players hear: the saddle's lesson again, but the special
    directions have moved -- proof that "saddle-ness" is about the shape,
    not about which way the map happens to be printed. The irrigated fields
    of Babylon, rising toward two corners, sinking toward two.
    """
    return 0.16 * x * y


# =============================================================================
# ACT III SURFACES -- richer lands: periodicity and a threefold saddle
# =============================================================================

def egg_carton(x, y):
    """z = 1.6*sin(1.5x)*sin(1.5y)  -- a doubly periodic field of peaks and pits.

    Mathematics:
      * Periodic in both directions with spatial period 2*pi/1.5 ~= 4.19
        world units; height swings between +1.6 and -1.6.
      * An infinite checkerboard of critical points: PEAKS (+1.6) where both
        sines are +1 or both -1, PITS (-1.6) where they disagree, and
        SADDLES (z = 0) at the grid points between them where either sine
        vanishes -- e.g. the origin itself is a saddle of this surface.
      * Gradient: (2.4*cos(1.5x)*sin(1.5y), 2.4*sin(1.5x)*cos(1.5y)).

    What the players hear: a landscape that CHANTS -- walk any straight line
    and the melody repeats, wave after wave. Every lesson of Acts I-II
    (peak, pit, saddle) appears again and again, tiled forever. Counting
    "how many steps until the tune comes back" is hearing the period.
    """
    return 1.6 * np.sin(1.5 * x) * np.sin(1.5 * y)


def egg_carton_1x1(x, y):
    """z = 1.6*sin(0.75x)*sin(0.75y)  -- sparse: ~1 swell per totem circle.

    Same amplitude as egg_carton (1.6), half the wave number (0.75 vs 1.5).
    Half-wavelength ~4.19 — one peak or trough inside the 2×R=5 hearing
    diameter. Used by Scene 10 quiz options A & B (Parent H).
    """
    return 1.6 * np.sin(0.75 * x) * np.sin(0.75 * y)


def egg_carton_3x3(x, y):
    """z = 1.6*sin(2.25x)*sin(2.25y)  -- dense: ~3 swells per totem circle.

    Same amplitude as egg_carton (1.6), 1.5× the wave number (2.25 vs 1.5).
    Half-wavelength ~1.40 — three peaks per crossing inside the hearing
    diameter. Used by Scene 10 quiz option D (Parent H).
    """
    return 1.6 * np.sin(2.25 * x) * np.sin(2.25 * y)


def monkey_saddle(x, y):
    """z = 0.08(x^3 - 3x*y^2)  -- the monkey saddle: three valleys, three ridges.

    Mathematics:
      * In polar coordinates this is z = 0.08 * r^3 * cos(3*theta): a
        threefold-symmetric wave around the origin -- three uphill sectors
        and three downhill sectors, alternating every 60 degrees. (A saddle
        for a monkey: two legs down, and one more valley for the tail.)
      * The origin is a DEGENERATE critical point: gradient
        (0.24(x^2 - y^2), -0.48xy) vanishes there AND the entire Hessian is
        the zero matrix -- the second-derivative test says nothing. The
        classification tools of the ordinary saddle genuinely fail here;
        only walking (or listening!) reveals the shape.
      * Level set z = 0: THREE lines through the origin (theta = 30, 90,
        150 degrees and their opposites), where cos(3*theta) = 0.
      * Growth is cubic in r: gentle near the center, then steepening fast.

    What the players hear: from the center, six different stories depending
    on heading -- rise, fall, rise, fall, rise, fall -- changing every 60
    degrees of the compass. The land that cannot be summarized by "up or
    down": you must turn and listen.
    """
    return 0.08 * (x ** 3 - 3 * x * y ** 2)


# =============================================================================
# THE FINALE SURFACE -- physics itself as terrain
# =============================================================================

# -----------------------------------------------------------------------------
# CANNON RANGE -- design-time scaling.
# DECISION DELEGATED TO PARENT G by Nir (DeepSeek Q11 answer, 2026-07-08):
# "pick k so the full cannon surface fits beautifully... the whole parabola
#  visible", bake it as a named constant with the reasoning in a comment.
#
# Physics: a projectile launched at speed v and elevation theta travels a
# range R = v^2 * sin(2*theta) / g. This surface plots RANGE as HEIGHT, so
# the terrain the players hear IS the range formula: silent (z = 0) at
# theta = 0 and theta = 90 (the shot goes nowhere), singing highest along the
# 45-degree sweet-spot ridge, and growing quadratically with launch speed.
#
# DESIGN DOMAIN assumed for scene 12 (the scene JSON does not exist yet --
# content author: keep or adapt these ranges, and keep this comment honest
# if you change them!):
#     x = v      in [0, 10]    launch speed  (arbitrary game units)
#     y = theta  in [0, 90]    launch elevation, in DEGREES (converted here)
#
# Over that domain, z spans [0, K_CANNON * 10^2 * 1] = [0, 100 * K_CANNON].
# K_CANNON = 0.03 places the global maximum -- the perfect shot at
# (v = 10, theta = 45) -- at z = +3.0: a summit comfortably inside the
# orchestra's range and just above the hill's peak (+2.8), so the farthest
# cannon shot in the campaign is also its highest note. With the default
# camera pulled back (Nir's instinct: "see the whole battlefield from a
# distance"), a z-span of [0, 3] over a 10 x 90 (unit-squashed by the mesh
# domain) land keeps the entire parabola-in-theta in frame at default zoom.
# (For scale: real gravity would give k = 1/g ~= 0.102 -- K_CANNON is a
# stage-scaling of the same law, not different physics.)
# -----------------------------------------------------------------------------
K_CANNON = 0.03


def cannon_range(x, y):
    """z = K_CANNON * v^2 * sin(2*theta)  with x = v (speed), y = theta (DEGREES).

    The finale: not a metaphor of a landscape, but a law of physics laid out
    as one. Height is the distance a cannonball flies.

    Mathematics:
      * y arrives in DEGREES (scripture contract) and is converted to
        radians here -- callers never convert.
      * For fixed speed v: z traces sin(2*theta) -- zero at 0 and 90 degrees,
        maximal at exactly 45. The "which angle shoots farthest?" question
        is a RIDGE of this terrain at theta = 45.
      * For fixed angle theta: z grows like v^2 -- the parabola of power.
      * Gradient: dz/dv = 2*K_CANNON*v*sin(2*theta);
        dz/dtheta = 2*K_CANNON*v^2*cos(2*theta) * (pi/180)
        (the degree-to-radian factor lives in the theta-derivative).
        The theta-slope VANISHES along the 45-degree line: walking across
        that line, the music crests -- the audible optimum.

    What the players hear: aim the totem's theta past 45 degrees and the
    pitch falls even though the cannon points "higher" -- the surface sings
    the counterintuitive truth of ballistics. The stories were imagined,
    but the mathematics was real.
    """
    theta_rad = np.deg2rad(y)
    return K_CANNON * x ** 2 * np.sin(2.0 * theta_rad)


# =============================================================================
# THE REGISTRY -- scene.json refers to surfaces ONLY by these names (frozen)
# =============================================================================

REGISTRY = {  # scene.json refers to surfaces ONLY by these names
    "ramp": ramp, "bowl": bowl, "hill": hill, "ridge": ridge,
    "ridge_y": ridge_y,
    "saddle": saddle, "field": field, "egg_carton": egg_carton,
    "egg_carton_1x1": egg_carton_1x1, "egg_carton_3x3": egg_carton_3x3,
    "monkey_saddle": monkey_saddle, "cannon_range": cannon_range,
}


def get(name: str):
    """REGISTRY lookup with a clear error message listing valid names.

    Raises KeyError (the natural exception for a failed name lookup) with a
    message that names the offender AND lists every valid surface, sorted --
    this error is a content-author's best friend: a typo in scene.json
    should cost seconds, not minutes. core/scene.py calls this during
    load-time validation, so a bad surface_name fails LOUD at load, never
    mid-game.
    """
    try:
        return REGISTRY[name]
    except KeyError:
        valid = ", ".join(sorted(REGISTRY))
        raise KeyError(
            f"Unknown surface name '{name}'. "
            f"Valid surface names are: {valid}."
        ) from None


# =============================================================================
# SELF-TEST -- run `python -m core.surfaces` from the repo root.
# Additive, zero imports beyond numpy, never executed by the game.
# Verifies the two load-bearing promises of this module:
#   (1) exact values of every frozen formula at hand-computed points,
#   (2) the shape contract: scalars in -> scalar out; arrays in -> same
#       shape out, for EVERY surface and EVERY scalar/array mix (this is
#       the test that catches the `ridge` broadcasting trap).
# =============================================================================

if __name__ == "__main__":
    _CHECKS = [  # (fn, x, y, expected z) -- all hand-computed
        (ramp,          2.0,        1.0,        1.40),    # 1.10 + 0.30
        (bowl,          0.0,        0.0,       -1.00),    # the lake bottom
        (bowl,          2.5,        0.0,        0.00),    # the waterline
        (hill,          0.0,        0.0,        2.80),    # 3.4 - 0.6
        (ridge,         1.0,      123.0,        1.58),    # y truly ignored
        (ridge,         0.0,       -7.0,        1.80),    # the crest line
        (saddle,        2.0,        0.0,        0.64),    # up along x
        (saddle,        0.0,        2.0,       -0.64),    # down along y
        (field,         1.0,        1.0,        0.16),    # quadrant I rises
        (field,         1.0,       -1.0,       -0.16),    # quadrant IV falls
        (egg_carton,    np.pi / 3,  np.pi / 3,  1.60),    # both sines = 1
        (monkey_saddle, 1.0,        0.0,        0.08),    # r^3 cos(3*0)
        (monkey_saddle, -1.0,       0.0,       -0.08),    # threefold flip
        (cannon_range, 10.0,       45.0,        3.00),    # the perfect shot
        (cannon_range, 10.0,       90.0,        0.00),    # straight up: zero
    ]
    for fn, xv, yv, want in _CHECKS:
        got = fn(xv, yv)
        assert np.isclose(got, want, atol=1e-9), (
            f"{fn.__name__}({xv}, {yv}) = {got}, expected {want}")
        assert np.shape(got) == (), (
            f"{fn.__name__} broke the scalar contract: shape {np.shape(got)}")

    _xs = np.linspace(-4.0, 4.0, 33)
    _ys = np.linspace(-4.0, 4.0, 17)
    _X, _Y = np.meshgrid(_xs, _ys)                 # shape (17, 33)
    for _name, _fn in REGISTRY.items():
        _Z = _fn(_X, _Y)                           # 2-D grid (TerrainMesh path)
        assert _Z.shape == _X.shape, f"{_name}: grid shape {_Z.shape} != {_X.shape}"
        assert np.all(np.isfinite(_Z)), f"{_name}: non-finite values on the grid"
        _z1 = _fn(_xs, _xs)                        # 1-D arrays (ring/path path)
        assert np.shape(_z1) == _xs.shape, f"{_name}: 1-D shape {np.shape(_z1)}"
        _zx = _fn(1.0, _ys)                        # scalar x, array y (ridge trap!)
        assert np.shape(_zx) == _ys.shape, f"{_name}: scalar-x mix {np.shape(_zx)}"
        _zy = _fn(_xs, 1.0)                        # array x, scalar y
        assert np.shape(_zy) == _xs.shape, f"{_name}: scalar-y mix {np.shape(_zy)}"

    assert get("saddle") is saddle
    try:
        get("sadle")  # deliberate typo
        assert False, "get() accepted a bad name"
    except KeyError as e:
        assert "Valid surface names are" in str(e)

    print("core/surfaces.py self-test: ALL PASSED "
          f"({len(_CHECKS)} value checks, {len(REGISTRY)} surfaces x 4 shape "
          "mixes, registry lookup + error message). The land is ready to sing.")
