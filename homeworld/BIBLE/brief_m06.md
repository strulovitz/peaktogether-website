MISSION BRIEF M6 (complete solution: "The Blockade Run")

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
