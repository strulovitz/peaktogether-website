# 📋 Story So Far (master summary — v6)

- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (Ch.3+5, absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale (major {0,2,4,5,7,9,11}; pentatonic friendly) → BPM grid → envelopes; velocity ← magnitude/derivative. Timbre (Ch.4): T = β·g(x); 2nd harmonic / filter cutoff / sample crossfade; slow, secondary. Ch.5: damped sine e^(−x)·sin(10x), x ∈ [0, 3π], Δx = 0.2, a = 15; cycloid: y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude; threshold crossings → rhythmic events; polyrhythm (3:4, ~2s measure) = parallel data streams, separate by timbre+register; chunk data into measures; avoid 3:4:5+. Architecture: Program A (function→CSV) / Program B (playback) + sliders. Refs: Shepard 1964, Chew 2001, Grey 1977.

- **Project goal:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: offline spell compiler → JSON → in-game player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid. Difficulty tiers: basic = flat-rhythm pitch contour → advanced = +timbre, +rhythm (zero-crossing ticks, duration ← |f|) → co-op boss spells = 3:4 polyrhythm, one voice per player ❤️.

- **Read so far:** Front matter ✅ · Ch.1–6 ✅
