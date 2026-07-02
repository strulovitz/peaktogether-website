# 📎 Summaries Bundle for Claude Fable

> Paste this whole file directly beneath the BIBLE mission prompt. It contains all of Fable's chapter-by-chapter summaries (front matter + Ch.1-10) followed by the running master summary (all versions v0 -> v10).

===================================================================
# PART 1 - CHAPTER-BY-CHAPTER SUMMARIES
===================================================================

# Chapter 00 — Front Matter (Epigraphs, Back Cover, Preface, ToC, Detailed Outline)

## Summary (project-oriented)

The book introduces the Helical Sonification System (HSS), framed as a "sonic coordinate system" — an auditory analogue of Descartes' Cartesian plane. Just as Cartesian coordinates let us see equations, HSS lets us hear them. The core architecture is a "three-axis + optional expansions" model:

| Axis | Musical dimension | Data role |
|------|-------------------|-----------|
| 1 | Pitch (helix) | Primary value of the function, f(x) |
| 2 | Timbre (brightness/filter cutoff, 1 parameter) | Secondary dimension (e.g., derivative df/dx) |
| 3 | Time (musical timeline) | The independent variable x |
| +Optional | Rhythm/polyrhythm | Extra dimensions or thresholds |
| +Optional | Emotional shading (major/minor, dynamics) | Valence/arousal overlay |

The helix resolves pitch's dual nature: cyclical (octave equivalence — chroma, angle θ) and linear (rising frequency — height z). Key formula previewed for Chapter 3:

x(θ) = r·cos(θ), y(θ) = r·sin(θ), z(θ) = k·θ

where θ corresponds to semitones. The book explicitly warns that naive "function playback" fails — it produces siren-like sweeps that are neither musical nor informative. Solutions previewed: scale quantization, rhythmic subdivision, envelope shaping (§3.4, §5.2).

## Key mappings/parameters to preserve

- General scheme (§5.1): x → time steps, f(x) → pitch on helix, df/dx → timbre
- Timbre kept deliberately one-dimensional (brightness/spectral centroid) for musicality
- Emotional model references: Hevner's circle, Russell's circumplex; minimal implementation = major/minor toggle + dynamic range
- Signature worked example: damped sine f(x) = e^(−x)·sin(10x) (§5.3)

## Ideas relevant to the LOOM game 🎮

- §10.2 explicitly names "gaming integrations" as a future direction — the book anticipated your game!
- The catalog of planned sonified objects = ready spellbook candidates: damped sine, Brachistochrone, planetary orbits, Lissajous curves, fractals, time-series data
- Multi-voice sonification (§8.1) → could map to two-player mechanics (each player hears/controls a different voice — very Peak Together ❤️)
- The "fear factor" / dissonance-as-primal-alarm concept → great for game feedback (wrong spell = subtle roughness/dissonance, right spell = consonant resolution)

## Notes/questions

- The Preface mentions co-author DeepSeek R1 in the technical treatment's byline — fitting that DeepSeek is now on the team again 😄
- No open questions yet; this chapter is a roadmap. The real meat starts at Chapter 2–3 (helix math) and Chapter 5 (mapping scheme).

---

# Chapter 1 — Introduction and Motivation

## Summary (project-oriented)

