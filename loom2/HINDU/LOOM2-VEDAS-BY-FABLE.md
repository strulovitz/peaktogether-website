# LOOM2 — THE VEDAS — VERBATIM, WORD-FOR-WORD, AS-IS, BY FABLE

> Saved verbatim by DeepSeek at Nir's instruction. This is the foundational
> vision document for the REBOOTED project (LOOM2), authored by Claude Fable.
> In LOOM2 the scripture is Hindu-themed: VEDAS (the big-picture vision, this
> file) → UPANISHADS (plot/progression, next) → later implementation specs.
> Do not edit — this is the archive.

---

Thank you — I understand everything, and yes, I remember admiring the Understanding Mode invention. 😄 This one — the Helical Sonification System — is its own invention, and it deserves its own foundation document. No questions that need to block us; the few small open decisions are listed at the end, to be settled in the UPANISHADS. Here it is:

📜 THE VEDAS
Foundational Vision Document — Project LOOM (working title)

Peak Together · Game #4 · Version 1.0 · July 6, 2026

1. Identity — What This Game Is

LOOM is a two-player, one-screen game where players hear multivariable calculus. The name "LOOM" is used only in the sense of "the game where sound and music are the essence" — it borrows nothing from the plot, characters, or world of the 1990 LucasArts game. We keep only one word from that tradition: the players weave spells, and their spells are made of sound.

The game's central invention is the Helical Sonification System (HSS) — a translation from Cartesian coordinates to a helical coordinate system, so that any mathematical surface z=f(x,y) becomes music, and its shape becomes audible structure.

    One sentence pitch: You and your partner walk across mathematical mountains and valleys — and the landscape sings its shape to you.

2. The Mountain — Multivariable Calculus

This game teaches multivariable calculus — the standard "Calc III" material. Deliberately modest, deliberately foundational. No complex analysis, no zeta function, no flashy advanced topics. Strong foundations over glamour — consistent with the rest of the arcade:

