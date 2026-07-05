MISSION BRIEF M2 (dot product: "First Contact / The Dust Stream")

BRIEF M2 — DOT-PRODUCT HARVESTING (Canon M2, §1.2; Mission 2).

FICTION. A dust river crosses the map: a flow field f, rendered as drifting
particle streaks so its direction is VISIBLE. The collector must drink from
it: harvest rate = rho * max(0, f . u), u = the intake axis unit vector.

THE GAME. Pilot selects the collector (TAB) and rotates its intake with the
coefficient keys repurposed as pitch/yaw of u (an arrow drawn on the hull).
Navigator's console shows: live f . u number, the angle theta, a drawn
angle arc between f and u (2D or 3D), and the hold gauge filling. Aligned:
gauge roars. 60 degrees off: exactly half (cos 60 = 0.5 — show the number,
let them notice). Perpendicular: zero. Facing away: zero (the clamp).
Win: fill the hold to quota, then a second dust stream with different f
forces re-aiming. The couple converges on the maximum TOGETHER: she reads
algebra ("you're at seventy degrees, pitch down"), he flies geometry.

BUILD NOTES. Orders: SetIntake exists in orders.py — ask DeepSeek whether
sim implements it and whether a resource_field context key already has a
format (it appears in the context-keys list!). If sim lacks harvest logic,
compute harvesting in your shell per pulse and keep sim untouched. rate
formula is one line; the VERDICT-free math here needs no referee call, but
if you display an angle number, compute it once, in one place. Particles:
a pool of short Trail or DashedLine vobjects drifting along f, recycled.
Fill gauge = Rect2D pair on the console. No timer pressure, no failure
state — the dust is patient (Iron Rule: never punish).

ACCEPTANCE. Nir and partner find the maximum by talking to each other,
and the phrase "perpendicular gives nothing" is SEEN, not read.
