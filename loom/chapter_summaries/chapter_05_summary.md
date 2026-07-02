# Chapter 5 — Practical Sonification of Mathematical Functions

## Summary (project-oriented)

The core application chapter: how to turn actual math functions into music using the Ch.3–4 machinery. Candidate functions named: polynomials (x², x³−x), exponentials, damped sine y = e^(−x)·sin(10x), and parametric curves (Lissajous, cycloids, brachistochrone).

The worked example — damped sine:

- Domain: x ∈ [0, 3π] (gives 10–30 oscillations depending on step size)
- Output y ∈ [−1, 1] → scale with θ = 15·y (i.e., a = 15, spanning roughly ±15 semitones ≈ 2.5 octaves total)
- Snap to scale as usual

Data conditioning rules:

- Blow-ups: bound or transform with log(1 + |y|)
- Negative values: shift up into valid pitch range, or clamp
- Wiggly functions: sample fewer points / smooth to avoid "spastic" music

Parametric curves get a lovely two-axis treatment: for a cycloid x(t) = R(t − sin t), y(t) = R(1 − cos t) — feed y(t) → pitch and x(t) → timbre. Both dimensions of the shape become audible.

Demonstration architecture (important!):

1. Choose function → 2. step x discretely (e.g., Δx = 0.2) → 3. scale & snap for pitch → 4. optionally map second stream to timbre → 5. write notes to CSV ("Program A"), then read & play ("Program B") — or all-in-one
2. Interactive sliders for: a (pitch scale), x_max (domain), tempo

## Key mappings/parameters to preserve

- ✅ Question settled: mapping is ABSOLUTE — θ = a·f(x) throughout (the relative Δθ idea from Ch.2 doesn't reappear)
- Damped sine reference parameters: domain [0, 3π], step 0.2, a = 15
- Safe-range transform: log(1 + |y|); shift-or-clamp for negatives
- The Program A / Program B split (generate note data → play it)

## Ideas relevant to the LOOM game 🎮

- The Program A/B architecture is exactly our game architecture! 🎯
  - Program A = offline "spell compiler": function → note list → save as JSON/CSV in the repo
  - Program B = the game: loads precompiled spells, plays Philharmonia samples
  - Benefits: spells are deterministic, hand-tunable (we can audition and tweak each one), and the game itself needs zero math at runtime — just sample playback. Simple, fast, kid-proof.
- First spellbook candidates from this chapter (each with a distinct contour):

| Spell | Function | What the ear learns |
|-------|----------|---------------------|
| 📏 Line | y = x | steady staircase |
| 🎢 Parabola | y = x² | accelerating rise |
| 🌊 Wave | sin(x) | even arcs |
| 🍂 Fading Wave | e^(−x)·sin(10x) | quickening arcs that fade & settle |
| 🚀 Growth | e^x | runaway leaps |
| 🛞 Wheel | cycloid | repeating melodic humps + timbre sweep |

- The cycloid's pitch+timbre pairing could be an "advanced spell" tier — two-channel spells for later levels.
- Sliders (a, x_max, tempo) → natural "spell laboratory" mode where players experiment freely. 🧪

## Notes/questions

- a = 15 with y ∈ [−1, 1] slightly exceeds the Ch.3 "2 octave" guidance (30-semitone span) — in practice we'll tune a per spell by ear.
- For 4–8-note LOOM drafts, we'll choose Δx so each function's most characteristic stretch is captured — e.g., the damped sine needs enough notes to show both oscillation and decay.
