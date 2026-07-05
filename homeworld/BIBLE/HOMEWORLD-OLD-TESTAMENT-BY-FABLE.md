# THE BIBLE — HOMEWORLD: A GOOD BASIS
## Founding Design Document, v2.1 — Peak Together — July 4, 2026

---

> ## ⚖️ OWNER AMENDMENTS (add-only, maintained by DeepSeek — READ FIRST) ⚖️
>
> **These are Nir's (the owner's) binding decisions made after this document was written.
> They OVERRIDE anything below that conflicts. Fable's original text is preserved verbatim
> underneath — do not delete it — but where it disagrees with an amendment here, the
> amendment wins. New amendments are appended to this list.**
>
> **Amendment A1 — ART DIRECTION: SHIPS ARE SOLID, NOT WIREframe (July 5, 2026).**
> Glowing-wireframe ships FAIL Bible Law 1 ("gaming first — would a gamer choose to play
> this?"). SHIPS are now **solid, opaque, lit triangle meshes** — per-pixel Blinn-Phong
> (key + fill + rim + specular), flat-shaded paneled hulls with per-face color variation,
> emissive engine nozzles/windows feeding bloom; hundreds+ triangles per class, generated
> by `shipwright.py` (procedural today; Blender/OBJ import is a sanctioned future path).
> **Only THE MATH LAYER** (arrows, grids, spans, ghost vectors, trails, labels) stays
> glowing holographic — drawn additively OVER the solid world with depth testing so hulls
> occlude it correctly. Render order: solid pass (depth write) → glow pass (depth test, no
> write) → bloom → crisp overlay. **Wherever this document calls ships "wireframe" or
> "holographic," that is superseded — ships are solid; the math around them glows.**
> "It must look like a game a gamer would choose" outranks any aesthetic theory in any
> design document; the owner is the sole arbiter. (Full text: `notes/amendment_a1_art_direction.md`.)
>
> **Amendment A1.1 — SHIPS NEVER BLOOM; DUAL RENDER TARGETS; DARK MOTHERSHIP AT ORIGIN (July 5, 2026).**
> A1's "emissive engine nozzles/windows feeding bloom" was wrong — ships must NEVER bloom, by
> construction. The scene FBO now has TWO color attachments sharing one depth buffer: SOLID buffer
> (ships, linear, untouched by bloom or tone map → crisp panel detail like real Homeworld hulls) +
> GLOW buffer (holograms — lines/labels/panels — additive; this buffer alone is downsampled, blurred,
> and tone-mapped, then added on top of the SOLID buffer). Mothership is at the origin (0,0,0) with a
> dark slate hull (0.155,0.165,0.195) and steel-blue accent [0.45,0.55,0.7]; bright 10-unit long
> basis axes e1/e2/e3 are drawn in a separate OVERLAY pass (depth test OFF) ON TOP of her hull —
> "she is the coordinate system made flesh." Engine nozzles, windows, and intake maws are dim lit
> "lamps" (emissive values ≤1, never HDR), painted into the solid buffer. COMPOSITE_FRAG reads 3
> textures (u_scene + u_glow + u_bloom) and tone-maps ONLY the hologram layer. Wherever this document
> or A1 says emissive ship parts "feed bloom," that is superseded — ships never interact with the
> bloom pipeline. (Deliverable 9 in BIBLE.)

NOTE TO ALL READERS (human, Opus parent/child, DeepSeek): All mathematics in this
document is written in LaTeX. Inline math is delimited by $...$ and display math by
$$...$$. Matrices use \begin{bmatrix}...\end{bmatrix}, read column by column is
stated explicitly where needed. Subscripts use _, superscripts use ^. Example:
$v_1^T$ means "vector v-sub-one, transposed." Never alter the LaTeX when copying.

This document is the single source of truth for the project. Every future
collaborator receives it in full. It contains the complete world model, every game
mechanic worked out to implementation depth with the real mathematics and real
code, the full campaign, and the engineering doctrine. When any later decision
contradicts this document, this document wins unless the project owner explicitly
overrules it.

---------------------------------------------------------------------------------
PART 0 — IDENTITY AND IRON RULES
---------------------------------------------------------------------------------

THE GAME IN ONE SENTENCE: a free, open-source, two-player-one-screen remake of
Homeworld (1999), in which commanding your fleet IS doing linear algebra — every
ship is a column vector, the fleet is a matrix, and the 16-mission journey home to
Hiigara is "the search for a good basis" (Strang, Section 8.3), ending in the
mission "The Victory of Orthogonality" (Strang, Section 7.4).

THE IRON RULES. Short because they must be memorized, not because unimportant:

1. GAMING FIRST. The first five minutes feel like commanding a fleet, never like a
   textbook. The math is the physics of the world, never announced.
2. TWO PLAYERS, ONE SCREEN. Baseline hardware is what every home has:
   Player 1 (Pilot) = keyboard. Player 2 (Navigator) = mouse.
   The game must be fully winnable with only these. Joystick (Thrustmaster
   T16000M) and Xbox controller are optional later additions behind the input
   abstraction — they map onto the same logical actions, so adding them touches
   zero game logic.
3. NO PENALTIES. Wrong answers never destroy ships. The narrator ("Fleet
   Intelligence") explains gently and the player tries again.
4. NO INVENTED MATH. All mathematical statements shown to the player come from
   "Introduction to Linear Algebra" (Strang, 6th edition) and its Solution Manual,
   supplied by the project owner via copy+paste and stored in content/ files. All
   numeric CHECKING is computed live by NumPy at runtime — never by a stored
   answer (see "NumPy is the Referee", Part 6). The worked examples in this
   document use placeholder numbers; each will be replaced by the corresponding
   example from the book when that chapter's text is pasted in.
5. NO "UNDERSTANDING MODE". That was Descent QED's gimmick. This game's teaching
   happens through the mechanics themselves.
6. ENGINE: real-time programmatic vector graphics in modern OpenGL — a real-time
   Manim, not a Doom clone. No Panda3D, no Ursina.
7. SCOPE: fleets of at most ~20 ships, each individually meaningful. No
   pathfinding (space is empty; straight lines work). Pulse-based pacing. Ship
   something lovable.
8. THIS GAME IS BASE CAMP, not one mountain: linear algebra is the camp from which
   every Peak Together peak is climbed. (Bonus lore only: the open problem of the
   matrix multiplication exponent — is $\omega = 2$?)

---------------------------------------------------------------------------------
PART 1 — THE MATHEMATICAL WORLD MODEL
---------------------------------------------------------------------------------

Everything in the game reduces to TWO MATRICES THAT SHARE THEIR COLUMNS. This is
the deepest design decision in the project, so here it is made precise.

Every ship in your fleet is simultaneously:

(a) A POSITION IN SPACE. Ship $j$ has position $p_j \in \mathbb{R}^3$, measured
from the Mothership, which sits at the origin $(0,0,0)$ — Homeworld already made
the Mothership immovable in the campaign, so this is canon-friendly. Stacking the
positions as columns gives the FORMATION MATRIX $P$, of size $3 \times n$:

$$P = \begin{bmatrix} p_1 & p_2 & \cdots & p_n \end{bmatrix}$$

(each $p_j$ is a column of 3 numbers: the x, y, z of ship $j$).

(b) A CAPABILITY SIGNATURE. Ship $j$ has a signature $a_j \in \mathbb{R}^m$, a
vector of tactical output channels. Stacking them as columns gives the FLEET
MATRIX $A$, of size $m \times n$:

$$A = \begin{bmatrix} a_1 & a_2 & \cdots & a_n \end{bmatrix}$$

SIGNATURE SPACE has $m = 6$ fixed, named channels, in this order:
Kinetic (K), Beam (B), Missile (M), Sensor (S), Jamming (J), Utility (U).
Every ship class has a small-integer base signature, chosen small so that a player
can do the arithmetic in their head, book-style. The starting roster (each
signature is a column vector of 6 numbers in channel order K,B,M,S,J,U):

- Fighter:            $(2, 0, 0, 1, 0, 0)^T$
- Beam Corvette:      $(0, 3, 0, 1, 0, 0)^T$
- Missile Frigate:    $(0, 0, 4, 1, 0, 0)^T$
- Transpose Scout:    $(0, 0, 0, 3, 0, 0)^T$
- Jamming Corvette:   $(0, 0, 0, 1, 3, 0)^T$
- Salvage Corvette:   $(0, 0, 0, 1, 0, 2)^T$
- Resource Collector: $(0, 0, 0, 0, 0, 3)^T$
- Elimination Corvette, Permutation Frigate, Inverse Cruiser: special-action ships
  (Parts 2.5, 2.6), signatures mostly Sensor/Utility.

WHY TWO MATRICES? Because the two players ARE the two matrices. The Pilot lives
inside $P$: ships as objects in 3D space, formations as geometry, volumes, angles
— THE COLUMN PICTURE DRAWN IN THE WORLD. The Navigator lives inside $A$ (and
inside whatever mission matrix is active): a console of numbers, ranks, residuals
— THE ROW PICTURE, THE ALGEBRA. Strang's signature pedagogy — every fact shown
twice, once as geometry and once as algebra — is implemented here as two human
beings who each see only one of the pictures and must TALK to win. The Navigator
says "column three is the sum of columns one and two"; the Pilot looks up and sees
the third beacon lying in the plane of the first two. That conversation is the
product.

THE FLOATING-POINT DOCTRINE. The book's examples are exact integers, but live
gameplay drifts continuously, so EVERY structural test in the engine uses
tolerances, never equality:

- Rank: count singular values with $\sigma_i > 10^{-6} \sigma_1$ (never
  row-reduce floating-point numbers to test rank).
- "Is this ship's course in the nullspace?": test
  $\| A x \| < \varepsilon \, \|A\| \, \|x\|$, and expose the MAGNITUDE of
  $\|Ax\|$ to gameplay as an analog alarm meter rather than a binary
  caught/not-caught (see 2.7 — this turns a numerical necessity into better game
  design).
- "Is the gate singular?": compare $|\det|$ against a required volume threshold,
  displayed as a gauge (see 2.10).

This doctrine matters doubly here: the project owner cannot verify math by hand,
so the engine must never contain a hand-derived answer that could silently be
wrong. Setups come from the book; verdicts come from numpy.linalg at runtime.

---------------------------------------------------------------------------------
PART 2 — THE MECHANICS, WORKED TO IMPLEMENTATION DEPTH
---------------------------------------------------------------------------------

Each mechanic follows the same skeleton: the fiction, the exact mathematics, the
exact gameplay loop, a small worked example, the implementation, and what appears
on screen.

=== 2.1 MOVEMENT — LINEAR COMBINATION FLIGHT ORDERS (Strang Section 1.1) ===

FICTION. Fleet drives don't take free waypoints; they take "combination orders"
built from calibrated "engine vectors" — thrust programs recovered from the
ruined Archive.

THE MATH. The fleet's unlocked engine vectors $e_1, e_2, \ldots \in \mathbb{R}^3$
span the reachable space. An order is a choice of scalars; the destination is the
linear combination $d = c_1 e_1 + c_2 e_2 + \cdots$. At game start only
$e_1 = (1,0,0)$ and $e_2 = (0,1,0)$ are unlocked: THE FLEET CAN ONLY MOVE WITHIN A
PLANE, and the players feel this as a hard physical fact long before anyone says
the word "span."

THE GAMEPLAY. The Navigator drags coefficient sliders (or types values) on the
console; as she drags, the Pilot's 3D view draws the construction live: the arrow
$c_1 e_1$ from the squad's position, then $c_2 e_2$ appended head-to-tail, the
dashed parallelogram completing, the ghost-destination glowing at the tip. The
Pilot confirms with the keyboard and the squad flies. A toggle chooses COMPONENT
FLIGHT (fly the two legs) or DIAGONAL FLIGHT (fly the resultant). Fuel makes the
triangle inequality a lived economy: component flight costs
$|c_1| \|e_1\| + |c_2| \|e_2\|$, diagonal flight costs $\|c_1 e_1 + c_2 e_2\|$,
and

$$\|v + w\| \le \|v\| + \|w\|$$

means the diagonal is ALWAYS cheaper or equal — players discover a theorem as a
fuel-saving trick. Concrete: order $(3,4)$ with unit axis engines: legs cost $7$,
diagonal costs $5$. Separately, the Pilot has continuous low-power THRUSTER TRIM
on the keyboard (small expensive nudges) so that flying feels alive between
orders; trim is deliberately too weak to cross the map, so combinations remain the
real transport.

WORKED EXAMPLE (Mission 3, "The Plane of Refugees"). Refugee pods sit at
$(3, 2, 4)$. Unlocked engines: $e_1 = (1,0,0)$, $e_2 = (0,1,0)$. Every combination
has third coordinate zero — the pods are physically unreachable, and the Pilot can
SEE the whole fleet imprisoned in a glowing plane while the pods float above it.
Research unlocks $e_3 = (0,0,1)$; the order $3 e_1 + 2 e_2 + 4 e_3$ reaches the
pods. Lesson delivered by rescue, not by lecture: INDEPENDENCE = FREEDOM OF
MOVEMENT; SPAN = EVERYWHERE YOU CAN EVER GO.

IMPLEMENTATION. Destination preview is one line: d = E @ c, where E is the
$3 \times k$ matrix of engine columns and c the coefficient vector. Reachability
warnings: numpy.linalg.lstsq(E, target) — if the residual is large, the target is
off-span, and Fleet Intelligence says so AND shows the closest reachable point
(the projection — quietly foreshadowing Section 4.2).

=== 2.2 HARVESTING — DOT PRODUCTS (Strang Section 1.2) ===

FICTION. Resource dust streams through space with a local flow field; a
collector's intake scoop must face into the stream.

THE MATH AND GAMEPLAY. The dust cloud carries a flow vector $f$ (drawn as drifting
particle streaks, so the Pilot can SEE the direction). The collector's intake axis
is a unit vector $u$ set by the Pilot's rotation keys. Harvest rate per pulse is

$$\text{rate} = \rho \cdot \max(0, \; f \cdot u) = \rho \, \|f\| \cos\theta
\quad (\text{clamped at } 0),$$

so perfectly aligned harvests fully, $60°$ off harvests half (because
$\cos 60° = 0.5$), perpendicular harvests nothing, and facing away harvests
nothing (the clamp — a ramp function the endgame will one day rename ReLU). The
Navigator's console shows the live number $f \cdot u$ and the angle; she calls
corrections ("you're at seventy degrees, pitch down") while the Pilot flies by
feel. The couple converges on the maximum together — one reading algebra, one
reading geometry. That's the whole game's DNA in the gentlest mechanic, which is
why it's Mission 2.

IMPLEMENTATION. rate = rho * max(0.0, f @ u). One line. The engine renders $f$ as
particle drift and $u$ as an arrow on the collector; the angle arc is drawn
between them.

=== 2.3 COMBAT — STRIKE GROUPS SOLVE $Ax = b$ (Strang Ch. 1–2, Section 4.3) ===

FICTION. Taiidan shields are layered: each layer absorbs one kind of output.
Breaking a shield means delivering a PRECISE RECIPE of damage, not maximum damage.

THE MATH. A shield is a requirement vector $b \in \mathbb{R}^m$ in signature
space. A strike group of ships with signature columns $a_1, \ldots, a_k$ forms the
group matrix $A_g$ (size $m \times k$). The Navigator assigns each ship a THROTTLE
$x_j \in [0, x_{\max}]$; the delivered blow per pulse is $A_g x$. The shield
falls when the residual is small:

$$\| b - A_g x \| < \varepsilon .$$

Three regimes, all real linear algebra and all distinct gameplay:

1. UNIQUE SOLUTION — the group is exactly adequate; there is one right throttle
   setting; finding it is the puzzle.
2. NO SOLUTION ($b$ outside the column space $C(A_g)$) — NO throttles will ever
   work. Fleet Intelligence: "Admiral, that target lies outside our column space.
   Recommend an independent vessel." The console offers the LEAST-SQUARES STRIKE:
   the $\hat{x}$ minimizing $\| b - A_g \hat{x} \|$, which knocks the shield down
   to its irreducible remainder $\|e\|$, with the error vector
   $e = b - A_g \hat{x}$ rendered as a glowing bar of "channels we simply do not
   possess" — a partial victory that TEACHES PROJECTION and motivates building the
   missing ship class (feeding directly into 2.4).
3. INFINITELY MANY SOLUTIONS (dependent columns) — the console shows a free
   slider: a whole line of valid throttle settings, and the cheapest one (smallest
   $\|x\|_1$, i.e., least total ammunition) is the smart pick. Special solutions
   become ammo economy.

THE TWO PICTURES IN COMBAT. The Pilot sees COLUMNS: each firing ship pours its
colored contribution into the target. The Navigator sees ROWS: each shield LAYER
is one equation, one row, one draining bar — the kinetic row, the beam row, the
missile row. Column picture and row picture of the same $Ax = b$, split across two
humans in real time.

WORKED EXAMPLE. Channels (K, B) only. Group: two Fighters merged as
$a_1 = (2, 0)$ per throttle unit, one Beam Corvette $a_2 = (1, 3)$. Shield
$b = (7, 6)$. Solve $x_1 a_1 + x_2 a_2 = b$ row by row.
Beam row: $3 x_2 = 6$, therefore $x_2 = 2$.
Kinetic row: $2 x_1 + 1 \cdot 2 = 7$, therefore $x_1 = 2.5$.
The Navigator solves it exactly like a book exercise, back substitution and all —
under fire, with her partner holding the firing position.

IMPLEMENTATION. Verdict: numpy.linalg.norm(b - Ag @ x) < eps. Least-squares
option: numpy.linalg.lstsq(Ag, b). Solvability check: compare
numpy.linalg.matrix_rank(Ag) with the rank of the augmented matrix
numpy.column_stack([Ag, b]) (both with the tolerance doctrine) — rank of augmented
vs. unaugmented matrix, straight from Chapter 2, deciding in code whether the game
even offers an exact solution.

=== 2.4 THE FLEET ECONOMY — RANK AND $A = CR$ (Strang Sections 1.3–1.4) ===

FICTION. The Taiidan Analyst catalogs your fleet. What matters strategically is
not how many ships you own but how many KINDS of blow you can strike.

THE MATH. The set of shields you can EVER break exactly is precisely the column
space $C(A)$ of the full fleet matrix. Adding a ship whose signature is a
combination of existing columns does not enlarge $C(A)$ — CAPABILITY IS RANK. But
dependent ships are not useless: they raise THROUGHPUT (you can push more total
output per pulse, since each throttle is capped at $x_{\max}$). This is the honest
mathematical distinction — the column space says what is reachable, magnitudes say
how fast — turned into the game's central economic tension: RANK BUYS NEW
POSSIBILITIES, COPIES BUY SPEED. The build screen's headline number is
"Fleet Rank: r / 6", and raising it is how the campaign paces power.

$A = CR$ ON THE CONSOLE. At any moment the Navigator can factor the fleet:
$C$ = the first independent "prototype" ships, $R$ = the recipe matrix expressing
every ship as a combination of prototypes. Example with 2 channels: columns
$a_1 = (2, 0)$, $a_2 = (1, 3)$, $a_3 = (3, 3)$. The console flags
$a_3 = a_1 + a_2$, and (reading each matrix column by column):

$$A = \begin{bmatrix} 2 & 1 & 3 \\ 0 & 3 & 3 \end{bmatrix}
= \begin{bmatrix} 2 & 1 \\ 0 & 3 \end{bmatrix}
\begin{bmatrix} 1 & 0 & 1 \\ 0 & 1 & 1 \end{bmatrix} = C R .$$

(Here $A$ is 2-by-3 with columns $(2,0)$, $(1,3)$, $(3,3)$; $C$ is 2-by-2 with
columns $(2,0)$ and $(1,3)$; $R$ is 2-by-3 with columns $(1,0)$, $(0,1)$,
$(1,1)$.) Reading the columns of $R$ IS reading the fleet's dependency structure:
the third column of $R$ being $(1,1)$ says exactly "ship 3 = 1 of prototype 1 plus
1 of prototype 2."

When a Salvage Corvette tows in a captured enemy ship (a new column), the dramatic
beat is a sensor sweep and one question: DID THE RANK GO UP? If yes — fanfare, new
capability, new shields become breakable. If no — no penalty, the ship joins as
throughput, and Fleet Intelligence notes, kindly, that its signature already lay
in our span. Over sixteen missions the player develops a REFLEX for independence,
which is the entire pedagogical ambition of Chapter 1.

IMPLEMENTATION. Rank via SVD tolerance (Part 1). $C$ and $R$ via pivot-column
selection on a rounded copy for display, but the VERDICT (did rank increase)
always via singular values on the true floats.

=== 2.5 THE MINEFIELD — ELIMINATION AS PHYSICAL ACTION (Strang Ch. 2) ===

FICTION (Mission 5). A derelict minefield is governed by control pylons.
Broadcasting the correct disarm frequencies shuts it down; the frequencies are the
solution of the pylons' control system $A x = b$.

THE GAMEPLAY — this is the set piece that makes elimination PHYSICAL. The
Navigator sees the augmented matrix $[\, A \mid b \,]$ on her console — three
rows, one per pylon, small book integers. To perform the row operation
$\text{row}_2 \leftarrow \text{row}_2 - \ell \cdot \text{row}_1$, she selects the
multiplier $\ell$; but the operation only executes when the Pilot physically
positions the ELIMINATION CORVETTE on the line between pylon 1 and pylon 2 (it
acts as the conduit). When the operation lands, a visible bank of mines POWERS
DOWN — a zero has appeared below the pivot, and the player can see the zero as a
dark lane through the field. If a pivot position holds a zero (dead pylon), the
PERMUTATION FRIGATE must physically tow two pylons past each other — a row
exchange the whole screen can watch, and it is exactly as absurd and delightful as
it sounds. When the matrix reaches upper triangular form $U$, the Navigator
back-substitutes from the bottom row up, entering $x_3$, then $x_2$, then $x_1$;
each correct frequency opens one ring of the field. A wrong broadcast makes the
field flicker and reset — no losses, and the console highlights the row where the
residual is largest, i.e., WHICH EQUATION YOU ARE VIOLATING MOST.

The multipliers $\ell$ the Navigator used are quietly collected in a
lower-triangular record — and two missions later (Mission 7, "Asteroid Lanes"),
the game reveals she has been building $L$ all along: THE PASSAGE THROUGH THE
FIELD WAS LITERALLY $A = L U$, the elimination itself stored as a matrix. The Key
of Elimination is this realization made into a relic.

IMPLEMENTATION. The row operations are integer operations on a small displayed
matrix; the final verdict on the player's $x$ is norm(A @ x - b) < eps on the true
system. The mission file stores $A$ and $b$ taken verbatim from a book exercise
whose solution appears in the Solution Manual, so the difficulty and the numbers
are professor-calibrated, not AI-invented.

=== 2.6 THE TRAP — INVERSES (Strang Section 2.5) ===

FICTION (Mission 6). An enemy gate scrambles the strike group: every ship's
position is hit by a known matrix $E$ (the gate's field, which the Transpose Scout
measured on the way in). Formation destroyed; the exit requires the original
formation.

THE MATH AND GAMEPLAY. Positions became $E p_j$. The fix is to fly back through a
counter-field configured to $E^{-1}$, restoring $E^{-1}(E p_j) = p_j$. The
Navigator computes $E^{-1}$ on the console — for the mission's 2-by-2 or 3-by-3
book matrix, by the augmented method $[\, E \mid I \,] \to [\, I \mid E^{-1} \,]$,
reusing the exact row-operation console from Mission 5 (Gauss–Jordan as a SECOND
USE OF A TOOL THE PLAYER ALREADY LOVES — this is how you teach without lecturing).
The INVERSE CRUISER projects the counter-field; if the Navigator's matrix is
right, the formation visibly un-scrambles, ship by ship, a genuinely satisfying
animation (each ship flies the straight line from $E p$ back to $p$). If $E$ is
singular — a later, crueler gate — no inverse exists: two different formations
were crushed onto the same image, information was destroyed, and the mission must
be solved another way. SINGULAR = INFORMATION LOST becomes something the player
has WATCHED HAPPEN TO THEIR OWN SHIPS.

IMPLEMENTATION. numpy.linalg.inv for the verdict; numpy.linalg.det and condition
checks to decide whether to run the "singular gate" story branch.

=== 2.7 STEALTH — NULLSPACE CLOAKING (Strang Sections 3.2–3.4) — THE CROWN JEWEL ===

FICTION (Mission 8, "Ghost Fleet"). The Taiidan sensor grid is a battery of
stations. Each station reads one linear measurement of a ship's position. A ship
that all stations read as zero DOES NOT EXIST to the grid.

THE MATH. Station $i$ has scan vector $a_i^T$ (a row); the grid is the matrix $A$
(size $k \times 3$, one row per station); the grid's reading of a ship at position
$p$ (relative to the grid's focal origin) is the vector $A p$ (one number per
station). The ship is invisible exactly when

$$A p = 0 \iff p \in N(A),$$

the nullspace. Now rank–nullity, $\dim N(A) = 3 - r$, stops being a formula and
becomes THE GEOMETRY OF WHERE YOU CAN HIDE:

- Grid rank 3 --> nullspace is only the zero vector --> NO stealth is possible.
- Grid rank 2 --> the nullspace is a LINE — a single narrow invisible corridor.
- Grid rank 1 --> a whole invisible PLANE.

And therefore the tactical verb: JAMMING OR DESTROYING A STATION DELETES A ROW OF
$A$, which can drop the rank, which GROWS THE NULLSPACE BY A WHOLE DIMENSION. The
Navigator studies $A$ and answers the only question that matters: WHICH station's
row is making the corridor thin — and the Pilot goes and kills exactly that one.

WORKED EXAMPLE. Stations $a_1^T = (1, 1, 0)$ and $a_2^T = (0, 1, 1)$, so

$$A = \begin{bmatrix} 1 & 1 & 0 \\ 0 & 1 & 1 \end{bmatrix}$$

(2 rows = 2 stations). Rank 2, so the nullspace is a line, spanned by
$(1, -1, 1)$. Check both rows: $1 - 1 + 0 = 0$ and $0 - 1 + 1 = 0$. The Pilot sees
a single glowing safe line through the grid in direction $(1, -1, 1)$. Jam
station 2 (delete row 2) and the nullspace blooms into the plane $x + y = 0$ — the
safe line visibly UNFOLDS INTO A SAFE WALL, one of the best visual moments in the
game.

THE ALARM IS THE RESIDUAL NORM. Ships never trip a binary alarm; the grid's
suspicion meter fills at a rate proportional to $\|A p\|$. Drift slightly off the
corridor and the meter creeps; the Navigator reads the per-station values (the
components of the vector $A p$ — WHICH EQUATION YOU ARE VIOLATING) and calls the
correction axis; the Pilot trims. This is the floating-point doctrine promoted
into co-op gameplay: the tolerance band IS the difficulty setting.

SPOOFING = THE COMPLETE SOLUTION $x = x_p + x_n$. The mission's climax: a
checkpoint demands the grid read the signature of a scheduled convoy — the fleet
must hold $A p = b$ with $b \neq 0$. The solution set is not a subspace but the
AFFINE set

$$p = p_{\text{particular}} + n, \quad n \in N(A):$$

one particular spoof position the Navigator computes, PLUS free drift along
nullspace directions — which means the Pilot can dodge patrol ships WHILE the
sensors keep reading exactly $b$, provided every dodge is a nullspace move. "Hold
the reading while dodging" is the complete solution of a linear system, played
with the hands.

IMPLEMENTATION. Safe-region rendering: numpy.linalg.svd(A) --> the right singular
vectors whose singular values are (near) zero span $N(A)$; render as line/plane.
Alarm: alarm_rate = k * norm(A @ p) per ship per pulse. Particular solution:
lstsq(A, b).

=== 2.8 FORMATIONS — THE GRAM MATRIX AND GRAM–SCHMIDT (Strang Section 4.4) ===

FICTION. Ships flying at bad relative angles foul each other's firing arcs and
sensor cones.

THE MATH. For a squad with offset directions $q_1, \ldots, q_k$ (unit vectors from
squad center, stacked as columns of $Q$), interference is defined through the GRAM
MATRIX $G = Q^T Q$: total interference $= \sum_{i \neq j} (q_i \cdot q_j)^2$,
i.e., the squared off-diagonal mass of $G$. Perfect formation means $G = I$:
ORTHONORMAL COLUMNS, zero interference, and the game grants the orthogonality
bonus (full damage, full sensor coverage) — orthogonal columns don't waste each
other, which is not flavor text but the literal content of Section 4.4.

THE GRAM–SCHMIDT DRILL. The Navigator fires the order (mathematician-named, per
Peak Together tradition) and the squad executes the algorithm PHYSICALLY, one ship
at a time, visibly: ship 2 subtracts its projection onto ship 1 —

$$q_2 \leftarrow q_2 - \frac{q_1 \cdot q_2}{q_1 \cdot q_1} \, q_1$$

— sliding along the drawn dashed projection line while the subtracted component
glows and fades; then ship 3 subtracts its projections onto both predecessors; and
so on. And here the game teaches something most lecture courses fumble: WHY $R$ IN
$A = Q R$ IS UPPER TRIANGULAR. Because ship $k$ only ever adjusted itself relative
to ships $1$ through $k-1$ — later ships never touched earlier ones. The
triangularity of $R$ is VISIBLE IN THE CHOREOGRAPHY. The record of the drill's
moves is displayed as $R$; final formation = $Q$; original ragged squad = $A$; the
console shows $A = Q R$ assembled from what the player just watched happen.

Tiny example: $q_1 = (1, 0, 0)$, raw $q_2 = (1, 1, 0)$. Projection of $q_2$ onto
$q_1$ is $(1, 0, 0)$; subtracting gives the new $q_2 = (0, 1, 0)$. The ship slides
one unit sideways and the right angle appears.

MISSION 11 ("The Narrow Corridor") makes it mandatory: the Mothership physically
does not fit through unless the escort's $G$ is within tolerance of $I$.

IMPLEMENTATION. Interference per pulse: G = Q.T @ Q;
penalty = ((G - np.eye(k))**2).sum(). Drill animation: run classical Gram–Schmidt
stepwise, interpolating ship positions between steps. Verdict via
numpy.linalg.qr comparison under tolerance.

=== 2.9 LEAST-SQUARES NAVIGATION (Strang Sections 4.2–4.3) ===

FICTION (Mission 10, "Nebula of Noise"). The nebula wrecks sensors; position pings
are noisy; the Mothership must fly the best straight trajectory through hostile
dust that thins near the true channel.

THE MATH AND GAMEPLAY. Pings arrive as pairs $(t_i, y_i)$. Fitting the trajectory
$y = C + D t$ means solving the unsolvable tall system $A \hat{x} \approx b$ where
the columns of $A$ are all-ones and the times $t_i$, via the normal equations
$A^T A \hat{x} = A^T b$. The game uses STRANG'S OWN CANONICAL EXAMPLE (the one he
has taught for fifty years): pings $(0, 6)$, $(1, 0)$, $(2, 0)$ give

$$A = \begin{bmatrix} 1 & 0 \\ 1 & 1 \\ 1 & 2 \end{bmatrix}, \quad
b = \begin{bmatrix} 6 \\ 0 \\ 0 \end{bmatrix}, \quad
A^T A = \begin{bmatrix} 3 & 3 \\ 3 & 5 \end{bmatrix}, \quad
A^T b = \begin{bmatrix} 6 \\ 0 \end{bmatrix}$$

and solving $A^T A \hat{x} = A^T b$ gives $\hat{x} = (C, D) = (5, -3)$: best line
$y = 5 - 3t$. On screen: the pings as floating debris-lights, the fitted line as
the projected course, and the ERROR VECTOR DRAWN PERPENDICULAR — visibly
orthogonal to the fit, because $e = b - A \hat{x}$ is perpendicular to the column
space, and the renderer draws exactly that right angle. Hull damage taken in the
nebula is proportional to $\|e\|$, so a better fit is FELT IN THE HULL. The
Navigator may exclude pings she distrusts (deleting rows) and watch the fit and
the error respond — outlier sensitivity discovered by play. The same projection
machinery powers the LEAST-SQUARES FIRING SOLUTION from 2.3 regime (2): one
mathematical idea, two weapons systems.

IMPLEMENTATION. x_hat, *rest = numpy.linalg.lstsq(A, b); error e = b - A @ x_hat;
render e as a perpendicular glowing segment.

=== 2.10 HYPERSPACE GATES — THE DETERMINANT AS VOLUME (Strang Ch. 5) ===

FICTION. A jump bubble is generated by three escort frigates; the bubble is the
parallelepiped they span from the gate focus, and physics only cares about one
number.

THE MATH AND GAMEPLAY. Frigates at positions $v_1, v_2, v_3$ relative to the gate
focus span the box with volume $| \det [\, v_1 \; v_2 \; v_3 \,] |$ (the 3-by-3
matrix whose columns are the three frigate positions). The jump requires
$|\det| \ge V_{\min}$ (the Mothership must fit inside). The wireframe box is drawn
live around the fleet, with the volume gauge on the console. Now the
determinant's PROPERTIES become gate-operation facts the players learn with their
hands: exchanging two frigates flips the sign (the mesh visibly turns inside-out
through zero — orientation reversal rendered as geometry); pushing one frigate
twice as far doubles the volume (linearity in each column); and if the three
frigates drift toward a common plane, $\det \to 0$ and the bubble AUDIBLY AND
VISIBLY FLATTENS — singularity as a felt emergency.

WORKED EXAMPLE. $v_1 = (2, 0, 0)$, $v_2 = (0, 3, 0)$, $v_3 = (1, 1, 1)$:

$$\det \begin{bmatrix} 2 & 0 & 1 \\ 0 & 3 & 1 \\ 0 & 0 & 1 \end{bmatrix} = 6 .$$

(Columns are $v_1$, $v_2$, $v_3$.) Enemy tractor beams drag $v_3$ toward
$(1, 1, 0)$: all three frigates now lie in the plane $z = 0$, the determinant
slides to $0$, and the box collapses like a tent. MISSION 12 ("The Collapsing
Gate") is exactly this fight: the Pilot repositions frigates under fire while the
Navigator watches $\det$ and calls which frigate to move to fatten the volume
fastest.

IMPLEMENTATION. numpy.linalg.det on a 3-by-3 each pulse; the spanned box is a
standard forge primitive (SpannedBox), also reused to visualize independence in
Act I (three dependent position vectors span a flat box — the SAME primitive
quietly teaching Chapter 1 and Chapter 5).

=== 2.11 EIGENVECTORS I — DOCKING AND THE SWARM (Strang Sections 6.1–6.2) ===

DOCKING (Mission 13 climax). An ancient relic tumbles: within its grip zone, every
pulse applies a fixed rotation $T$ (axis $w$, angle $\theta$) to a ship's relative
position: $p \mapsto T p$. A genuine 3D rotation has exactly one real eigenvector
— its axis, with eigenvalue $1$. Approach along any other line and you are dragged
into a spiral (the game just iterates $p \mapsto T p$ and the Pilot feels the
drag); approach along $w$ and $T w = w$: your ship rolls about its own nose but
STAYS ON COURSE. FINDING THE CALM AXIS OF A SPINNING THING = FINDING THE
EIGENVECTOR, experienced in the hands before it is named. The Navigator extracts
$T$ from the scout's readings, runs the eigen-decomposition, and marks the one
real eigendirection as the approach corridor; the docking port sits at the axis
pole. The Key of Resonance is inside.

THE SWARM (Mission 13 main phase). Enemy swarm mass redistributes between two
nesting grounds each pulse by a fixed positive matrix:

$$x_{k+1} = A x_k, \qquad
A = \begin{bmatrix} 0.8 & 0.3 \\ 0.2 & 0.7 \end{bmatrix}.$$

(Here $x_k$ is the 2-vector of swarm mass at ground 1 and ground 2 after wave
$k$.) The dominant eigenvalue is $1$ with eigenvector proportional to $(3, 2)$:
no matter the initial distribution, the swarm converges to a 60/40 split — THE
GAME ITSELF IS RUNNING THE POWER METHOD, wave after wave, so the Navigator's
prediction is verifiable by simply watching. The winning play is to pre-position
the ambush at the 60% ground instead of chasing waves. Deeper tactical layer:
damage inflicted along eigendirections with $|\lambda| < 1$ decays (the swarm
recovers between waves); damage aligned with the dominant eigenvector compounds.
PREDICTION BEATS FIREPOWER, which is the emotional thesis of Chapter 6.

IMPLEMENTATION. numpy.linalg.eig; select the real eigenvector for docking (the one
with abs(eigenvalue.imag) < tol); the swarm literally updates by x = A @ x per
wave, so simulation and lesson are the same code.

=== 2.12 EIGENVECTORS II — SHIELD HARMONICS (Strang Sections 6.3–6.4) ===

FICTION (Mission 14). The Taiidan flagship's shield is not a wall but a RESPONSE:
it resists a strike from unit direction $d$ with strength

$$\text{resistance}(d) = d^T S d,$$

where $S$ is symmetric positive definite. THE SHIELD IS RENDERED AS THE ELLIPSOID
$x^T S x = 1$ — and this is the single most beautiful visual identity in the game,
because the ellipsoid's principal axes ARE the eigenvectors of $S$ and its
semi-axis lengths are $1 / \sqrt{\lambda_i}$: THE LONGEST AXIS OF THE GLOWING
SHIELD-ELLIPSOID POINTS EXACTLY ALONG THE WEAKEST EIGENDIRECTION. The Pilot can
SEE the vulnerability as shape; the Navigator diagonalizes $S = Q \Lambda Q^T$ on
the console to confirm it and calls the strike.

WORKED EXAMPLE.

$$S = \begin{bmatrix} 5 & 4 \\ 4 & 5 \end{bmatrix}$$

(2-by-2 symmetric: first column $(5, 4)$, second column $(4, 5)$). Eigenvalues:
$9$ and $1$. Eigenvectors: $(1, 1)$ for eigenvalue $9$, and $(1, -1)$ for
eigenvalue $1$ — orthogonal, as symmetry guarantees. Attacking along $(1, 1)$
meets resistance $9$; attacking along $(1, -1)$ meets resistance $1$ — a NINEFOLD
difference between looking at the shield and SEEING INTO IT (Strang's phrase for
the whole subject). Because $S$ is symmetric the eigenvectors are exactly
perpendicular — so the strike run is at a clean right angle to the shield's strong
axis, and the Gram–Schmidt-trained player already flies right angles by instinct.
Mid-fight, the flagship RE-TUNES $S$ (a new symmetric matrix); the ellipsoid
morphs; the couple re-solves under pressure.

IMPLEMENTATION. numpy.linalg.eigh (the symmetric-matrix routine — even our
function choice follows the book's structure); ellipsoid rendered by transforming
a unit wire-sphere by $Q \, \Lambda^{-1/2}$.

=== 2.13 SALVAGE REFIT — DETERMINING A MATRIX FROM ITS ACTION (Strang Ch. 8) ===

FICTION. Captured ships report signatures in ENEMY channel conventions. Refitting
requires the conversion matrix $M$ — which nobody hands you.

THE GAMEPLAY PUZZLE. The Navigator scans three reference objects whose true
signatures $y_1, y_2, y_3$ are known from the Archive, and reads the enemy-basis
values $x_1, x_2, x_3$. Since $M x_i = y_i$ for three independent probes, stacking
the probe vectors as columns of $X$ and $Y$ gives $M X = Y$, hence

$$M = Y X^{-1}$$

— A LINEAR TRANSFORMATION IS COMPLETELY DETERMINED BY WHAT IT DOES TO A BASIS,
which is the load-bearing idea of Chapter 8, here disguised as a salvage minigame.
Refit then converts every captured column, and 2.4's rank question ("did we gain
capability?") is asked IN OUR COORDINATES, as it must be.

IMPLEMENTATION. M = Y @ numpy.linalg.inv(X), guarded by the independence check on
the probes (rank of $X$) — if the Navigator picks dependent probes, the puzzle
honestly fails and Intelligence explains why three INDEPENDENT probes are needed.

=== 2.14 THE GUIDESTONE — THE SVD AS THE CAMPAIGN'S SOUL (Strang 7.1–7.2) ===

FICTION. The Guidestone, sole surviving fragment of the Knowledge Archive, is a
carved image of Hiigara — recovered RANK-DEFICIENT, a blur. Each mission's
Key-fragment restores one singular component.

THE MATH MADE EMOTIONAL. The true image is a 128-by-128 grayscale matrix $G$ with
singular value decomposition

$$G = \sum_i \sigma_i u_i v_i^T$$

(each term is: singular value $\sigma_i$ times column vector $u_i$ times the
transpose of column vector $v_i$ — a rank-1 matrix). After mission $k$ the game
displays the rank-$k$ partial sum

$$G_k = \sigma_1 u_1 v_1^T + \sigma_2 u_2 v_2^T + \cdots + \sigma_k u_k v_k^T,$$

computed LIVE by numpy.linalg.svd on the real image file. Sixteen missions,
sixteen singular values, and — because natural images concentrate energy in their
top singular values — rank 16 of a well-chosen 128-pixel image is genuinely
recognizable: THE PICTURE OF HOME LITERALLY COMES INTO FOCUS OVER THE COUPLE'S
MANY EVENINGS TOGETHER, and the campaign completion meter is the captured spectral
energy

$$\frac{\sigma_1^2 + \cdots + \sigma_k^2}{\sigma_1^2 + \cdots + \sigma_r^2}.$$

Progress bar, emotional arc, and low-rank approximation (Eckart–Young) are one
object.

MISSION 15 ("Transmit the Map Home"). The antenna's bandwidth is tiny. Sending
rank $k$ costs $k(m + n + 1)$ numbers versus $m \cdot n$ for the full image — the
console displays this exact tradeoff. For 128-by-128: rank 16 costs
$16 \times (128 + 128 + 1) = 4112$ numbers vs. $128 \times 128 = 16384$ — a real
compression ratio, from the real formula in Section 7.2. The Navigator chooses
$k$; transmission time scales with the cost; the Pilot must defend the antenna for
the whole transmission. HIGHER FIDELITY = LONGER SIEGE. The players argue about
how much of home is worth how much blood, and the argument IS rank selection.

=== 2.15 THE FINAL BOSS — DEATH BY DECOMPOSITION (Strang Ch. 7; Mission 16) ===

FICTION. The Emperor's flagship projects a warp field: every torpedo's velocity
$v$ is transformed to $A v$ mid-flight. Your shots curve away. The flagship cannot
be out-shot; it must be DECOMPOSED.

THE FIGHT, IN THREE PHASES MIRRORING $A = U \Sigma V^T$:

- PHASE 1 — BREAK $V^T$: destroy the input gyros. The pre-rotation dies; the
  residual warp becomes $U \Sigma$. Mechanically, until then, the Navigator
  computes aim corrections — to hit point $b$, fire toward $A^{-1} b$, with the
  Inverse Cruiser (2.6) projecting the corrected solution; every phase simplifies
  the correction she must compute.
- PHASE 2 — BREAK $\Sigma$: the amplifier cores, one per singular value, each
  stretching space by $\sigma_i$ along a principal axis (rendered as the unit
  sphere of space deformed into an ellipsoid — the same primitive as 2.12, because
  it is the same mathematics). Cores must fall in DECREASING order of $\sigma_i$:
  kill the biggest stretch first or its amplification feeds the others.
- PHASE 3 — BREAK $U$: only a pure rotation remains — and a pure rotation CANNOT
  STOP a shot fired along its axis. The killing blow travels along $u_1$, the
  first left singular vector: THE DIRECTION THE ENEMY AMPLIFIED MOST BECOMES, ONCE
  THE AMPLIFIERS ARE DEAD, THE STRAIGHT LINE TO ITS HEART.

As the flagship dies, the hyperspace ritual performs the same three steps on space
itself — rotate, stretch, rotate — the fleet jumps, and the fully restored
Guidestone dissolves into the real Hiigara filling the screen. Strang calls
orthogonal matrices "the winners in the end"; the mission is named for his
Section 7.4, and the music does what Adagio for Strings did in 1999.

---------------------------------------------------------------------------------
PART 3 — THE CAMPAIGN INDEX
---------------------------------------------------------------------------------

Sixteen missions, five acts; each act recovers one Key = one factorization; each
mission awards one singular value to the Guidestone. Mechanics referenced by
section number above; every mission's matrices and systems are instantiated from
book / solution-manual examples via the content pipeline (Part 6).

ACT I — EXILE. Key of Independence, $A = C R$ (Chapter 1).
  1. Kharak Burns — tutorial; mothership = origin; combination flight orders (2.1).
  2. First Contact — dot-product harvesting and aiming (2.2); first combat (2.3,
     unique-solution regime).
  3. The Plane of Refugees — span as prison; third engine vector as liberation (2.1).
  4. Salvage Run — dependence, rank, first $A = C R$ on the console (2.4);
     Guidestone's first shimmer.

ACT II — THE GAUNTLET. Key of Elimination, $A = L U$ (Chapters 2–3).
  5. Minefield — elimination as physical row operations; back substitution (2.5).
  6. The Trap — Gauss–Jordan inversion; the un-scrambling (2.6).
  7. Asteroid Lanes — dead pivots, Permutation Frigate row exchanges; the $L$
     reveal: $A = L U$ (2.5).
  8. Ghost Fleet — nullspace cloaking; jamming as rank surgery; spoofing as
     $x = x_p + x_n$ (2.7).

ACT III — THE BIG PICTURE. Key of Perpendicularity, $A = Q R$ (Chapters 3–5).
  9. The Karos Graveyard — the Navigator's console unlocks the full four-subspace
     display for the mission matrix — dimensions $r$, $n - r$, $r$, $m - r$
     live-updating; the Fundamental Theorem (row rank = column rank) delivered as
     a plot revelation by an ancient beacon.
 10. Nebula of Noise — least-squares trajectory and firing (2.9, 2.3).
 11. The Narrow Corridor — Gram–Schmidt drill; mandatory $G \approx I$ (2.8).
 12. The Collapsing Gate — determinant-volume gate under sabotage (2.10).

ACT IV — THE INNER WAR. Key of Resonance, $S = Q \Lambda Q^T$ (Chapter 6).
 13. The Swarm — power-method prediction; eigenvector docking climax (2.11).
 14. Shield Harmonics — the quadratic-form ellipsoid; strike along the weak
     eigenvector (2.12).

ACT V — HOMECOMING. The Master Key, $A = U \Sigma V^T$ (Chapter 7).
 15. Transmit the Map Home — rank-$k$ choice, compression-vs-siege tradeoff (2.14).
 16. The Victory of Orthogonality — the three-phase decomposition boss;
     homecoming (2.15).

Persistent fleet across all sixteen (accumulated ships = accumulated knowledge);
black-and-white still-image cutscenes with narration between missions,
Homeworld-fashion. Faction choice at campaign start — Kushan "Column" doctrine vs.
Taiidan "Row" doctrine — is cosmetic (UI accents, ship silhouettes), with one lore
payoff: the Act III beacon proves the two doctrines were always equal in strength,
because row rank equals column rank.

---------------------------------------------------------------------------------
PART 4 — CO-OP AND CONTROLS
---------------------------------------------------------------------------------

- PILOT (KEYBOARD): camera orbit / follow / ship-POV, thruster trim, ship and
  squad selection cycling, order confirmation, positioning ships for physical
  actions (conduits, corridors, strike runs, frigate placement). Never touches
  console widgets.
- NAVIGATOR (MOUSE): the console — fleet matrix grid, coefficient sliders,
  row-operation tools, throttle assignment, rank / det / eigen / SVD readouts,
  build & research, Big Picture overlay. Never moves the camera.
- ONE SCREEN: 3D viewport dominant; console as persistent right/bottom panel; Big
  Picture as a translucent toggle overlay. The device separation doubles as an
  architectural boundary (no input-routing ambiguity to debug).
- SOLO MODE = one human using both devices; zero special code.
- The helm module defines a frozen list of LOGICAL ACTIONS; keyboard and mouse
  mappers ship first; joystick and Xbox mappers are added later as new mapping
  files only (pyglet exposes all four device types on Windows), touching no game
  logic. Any device may drive either role.

---------------------------------------------------------------------------------
PART 5 — STORY AND TONE (COMPACT)
---------------------------------------------------------------------------------

The Knowledge Archive burned with Kharak. The ancient hyperspace core takes five
Keys — the five great factorizations, recovered act by act: $A = CR$, $A = LU$,
$A = QR$, $S = Q \Lambda Q^T$, $A = U \Sigma V^T$. The Guidestone sharpens by one
singular value per mission until home is legible. Fleet Intelligence narrates:
calm, warm, never punishing; all of its mathematical sentences originate from
content/ files sourced from Strang. Visual tone: deep-space black, glowing
wireframes, Homeworld's contemplative majesty rendered honestly by a vector
engine instead of imitated with textures.

---------------------------------------------------------------------------------
PART 6 — ENGINEERING DOCTRINE
---------------------------------------------------------------------------------

STACK: Python 3.12+; NumPy (the math AND the curriculum — svd, qr, eig, eigh,
det, lstsq, inv, matrix_rank are the game's mechanics); moderngl (OpenGL 3.3+
core, shader-based glow and additive blending); pyglet (window, keyboard/mouse
now, joystick/gamepad later, audio); Pillow (Guidestone image, glyph atlas).
Nothing else without cause.

SIMULATION: fixed-timestep logic pulses at 10 Hz, rendering at 60 fps with
interpolation. Deliberate Homeworld pacing — and pulses give the couple time to
talk, which is the design's beating heart. Fully deterministic under a visible
seed, so any bug report is reproducible from a description.

REPOSITORY:

```
basecamp/
├── app.py            # entry point; wiring only
├── run.bat           # double-click launcher
├── settings.json     # human-editable config
├── INTERFACES.md     # frozen module interfaces, versioned
├── forge/            # render engine: window, camera, VObject primitives
├── helm/             # logical actions + device mappers
├── fleet/            # simulation core: matrices P and A, pulses, orders, combat
├── campaign/         # mission runtime + data-driven mission files + Guidestone
├── bridge/           # Navigator console, Big Picture overlay, HUD
├── intel/            # narrator line selection & subtitle queue
├── audio/
└── content/          # book-sourced data: matrices, narrator text, missions, images
```

FROZEN-INTERFACE LAW: modules communicate only through signatures documented in
INTERFACES.md. Single-module work never changes an interface; interface changes
require explicit owner approval and a version bump. forge knows nothing about
ships; fleet knows nothing about pixels; bridge reads fleet state through
read-only snapshots and issues orders through the same queue the Pilot uses.

FORGE PRIMITIVE VOCABULARY (initial, frozen): Line, Arrow, DashedLine, Grid,
WireMesh, WireSphere, SpannedBox (parallelepiped of 2–3 vectors — serves Chapters
1 AND 5), Ellipsoid (unit sphere transformed by a matrix — serves 2.12 AND 2.15),
Trail, Label (billboarded text), ImagePanel (Guidestone). Every primitive is
constructed from NumPy arrays. This vocabulary is the "real-time Manim" and is
deliberately tiny.

NUMPY IS THE REFEREE (THE CONTENT PIPELINE):
1. The project owner pastes a book / solution-manual section to the current lead
   conversation.
2. It is distilled into a content/ file: narrator text as verbatim quotes with
   section citations; mission matrices and vectors copied from the book's OWN
   worked examples and solved exercises (so difficulty is professor-calibrated).
3. The engine stores only SETUPS, never answers. Every verdict — does $A_g x$
   reach $b$, is the course in $N(A)$, did the rank rise, is the gate singular —
   is computed at runtime by numpy.linalg under the tolerance doctrine of Part 1.
   Consequently no human ever needs to verify mathematics by hand, and no
   AI-invented "answer" can silently be wrong.

DEBUGGING-BY-DESCRIPTION DOCTRINE: every crash writes a full traceback to
crashlog.txt with a friendly on-screen notice; the window title always shows the
build version; F1 toggles a debug overlay (fps, pulse count, seed, fleet rank,
mission state); F12 saves a screenshot. The person running the game reports bugs
by pasting crashlog.txt and describing the screen — the game is built to make
that sufficient.

BUILD ORDER: (1) forge walking skeleton — window, camera, glowing grid, one arrow
drawn from the origin; (2) helm keyboard+mouse and fleet pulse core with three
ships as live columns; (3) Mission 1 end-to-end including narrator and first
Guidestone shimmer; (4) bridge console v1; (5) missions in order, each mission a
self-contained work package.

---------------------------------------------------------------------------------
PART 7 — DEFERRED (NOT IN v1.0; REQUIRES OWNER APPROVAL TO BEGIN)
---------------------------------------------------------------------------------

New Game+ frontier sectors for Chapters 8–10 (gate networks as linear
transformations; an enemy that trains by gradient descent; the couple training a
tiny neural-network autopilot — piecewise-linear functions, tying into Peak
Together's "the last things AI can't do"). Markov-matrix pirate patrols predicted
by the steady-state eigenvector. Condition number as a fleet "stability" stat.
Joystick / Xbox mapper files. Deeper faction asymmetry; multiplayer;
matrix-multiplication-exponent lore missions.

---------------------------------------------------------------------------------
END OF THE BIBLE. Next documents: the NEW TESTAMENT (deep design of forge, fleet,
and helm — the three hardest modules) and the APOCRYPHA (campaign + content
pipeline, bridge + Big Picture, Guidestone / intel subsystems).
---------------------------------------------------------------------------------
