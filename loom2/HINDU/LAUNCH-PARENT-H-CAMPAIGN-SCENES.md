Hello again, Fable! 😊

This is Nir and DeepSeek. We've been building LOOM2 — a two-player game that teaches multivariable calculus through sound. The whole game is assembled and running (all code is done!), and now we need the most important part: the CAMPAIGN CONTENT.

You're being brought in to flesh out 12 campaign scenes into complete, playable scene.json files. The creative vision for each scene was already designed (by Fable, in the UPANISHADS scripture). Your job is to take those designs and fill in all the details: precise domains, totem start positions, quiz option audio descriptions, LaTeX equations, hint texts, wrong-answer explanations, success messages, and camera limits.

---

## What LOOM2 Is (in one breath)

A mathematical surface z = f(x, y) becomes music. Players plant a "Listening Totem" on the landscape and hear every musician inside its hearing circle play at once — height→pitch, compass angle→timbre, distance from totem→rhythm. The screen is split 50/50: left = Cartesian terrain, right = the helix (the orchestra visualized as a coil). A scene is a surface + a four-option listening quiz.

---

## The 9 Surfaces (each a pure function z = f(x,y))

Each surface was designed to teach a specific concept. Their complete docstrings (math + what-players-hear):

### act i — planes and bowls

**`ramp`** — z = 0.55x + 0.30y, an inclined plane.
Linear, no curvature. Gradient is CONSTANT everywhere. Walk east and pitch climbs steadily; walk along a level line and the whole orchestra holds one chord. Slope made audible.

**`bowl`** — z = 0.16(x² + y²) − 1.0, a circular paraboloid.
Radially symmetric pit. Unique GLOBAL MINIMUM at origin (−1.0). Step any direction from the bottom and pitch rises identically. Waterline z=0 at r=2.5.

**`hill`** — z = 3.4·exp(−(x²+y²)/7) − 0.6, a Gaussian mountain.
Radially symmetric bump, unique GLOBAL MAXIMUM at origin (+2.8). Far from the peak the land flattens toward −0.6 (asymptote). Both a clear top AND an endless quiet skirt.

**`ridge`** — z = 1.8 − 0.22x² (y is absent), a parabolic mountain ridge.
A CYLINDER surface. Crest is the entire LINE x=0 at height 1.8. Walk north-south and the orchestra freezes on one pitch forever; turn east-west and the melody arcs. One direction is music standing still.

### act ii — saddles

**`saddle`** — z = 0.16(x² − y²), the canonical saddle.
Critical point at origin. Hessian: one positive, one negative eigenvalue. Along x: minimum (land rises both ways). Along y: maximum (land falls both ways). "Up one way, down the other."

**`field`** — z = 0.16·x·y, the same saddle rotated 45° (Babylon).
Up-valleys along the diagonal y=x. Proves "saddle-ness" is about shape, not map orientation.

### act iii — richer lands

**`egg_carton`** — z = 1.6·sin(1.5x)·sin(1.5y), a doubly periodic checkerboard.
Infinite peaks, pits, and saddles tiled forever. Walk any straight line and the melody repeats, wave after wave.

**`monkey_saddle`** — z = 0.08(x³ − 3xy²), three valleys, three ridges.
Threefold symmetry. Origin is DEGENERATE — Hessian is zero matrix, 2nd-derivative test says nothing. Six different stories depending on heading, changing every 60°.

### finale

**`cannon_range`** — z = 0.03·v²·sin(2θ), with x=v (launch speed), y=θ (elevation in degrees).
Physics as terrain. Height = cannonball distance. Zero at θ=0 and θ=90, maximal at exactly 45°. The 45° optimum is the ridge the players must hear. (Design domain: v ∈ [0, 10], θ ∈ [0, 90°]; peak at z=+3.0.)

---

## The Campaign — 12 Scenes in 7 Acts (from the UPANISHADS)

Here is the complete scene plan, exactly as it was designed. Your job is to turn each one into a full scene.json with all the specifics filled in.

### ACT I — Surfaces (Stage 1)

**Scene 1: The Roman Road (ramp)**
Aqueduct engineers need a steady slope. Which sound is the constant slope?
- Surface: `ramp` — a plane with gradient everywhere the same

**Scene 2: The Granary of Egypt (hill)**
A heap of grain; stand on the summit, the chord hangs below you. Which sound is the top of the heap?
- Surface: `hill` — a Gaussian dome with a unique maximum

**Scene 3: The Valley Basin (bowl)**
A blue lake below A440. Which sound is the bottom of the valley?
- Surface: `bowl` — a circular paraboloid with a unique minimum

**Scene 4: The Rain Gutter (ridge)**
Which sound is the ridge? First taste of "one player changes nothing."
- Surface: `ridge` — z depends only on x, y is absent

