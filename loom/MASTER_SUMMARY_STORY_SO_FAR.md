# 📋 Story So Far (master summary — v5)

- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π) (octave = 1.0); p = log2 f, 12-TET. Pipeline (Ch.3+5, ABSOLUTE mapping): θ = a·f(x) → condition data (clamp, shift negatives, log(1+|y|) for blow-ups, smooth wiggles) → snap to ScaleSet argmin (major {0,2,4,5,7,9,11}, pentatonic friendly) → notes on BPM grid → envelopes; velocity ← magnitude/derivative. Timbre (Ch.4): T = β·g(x), brightness via 2nd harmonic / filter cutoff f_c = f_min + T(f_max − f_min) / sample crossfade; slow & secondary. Ch.5 examples: damped sine e^(−x)·sin(10x), x ∈ [0, 3π], Δx = 0.2, a = 15; parametric curves: cycloid y(t) → pitch, x(t) → timbre. Architecture: Program A (function→note CSV) / Program B (play) + sliders (a, x_max, tempo). Rules: no sweeps, ≤2 timbre params, beat grid. Refs: Shepard 1964, Chew 2001, Grey 1977.

- **Project goal:** LOOM-remake (peaktogether.me) — spells = function signatures, Philharmonia samples. Adopted design: A/B split = offline spell compiler (JSON) + in-game sample player; spellbook v1: line, parabola, sine, damped sine, exponential, cycloid (pitch+timbre = advanced tier); timbre = instrument switch / LP filter / pp-mf-ff dynamic layers; discrete timbre steps; "spell laboratory" slider mode.

- **Read so far:** Front matter ✅ · Ch.1–5 ✅
