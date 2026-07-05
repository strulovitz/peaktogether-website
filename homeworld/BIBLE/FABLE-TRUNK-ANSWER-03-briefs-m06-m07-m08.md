The geometry act — the two escape theorems and the drill. DeepSeek: save as brief_m06.md, brief_m07.md, brief_m08.md.

FILE: brief_m06.md — MISSION BRIEF M6 (complete solution: "The Blockade Run")

BRIEF M6 — COMPLETE SOLUTION x = x_p + x_n (Canon M6, §3.3-3.4;
second half of Mission 8). File suggestion: m06_blockaderun.py
This is M5's sequel — read brief_m05.md first; reuse its sensor-grid
fiction and (ideally) its shell code as your starting point.

FICTION. The blockade now DEMANDS a crossing: supply pods must reach a
besieged station. The route must satisfy a hard constraint A x = b (the
corridor gate admits only ships arriving with a specific approach
velocity signature b — fiction: the gate's resonance), while the sensor
grid from M5 still watches. One particular solution gets you THROUGH;
nullspace drift keeps you FLEXIBLE around patrols.

THE GAME — one theorem as level design: EVERY safe route is
x = x_particular + (any nullspace drift). The console computes and
displays x_p (via referee.least_squares when consistent — check with
referee.is_solvable first) and the ghost headings from
referee.nullspace_basis. In SPACE: x_p is drawn as one solid golden
route-arrow through the gate; the nullspace line/plane from M5 glows
around it. The Navigator has a DRIFT slider (or two, if the nullspace
is 2D): x = x_p + t1*n1 + t2*n2, and the previewed route bends LIVE as
she drags — infinitely many safe paths, one structure, visibly a line/
plane of routes anchored on one particular arrow. Patrols force her to
pick nonzero drift; the Pilot flies the chosen route and handles timing.
Win: pods docked; end-card (content, cited): "One solution opens the
door. The nullspace is every way to walk through it."

BUILD NOTES. All verdicts referee-side: is_solvable, least_squares,
nullspace_basis, in_nullspace. The gate constraint A and b live in your
shell or mission content JSON — fresh context keys if you touch
snapshot.context. Ask DeepSeek: whatever M5's branch built (its shell
file name, its sensor helpers) — inherit, don't reinvent.

ACCEPTANCE. The player drags the drift slider back and forth, watching
one anchored family of routes sweep through space, and understands
"infinitely many solutions" as A SHAPE, not a phrase.

FILE: brief_m07.md — MISSION BRIEF M7 (the Fundamental Theorem: "The Karos Graveyard")

BRIEF M7 — THE BIG PICTURE AS A LITERAL STAR MAP (Canon M7, §3.5;
Mission 9). File suggestion: m07_karos.py
The most abstract canon entry — so be the MOST spatial. Everything is
regions, colors, and travel; the word "subspace" appears only in cited
end-cards.

FICTION. Karos: a graveyard region ruled by an ancient relay matrix A
(3x3, rank 2 — chosen so every subspace is visible in 3D). The relay
TELEPORTS: any ship at position x is beamed to A x. Four territories:
 - THE HIGHWAY (row space, dim r=2): a glowing plane in the fleet's
   half of the map. Motion here is "seen" by the relay.
 - THE SHADOW (nullspace, dim n-r=1): the line PERPENDICULAR to the
   highway (draw the right angle!). Ships here teleport to ZERO — the
   relay's maw at the origin. Danger and stealth in one geometry.
 - THE DESTINATION FIELD (column space, dim r=2): the plane on the far
   half where every teleport lands. Wrecks of ancient fleets litter it.
 - THE DEAD ZONE (left nullspace, dim m-r=1): perpendicular to the
   destination field; NOTHING can teleport there — cargo beacons in
   the dead zone are unreachable by relay and must be flown to by hand.