This chapter is the "why" of HSS, in two parts (a concise Part A + expanded Part B). The core argument: sonification has a long history (Mersenne/Newton's speculations → Xenakis/Hiller's stochastic compositions → NASA's data sonifications since the 1980s), but most attempts fail because they lack musical scaffolding. Three named failure modes:

1. Raw function playback (e.g., Mathematica's Play[]) → continuous glissandi, "vacuum cleaner" drones
2. Overloaded timbre — encoding too many parameters at once overwhelms the ear; keep to 1–2 timbre parameters max
3. No clear mapping logic — if data→sound correlations aren't perceptually stable, listeners can't build mental models

The fix is a coordinate-based approach — the auditory analogue of Cartesian coordinates:

- Pitch helix: one full turn = one octave (cyclic chroma), vertical rise = continuous frequency
- Timbre axis: one parameter (brightness / filter cutoff / spectral centroid), deliberately minimal
- Discrete time grid: data events sliced into beats/measures, not raw time increments — the ear needs pulse to parse patterns

Target audiences named: scientists, educators (explicitly: teaching functions and derivatives through auditory analogies for students who struggle with visual/symbolic approaches — literally your game's mission 🎯), and musicians.

## Key mappings/parameters to preserve

- Design commandments distilled from pitfalls:
  - ✅ Quantize pitch to scales (never continuous sweeps)
  - ✅ Max 1–2 timbre parameters
  - ✅ Rhythmic grid mandatory — discrete beats, not arbitrary timing
  - ✅ Stable, explicit mapping logic — each data dimension → exactly one audible parameter
- Toolchain assumed: Python + numpy, matplotlib, sounddevice, optionally ipywidgets

## Ideas relevant to the LOOM game 🎮

- The three pitfalls are our spell-design QA checklist: every spell must be quantized, rhythmically gridded, and timbre-simple — otherwise players can't memorize/distinguish them (exactly the "stable mental representation" problem)
- The educator use-case validates the game concept directly: HSS was designed for teaching functions by ear
- The discrete time grid maps beautifully onto LOOM's mechanic: LOOM drafts were discrete note sequences — HSS's beat-sliced approach naturally produces LOOM-compatible motifs

## Notes/questions

- Scholarly anchors worth keeping for the website's "learn more" pages: Shepard (1964) — origin of the pitch helix; Elaine Chew (2014) — spiral array model (3D pitch/chord/key spaces — could inspire in-game visuals of the helix!); Diana Deutsch; Carla Scaletti (Kyma); Xenakis
- Still conceptual — the math starts next chapter.

---

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

---

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

---

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

---

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

---

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

---

# Chapter 7 — Emotional Shading (Optional)

> Fable delivered his Chapter 7 answer in TWO parts. Both are preserved below.
> PART 1 = the more detailed version (note: it assumed a kids'/family audience, which was later corrected — the game is for ~20-year-olds).
> PART 2 = the corrected version (audience ~20-year-olds; full fear/tension palette in scope).

---

## PART 1 (detailed version)

### Summary (project-oriented)

Three parts: A/B give the minimal valence-arousal implementation; Part C is a deep dive into psychoacoustic triggers of fear/tension — the "fear factor" promised on the back cover.

Minimal implementation (Parts A–B) — Russell's circumplex model: two orthogonal axes.

- Valence (positive/negative) → scale choice: scale = major if v ≥ 0, minor if v < 0 (or smooth blending for intermediate states)
- Arousal (calm/excited) → tempo and/or dynamics (louder + faster = more aroused)
- Caveats: major/happy vs. minor/sad is culturally learned, not universal (Smit et al. 2022); mode toggling alone can feel gimmicky
- Richer alternatives: legato/staccato, crescendo/diminuendo, instrument selection

The fear toolbox (Part C) — Deep biological roots: rough/chaotic sounds mimic animal distress calls and screams, triggering amygdala circuits before conscious thought (Blumstein 2010, Arnal 2015). Rising pitch = "looming threat" (Neuhoff). Tempo entrains heart rate (Gomez & Danuser 2007). Frameworks: BRECVEMA (Juslin — how music induces emotion: brainstem reflex, rhythmic entrainment, conditioning...) and GEMS (Zentner — which emotions: tension, wonder, transcendence...).

Modulation rates:

| Rate | Effect |
|------|--------|
| 20–150 Hz AM | "roughness band" — screams, sirens, amygdala fear |
| 30–40 Hz FM | growling, monstrous roars |
| 2–8 Hz tremolo | trembling, ghostly whispers |

Tempo:

| BPM | Emotional register |
|-----|--------------------|
| 50–80 | suspense, creeping dread |
| 80–110 | building anxiety |
| 120–160 | action, adrenaline |
| >160 + dissonance | chaotic panic |

Dissonant intervals:

| Interval | Effect |
|----------|--------|
| Minor 2nd | high tension (Jaws: E–F accelerating = heartbeat) |
| Tritone | "Devil's Interval," unresolved unease |
| Minor 9th | extreme dissonance (screechy clusters, Psycho) |

Case studies: Dalek ring-mod (~30 Hz carrier), Jaws, Psycho strings, Silent Hill (industrial sirens, 60–90 BPM drones), Resident Evil (calm save rooms ↔ dissonant boss escalation 110→130+ BPM), Dead Space (adaptive to player vitals), DOOM 2016 (100→160+ BPM combat).

### Key mappings/parameters to preserve

- Valence → mode toggle; Arousal → tempo/dynamics — the clean 2D emotional API
- The §7.6 range tables above (BPM bands, roughness bands, interval effects)
- Resident Evil "save room" pattern: deliberate calm-zone music as emotional contrast/relief

### Ideas relevant to the LOOM game 🎮

- ⚠️ Gentle-touch principle first: this is a game for kids on a family site — we want tension, never terror. The book's tools work at low intensity too: a touch of minor mode + slower tempo = "mysterious," not scary. [NOTE: audience later corrected to ~20-year-olds — see Part 2.]
- Feedback via consonance/dissonance 🎯: cast the spell correctly → consonant confirmation chord (major); slightly wrong → a gentle minor-2nd "wobble" nudging you to retry. The player feels correctness before the game says anything.
- Adaptive tempo as difficulty/excitement dial: practice mode ~70 BPM (suspense-calm band), challenge mode ~110 (building), timed "boss" spells ~130 (excitement) — straight from the BPM table, capped well below panic range.
- Save-room equivalent: LOOM's original had serene island themes between challenges — a calm major-key "spellbook study" area between levels matches both LOOM and Resident Evil's contrast principle. 🏝️
- Evaluative conditioning (BRECVEMA) is secretly the whole game: repeated pairing of a motif with a function is the learning mechanism. The book just gave us the theory name for our core loop!
- Valence could even encode math: functions with negative values dip into minor mode; positive functions stay major — the mode shift itself carries information. Elegant. ✨

### Notes/questions

- Philharmonia samples make dissonance easy (just play a minor 2nd) but roughness/AM effects would need DSP — probably unnecessary for our audience. Skip the roughness band entirely?
- Part C's length suggests the authors were passionate about this — worth an easter-egg "haunted spell" for older players? 👻 (Tastefully!)

---

## PART 2 (corrected version — audience: ~20-year-olds)

Correction: the "family site → kids" assumption in Part 1 was wrong. The game is for ~20-year-old players. This changes the Chapter 7 takeaways substantially — for the better.

### Revised Ch.7 game notes (audience: ~20-year-olds)

- Part C is now fully usable, not something to soften. The fear/tension toolbox is exactly what makes games gripping for adult players:
  - Roughness band (20–150 Hz AM) — fair game for failed casts, corrupted spells, or menacing entities. Worth the DSP effort after all.
  - Tritones, minor 2nds, clusters — real dissonance for real stakes, not gentle wobbles.
  - Full BPM range: exploration ~80–110, combat/challenge 120–160, and yes — >160 + dissonance chaotic-panic tier for climactic boss spells (the DOOM/Dead Space playbook).
- Dark spell tier becomes a core feature, not an easter egg: a "forbidden spellbook" of functions rendered with the horror palette — the Dalek-style ring-mod, Jaws-style accelerating semitones — is a legitimate design pillar now. 🖤
- The Resident Evil save-room contrast still applies (it's an adult-game pattern anyway): calm study area ↔ tense casting encounters. Contrast is what makes the tension land.
- What stays unchanged: consonance/dissonance as instant feedback, evaluative conditioning (BRECVEMA) as the learning loop, mode-as-data (minor when f<0), adaptive tempo — these were audience-independent.

---

# Chapter 8 — Advanced Topics and Scaling Up

## Summary (project-oriented)

The "make it big" chapter — three scaling axes: multi-voice, large data, real-time interactivity.

Multi-voice sonification (§8.1):

- When one pitch+timbre channel isn't enough, split variables across voices: e.g., v1 → Voice A (pitch+timbre), v2 → Voice B (an octave higher), v3, v4 → polyrhythmic triggers/amplitude
- Hard rules for separability: limit to 2–4 voices; separate by register (low vs. high) AND timbre family (strings vs. bells vs. brass) — echoes Ch.6's voice-separation rule
- Voices can also interact musically: call-and-response, polyrhythmic interplay

Large data strategies (§8.2):

- Chunking: window the data, summarize each chunk (mean/median/max–min) → one note or measure per chunk; long data = multiple "movements"
- Dimensionality reduction: PCA → few principal axes → each mapped to one sonic dimension; clustering → each cluster gets its own instrument/chord
- Layering (the "soundscape" recipe): base pitch line = main trend + rhythmic motif overlays on threshold events + ambient drone = global mean/std as slowly shifting chord — needs careful volume balancing

Real-time (§8.3):

- Use cases: live sensors (EEG, seismographs), interactive exhibits, VR "data playgrounds" where movement through space changes what you hear
- Technical: minimize latency (small audio buffers, more CPU), preprocess/cache for big data, expose intuitive controls (MIDI, hand tracking, sliders)

Pitfalls (§8.4): cacophony → provide per-voice mute toggles; performance → precompute; and users need layered learning/tutorials to parse multi-voice sound.

## Key mappings/parameters to preserve

- 2–4 voice ceiling; register + timbre separation mandatory
- Chunk-and-summarize pattern for long series
- Three-layer soundscape template: trend line / event motifs / stat-drone
- "Mute voice" as a first-class UX feature

## Ideas relevant to the LOOM game 🎮

- The three-layer soundscape = our level ambience engine 🌌: each game area could have a drone derived from that level's "theme function" statistics, with event motifs triggered by gameplay — the world itself is sonified, not just the spells. Very atmospheric for a 20-something audience raised on Journey/Hyper Light Drifter-style audio design.
- §8.4's "user training" point is literally our game: the book admits multi-voice sonification needs tutorials and layered learning — our tier progression (flat melody → +timbre → +rhythm → polyrhythm co-op → dark tier) is that curriculum, gamified. We're building the training the book says users need. 🎯
- Per-voice mute → gameplay verb: in co-op polyrhythm spells, letting a player "solo" their own voice to practice their part, then unmute the partner — great difficulty ramp and a natural communication moment.
- Chunk-summarize is the answer if we ever sonify player performance data (e.g., a "replay anthem" of your session stats as an end-of-level flourish).
- Multi-voice spells = late-game content: a 2-voice spell where melody encodes f(x) and a bass voice encodes f′(x) — hearing a function with its derivative in counterpoint. Peak difficulty, peak pedagogy. 🔥

## Notes/questions

- Real-time synthesis latency concerns barely apply to us — Program A/B split means spells are precompiled; only the interactive "spell laboratory" mode needs low-latency playback, and triggering pre-loaded Philharmonia samples is cheap.
- PCA/clustering: noted but likely out of scope for the game — flagging as "website 'learn more' material" rather than game features.

---

# Chapter 9 — Practical Applications and Case Studies

## Summary (project-oriented)

The "proof it works" chapter: three concrete case studies + future directions.

Case studies:

- Brachistochrone 🛷 — the fastest-descent curve (a cycloid, per Bernoulli/Newton/Leibniz). Mapping: parametric time → note triggers, y-value → pitch (scale-snapped), curvature/slope → timbre (steeper = brighter). Key payoff: comparative sonification — you can hear the cycloid beating a parabola to the bottom, because its pitch descends more swiftly.
- Planetary orbits & resonances 🪐 — each body = one voice, pulsing on orbital-phase fractions. Near-integer resonances (e.g., 2:3 period ratios) become audible polyrhythmic alignments — moments of "consonance" when orbits sync. Ch.6's polyrhythm machinery applied to real celestial mechanics.
- Statistical data 📈 — climate: chunked 150-year temperature anomalies → rising pitch baseline (warming trend) + melodic oscillations (short-term cycles). Stocks: closes/volume → pitch/timbre; crashes = dissonant bursts; some traders reportedly recognize patterns by ear.

Future directions (§9.2):

- AI/ML: adaptive mapping strategies, generative themes per data cluster, LLMs proposing emotive progressions
- VR/AR: spatial audio (streams from distinct directions), gesture control (grab a curve, hear it change), walking through PCA space
- Biofeedback: heart rate / skin response adjusting tension/dissonance in real time; therapeutic/meditative sonification

Pitfalls (§9.3): density/chaos (→ tutorials, incremental layering, mute/isolate — reiterating Ch.8); real-time needs sub-50 ms latency; recommended middleware: Csound, Wwise, FMOD; precompute/offload heavy transforms.

## Key mappings/parameters to preserve

- Brachistochrone recipe: time → triggers, y → pitch, slope/curvature → timbre
- Orbital resonance = polyrhythm with ratios from period ratios (2:3 etc.)
- Trend + oscillation decomposition for time-series (baseline pitch + melodic wiggle)
- Sub-50 ms latency bar for interactive audio

## Ideas relevant to the LOOM game 🎮

- The brachistochrone is a ready-made level! 🏆 A "race puzzle": the player hears 2–3 descent curves sonified and must pick the fastest by ear before seeing them. Then the reveal animates the beads racing down. Comparative listening as gameplay — this is the strongest single game idea in the book so far.
- Orbital resonance = the lore-friendly co-op boss: our planned 3:4 polyrhythm co-op spell can literally be an orbital-resonance encounter (two players = two celestial bodies; the spell completes when their pulses align). Gives the mechanic a gorgeous theme and a real-physics anchor. 🌌
- Comparative sonification generalizes: "which grows faster, x² or e^x?" as by-ear duels — a whole quiz mode falls out of the brachistochrone pattern.
- Slope → timbre confirms our earlier "timbre ← derivative" instinct (Ch.4 notes) — now book-endorsed via the brachistochrone case.
- Latency check: sub-50 ms for triggering preloaded samples in the browser (Web Audio API) is very achievable — no need for Wwise/FMOD-class middleware at our scale.
- Biofeedback + VR: out of scope, but the meditative sonification idea could inspire the calm study-zone soundscape.

## Notes/questions

- The stock/climate examples suggest a possible post-launch mode: "sonify your own data" sandbox (upload CSV → hear it as a spell). Community content potential for peaktogether.me? Parking the thought.
- One chapter's worth of signals says the book is winding toward implementation/appendices — expecting code next.

---

# Chapter 10 — Conclusion and Future Directions

## Summary (project-oriented)

A retrospective + horizon-scan chapter. The recap of Ch.1–9 matches our running summaries (nothing new to correct ✅ — good validation of our notes). The substantive new content is in limitations and future directions:

Limitations acknowledged (§10.2):

- Learning curve — users need training to parse pitch/rhythm/timbre as data (the book's recurring refrain)
- Individual differences in pitch/rhythm acuity
- Cultural variance in emotional connotations; too much emotional intensity can distract from the data
- Technical: latency for real-time; messy data needs preprocessing

Future directions (§10.3) — the new ideas:

- Microtonality: beyond 12-TET → 19-TET, 24-TET, or just intonation — finer pitch resolution could reveal subtler data variations
- AI-adaptive sonification: ML picks optimal scale/timbre for the data; if the user misses an anomaly, the system escalates (more dissonance, louder pitch); reinforcement learning to discover which mappings maximize comprehension
- VR/AR: physically walk around the pitch helix; gestures control pitch/timbre; polyrhythm streams placed at different spatial locations — walk toward a stream to focus on it
- Clinical & STEAM education: biofeedback therapy; multi-sensory math labs, notably for visually impaired students

Closing thesis: HSS aims for music-like structures, not beeps — data as music that is simultaneously aesthetic and interpretable.

## Key mappings/parameters to preserve

- The adaptive-escalation pattern: unnoticed anomaly → intensify dissonance/volume
- Microtonal option flagged (12-TET was a convenience choice, not a necessity)
- Spatial placement of rhythm streams as a focus/attention mechanism

## Ideas relevant to the LOOM game 🎮

- Adaptive escalation → hint system 🎯: if a player repeatedly fails to distinguish two spells, the game quietly widens the difference (bigger a, added timbre contrast), then narrows it back as they improve. The book proposes this for anomaly detection; for us it's an invisible, elegant difficulty-assist — no "hint" button needed.
- Microtonality = dark-tier flavor: detuned/microtonal renderings of familiar spells would sound uncannily wrong — perfect for the corrupted/forbidden spellbook aesthetic. Cheap to implement (pitch-shift samples by quarter-tones). 👻
- Spatial rhythm streams → stereo panning: the co-op polyrhythm boss gains clarity if Player 1's voice sits left, Player 2's right. Web Audio panning is trivial; the VR idea distills down to plain stereo for us.
- The "walk the helix" VR image could survive as a visual: rendering the pitch helix on-screen as spells play (notes lighting up along the spiral) would make the book's core geometry the game's signature visual motif. 🌀
- Accessibility note: the visually-impaired-education angle suggests our game is genuinely playable eyes-free by design — worth stating on the site as a feature, and worth protecting in UI decisions.

## Notes/questions

- The promised code never arrived in the main chapters — Ch.5 referenced "code examples" and Program A/B, so I expect appendices with the Python/CSV implementation. Do you have them? They'd be directly reusable for our spell compiler.
- With the book complete, natural next step: I can consolidate everything into a design-doc draft for the spell compiler + game audio systems whenever you want.

---

===================================================================
# PART 2 - MASTER SUMMARY (THE STORY SO FAR, v0 -> v10)
===================================================================

# 📋 Master Summary — The Story So Far

> Every version Fable produced is ADDED here in order (nothing erased). Newest is at the bottom.

---

## v0

- **Book: Sounding the Unknown** — introduces HSS (Helical Sonification System): data → music via (1) pitch helix [θ = semitone angle = chroma, z = pitch height], (2) one-dimensional timbre axis (brightness), (3) musical time, plus optional rhythm/polyrhythm and emotional shading (major/minor, dynamics). Naive playback = sirens; fix via scale quantization + rhythm + envelopes. Worked examples planned: damped sine e^(−x)·sin(10x), orbits, Lissajous, fractals, financial data.
- **Project goal:** LOOM-style game for peaktogether.me where "spell drafts" are short sonic signatures of mathematical functions (Philharmonia orchestral samples), training players to distinguish functions by ear.
- **Read so far:** Front matter ✅

---

## v1

- **Book: Sounding the Unknown** — HSS (Helical Sonification System): auditory Cartesian coordinates. (1) Pitch helix: 1 turn = 1 octave, z = continuous pitch height, θ = semitone angle; (2) single timbre parameter (brightness); (3) discrete rhythmic time grid. Design rules from Ch.1 pitfalls: quantize pitch to scales, ≤2 timbre params, mandatory beat grid, one-to-one stable mappings. General scheme (Ch.5): x → time, f(x) → pitch, df/dx → timbre. Optional layers: polyrhythm, emotional shading (major/minor + dynamics). Key example: e^(−x)·sin(10x). References: Shepard 1964 (pitch helix), Chew (spiral array). Toolchain: Python/numpy/sounddevice.
- **Project goal:** LOOM-remake for peaktogether.me — spell "drafts" = short sonic signatures of math functions (Philharmonia samples); trains ear to distinguish functions. Ch.1's educator use-case + discrete-beat motifs = perfect LOOM fit.
- **Read so far:** Front matter ✅ · Ch.1 ✅

---

## v2

- **Book: Sounding the Unknown** — HSS: auditory Cartesian coordinates. Pitch helix: x = r·cosθ, y = r·sinθ, z = k·θ; θ in semitones, 2π = 1 octave; log-pitch p = log2 f; 12-TET semitone = 2^(1/12) ratio; pitch classes = Z_12 = R/12Z. Timbre: single brightness parameter. Time: discrete beat grid (mandatory). Design rules (Ch.1): quantize to scales (pentatonic/major/minor recommended, Ch.2), ≤2 timbre params, stable one-to-one mappings, no continuous sweeps. Two mapping recipes (Ch.2 §2.7): absolute (f(x)→θ) or relative (Δf→Δθ, contour = derivative). Optional layers: polyrhythm, emotional shading. Key example ahead: e^(−x)·sin(10x) (Ch.5). References: Shepard 1964, Chew 2001 spiral array, Euler Tonnetz.
- **Project goal:** LOOM-remake for peaktogether.me — spells = short sonic signatures of math functions (Philharmonia 12-TET samples → pentatonic quantization ideal); trains ear to distinguish functions. Open design Q: absolute vs. relative pitch mapping per spell (await Ch.5).
- **Read so far:** Front matter ✅ · Ch.1 ✅ · Ch.2 ✅

---

## v3

- **Book: Sounding the Unknown** — HSS: auditory Cartesian coordinates. Pitch helix: x = r·cosθ, y = r·sinθ, z = k·θ, with k = 1/(2π) so 1 octave = Δz of 1.0; θ in semitones; p = log2 f; 12-TET. Pitch pipeline (Ch.3): θ = a·f(x) (scaling a user-tunable, target ≤ 2 octaves ≈ 24 semitones) → quantize via arg min over s ∈ ScaleSet of |θ − s| (major {0,2,4,5,7,9,11}; pentatonic recommended for pleasantness) → trigger notes on BPM grid (8th/16th subdivisions), x(t) = x0 + Δx·t → apply attack/decay envelopes; smooth noisy data; optionally velocity ← magnitude/derivative. Timbre: single brightness param (Ch.4 ahead). Design rules (Ch.1): no sweeps, ≤2 timbre params, beat grid, stable mappings. Key example ahead: e^(−x)·sin(10x) (Ch.5). Refs: Shepard 1964, Chew 2001.
- **Project goal:** LOOM-remake (peaktogether.me) — spells = short sonic signatures of functions via "spell compiler": sample function at N beats → θ mapping → scale snap → Philharmonia note playback. 2-octave cap suits single instruments. Open Q: absolute vs. relative mapping (Ch.3 uses absolute; check Ch.5).
- **Read so far:** Front matter ✅ · Ch.1 ✅ · Ch.2 ✅ · Ch.3 ✅

---

## v4

- **Book: Sounding the Unknown** — HSS: auditory coordinates. Pitch helix: x = r·cosθ, y = r·sinθ, z = k·θ, k = 1/(2π) (octave = 1.0 in z); p = log2 f, 12-TET. Pitch pipeline (Ch.3): θ = a·f(x) (≤2 octaves) → snap to ScaleSet via argmin (major {0,2,4,5,7,9,11}; pentatonic friendly) → notes on BPM grid → attack/decay envelopes; smooth noisy data; velocity ← magnitude/derivative. Timbre (Ch.4): single brightness T = β·g(x); methods: 2nd-harmonic scaling, filter cutoff f_c = f_min + T(f_max − f_min), or sample crossfade; pitch primary, timbre slow/secondary; tandem (f drives both) or split (g = e.g. derivative). Rules (Ch.1): no sweeps, ≤2 timbre params, beat grid, stable mappings. Ahead: Ch.5 mapping scheme + damped sine e^(−x)·sin(10x). Refs: Shepard 1964, Chew 2001, Grey 1977.
- **Project goal:** LOOM-remake (peaktogether.me) — spells = sonic signatures of functions via spell compiler (sample function → θ → scale snap → Philharmonia playback). Game adaptations: timbre axis = instrument switching or LP-filtered samples or Philharmonia dynamic layers (pp/mf/ff); discrete timbre steps for memorability; timbre ← derivative teaches growth-by-ear. Open Q: absolute vs. relative pitch mapping (check Ch.5).
- **Read so far:** Front matter ✅ · Ch.1 ✅ · Ch.2 ✅ · Ch.3 ✅ · Ch.4 ✅

---

## v5

- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π) (octave = 1.0); p = log2 f, 12-TET. Pipeline (Ch.3+5, ABSOLUTE mapping): θ = a·f(x) → condition data (clamp, shift negatives, log(1+|y|) for blow-ups, smooth wiggles) → snap to ScaleSet argmin (major {0,2,4,5,7,9,11}, pentatonic friendly) → notes on BPM grid → envelopes; velocity ← magnitude/derivative. Timbre (Ch.4): T = β·g(x), brightness via 2nd harmonic / filter cutoff f_c = f_min + T(f_max − f_min) / sample crossfade; slow & secondary. Ch.5 examples: damped sine e^(−x)·sin(10x), x ∈ [0, 3π], Δx = 0.2, a = 15; parametric curves: cycloid y(t) → pitch, x(t) → timbre. Architecture: Program A (function→note CSV) / Program B (play) + sliders (a, x_max, tempo). Rules: no sweeps, ≤2 timbre params, beat grid. Refs: Shepard 1964, Chew 2001, Grey 1977.
- **Project goal:** LOOM-remake (peaktogether.me) — spells = function signatures, Philharmonia samples. Adopted design: A/B split = offline spell compiler (JSON) + in-game sample player; spellbook v1: line, parabola, sine, damped sine, exponential, cycloid (pitch+timbre = advanced tier); timbre = instrument switch / LP filter / pp-mf-ff dynamic layers; discrete timbre steps; "spell laboratory" slider mode.
- **Read so far:** Front matter ✅ · Ch.1–5 ✅

---

## v6

- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (Ch.3+5, absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale (major {0,2,4,5,7,9,11}; pentatonic friendly) → BPM grid → envelopes; velocity ← magnitude/derivative. Timbre (Ch.4): T = β·g(x); 2nd harmonic / filter cutoff f_c = f_min + T(f_max − f_min) / sample crossfade; slow, secondary. Ch.5: damped sine e^(−x)·sin(10x), x ∈ [0, 3π], Δx = 0.2, a = 15; cycloid: y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude; threshold crossings → rhythmic events; polyrhythm (3:4, ~2s measure) = parallel data streams, separate by timbre+register; chunk data into measures; avoid 3:4:5+. Architecture: Program A (function→CSV) / Program B (playback) + sliders. Refs: Shepard 1964, Chew 2001, Grey 1977.
- **Project goal:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: offline spell compiler → JSON → in-game player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid. Difficulty tiers: basic = flat-rhythm pitch contour → advanced = +timbre, +rhythm (zero-crossing ticks, duration ← |f|) → co-op boss spells = 3:4 polyrhythm, one voice per player ❤️.
- **Read so far:** Front matter ✅ · Ch.1–6 ✅

---

## v7

- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale (major/pentatonic) → BPM grid → envelopes; velocity ← magnitude. Timbre: T = β·g(x) (2nd harmonic / filter / crossfade), slow & secondary. Ch.5: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude, threshold events, 3:4 polyrhythm = parallel streams (separate timbre+register). Emotion (Ch.7): valence → major/minor toggle, arousal → tempo/dynamics (Russell circumplex); fear toolbox: roughness 20–150 Hz AM, minor 2nd/tritone dissonance, BPM bands (50–80 dread / 80–110 anxiety / 120–160 action); BRECVEMA (mechanisms) + GEMS (emotion types); cultural caveats on mode. Architecture: Program A (compile) / B (play). Refs: Shepard, Chew, Grey, Juslin, Zentner.
- **Project goal:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: offline spell compiler → JSON → sample player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat-rhythm → +timbre/rhythm → co-op 3:4 polyrhythm ❤️. From Ch.7: consonant/dissonant feedback chords for right/wrong casts; adaptive BPM (70/110/130) for modes; calm "study island" between levels; minor mode when f<0 (mode = data); gentle-touch principle (tension, never terror); conditioning-by-repetition = the core learning loop (BRECVEMA).
- **Read so far:** Front matter ✅ · Ch.1–7 ✅

---

## v7.1 (corrected)

- ⚠️ **AUDIENCE:** ~20-year-old players. NOT a kids' game. Full emotional/tension palette from Ch.7 Part C is in scope (roughness DSP, real dissonance, high-BPM boss tiers, dark spell tier). Note: original website details are outside current context — don't invent specifics about peaktogether.me; ask if needed.
- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale (major/pentatonic) → BPM grid → envelopes; velocity ← magnitude. Timbre: T = β·g(x) (2nd harmonic / filter / crossfade), slow & secondary. Ch.5: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude, threshold events, 3:4 polyrhythm = parallel streams. Emotion (Ch.7): valence → major/minor, arousal → tempo/dynamics; fear toolbox: 20–150 Hz AM roughness, minor 2nd/tritone/minor 9th, BPM bands (50–80 dread / 80–110 anxiety / 120–160 action / >160 panic); BRECVEMA + GEMS. Architecture: Program A (compile) / B (play).
- **Project:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: offline spell compiler → JSON → sample player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat-rhythm → +timbre/rhythm → co-op 3:4 polyrhythm → dark/boss tier w/ horror palette; consonant/dissonant cast feedback; adaptive BPM incl. >160 boss tier; save-room-style calm zones; mode = sign of f; conditioning = learning loop.
- **Read so far:** Front matter ✅ · Ch.1–7 ✅

---

## v8

- ⚠️ **AUDIENCE:** ~20-year-old players, NOT kids. Full tension palette in scope. Original website details outside current context — don't invent peaktogether.me specifics; ask if needed.
- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale → BPM grid → envelopes; velocity ← magnitude. Timbre: T = β·g(x), slow & secondary. Ch.5: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude, threshold events, 3:4 polyrhythm. Emotion (Ch.7): valence → mode, arousal → tempo/dynamics; fear toolbox (20–150 Hz AM roughness, m2/tritone/m9, BPM bands 50–80/80–110/120–160/>160); BRECVEMA + GEMS. Scaling (Ch.8): 2–4 voices max, separate by register+timbre; chunk-and-summarize big data; PCA/clustering for high-dim; 3-layer soundscape (trend line / event motifs / stats-drone); per-voice mute; real-time = low-latency buffers + preprocessing; users need layered training. Architecture: Program A (compile) / B (play).
- **Project:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: spell compiler → JSON → sample player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat melody → +timbre/rhythm → co-op 3:4 polyrhythm (per-voice mute/solo mechanic) → dark/boss tier (horror palette, >160 BPM) → multi-voice spells (f + f′ counterpoint); consonant/dissonant cast feedback; calm study zones; mode = sign of f; level ambience = 3-layer soundscape; tier progression = the "user training" the book calls for.
- **Read so far:** Front matter ✅ · Ch.1–8 ✅

---

## v9

- ⚠️ **AUDIENCE:** ~20-year-old players, NOT kids. Full tension palette in scope. Original website details outside current context — don't invent peaktogether.me specifics; ask Nir.
- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale → BPM grid → envelopes; velocity ← magnitude. Timbre: T = β·g(x), slow/secondary; slope→timbre endorsed (Ch.9 brachistochrone). Ch.5: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude, threshold events, 3:4 polyrhythm. Emotion (Ch.7): valence → mode, arousal → tempo/dynamics; fear toolbox (20–150 Hz AM, m2/tritone/m9, BPM bands 50–80/80–110/120–160/>160); BRECVEMA+GEMS. Scaling (Ch.8): ≤4 voices, register+timbre separation; chunking; PCA; 3-layer soundscape; per-voice mute. Cases (Ch.9): brachistochrone (time→triggers, y→pitch, slope→timbre; comparative listening); orbital resonances = polyrhythms from period ratios; climate/stocks = trend baseline + oscillations; sub-50 ms latency; Csound/Wwise/FMOD. Architecture: Program A (compile) / B (play).
- **Project:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: spell compiler → JSON → sample player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat melody → +timbre/rhythm → co-op polyrhythm (= orbital-resonance boss 🌌, per-voice solo/mute) → dark tier (>160 BPM horror palette) → multi-voice f+f′ counterpoint. New from Ch.9: brachistochrone race-by-ear level; comparative-listening quiz mode (x² vs e^x); Web Audio suffices (<50 ms); meditative study-zone soundscape; parked idea: user-CSV sonification sandbox.
- **Read so far:** Front matter ✅ · Ch.1–9 ✅

---

## v10 (book complete)

- ⚠️ **AUDIENCE:** ~20-year-old players, NOT kids. Full tension palette in scope. Original website details outside current context — don't invent peaktogether.me specifics; ask Nir.
- **Book: Sounding the Unknown** (COMPLETE, Ch.1–10; code appendices pending?). HSS core: helix x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f; 12-TET (microtonal 19/24-TET flagged as future). Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale → BPM grid → envelopes; velocity ← magnitude; timbre T = β·g(x) (slope→timbre endorsed). Ch.5 ref: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm: duration ← magnitude, threshold events, 3:4 polyrhythm. Emotion: valence → mode, arousal → tempo/dynamics; fear toolbox (20–150 Hz AM, m2/tritone/m9, BPM 50–80/80–110/120–160/>160); BRECVEMA+GEMS; cultural caveats. Scaling: ≤4 voices (register+timbre separation), chunking, PCA, 3-layer soundscape, per-voice mute, sub-50 ms. Ch.9 cases: brachistochrone (comparative listening), orbital-resonance polyrhythms, trend+oscillation for time-series. Ch.10: adaptive escalation (missed anomaly→more dissonance), spatial stream placement, accessibility/STEAM angle. Architecture: Program A (compile) / B (play).
- **Project:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: spell compiler → JSON → Web Audio sample player (<50 ms fine); spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat melody → +timbre/rhythm → co-op 3:4 polyrhythm (orbital-resonance boss, stereo-panned voices, solo/mute) → dark tier (>160 BPM, horror palette, microtonal detuning) → f+f′ counterpoint. Features: consonant/dissonant cast feedback; adaptive-escalation hint system; brachistochrone race-by-ear level; comparative quiz mode; calm study zones; mode = sign of f; helix as signature on-screen visual 🌀; eyes-free playable (accessibility selling point). Parked: user-CSV sandbox.
- **Read so far:** Front matter ✅ · Ch.1–10 ✅ (book complete)
