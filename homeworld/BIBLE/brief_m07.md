MISSION BRIEF M7 (the Fundamental Theorem: "The Karos Graveyard")

BRIEF M7 — THE BIG PICTURE AS A LITERAL STAR MAP (Canon M7, §3.5;
Mission 9). File suggestion: m07_karos.py
The most abstract canon entry — so be the MOST spatial. Everything is
regions, colors, and travel; the word "subspace" appears only in cited
end-cards.

FICTION. Karos: a graveyard region ruled by an ancient relay matrix A
(3x3, rank 2 — chosen so every subspace is visible in 3D). The relay
TELEPORTS: any ship at position x is beamed to A x. Four territories:
 - THE HIGHWAY (row space, dim r=2): a glowing plane in the fleet's
   half of the map. Motion here is "seen" by the relay.
 - THE SHADOW (nullspace, dim n-r=1): the line PERPENDICULAR to the
   highway (draw the right angle!). Ships here teleport to ZERO — the
   relay's maw at the origin. Danger and stealth in one geometry.
 - THE DESTINATION FIELD (column space, dim r=2): the plane on the far
   half where every teleport lands. Wrecks of ancient fleets litter it.
 - THE DEAD ZONE (left nullspace, dim m-r=1): perpendicular to the
   destination field; NOTHING can teleport there — cargo beacons in
   the dead zone are unreachable by relay and must be flown to by hand.

THE GAME. Recover four data cores, one per territory. Each retrieval
teaches its region by feel: highway cores teleport cleanly; the shadow
core must be grabbed by a ship whose position splits x = x_row + x_null
(console shows the split as two stacked arrows in space — projection
onto the highway); dead-zone core is unreachable by relay (attempted
beam visibly lands on the destination plane instead — the projection!),
so the Pilot flies it manually. Finale: the ancient beacon (Book VI's
plot revelation, content-cited): row rank = column rank — "the two
independent directions you fly are the two independent directions you
arrive." Dimensions r, n-r, r, m-r shown on the map corners as region
labels: 2, 1, 2, 1.

BUILD NOTES. Verdicts and bases from referee: rank, nullspace_basis
(for A and A^T — pass A.T for the left nullspace; row space basis =
column space of A^T). If you need an orthonormal basis helper, spec a
small referee addition rather than computing shell-side. The teleport
is a mini-game rule in your shell: an ORDER (reuse ApplyTransform with
matrix A? decide with Nir) or a "RELAY" button; animate the beam.
A suggestion: A = [[1,0,1],[0,1,1],[1,1,2]] (rank 2, nice integers) —
verify its subspaces with the referee before hardcoding labels.

ACCEPTANCE. A player can point at the four regions on screen and say
what each DOES (seen / swallowed / landing field / unreachable) —
without using one mathematical word.
