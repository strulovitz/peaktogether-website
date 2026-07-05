MISSION BRIEF M10 (determinant: "The Collapsing Gate")

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
