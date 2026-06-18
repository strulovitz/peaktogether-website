================================================================================
DESCENT QED — AUTHORING PROMPT FOR A NEW CORRIDOR
================================================================================

You are authoring content for DESCENT QED, a game about the hardest problems in
mathematics. The player flies down a corridor and meets a row of robot sentinels.
Each robot is one STEP of a real mathematical argument. The player defeats a robot
by firing the correct MATHEMATICIAN at it — the person whose idea that step is.
Clear all the robots and the corridor opens.

Read this whole document before writing anything. The three real, on-disk files
for the existing Basel corridor are pasted at the END as your canonical reference.
Everything before them explains the LOGIC so you understand WHY those files look
the way they do. Adapt the reasoning to your own subject; do not copy Basel's
content.


--------------------------------------------------------------------------------
0. NAMING: GAME vs LEVEL vs CORRIDOR vs ROBOT  (READ THIS FIRST)
--------------------------------------------------------------------------------

There is a four-level hierarchy. Do not confuse them.

  GAME      = DESCENT QED. The whole product. About the hardest math problems.
  LEVEL     = one mathematical SUBJECT. Implemented as a flat MANIFEST file in
              levels/<slug>.txt. There is NO hierarchy above a level — each
              subject is its own self-contained manifest. (In the future there
              may be other Descent games entirely, each its own level with its
              own corridors, on other subjects.)
  CORRIDOR  = one APPROACH or stepping-stone within that subject. A level can
              hold MANY corridors.
  ROBOT     = one STEP inside a corridor.

CONCRETE EXAMPLE (the reference files below):
  - The LEVEL is "The Basel Problem" (manifest: levels/basel.txt).
  - The CORRIDOR you will see is Euler's 1734 approach to proving
    sum 1/n^2 = pi^2/6 (game file: corridors/basel.txt).
  - This level currently has just this ONE corridor, but more corridors (other
    approaches / related stepping-stones) will be added to the same level later.

IMPORTANT: The reference files below still carry the older internal title
"The Basel Problem — Euler's Descent" and a folder named basel_euler_proof. Treat
those as historical names baked into existing files; the game is DESCENT QED, the
level is the subject, the corridor is the approach. Do not propagate "Euler's
Descent" as if it were the game's name — it isn't.


--------------------------------------------------------------------------------
1. THE CENTRAL IDEA: EACH ROBOT IS ONE "WHOSE IDEA IS THIS?" PUZZLE
--------------------------------------------------------------------------------

A corridor adapts one real argument, broken into steps, one robot per step. The
player's weapons are MATHEMATICIANS. To defeat a robot the player reads its
mathematics and its holographic face and answers: "whose idea is this step?" —
then fires that person.

So every robot resolves to ONE answer: the mathematician who owns that step. Many
parts of the robot must all point at that same answer:
  - the game NAME and its hologram portrait,
  - the BRIEFING_HINT and PROBLEM (which describe the step and ask whose it is),
  - the mathematics (SEGMENTS and the four EXPLAIN layers),
  - the VULNERABLE_TO id (the correct weapon).
If these disagree, the robot is broken. Coherence is the first law.

Robots are ordered as the argument flows. Robot 1 is nearest the doorway. The
order is usually LOGICAL (state the goal, assemble the machinery, generalize at
the end), not chronological/biographical. In Basel, Robot 1 states the prize and
Robot 7 generalizes beyond it.


--------------------------------------------------------------------------------
2. THE TWO KINDS OF NAME  (a subtlety the reference files demonstrate)
--------------------------------------------------------------------------------

A robot's NAME in the BAKER file may be EITHER:
  (a) a person's name           — e.g. ROBOT 1 "Leonhard Euler",
                                          ROBOT 5 "François Viète",
                                          ROBOT 7 "Bernhard Riemann"
  (b) the name of the TECHNIQUE — e.g. ROBOT 2 "Coefficient Matching",
                                          ROBOT 3 "The Product Over Roots",
                                          ROBOT 4 "The Series From Derivatives",
                                          ROBOT 6 "The Zeros of Sine"

Either way, in the GAME file every robot is defeated by a PERSON. The
VULNERABLE_TO id is always the mathematician who owns that step. So a robot named
after a technique in the baker is still tied to a person in the game:
  "Coefficient Matching"        -> VULNERABLE_TO { al_khwarizmi }
  "The Product Over Roots"      -> VULNERABLE_TO { weierstrass }
  "The Series From Derivatives" -> VULNERABLE_TO { taylor }
  "The Zeros of Sine"           -> VULNERABLE_TO { hipparchus }

THE HOLOGRAM FILENAME IS DERIVED FROM THE GAME ROBOT'S NAME, WHICH IS A PERSON.
The rule (from robots.py):

    filename = NAME.strip().replace(" ", "_") + "-hologram.png"

No lowercasing, no accent-stripping. Therefore the game NAME that drives the
filename must be ASCII: the baker prose may write "François Viète", but the game
NAME is "Francois Viete" -> Francois_Viete-hologram.png. Portraits live at the
repo root as <Name_With_Underscores>-hologram.png.

A new corridor will usually need portraits that do not exist yet. Do NOT restrict
your mathematicians to existing portraits, and do NOT silently assume files
exist. Compute every needed filename and emit a PORTRAITS NEEDED block at the top
of your deliverable, e.g.:

    PORTRAITS NEEDED
      Leonhard_Euler-hologram.png    — Leonhard Euler
      al-Khwarizmi-hologram.png      — Muhammad al-Khwarizmi
      Francois_Viete-hologram.png    — Francois Viete
      ...


--------------------------------------------------------------------------------
3. THE THREE FILES YOU WILL WRITE
--------------------------------------------------------------------------------

  BAKER FILE   grammar: KEY { value }
     Path: no fixed convention yet — infer from what exists. Basel's lives at
     levels/mathematics/basel_problem/basel_euler_proof.txt. Choose a sensible
     path under levels/<subject>/<corridor>/.
     Role: the rich teaching content. Its EXPLAIN_* fields get "baked" into the
     PNGs shown in Understanding Mode (baked/<slug>/).

  GAME FILE    grammar: KEY { value }
     Path: corridors/<slug>.txt  (e.g. corridors/basel.txt)
     Role: everything the engine needs to PLAY the corridor.

  MANIFEST     grammar: YAML-ish key: value
     Path: levels/<slug>.txt  (e.g. levels/basel.txt). THIS IS THE LEVEL FILE.
     Role: names the level (subject) and lists its corridor file(s).

