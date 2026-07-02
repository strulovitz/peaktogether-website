# 📋 Story So Far (master summary — v1)

- **Book: Sounding the Unknown** — HSS (Helical Sonification System): auditory Cartesian coordinates. (1) Pitch helix: 1 turn = 1 octave, z = continuous pitch height, θ = semitone angle; (2) single timbre parameter (brightness); (3) discrete rhythmic time grid. Design rules from Ch.1 pitfalls: quantize pitch to scales, ≤2 timbre params, mandatory beat grid, one-to-one stable mappings. General scheme (Ch.5): x → time, f(x) → pitch, df/dx → timbre. Optional layers: polyrhythm, emotional shading (major/minor + dynamics). Key example: e^(−x)·sin(10x). References: Shepard 1964 (pitch helix), Chew (spiral array). Toolchain: Python/numpy/sounddevice.

- **Project goal:** LOOM-remake for peaktogether.me — spell "drafts" = short sonic signatures of math functions (Philharmonia samples); trains ear to distinguish functions. Ch.1's educator use-case + discrete-beat motifs = perfect LOOM fit.

- **Read so far:** Front matter ✅ · Ch.1 ✅
