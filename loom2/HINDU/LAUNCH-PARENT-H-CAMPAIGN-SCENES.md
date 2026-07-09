Hello again, Fable! 😊

This is Nir and DeepSeek. We've been building LOOM2 — a two-player game that teaches multivariable calculus through sound. The whole game is assembled and running (all code is done!), and now we need the most important part: the CAMPAIGN CONTENT.

You're being brought in as a creative collaborator to design the 12 scenes that teach the player multivariable calculus through their ears. We think you'll enjoy this — it's the heart of the game, and your sensibilities about teaching, pacing, and wonder are exactly what we need.

---

## What LOOM2 Is (in one breath)

A mathematical surface z = f(x, y) becomes music. Players plant a "Listening Totem" on the landscape and hear every musician inside its hearing circle play at once — height→pitch, compass angle→timbre, distance from totem→rhythm. The screen is split 50/50: left = Cartesian terrain, right = the "helix" (the orchestra visualized as a coil). A scene is a surface + quiz questions that test whether the player truly heard the math.

The core idea: a surface is not a melody, it's an ORCHESTRA. Moving the totem re-orchestrates the song.

---

## The 9 Surfaces We Have (with their teaching purpose)

Each surface is a pure Python function z = f(x, y). The players walk the land and hear it — and each surface was designed to teach a specific concept. Their complete docstrings (mathematics + what-players-hear) are below. You can choose from these or suggest new ones.

### act i — planes and bowls: the first sounds of slope and depth

**`ramp`** — z = 0.55x + 0.30y, an inclined plane.
The simplest singing land. Linear, no curvature. Gradient is CONSTANT everywhere. Walk east and pitch climbs steadily; walk along a level line and the whole orchestra holds one chord. Slope made audible.

**`bowl`** — z = 0.16(x² + y²) − 1.0, a circular paraboloid.
Radially symmetric pit. Unique CRITICAL POINT at the origin: a strict GLOBAL MINIMUM. Step any direction from the bottom and the pitch rises identically. The waterline z=0 is at r=2.5.

**`hill`** — z = 3.4·exp(−(x²+y²)/7) − 0.6, a Gaussian mountain.
Radially symmetric bump, unique GLOBAL MAXIMUM at the origin (+2.8). Far from the peak the land flattens toward −0.6 (asymptote). The only surface where the melody has both a clear top AND an endless quiet skirt.

**`ridge`** — z = 1.8 − 0.22x² (y is absent), a parabolic mountain ridge.
A CYLINDER surface. The crest is the entire LINE x=0 at constant height. Walk north-south anywhere and the orchestra freezes on one pitch forever; turn east-west and the melody arcs. One direction is music standing still.

### act ii — saddles: where "which way you walk" changes everything

**`saddle`** — z = 0.16(x² − y²), the canonical saddle point.
Critical point at the origin. Hessian has one positive, one negative eigenvalue. Along x: a minimum (land rises both ways). Along y: a maximum (land falls both ways). The classic "up one way, down the other."

**`field`** — z = 0.16·x·y, the same saddle rotated 45° (Babylon).
Same animal, new clothes. Up-valleys lie along the diagonal y=x. Proves that "saddle-ness" is about shape, not map orientation. The irrigated fields of Babylon, rising toward two corners, sinking toward two.

### act iii — richer lands: periodicity and a threefold saddle

**`egg_carton`** — z = 1.6·sin(1.5x)·sin(1.5y), a doubly periodic field.
Infinite checkerboard of peaks, pits, and saddles tiled forever. Walk any straight line and the melody repeats, wave after wave. Every prior lesson appears again and again — hearing the period IS the lesson.

**`monkey_saddle`** — z = 0.08(x³ − 3xy²), three valleys, three ridges.
Threefold symmetry. The origin is a DEGENERATE critical point — the Hessian is the zero matrix entirely, so the 2nd-derivative test says nothing. Six different stories depending on heading (rise/fall/rise/fall/rise/fall every 60°). The land that cannot be summarized.

### finale — physics itself as terrain

**`cannon_range`** — z = 0.03·v²·sin(2θ), with x=v (launch speed), y=θ (elevation in degrees).
Not a metaphor — a law of physics laid out as a landscape. Height = the distance a cannonball flies. Zero at θ=0 and θ=90, maximal at exactly 45°. The terrain sings the counterintuitive truth of ballistics: aim higher than 45° and the pitch falls. This is Tartaglia's cannon, and the 45° optimum is the ridge the players must hear.

---

## The Curriculum (7 topics, in order)

1. functions of two variables / surfaces
2. level curves / contour maps
3. partial derivatives
4. directional derivatives & gradient
5. critical points (max/min/saddle)
6. second-derivative test
7. optimization by ear

Double integrals were dropped (no good way to hear volume without cacophony).

---

## What a Scene Looks Like

Each scene lives in `data/scenes/<scene_id>/` and contains:

```
scene_id/
  scene.json    ← the scene definition (see below)
  equation.png  ← LaTeX equation rendered in yellow with black outline
  option_a.wav  ← quiz option audio (pre-rendered by the audio engine)
  option_b.wav
  option_c.wav
  option_d.wav
  options.json  ← instructions for the offline WAV renderer
```

