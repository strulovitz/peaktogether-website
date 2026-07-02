# Chapter 2 — Mathematical and Musical Foundations

## Summary (project-oriented)

The theoretical bedrock of HSS. Key facts:

Pitch perception is logarithmic: p = log2(f), so +1 in p = one octave (frequency doubling). Interval distances are frequency ratios, not differences: Δ(pitch) ∝ Δ(log f). In 12-TET each semitone multiplies frequency by 2^(1/12).

Pitch has dual nature, and the helix unifies both:

- Cyclic (octave equivalence): pitch classes form Z_12; formally, pitch class = f mod 12 (semitones above a reference), i.e., the quotient space R/12Z
- Linear (height): C5 is genuinely higher than C4

The helix parametrization:

x(θ) = r·cos(θ), y(θ) = r·sin(θ), z(θ) = k·θ

where θ is in semitones; each 2π revolution = one octave; notes 12 semitones apart align vertically on the coil.

Tuning/scale guidance: 12-TET is the default; pentatonic or major/minor scales recommended for sonification (less dissonant for untrained listeners); microtonal scales (24/31-TET) offer finer resolution but need listener training. Historical lineage: Pythagoras → Euler's Tonnetz → Neo-Riemannian lattices → Shepard's helix (1964) → Chew's spiral array (2001).

## Key mappings/parameters to preserve

- p = log2(f) — always work in log-frequency
- Semitone frequency: f_n = f_ref · 2^(n/12)
- Two concrete mapping recipes from §2.7:
  - Function grapher: x → time, f(x) → θ (angle on pitch-class circle); large excursions traverse octaves vertically
  - Data streams: map differences between consecutive points to Δθ → fluctuations become melodic arcs (relative/derivative mapping, not absolute!)
- Data can be snapped mod 12 into one octave or spread across octaves — a design choice

## Ideas relevant to the LOOM game 🎮

- Pentatonic scale is our friend: pentatonic has no dissonant intervals between any two notes — perfect for young players; LOOM itself used simple diatonic notes. Quantizing spells to pentatonic makes every draft pleasant while staying distinguishable.
- The Δθ (difference) mapping is a big insight for spell design: mapping a function's changes rather than absolute values means the spell's melodic contour directly encodes the function's derivative behavior — linear = steady steps, exponential = accelerating leaps, sine = arcs. That's exactly what we want players to learn to hear!
- Visual congruence (§2.6): plot the helix on screen while the spell plays — players see the coil light up as they hear it. Great for the game's "Understanding Mode" à la Descent QED.

## Notes/questions

- Design decision to make later: per-spell, do we map f(x) → θ absolutely, or Δf → Δθ relatively? The book presents both; they'll sound quite different. Chapter 5 will likely settle this.
- Philharmonia samples are 12-TET pitched instruments → confirms we should stay in 12-TET and pick scale subsets (pentatonic/major/minor), no microtonality needed.
