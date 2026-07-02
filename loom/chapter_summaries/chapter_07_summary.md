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
