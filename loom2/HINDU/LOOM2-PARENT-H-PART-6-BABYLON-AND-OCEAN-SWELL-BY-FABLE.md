Onward! 😊 Here is Part 6 of 8 — the oldest formula on Earth, and the sea you can count.
📜 SCENE 9 — fields_of_babylon (field, z=0.16xy)

Teaching goal: saddle-ness is about shape, not map orientation. The surveyor's corner is Hannibal's pass, rotated 45°.
data/scenes/fields_of_babylon/scene.json

{
  "scene_id": "fields_of_babylon",
  "title_lines": [
    "BABYLON, 1800 BC 📜 The surveyor multiplies length by width —",
    "z = x·y, the oldest two-variable formula on Earth. And at the",
    "field's corner hides a shape you met in the Alps… 🎧🐘"
  ],
  "surface_name": "field",
  "equation_png": "data/scenes/fields_of_babylon/equation.png",
  "totem_start": [0.0, 0.0],
  "domain": [-5.0, 5.0, -5.0, 5.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Which sound is the corner's TWIN — the same shape in disguise? 🌾",
  "hint_lines": [
    "Shape is what your ear keeps when the map turns. 💡",
    "The corner climbs toward NE and SW together, and sinks toward NW and SE —",
    "which recording does the same trick, just with different compass names?"
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/fields_of_babylon/option_a.wav", "correct": false,
      "explain": "A pit rises EVERY way — but the corner climbs along one diagonal and sinks along the other. Not a twin. 🙂" },
    { "label": "B", "wav_path": "data/scenes/fields_of_babylon/option_b.wav", "correct": false,
      "explain": "A crest holds one frozen top line with nothing above it — the corner has voices above AND below A440. Not a twin. 🙂" },
    { "label": "C", "wav_path": "data/scenes/fields_of_babylon/option_c.wav", "correct": false,
      "explain": "One single lean — high toward one side only. The corner climbs toward TWO opposite sides at once. Not a twin. 🙂" },
    { "label": "D", "wav_path": "data/scenes/fields_of_babylon/option_d.wav", "correct": true,
      "explain": "" }
  ],
  "camera_limits": { "target": [0, 0, 0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 14.0 },
  "success_text": "TWINS! 🎉 Rotate the map 45° and 0.16·x·y becomes Hannibal's 0.16(x² − y²) — the very same saddle. Your ear knew it: shape is real, north is just a choice. 🌾🐘"
}

data/scenes/fields_of_babylon/options.json

{
  "A": { "surface": "bowl",   "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/fields_of_babylon/option_a.wav" },
  "B": { "surface": "ridge",  "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/fields_of_babylon/option_b.wav" },
  "C": { "surface": "ramp",   "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/fields_of_babylon/option_c.wav" },
  "D": { "surface": "saddle", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/fields_of_babylon/option_d.wav" }
}

Equation LaTeX

z = 0.16\,x\,y

What each option sounds like

    A — "the pit," B — "the endless wall," C — "the mountainside": the three familiar non-saddles, one act older now. (Gross: low cluster / frozen top line / single lean.)
    D — CORRECT, "the pass itself": the axis-aligned saddle — the identical render as Scene 8's answer. The player stands on the rotated corner, hears its live diagonal straddle, and must recognize the same shape wearing different compass names. (Gross: straddle in symmetric pairs, A440 center.)

Design rationale (click to expand)

    The quiz IS the theorem. The live scene plays 0.16xy (high pairs NE/SW, low pairs NW/SE); the correct WAV plays 0.16(x2−y2) (high pairs E/W, low pairs N/S). Choosing D means the ear performed a rotation and reported "same shape" — which is exactly the invariance the scene exists to teach. Option D's file can literally be a copy of hannibal_saddle/option_c.wav — same recipe, and poetic that it is.
    The map is Scene 8's map, turned 45°: shorelines now run along the coordinate axes (since z=0 wherever x=0 or y=0), snow in the NE and SW corners (z=4.0), seas in the NW and SE. Players see the rotation before they hear it.
    Totem starts at the corner (0,0) — both hands feel level again (both partials zero), but walk the NE diagonal and both hands together climb; walk NW and both together sink. The two-hands mechanic discovers that the "special directions" don't have to be anyone's axis.
    History: Babylonian tablets computed field areas as length × width in the Old Babylonian period — xy really is humanity's first two-variable function, and it was drawn on clay before it was a saddle. 📜

🌊 SCENE 10 — ocean_swell (egg_carton — hearing the period)

Teaching goal: frequency by ear. Same wave height, different spacing — count the hills inside one circle.

    ⚙️ FLAG FOR DEEPSEEK — the two sanctioned new density surfaces (hand-off clause, Scene 10):

    def egg_carton_1x1(x, y):  return 1.6 * np.sin(0.75 * x) * np.sin(0.75 * y)   # half-wave ~4.2: one swell per circle
    def egg_carton_3x3(x, y):  return 1.6 * np.sin(2.25 * x) * np.sin(2.25 * y)   # half-wave ~1.4: three per crossing

    Add both to REGISTRY as "egg_carton_1x1" and "egg_carton_3x3". Same amplitude A=1.6 as the standard egg_carton (k=1.5) — only k changes, exactly per the spec.

data/scenes/ocean_swell/scene.json

{
  "scene_id": "ocean_swell",
  "title_lines": [
    "THE OPEN PACIFIC 🌊🛶 The wayfinder reads the swell with closed eyes —",
    "how many waves pass beneath the canoe tells her which sea she sails.",
    "Count the hills inside your circle. 🎧"
  ],
  "surface_name": "egg_carton",
  "equation_png": "data/scenes/ocean_swell/equation.png",
  "totem_start": [1.05, 1.05],
  "domain": [-5.0, 5.0, -5.0, 5.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Which groove is THIS sea — the swell under your totem right now? 🌊",
  "hint_lines": [
    "Stand on any hilltop and listen: how many hills and hollows fit inside",
    "your circle? One lonely swell… two… or three packed tight? 💡",
    "Same wave height everywhere — only the SPACING changes."
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/ocean_swell/option_a.wav", "correct": false,
      "explain": "One great lonely swell — a single hill filling the whole circle, hollows only at the rim. Wider waves than this sea. 🙂" },
    { "label": "B", "wav_path": "data/scenes/ocean_swell/option_b.wav", "correct": false,
      "explain": "That canoe sat DOWN in one wide hollow — everything rising around it. A wider sea than this one… and listen from a hilltop! 🙂" },
    { "label": "C", "wav_path": "data/scenes/ocean_swell/option_c.wav", "correct": true,
      "explain": "" },
    { "label": "D", "wav_path": "data/scenes/ocean_swell/option_d.wav", "correct": false,
      "explain": "Waves packed TIGHT — three crests per crossing, the music cycling fast. A choppier sea than the one beneath you. 🙂" }
  ],
  "camera_limits": { "target": [0, 0, 0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 14.0 },
  "success_text": "THE WAYFINDER NODS. 🌊🛶 Two swells per crossing — you heard the PERIOD of the sea. Same height, different spacing: your ear just measured a frequency. 🎉"
}

data/scenes/ocean_swell/options.json

{
  "A": { "surface": "egg_carton_1x1", "xy": [2.09, 2.09],  "radius": 2.5,
         "out": "data/scenes/ocean_swell/option_a.wav" },
  "B": { "surface": "egg_carton_1x1", "xy": [2.09, -2.09], "radius": 2.5,
         "out": "data/scenes/ocean_swell/option_b.wav" },
  "C": { "surface": "egg_carton",     "xy": [1.05, 1.05],  "radius": 2.5,
         "out": "data/scenes/ocean_swell/option_c.wav" },
  "D": { "surface": "egg_carton_3x3", "xy": [0.7, 0.7],    "radius": 2.5,
         "out": "data/scenes/ocean_swell/option_d.wav" }
}

Equation LaTeX

z = 1.6\,\sin(1.5\,x)\,\sin(1.5\,y)

What each option sounds like

    A — "the lonely swell" (1×1, on the crest): F♯5 at center, everything falling away, first hollows just brushing the rim. Sounds like a soft summit. (Gross: high cluster only.)
    B — "the wide hollow" (1×1, in the trough): B3 at center, everything rising. Sounds like a gentle pit. (Gross: low cluster only.)
    C — CORRECT, "this sea" (2×2): rendered at the scene's own starting hilltop (1.05,1.05) — F♯5 crest under the totem and B3 troughs inside the circle: the chord alternates high–low–high across the rings, two swells per crossing. (Gross: full straddle, alternating once.)
    D — "the chop" (3×3): same B3–F♯5 span, but the alternation happens every ring — a tight, jangly, fast-cycling groove. (Gross: full straddle, alternating tightly.)

Design rationale (click to expand)

    Density is position-proof: the sea is periodic, so wherever the players drift, the spacing signature stays the same — the quiz can't be broken by wandering. The hint still says "listen from a hilltop" so the comparison with C (rendered on a crest) is apples-to-apples; B's explain repeats that tip as a gift.
    A/B vs C/D is the deep contrast: in the sparse sea, one circle sees only half a period — and a half-period of a wave is indistinguishable from a summit or a pit! That's a quietly profound lesson (local views of periodic worlds), and it's why A and B are rendered from the same surface at crest and trough.
    k values: 0.75/1.5/2.25 — half-wavelengths ≈4.19/2.09/1.40, i.e. ~1, ~2, ~3 swells across the 5-unit hearing diameter. Factor-of-safety spacing between options: each step is a ×1.5 density jump, grossly countable.
    Totem start (1.05,1.05)=(π/3,π/3), exactly on a crest, matching option C's render point.
    The visual: a checkerboard of green islands and blue lakes — shorelines form a perfect grid (the z=0 lines at multiples of π/1.5≈2.09), with tiny deep-blue eyes at trough centers (−1.6 just crosses the −1.5 band). No snow — peaks at 1.6 stay below 2.2. An ocean, painted by the fixed bands.
    Rhythm carries the lesson too: outer rings strike more per measure, so in D the pitch alternation rides on the fast outer rhythms — "tighter, faster-cycling music," exactly as the spec asks the players to hear.

Say "continue" for Part 7 — Scene 11 three_chairs (bowl vs saddle vs monkey saddle: where the second-derivative test falls silent, but the ear does not). 🐒🪑