MISSION BRIEF M4 (Ax = b combat: "The Shield Recipe")

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
