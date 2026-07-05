The drama act — the perpendicular error, the flattening emergency, and the calm axis. DeepSeek: save as brief_m09.md, brief_m10.md, brief_m11.md.

FILE: brief_m09.md — MISSION BRIEF M9 (projection & least squares: "The Nebula of Noise")

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

FILE: brief_m10.md — MISSION BRIEF M10 (determinant: "The Collapsing Gate")

BRIEF M10 — DETERMINANT HYPERSPACE GATES (Canon M10; Mission 12).
File suggestion: m10_gate.py

FICTION. A hyperspace jump needs a bubble: the tilted box (parallel-
epiped) SPANNED BY THREE ESCORT FRIGATES' position vectors from Mom.
Bubble capacity = |det| of the 3x3 matrix whose columns are the three
escorts. Sabotaged gate + enemy tractor drift = the escorts keep
sliding toward a common plane. det -> 0 means the box goes FLAT and
the jump fails. Singularity as a felt emergency.

THE GAME. A survival-and-charge loop, played entirely in space:
 - The BOX IS DRAWN, always: 12 glowing edges of the parallelepiped
   spanned by the escorts, from Mom. Its volume readout
   (referee.spanned_volume) doubles as the JUMP CHARGE RATE — a fat
   box charges fast, a thin one barely.
 - Enemy tractor pulses (seeded, telegraphed) drag one escort at a
   time toward the plane of the other two — the player WATCHES the
   box thin. Alarm at low volume; at det = 0 the box renders as a
   flat sheet, charge stops, Fleet Intelligence (content, cited):
   "We've gone flat! The escorts share a plane — spread out!"
 - Pilot: flies the dragged escort back out (trim/combinations).
   Navigator: watches det live (SIGNED, referee.determinant — and
   when a tractor pulse flips orientation through zero the sign
   flips: the box turned inside out; show +/- and let them wonder),
   assigns which escort to correct, and can fire ONE emergency
   ApplyTransform (from the template's TRANSFORM zone) to re-spread
   the formation — a matrix as a rescue lever.
 - Win: charge reaches 100% while volume stays above gate_min_volume;
   the jump fires (M16's future ritual gets a one-frame teaser).

BUILD NOTES. Context keys gate_frigates / gate_center /
gate_min_volume already exist — ASK DEEPSEEK FIRST whether sim already
implements a gate/volume rule (likely at least partially; reuse).
Volume verdicts: referee.spanned_volume; signed value:
referee.determinant. Box rendering: 8 corners from column sums
(0, a, b, c, a+b, a+c, b+c, a+b+c) joined by 12 Line vobjects —
positions interpolate per frame like ships do. Keep the tractor gentle
(Iron Rule): drift is slow, telegraphed, and never drags two escorts
at once on normal difficulty.

ACCEPTANCE. Someone shouts "spread out, we're going flat!" at a
sheet of light. Determinant = volume, singular = collapsed, learned
under adrenaline.

FILE: brief_m11.md — MISSION BRIEF M11 (eigenvectors: "The Calm Axis")

BRIEF M11 — EIGENVECTOR DOCKING (Canon M11, §6.1; the Act IV relic).
File suggestion: m11_relic.py

FICTION. An ancient relic tumbles under a fixed transformation T:
every pulse, the space AROUND it is stirred by T. Approach from any
direction and your approach vector is swung off course and you're
flung away — except along an eigenvector, where T x = lambda x keeps
your DIRECTION unchanged. Docking = finding the calm axis of a
spinning thing.

THE GAME.
 - The stirring is VISIBLE: a shell of ghost test-arrows around the
   relic redraws each pulse as T bends them (each arrow drawn from
   x toward T x, normalized) — a whirlpool of directions... except
   along one axis, where arrows lie still. The calm axis is
   findable BY EYE if you stare — that's intended.
 - Navigator's console: a PROBE widget — she aims a trial direction
   x (two angle sliders), and the console draws x and T x side by
   side with the angle between them; misaligned probes visibly
   scissor apart, and on the eigenvector they fuse into one line
   with a pure stretch readout (the lambda! shown as "x 1.7" —
   scale, not turn). A FIND button may exist but costs the mission's
   only scan charge (referee.real_eigen_axis) — probing by hand is
   cheaper and more fun.
 - Pilot: flies the docking ship onto the axis line (drawn once the
   Navigator locks a probe within tolerance), then approaches WITH
   THE AXIS. Drift off-axis and the relic's stir pushes the ship
   sideways (gentle spring, telegraphed — never a slam); on-axis,
   approach is glass-smooth. Contact: dock, relic powers up, the Key
   turns (content-cited end card: "Every spinning thing has an axis
   it cannot move. Find it, and it will hold you steady.").
 - Optional second relic (harder): negative lambda — the calm axis
   holds your LINE but reverses you each pulse; docking requires
   half-speed. Let them discover why.

BUILD NOTES. T: pick a rotation-plus-stretch with ONE real eigen-
direction dominant, integer-friendly; VERIFY with referee.
real_eigen_axis before hardcoding. The stir on the ship = shell-side
rule (per-pulse nudge proportional to how far the ship's relative
position direction is from the axis); the AXIS and all eigen verdicts
come from referee only. The test-arrow shell: ~60 pooled Arrow/Line
vobjects on a sphere, recomputed per pulse, interpolated per frame.
Ask DeepSeek: current Arrow pooling patterns from earlier branches
(M5's corridor, M9's residuals) to reuse.

ACCEPTANCE. A tester finds the axis BY EYE from the whirlpool before
touching the probe — and the probe then CONFIRMS what they saw.
Eigenvector = the direction the storm cannot turn.

Say "continue" for the final act: M12, M13, M14 — then M15, M16 to close the tree. 🚀
