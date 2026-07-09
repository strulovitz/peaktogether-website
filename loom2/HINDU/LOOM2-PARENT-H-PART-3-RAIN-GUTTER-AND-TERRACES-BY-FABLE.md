With joy! 😊 Here is Part 3 of 8 — Act I closes with the dead direction, and Act II opens the level curves.
🌧️ SCENE 4 — rain_gutter (ridge)

Teaching goal: y is absent from the formula. One whole direction changes nothing — the first taste of a frozen variable.
data/scenes/rain_gutter/scene.json

{
  "scene_id": "rain_gutter",
  "title_lines": [
    "HOLLAND, 1421 🌷🌧️ The storm rises and two waters press the dyke.",
    "The keeper must walk the crest — the one line that stays high",
    "while the land falls away east and west. Find it by ear. 🎧"
  ],
  "surface_name": "ridge",
  "equation_png": "data/scenes/rain_gutter/equation.png",
  "totem_start": [1.5, -2.5],
  "domain": [-5.0, 5.0, -5.0, 5.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Which sound is the crest — where a whole LINE of musicians shares the top note? 🌧️",
  "hint_lines": [
    "On the crest, walking north–south changes NOTHING —",
    "friends ahead of you and behind you sing your exact note. 💡",
    "Does the highest note live at one point… or along a whole row?"
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/rain_gutter/option_a.wav", "correct": false,
      "explain": "EVERY direction was dead there — one note everywhere, a flat floor. On the dyke, one direction holds still but the other falls to the water. 🙂" },
    { "label": "B", "wav_path": "data/scenes/rain_gutter/option_b.wav", "correct": false,
      "explain": "So close! That peak falls away in EVERY direction — its top note lives at a single point. The crest's top note stretches along a whole line. 🙂" },
    { "label": "C", "wav_path": "data/scenes/rain_gutter/option_c.wav", "correct": true,
      "explain": "" },
    { "label": "D", "wav_path": "data/scenes/rain_gutter/option_d.wav", "correct": false,
      "explain": "That was the dyke's SLOPE — the music leaned down toward the water. Climb until the highest voices sing right beside you, ahead and behind. 🙂" }
  ],
  "camera_limits": { "target": [0, 0, 0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 14.0 },
  "success_text": "THE CREST! 🌧️ North–south the music froze — that whole line sings one note, and only east–west falls away. You just heard a direction where nothing changes. Remember it. 🎉"
}

data/scenes/rain_gutter/options.json

{
  "A": { "surface": "ramp",  "xy": [0.0, 0.0], "radius": 2.5, "z_per_octave": 200.0,
         "out": "data/scenes/rain_gutter/option_a.wav" },
  "B": { "surface": "hill",  "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/rain_gutter/option_b.wav" },
  "C": { "surface": "ridge", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/rain_gutter/option_c.wav" },
  "D": { "surface": "ridge", "xy": [2.0, 0.0], "radius": 2.5,
         "out": "data/scenes/rain_gutter/option_d.wav" }
}

Equation LaTeX

z = 1.8 - 0.22\,x^{2}

(The missing y IS the lesson — players will stare at it after they hear it.)
What each option sounds like

    A — "the flat floor": total unison A4 — dead in both directions. (Gross: one single note.)
    B — "the lonely peak": hill summit — C♯6 at the center only, everything falling away all around. (Gross: high cluster, top note at one point.)
    C — CORRECT, "the crest line": ridge at (0,0) — five musicians in a north–south line all singing A5 (the entire x=0 column inside the circle), F♯5 columns beside them, C♯5/E5 at the east–west rim. The top note is a row of friends. (Gross: top note stretched along a line, falling east–west only.)
    D — "the slope": ridge at (2,0) — a hard lean toward the water, dead north–south but tilted, top notes off to one side. (Gross: tilted spread.)

Design rationale (click to expand)

    B vs C is deliberately the subtle pair — that is this scene's teaching goal, so per the Confusability Rule the question text itself names the exact feature to listen for ("a whole LINE shares the top note"), and the hints repeat it. A and D stay grossly distinct as safe landmarks.
    The visual sells the story: z=0 at x=±2.86, z=−3.7 at the map's east/west edges — a straight green-and-brown causeway between two deep blue seas, color bands in perfect north–south stripes. The St. Elizabeth's flood of 1421 really did break the Dutch dykes; our keeper walks a luckier timeline. 🌷
    scene_id stays rain_gutter (matching the campaign map and the UPANISHADS seed); the title got the storm that the shape deserved.
    Totem start (1.5,−2.5) on the eastern slope: the opening groove leans, and the players' first playful discovery is that W/S (the y player!) does nothing to the pitch — the boyfriend/girlfriend asymmetry becomes a giggle before it becomes a lesson (Scene 6 will name it).
    Success text plants Scene 6: "Remember it." The frozen direction returns with its true name, ∂f/∂y=0.

🌾 SCENE 5 — terraces_of_banaue (hill, the level walk)

Teaching goal: level curves. A path of constant height = a note carried sideways — the contour through your point.
data/scenes/terraces_of_banaue/scene.json

{
  "scene_id": "terraces_of_banaue",
  "title_lines": [
    "BANAUE, PHILIPPINES 🌾⛰️ For two thousand years the terraces",
    "have climbed this mountain — every stone wall traces one height.",
    "Find where the village walks without climbing. 🎧"
  ],
  "surface_name": "hill",
  "equation_png": "data/scenes/terraces_of_banaue/equation.png",
  "totem_start": [-2.0, 1.0],
  "domain": [-5.0, 5.0, -5.0, 5.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Where can the farmers walk a level path THROUGH the village — the center's note carried out to both sides? 🌾",
  "hint_lines": [
    "A level path sings ONE note — listen for the middle note",
    "stretched sideways by an arc of friends, uphill voices above it,",
    "downhill voices below it. 💡"
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/terraces_of_banaue/option_a.wav", "correct": false,
      "explain": "That was the SUMMIT — its height belongs to one single point, so there is no room to walk level there. The paths live on the slopes. 🙂" },
    { "label": "B", "wav_path": "data/scenes/terraces_of_banaue/option_b.wav", "correct": true,
      "explain": "" },
    { "label": "C", "wav_path": "data/scenes/terraces_of_banaue/option_c.wav", "correct": false,
      "explain": "The whole land was ONE height — a floor, not a mountainside. Terraces are carved where the land slopes. 🙂" },
    { "label": "D", "wav_path": "data/scenes/terraces_of_banaue/option_d.wav", "correct": false,
      "explain": "That was the bottom of a PIT — lovely level rings around you, but the lowest note itself belongs to a single point, just like a summit. 🙂" }
  ],
  "camera_limits": { "target": [0, 0, 0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 14.0 },
  "success_text": "A LEVEL PATH! 🌾 The middle note stretched along a curve — walk it and the music never changes. That curve is a CONTOUR, and the terraces you see are contours made of stone. 🎉"
}

data/scenes/terraces_of_banaue/options.json

{
  "A": { "surface": "hill", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/terraces_of_banaue/option_a.wav" },
  "B": { "surface": "hill", "xy": [2.0, 0.0], "radius": 2.5,
         "out": "data/scenes/terraces_of_banaue/option_b.wav" },
  "C": { "surface": "ramp", "xy": [0.0, 0.0], "radius": 2.5, "z_per_octave": 200.0,
         "out": "data/scenes/terraces_of_banaue/option_c.wav" },
  "D": { "surface": "bowl", "xy": [0.0, 0.0], "radius": 2.5,
         "out": "data/scenes/terraces_of_banaue/option_d.wav" }
}

Equation LaTeX

z = 3.4\,e^{-(x^{2}+y^{2})/7} - 0.6

What each option sounds like

    A — "the summit": the Scene 2 winner — C♯6 center, all falling away. Its top note has no companions. (Gross: high cluster, lonely top.)
    B — CORRECT, "the terrace path": hill at (2,0) — the center's E5 carried by an arc of three musicians running across the middle (the contour through the totem), A5/B5 voices uphill, B4/A4 voices downhill. A lean with a level seam through it. (Gross: tilted spread with the middle note shared sideways.)
    C — "the floor": total unison A4. Everything level, nothing to terrace. (Gross: one note.)
    D — "the pit": bowl-bottom — level rings, yes, but the center's own note is companionless at the bottom. (Gross: low unison rings.)

Design rationale (click to expand)

    The core insight made audible: through every point on a slope runs exactly one contour — an arc of same-pitch neighbors. At a summit or pit, the "contour" through the center degenerates to a point — which is precisely why A and D are wrong, and their explanations say so in walking language. This quietly pre-teaches critical points: extrema are where the level curve collapses.
    Scene 2 echo, new ears: option B is literally the same spot that was a wrong answer ("the side of the heap") in Scene 2. What was a distractor becomes the treasure once the question changes — the same land holds many lessons, which is the whole philosophy of reusing surfaces across acts.
    D's explain does double duty: it praises what the player correctly heard (level rings!) while pinpointing the miss (the path must pass through the village at the village's height). Kindness Rule: the wrong answer confirms their ear worked.
    The visual is the lesson: the hill's fixed color bands are concentric terrace rings — from this scene on, players know the painted band edges are exactly the places where the orchestra holds one note.
    Same surface as Scene 2 by design (UPANISHADS); new totem start on the west flank (−2,1) so the land feels revisited, not repeated.

Say "continue" for Part 4 — Scene 6 ridge_two_hands (his hand is ∂f/∂x, hers is ∂f/∂y) and Scene 7 water_finds_the_way (the gradient, steepest climb). 🤝💧