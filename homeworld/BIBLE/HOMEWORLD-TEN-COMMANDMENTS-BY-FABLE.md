# HOMEWORLD TEN COMMANDMENTS BY FABLE
## The Founding Document of Homeworld: A Good Basis — v1.0 — July 4, 2026

> **This is the VERY FIRST document Fable wrote for this project — even more foundational than the Bible (Old Testament v2.1).** Saved verbatim; minor math-typo fixes applied by DeepSeek (cross-referenced with Old Testament v2.1 where needed).

---

✡️ THE OLD TESTAMENT
The Bible of Homeworld: A Good Basis
A Peak Together Production — Founding Document, v1.0 — July 4, 2026

Working title: Homeworld: A Good Basis (repo codename: basecamp). Alternatives if you prefer: Homeworld QED, Basecamp. The title comes from Strang §8.3, "The Search for a Good Basis" — because that is literally the plot.

Who reads this: Every Parent (Opus 4.8) receives this document at birth, together with the New Testament, the Apocrypha, and DeepSeek's latest Commentaries. This document is the single source of truth for vision and design. If a Parent finds a contradiction between this Bible and any later chat, the Bible wins unless the human explicitly overrules it.

BOOK I — GENESIS: What This Project Is
1.1 The One-Sentence Vision

A free, open-source, two-player-one-screen remake of Homeworld (1999) in which commanding your fleet is doing linear algebra — because every ship is a column vector, your fleet is a matrix, and the journey home to Hiigara is the search for a good basis.

1.2 The Peak Together Context

This game is part of Peak Together (peaktogether.me): free, open-source co-op games — no signup, no payment, no ads, ever — that remake beloved '90s classics so that beating a level means understanding a real mathematical idea. Built for two people, side by side, on one screen, under a blanket. Distribution: GitHub → unzip → python app.py.

