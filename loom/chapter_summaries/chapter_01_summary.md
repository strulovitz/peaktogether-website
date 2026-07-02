# Chapter 1 — Introduction and Motivation

## Summary (project-oriented)

This chapter is the "why" of HSS, in two parts (a concise Part A + expanded Part B). The core argument: sonification has a long history (Mersenne/Newton's speculations → Xenakis/Hiller's stochastic compositions → NASA's data sonifications since the 1980s), but most attempts fail because they lack musical scaffolding. Three named failure modes:

1. Raw function playback (e.g., Mathematica's Play[]) → continuous glissandi, "vacuum cleaner" drones
2. Overloaded timbre — encoding too many parameters at once overwhelms the ear; keep to 1–2 timbre parameters max
3. No clear mapping logic — if data→sound correlations aren't perceptually stable, listeners can't build mental models

The fix is a coordinate-based approach — the auditory analogue of Cartesian coordinates:

- Pitch helix: one full turn = one octave (cyclic chroma), vertical rise = continuous frequency
- Timbre axis: one parameter (brightness / filter cutoff / spectral centroid), deliberately minimal
- Discrete time grid: data events sliced into beats/measures, not raw time increments — the ear needs pulse to parse patterns

Target audiences named: scientists, educators (explicitly: teaching functions and derivatives through auditory analogies for students who struggle with visual/symbolic approaches — literally your game's mission 🎯), and musicians.

## Key mappings/parameters to preserve

- Design commandments distilled from pitfalls:
  - ✅ Quantize pitch to scales (never continuous sweeps)
  - ✅ Max 1–2 timbre parameters
  - ✅ Rhythmic grid mandatory — discrete beats, not arbitrary timing
  - ✅ Stable, explicit mapping logic — each data dimension → exactly one audible parameter
- Toolchain assumed: Python + numpy, matplotlib, sounddevice, optionally ipywidgets

## Ideas relevant to the LOOM game 🎮

- The three pitfalls are our spell-design QA checklist: every spell must be quantized, rhythmically gridded, and timbre-simple — otherwise players can't memorize/distinguish them (exactly the "stable mental representation" problem)
- The educator use-case validates the game concept directly: HSS was designed for teaching functions by ear
- The discrete time grid maps beautifully onto LOOM's mechanic: LOOM drafts were discrete note sequences — HSS's beat-sliced approach naturally produces LOOM-compatible motifs

## Notes/questions

- Scholarly anchors worth keeping for the website's "learn more" pages: Shepard (1964) — origin of the pitch helix; Elaine Chew (2014) — spiral array model (3D pitch/chord/key spaces — could inspire in-game visuals of the helix!); Diana Deutsch; Carla Scaletti (Kyma); Xenakis
- Still conceptual — the math starts next chapter.
