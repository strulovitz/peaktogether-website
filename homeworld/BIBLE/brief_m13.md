MISSION BRIEF M13 (diagonalization: "Shield Harmonics")

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