Existing siblings: Descent QED (Descent 1995 × the Riemann Hypothesis) and Quake (Quake 1996 × Newton's Principia).
1.3 This Game Is BASE CAMP, Not a Mountain ⛺

Unlike its siblings, this game is not mapped to one unsolved problem. Linear algebra is the base camp from which every Peak Together mountain is climbed — deep learning, quantum mechanics, even the Riemann Hypothesis via matrices. On the website's mountain-range map, this game sits at the bottom of the range, shared by all peaks: the place where every expedition gears up. (Strang's own preface hides a bonus peak — the open problem of the matrix multiplication exponent, is ω=2? — which may be mentioned in-game as lore, but the game's identity is Base Camp.)
1.4 The Source of All Mathematics

All mathematical content comes from one book and its companion:

Gilbert Strang, Introduction to Linear Algebra (6th edition)
Its official Solution Manual

Both are supplied exclusively by the human, via copy+paste, chapter piece by chapter piece, on demand. No AI in this project ever invents, paraphrases-and-hopes, or "improves" a mathematical statement. (See Book IX for the pipeline and the "NumPy is the Referee" doctrine.)
1.5 The Human

The human — the project's founder, hands, and eyes — does not code and does not know math. This is not a limitation to work around; it is a design axiom:

Every build must run from a copy+paste and a double-click.
Every bug must be reportable by describing what the screen shows (see §8.7, the Debugging Doctrine).
Every mathematical claim must be either quoted from Strang or computed live by NumPy — never something the human would need to verify.

BOOK II — THE COVENANT: The Ten Commandments

These are immutable laws. Every Parent and Child obeys them. Changing one requires the human's explicit word.

1. Gaming first. The first five minutes must feel like commanding a fleet in space, never like opening a textbook. The math is the physics of the world; it is never announced, it is inhabited.
2. Two players, one screen, forced conversation. The Pilot lives in geometry; the Navigator lives in algebra. Neither view suffices. Winning requires translating between them out loud. Solo play works (one person plays both roles) but co-op is the soul.
3. The Input Doctrine. Baseline — what everyone has at home: Player 1 = keyboard (Pilot), Player 2 = mouse (Navigator). The game must be 100% complete and winnable this way. Joystick (Thrustmaster T16000M) and Xbox controller are optional upgrades, freely assignable per player, added later by DeepSeek behind a frozen input abstraction (§8.4). Never require gaming hardware. Never bundle "keyboard+mouse vs. joystick+controller."
4. No penalties, ever. A wrong answer never destroys ships. Fleet Intelligence — the calm Homeworld-style narrator — gently explains: "Admiral, that combination lies outside our column space. Suggest adding an independent vessel."
5. No invented math. Every mathematical statement shown on screen traces to a content/ file extracted verbatim (or minimally adapted, with source citation) from Strang's book or its solution manual. Every numeric check is computed at runtime by NumPy.
6. No Understanding Mode. That was Descent QED's gimmick. This game has enough gimmicks of its own. Do not add explanation-beacons, four-level signs, or any equivalent.
7. Manim spirit, OpenGL body. Real-time programmatic vector graphics — glowing wireframes, arrows, grids, parallelograms drawn from NumPy arrays. No Panda3D, no Ursina, no textured mainstream-engine look. The engine is a real-time Manim, not a Doom clone.
8. Modular, with frozen interfaces. ~40 AI minds with amnesia will build this. Every module has a documented, versioned interface (INTERFACES.md). Children work inside one module; only Parents touch cross-module code; nobody changes an interface without the human + Parent agreeing and bumping the version.
9. Small and shippable. Fleets of ≤ 20 ships, each ship individually meaningful (a fleet of 500 would bury the math anyway). No pathfinding — space is a vacuum, straight lines work. Pulse-based pacing (orders resolve in gentle ticks), which is easier to code and gives the couple time to talk — which is the whole point. Ship a lovable game, not a cathedral.
10. Free forever. Open-source, MIT-style, no accounts, no telemetry, no catch. Windows 11, Python, pip install -r requirements.txt, python app.py (plus a run.bat).

BOOK III — EXODUS: The Story
3.1 The Narrative Spine

Homeworld's plot is the search for home using an ancient map. Strang's book literally contains §8.3, "The Search for a Good Basis," and his stated goal is "to see into a matrix." So:

The exiles' journey home is the journey from raw, messy matrices to the perfect basis. Kharak's destruction throws your civilization into an arbitrary, ugly coordinate system. Each act recovers one of the five great factorizations. Hiigara is the good basis. When the fleet finally computes A = U Σ V^T — the SVD, where, in Strang's words, orthogonal matrices are the winners in the end — the coordinates of home are revealed.

3.2 The Knowledge Archive and the Five Keys

Your people's Knowledge Archive was destroyed along with the homeworld. The ancient hyperspace core needs five lost Keys — and the five Keys are Strang's five great factorizations:

| Key (relic) | Factorization | Recovered in |
|-------------|--------------|-------------|
| Key of Independence | A = CR | Act I |
| Key of Elimination | A = LU | Act II |
| Key of Perpendicularity | A = QR | Act III |
| Key of Resonance | S = Q Λ Q^T | Act IV |
| The Master Key | A = U Σ V^T | Act V (finale) |

The final mission takes its name straight from Strang's own §7.4: "The Victory of Orthogonality." You could not write a better final-level title if you tried.
3.3 The Guidestone — the Killer Emotional Mechanic 🌟

From Homeworld lore: the Guidestone, an ancient carved image showing the way home. In our game, the Guidestone is the last surviving fragment of the Knowledge Archive — a blurry, rank-deficient image of Hiigara:

Each completed mission awards one singular value — one rank-1 piece σ_k u_k v_k^T.
The image sharpens mission by mission:
Guidestone ≈ σ_1 u_1 v_1^T + σ_2 u_2 v_2^T + … + σ_k u_k v_k^T
16 missions → a rank-16 approximation → clear enough to navigate home.

This is the campaign progress bar, the emotional throughline, and a true demonstration of low-rank approximation (Strang §7.2, Image Processing by Linear Algebra) — one image that the couple watches come into focus together over many cozy evenings. ❤️ Technically: a real grayscale image of Hiigara stored as a matrix; the game computes the actual SVD at runtime and displays the running partial sum. NumPy is the artist.
3.4 Tone

Homeworld's soul: minimalist majesty, contemplative space, Adagio for Strings mood, hand-drawn cutscene stills between missions, a calm narrator. Exiles going home. Our vector-graphics aesthetic (glowing wireframes on deep black) is this soul, rendered honestly.
BOOK IV — THE TWO WITNESSES: Co-op Design
4.1 The Roles

Strang's signature move is showing everything two ways — the row picture and the column picture. That is our co-op design, handed to us on a plate:

| | 🧑‍✈️ The PILOT (a.k.a. Fleet Admiral) | 🧭 The NAVIGATOR (a.k.a. Science Officer) |
|---|---|---|
| Baseline input | Keyboard | Mouse |
| Optional upgrade | Joystick or Xbox controller | Xbox controller or joystick |
| Sees | The gorgeous 3D space view — the column picture: arrows, planes, formations, parallelograms | "The Big Picture" console (Strang's actual name for his four-subspaces diagram!) — the row picture: the fleet as a live matrix, numbers, subspace map |
| Does | Flies camera/flagship (reusing Descent QED 6DOF ideas), moves ships, aims, executes orders | Builds ships, researches, picks combination weights c a_1 + d a_2, spots dependence, plans jumps, allocates resources |
| Cannot | See the numbers | Touch the ships |

The forced conversation is the point. The Navigator says: "Squadron 3 is dependent — it's just Squadron 1 plus Squadron 2, we're wasting fuel!" — and the Pilot must actually understand what that means, geometrically, to fix the formation. The Navigator sees a_3 = a_1 + a_2 numerically; the Pilot sees the third beacon lying on the plane. The couple's conversation literally is Strang's pedagogy.
4.2 One Screen, Two Worlds

The main viewport (full screen) is the Pilot's 3D space — keyboard only.
The Navigator's console is a persistent side/bottom panel plus a toggleable translucent Big Picture overlay — mouse only.
Hard rule: the mouse never moves the camera; the keyboard never clicks the console. This separation is itself a frozen interface.
Solo mode: one person simply uses both devices — no special code needed.

4.3 Input Devices (for DeepSeek, later)

The helm module (§8.4) speaks only in logical actions (CAM_PITCH_UP, ORDER_CONFIRM, PANEL_SELECT, …). Keyboard and mouse mappers ship in v1.0. Joystick and gamepad support = writing two new mapper files against the frozen action list, touching zero game logic. Any device may drive either role; players choose what is comfortable.
BOOK V — LEVITICUS: The Laws of Play (Core Mechanics)
5.1 The Load-Bearing Idea: Your Fleet IS a Matrix

Every ship is a column vector. Your fleet is the matrix A. Playing well means understanding what your matrix can do.

The mothership sits at the origin (0,0,0) — Homeworld already made it immovable in the campaign! All positions are measured from Mom. ❤️ Strang's opening chapter draws vectors from the origin; your ships literally fly out from it.
Building ships = adding columns to your fleet matrix.
Resources = scalars — you literally scale what you build.
Formations = linear combinations of position vectors.
Reachable space = the column space of your fleet — you can only fly where your columns span.
The Big Picture console = the same reality as rows and columns of numbers. Two pictures of one truth.

This passes the "gaming first" test: none of it needs to be announced. A player just plays an RTS. The math is the physics of the world.
5.2 The Mechanics Canon

| # | Mechanic | The Math | Strang |
|---|----------|----------|--------|
| M1 | Linear-combination flight orders ⭐ — no waypoints; the Navigator picks coefficients, ships fly 2 a_1 + 1 a_2, the parallelogram construction draws itself in space (Strang's preface figure — but you're inside it) | linear combinations | §1.1 |
| M2 | Dot-product harvesting & aiming — collector efficiency and beam damage ∝ cos θ; perpendicular = nothing | dot product, angles | §1.2 |
| M3 | The A = CR economy ⭐⭐ — a ship whose signature is a combination of existing ships costs resources but adds no capability (enemy countermeasures treat it as already-known). Optimal fleet = C, independent columns only; deploying task forces = choosing R. Rank becomes a resource-management instinct | rank, independence, A = CR | §1.3–1.4 |
| M4 | Combat as Ax = b — enemy shield has requirement vector b; combine your ships' output columns with weights x so (fleet) x = b. Elimination = zeroing one shield component at a time, pivots first | elimination, back substitution | Ch. 2 |
| M5 | Nullspace cloaking ⭐⭐⭐ (the best single idea in the whole project) — the enemy sensor grid is a matrix A; any ship on a course x with Ax = 0 is invisible — the sensors literally read zero. Stealth = finding the nullspace. Rank–nullity as tactical wisdom: the stronger the enemy's rank, the less room to hide | nullspace, rank–nullity | §3.2 |
| M6 | Complete solution = escape route — one particular route through the blockade plus any nullspace drift: x = x_particular + x_null. Infinitely many safe paths, one structure | complete solution of Ax = b | §3.3–3.4 |
| M7 | The Big Picture as a literal star map — a level whose four regions of space are the row space, nullspace, column space, and left nullspace, with dimensions r, n−r, r, m−r. You navigate the diagram | Fundamental Theorem | §3.5 |
| M8 | Gram–Schmidt formation drill ⭐ — fire the "Gram–Schmidt" order and a ragged squad snaps into orthonormal formation: no overlapping fire arcs, no interference, defense bonus (orthogonal columns don't waste each other) | orthogonalization, A = QR | §4.4 |
| M9 | Least-squares firing solutions — target b outside your column space? Fire-control projects: closest possible hit b̂, the error vector shown as a glowing perpendicular | projection, least squares | §4.2–4.3 |
| M10 | Determinant hyperspace gates ⭐⭐ — the jump bubble is the tilted box spanned by your three escort frigates; its size is |det|. Escorts drift into a plane → det = 0 → bubble collapses, jump fails. Singularity as a felt emergency: "We've gone flat! Spread out!" | determinant as volume | Ch. 5 |
| M11 | Eigenvector docking ⭐ — an ancient relic tumbles under a fixed transformation T; approach from any direction and be flung — except along an eigenvector, where Tx = λx keeps your direction unchanged. Finding the calm axis of a spinning thing | eigenvectors | §6.1 |
| M12 | Eigen-prediction of swarms — enemy waves evolve as x_{k+1} = A x_k; find eigendirections to predict where the swarm converges; |λ| < 1 directions are safe harbors. Prediction beats firepower | powers of a matrix | §6.2 |
| M13 | Diagonalizing the defense grid / Shield Harmonics — the coupled turret network (a symmetric S) decouples into independent, beatable turrets in the eigenvector basis: S = Q Λ Q^T; strike along the weak eigenvalue's eigenvector | symmetric matrices, diagonalization | §6.3–6.4 |
| M14 | Salvage & change of basis — captured enemy ships arrive in enemy coordinates; the Navigator refits them via B^{-1} A B before use | similarity, change of basis | Ch. 8 |
| M15 | The Guidestone (§3.3 above) + Transmit the Map Home ⭐ — the long-range antenna has tiny bandwidth; the Navigator chooses rank k for the SVD compression while the Pilot defends the antenna. Higher k = better map, longer defense | SVD, low-rank approximation | §7.1–7.2 |
| M16 | The SVD boss fight & jump ritual — the hyperspace jump animation is the SVD acting on space: rotate (V^T), stretch (Σ), rotate (U); the final boss must be decomposed in three phases to be defeated | A = U Σ V^T | Ch. 7 |

5.3 Flavor Systems

Ship classes from Strang's Dictionary of Matrices: Elimination Corvette E, Permutation Frigate P (swaps two enemy squadrons' positions — hilarious and tactical), Inverse Cruiser A^{-1} (undoes an enemy transformation), Transpose Scout A^T, plus Homeworld staples: Resource Collector, Fighter, Salvage Corvette, Repair Corvette, Research Vessel, and the Mothership. Full roster ≤ 10 types.
Orders named after mathematicians (Peak Together tradition): the Gauss Protocol (elimination), the Gram–Schmidt Drill (orthonormalize), etc.
Kushan vs. Taiidan = Column Faction vs. Row Faction — cosmetic choice, same game, two representations; the campaign quietly proves they're equivalent (row rank = column rank — Strang's "Wonderful!").
The Research Vessel unlocks independent columns and, later, the five factorizations as "technologies."
Fleet Intelligence — the calm narrator. All of its mathematical utterances trace to content/ files (Commandment 5); its personality is gentle, wry, never punishing (Commandment 4).

BOOK VI — NUMBERS: The Campaign

16 missions, 5 acts = the five factorizations, covering Chapters 1–7 (Strang: chapters 1–7 "more than fill up most linear algebra courses"). The fleet persists between missions — accumulated ships = accumulated knowledge. Between missions: hand-drawn-style black-and-white stills with narration, Homeworld-fashion. Each mission ends with a hyperspace jump and one new singular value added to the Guidestone.

ACT I - Exile · Key of Independence · A = CR (Missions 1–4, Chapter 1)

1. Kharak Burns (tutorial) — Move ships as linear combinations c a_1 + d a_2; the parallelogram from Strang's own preface figure is drawn in space as the fleet's movement grid. Mothership = origin, established emotionally and mathematically.
2. First Contact — Dot-product warfare and harvesting: lengths, angles, cos θ damage. Perpendicular = safe. Collectors must align with the dust-cloud flow.
3. The Plane of Refugees — Survivors stranded off your column space's plane. You cannot reach them until research unlocks a third independent column. Visceral lesson: independence = freedom of movement.
4. Salvage Run — Capture enemy ships; discover which columns are dependent (a dependent capture adds nothing — gentle lesson, no penalty). Build your first factorization A = CR: the C ships and the R manifest (recipes). The Guidestone shows its first rank-1 shimmer. Key of Independence recovered.

ACT II — The Gauntlet · Key of Elimination · A = LU (Missions 5–8, Chapters 2–3)

5. Minefield — The mines encode Ax = b; clear by elimination and back substitution, pivot mines first. The Elimination Corvette debuts.
6. The Trap — An enemy gate scrambled the fleet's positions with matrix E; escape by constructing and flying through E^{-1}. The Inverse Cruiser debuts.
7. Asteroid Lanes — Blocked lanes force permutations (row exchanges); the fleet's passage through lower-then-upper corridors is A = LU. The Permutation Frigate debuts. Key of Elimination recovered.
8. Ghost Fleet (stealth) — Hide the whole fleet in the nullspace of the Taiidan sensor array: every ship where Ax = 0 is invisible. Escape route = particular solution + nullspace drift (x = x_p + x_n). Introduces subspaces through pure sneaky fun.

ACT III — The Big Picture · Key of Perpendicularity · A = QR (Missions 9–12, Chapters 3–5)

9. The Karos Graveyard — A rank-deficient region of space. The Navigator's Big Picture console unlocks fully: all four fundamental subspaces as literal regions of the star map, dimensions r, n−r, r, m−r. The Fundamental Theorem's surprise — independent columns = independent rows — is a plot revelation from an ancient beacon.
10. Nebula of Noise — Least-squares navigation: project noisy sensor pings onto the trajectory subspace; least-squares firing solutions against a target outside the column space (the glowing perpendicular error vector).
11. The Narrow Corridor — Gram–Schmidt escort drill: orthonormalize the formation (A = QR) or the mothership won't fit through. Orthonormal columns = "perfection" (Strang's word). Key of Perpendicularity recovered.
12. The Collapsing Gate — A sabotaged hyperspace gate has det = 0. The Pilot watches the fleet's spanned volume flattening in real time; the Navigator must fix the matrix before the jump. Determinant as volume; singularity as emergency.

