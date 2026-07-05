MISSION BRIEF M9 (projection & least squares: "The Nebula of Noise")

BRIEF M9 — LEAST-SQUARES FIRING SOLUTIONS (Canon M9, §4.2-4.3;
Mission 10). File suggestion: m09_nebula.py
Cousin of M4 (read brief_m04.md; regime 2 there is this mechanic's
combat seed). Here PROJECTION is the star, not the consolation prize.

FICTION. A nebula that lies. Sensor pings are noisy; targets drift
outside what the fleet can deliver. Fire-control's ancient motto
(content, cited): "When you cannot hit the truth, hit its shadow —
and know the difference."

THE GAME — two acts, one picture:
 ACT 1, NAVIGATION BY FIT. The station's beacon pings arrive as noisy
 points in space (drawn as flickering dots). The true course is known
 to lie in a subspace (a glowing plane — 2 basis vectors). The console
 fits: referee.least_squares projects the pings' evidence onto the
 plane; in SPACE, each dot drops a faint PERPENDICULAR onto the plane
 (the residuals) and the fitted course-arrow forms where they balance.
 The Navigator can toggle any ping "trusted/untrusted" and watch the
 fit shift live. Fly the fitted course: it works. The lesson drawn:
 the best answer inside a world that cannot contain the question.
 ACT 2, THE SHADOW SHOT. A shielded hulk demands b OUTSIDE the strike
 group's column space (referee.is_solvable says no — reuse M4's row
 bars if that branch shipped). The FIRE BUTTON becomes "PROJECT & FIRE":
 referee.least_squares gives x-hat; the delivered blow b-hat = A x-hat
 lands; and THE ERROR VECTOR e = b - b-hat is rendered as a glowing bar
 PERPENDICULAR to the column-space plane on the console's spatial
 inset — with the right-angle marker. |e| is the shield's irreducible
 remainder; a scripted reinforcement (new independent column) then
 shrinks e to zero and the hulk cracks. Win.

BUILD NOTES. ALL fitting via referee.least_squares / residual /
is_solvable — the shell never solves anything. Noisy pings: seeded RNG
(determinism law). The perpendicular-residual rendering is the whole
mechanic — spend your polish there (thin DashedLines from each dot to
its foot on the plane). Ask DeepSeek: did M4's branch ship, and what
are its shield-encounter helpers called?

ACCEPTANCE. The player, seeing e drawn perpendicular, says some form
of "that's the part that doesn't fit." Projection understood as
geometry, least squares as its name.
