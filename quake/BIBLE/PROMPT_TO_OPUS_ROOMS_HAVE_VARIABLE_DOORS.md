# PROMPT TO OPUS 4.8 (alone) — a room has a VARIABLE number of doors (= its node degree), not one

Opus — one important correction to the Room Maker. (Same working model as always: you produce the DESIGN / algorithm-spec / child brief — the DOCUMENT — never running code.)

## The problem
Your Room Maker thinking assumes a room has ONE entrance. That's wrong, and it matters a lot.

## Why — a room IS a graph node
A room **is** a node in the concept graph. The number of doors a room has = the number of corridors (edges) connected to that node = the node's **degree**. That can be **1, 2, 3, … or many**. And we do **NOT know how many until the force-directed graph layout is computed** — that is the moment we learn which edges touch the node (and from which direction). The rule is simple and absolute: **one edge = one corridor = one door.** A leaf result might have a single door; a foundational lemma that everything depends on might have a dozen.

## Don't confuse it with the hidden door
This is SEPARATE from the single **hidden/secret door** (the final-proof wall that opens to release the demon). So every room has BOTH:
- (a) a **variable number of entrance/exit doors** = its node degree (the corridor mouths, determined by the layout), AND
- (b) exactly **one** hidden door (the final proof step that releases the demon).

Please keep these two kinds of door distinct in the design.

## What the Room Maker algorithm must do
The algorithm must take the room's **incident corridors (from the floorplan)** as input and:
1. Reserve a wall slot / gap for **each** entrance door (N of them, N = the node's degree) **before** placing any proof panels.
2. Lay out the proof panel-pairs in **whatever wall space is left**, in reading order, working with however many doors there are.
3. Keep a **door ↔ corridor mapping**, so walking out through a door returns the player to the correct corridor in the graph.
4. Handle the extremes gracefully: a **degree-1** room (one door) and a **high-degree hub** room (many doors eat a lot of wall, so the TARDIS sizing must compute capacity as "total wall minus the door gaps," and grow the room if the panels + doors don't fit).

## Likely format consequences (please address)
- `RoomRuntime` (§4.5) currently has only `hidden_door_wall_slot` and **no representation of the entrance doors at all**. It probably needs a list of entrance doors, each carrying its wall slot + the `corridor_id` it connects to.
- `FloorRoom` (§4.4) doesn't list a room's incident corridors. The Room Maker can derive them by scanning the `corridors` list by `source`/`target`, and can read each corridor's approach direction from its `path_xz` if you want door placement to follow the map. Please confirm the floorplan gives the Room Maker everything it needs (count + which corridor + approach bearing).

(Even with the TARDIS decoupling — interiors living in their own coordinate space — the **count** of doors and the door↔corridor mapping still matter: you must place exactly that many doors and route every exit back to the right corridor.)

Please update the Room Maker algorithm design (and any affected formats) so it handles a **variable, layout-determined number of doors per room**. Thank you.