HARD FACTS:
  - Baker and game files use BRACE grammar: KEY { ... }. The manifest uses a
    DIFFERENT, YAML-ish grammar. Do not mix them.
  - content_parser.py is the AUTHORITATIVE parser. If it would not parse, it is
    wrong, however well it reads.
  - You NEVER author understanding_dir; it is injected at runtime from the
    manifest's "baked:" line.
  - Manifest paths are relative with ../ (the manifest is in levels/, pointing
    up-and-over to baked/ and corridors/).
  - corridors: in the manifest is a LIST — a level can hold many corridors. Add
    one indented line per corridor.


--------------------------------------------------------------------------------
4. THE COLOUR SYSTEM *IS* THE ARGUMENT  (STAINS <-> LEDGER)
--------------------------------------------------------------------------------

Colours are not decoration. They encode the dependency structure of the argument.

In the BAKER file, STAINS assigns each IDEA an RGB colour. Two kinds:
  - PRIMARIES — the irreducible ingredient ideas. Each gets a distinct colour.
  - BLENDS — ideas that are the FUSION of two primaries. A blend's colour is
    visibly the mix of its two parents, and its MEANING is "this is where those
    two ingredients combine."

In Basel:
  roots (red) + coeff_root (yellow)   => product (orange)
  coeff_root (yellow) + sine_fn (blue) => series (green)
  roots (red) + sine_fn (blue)        => answer (purple)

Read as sentences: the product-over-roots picture is the roots combined with the
root<->coefficient principle; the power-series picture is that principle combined
with the sine function; and the final answer pi^2/6 is born where the roots
(which carry pi) meet the sine function.

Your colour task: identify the irreducible ingredients (primaries), then identify
which key objects are fusions of two ingredients (blends). Write a short comment
after each STAIN stating its meaning, exactly as Basel does.

The GAME file's LEDGER mirrors STAINS exactly — same names, same primary/blend
structure, same meaning — using named display colours instead of RGB. If LEDGER
and STAINS disagree, the corridor is broken.


--------------------------------------------------------------------------------
5. THE FOUR EXPLAIN LAYERS — A LADDER OF MATHEMATICAL MATURITY
--------------------------------------------------------------------------------

Each robot has four explanations of its step, the SAME mathematics at four
registers:

  EXPLAIN_MATHEMATICIAN — Graduate / Wikipedia level. Terse, closed forms, steps
       implied. Writes (a+b)^2 and moves on.

  EXPLAIN_PHYSICIST (THE SWEET SPOT) — Undergraduate. The mathematician's content
       OPENED UP: expand the closed expressions, show intermediate lines
       ((a+b)^2 -> a^2+2ab+b^2). Same rigour, more steps. This is the layer that
       most naturally carries actual NUMBERS.

  EXPLAIN_BIOLOGIST — A capable non-specialist. The real mechanism in plain
       words, light on symbols. Explain it the way you'd explain how an engine
       actually works to a smart teenager — real parts, real cause and effect, no
       condescension.

  EXPLAIN_ENGINEER — Applied. What the result is FOR: real uses, real plug-in
       numbers, why anyone cares.

The PHYSICIST layer is special: it is NOT hand-waving, it is the worked
derivation an undergraduate needs — the mathematician's argument with the algebra
expanded and intermediate steps written out.


--------------------------------------------------------------------------------
6. DUAL REGISTER: THE GAME EXPLAIN IS THE BAKER EXPLAIN, STRIPPED
--------------------------------------------------------------------------------

You write each EXPLAIN ONCE, richly, in the BAKER file, using full LaTeX plus the
\stain{} and \thread{} markup. The GAME file's version of that same EXPLAIN is the
SAME words, SAME steps, SAME numbers, with two mechanical changes:

  1. Strip baker-only LaTeX the game's mathtext renderer can't handle:
     remove \displaystyle, \tfrac -> \frac, \emph{...} -> plain text, \text{...}
     simplified, etc. Game math must be LEGAL MATHTEXT (the matplotlib mathtext
     subset: \sum \frac \prod \sin \pi \zeta \cdots are fine; rich macros are not).
  2. Remove the \stain{}{} and \thread{}{} wrappers, keeping their inner content.

You are NOT writing a second, different explanation. Compare Robot 4's baker
physicist layer to the game physicist layer in the reference: same sentence,
stripped.

BRIEFING_HINT and PROBLEM are GAME-ONLY fields with no baker counterpart — write
them fresh. The PROBLEM describes the step and asks, in effect, "whose idea is
this?"


--------------------------------------------------------------------------------
7. THREADS AND VALUE-ARCS
--------------------------------------------------------------------------------

THREADS: \thread{id}{...} (baker only) marks a RECURRING MOTIF tracked across
robots. Thread ids are STABLE and REUSED. Basel uses TWO:
  - t1 = the x^2 coefficient / product-form motif (appears in robots 2,3,4,7),
  - t2 = the leading x term of the sine series (appears in robot 4).
Use a thread when the same quantity recurs and you want the reader to follow it.

VALUE-ARCS: [[ $expr$ | value ]] (game EXPLAIN, mainly physicist/engineer) pair a
symbolic expression with the number it evaluates to, so the abstract meets the
concrete. Make sure the arithmetic is correct.


--------------------------------------------------------------------------------
8. SEGMENTS, EYE, VULNERABLE_TO  (game file)
--------------------------------------------------------------------------------

  SEGMENTS — the robot's body: a short stack of expression fragments, each tagged
       with a stain name (or NEUTRAL for connective tissue like $=$). Typically a
       left side, a NEUTRAL $=$, and a right side. The tags colour the body
       according to the section-4 argument.

  EYE — the single stain that glows as the weak point: usually the stain of the
       KEY idea of the step.

  VULNERABLE_TO — the id of the one correct weapon (the mathematician). Ids are
       lowercase ASCII, underscore-joined (al_khwarizmi, francois_viete).


--------------------------------------------------------------------------------
9. THE ARSENAL AND THE FIZZLE MATH
--------------------------------------------------------------------------------

The ARSENAL is the set of VULNERABLE_TO ids across all robots — one per robot.
With R robots there are R weapons.

For EVERY robot you write one FIZZLE for EVERY weapon that is NOT its correct
answer — i.e. R-1 fizzles per robot. Total:

    R * (R - 1)

