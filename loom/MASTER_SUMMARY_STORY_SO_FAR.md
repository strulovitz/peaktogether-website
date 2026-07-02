# 📋 Story So Far (master summary — v4)

- **Book: Sounding the Unknown** — HSS: auditory coordinates. Pitch helix: x = r·cosθ, y = r·sinθ, z = k·θ, k = 1/(2π) (octave = 1.0 in z); p = log2 f, 12-TET. Pitch pipeline (Ch.3): θ = a·f(x) (≤2 octaves) → snap to ScaleSet via argmin (major {0,2,4,5,7,9,11}; pentatonic friendly) → notes on BPM grid → attack/decay envelopes; smooth noisy data; velocity ← magnitude/derivative. Timbre (Ch.4): single brightness T = β·g(x); methods: 2nd-harmonic scaling, filter cutoff f_c = f_min + T(f_max − f_min), or sample crossfade; pitch primary, timbre slow/secondary; tandem (f drives both) or split (g = e.g. derivative). Rules (Ch.1): no sweeps, ≤2 timbre params, beat grid, stable mappings. Ahead: Ch.5 mapping scheme + damped sine e^(−x)·sin(10x). Refs: Shepard 1964, Chew 2001, Grey 1977.

- **Project goal:** LOOM-remake (peaktogether.me) — spells = sonic signatures of functions via spell compiler (sample function → θ → scale snap → Philharmonia playback). Game adaptations: timbre axis = instrument switching or LP-filtered samples or Philharmonia dynamic layers (pp/mf/ff); discrete timbre steps for memorability; timbre ← derivative teaches growth-by-ear. Open Q: absolute vs. relative pitch mapping (check Ch.5).

- **Read so far:** Front matter ✅ · Ch.1 ✅ · Ch.2 ✅ · Ch.3 ✅ · Ch.4 ✅
