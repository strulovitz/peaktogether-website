Excellent — the middle act. Three briefs: the economy, the war, and the crown jewel. DeepSeek: save as brief_m03.md, brief_m04.md, brief_m05.md.

FILE: brief_m03.md — MISSION BRIEF M3 (rank & A = CR: "Salvage Run")

BRIEF M3 — THE A = CR ECONOMY (Canon M3, §1.3-1.4; Mission 4).
File suggestion: m03_salvage.py

NOTE. This is one of exactly two places (with M4) where the SIGNATURE
matrix is canon — but ground it spatially anyway: derelicts float in
SPACE, tugs fly to them, and the console's matrix always sits beside the
living fleet, never instead of it.

FICTION. A battlefield graveyard. Derelict ships drift among asteroids;
salvage them or build new — but enemy countermeasures ignore any ship
whose signature is a COMBINATION of signatures they already know. A
dependent ship costs resources and adds nothing. The optimal fleet is C:
independent columns only. Deploying a task force = choosing R (recipes).

THE GAME. Pilot flies salvage tugs (squad orders from the template) to
derelicts scattered in space; each capture adds a column. Navigator runs
the yard console: for every candidate (derelict or buildable), a PREVIEW
verdict before committing — referee.rank of fleet-matrix-with-candidate
vs without. "FT: rank 5 -> 5. Countermeasures already know this
signature. Adds nothing." vs "CV: rank 5 -> 6. NEW capability." Wasted
salvage is a lesson, not a loss: scrap refunds. Win: assemble a fleet of
target rank within the resource budget, then the Guidestone shimmer plays
(the first rank-1 shimmer, per Book VI Mission 4). Optional beat: console
shows C (kept ships) and R (how each dependent derelict = recipe of C
columns), via referee.cr_factor.

BUILD NOTES. BuildShip order + SHIP_BUILT event (rank_increased flag)
already exist; ask DeepSeek: does sim charge resources for BuildShip?
Does spawn support derelict/neutral ships, or do you fake derelicts in
your shell (positions + pickup radius) and call sim.spawn on capture?
(Faking in the shell is fine and keeps sim untouched.) Klass signatures
are in the charter. All verdicts: referee.rank / cr_factor — never local.

ACCEPTANCE. A player who cannot define "rank" starts refusing dependent
ships because "they're a waste of money." That instinct is the win.

FILE: brief_m04.md — MISSION BRIEF M4 (Ax = b combat: "The Shield Recipe")

BRIEF M4 — COMBAT AS Ax = b (Canon M4, Ch. 2; Bible 2.3 worked to depth).
File suggestion: m04_shields.py

FICTION. Taiidan shields are layered; each layer absorbs one output
channel. Breaking one needs a PRECISE RECIPE of damage, not maximum fire.

THE GAME. A shielded target sits in space with requirement vector b.
The strike group's ships are columns of A_g. The Navigator sets one
THROTTLE SLIDER per firing ship (x); the shield falls when
|b - A_g x| < eps (referee.residual verdict). TWO PICTURES, TWO SEATS:
the Pilot sees COLUMNS — each firing ship pours a colored stream into the
target, thicker with throttle; the Navigator sees ROWS — one draining bar
per shield layer (the kinetic equation, the beam equation...), each bar
showing "delivered / required". THREE ENCOUNTERS, three regimes:
 1. UNIQUE — exactly adequate group; find the one right x (back-
    substitution puzzle: Bible's worked example a1=(2,0), a2=(1,3),
    b=(7,6): beam row forces x2=2, then kinetic row gives x1=2.5).
 2. NO SOLUTION — b outside the column space. referee.is_solvable says
    no; Fleet Intelligence (content line, cited): "That target lies
    outside our column space. Recommend an independent vessel." The
    LEAST SQUARES button (greyed until this moment) fires referee.
    least_squares: shield drops to its irreducible remainder |e|,
    rendered as a glowing bar of channels-we-do-not-possess. Partial
    victory; then a reinforcement ship arrives and regime 1 finishes it.
 3. INFINITELY MANY — dependent columns; the console grows a FREE
    slider that walks the solution line; ammo cost = |x|_1 displayed
    live; the cheapest valid x is the smart pick.

BUILD NOTES. FireSolution + LeastSquaresFire orders exist; context keys
shield_b / shield_target / tolerance exist — ask DeepSeek whether sim
already executes shield combat or whether you run the encounter in your
shell (shell-side is acceptable; keep verdicts in referee). Enemy fire
should pressure but not kill (Iron Rule: explain, never punish —
shields regenerate slowly instead of ships dying).

ACCEPTANCE. The Navigator solves regime 1 by back-substitution under
fire and FEELS clever; regime 2's "impossible" is understood as a fact
about the fleet, not a difficulty setting.

FILE: brief_m05.md — MISSION BRIEF M5 (nullspace cloaking: "Ghost Fleet") — the best single idea in the project; build it with love

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

Say "continue" for M6, M7, M8 (the escape route, the Big Picture star map, and the Gram–Schmidt drill). 🚀