Basel has R = 7 robots -> 42 fizzles. Count yours against this formula.

A FIZZLE is the message when the player fires the WRONG weapon. Each fizzle must:
  - acknowledge the wrong weapon's technique is a REAL, genuine part of the larger
    argument (never dismissive),
  - explain WHY it doesn't apply to THIS step,
  - steer toward the right idea WITHOUT NAMING THE PERSON ("think of the discipline
    whose name means restoring and balancing," not "fire al-Khwarizmi").
Study the Basel fizzles below: specific, respectful, steering, never naming.


--------------------------------------------------------------------------------
10. PRE-FLIGHT CHECKLIST (run before declaring done)
--------------------------------------------------------------------------------

  [ ] Naming is right: this is a CORRIDOR within a LEVEL (subject) of DESCENT QED.
  [ ] Every robot's game NAME, hologram, BRIEFING_HINT, PROBLEM, math, and
      VULNERABLE_TO point at the SAME person.
  [ ] LEDGER (game) mirrors STAINS (baker) exactly.
  [ ] Every blend colour is the mix of its two named parents, with a meaning
      comment stating "born where X meets Y".
  [ ] All four EXPLAIN layers exist for every robot, at the four registers.
  [ ] Each game EXPLAIN is the baker EXPLAIN STRIPPED (legal mathtext, no
      \stain/\thread/\tfrac/\displaystyle/\emph), same words/steps/numbers.
  [ ] Value-arcs [[ expr | value ]] are arithmetically correct.
  [ ] Thread ids are stable and reused where a motif recurs.
  [ ] Fizzle count is exactly R*(R-1); NO fizzle names a mathematician; each is
      respectful and steering.
  [ ] Every game NAME is ASCII; PORTRAITS NEEDED lists every required hologram.
  [ ] understanding_dir appears NOWHERE.
  [ ] Manifest uses YAML-ish grammar with ../ paths; baker/game use brace grammar.
  [ ] Would content_parser.py accept all three files? If unsure, it's wrong.


--------------------------------------------------------------------------------
11. WHEN TO STOP AND ASK THE HUMAN
--------------------------------------------------------------------------------

You are trusted to use judgment, not to invent your way past trouble. STOP and
ask if:
  - the argument doesn't break cleanly into one-idea-per-robot steps,
  - you can't build an honest colour graph (primaries/blends) without forcing it,
  - a step's "whose idea is this?" answer is genuinely ambiguous or contested,
  - you're unsure whether an expression is legal mathtext,
  - a required portrait, path, or convention is unclear.
A clear question always beats shipping something subtly wrong — a wrong corridor
teaches wrong mathematics. If you do not have a file you need, SAY SO PLAINLY and
ask for it; never fabricate it.


================================================================================
12. CANONICAL REFERENCE — THE REAL BASEL FILES (VERBATIM, ON-DISK TRUTH)
================================================================================

Study these as worked examples of every rule above. They are the actual files on
disk; do not transplant their content into your own corridor.


--------------------------------------------------------------------------------
FILE A — BAKER FILE
path: levels/mathematics/basel_problem/basel_euler_proof.txt
--------------------------------------------------------------------------------

TITLE { The Basel Problem — Euler's Descent }

STAINS {
  roots       = 0.85 0.12 0.12   # red — the zeros/roots; primitive idea feeding both the product and the final pi^2
  coeff_root  = 0.90 0.78 0.10   # yellow — the root<->coefficient principle (Vieta); shared ingredient of BOTH expansions
  sine_fn     = 0.12 0.30 0.85   # blue — the analytic sine function itself, the object being expanded
  product     = 0.90 0.45 0.10   # orange — sin x / x AS A PRODUCT OF ITS ROOTS = red(roots)+yellow(coeff principle)
  series      = 0.15 0.55 0.20   # green — sin x / x AS A POWER SERIES = yellow(coeff principle)+blue(sine function)
  answer      = 0.55 0.10 0.65   # purple — the Basel sum pi^2/6 = red(roots give pi) + blue(the sine function): born where the two pictures meet
}

ROBOT: 1
  NAME { Leonhard Euler }
  EXPLAIN_MATHEMATICIAN { The Basel problem asks for the closed form of $\displaystyle \stain{answer}{$\zeta(2)=\sum_{n=1}^{\infty}\frac{1}{n^2}$}$. Euler (1734) obtained $\stain{answer}{$\sum_{n=1}^{\infty}\frac{1}{n^2}=\frac{\pi^2}{6}$}\approx 1.644934$. The proof rests on writing the single function $\stain{sine_fn}{$\sin x$}$ in two ways and forcing their coefficients to agree. }
  EXPLAIN_PHYSICIST { Add up $1+\tfrac14+\tfrac19+\tfrac1{16}+\cdots$, the reciprocals of the squares. It converges to a number near $1.645$, but to \emph{what}? Euler's stunning answer is $\stain{answer}{$\frac{\pi^2}{6}$}$ — a circle constant appearing in a sum that has nothing to do with circles. The bridge is the function $\stain{sine_fn}{$\sin x$}$. }
  EXPLAIN_BIOLOGIST { Take the squares $1,4,9,16,\dots$ and add up their reciprocals forever. The pile of numbers settles down near $1.645$. The shocking fact is that this is exactly $\stain{answer}{$\pi^2/6$}$ — the number $\pi$ from circles, hiding inside a sum of fractions. }
  EXPLAIN_ENGINEER { This sum measures real things: the chance two random integers share no common factor is $6/\pi^2$, and infinite ladders of inverse-square terms appear in signal power and physics. Knowing $\stain{answer}{$\sum 1/n^2 = \pi^2/6$}$ turns an endless sum into one exact constant you can compute with. }

ROBOT: 2
  NAME { Coefficient Matching }
  EXPLAIN_MATHEMATICIAN { If a function equals \emph{both} $\stain{series}{$1-\tfrac{x^2}{3!}+\cdots$}$ and $\stain{product}{$\prod_n(1-\tfrac{x^2}{n^2\pi^2})$}$, then their like-power coefficients coincide. The $\thread{t1}{x^2}$ term of the series is $\thread{t1}{-\tfrac{1}{6}}$; of the product it is $\thread{t1}{-\tfrac{1}{\pi^2}\sum 1/n^2}$. Equating: $\stain{coeff_root}{$-\tfrac16=-\tfrac1{\pi^2}\sum\tfrac1{n^2}$}$. }
  EXPLAIN_PHYSICIST { Two formulas for the same curve must agree term by term. Look only at the $\thread{t1}{x^2}$ coefficient. From the series it is $\thread{t1}{-1/6}$; from the product it is $\thread{t1}{-\tfrac1{\pi^2}\sum 1/n^2}$. Setting them equal, $\stain{coeff_root}{$\sum 1/n^2 = \pi^2/6$}$. }
  EXPLAIN_BIOLOGIST { Imagine the same song written in two different notations. If both are correct, the note at each beat must match. Euler writes $\stain{sine_fn}{$\sin x / x$}$ two ways and compares just the $\thread{t1}{x^2}$ "beat." The two values must be equal — and that equality is the whole answer. }
  EXPLAIN_ENGINEER { This is "equate coefficients," the workhorse trick: two valid expansions of one function let you read off an unknown by matching a single power. Here matching the $\thread{t1}{x^2}$ terms lets you solve for $\stain{coeff_root}{$\sum 1/n^2$}$ without ever summing it directly. }

ROBOT: 3
  NAME { The Product Over Roots }
  EXPLAIN_MATHEMATICIAN { Treating $\stain{sine_fn}{$\sin x/x$}$ as an "infinite polynomial," Euler factors it over its $\stain{roots}{$\text{roots } \pm\pi,\pm2\pi,\dots$}$: $\displaystyle \stain{product}{$\frac{\sin x}{x}=\prod_{n=1}^{\infty}\thread{t1}{\Big(1-\frac{x^2}{n^2\pi^2}\Big)}$}$. Weierstrass later justified this. The $x^2$ coefficient is $-\sum 1/(n^2\pi^2)$. }
  EXPLAIN_PHYSICIST { A polynomial is the product of $\thread{t1}{(1-x/\text{root})}$ over its roots. Euler dares to do the same for $\stain{sine_fn}{$\sin x/x$}$, whose $\stain{roots}{$\text{roots are }n\pi$}$: $\stain{product}{$\frac{\sin x}{x}=\prod_n\thread{t1}{(1-\frac{x^2}{n^2\pi^2})}$}$. The $\pi$'s enter \emph{here}, straight from the roots. }
  EXPLAIN_BIOLOGIST { You can rebuild a polynomial from where it crosses zero: multiply one factor per crossing. Euler treats wavy $\stain{sine_fn}{$\sin x$}$ like a polynomial with infinitely many crossings at the $\stain{roots}{$\text{multiples of }\pi$}$, and multiplies a factor for each. This $\stain{product}{\text{product of factors}}$ is where $\pi$ sneaks in. }
  EXPLAIN_ENGINEER { Engineers factor transfer functions by their zeros all the time: each zero contributes one factor. Euler applies the same root-by-root assembly to $\stain{sine_fn}{$\sin x/x$}$, building it as a $\stain{product}{$\text{product over its zeros }n\pi$}$. The risky part — doing it for infinitely many zeros — is what Weierstrass had to certify. }

ROBOT: 4
  NAME { The Series From Derivatives }
  EXPLAIN_MATHEMATICIAN { The Maclaurin expansion of $\stain{sine_fn}{$\sin x$}$ is $\thread{t2}{x}-\tfrac{x^3}{3!}+\tfrac{x^5}{5!}-\cdots$, so $\displaystyle \stain{series}{$\frac{\sin x}{x}=1-\frac{x^2}{3!}+\frac{x^4}{5!}-\cdots$}$. Hence the $\thread{t1}{x^2}$ coefficient is $\thread{t1}{-1/3!=-1/6}$, the value to be matched against the product. }
  EXPLAIN_PHYSICIST { Differentiating $\stain{sine_fn}{$\sin x$}$ repeatedly at $0$ gives its power series $\thread{t2}{x}-\tfrac{x^3}{6}+\cdots$. Divide by $x$: $\stain{series}{$\frac{\sin x}{x}=1-\frac{x^2}{6}+\cdots$}$. The $\thread{t1}{x^2}$ coefficient is simply $\thread{t1}{-1/6}$ — clean, no $\pi$ in sight. }
  EXPLAIN_BIOLOGIST { A Taylor series rebuilds a function from its slopes at one point — add bigger and bigger correction terms. For $\stain{sine_fn}{$\sin x$}$ this gives $\thread{t2}{x}-\tfrac{x^3}{6}+\cdots$, and dividing by $x$ leaves $\stain{series}{$1-\tfrac{x^2}{6}+\cdots$}$. The size of the $\thread{t1}{x^2}$ bump is just $\thread{t1}{-1/6}$. }
  EXPLAIN_ENGINEER { The Taylor series is the practical way to compute $\stain{sine_fn}{$\sin x$}$ in hardware: a few terms approximate it. Here we only need one number — the $\stain{series}{\text{series'}}$ $\thread{t1}{x^2}$ coefficient, which is $\thread{t1}{-1/6}$ from the factorial $3!$. That known value is the anchor Euler matches. }

ROBOT: 5
  NAME { François Viète }
  EXPLAIN_MATHEMATICIAN { Vieta's formulas: for $a_0\prod(x-r_i)$, the coefficients are signed elementary symmetric functions of the $\stain{roots}{$\text{roots } r_i$}$. In the form $\prod(1-x/r_i)$, the linear coefficient is $\stain{coeff_root}{$-\sum 1/r_i$}$. This is exactly the legitimate \emph{finite} fact Euler extends to infinitely many roots. }
  EXPLAIN_PHYSICIST { For a quadratic $a(x-r_1)(x-r_2)$, the sum of roots and product of roots \emph{are} the coefficients: $r_1+r_2=-b/a$, $r_1r_2=c/a$. So $\stain{coeff_root}{\text{coefficients are built from the roots}}$ — and reading the $x^2$ coefficient of $\prod(1-x^2/r^2)$ gives $-\sum 1/r^2$. }
  EXPLAIN_BIOLOGIST { Here is a true fact about ordinary polynomials: once you know where it hits zero (its $\stain{roots}{\text{roots}}$), you know its coefficients — they are just sums and products of those roots. Euler's leap is to trust this same $\stain{coeff_root}{\text{roots-give-coefficients}}$ rule even for an infinitely long polynomial. }
  EXPLAIN_ENGINEER { Vieta lets you go between a polynomial's roots and its coefficients without solving anything — invaluable for designing filters from desired zeros. Euler uses one slice of it: the $\stain{coeff_root}{$x^2\text{ coefficient}=-\sum 1/r^2$}$, applied to the roots of sine. }

ROBOT: 6
  NAME { The Zeros of Sine }
  EXPLAIN_MATHEMATICIAN { $\stain{sine_fn}{$\sin x$}=0$ exactly on $\stain{roots}{$\{n\pi:n\in\mathbb{Z}\}$}$. Removing the zero at $0$ (via $\sin x/x$) leaves roots $\stain{roots}{$\pm\pi,\pm2\pi,\dots$}$, paired as $\pm n\pi$ to give factors $1-x^2/(n^2\pi^2)$. These roots are the sole source of $\pi$ in the final answer. }
  EXPLAIN_PHYSICIST { Where does $\stain{sine_fn}{$\sin x$}$ cross zero? At every $\stain{roots}{$\text{multiple of }\pi$}$: $0,\pm\pi,\pm2\pi,\dots$. These crossing points are the raw material — feed them into the product and the $\pi^2$ in $\pi^2/6$ comes directly from squaring those $\stain{roots}{$n\pi$}$. }
  EXPLAIN_BIOLOGIST { The wave $\stain{sine_fn}{$\sin x$}$ touches the axis at evenly spaced spots: $0,\pi,2\pi,3\pi,\dots$ and their negatives. These $\stain{roots}{\text{zero-crossings}}$ are the only place the number $\pi$ enters the whole story; everything downstream is built from them. }
  EXPLAIN_ENGINEER { The zeros of a system are where its output vanishes. For $\stain{sine_fn}{$\sin x$}$ they sit at $\stain{roots}{$n\pi$}$, perfectly periodic. Euler harvests this list of zeros as the inputs to his product; the regular spacing $\pi$ is what ultimately surfaces as $\pi^2$ in the answer. }

ROBOT: 7
  NAME { Bernhard Riemann }
  EXPLAIN_MATHEMATICIAN { Basel is the value $s=2$ of $\displaystyle \zeta(s)=\sum_{n=1}^{\infty}\frac1{n^s}=\prod_{p\text{ prime}}\thread{t1}{\frac{1}{1-p^{-s}}}$. The same sum-equals-product duality that solved Basel reappears as Euler's product over $\stain{roots}{\text{primes}}$; Riemann's continuation of $\zeta$ then governs prime distribution. }
  EXPLAIN_PHYSICIST { Euler's $\stain{answer}{$\sum 1/n^2$}$ is one value of a whole family $\zeta(s)=\sum 1/n^s$. Euler also wrote it as a $\thread{t1}{\text{product over primes}}$, $\prod 1/(1-p^{-s})$ — again a sum equals a product. Riemann extended $\zeta$ to complex $s$, linking it to where the primes lie. }
  EXPLAIN_BIOLOGIST { The Basel sum is just one room in a larger building: the zeta function $\sum 1/n^s$ for any power $s$. Euler found this whole building secretly factors over the prime numbers — a sum turning into a $\thread{t1}{\text{product}}$, just like the sine trick. Riemann's study of it became the deepest open question in math. }
  EXPLAIN_ENGINEER { Generalize the exponent: $\zeta(s)=\sum 1/n^s$. Its prime $\thread{t1}{\text{product form}}$ $\prod 1/(1-p^{-s})$ is the engine behind counting primes and estimating coprimality. Basel ($s=2$) is the first concrete value; the machinery scales to the analytic number theory built on it. }


--------------------------------------------------------------------------------
FILE B — GAME FILE
path: corridors/basel.txt
--------------------------------------------------------------------------------

# ===========================================================
# The Basel Problem — Euler's Descent. Seven sentinels, one per
# step of Euler's 1734 solution of sum 1/n^2 = pi^2/6. Robot 1 is
# nearest the doorway. Each yields to exactly ONE mathematician id.
# Robot N maps 1:1 to baker step N (baked/basel/robotN_*.png).
# LEDGER mirrors the baker STAINS: roots=red, coeff_root=yellow,
# sine_fn=blue; product=red+yellow, series=yellow+blue, answer=red+blue.
# ===========================================================
CORRIDOR: 1
TITLE { The Basel Problem -- Euler's Descent }
FLAVOR { One sum of squares, two faces of a single sine, and the circle hidden inside. }
LEDGER {
  PRIMARY roots      = red
  PRIMARY coeff_root = yellow
  PRIMARY sine_fn    = blue
  BLEND   product    = roots + coeff_root
  BLEND   series     = coeff_root + sine_fn
  BLEND   answer     = roots + sine_fn
}
BRIEFING_INTRO { Seven sentinels guard the road to the hostages, one for each
          move in Euler's descent on the Basel sum. Read each robot's blue
          hologram face, judge whose idea its mathematics belongs to, and fire
          that mathematician. Match the face to the technique and the corridor opens. }
ENTRY_TEXT { You have entered the Basel corridor. Somewhere ahead, a sum of squares is waiting to become a circle. }
EXIT_TEXT { The last sentinel falls and the sum closes into pi^2/6. The hostages are free -- you have flown the whole length of Euler's proof. Well done. }

ROBOT: 1
NAME { Leonhard Euler }
BRIEFING_HINT { This sentinel states the prize itself: the closed form of the sum
          of inverse squares. It yields to the man who first named the result. }
PROBLEM { Identify the value of the Basel sum $\sum_{n=1}^{\infty} \frac{1}{n^2}$ --
          who first proved it equals $\frac{\pi^2}{6}$? }
EXPLAIN_MATHEMATICIAN { The Basel problem asks for the closed form of
          $\zeta(2) = \sum_{n=1}^{\infty} \frac{1}{n^2}$; in 1734 Euler proved it
          equals $\frac{\pi^2}{6} \approx 1.644934$ by writing $\sin x$ two ways
          and forcing their coefficients to agree. }
EXPLAIN_PHYSICIST { Add $1 + \frac{1}{4} + \frac{1}{9} + \frac{1}{16} + \cdots$; it
          settles near $1.645$. Euler's shock was that the exact value is
          $\frac{\pi^2}{6}$ -- a circle constant inside a sum with no circles. }
EXPLAIN_BIOLOGIST { Add the reciprocals of the squares $1, 4, 9, 16, \dots$ forever
          and the pile settles near $1.645$. The surprise is that this is exactly
          $\frac{\pi^2}{6}$ -- the circle number $\pi$, hiding in plain fractions. }
EXPLAIN_ENGINEER { Plug in numbers: the sum [[ $\sum \frac{1}{n^2}$ | 1.6449 ]]
          meets the constant [[ $\frac{\pi^2}{6}$ | 1.6449 ]], so they match -- an
          endless sum collapses into one exact value you can compute with. }
SEGMENTS {
  $\sum_{n=1}^{\infty} \frac{1}{n^2}$   | answer
  $=$                                   | NEUTRAL
  $\frac{\pi^2}{6}$                     | answer
}
EYE { answer }
VULNERABLE_TO { euler }
FIZZLE al_khwarizmi { Matching like-power coefficients is a true step further inside this proof, but right here you are only being asked to NAME the famous result -- think about WHO first summed these squares. }
FIZZLE weierstrass { Justifying the infinite product is a genuine and deep part of the story, but this opening robot just states the headline answer -- name the person who first claimed it. }
FIZZLE taylor { Expanding a function into a power series is a real ingredient used later, but here no function is being expanded -- you are being asked who owns this famous sum. }
FIZZLE viete { Relating roots to coefficients is a real tool used downstream, but this robot only poses the result itself -- recall who first announced that the squares sum to pi-squared over six. }
FIZZLE hipparchus { The zeros of sine matter deeper in the proof, but no sine appears yet -- this sentinel just states the prize, so name its discoverer. }
FIZZLE riemann { Generalizing to the zeta function comes at the very end of the corridor, but this first robot is the original special case -- name the man who solved it in 1734. }

ROBOT: 2
NAME { al-Khwarizmi }
BRIEFING_HINT { Coefficient Matching: two true expansions of one function must
          agree term by term. This sentinel yields to the father of algebra. }
PROBLEM { Two expansions describe the same function. Equate their $x^2$
          coefficients to extract the unknown sum -- which algebraic discipline is this? }
EXPLAIN_MATHEMATICIAN { If one function equals both the series $1 - \frac{x^2}{3!} +
          \cdots$ and the product $\prod_n \left( 1 - \frac{x^2}{n^2 \pi^2} \right)$,
          their like-power coefficients coincide; equating the $x^2$ terms gives
          $-\frac{1}{6} = -\frac{1}{\pi^2} \sum \frac{1}{n^2}$. }
EXPLAIN_PHYSICIST { Two correct formulas for one curve must agree term by term.
          The $x^2$ coefficient is $-\frac{1}{6}$ from the series and
          $-\frac{1}{\pi^2} \sum \frac{1}{n^2}$ from the product; setting them equal
          gives $\sum \frac{1}{n^2} = \frac{\pi^2}{6}$. }
EXPLAIN_BIOLOGIST { It is one song written in two notations: if both are right, the
          note on each beat must match. Compare just the $x^2$ beat of the two
          versions and that single equality hands you the whole answer. }
EXPLAIN_ENGINEER { This is equate-coefficients, the workhorse trick: two valid
          expansions let you read off an unknown by matching one power. Here the
          $x^2$ terms let you solve for $\sum \frac{1}{n^2}$ without summing it. }
SEGMENTS {
  $-\frac{1}{6}$                         | series
  $=$                                    | NEUTRAL
  $-\frac{1}{\pi^2} \sum \frac{1}{n^2}$  | product
}
EYE { coeff_root }
VULNERABLE_TO { al_khwarizmi }
FIZZLE euler { Naming the final result is what the first sentinel wanted; this robot is about the algebraic MOVE of equating two expansions -- think of the discipline whose very name means restoring and balancing. }
FIZZLE weierstrass { Certifying the infinite product is the rigour behind one side, but this step is the pure act of balancing two expressions against each other -- recall who founded the art of solving equations. }
FIZZLE taylor { One of the two expansions is indeed a power series, but here you must MATCH it against the other, not generate it -- which ancient discipline is built on balancing equals against equals? }
FIZZLE viete { Roots and coefficients meet later; this robot is the broader act of setting two whole expansions equal and reading off a term -- think of the founder of algebra itself. }
FIZZLE hipparchus { Sine's zeros feed one expansion, but this sentinel is about the algebraic balancing of two formulas -- name the scholar whose book gave algebra its name. }
FIZZLE riemann { The grand generalization waits at the end; this is the humble, powerful act of equating like powers -- recall who first systematized solving for an unknown. }

ROBOT: 3
NAME { Karl Weierstrass }
BRIEFING_HINT { The Product Over Roots: factor sine over its zeros as if it were an
          infinite polynomial. This sentinel yields to the man who made it rigorous. }
PROBLEM { Euler writes $\frac{\sin x}{x}$ as an infinite product over its roots.
          Who supplied the rigorous justification that such a product is valid? }
EXPLAIN_MATHEMATICIAN { Treating $\frac{\sin x}{x}$ as an infinite polynomial, Euler
          factors it over its roots $\pm \pi, \pm 2\pi, \dots$ as $\frac{\sin x}{x} =
          \prod_{n=1}^{\infty} \left( 1 - \frac{x^2}{n^2 \pi^2} \right)$; Weierstrass
          later justified that this product converges and represents the function. }
EXPLAIN_PHYSICIST { A polynomial is the product of factors, one per root. Euler dares
          the same for $\frac{\sin x}{x}$, whose roots are the $n\pi$: $\frac{\sin x}{x}
          = \prod_n \left( 1 - \frac{x^2}{n^2 \pi^2} \right)$. The $\pi$'s enter here. }
EXPLAIN_BIOLOGIST { You can rebuild a polynomial from where it crosses zero -- one
          factor per crossing. Euler treats wavy sine like a polynomial with
          infinitely many crossings and multiplies a factor for each; later someone
          had to prove that infinite product was even allowed. }
EXPLAIN_ENGINEER { Engineers factor transfer functions by their zeros, one factor
          each. Euler does the same to $\frac{\sin x}{x}$ over its zeros $n\pi$. The
          risky part -- doing it for infinitely many zeros -- is what had to be certified. }
SEGMENTS {
  $\frac{\sin x}{x}$                                          | sine_fn
  $=$                                                         | NEUTRAL
  $\prod_{n=1}^{\infty} \left( 1 - \frac{x^2}{n^2 \pi^2} \right)$ | product
}
EYE { product }
VULNERABLE_TO { weierstrass }
FIZZLE euler { Euler boldly WROTE this product, but the robot before you asks who made the daring step safe -- think of the founder of rigorous analysis, not the one who leapt. }
FIZZLE al_khwarizmi { Equating coefficients uses this product as one input, but this sentinel is about whether the infinite product is even legitimate -- recall who built the careful foundations of limits. }
FIZZLE taylor { A power series is the OTHER expansion; here the function is written as a product over roots, and someone had to prove that convergent -- name the master of rigorous analysis. }
FIZZLE viete { Vieta's root-coefficient link inspires the idea, but the question here is who justified extending products to infinitely many factors -- think of the founder of epsilon-delta rigour. }
FIZZLE hipparchus { Sine's zeros are the roots feeding this product, yet the robot asks who PROVED the product valid -- recall the analyst who put infinite processes on solid ground. }
FIZZLE riemann { Riemann generalizes much later; this robot is specifically about certifying Euler's infinite product -- name the mathematician famous for rigorous foundations of analysis. }

ROBOT: 4
NAME { Brook Taylor }
BRIEFING_HINT { The Series From Derivatives: build sine from its slopes at zero as a
          power series. This sentinel yields to the namesake of that expansion. }
PROBLEM { The other expansion of $\frac{\sin x}{x}$ is a power series from repeated
          derivatives at $0$. Whose expansion gives $1 - \frac{x^2}{3!} + \cdots$? }
EXPLAIN_MATHEMATICIAN { The Maclaurin expansion of $\sin x$ is $x - \frac{x^3}{3!} +
          \frac{x^5}{5!} - \cdots$, so $\frac{\sin x}{x} = 1 - \frac{x^2}{3!} +
          \frac{x^4}{5!} - \cdots$; hence its $x^2$ coefficient is
          $-\frac{1}{3!} = -\frac{1}{6}$, the value matched against the product. }
EXPLAIN_PHYSICIST { Differentiating $\sin x$ repeatedly at $0$ gives the series $x -
          \frac{x^3}{6} + \cdots$. Divide by $x$: $\frac{\sin x}{x} = 1 - \frac{x^2}{6}
          + \cdots$. The $x^2$ coefficient is simply $-\frac{1}{6}$, with no $\pi$. }
EXPLAIN_BIOLOGIST { This kind of series rebuilds a function from its slopes at one
          point, adding bigger correction terms. For sine it gives $x - \frac{x^3}{6}
          + \cdots$, and dividing by $x$ leaves $1 - \frac{x^2}{6} + \cdots$. }
EXPLAIN_ENGINEER { This series is the practical way hardware computes $\sin x$ -- a
          few terms suffice. Here we need just one number: the $x^2$ coefficient
          $-\frac{1}{6}$, coming from the factorial $3!$. That value is Euler's anchor. }
SEGMENTS {
  $\frac{\sin x}{x}$                                  | sine_fn
  $=$                                                 | NEUTRAL
  $1 - \frac{x^2}{3!} + \frac{x^4}{5!} - \cdots$      | series
}
EYE { series }
VULNERABLE_TO { taylor }
FIZZLE euler { Euler assembles all the pieces, but this robot is the specific power-series expansion of sine -- think of the man whose name that series carries. }
FIZZLE al_khwarizmi { Equating coefficients USES this series as one side; the robot itself is about GENERATING the series from derivatives -- recall whose expansion turns a function into powers of x. }
FIZZLE weierstrass { Weierstrass justified the PRODUCT side; here you face the series side built from slopes at zero -- name the mathematician whose expansion this is. }
FIZZLE viete { Roots and coefficients belong to the product picture; this robot is the derivative-built series $1 - x^2/6 + \cdots$ -- think of the namesake of that power series. }
FIZZLE hipparchus { Sine's zeros build the product; here sine is built instead from its derivatives at a point -- recall who lends his name to that expansion of a function. }
FIZZLE riemann { The zeta generalization is far ahead; this robot is the humble Maclaurin/Taylor series of sine -- name the expansion's namesake. }

ROBOT: 5
NAME { Francois Viete }
BRIEFING_HINT { Vieta's formulas: a polynomial's coefficients are built from its
          roots. This sentinel yields to the man who first linked roots and coefficients. }
PROBLEM { For a polynomial written as $\prod (1 - x/r_i)$, the linear coefficient is
          $-\sum 1/r_i$. Whose formulas connect roots to coefficients like this? }
EXPLAIN_MATHEMATICIAN { Vieta's formulas express a polynomial's coefficients as signed
          symmetric functions of its roots; in the form $\prod (1 - x/r_i)$ the linear
          coefficient is $-\sum \frac{1}{r_i}$. This is the legitimate finite fact that
          Euler boldly extends to infinitely many roots. }
EXPLAIN_PHYSICIST { For a quadratic $a(x - r_1)(x - r_2)$ the sum and product of roots
          ARE the coefficients: $r_1 + r_2 = -\frac{b}{a}$. Reading the $x^2$
          coefficient of $\prod (1 - x^2/r^2)$ gives exactly $-\sum \frac{1}{r^2}$. }
EXPLAIN_BIOLOGIST { Here is a true fact about ordinary polynomials: once you know where
          one hits zero, you know its coefficients -- they are just sums and products
          of those roots. Euler's leap is to trust that rule for an infinite polynomial. }
EXPLAIN_ENGINEER { These formulas let you pass between a polynomial's roots and its
          coefficients without solving anything -- prized for designing filters from
          chosen zeros. Euler uses one slice: the $x^2$ coefficient is $-\sum 1/r^2$. }
SEGMENTS {
  $\prod \left( 1 - \frac{x}{r_i} \right)$   | product
  $=$                                       | NEUTRAL
  $-\sum \frac{1}{r_i}$                      | coeff_root
}
EYE { coeff_root }
VULNERABLE_TO { viete }
FIZZLE euler { Euler exploits this root-coefficient link, but he did not discover it -- this robot honours the man who first wrote those relations down. }
FIZZLE al_khwarizmi { Algebra balances expansions; this robot is the SPECIFIC law tying a polynomial's roots to its coefficients -- recall whose named formulas state that link. }
FIZZLE weierstrass { Weierstrass justified the infinite product; this sentinel is the finite, classical roots-to-coefficients rule it rests on -- name the man those formulas are named for. }
FIZZLE taylor { That is the series side, built from derivatives; here the picture is roots determining coefficients -- think of the namesake of the root-coefficient relations. }
FIZZLE hipparchus { Sine's zeros are the roots being fed in, but this robot is the general principle that roots fix the coefficients -- recall whose formulas express exactly that. }
FIZZLE riemann { The grand zeta picture is the finale; this is the elementary symmetric-function law of roots and coefficients -- name the early algebraist it is named after. }

ROBOT: 6
NAME { Hipparchus }
BRIEFING_HINT { The Zeros of Sine: sine vanishes exactly at the multiples of pi.
          This sentinel yields to the founder of trigonometry. }
PROBLEM { Where does $\sin x = 0$? These crossings at the multiples of $\pi$ are the
          product's raw material. Which founder of trigonometry first charted sine? }
EXPLAIN_MATHEMATICIAN { $\sin x = 0$ exactly on the multiples of $\pi$; removing the
          zero at $0$ via $\frac{\sin x}{x}$ leaves roots $\pm \pi, \pm 2\pi, \dots$,
          paired as $\pm n\pi$ to give factors $1 - \frac{x^2}{n^2 \pi^2}$. These roots
          are the sole source of $\pi$ in the answer. }
EXPLAIN_PHYSICIST { Where does $\sin x$ cross zero? At every multiple of $\pi$:
          $0, \pm \pi, \pm 2\pi, \dots$. Feed these crossings into the product and the
          $\pi^2$ in $\frac{\pi^2}{6}$ comes straight from squaring the $n\pi$. }
EXPLAIN_BIOLOGIST { The wave $\sin x$ touches the axis at evenly spaced spots: $0, \pi,
          2\pi, 3\pi, \dots$ and their negatives. These crossings are the only place
          the number $\pi$ enters the whole story. }
EXPLAIN_ENGINEER { The zeros of a system are where its output vanishes. For $\sin x$
          they sit at $n\pi$, perfectly periodic. Euler harvests this list of zeros as
          the product's inputs; the spacing $\pi$ resurfaces as $\pi^2$ in the answer. }
SEGMENTS {
  $\sin x = 0$        | sine_fn
  $=$                 | NEUTRAL
  $x = n\pi$          | roots
}
EYE { roots }
VULNERABLE_TO { hipparchus }
FIZZLE euler { Euler USES these zeros, but this robot is about the trigonometry of where sine vanishes -- think of the ancient astronomer who first tabulated the sine. }
FIZZLE al_khwarizmi { Algebra balances the two expansions; this sentinel is pure trigonometry -- where sine crosses zero -- so recall who founded the study of those angles. }
FIZZLE weierstrass { Weierstrass certified the product these zeros feed, but the robot asks WHERE sine is zero -- name the founder of trigonometry who first charted the sine. }
FIZZLE taylor { That is the derivative-built series; here you need the geometric zeros of sine at the multiples of pi -- think of the father of trigonometry. }
FIZZLE viete { Vieta turns roots into coefficients, but first you must know WHERE the roots are -- recall the ancient who first measured sine and its vanishing points. }
FIZZLE riemann { Riemann's zeta is the finale; this robot is the elementary fact that sine vanishes at every multiple of pi -- name trigonometry's founder. }

ROBOT: 7
NAME { Bernhard Riemann }
BRIEFING_HINT { Generalization: the Basel sum is one value of the zeta function, which
          factors as a product over primes. This sentinel yields to zeta's master. }
PROBLEM { Basel is the case $s = 2$ of $\zeta(s) = \sum \frac{1}{n^s}$, with a product
          over primes. Who extended $\zeta$ and tied it to the primes? }
EXPLAIN_MATHEMATICIAN { Basel is the value $s = 2$ of $\zeta(s) = \sum_{n=1}^{\infty}
          \frac{1}{n^s} = \prod_p \frac{1}{1 - p^{-s}}$. The same sum-equals-product
          duality reappears as a product over primes; Riemann's continuation of
          $\zeta$ to complex $s$ then governs how the primes are distributed. }
EXPLAIN_PHYSICIST { Euler's $\sum \frac{1}{n^2}$ is one value of a whole family
          $\zeta(s) = \sum \frac{1}{n^s}$. Euler also wrote it as a product over primes,
          $\prod \frac{1}{1 - p^{-s}}$ -- again a sum equals a product. Riemann
          extended $\zeta$ to complex $s$, linking it to where the primes lie. }
EXPLAIN_BIOLOGIST { The Basel sum is one room in a larger building: the zeta function
          $\sum \frac{1}{n^s}$ for any power $s$. Euler found it secretly factors over
          the primes -- a sum turning into a product, just like the sine trick -- and
          studying it became the deepest open question in mathematics. }
EXPLAIN_ENGINEER { Generalize the exponent: $\zeta(s) = \sum \frac{1}{n^s}$. Its prime
          product form $\prod \frac{1}{1 - p^{-s}}$ drives counting primes and
          estimating coprimality. Basel ($s = 2$) is the first concrete value; the
          machinery scales to the analytic number theory built on it. }
SEGMENTS {
  $\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s}$   | answer
  $=$                                              | NEUTRAL
  $\prod_p \frac{1}{1 - p^{-s}}$                   | product
}
EYE { answer }
VULNERABLE_TO { riemann }
FIZZLE euler { Euler indeed found the prime product, but this final robot is about the deep continuation of zeta and its link to the primes -- name the man whose hypothesis governs them. }
FIZZLE al_khwarizmi { Equating coefficients solved the special case; this sentinel is the grand generalization to all exponents s -- recall who extended zeta into the complex plane. }
FIZZLE weierstrass { Weierstrass secured one infinite product, but this robot is the whole zeta function and its prime factorization -- name the master of its analytic continuation. }
FIZZLE taylor { The power series cracked one value; here zeta runs over every exponent and over the primes -- think of the man whose name the famous hypothesis bears. }
FIZZLE viete { Vieta linked finite roots and coefficients; this robot reaches to the infinitude of primes through zeta -- recall who tied that function to their distribution. }
FIZZLE hipparchus { Sine's zeros gave the special case; this final sentinel is about the zeros of zeta and the primes -- name the mathematician whose study of them is the deepest open problem. }


--------------------------------------------------------------------------------
FILE C — MANIFEST (THE LEVEL FILE)
path: levels/basel.txt
--------------------------------------------------------------------------------

title: The Basel Problem
baked: ../baked/basel
corridors:
  ../corridors/basel.txt


================================================================================
END OF PROMPT
================================================================================
Build the three files, run the checklist in section 10, emit the PORTRAITS NEEDED
block, and stop to ask the human (section 11) if anything resists clean
adaptation or if you lack a file you need. Faithfulness to the mathematics comes
first; everything else serves it.
