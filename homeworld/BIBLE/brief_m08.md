MISSION BRIEF M8 (Gram–Schmidt: "The Narrow Corridor")

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