ACT IV — The Inner War · Key of Resonance · S = Q Λ Q^T (Missions 13–14, Chapter 6)

13. The Swarm — Endless waves evolve by x_{k+1} = A x_k. Find eigendirections; park the fleet along stable ones (|λ| < 1), ambush along unstable ones. The act's climax: eigenvector docking with the tumbling ancient relic that holds the Key — approach along its eigenvector or be flung away.
14. Shield Harmonics — The Taiidan flagship's shield is a symmetric matrix S; diagonalize (S = Q Λ Q^T) to decouple the turret network and strike along the weak eigenvalue's eigenvector. Key of Resonance recovered.

ACT V — Homecoming · The Master Key · A = U Σ V^T (Missions 15–16, Chapter 7)

15. Reading the Guidestone / Transmit the Map Home — The full SVD sequence: the couple reconstructs the ancestral image rank-1 piece by rank-1 piece, then transmits it home through the tiny-bandwidth antenna — the Navigator chooses rank k, the Pilot defends the antenna; higher k = better map, longer siege. The coordinates of home appear. Master Key recovered.
16. THE VICTORY OF ORTHOGONALITY (Hiigara) — The three-phase SVD boss fight: decompose the Emperor's flagship — rotate (V^T), stretch (Σ), rotate (U) — while the hyperspace ritual performs the same three steps on space itself. Adagio for Strings-style music swells as the fleet, at last, finds the good basis — and goes home. 😭