### ACT II — Level Curves (Stage 2)

**Scene 5: The Rice Terraces of Banaue (hill, level walk)**
Farmers need paths of constant height. Which sound is a level walk — the unison?
- Surface: `hill` — same surface as Scene 2, but quiz is about LEVEL WALKS
- Quiz angle: walk along a contour = constant pitch = unison chord

### ACT III — Partial Derivatives (Stage 3)

**Scene 6: The Ridge, Revisited (ridge, ∂f/∂x and ∂f/∂y)**
His hand is ∂f/∂x, hers is ∂f/∂y. In which sound does only ONE player's movement matter?
- Surface: `ridge` — same as Scene 4, but now the quiz names the concept out loud

### ACT IV — Gradient (Stage 4)

**Scene 7: Water Finds the Way (hill, steepest descent)**
Water flows perpendicular to contours. Which sound is the steepest climb?
- Surface: `hill` — quiz is about the gradient direction

### ACT V — Critical Points (Stage 5)

**Scene 8: Hannibal at the Pass (saddle)**
The FLAGSHIP scene. 218 BC. Hannibal's army stands before the Alps. The scouts must find the pass — the one place where the mountain lets you through.
- Surface: `saddle` — the canonical saddle point
- This is the "test_saddle" scene scaled up to campaign quality

**Scene 9: The Fields of Babylon (field, z=xy)**
The oldest two-variable function in history is secretly a rotated saddle. Which sound proves the surveyor's field-corner is a saddle?
- Surface: `field` — same math as saddle, rotated 45°

**Scene 10: The Ocean Swell (egg_carton)**
Summits, valleys, and passes repeating. Distinct critical points repeating in all directions.
- Surface: `egg_carton` — doubly periodic checkerboard of peaks, pits, and saddles
- 🌊 Note: the original UPANISHADS proposed a richer "match each groove" format for this scene rather than plain A/B/C/D. Nir hasn't yet decided whether to keep the richer format or flatten it. Present your thoughts if you have them, or assume standard A/B/C/D for now.

### ACT VI — Second-Derivative Test (Stage 6)

**Scene 11: The Three Chairs (bowl vs saddle vs monkey_saddle)**
Where the classic second-derivative test fails. Pure classification by chord quality.
- Surface: `monkey_saddle` — the Hessian is zero; the test says nothing. But the ear knows.
- Quiz: which is which — bowl, saddle, monkey saddle — by ear alone?

### ACT VII — Optimization (Stage 7)

**Scene 12: Tartaglia's Cannon (cannon_range) / The Fog Summit**
The range surface R(v,θ) — players discover the summit at 45° by ear. Then the finale: The Fog Summit — the map dims to near-black, and the players find the highest peak by ear alone.
- Surface: `cannon_range` — physics as terrain, x = launch speed, y = launch angle
- Design domain: v ∈ [0, 10], θ ∈ [0, 90°]; peak at (v=10, θ=45°) → z = +3.0
- This scene may contain both the Tartaglia quiz AND a Fog Summit bonus/finale — or they could be split. Your call how to handle it.
- The closing text (inherited from LOOM1): "Our stories were imagined — but the mathematics, and everything your ears just learned, is real."

---

## Scene Design Rules (from the UPANISHADS — the soul of the game)

These are verbatim from the scriptures. They matter more than any field format.

### The Confusability Rule

> The four options must differ in a **gross audible feature** (unison vs. spread chord, transposing vs. static, above vs. below) — unless the scene's explicit teaching goal is a subtle distinction, in which case the question text says exactly what tiny difference to listen for.

If two quiz options sound too similar, the player has no fair way to choose — the ear can't learn what it can't distinguish. The difference between options should be OBVIOUS to a first-time listener. The teaching happens when they connect "that obvious difference" to the math concept.

### The Kindness Rule

> Every explanation encourages; wrong answers teach; nothing ever shames.

When a player picks wrong:
- The explanation tells them what that sound actually WAS and what to listen for next time
- Wrong-answer text is pink (never red — red means "you failed"; pink means "let's try again")
- No penalty, no score, no timer — they just try again

### Other locked rules

- **HINT is free forever.** Pressing H costs nothing, records nothing, penalizes nothing. The game wants you to succeed.
- **No timers, no scores, no shame. Ever.** (VEDAS)
- **Correct answer → warm celebration, 1–2 sentences connecting sound to idea, on to the next scene.** (UPANISHADS)
- **2–3 lines of scenario text per scene, no more.** The history sets the mood; the music is the star.
- **Emojis are welcome** in title_lines, question, hint_lines, success_text, and explain text.

---

## What a Scene Looks Like (concrete format)

Each scene lives in `data/scenes/<scene_id>/` and requires:

