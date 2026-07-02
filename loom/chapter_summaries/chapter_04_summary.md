# Chapter 4 — Timbre as a Second Dimension

## Summary (project-oriented)

Adds the second axis: timbre, deliberately reduced to a single "brightness" parameter T (dark → bright). The chapter acknowledges timbre is really multi-dimensional (Grey 1977, McAdams: spectral centroid, attack/decay transients, spectral flux) but flattens it to one axis for perceptual clarity.

Three implementation methods:

1. Harmonic scaling (simplest, book's default): wave(t) = A·sin(2πft) + T·B·sin(2π·2f·t); higher T = stronger 2nd harmonic = brighter/buzzier
2. Filter cutoff: f_c = f_min + T·(f_max − f_min); higher T = more high frequencies pass = brighter
3. Sample/wavetable crossfade — blend between a "dark" sample and a "bright" sample (mentioned as advanced)

Mapping: T = β·g(x) with sensitivity factor β (parallel to pitch's a). Two configurations:

- Same stream drives both: θ = a·f(x), T = β·f(x) → pitch and brightness move in tandem, creating a distinctive sonic "shape"
- Separate streams: f(x) → pitch, g(x) → timbre (e.g., the derivative)

Warnings: fast pitch + fast timbre changes = listener overload (smooth the timbre motion); high harmonics get harsh on consumer speakers/headphones; timbre can overshadow pitch if overused.

## Key mappings/parameters to preserve

- T = β·g(x); keep T's range bounded to avoid harshness
- Rule of thumb: pitch = primary channel, timbre = secondary/slow channel
- Timbre's real dimensions (for future reference): spectral centroid, attack time, spectral flux

## Ideas relevant to the LOOM game 🎮

- Big adaptation point: the book synthesizes waveforms, but we use Philharmonia recordings. Our translation options:
  - Method 3 is our native fit 🎯 — crossfade or switch between instruments! E.g., dark→bright = cello → viola → violin → flute. Instrument choice becomes the timbre axis.
  - Or apply a low-pass filter (Method 2) on the samples — easy with scipy, keeps one instrument per spell.
- Even simpler for a kids' game: quantize timbre too! Instead of continuous brightness, use 2–3 discrete instrument "registers" per spell. Discrete = memorable = LOOM-like.
- Timbre ← derivative is pedagogically sweet: a sine spell keeps constant-ish brightness while pitch arcs; an exponential spell gets steadily brighter — players learn "growing functions sound increasingly urgent." 🔥
- The "tandem" configuration (§4.5) gives each function a richer fingerprint even from few notes — useful since LOOM drafts are short (4–8 notes).

## Notes/questions

- Philharmonia samples come per-note, per-dynamic (pp/mf/ff) and per-articulation — dynamics layers could serve as a free timbre/intensity axis (mf → ff = brighter + louder) without any DSP. Worth remembering when we implement.
- Still watching the absolute-vs-relative mapping question for Ch.5.
