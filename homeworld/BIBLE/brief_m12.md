MISSION BRIEF M12 (eigen-dynamics: "The Swarm")

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