THE GAME. Recover four data cores, one per territory. Each retrieval
teaches its region by feel: highway cores teleport cleanly; the shadow
core must be grabbed by a ship whose position splits x = x_row + x_null
(console shows the split as two stacked arrows in space — projection
onto the highway); dead-zone core is unreachable by relay (attempted
beam visibly lands on the destination plane instead — the projection!),
so the Pilot flies it manually. Finale: the ancient beacon (Book VI's
plot revelation, content-cited): row rank = column rank — "the two
independent directions you fly are the two independent directions you
arrive." Dimensions r, n-r, r, m-r shown on the map corners as region
labels: 2, 1, 2, 1.

BUILD NOTES. Verdicts and bases from referee: rank, nullspace_basis
(for A and A^T — pass A.T for the left nullspace; row space basis =
column space of A^T). If you need an orthonormal basis helper, spec a
small referee addition rather than computing shell-side. The teleport
is a mini-game rule in your shell: an ORDER (reuse ApplyTransform with
matrix A? decide with Nir) or a "RELAY" button; animate the beam.
A suggestion: A = [[1,0,1],[0,1,1],[1,1,2]] (rank 2, nice integers) —
verify its subspaces with the referee before hardcoding labels.

ACCEPTANCE. A player can point at the four regions on screen and say
what each DOES (seen / swallowed / landing field / unreachable) —
without using one mathematical word.

FILE: brief_m08.md — MISSION BRIEF M8 (Gram–Schmidt: "The Narrow Corridor")

BRIEF M8 — GRAM-SCHMIDT FORMATION DRILL (Canon M8, §4.4; Mission 11).
File suggestion: m08_corridor.py

FICTION. A canyon of wrecks too narrow for the Mothership unless her
three escort frigates hold a PERFECT mutually-perpendicular, unit-
distance formation around her — overlapping fire arcs interfere;
orthogonal columns waste nothing. The ancient order is named the
GRAM-SCHMIDT DRILL (orders named for mathematicians — Peak Together
tradition).

THE GAME. The escorts' offsets from Mom are three columns a1, a2, a3
— ragged, oblique, wrong. THE DRILL RUNS AS A VISIBLE RITUAL, step by
step, slow enough to read (1-2 s per step, Pilot triggers each step
with ENTER):
 STEP 1: a1 shrinks/grows to unit length -> q1 (its column on the
   console normalizes simultaneously).
 STEP 2: from a2, a ghost arrow shows the PROJECTION onto q1 being
   SUBTRACTED (the projection arrow detaches and fades); the remainder
   swings perpendicular, then normalizes -> q2. The right angle marker
   flashes.
 STEP 3: a3 loses TWO ghost projections (onto q1 and q2), swings, and
   normalizes -> q3.
The ship physically FLIES each correction (ApplyTransform or per-ship
plans — decide with DeepSeek). Console shows Q forming column by
column and referee.gram_penalty(Q) falling to ~0 as a "FORMATION
INTERFERENCE" gauge. When the gauge hits green, the corridor gate
opens and the convoy threads it (win). Optional beat for the R of
A = QR: the console notes the recipe that rebuilds the old ragged
formation from the perfect one.
DEGENERATE CASE, handled kindly: if the Pilot parks two escorts in
nearly the same direction, step 2's remainder is ~zero — Fleet
Intelligence: "Two escorts share a direction; there is nothing
perpendicular left to make. Reposition one." (explain, never punish).

BUILD NOTES. GramSchmidtDrill order exists in orders.py — ask DeepSeek
whether sim implements it (instant snap?) and whether you should
choreograph the staged version shell-side instead (likely yes:
compute the steps ONCE from referee-sanctioned math — if referee lacks
a qr/gram_schmidt-steps helper, spec a small addition returning the
intermediate vectors; do NOT hand-roll projections in the shell).
Interference gauge = referee.gram_penalty. Angles/arcs: reuse M2's
angle-arc drawing if that branch built one.

ACCEPTANCE. The subtraction of the projection — the ghost arrow being
TAKEN AWAY — is the image the player remembers. If a tester describes
step 2 as "it removes the shadow it casts on the first one," ship it.

Say "continue" for M9, M10, M11 (least squares, the determinant gate emergency, and eigenvector docking). 🚀