```
scene_id/
  scene.json    ← the scene definition
  equation.png  ← LaTeX equation in yellow with black outline (DeepSeek renders)
  option_a.wav  ← quiz option audio (DeepSeek renders from the audio engine)
  option_b.wav
  option_c.wav
  option_d.wav
  options.json  ← instructions for the offline WAV renderer
```

Here is the one scene that already exists, as reference:

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

**`data/scenes/test_saddle/options.json`** (tells the offline WAV renderer what to render for each quiz option):
```json
{
  "A": {"surface": "bowl",   "xy": [0.0, 0.0], "radius": 2.5, "out": "data/scenes/test_saddle/option_a.wav"},
  "B": {"surface": "hill",   "xy": [0.0, 0.0], "radius": 2.5, "out": "data/scenes/test_saddle/option_b.wav"},
  "C": {"surface": "saddle", "xy": [0.0, 0.0], "radius": 2.5, "out": "data/scenes/test_saddle/option_c.wav"},
  "D": {"surface": "ramp",   "xy": [0.0, 0.0], "radius": 2.5, "out": "data/scenes/test_saddle/option_d.wav"}
}
```

### scene.json field reference

| Field | Type | Notes |
|---|---|---|
| `scene_id` | string | matches the folder name |
| `title_lines` | 1–3 strings | shown at the top of the screen (white+outline). Emojis welcome. |
| `surface_name` | string | one of: ramp, bowl, hill, ridge, saddle, field, egg_carton, monkey_saddle, cannon_range |
| `equation_png` | string | path to the equation image (DeepSeek renders from LaTeX) |
| `totem_start` | [x, y] | where the totem appears when the scene loads; must be inside the domain |
| `domain` | [xmin, xmax, ymin, ymax] | the rectangular land the players can walk |
| `mesh_step` | float | grid spacing for terrain triangles (~0.2–0.5 typical) |
| `z_per_octave` | float | world units per musical octave. 2.0 is standard. Bigger = compressed range. |
| `question` | string | one line, shown in the quiz bar |
| `hint_lines` | 1–3 strings | shown when player presses H |
| `options` | 4 objects | exactly 4, exactly one `correct: true` |
| `options[].label` | string | "A", "B", "C", or "D" |
| `options[].wav_path` | string | path to the pre-rendered WAV |
| `options[].correct` | boolean | exactly one option is true |
| `options[].explain` | string | shown after wrong answer; can be "" for the correct option |
| `camera_limits` | object | optional; defaults: target [0,0,0], zoom_min 0.5, zoom_max 2.5, distance 14.0 |
| `success_text` | string | shown when the player answers correctly |

### options.json field reference

| Field | Notes |
|---|---|
| `surface` | which surface to render for this audio option |
| `xy` | [x, y] position of the totem on that surface |
| `radius` | hearing radius (2.5 is standard, matching the default HEARING_R) |
| `out` | output WAV path |
| `domain` | optional: [xmin, xmax, ymin, ymax] for the musician grid (defaults to reasonable bounds) |
| `step` | optional: grid spacing (defaults to 1.0) |
| `z_per_octave` | optional: overrides the scene's value for this option |

---

## What We'd Love From You

For each of the 12 scenes, fill in the creative details:

- **scene_id** — a short, evocative folder name
- **title_lines** — 2–3 lines of scenario text that set the moment (can use emojis). The UPANISHADS gives you the historical seed for each.
- **surface_name** — which surface (from the UPANISHADS mapping above)
- **equation** — the LaTeX math for equation.png (e.g. `z = x^2 - y^2`). DeepSeek renders these.
- **domain** — [xmin, xmax, ymin, ymax]. Each surface has its own natural scale.
- **mesh_step** — usually 0.25 is fine
- **z_per_octave** — usually 2.0 is fine, but some surfaces might want more/less pitch range
- **totem_start** — where the player begins. Center the interesting math feature.
- **question** — the quiz question, weaving the historical scenario into the math
- **hint_lines** — 1–3 lines, gentle pointer toward what to listen for
- **options** — for each of A/B/C/D: which surface+position to render, whether it's correct, and the wrong-answer explanation
- **camera_limits** — if different from defaults
- **success_text** — celebration with math insight

The scene 10 "match each groove" format, the Fog Summit finale mechanics, and any other special touches are yours to design — the souls of these scenes belong to you.

---

## Where Things Stand

The entire game code is complete and running (parents A through G delivered everything). Only `test_saddle` exists as a scene. `campaign.json` currently just lists `["test_saddle"]`. DeepSeek handles the mechanical work: renders quiz WAVs, renders equation PNGs, writes the JSON files, updates campaign.json.

Nir has been playing the game with joystick and Xbox controller and it works great. He's warm, generous with praise, and makes the final creative calls. 😊

We're excited to see what you bring to these scenes — they are the soul of the game. 🎵🏔️
