Understood, Nir — the goal was always the hand-off, and I lost sight of it. No more of that. Here is Part 1 of 8: the campaign map, then Scene 1 complete. Say "continue" after each part.
🗺️ THE CAMPAIGN MAP (Parts 1–8)
#	scene_id	Surface	Correct	Delivered in
1	roman_road	ramp	B	Part 1 (now)
2	granary_of_egypt	hill	D	Part 2
3	valley_lake	bowl	A	Part 2
4	rain_gutter	ridge	C	Part 3
5	terraces_of_banaue	hill	B	Part 3
6	ridge_two_hands	ridge	D	Part 4
7	water_finds_the_way	hill	A	Part 4
8	hannibal_saddle 🏔️	saddle	C	Part 5 (flagship, alone)
9	fields_of_babylon	field	D	Part 6
10	ocean_swell	egg_carton	C (per spec)	Part 6 (+ new surface specs)
11	three_chairs	monkey_saddle	B	Part 7
12	tartaglia_cannon	cannon_range	A	Part 8 (+ Fog Summit design + campaign.json + final checklist)

Correct answers spread evenly (3×A, 3×B, 3×C, 3×D) — no letter pattern to game. The Fog Summit design comes in Part 8; if it needs a tiny code hook, I'll present it there as a clean yes/no decision for you and DeepSeek — nothing before that is blocked by it.
🏛️ SCENE 1 — roman_road (ramp)

Teaching goal: constant slope. A plane's gradient is the same everywhere — the orchestra leans evenly and never changes shape.
data/scenes/roman_road/scene.json

{
  "scene_id": "roman_road",
  "title_lines": [
    "ROME, 19 BC 🏛️💧 The new aqueduct must fall steadily —",
    "one perfect, unchanging slope for fifty miles,",
    "or the water stops. Find that slope by ear. 🎧"
  ],
  "surface_name": "ramp",
  "equation_png": "data/scenes/roman_road/equation.png",
  "totem_start": [0.0, 0.0],
  "domain": [-5.0, 5.0, -5.0, 5.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Which sound is a steady, unchanging slope? 🏛️",
  "hint_lines": [
    "A steady slope LEANS the whole orchestra evenly —",
    "low voices on one side, high on the other, A440 in the middle. 💡",
    "A pit or a peak curves. A road just leans."
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/roman_road/option_a.wav", "correct": false,
      "explain": "That land was perfectly FLAT — every musician sang the very same note. A flat channel carries no water. 🙂" },
    { "label": "B", "wav_path": "data/scenes/roman_road/option_b.wav", "correct": true,
      "explain": "" },
    { "label": "C", "wav_path": "data/scenes/roman_road/option_c.wav", "correct": false,
      "explain": "That was a PIT — the whole chord sat low and rose all around you. Water would pool there, never flow. 🙂" },
    { "label": "D", "wav_path": "data/scenes/roman_road/option_d.wav", "correct": false,
      "explain": "That was a HILLTOP — every note hung high, falling away on all sides. Water would scatter, not follow. 🙂" }
  ],
  "camera_limits": { "target": [0, 0, 0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 14.0 },
  "success_text": "AQUA FLUIT! 💧 A slope that never changes — the orchestra leans evenly and keeps its shape wherever you walk. That is a plane: the gradient is the same everywhere. 🎉"
}

data/scenes/roman_road/options.json

{
  "A": { "surface": "ramp", "xy": [0.0, 0.0], "radius": 2.5, "z_per_octave": 200.0,
         "out": "data/scenes/roman_road/option_a.wav" },
  "B": { "surface": "ramp", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/roman_road/option_b.wav" },
  "C": { "surface": "bowl", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/roman_road/option_c.wav" },
  "D": { "surface": "hill", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/roman_road/option_d.wav" }
}

Equation LaTeX (for DeepSeek)

z = 0.55\,x + 0.30\,y

What each option sounds like (for your ears when you test)

    A — "the flat plaza": ramp with z_per_octave: 200 — every height collapses to under a tenth of a semitone, so all ~21 musicians snap to A4 unison. Full rhythm groove, one single pitch. (Gross feature: total unison.)
    B — CORRECT, "the steady lean": double bass & tuba on the downhill (SW) side, violins & flutes on the uphill (NE) side, an even pentatonic staircase through A440 at the totem — roughly ±9 semitones across the circle. (Gross feature: even spread, low side / high side.)
    C — "the pit": bowl-bottom. Whole chord sits below A440 (center z=−1), each ring in unison, rising outward. (Gross feature: low cluster, all around you.)
    D — "the mound": hill-summit. Whole chord hangs above and below itself downward — center z=2.8, everything descending outward, all notes high. (Gross feature: high cluster.)

Four options, four unmistakably different worlds — Confusability Rule satisfied for first-time ears.

Design rationale (click to expand)

    Domain [−5,5]2: corners reach z=±4.25 — the SW corner is deep abyss, the NE corner crosses the snow line (z>2.2), so the full hypsometric palette appears on the very first scene, and the color bands are parallel straight stripes — the level curves of a plane, painted before the players ever hear the word "contour." The shoreline (z=0) runs straight through the origin.
    Totem start [0,0]: planted exactly on the shoreline — half the hearing circle in blue, half on land; the opening groove is centered on A440 with the lean immediately audible, and panning puts the low instruments on one side of the stereo field.
    Flat option via z_per_octave override (Amendment G2.5-A): the registry has no flat surface, and the sanctioned per-option override gives us one with zero new code. "Zero slope" is the single most valuable wrong answer for a scene about slope.
    All options at [0,0], radius 2.5, far from any edge → default seating lattice is safe, no domain override needed (G2.5-A habit checked).
    Story: real Roman aqueducts held gradients near 1 : 4800 for tens of miles — the Pont du Gard's engineers really did live or die by "one perfect, unchanging slope." 2–3 lines, mood only, music is the star.
    Kindness: every wrong answer teaches what it was (flat / pit / hilltop) in water-flow language the scenario already set up. Pink text, retry forever.

Say "continue" for Part 2 — Scene 2 granary_of_egypt (hill, the maximum) and Scene 3 valley_lake (bowl, the minimum, the lake below A440). 🌾🏞️