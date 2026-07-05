MISSION BRIEF M1 (linear combinations + span: "The Plane of Refugees")

BRIEF M1 — COMBINATION FLIGHT / THE PRISON OF THE PLANE (Canon M1, §1.1;
Missions 1+3 fused). The template app.py already flies by combinations —
your job is to turn it into a GAME with the span lesson as its heart.

FICTION. First flight of the exile fleet. Refugee pods drift at (3, 5, 4)
— note the nonzero SECOND coordinate: height. At mission start only e1 and
e3 are unlocked (the horizontal plane): the fleet is imprisoned in a glowing
plane it cannot leave, and the pods float ABOVE it, visibly, hauntingly.

THE GAME. Phase 1: tutorial tasks — fly squad 1 to marked buoys IN the
plane using coefficient orders (Navigator sliders or Pilot keys; c2 slider
is LOCKED/greyed). Phase 2: a buoy appears at the pods. Every attempted
order visibly slides along the plane under it; Fleet Intelligence (content
lines, cited): "That target lies outside the span of our engines." The
console shows the reachable set for what it is. Phase 3: the Research
Vessel event unlocks e3 -> wait, e2 (the vertical) — the c2 slider wakes,
a third basis arrow ignites in green, and the order (3, 5, 4) rescues the
pods. Win screen: pods dock with Mom. Lesson felt, never lectured:
independence = freedom, span = everywhere you can ever go.

BUILD NOTES. Lock/unlock = your mini-game state gating which coeffs are
accepted (sim's engine_vectors already exist; ask DeepSeek whether the sim
supports fewer unlocked engines or gate it in your shell). Draw the prison
plane as a translucent Grid/lines vobject. Buoys = small glowing rings
(circle points pattern is in app.py). Use referee.is_solvable(E, target)
for the "reachable?" verdict (E = matrix of UNLOCKED engine columns).
Questions for DeepSeek: does sim expose engine unlock state or is
engine_vectors fixed at 3? Does content_db have a narrator-lines loader?

ACCEPTANCE. A non-mathematician must feel trapped in Phase 2 and free in
Phase 3, and say so unprompted.
