# Chapter 6 — Rhythm, Meter, and Polyrhythms (Optional)

## Summary (project-oriented)

The first "optional layer" chapter: using time structure itself as a data channel, beyond just placing notes on a grid.

Two ways to encode data in rhythm:

1. Note durations — larger data value = longer note
2. Onset events — data crossing thresholds triggers an extra beat or skips one

Polyrhythms as a parallel-data channel: two simultaneous pulse streams at different subdivisions (classic 3:4) — Stream A divides the measure into 3, Stream B into 4; they align only at measure boundaries, creating interference patterns in between. Each stream carries a different data series. If the data sets are correlated, the streams' interplay reveals it audibly.

Practical guidance:

- Meters: simple (4/4, 3/4) for regularity; odd meters (5/4) can highlight irregular cycles
- Chunk large data into measures (one chunk = one measure); loop or progress measure-by-measure
- Separate polyrhythmic voices by timbre/register (e.g., bell for the 3-stream, bass for the 4-stream) so the ear can track them
- ⚠️ Limits: 3:4:5 and beyond overloads listeners; polyrhythm implies "musical time," awkward for continuous real-time streams

## Key mappings/parameters to preserve

- Duration ← data magnitude; threshold-crossings ← rhythmic events
- 3:4 as the canonical demo (measure ≈ 2 s, 3 triggers vs. 4 triggers)
- Voice separation rule: distinct timbre + distinct register per stream

## Ideas relevant to the LOOM game 🎮

- Polyrhythm = the two-player mechanic! ❤️ This is the most Peak-Together idea in the book: Player 1's controller drives the 3-voice, Player 2's drives the 4-voice — a co-op spell only works when both streams align correctly at the measure boundary. Talking to each other to sync up is literally the gameplay.
- Rhythm can encode function features for free: e.g., trigger a percussive "tick" at every zero crossing of the function — a damped sine's ticks accelerate then vanish; a pure sine's ticks stay steady. Kids can hear frequency behavior without any pitch at all!
- Duration ← |f(x)| adds a second fingerprint to short drafts: the decaying wave gets progressively shorter, softer notes — very intuitive.
- Restraint note: LOOM drafts were rhythmically flat (equal notes), which aided memorability. Suggest: basic spells = flat rhythm (pure pitch contour), advanced spells = rhythm layer added. Difficulty tiers emerge naturally.

## Notes/questions

- Polyrhythm is best saved for special co-op "boss spells" rather than the core spellbook — it's the most cognitively demanding layer, matching the book's own overload warning.