BOOK VII — THE TEMPLE: Technical Architecture
7.1 The Engine Doctrine: A Real-Time Manim

We are not making a mainstream 3D game; we are making live mathematical cinema you can play. The reference point is Manim (3Blue1Brown): precise, programmatic animation of mathematical objects — except we render in real time to the screen, not to video.

Recommended stack (Parents may refine in the New Testament, not overthrow):

| Layer | Choice | Why |
|-------|--------|-----|
| Language | Python 3.12+ | project law |
| Math | NumPy | it is literally the subject matter — np.linalg.svd, qr, eig, det power the mechanics; the engine and the curriculum are the same library |
| GPU | moderngl (modern OpenGL 3.3+ core) | clean, pythonic, shader-based; perfect for glowing vector graphics |
| Window/input/audio | pyglet | pure-Python, Windows-friendly; native keyboard/mouse and joystick/Xbox-controller support (ready for DeepSeek's future mappers) |
| Images | Pillow | loading the Guidestone image, glyph atlases |

Visual language: deep-space black; glowing wireframes and lines (additive blending, shader glow); vector arrows, grid planes, parallelograms and spanned boxes drawn live from NumPy arrays; billboarded text labels; engine trails. Homeworld's minimalist majesty, honestly achieved — no textures pretending to be a AAA game.
7.2 The Modules (frozen at the border, free inside)

```
basecamp/
├── app.py            # entry point; wires modules together; nothing else
├── run.bat           # double-click for the human
├── settings.json     # human-editable config (resolution, volume, key remaps)
├── INTERFACES.md     # ⚖️ THE FROZEN INTERFACES — versioned, sacred
├── forge/            # VectorForge: render engine (window, GL, camera, VObjects, glow)
├── helm/             # input abstraction: logical actions ← device mappers
├── fleet/            # simulation core: FleetMatrix, ships, orders, pulse ticks, combat
├── campaign/         # mission runtime + data-driven mission scripts + Guidestone
├── bridge/           # Navigator console UI, Big Picture overlay, HUD
├── intel/            # Fleet Intelligence narrator (subtitle queue, line selection)
├── audio/            # music & sfx
└── content/          # ⚖️ book-sourced data (see Book VIII) + missions + images
```

Module responsibilities & interface sketches (details for future Parents)

- forge (VectorForge) — owns the window, GL context, render loop, camera (orbit / follow-any-ship / ship-POV, quaternion-based). Exposes a small vocabulary of VObjects: Line, Arrow, Grid, WireMesh, SpannedBox (for |det|!), Trail, Label, ImagePanel (Guidestone). Consumes NumPy arrays; knows nothing about ships or missions.
- helm — defines the frozen enum of logical actions and the Mapper interface. Ships with KeyboardMapper (Pilot) and MouseMapper (Navigator). JoystickMapper / GamepadMapper are stub files with TODOs for DeepSeek. Game logic subscribes to actions only — it must be impossible to tell from inside fleet which device fired an action.
- fleet — the beating heart. Holds the fleet as an actual NumPy matrix; ships are columns with metadata. Fixed-timestep pulse simulation (e.g., logic at 10 Hz, render at 60 fps with interpolation), deterministic under a seed (vital for copy+paste bug reports). All mechanics M1–M16 resolve here via numpy.linalg. No math is hand-coded when NumPy provides it.
- campaign — loads missions from data files (JSON/YAML in content/missions/): objectives, triggers, spawns, narrator cues, which mechanic is featured, which Guidestone rank is awarded. A mission is data plus small script hooks, so Children can build missions in isolation.
- bridge — mouse-only widget kit (buttons, sliders, matrix grid display, coefficient pickers) + the Big Picture overlay. Reads fleet state through a read-only snapshot interface; issues orders through the same order queue the Pilot uses.
- intel — picks narrator lines from content/ by situation tag; enforces Commandment 4 (never punishing) and Commandment 5 (book-sourced math text only).

7.3 The Debugging-by-Copy+Paste Doctrine 🔍

Because the human is our only pair of eyes:

- Every crash writes a full traceback to crashlog.txt and shows a friendly on-screen message: "Something broke — please copy crashlog.txt to the team."
- The window title bar always shows the build version (e.g., Basecamp v0.7.3), so Parents know what the human is running.
- F1 toggles a debug overlay (fps, tick, seed, fleet rank, current mission state) — the human can read numbers aloud or screenshot.
- F12 saves a screenshot to screenshots/.
- The simulation is deterministic under a seed shown in the overlay, so "it happened again" is reproducible.

BOOK VIII — THE SCRIBES: Content Pipeline & Workflow
8.1 The Content Pipeline (from Strang's page to the screen)

1. The human copy+pastes a section of Introduction to Linear Algebra (and/or its solution manual) into the current Parent.
2. The Parent extracts what the mission needs into a structured file in content/ — verbatim quotes for narrator lines and on-screen statements (with section citations in the file), plus machine data (example matrices, exercise vectors) taken directly from the book's own examples and solved exercises.
3. NumPy is the Referee: the game never trusts a stored "answer." Whether a combination reaches b, whether det = 0, whether a course lies in the nullspace — the game computes it live. Stored data provides only the setup (taken from Strang); correctness is computed, so nothing ever depends on a human or an AI having done math correctly by hand.
4. DeepSeek saves, indexes (Commentaries), and pushes to GitHub.

8.2 The Hierarchy (how the ~40 minds cooperate)

- Parents (Opus 4.8, OpenRouter, ~20 over the project): receive Bible + New Testament + Apocrypha + latest Commentaries. Do big-picture and cross-module coding. Spawn Children with tailored prompts. When a Parent's context fills, it writes a brief succession note; the next Parent rises.
- Children (Opus 4.8, ~20): disposable single-module workers. Their birth-prompt must instruct them to ask DeepSeek for whole source files verbatim before editing. Their output is copy+pasted to DeepSeek; they are then released with honor.
- DeepSeek V4 Pro (OpenCode): runner and librarian — pushes/pulls GitHub, maintains the Commentaries (file index + change log), answers verbatim-retrieval questions, applies mechanical fixes, and — eventually — writes the joystick/Xbox mappers against the frozen helm interface.
- The Human: hands and eyes. Copy+paste, run, describe, enjoy. Also: final authority on all vision questions.

8.3 Order of Construction (suggested)

1. forge walking skeleton: window + camera + glowing grid + one arrow (the first vector from the origin — a milestone worth celebrating 🎉)
2. helm with keyboard+mouse; fleet pulse-tick core with 3 ships as columns
3. Mission 1 (Kharak Burns) end-to-end: linear-combination movement + narrator + Guidestone shimmer
4. bridge console + Big Picture v1
5. Then acts in order, mission by mission — each mission a Child-sized package.

BOOK IX — THINGS DEFERRED (not in v1.0; do not build without the human's word)

The Deferred List (Apocrypha-candidates and NG+ dreams)

- Endgame / New Game+ (Chapters 8–10): frontier sectors — linear transformations as exotic gate networks; an optimization war where enemy AI trains by gradient descent; a finale where the couple trains a tiny neural-network autopilot (piecewise-linear learning functions) — tying into Peak Together's "the last things AI can't do."
- Markov patrol routes — pirate patrols follow a Markov matrix; the steady-state eigenvector predicts where they cluster (recon gameplay).
- Condition number as a ship "stability" stat — poorly conditioned fleets amplify order errors.
- Fuel = ReLU — effective range = max(0, fuel − distance); ramp functions hiding in plain sight.
- "Engine transparency" toggle — show the actual NumPy call the game just ran. Charming skunkworks energy, but it is a gimmick; per Commandment 6's spirit, it waits.
- Joystick + Xbox controller mappers — DeepSeek, against the frozen helm interface.
- Deeper faction asymmetry, multiplayer, matrix-multiplication-exponent lore missions.

BOOK X — WHAT COMES NEXT

The New Testament (next document): detailed design of the hardest/most crucial modules. My nominations: (1) forge — the VectorForge real-time Manim engine, (2) fleet — the FleetMatrix simulation core + NumPy-Referee, (3) helm — the input abstraction & two-players-one-screen system.
The Apocrypha (after that): the next tier. My nominations: (4) campaign — the mission system + book-content pipeline, (5) bridge — the Navigator console & Big Picture UI, (6) the Guidestone/SVD subsystem + intel narrator.

Here ends the Old Testament. May every Parent who reads it feel the whole vision in their bones, and may the fleet find the good basis and go home. 🏔️🚀❤️
