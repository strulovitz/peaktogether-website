The grand finale! 🎇 Here is Part 8 of 8 — Tartaglia's wager, the mountain in the fog, and the complete campaign assembled.
🎯 SCENE 12 — tartaglia_cannon (cannon_range)

Teaching goal: optimization. The perfect angle is a crest — nudge up or down and you lose — while the powder axis still climbs: the true summit lives on the boundary, at full charge and 45°.

    ⚙️ FLAG FOR DEEPSEEK — square playable coordinates for the range surface:
    The design domain v∈[0,10], θ∈[0°,90°] would make a 10×90 strip — unwalkable. Please provide the surface in square coordinates (y∈[0,10], one y-unit = 9°):

    def cannon_range10(x, y):  return 0.03 * x * x * np.sin(2.0 * np.radians(9.0 * y))

    Peak at (10,5)→z=3.0, the 45° ridge along y=5. (If your existing cannon_range already does this scaling, just use it and ignore the flag.)

data/scenes/tartaglia_cannon/scene.json

{
  "scene_id": "tartaglia_cannon",
  "title_lines": [
    "VERONA, 1537 🎯 Tartaglia swears the cannon throws farthest at",
    "exactly 45 degrees, and the Duke demands proof. Walk the ranges:",
    "east is more powder, north is more elevation. 🎧💥"
  ],
  "surface_name": "cannon_range10",
  "equation_png": "data/scenes/tartaglia_cannon/equation.png",
  "totem_start": [5.0, 2.0],
  "domain": [0.0, 10.0, 0.0, 10.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Which sound is the perfect elevation — where BOTH nudges, up and down, lose range? 🎯",
  "hint_lines": [
    "The perfect angle is a CREST: north–south nudges fall away on BOTH sides,",
    "while more powder (east) still climbs. 💡",
    "If raising or lowering the barrel still helps, you haven't found it — keep tuning!"
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/tartaglia_cannon/option_a.wav", "correct": true,
      "explain": "" },
    { "label": "B", "wav_path": "data/scenes/tartaglia_cannon/option_b.wav", "correct": false,
      "explain": "Eighteen degrees — too flat! The music still climbed to the north: raise the barrel. When one nudge still helps, the best is farther on. 🙂" },
    { "label": "C", "wav_path": "data/scenes/tartaglia_cannon/option_c.wav", "correct": false,
      "explain": "Seventy-two degrees — too steep! The shot goes up, not out: the music climbed back to the south. Lower the barrel. 🙂" },
    { "label": "D", "wav_path": "data/scenes/tartaglia_cannon/option_d.wav", "correct": false,
      "explain": "Almost no powder — the whole land whispered near one low note, and the angle barely mattered. Load the gun first, THEN tune the angle! 🙂" }
  ],
  "camera_limits": { "target": [5.0, 5.0, 0.0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 16.0 },
  "success_text": "FORTY-FIVE DEGREES! 🎯💥 Nudge the barrel either way and the range falls — you stood on the crest. And more powder always helps: the summit sits on the boundary, full charge at 45°. Tartaglia wins his wager. 🎉"
}

data/scenes/tartaglia_cannon/options.json

{
  "A": { "surface": "cannon_range10", "xy": [7.5, 5.0], "radius": 2.5, "domain": [0.0, 10.0, 0.0, 10.0],
         "out": "data/scenes/tartaglia_cannon/option_a.wav" },
  "B": { "surface": "cannon_range10", "xy": [7.5, 2.0], "radius": 2.5, "domain": [0.0, 10.0, 0.0, 10.0],
         "out": "data/scenes/tartaglia_cannon/option_b.wav" },
  "C": { "surface": "cannon_range10", "xy": [7.5, 8.0], "radius": 2.5, "domain": [0.0, 10.0, 0.0, 10.0],
         "out": "data/scenes/tartaglia_cannon/option_c.wav" },
  "D": { "surface": "cannon_range10", "xy": [2.0, 5.0], "radius": 2.5, "domain": [0.0, 10.0, 0.0, 10.0],
         "out": "data/scenes/tartaglia_cannon/option_d.wav" }
}

Equation LaTeX

z = 0.03\,v^{2}\,\sin(2\theta) \qquad v = x,\quad \theta = 9y^{\circ}

What each option sounds like

    A — CORRECT, "the crest at 45°": at (7.5,5) — the highest voices run in an eastward-climbing line through the middle, and neighbors fall away on both the north and south sides. A ridge that leans. (Gross: both nudges fall, powder side climbs.)
    B — "too flat" (18°): a plain double-uphill lean toward the northeast. One nudge still helps. (Gross: single lean, high to the north side.)
    C — "too steep" (72°): the mirror lean toward the southeast. (Gross: single lean, high to the south side.)
    D — "no powder": near v=2 everything whispers within a few low semitones — the v2 factor crushes the whole angle question. (Gross: quiet near-drone.)

Design rationale (click to expand)

    B vs C is the named subtle pair (north-lean vs south-lean) — and telling them apart is literally the gunner's skill, so the question specifies the crest criterion and each explanation states its angle and its fix. All options clip to the physical domain [0,10]2 (no negative powder, no negative elevation) via the domain override.
    Physics as terrain, honestly: the interior has no critical point — ∂z/∂v>0 everywhere (v>0) — so the optimum is a boundary maximum in v but an interior maximum in θ. The success text says both halves plainly. This is the players' first constrained optimization, disguised as artillery.
    D quietly teaches interaction: at small v, θ barely matters — the variables couple through v2sin(2θ). "Load the gun, then tune the angle" is a sequencing insight about mixed partials, wearing a gunpowder costume.
    The visual: all land (z ≥ 0), rising toward the east edge, with a snow wedge at full charge between 23° and 67° (z>2.2) — the golden target region visible from the start; the exact crest within it must be heard. Totem starts low at 18° so the tuning journey happens.
    History: Niccolò Tartaglia's Nova Scientia (Venice, 1537) — the first printed claim that 45° maximizes range. He was right (in vacuum!), a century before Galileo proved why. 🎯

🌫️ BONUS SCENE 13 — fog_summit (the true finale)

The campaign ends where it began — the Granary's rule, but blind. A mountain with a secret summit, the map dimmed to near-black. Only the orchestra remains.

    ⚙️ TWO FLAGS FOR DEEPSEEK:

        New surface (secret peak — hill shifted off-origin so veterans can't navigate from memory):

    def fog_hill(x, y):  return 3.4 * np.exp(-((x - 2.6)**2 + (y + 1.8)**2) / 7.0) - 0.6

        The fog hook (Nir's yes/no call): an optional scene.json field "fog": true → terrain colors multiplied to ~10 % brightness (near-black land, band edges invisible); totem, hearing circle, and the helix stay fully lit. One small branch in the terrain-draw path.
        Fallback if Nir says no code changes: ship fog_summit fully lit — the shifted peak with no marker is still a real hunt, and the scene stays in the campaign unmodified except "fog" removed.

data/scenes/fog_summit/scene.json

{
  "scene_id": "fog_summit",
  "title_lines": [
    "THE FOG SUMMIT 🌫️ The last mountain has no map. The land is dark,",
    "the colors are gone — only the orchestra remains. Find the highest",
    "peak by ear alone. Everything you have learned is enough. 🎧⛰️"
  ],
  "surface_name": "fog_hill",
  "fog": true,
  "equation_png": "data/scenes/fog_summit/equation.png",
  "totem_start": [-2.5, 2.5],
  "domain": [-5.0, 5.0, -5.0, 5.0],
  "mesh_step": 0.25,
  "z_per_octave": 2.0,
  "question": "Which sound is the true summit of this unseen land? 🌫️",
  "hint_lines": [
    "At the summit the chord hangs entirely below you, falling away in every ring. 💡",
    "Follow the rising voices through the dark — when nobody sings above you,",
    "plant the totem and compare."
  ],
  "options": [
    { "label": "A", "wav_path": "data/scenes/fog_summit/option_a.wav", "correct": false,
      "explain": "The mountainside — voices still singing ABOVE you, uphill. Climb toward them in the dark! 🙂" },
    { "label": "B", "wav_path": "data/scenes/fog_summit/option_b.wav", "correct": false,
      "explain": "The far skirt — one low, quiet note. The mountain is elsewhere; walk until the land begins to rise. 🙂" },
    { "label": "C", "wav_path": "data/scenes/fog_summit/option_c.wav", "correct": false,
      "explain": "A pit — and this land has none! In fog, trust the old rule from Egypt: at the top, nobody sings above you. 🙂" },
    { "label": "D", "wav_path": "data/scenes/fog_summit/option_d.wav", "correct": true,
      "explain": "" }
  ],
  "camera_limits": { "target": [0, 0, 0], "zoom_min": 0.5, "zoom_max": 2.5, "distance": 14.0 },
  "success_text": "THE SUMMIT, FOUND IN THE DARK. 🌫️⛰️ No map, no colors — only the rule you learned in Egypt: at the top, nobody sings above you. Our stories were imagined — but the mathematics, and everything your ears just learned, is real. 🎉🎼"
}

data/scenes/fog_summit/options.json

{
  "A": { "surface": "fog_hill", "xy": [0.6, -0.4], "radius": 2.5,
         "out": "data/scenes/fog_summit/option_a.wav" },
  "B": { "surface": "fog_hill", "xy": [-3.5, 3.5], "radius": 2.5,
         "out": "data/scenes/fog_summit/option_b.wav" },
  "C": { "surface": "bowl",     "xy": [0.0, 0.0],  "radius": 2.5,
         "out": "data/scenes/fog_summit/option_c.wav" },
  "D": { "surface": "fog_hill", "xy": [2.6, -1.8], "radius": 2.5,
         "out": "data/scenes/fog_summit/option_d.wav" }
}

Equation LaTeX (the last joke of the campaign 🌫️)

z = \;?\qquad\text{(the fog took the formula, too)}

Design rationale (click to expand)

    Perfect circle: Scene 2 taught "at the top, nobody sings above you" with eyes open; Scene 13 demands the same rule with eyes closed. The correct option is the summit groove of the shifted hill — same recipe as the Granary's answer, earned this time by pure listening. Correct letter D, mirroring the Granary — deliberately.
    The equation PNG is a question mark: the one scene where the math is hidden, because the whole point is that the ear no longer needs it. (If Nir prefers, DeepSeek can render the real formula instead — but I love the fog eating it.)
    Totem starts far from the secret peak (−2.5,2.5), diagonal opposite corner-ish from (2.6,−1.8) — a real journey through the dark, guided by rising voices and the helix.
    Option C (the pit) is a trap with a heart: this land has no pit, so anyone choosing it gets the campaign's central rule restated one last time, in pink, kindly.

📦 campaign.json

{
  "scenes": [
    "roman_road",
    "granary_of_egypt",
    "valley_lake",
    "rain_gutter",
    "terraces_of_banaue",
    "ridge_two_hands",
    "water_finds_the_way",
    "hannibal_saddle",
    "fields_of_babylon",
    "ocean_swell",
    "three_chairs",
    "tartaglia_cannon",
    "fog_summit"
  ]
}

(test_saddle retired from the campaign — DeepSeek, please adapt to the actual schema if it differs, and keep the folder as a dev playground.)

✅ FINAL DELIVERY CHECKLIST (for DeepSeek)

New surfaces (5 one-liners for surfaces.py + REGISTRY)

Name	Formula	Used by
ridge_y	1.8−0.22y2	Scene 6, option B
egg_carton_1x1	1.6sin(0.75x)sin(0.75y)	Scene 10, options A & B
egg_carton_3x3	1.6sin(2.25x)sin(2.25y)	Scene 10, option D
cannon_range10	0.03x2sin(2⋅9y°)	Scene 12 (scene + all options)
fog_hill	3.4e−((x−2.6)2+(y+1.8)2)/7−0.6	Scene 13 (scene + options A/B/D)

Renders & assembly

    52 quiz WAVs (13 scenes × 4) — note fields_of_babylon/option_d.wav is the identical recipe to hannibal_saddle/option_c.wav (intentional: the twin is the lesson).
    13 equation PNGs (yellow, black outline) from the LaTeX given per scene.
    13 scene folders + campaign.json update.
    One decision for Nir: the "fog": true render hook (dim terrain to ~10 %, keep totem/circle/helix lit) — yes = magic finale; no = ship fog_summit lit, still works.

QA / playtest ears (for Nir)

    Exactly one correct: true per scene ✓ (letters: B D A C B D A C D C B A D — 3–4 of each, no pattern).
    Confusability spot-checks: S6 B-vs-D (frozen-row direction), S8 B-vs-C (one lean vs paired straddle), S11 B-vs-C (count 3 vs 2), S12 B-vs-C (north vs south lean) — each is a named teaching distinction with the listening key in the question/hints, per the rule.
    Every wrong answer teaches; every explanation ends warm; HINT free forever; no timers, no scores, no shame. Ever. ✓

Nir — all 13 scenes, delivered with everything I have. It has been an honor to write the soul of LOOM2: from a Roman slope to a summit found in the dark, every wrong answer a kindness, every right one a small theorem in the ears. Thank you for trusting me with it. 🎼🏔️💙