Here is the one scene that already exists, as a concrete example:

**`data/scenes/test_saddle/scene.json`:**
```json
{
  "scene_id": "test_saddle",
  "title_lines": [
    "TEST SCENE — the Saddle 🐎",
    "Listen: does the ground rise or fall?",
    "Move the Totem to explore. 🎧"
  ],
  "surface_name": "saddle",
  "equation_png": "data/scenes/test_saddle/equation.png",
  "totem_start": [0.0, 0.0],
  "domain": [-4.0, 4.0, -4.0, 4.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Is the origin a peak, a pit, or a saddle?",
  "hint_lines": [
    "A saddle goes UP one way and DOWN the other. 💡"
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/test_saddle/option_a.wav", "correct": false,
      "explain": "Not a peak — one direction goes downhill. 🙂" },
    { "label": "B", "wav_path": "data/scenes/test_saddle/option_b.wav", "correct": false,
      "explain": "Not a pit — one direction goes uphill. 🙂" },
    { "label": "C", "wav_path": "data/scenes/test_saddle/option_c.wav", "correct": true,
      "explain": "" },
    { "label": "D", "wav_path": "data/scenes/test_saddle/option_d.wav", "correct": false,
      "explain": "Not flat — the ground really curves. 🙂" }
  ],
  "camera_limits": { "target": [0, 0, 0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 14.0 },
  "success_text": "YES! A saddle — up one way, down the other. 🎉"
}
```

**`data/scenes/test_saddle/options.json`:**
```json
{
  "A": {"surface": "bowl",   "xy": [0.0, 0.0], "radius": 2.5, "out": "data/scenes/test_saddle/option_a.wav"},
  "B": {"surface": "hill",   "xy": [0.0, 0.0], "radius": 2.5, "out": "data/scenes/test_saddle/option_b.wav"},
  "C": {"surface": "saddle", "xy": [0.0, 0.0], "radius": 2.5, "out": "data/scenes/test_saddle/option_c.wav"},
  "D": {"surface": "ramp",   "xy": [0.0, 0.0], "radius": 2.5, "out": "data/scenes/test_saddle/option_d.wav"}
}
```

The options.json tells the offline WAV renderer what surface, position, and radius to render each quiz option from. Players listen to all four options (looping) and choose which one matches the landscape they're standing on.

A few notes about the scene JSON format:
- `title_lines`: 1–3 lines shown at the top of the screen (white text, black outline). Emojis welcome.
- `surface_name`: must match one of the 9 surfaces above (or a new one, if you invent one).
- `domain`: [xmin, xmax, ymin, ymax] — the rectangular land the players can walk.
- `mesh_step`: grid spacing for the terrain triangles (~0.2–0.5 is typical).
- `z_per_octave`: how many world units = one musical octave. Bigger = compressed pitch range.
- `totem_start`: [x, y] where the listening totem appears when the scene loads.
- `question`: one line, shown in the quiz bar at the bottom.
- `hint_lines`: 1–3 lines shown when the player presses H.
- `options`: exactly 4 (A/B/C/D), exactly one marked `correct: true`.
- `explain`: shown after a wrong answer. Can be empty for the correct option.
- `success_text`: shown when the player picks correctly.
- `camera_limits`: optional (the defaults in the example are fine for most scenes). `distance` = camera zoom-out height.

---

## What We Need From You

**12 campaign scenes** that walk the player through the 7 curriculum topics, each centered on a surface (or surfaces — a scene can use multiple surfaces for its quiz options), each with a quiz that tests whether the player truly HEARD the math.

Some scenes from Nir's notes and the game's lore we've been imagining:
- Hannibal's saddle (crossing the Alps — a saddle pass)
- Babylon (the irrigated field — a rotated saddle)
- Tartaglia's cannon (optimization — finding the 45° maximum)
- Fog Summit (maybe a ridge in the mist?)

But these are just seeds — you should own the creative direction. The surfaces are tools; the scenes are the stories that make them memorable.

---

## The Workflow

We imagine it going like this:
- You draft scenes — scenario text, quiz questions, hints, wrong-answer explanations, which surface for each, where on the domain interesting things happen.
- Nir reads, responds by taste, adjusts character/text/feel. He is the final creative authority.
- DeepSeek handles the mechanical work: renders quiz WAVs from the audio engine, renders equation PNGs from LaTeX, writes the JSON files, makes everything compile and run.

You don't need to write JSON — describe the scenes, and we'll encode them.

---

## Where Things Stand Now

The entire game code is complete and running. Only one scene exists (test_saddle). The campaign.json currently just lists `["test_saddle"]`. There's a render_equations.py tool that takes a LaTeX string and produces the yellow+black-outline equation PNG. There's an offline audio renderer that takes surface+position+radius and produces a quiz option WAV with the full 13-instrument orchestra.

Nir has been playing the game with a joystick and Xbox controller and it works great. 😊

---

We're excited to see what you come up with! This is the soul of the game — the part the players will remember. 🎵🏔️
