MISSION BRIEF M5 (nullspace cloaking: "Ghost Fleet") — the best single idea in the project; build it with love

BRIEF M5 — NULLSPACE CLOAKING (Canon M5, §3.2; Mission 8 "Ghost Fleet").
File suggestion: m05_ghostfleet.py

FICTION. A Taiidan sensor blockade: stations project a detection grid —
a matrix A, ONE ROW PER STATION. A ship moving with velocity x is seen
with intensity |row_i . x| by station i. A course x with Ax = 0 is
INVISIBLE — every sensor literally reads zero. Stealth = living in the
nullspace.

THE GAME — ALWAYS SPACE, maximally: the nullspace is drawn as literal
GEOMETRY. With 2 independent station rows in R^3, the safe courses form
a LINE: render a glowing translucent corridor-line through the squad.
Jam a station (JamStation order — deletes a row) and the nullspace GROWS
before your eyes into a PLANE of safe motion (rank-nullity as a felt
event: n - r went from 1 to 2). Enemy adds a station: the plane snaps
back to a line; three independent rows: NO safe direction exists —
nowhere to hide, the corridor visual dies, you must jam first.
 - Navigator: console shows the station matrix A (rows highlighted per
   station, spatially linked — hover a row, the station in space
   pulses), per-station detection bars |a_i . x| live, and the JAM
   button (limited charges). referee.nullspace_basis(A) gives the safe
   directions; the console offers them as "GHOST HEADINGS."
 - Pilot: flies the squad along the corridor with trim/combinations;
   drifting off the nullspace makes bars rise smoothly (grace, not
   instant fail); detection raises ALERT, which repositions patrols —
   pressure, never punishment.
 - Win: the whole squad crosses the blockade line undetected; end-card
   line (content, cited): the stronger the enemy's rank, the less room
   to hide.

BUILD NOTES. context keys A_grid / cloaked_squad / grid_eps already
exist — ask DeepSeek FIRST whether sim already implements sensor-grid
detection and JamStation (it likely does at least partially; reuse it,
do not duplicate). Verdicts: referee.in_nullspace(A, x, eps) and
referee.nullspace_basis(A) ONLY. Corridor rendering: Line/DashedLine
along basis vector(s) through the squad centroid; for a 2D nullspace
draw a translucent grid-plane (Grid vobject oriented by the two basis
vectors). Station rows change => recompute basis once per pulse, 10 Hz.

ACCEPTANCE. When the jammer fires and the line blooms into a plane,
somebody at the desk says "ohhh." That sound is the whole mechanic.
