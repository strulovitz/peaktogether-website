# Chapter 3 — Implementing the Helical Pitch Axis

## Summary (project-oriented)

This is the implementation recipe for the pitch axis. The full pipeline from data to notes:

1. Map data to angle: θ = a·f(x), where a is a scaling factor controlling pitch sensitivity
2. Choose a perceptually: e.g., if f(x) ∈ [0,10] and you want ≤ 2 octaves of range, pick a so θ spans at most 2π·2. Ideally, expose a as a user slider.
3. Quantize to a scale: RoundToScale(θ_real) = arg min over s ∈ ScaleSet of |θ_real − s|, with e.g. ScaleSet = {0,2,4,5,7,9,11} (major scale, in semitones); practically: round(θ_real), then mod 12 + snap to scale subset
4. Sample on a rhythmic grid: increment time t in musical subdivisions (8th/16th notes at a chosen BPM); either step x linearly, x(t) = x0 + Δx·t, or feed real data
5. Geometry constants: with k = 1/(2π), each octave raises z by exactly 1.0 (each semitone by 1/12); r is mostly visual

Anti-siren toolkit (the chapter's namesake concern):

- Quantize pitch to discrete scale notes ✂️
- Give each note a clear attack/decay envelope (no continuous tones)
- Trigger note changes only at grid intervals; downsample/smooth noisy data (rolling average)
- Limit range: e.g., θ ∈ [0,24] semitones above a base pitch — keeps everything comfortably audible

## Key mappings/parameters to preserve

- θ = a·f(x) — the master mapping equation
- k = 1/(2π) — octave = 1.0 in z (nice normalization convention)
- Major ScaleSet {0,2,4,5,7,9,11}; (pentatonic would be {0,2,4,7,9})
- Recommended range cap: ~2 octaves (24 semitones)
- Extra expressive channel suggested: amplitude/velocity ← data magnitude or derivative

## Ideas relevant to the LOOM game 🎮

- This pipeline is essentially our spell compiler: function → sample at N beats → θ = a·f(x) → snap to scale → note list → play Philharmonia samples. Clean, deterministic, and each function gets a reproducible motif. ✨
- The 2-octave cap is game-gold: Philharmonia instruments each cover their comfortable range well; capping spells at ~2 octaves means one instrument can play any spell without awkward register jumps.
- The scaling slider a could become a game mechanic itself: an advanced puzzle where players "zoom" pitch sensitivity to reveal fine structure of a function — like zooming a graph, but by ear! 🔍
- Velocity ← derivative gives free expressiveness: exponential spells get louder as they leap, damped sines fade as they settle — reinforcing the math through a second perceptual channel.

## Notes/questions

- Note the mapping here is absolute (θ = a·f(x)), while Ch.2 §2.7 also floated relative (Δf → Δθ). Part B uses absolute as the default — I'll watch whether Ch.5 confirms this.
- For LOOM-style short drafts (4–8 notes), "smoothing" ≈ just sampling the function at few well-chosen points — the sparse sampling is the downsampling. 👍
