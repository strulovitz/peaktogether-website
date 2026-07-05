Act IV — prediction, resonance, and the enemy's coordinates. DeepSeek: save as brief_m12.md, brief_m13.md, brief_m14.md.

FILE: brief_m12.md — MISSION BRIEF M12 (eigen-dynamics: "The Swarm")

BRIEF M12 — EIGEN-PREDICTION OF SWARMS (Canon M12; Mission 13).
File suggestion: m12_swarm.py
Sequel in spirit to M11 (read brief_m11.md) — same math, now in TIME.

FICTION. Taiidan drone swarms are mindless repeaters: each wave's
displacement-from-hive evolves by the SAME rule every pulse,
x_{k+1} = A x_k. Firepower cannot outshoot them; PREDICTION beats
firepower. The eigendirections of A are prophecy: components along
|lambda| > 1 directions GROW (the swarm converges toward the dominant
eigenvector's line); components along |lambda| < 1 directions DIE
(safe harbors — the swarm cannot sustain presence there).

THE GAME — three waves, one deepening skill:
 - The swarm is drawn as many glowing motes, each stepping x -> A x
   per pulse (seeded spawn cloud). WATCH: whatever ragged shape it
   starts as, it smears onto ONE line through the hive — the dominant
   eigendirection, emerging live from raw dynamics. First "ohhh."
 - Navigator's console: M11's probe returns, now with FORECAST —
   pick direction x, and the console draws x, Ax, A^2 x, A^3 x as a
   fading chain of arrows (four referee-sanctioned multiplications,
   displayed, never trusted to the shell). Chains along the dominant
   axis stretch; chains in the safe harbor shrink to dots. She marks
   AMBUSH LINE (dominant axis) and SAFE HARBOR (decaying direction).
 - Pilot: parks the fleet in the safe harbor (drones thin out and
   starve there — visibly), and sets the ambush: mines/turrets laid
   along the marked ambush line where the swarm MUST converge. Wave
   crests onto the line, meets the guns, dies. Win after wave 3,
   where the enemy hive REORIENTS (new A — content-cited beat: "New
   song, new axis. Listen again.") and the couple must re-probe under
   pressure.

BUILD NOTES. referee.real_eigen_axis gives ONE real axis; you need
the eigenvalues and ideally 2-3 real eigenpairs. SPEC A SMALL REFEREE
ADDITION (give DeepSeek the exact function): eigen_pairs(A) ->
list of (lambda, unit_vector) for real eigenpairs, TOL_IMAG doctrine
applied. Choose A yourself: symmetric-ish 3x3 with eigenvalues like
(1.15, 0.7, 0.4) so the dominant axis emerges in ~10 pulses and
motes don't explode off-screen (clamp/respawn motes at a radius —
fiction: drones peel off to re-arm). Motes: pooled points/short
Trails, a few hundred max, updated at 10 Hz, interpolated. Determinism:
one seed. Never punish: drones harass shields, they don't kill.

ACCEPTANCE. Before wave 3 is over, the player predicts OUT LOUD where
the swarm will thicken — and is right. Prediction beat firepower.

FILE: brief_m13.md — MISSION BRIEF M13 (diagonalization: "Shield Harmonics")

BRIEF M13 — DIAGONALIZING THE DEFENSE GRID (Canon M13, §6.3-6.4;
Mission 14, the Act IV climax). File suggestion: m13_harmonics.py
Read briefs M4 and M11 — this fuses their mechanics.

FICTION. The Taiidan flagship's shield is a COUPLED turret network: a
symmetric matrix S. Hit it along any ordinary direction and the
turrets share the load — energy poured in one channel bleeds into the
others and the shield sheds it (the coupling is drawn: pulsing links
between turret nodes). But a symmetric S decouples: S = Q Lambda Q^T.
In the RIGHT basis — its eigenvector axes — the network is just
independent turrets, each with its own stiffness lambda_i. Strike
along the WEAK eigenvalue's eigenvector and the smallest stiffness
takes the whole blow, alone.

THE GAME.
 - The shield is a translucent ellipsoid around the flagship — and
   the ellipsoid IS the math: its principal axes are the eigen-
   vectors, its radii the stiffness (long axis = strong, short axis
   = weak). Don't label it; let its shape be the tell.
 - Phase 1, SOUNDING: the Navigator fires harmless sounding pings
   (M11's probe, third appearance): ping along direction u, read
   back the response — misaligned pings SCATTER (response vector
   S u visibly not parallel to u; the shield "rings dirty"); on a
   principal axis the response is pure — same line, clean tone
   (audio cue if trivial, else visual "clean ring"). She locks the
   three axes one by one; console shows S rotating into diagonal
   form as axes lock: off-diagonal cells literally fade to zero,
   Lambda emerging on the diagonal. The weak axis is the smallest
   entry — referee.weak_axis is the authority (it exists already!).
 - Phase 2, THE STRIKE: Pilot maneuvers the strike wing onto the
   weak axis line (drawn golden once locked) while flagship guns
   pressure everyone off-line (gentle, telegraphed). Volley fired
   ON-AXIS hits stiffness lambda_min and cracks the layer; three
   layers, re-sounding between them (S changes). Win: shield down,
   Key of Resonance card (content-cited): "Every fortress has a
   grain. Strike with it, not against it."

BUILD NOTES. S: symmetric 3x3, eigenvalues well-separated (e.g.
9, 4, 1). Verdicts: referee.weak_axis for the answer, and your
eigen_pairs addition from M12 (coordinate with DeepSeek — if M12's
branch shipped it, it's already in referee.py). The "response" to a
ping is S @ u DISPLAYED as geometry — computed via one referee helper
if you display verdicts about alignment (spec if needed). Ellipsoid:
scale a unit sphere's points by the eigen-frame — build it as Line
loops (three principal circles suffice and look holographic).
Diagonal-emerging console: a 3x3 MatrixGrid whose values you set each
pulse from the locked-axes-so-far conjugation — referee-sourced.

ACCEPTANCE. The player, seeing the NEXT encounter's ellipsoid, points
at its short axis and says "hit it there" before sounding at all.
The shape taught the theorem.

FILE: brief_m14.md — MISSION BRIEF M14 (change of basis: "The Defector's Ship")

BRIEF M14 — SALVAGE & CHANGE OF BASIS (Canon M14, Ch. 8).
File suggestion: m14_defector.py

FICTION. A Taiidan corvette defects mid-battle and must be flown NOW —
but its helm speaks ENEMY COORDINATES. Its thrusters answer to the
Taiidan basis B (three skewed amber axes drawn ON the captured hull,
visibly non-orthogonal, visibly not ours), while your orders arrive
in fleet basis (e1/e2/e3, red/green/blue on Mom). Until refit, every
order is MISHEARD: command "straight up" and it slides up-and-
sideways along ITS OWN idea of up.

THE GAME.
 - Act 1, THE COMEDY OF ERRORS: the Pilot must dock the defector at
   Mom using raw orders that get mangled through the enemy basis.
   Doable but maddening — INTENDED (2 minutes, generous dock radius).
   The couple laughs; the problem is now in their bones: same space,
   different coordinates.
 - Act 2, THE REFIT: the Navigator rebuilds the translator on the
   console. The enemy basis vectors b1, b2, b3 are measurable: a
   CALIBRATE button fires each enemy thruster once; the resulting
   displacement IS that column of B, drawn in space as it's measured
   and filling a 3x3 console matrix column by column. Refit =
   commanding in fleet terms by conjugation: to make the captured
   ship perform fleet-maneuver A, send its helm B^{-1} A B (the
   translation sandwich: into enemy coordinates, act, back out).
   The console shows the sandwich as three stamped cards:
   [OURS -> THEIRS][THE MANEUVER][THEIRS -> OURS]. Inverse verdict
   (does B^{-1} exist? is B truly a basis?) — referee: rank(B) = 3,
   and spec a small referee addition inverse(B) if absent.
 - Act 3, PROOF OF REFIT: fly a formation maneuver (an ApplyTransform
   A from the template's TRANSFORM zone) with the WHOLE fleet
   INCLUDING the defector: fleet ships receive A, the defector
   receives B^{-1} A B — and it moves AS ONE with the fleet. That
   unison is the win condition and the theorem: similar matrices,
   same motion, different coordinates. End card (content-cited):
   "She flies with us now. Same space. Her own words."

BUILD NOTES. The mangling rule (Act 1) and the sandwich (Act 3) are
shell-side wiring of referee-verified matrices; NEVER invert B in the
shell. B: pick skewed-but-tame integer-ish columns (det well away
from 0); verify with referee.determinant / rank. The captured ship:
sim.spawn a corvette, tint amber via shipwright spec if content
allows — ask DeepSeek whether ship color per-instance is supported,
else mark it with an amber selection ring. Ask DeepSeek also for the
TRANSFORM-zone wiring pattern from console.py (the trunk's corrected
B3) to reuse for sending A and B^{-1} A B.

ACCEPTANCE. Act 1 must get a laugh; Act 3 must get the quiet "oh —
now it's OURS." If both sounds happen, change of basis is learned.

Say "continue" one last time for the finale: M15 (the Guidestone / SVD transmission) and M16 (the SVD boss fight & the jump home) — and a short trunk hand-off note to close the tree properly. 🚀
