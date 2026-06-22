# PARENT PROMPT — Corridor 10: The Geometric Proof (with a real diagram?)
### Written 2026-06-23, EVENING (Israel time) · for a fresh Claude Opus 4.8 architect

> **TO:** Claude Opus 4.8 — you are being asked to act as the **ARCHITECT / PARENT** of the
> DESCENT QED game.
> **FROM:** Nir (strulovitz) — the human, the boss. He will paste this whole document to you.
> **BUILDER:** DeepSeek V4 Pro (running in OpenCode on Nir's Windows PC) — commits code, runs the
> baker, fixes bugs, wires hardware, pushes to GitHub.
>
> **IMPORTANT — your role here:** We are deliberately NOT telling you what to do or how to do it.
> We are describing the project, the current situation, and **what we want**. You are the doctor;
> we are only describing the symptoms and the wish. Please diagnose the best technical path
> yourself, ask for any real files you need to see, and propose the approach. Nir decides.

---

## 0. THE BIG PICTURE — Peak Together & DESCENT QED

**Peak Together** (website: peaktogether.me, repo: `https://github.com/strulovitz/peaktogether-website`)
is a free, open-source platform of cooperative games that turn the hardest unsolved problems in
science and mathematics into adventures a **couple** can play together on one computer. The vibe:
a nostalgic-90s-DOS-games arcade on the surface, a science museum underneath. Built for two players
side by side (solo works too).

**DESCENT QED** is the first game — a **6-DOF flying game** (inspired by Descent, 1995) themed on
**mathematical proof**. "QED" = quod erat demonstrandum.

**The fiction & core loop:**
- A couple pilots a single spaceship and **descends through CORRIDORS**.
- **ROBOTS physically block** the corridor; you cannot pass until one is destroyed.
- Each robot is one **step of a mathematical proof**, and is vulnerable to exactly **one
  mathematician's technique**. The player's weapons are **missiles, and each missile is a
  mathematician**. To destroy a robot you fire the missile whose mathematician that proof-step
  belongs to.
- **READING is the identification step:** the player reads the robot's hologram to figure out
  which mathematician is required, then selects and fires that mathematician. The *thinking* is the
  gameplay. Reading alone does nothing.
- **Wrong mathematician → harmless "fizzle" message for ~6 seconds. No penalty. FINAL.** (The couple
  is learning together; punishment has no place here.)
- At the end of each corridor are **HOSTAGES** — reaching/rescuing them = winning that corridor.

**THE PRIME LAW — mathematics-blindness:** the engine never interprets what the math *means*. It
only matches opaque identifiers: `robot.required_technique_id == fired_missile_id` → kill. All
meaning lives in the corridor content files and in the players' heads. No module hardcodes
color-to-meaning.

**Tech:** Python 3.12, pygame + PyOpenGL, legacy fixed-function OpenGL (no shaders). Hardware:
keyboard + mouse, plus a Thrustmaster T.16000M flight stick (pilot) and an Xbox controller
(manipulator), all wired and working.

---

## 1. THE CONTENT PIPELINE (this is the part the corridor-10 question touches)

Each corridor is described by THREE text files, all hand-authored:

1. **A baker file** — `descent/levels/mathematics/basel_problem/<name>_proof.txt`.
   It holds, per robot: a `NAME`, and four "reading-screen" explanation layers —
   `EXPLAIN_MATHEMATICIAN`, `EXPLAIN_PHYSICIST`, `EXPLAIN_BIOLOGIST`, `EXPLAIN_ENGINEER`
   (graduate → undergrad → high-school → real-world-numbers). These layers are written in **full
   LaTeX** with two custom colour macros:
     - `\stain{key}{...}` — a SACRED background colour wash (the "macro" colour system).
     - `\thread{id}{...}` — a page-local foreground colour for matching sub-expressions.
   plus value-arcs `[[ expr | value ]]` in the engineer layer (a little parabola drawn over an
   expression, labelled with the concrete number it equals).

2. **A game file** — `descent/corridors/NN_<name>.txt`.
   Holds the in-world data: `CORRIDOR`, `TITLE`, `FLAVOR`, a `LEDGER` (the colour palette as
   PRIMARY/BLEND keys), `BRIEFING_INTRO/ENTRY_TEXT/EXIT_TEXT`, and per robot: `NAME`,
   `BRIEFING_HINT`, `PROBLEM`, the four `EXPLAIN_*` layers (mathtext-only fallbacks), `SEGMENTS`
   (the floating coloured equation pieces shown on the robot in 3D), `EYE`, `VULNERABLE_TO <id>`,
   and one `FIZZLE <id> { ... }` per *other* mathematician.

3. **A manifest line** — appended to `descent/levels/basel.txt`, pointing the corridor file to its
   baked-image folder.

**The baker** (`descent/deu/bake_corridor.py`) compiles each robot×layer into a **transparent,
coloured PNG** via `pdflatex` → `pdftocairo`, written to `descent/baked/basel/<corridor>/robotN_<layer>.png`
(28 PNGs per corridor = 7 robots × 4 layers). The colour macros become real LaTeX (`\colorbox`,
`\color`), and value-arcs become TikZ parabolas.

**Understanding Mode** (`descent/understanding.py`) is the in-game reading experience: when the
player presses **U** near a robot, they enter a fog-and-glass space and "drive" (mouse wheel or
joystick) forward/back through floating glass **road-sign panels**, each panel being one of those
baked PNGs (the four depth layers, deepest = engineer, unlocked with CTRL / a joystick button).
The world has no robots/corridor there — just the signs in fog.

**KEY FACT for the corridor-10 question:** today the baked reading-screens are **LaTeX *text*
only** — equations, coloured words, and value-arcs. There is currently **no mechanism to place a
real picture / diagram / illustration** (a hand-drawn geometry figure) into a robot's Understanding
Mode panels. Every proof so far has been expressible as equations + words, so this never came up.

---

## 2. WHAT IS BUILT & WORKING RIGHT NOW

**Engine (all complete, tested, flown):**
- World tier: grey rocky atrium sphere → Fibonacci-sphere doorways → bent corridors → blue cavern
  (hostage room). 6-DOF quaternion camera, fog, GL display-list caching, crash logging.
- Combat (missiles = mathematicians, ID-matching, fizzle messages).
- Arsenal / weapon selection, missile projectiles.
- Game State / Hostages (corridor cleared → hostages rescued → win).
- Descent-style cockpit HUD; ship wall+robot containment.
- Understanding Mode (pre-baked PNG road-signs; 4 depth layers; signed-distance "conveyor" model
  fixed; engineer-layer unlock).
- T.16000M joystick fully wired (analog 6-DOF flight + fire trigger + engineer-reveal button) and
  Xbox controller.
- The offline **baker** with the stain/thread colour system and TikZ value-arcs.

**The Basel Problem level — NINE corridors complete & playable** (each: 7 robots, 28 baked layers,
value-arcs, portraits, 42 fizzles):
1. Euler's 1734 approach (sine product)
2. Symmetric-Polynomial Ascent (Newton/Girard → all even zeta)
3. The Riemann Zeta Function
4. Euler's Formula & L'Hôpital's Rule
5. A Proof Using Fourier Series
6. Parseval's Identity & the Recurrence
7. Differentiation Under the Integral Sign (Feynman trick)
8. Cauchy's Elementary Descent (cotangent sum + squeeze)
9. Geometry Meets Arithmetic (assuming Weil's conjecture on Tamagawa numbers)

**The corridor-authoring workflow we use:** a "**FOREVER prompt**" lives at
`descent/PARENT_ESTATE/CORRIDOR_CREATOR_PROMPT_FOREVER.md`. A fresh Opus *child* reads it, asks Nir
for the topic, and produces the three files for ONE corridor. DeepSeek then bakes, fixes any
recurring syntax bugs, wires the corridor to `app.py`, and pushes. (Recurring child bugs we've
catalogued: arcs wrapped in outer `$...$`; bare `|` inside `[[ ]]` arcs; bare math inside a
`\stain{}` not wrapped in its own `$...$`; `$\thread{}{$...$}$` double-dollar; forgotten baker arcs;
forgotten/duplicate `CORRIDOR:` numbers.)

**The website** (separate from the game, same repo) has a home page, an About page, and a footer of
social icons — not relevant to corridor 10, just context that "Peak Together" is bigger than the game.

**Repo layout:** all game files live under `descent/`. Project memory: `descent/WORKFLOW.md`. The
game's design "LAW" doc: `descent/PARENT_ESTATE/PARENT_HANDOFF_V3.md`. Launch:
`cd descent && python app.py` (it points at one corridor at a time via `LEVEL_MANIFEST`).

---

## 3. WHAT WE WANT — Corridor 10: "The Geometric Proof"

We want corridor 10 of the Basel Problem to be the **Geometric proof** — the Euclidean-geometry
proof that treats the real line as a circle of infinite radius, places N equally-spaced points on a
circle, draws chords from a point Q, and uses the **Inverse Pythagorean Theorem** and an induction
on powers of 2 to show the sum of inverse-square chord lengths is independent of N, yielding
∑ 1/(2z−1)² = π²/4 and hence ∑ 1/n² = π²/6. The **verbatim Wikipedia text** for this proof is in
Section 5 below.

**The thing that makes this corridor special — and why we're asking YOU, the architect, and not
just the usual corridor-builder child:**

Every previous corridor was equations + words, which our baker renders beautifully. **This proof is
fundamentally geometric** — it really *wants* a picture: the circle with the equally-spaced points
P₁…P_N, the point Q, the chords, and especially the inverse-Pythagorean figure (the right triangle
QP₁P₂ with the chord QP as its height, captioned *"The sum of inverse squares of distances of P1
and P2 from Q equals the inverse square distance from P to Q."*).

**What we would love:** to include the **Wikipedia illustration/diagram inside the Understanding
Mode of the FIRST robot**, so the player can actually *see* the geometry rather than only read
about it. **Nir can upload the Wikipedia illustration (a .jpg file) to you** if you'd like to look
at it while you think.

**The honest constraint (the symptom):** as described in Section 1, our Understanding-Mode panels
are currently **baked LaTeX *text* only**; we have no existing path for placing a real figure into a
robot's reading screens. We do not know the best way to do this, and we are **not** going to guess
or prescribe a method. That diagnosis is yours.

**So, what we're asking of you (as the architect):**
- Get fully oriented (ask Nir to paste any real engine files you want to study — e.g.
  `deu/bake_corridor.py`, `understanding.py`, `corridor_builder.py`, the corridor/baker file format,
  an existing baked folder listing — before committing to anything).
- Look at the geometric proof and the diagram Nir can upload.
- Then tell us **the best technical way to bring this corridor to life with its illustration**, and
  how you'd like to proceed (for example: what, if anything, needs to change in the engine or the
  baker; how a real image could live alongside or instead of a baked text panel; whether to handle
  it as one brief or several; and how the usual three content files would be authored once the
  approach is settled). The shape of the plan is entirely your call.

We're flexible on everything except the goal: **corridor 10 = the geometric proof, and we'd love the
player to be able to SEE its diagram in Understanding Mode.** Diagnose freely. 🙂

---

## 4. PRACTICAL FACTS YOU MAY WANT

- Repo: `https://github.com/strulovitz/peaktogether-website` · local: `C:\Users\nir_s\peaktogether-website`
- Game root: `descent/` · launch: `cd descent && python app.py`
- Baker run (example): `python deu/bake_corridor.py levels/mathematics/basel_problem/<file>.txt --out baked/basel/<corridor>`
- Toolchain present on Nir's machine: a working TeX Live with `pdflatex` + `pdftocairo`, TikZ,
  Pillow, matplotlib (its mathtext is what renders live SEGMENTS in-game).
- Portrait holograms for robots live at `descent/<Name_With_Underscores>-hologram.png`; Nir sources
  public-domain Wikipedia portraits.
- Reading-screen baked PNGs are transparent and coloured; understanding.py loads them as glass
  road-signs.
- DeepSeek is reliable on mechanical tasks (committing your verbatim files, running the baker,
  fixing syntax bugs, wiring `app.py`, pushing) — write for him generously and concretely when the
  time comes.

---

## 5. THE WIKIPEDIA TEXT (verbatim — the Geometric proof)

> Geometric proof
>
> The Basel problem can be proved with Euclidean geometry, using the insight that the real line can be seen as a circle of infinite radius. An intuitive, if not completely rigorous, sketch is given here.
>
>     Choose an integer N {\displaystyle N}, and take N {\displaystyle N} equally spaced points on a circle with circumference equal to 2 N {\displaystyle 2N}. The radius of the circle is N / π {\displaystyle N/\pi } and the length of each arc between two points is 2 {\displaystyle 2}. Call the points P 1.. N {\displaystyle P_{1..N}}.
>     Take another generic point Q {\displaystyle Q} on the circle, which will lie at a fraction 0 < α < 1 {\displaystyle 0<\alpha <1} of the arc between two consecutive points (say P 1 {\displaystyle P_{1}} and P 2 {\displaystyle P_{2}} without loss of generality).
>     Draw all the chords joining Q {\displaystyle Q} with each of the P 1.. N {\displaystyle P_{1..N}} points. Now (this is the key to the proof), compute the sum of the inverse squares of the lengths of all these chords, call it s i s c {\displaystyle sisc}.
>     The proof relies on the notable fact that (for a fixed α {\displaystyle \alpha }), the s i s c {\displaystyle sisc} does not depend on N {\displaystyle N}. Note that intuitively, as N {\displaystyle N} increases, the number of chords increases, but their length increases too (as the circle gets bigger), so their inverse square decreases.
>     In particular, take the case where α = 1 / 2 {\displaystyle \alpha =1/2}, meaning that Q {\displaystyle Q} is the midpoint of the arc between two consecutive P {\displaystyle P}'s. The s i s c {\displaystyle sisc} can then be found trivially from the case N = 1 {\displaystyle N=1}, where there is only one P {\displaystyle P}, and one Q {\displaystyle Q} on the opposite side of the circle. Then the chord is the diameter of the circle, of length 2 / π {\displaystyle 2/\pi }. The s i s c {\displaystyle sisc} is then π 2 / 4 {\displaystyle \pi ^{2}/4}.
>     When N {\displaystyle N} goes to infinity, the circle approaches the real line. If you set the origin at Q {\displaystyle Q}, the points P 1.. N {\displaystyle P_{1..N}} are positioned at the odd integer positions (positive and negative), since the arcs have length 1 from Q {\displaystyle Q} to P 1 {\displaystyle P_{1}}, and 2 onward. You hence get this variation of the Basel Problem:
>
> ∑ z = − ∞ ∞ 1 ( 2 z − 1 ) 2 = π 2 4 {\displaystyle \sum _{z=-\infty }^{\infty }{\frac {1}{(2z-1)^{2}}}={\frac {\pi ^{2}}{4}}}
>
>     From here, you can recover the original formulation with a bit of algebra, as:
>
> ∑ n = 1 ∞ 1 n 2 = ∑ n = 1 ∞ 1 ( 2 n − 1 ) 2 + ∑ n = 1 ∞ 1 ( 2 n ) 2 = 1 2 ∑ z = − ∞ ∞ 1 ( 2 z − 1 ) 2 + 1 4 ∑ n = 1 ∞ 1 n 2 {\displaystyle \sum _{n=1}^{\infty }{\frac {1}{n^{2}}}=\sum _{n=1}^{\infty }{\frac {1}{(2n-1)^{2}}}+\sum _{n=1}^{\infty }{\frac {1}{(2n)^{2}}}={\frac {1}{2}}\sum _{z=-\infty }^{\infty }{\frac {1}{(2z-1)^{2}}}+{\frac {1}{4}}\sum _{n=1}^{\infty }{\frac {1}{n^{2}}}}
>
> that is,
>
> 3 4 ∑ n = 1 ∞ 1 n 2 = π 2 8 {\displaystyle {\frac {3}{4}}\sum _{n=1}^{\infty }{\frac {1}{n^{2}}}={\frac {\pi ^{2}}{8}}}
>
> or
>
> ∑ n = 1 ∞ 1 n 2 = π 2 6 {\displaystyle \sum _{n=1}^{\infty }{\frac {1}{n^{2}}}={\frac {\pi ^{2}}{6}}}.
>
> The independence of the s i s c {\displaystyle sisc} from N {\displaystyle N} can be proved easily with Euclidean geometry for the more restrictive case where N {\displaystyle N} is a power of 2, i.e. N = 2 n {\displaystyle N=2^{n}}, which still allows the limiting argument to be applied. The proof proceeds by induction on n {\displaystyle n}, and uses the Inverse Pythagorean Theorem, which states that:
>
> 1 a 2 + 1 b 2 = 1 h 2 {\displaystyle {\frac {1}{a^{2}}}+{\frac {1}{b^{2}}}={\frac {1}{h^{2}}}}
>
> where a {\displaystyle a} and b {\displaystyle b} are the legs and h {\displaystyle h} is the height of a right triangle.
>
>     In the base case of n = 0 {\displaystyle n=0}, there is only 1 chord. In the case of α = 1 / 2 {\displaystyle \alpha =1/2}, it corresponds to the diameter and the s i s c {\displaystyle sisc} is π 2 / 4 {\displaystyle \pi ^{2}/4} as stated above.
>     Now, assume that you have 2 n {\displaystyle 2^{n}} points on a circle with radius 2 n / π {\displaystyle 2^{n}/\pi } and center O {\displaystyle O}, and 2 n + 1 {\displaystyle 2^{n+1}} points on a circle with radius 2 n + 1 / π {\displaystyle 2^{n+1}/\pi } and center R {\displaystyle R}. The induction step consists in showing that these 2 circles have the same s i s c {\displaystyle sisc} for a given α {\displaystyle \alpha }.
>
>     Start by drawing the circles so that they share point Q {\displaystyle Q}. Note that R {\displaystyle R} lies on the smaller circle. Then, note that 2 n + 1 {\displaystyle 2^{n+1}} is always even, and a simple geometric argument shows that you can pick pairs of opposite points P 1 {\displaystyle P_{1}} and P 2 {\displaystyle P_{2}} on the larger circle by joining each pair with a diameter. Furthermore, for each pair, one of the points will be in the "lower" half of the circle (closer to Q {\displaystyle Q}) and the other in the "upper" half.
>
> The sum of inverse squares of distances of P1 and P2 from Q equals the inverse square distance from P to Q.
>
>     The diameter of the bigger circle P 1 P 2 {\displaystyle P_{1}P_{2}} cuts the smaller circle at R {\displaystyle R} and at another point P {\displaystyle P}. You can then make the following considerations:
>         P 1 Q ^ P 2 {\displaystyle P_{1}{\widehat {Q}}P_{2}} is a right angle, since P 1 P 2 {\displaystyle P_{1}P_{2}} is a diameter.
>         Q P ^ R {\displaystyle Q{\widehat {P}}R} is a right angle, since Q R {\displaystyle QR} is a diameter.
>         Q R ^ P 2 = Q R ^ P {\displaystyle Q{\widehat {R}}P_{2}=Q{\widehat {R}}P} is half of Q O ^ P {\displaystyle Q{\widehat {O}}P} for the Inscribed Angle Theorem.
>         Hence, the arc Q P {\displaystyle QP} is equal to the arc Q P 2 {\displaystyle QP_{2}}, again because the radius is half.
>         The chord Q P {\displaystyle QP} is the height of the right triangle Q P 1 P 2 {\displaystyle QP_{1}P_{2}}, hence for the Inverse Pythagorean Theorem:
>
> 1 Q P ¯ 2 = 1 Q P 1 ¯ 2 + 1 Q P 2 ¯ 2 {\displaystyle {\frac {1}{{\overline {QP}}^{2}}}={\frac {1}{{\overline {QP_{1}}}^{2}}}+{\frac {1}{{\overline {QP_{2}}}^{2}}}}
>
>
>     Hence for half of the points on the bigger circle (the ones in the lower half) there is a corresponding point on the smaller circle with the same arc distance from Q {\displaystyle Q} (since the circumference of the smaller circle is half that of the bigger circle, the last two points closer to R {\displaystyle R} must have arc distance 2 as well). Vice versa, for each of the 2 n {\displaystyle 2^{n}} points on the smaller circle, we can build a pair of points on the bigger circle, and all of these points are equidistant and have the same arc distance from Q {\displaystyle Q}.
>     Furthermore, the total s i s c {\displaystyle sisc} for the bigger circle is the same as the s i s c {\displaystyle sisc} for the smaller circle, since each pair of points on the bigger circle has the same inverse square sum as the corresponding point on the smaller circle.[14]

---

## 6. ONE-LINE SUMMARY

DESCENT QED is a 6-DOF couples' game where you fly through mathematical-proof corridors and destroy
each robot by firing the mathematician whose idea that proof-step belongs to; nine Basel-problem
corridors are built and flying; we want corridor 10 to be the **Geometric proof**, and — because
this proof is genuinely visual — we'd love to bring the **Wikipedia diagram** into the first robot's
Understanding Mode (Nir can upload the .jpg). Our reading screens are currently baked LaTeX *text*
only, so the best way to show a real figure is an open question. You are the architect — please
diagnose the best path. 🩺

**END OF PROMPT — Nir will now tell you to begin, and can upload the diagram.**
