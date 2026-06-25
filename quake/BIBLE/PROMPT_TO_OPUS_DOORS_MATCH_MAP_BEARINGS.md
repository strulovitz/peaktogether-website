# CORRECTION FOR OPUS 4.8 — doors must sit at the REAL map bearings. This is not sci-fi teleportation.

Opus — another correction, and again I want you to rethink the room/door design **holistically**, not patch one field. (Standing rules: you produce the DOCUMENT / design / child-brief, never running code; and deliver anything I'll copy-paste as prose or fenced code blocks, never tables.)

You concluded that it doesn't matter where a room's doors are, because the player never sees a door opening on the corridor side. That conclusion is wrong, and I want to be clear about why.

Yes — we never render a door opening *into* a corridor. But that is a **simplification I granted to make the engine easier for you to build — a favor.** It is **not** a license to treat door position as meaningless. Please don't take the kindness and turn it into an excuse to make the world incoherent.

Here is the requirement, and it's not negotiable: **a room's doors must be placed in the actual direction each corridor leaves the node in the map layout — consistent with the map.** If an edge leaves the node toward the north-west (better still: at a specific bearing/angle in degrees), then that corridor's door must be on that side of the room, at that bearing. The doors fan out around the room at the same angles the edges fan out from the node on the map.

This is **not** portal transport — we are not in sci-fi. The two players are physically running around inside this place, and it has to **feel real**: enter from the north-west corridor → you come in from the north-west of the room; turn around and leave → you head back out the way you came, in the right direction. Their sense of orientation must stay coherent as they move through the whole structure.

To be exact about what stays and what changes: room **size** stays decoupled from the map (TARDIS — a room is as big inside as its contents demand). But door **direction** is now coupled to the map — each door sits at the real bearing of its corridor. (Door **count** is still the node's degree: one edge = one corridor = one door.)

Please reconsider the room/door spatial model as a whole in light of this — however it ripples through your design — with your full architect's view. I'm deliberately not prescribing the fix.
