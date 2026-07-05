MISSION BRIEF M3 (rank & A = CR: "Salvage Run")

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