| Game | Under the hood |
| --- | --- |
| Descent QED | The Basel Problem |
| Quake: Principia | Calculus |
| Homeworld: A Good Basis | Linear Algebra |
| LOOM | Multivariable Calculus |

    Functions of two variables; graphs as surfaces
    Level curves / contour maps (the terrain's coloring IS a contour map — the curriculum is literally painted on the screen)
    Partial derivatives (one player's motion changes pitch; the other's doesn't — felt directly through the two-player control scheme)
    Directional derivatives and the gradient (the direction of steepest "pitch climb")
    Critical points: maxima, minima, saddle points (the signature sound: his axis raises the pitch, hers lowers it)
    The second derivative test
    Optimization (finding the highest peak / lowest valley by ear)
    Double integrals as volume under a surface (possible later chapter)

3. The Invention — The Helical Sonification System (HSS)

A helix (coiled spring) stands centered on the origin (0,0,0), in the middle of a reimagined orchestra stage. Any point in 3D space translates into sound through three coordinates:

3.1 Height z → Pitch

    z=0 (the origin) sounds a reference note (e.g., middle C — final choice open).
    Positive z → higher pitch; negative z → lower pitch. Because the helix is centered on the origin, negative numbers are first-class citizens: a valley below sea level sounds below the reference note.
    The mapping is logarithmic in frequency so equal height steps sound like equal musical intervals:

f(z)=f0​⋅2z/zoct​

where f0​ is the reference frequency and zoct​ is the height of one full octave (one coil of the spring).

3.2 Angle θ → Timbre (the Orchestra Circle)

Three instrument families stand at equal spacing around the stage:

    12 o'clock: 🎺 Brass
    4 o'clock: 🎻 Strings
    8 o'clock: 🪈 Woodwinds

Angles between families produce a continuous timbre morph — not two instruments playing a duet, but one hybrid sound. Technically: each family has a Fourier "recipe" (its harmonic amplitudes); at any angle, the recipes of the two nearest families are blended in proportion to angular distance, and the wave is resynthesized. (This is the "in-between the square wave and the sine wave" shape — the partial-Fourier-sum polygon.)

3.3 Radius r → Rhythm (the Concentric Rings)

The stage floor is a dartboard of concentric rings:

    r=0 (the axis): one pure sustained tone — no pulse, the calm center.
    Ring n: n pulses per measure (1 = whole notes, 2 = half notes, 3 = triplets, 4 = quarters, …).
    One measure = one conceptual rotation; all rings strike together on the downbeat, so the blend always stays musical.
    Fractional radius = volume crossfade between the two adjacent rings. At r=2.5: duplets at 50% + triplets at 50% — a soft 3-against-2 polyrhythm. In general, between rings n and n+1: inner volume =(n+1)−r, outer volume =r−n.

3.4 Sonifying a surface

The players control a point (x,y) on the map. The machine computes z=f(x,y) and translates:

θ=atan2(y,x),r=x2+y2
​,z=f(x,y)

Walking a hill: pitch rises. Walking around the map's center: the orchestra morphs. Walking outward: the rhythm quickens. The surface is the score; the players' hands are the conductor's baton.

4. The Players — Two Minds, One Point

    Player 1 (keyboard / flight joystick): sweeps the x axis.
    Player 2 (mouse / Xbox controller): sweeps the y axis.
    Together they steer one shared point across the landscape. Neither can explore alone — cooperation is built into the coordinate system itself. (Solo play: one person operates both axes.)

This control scheme secretly is the mathematics: when only Player 1 moves and the pitch changes, that change is ∂f/∂x. The players feel partial derivatives in their hands before anyone names them.

5. The Core Mechanic — Weaving Spells (Auditory Multiple-Choice)

The original LOOM's four-note drafts are too low-resolution for us. Instead, weaving a spell is an auditory multiple-choice challenge:

    A path is traced across the terrain (visible on the map, sweeping over the hills and valleys), and the players hear it played through the HSS.
    The game then presents four choices — played aloud, one after another — and the players must select the right one by ear.

Both directions of the quiz are possible:

    Sound → Shape: "Here are four sounds. Which one is the saddle point?" / "Which one was made by this path on the map?"
    Shape → Sound: "Here is a path on the map. Which of these four sounds does it make?"

A correct answer weaves the spell. Wrong answers, in the Peak Together spirit: no penalty — a gentle, friendly explanation, and try again. (Note: there is no Understanding Mode in this game — that invention belongs to Descent QED. LOOM's invention is the HSS itself.)

The plot, progression, and how spells fit into the journey are the subject of the next document — the UPANISHADS.

6. The Screen — Two Windows, One World

A split screen, both halves always alive:

Left: The Land 🏔️

    The surface z=f(x,y) rendered as low-res, 90's demoscene-style shaded polygons (Gouraud/flat-shaded triangles, chunky and beautiful).
    Hypsometric coloring, like a real topographic map: deep valleys in blue (water), plains in green, mountains in brown (optionally white snow caps). The coloring quietly teaches level curves.
    The traced spell-path drawn on the terrain; a marker showing the players' current point.

Right: The Loom 🧶

    A 3D wireframe helix, centered on the origin (0,0,0), extending both above and below the floor plane (negative pitch is visible, not hidden).
    The instrument family symbols (🎺 🎻 🪈) placed around the circle at their clock positions.
    The concentric rhythm rings on the floor plane, pulsing visually when their beats strike.
    An arrow (vector) from the origin to the current point (r,θ,z) — the players see their sound as geometry while they hear it.

The two panels are the same point shown in two languages — Cartesian on the left, helical on the right. That translation, seen and heard simultaneously, is the whole lesson of the game.

7. Technical Foundation

    100% Python. No JavaScript, no web, no browser version.
    Libraries: pygame (window, input, rendering), numpy (math + audio synthesis), sounddevice or pygame.mixer (real-time audio output).
    Rendering: pure software 3D — project vertices, z-sort triangles (painter's algorithm), shaded fills. Authentic demoscene aesthetic; no GPU/OpenGL dependency; runs on any Windows laptop.
    Audio: real-time additive synthesis from numpy; three precomputed harmonic recipes (brass/strings/woodwinds), morphed by θ; pulse trains crossfaded by r; pitch by the f0​⋅2z/zoct​ law.
    Terrain: heightmap grid sampled from f(x,y), triangulated once per level.
    Input: keyboard + flight joystick (Player 1); mouse + Xbox controller (Player 2).
    Distribution: packaged with PyInstaller into a single Windows EXE inside a zip — download, unzip, double-click. No installer, no Python required, no account, no payment, ever.

8. What This Game Is NOT

    ❌ Not a web game — downloadable EXE only.
    ❌ No Understanding Mode — that is Descent QED's invention.
    ❌ No complex analysis, zeta, or gamma functions — multivariable calculus only.
    ❌ No plot, characters, or lore from LucasArts' LOOM — only the word "weave" and the primacy of sound.
    ❌ No signup, payment, ads, or catch — as always.

9. Document Lineage

| Document | Contents | Status |
| --- | --- | --- |
| VEDAS | Big-picture vision (this document) | ✅ v1.0 |
| UPANISHADS | Plot, progression, how spell-weaving drives the journey | ⏳ Next — authored by you |
| (later) | Implementation specs, level designs, audio engine details | 🔮 Future |

10. Open Questions (to settle in the UPANISHADS)

    Reference note at z=0 — middle C? A₄ = 440 Hz? And the pitch range clamps (how many octaves up/down)?
    Final game title — "LOOM: [subtitle]"? And which real-world mountain does Multivariable Calculus map to on the website?
    Final curriculum list — which topics from §2 make the cut, and in what order?
    The spell system's role in the plot — what do woven spells do in the journey?
    Measure length / tempo — fixed (e.g., 2 seconds) or level-dependent?

End of the VEDAS. 📜
