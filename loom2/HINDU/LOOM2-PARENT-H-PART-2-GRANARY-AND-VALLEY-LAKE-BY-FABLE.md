Wonderful! 😊 Here is Part 2 of 8 — the maximum and the minimum, Act I's twin hearts.
🌾 SCENE 2 — granary_of_egypt (hill)

Teaching goal: a unique global maximum. At the summit, nobody sings above you — the chord hangs entirely below.
data/scenes/granary_of_egypt/scene.json

{
  "scene_id": "granary_of_egypt",
  "title_lines": [
    "EGYPT, 1870 BC 🌾 Seven years of plenty fill the granary —",
    "the overseer must stand on the very top of the golden heap",
    "to count the harvest. Climb to the summit by ear. 🎧"
  ],
  "surface_name": "hill",
  "equation_png": "data/scenes/granary_of_egypt/equation.png",
  "totem_start": [2.0, -2.0],
  "domain": [-5.0, 5.0, -5.0, 5.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Which sound is the very top of the grain heap? 🌾",
  "hint_lines": [
    "On the summit, every musician around you sings BELOW the middle —",
    "the whole chord hangs high and falls away outward. 💡",
    "On the side of the heap, some still sing above you. Keep climbing!"
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/granary_of_egypt/option_a.wav", "correct": false,
      "explain": "That was the bottom of a PIT — every voice rose around you. The top of the heap is the exact opposite. 🙂" },
    { "label": "B", "wav_path": "data/scenes/granary_of_egypt/option_b.wav", "correct": false,
      "explain": "That was the SIDE of the heap — voices above you uphill, voices below you downhill. Climb until nobody sings above you! 🙂" },
    { "label": "C", "wav_path": "data/scenes/granary_of_egypt/option_c.wav", "correct": false,
      "explain": "That was the flat ground far from the heap — one low note, nearly unison. The grain is elsewhere. 🙂" },
    { "label": "D", "wav_path": "data/scenes/granary_of_egypt/option_d.wav", "correct": true,
      "explain": "" }
  ],
  "camera_limits": { "target": [0, 0, 0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 14.0 },
  "success_text": "THE TOP! 🌾 Nobody sings above you — the chord hangs entirely below and falls away in every direction. That is a MAXIMUM. 🎉"
}

data/scenes/granary_of_egypt/options.json

{
  "A": { "surface": "bowl", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/granary_of_egypt/option_a.wav" },
  "B": { "surface": "hill", "xy": [2.0, 0.0], "radius": 2.5,
         "out": "data/scenes/granary_of_egypt/option_b.wav" },
  "C": { "surface": "hill", "xy": [4.5, 4.5], "radius": 2.5, "domain": [1.5, 7.5, 1.5, 7.5],
         "out": "data/scenes/granary_of_egypt/option_c.wav" },
  "D": { "surface": "hill", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/granary_of_egypt/option_d.wav" }
}

Equation LaTeX

z = 3.4\,e^{-(x^{2}+y^{2})/7} - 0.6

What each option sounds like

    A — "the pit": bowl-bottom. Low cluster around E4, rings in unison, rising outward. (Gross: low, rising around you.)
    B — "the flank": hill at (2,0) — heights from 2.68 down to −0.41 across the circle: a huge lean, C♯6 on the uphill side to F♯4 on the downhill side, straddling the local pitch. (Gross: tilted spread, above AND below.)
    C — "the far skirt": hill at (4.5,4.5), r≈6.4 from the peak — the land flattens toward −0.6: nearly unison F♯4, a quiet low drone. (Gross: near-unison, low.)
    D — CORRECT, "the summit": center C♯6 (from z=2.8), descending outward to C♯5 at the rim — a bright, high cluster with the top note dead center, everything falling away. (Gross: high cluster, peak in the middle.)

Design rationale (click to expand)

    The hill is an island 🏝️: with band edges fixed at −1.5,−0.6,0,1.1,2.2, the shoreline sits at r≈3.48, upland begins at r≈1.9, and a snowcap crowns r<1.17 (z>2.2). Grain heap in the story, snow-capped island on screen — the palette shows the concentric level curves before Scene 5 makes them the lesson.
    Totem start (2,−2) on the flank: the opening groove already leans, inviting the climb. Players ride the pitch up to the top — discovery before the quiz.
    Option C uses the domain override (Amendment G2.5-A habit): its hearing circle at (4.5,4.5) pokes past the scene's map edge, so the seating window [1.5,7.5]2 is stated explicitly — the surface formula is pure math and extends gracefully.
    B's explain is a compass: "climb until nobody sings above you" is literally the algorithm for finding a maximum by ear — the wrong answer teaches the search procedure.
    Summit chord (zmax​=2.8→16.8 st → C♯6) stays comfortably inside the orchestra's range — flutes and violins own it.

🛶 SCENE 3 — valley_lake (bowl)

Teaching goal: a unique global minimum — and the lake below A440: negative numbers made audible.
data/scenes/valley_lake/scene.json

{
  "scene_id": "valley_lake",
  "title_lines": [
    "A MOUNTAIN LAKE 🏔️💧 The fishermen say the deepest water",
    "sings the lowest song — notes below A440, under the waterline.",
    "Row out and find the very bottom of the valley. 🛶🎧"
  ],
  "surface_name": "bowl",
  "equation_png": "data/scenes/valley_lake/equation.png",
  "totem_start": [3.0, 0.0],
  "domain": [-5.0, 5.0, -5.0, 5.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Which sound is the deepest point of the lake? 🛶",
  "hint_lines": [
    "At the very bottom, each ring of musicians sings ONE note in unison —",
    "and every ring outward is higher. Nobody sings below the middle. 💡",
    "Deep water sits BELOW A440 — listen for the whole chord hanging low."
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/valley_lake/option_a.wav", "correct": true,
      "explain": "" },
    { "label": "B", "wav_path": "data/scenes/valley_lake/option_b.wav", "correct": false,
      "explain": "That was a SUMMIT — every voice fell away below you. We want the mirror image: the place where every voice rises above. 🙂" },
    { "label": "C", "wav_path": "data/scenes/valley_lake/option_c.wav", "correct": false,
      "explain": "That was the SHORELINE — low voices over the water, high voices toward the land. Keep rowing toward the low side! 🙂" },
    { "label": "D", "wav_path": "data/scenes/valley_lake/option_d.wav", "correct": false,
      "explain": "Every musician sang one middle note — flat ground at A440, no valley anywhere. 🙂" }
  ],
  "camera_limits": { "target": [0, 0, 0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 14.0 },
  "success_text": "THE DEEPEST POINT! 💙 Every ring in unison, everything rising around you, the whole chord below A440 — a MINIMUM. You just heard negative numbers. 🎉🛶"
}

data/scenes/valley_lake/options.json

{
  "A": { "surface": "bowl", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/valley_lake/option_a.wav" },
  "B": { "surface": "hill", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/valley_lake/option_b.wav" },
  "C": { "surface": "bowl", "xy": [2.5, 0.0], "radius": 2.5,
         "out": "data/scenes/valley_lake/option_c.wav" },
  "D": { "surface": "ramp", "xy": [0.0, 0.0], "radius": 2.5, "z_per_octave": 200.0,
         "out": "data/scenes/valley_lake/option_d.wav" }
  }

Equation LaTeX

z = 0.16\,(x^{2}+y^{2}) - 1

What each option sounds like

    A — CORRECT, "the deep": bowl-bottom. Center z=−1→ E4 (below A440!), rings in unison — E4, F♯4, A4 at the rim. A compact low chord with nothing beneath its center, rising outward in perfect rings. (Gross: low unison rings, rising around you.)
    B — "the summit": the granary sound from Scene 2 — high cluster, C♯6 falling away. (Gross: high cluster — instantly recognizable from the scene they just beat, a kind echo.)
    C — "the shoreline": bowl at (2.5,0), right on the waterline — cellos over the deep side, violins toward the high shore, a strong lean through A440. (Gross: tilted spread.)
    D — "the flat plaza": the Scene 1 flat trick — total unison on A4. (Gross: one single note.)

Design rationale (click to expand)

    The visual is a perfect target 🎯: concentric circular bands — deep blue disk (r<1.58... deepest band), shallow blue to the shoreline at r=2.5, green, upland, and a snow rim in the corners (r>4.47, z>2.2). Circular level curves painted, again a scene ahead of the lesson.
    Totem start (3,0) on dry land near the shore: as they row inward, the whole groove slides down through A440 into the blue — the waterline crossing is audible (the pitch center passes A) and visible at once. Negative numbers stop being scary.
    Scenes 2 and 3 are deliberate mirrors: max = "nobody above you," min = "nobody below you," and each quiz plants the other's correct sound as a wrong option. The pair trains the ear's most fundamental classification, and option B rewards Scene 2's graduates.
    Corner heights reach z=7.0→+42 st, past the violin's A7 — the family soft-clamp rule (SUTRAS 1.3) handles the extreme corners gracefully; the quiz never goes there.
    All four option positions sit safely inside default seating windows — no domain override needed (C's circle at (2.5,0) spans exactly x∈[0,5] ✓).

Say "continue" for Part 3 — Scene 4 rain_gutter (ridge: one player changes nothing) and Scene 5 terraces_of_banaue (hill: the level walk, unison as a path). 🌧️🌾