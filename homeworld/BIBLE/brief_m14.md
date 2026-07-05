MISSION BRIEF M14 (change of basis: "The Defector's Ship")

BRIEF M14 — SALVAGE & CHANGE OF BASIS (Canon M14, Ch. 8).
File suggestion: m14_defector.py

FICTION. A Taiidan corvette defects mid-battle and must be flown NOW —
but its helm speaks ENEMY COORDINATES. Its thrusters answer to the
Taiidan basis B (three skewed amber axes drawn ON the captured hull,
visibly non-orthogonal, visibly not ours), while your orders arrive
in fleet basis (e1/e2/e3, red/green/blue on Mom). Until refit, every
order is MISHEARD: command "straight up" and it slides up-and-
sideways along ITS OWN idea of up.

THE GAME.
 - Act 1, THE COMEDY OF ERRORS: the Pilot must dock the defector at
   Mom using raw orders that get mangled through the enemy basis.
   Doable but maddening — INTENDED (2 minutes, generous dock radius).
   The couple laughs; the problem is now in their bones: same space,
   different coordinates.
 - Act 2, THE REFIT: the Navigator rebuilds the translator on the
   console. The enemy basis vectors b1, b2, b3 are measurable: a
   CALIBRATE button fires each enemy thruster once; the resulting
   displacement IS that column of B, drawn in space as it's measured
   and filling a 3x3 console matrix column by column. Refit =
   commanding in fleet terms by conjugation: to make the captured
   ship perform fleet-maneuver A, send its helm B^{-1} A B (the
   translation sandwich: into enemy coordinates, act, back out).
   The console shows the sandwich as three stamped cards:
   [OURS -> THEIRS][THE MANEUVER][THEIRS -> OURS]. Inverse verdict
   (does B^{-1} exist? is B truly a basis?) — referee: rank(B) = 3,
   and spec a small referee addition inverse(B) if absent.
 - Act 3, PROOF OF REFIT: fly a formation maneuver (an ApplyTransform
   A from the template's TRANSFORM zone) with the WHOLE fleet
   INCLUDING the defector: fleet ships receive A, the defector
   receives B^{-1} A B — and it moves AS ONE with the fleet. That
   unison is the win condition and the theorem: similar matrices,
   same motion, different coordinates. End card (content-cited):
   "She flies with us now. Same space. Her own words."

BUILD NOTES. The mangling rule (Act 1) and the sandwich (Act 3) are
shell-side wiring of referee-verified matrices; NEVER invert B in the
shell. B: pick skewed-but-tame integer-ish columns (det well away
from 0); verify with referee.determinant / rank. The captured ship:
sim.spawn a corvette, tint amber via shipwright spec if content
allows — ask DeepSeek whether ship color per-instance is supported,
else mark it with an amber selection ring. Ask DeepSeek also for the
TRANSFORM-zone wiring pattern from console.py (the trunk's corrected
B3) to reuse for sending A and B^{-1} A B.

ACCEPTANCE. Act 1 must get a laugh; Act 3 must get the quiet "oh —
now it's OURS." If both sounds happen, change of basis is learned.
