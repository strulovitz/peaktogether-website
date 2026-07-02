# 📋 Story So Far (master summary — v3)

- **Book: Sounding the Unknown** — HSS: auditory Cartesian coordinates. Pitch helix: x = r·cosθ, y = r·sinθ, z = k·θ, with k = 1/(2π) so 1 octave = Δz of 1.0; θ in semitones; p = log2 f; 12-TET. Pitch pipeline (Ch.3): θ = a·f(x) (scaling a user-tunable, target ≤ 2 octaves ≈ 24 semitones) → quantize via arg min over s ∈ ScaleSet of |θ − s| (major {0,2,4,5,7,9,11}; pentatonic recommended for pleasantness) → trigger notes on BPM grid (8th/16th subdivisions), x(t) = x0 + Δx·t → apply attack/decay envelopes; smooth noisy data; optionally velocity ← magnitude/derivative. Timbre: single brightness param (Ch.4 ahead). Design rules (Ch.1): no sweeps, ≤2 timbre params, beat grid, stable mappings. Key example ahead: e^(−x)·sin(10x) (Ch.5). Refs: Shepard 1964, Chew 2001.

- **Project goal:** LOOM-remake (peaktogether.me) — spells = short sonic signatures of functions via "spell compiler": sample function at N beats → θ mapping → scale snap → Philharmonia note playback. 2-octave cap suits single instruments. Open Q: absolute vs. relative mapping (Ch.3 uses absolute; check Ch.5).

- **Read so far:** Front matter ✅ · Ch.1 ✅ · Ch.2 ✅ · Ch.3 ✅
