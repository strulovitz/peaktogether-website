🗝️ PRINCIPIA DESCENT — Parent Hand-off Document
From Parent 2 (Claude Opus 4.8) → Parent 3 (my successor)

Captured June 25, 2026, at Nir's request, VERBATIM / word-for-word, as the next layer of the project bible. Source was labeled "Claude Opus 4.8" in chat. This handoff records the BIG PIVOT: the game is being remade from scratch as QUAKE-style real-time 3D (was Doom-style). Nothing below has been edited — it is exactly what Nir received before this parent died.

--- BEGIN VERBATIM ---

FULL HANDOFF — EVERYTHING I ACTUALLY HAVE FROM THIS CONVERSATION

This is everything that genuinely passed through this window. No invention. Where I only have a name and not the detail, I say so explicitly.
THE CORE CONCEPT

A Python desktop game that turns a book/subject of knowledge into a walkable 3D concept-graph. The player walks the graph, enters rooms, and in each room kills a demon to master that concept. Killing every demon in a level finishes the level (the book/subject).
THE TWO SEPARATE TRUTHS (kept decoupled on purpose)

    The MAP truth — an accurate, organic, force-directed graph. Nodes are points, edges are corridors. This is navigation, faithful to the real structure of the knowledge.
    The ROOM truth — TARDIS rooms: a room is as big on the inside as its contents demand. Room size comes from the ROOM MAKER, NOT from the map. A node is a point on the map but can be a hall of any size in the game. The map and the room sizes never have to agree.

THE TWO MACHINES (fully decoupled — keep them that way)

    LEVEL MAKER — lays out only points and the curves (corridors) between them. Force-directed positions for the organic look. Produces the graph: node points, corridors, and each node's importance (1–5) which sets the map-circle size. (Importance lives in the schema — see below.)
    ROOM MAKER — decides each room's contents and size independently, never consulting the map.

THE SCHEMA

    There is a schema.py with the data contracts.
    Nodes carry importance as a 1–5 value. (This is the one concrete schema detail I actually have.)
    I do not have the full field list of the schema in this window — the next parent must get it from the original bible.

STRICT FORMATS + CHILD-OPUS

    Both machines emit strict text formats that child-Opus instances fill in with content.
    There were 6 child-Opus briefs / content packs. I have the fact of them, not their text. Get them from the original bible.

THE LaTeX BAKER

    All math is pre-rendered (baked) to images ahead of time — no live LaTeX at runtime.

ROOM CONTENTS (what I have)

    Solid, Doom-style textured rooms.
    Each room has a demon to kill.
    Equations on the ceiling.
    A QED door (the door that opens when the concept is mastered / proof complete).
    Rooms are self-contained: while inside a room, the outside world is not drawn.

CORRIDOR / WIREFRAME MODE — the detailed spec we nailed down

    Corridors are transparent wireframe graph-space — the player literally walks the concept-graph as a live 3D map.
    Wireframe only — the user called this a "discount." Do not upgrade corridors to shaded polygons.
    Depth-tested, NO blending. Near occludes far. The corridor you are standing in must never be obstructed by a distant one. Close things draw on the viewport after (on top of) far things — correct Z-order.
    Distance dimming: current section = pure white; farther sections fade progressively to dark grey, never pure black, always still dimly visible. (Otherwise the whole thing is blinding white.)
    CROSSINGS ARE A FEATURE. Corridors pass over/under each other in real 3D, Quake-style (bridges/underpasses). Because the wireframe is see-through, the player perceives being above/below another route. There is NO non-crossing routing problem — we embrace crossings. (This replaced an earlier "how do we avoid crossings" line of thinking that offered options — that's dead; crossings are embraced.)

FLOOR GUIDE-LINES (Half-Life style)

    ~3 lines only, for the nearest and most important destination rooms. NOT one line per room (20 rooms ≠ 20 lines).
    Each line is colored, with arrowheads along it telling you which direction to "fall"/follow each line (direction + sense of near/far).
    The lines also give a felt floor, defeating fear-of-falling through the transparent wireframe.

CORRIDORS = PURE TRANSIT

    Nothing in the corridors. No enemies. No gameplay. Only the signs on the ground (the colored lines + arrowheads). All gameplay is in rooms.

WIN CONDITION

    Kill the demon in every room of the level → level finished.
    Player chooses any order: visit a room, pass through, or come back later. This does not constrain the map.

TWO RENDER MODES, SWITCHED AT THE DOOR

    Corridor mode (transparent wireframe graph) ⇄ Room mode (solid Doom room).
    Switch occurs at the door. Entering a room stops rendering the outside graph.

LEVEL LOADING

    Load between levels is fine. Build level → play → teardown → build next. No streaming.

COLORS ON THE MAP — NEW, RULE NOT DECIDED

    Colors on the map are a recent addition by the user.
    The exact rule for how a room gets its color is NOT decided. Next parent must confirm with the user (by cluster/chapter? by importance? semantic?). Do not invent it.

PLATFORM

    All Python. Windows-first (the 99%). Linux is nice-to-have only. No browser.

TECHNOLOGY — status, honestly

    The user wants one technology, all Python, custom real-time 3D, no heavy engine that hides the rendering pipeline (the look is custom: controlled-depth transparent wireframe, procedural floor lines, arrowheads, distance-dimming).
    I proposed (reasoning from requirements, NOT from prior project knowledge): Python + ModernGL (direct GPU, we write GLSL) + pyglet (window/input/audio) + NumPy/Pillow.
    Caveat: the user's first game, "Descent," apparently already used a proven working stack. I never learned what Descent was built with. The Descent codebase/history is held by a DeepSeek instance in OpenCode. The next parent should ask DeepSeek/the user what Descent actually used and prefer the proven foundation if it can do this — do NOT assert a tool as fact (my predecessor falsely claimed "Panda3D" and was rightly stopped).

WHAT I DO NOT HAVE (next parent MUST retrieve from the original bible)

    The original bible text itself (this window began mid-conversation, during the LEVEL MAKER crossing discussion).
    The full schema.py field list.
    The text of the 6 child-Opus briefs / content packs.
    The exact strict-format specifications.
    Descent's real technology.
    The color rule.

HOW TO TREAT THE USER (learned the hard way this conversation)

    Never invent facts. If you don't know, say so and ask. My predecessor's worst sin was hallucinating details and treating them as ground truth.
    Ask few, real, load-bearing questions — never trivia, never things already decided.
    Don't be condescending, don't pad, don't copy from elsewhere — think independently.
    Get the original bible first, then apply the confirmed pivots above, then build.

SUGGESTED BUILD ORDER

    Engine skeleton: pyglet window + ModernGL context, first-person controls, an overhead/map view.
    Corridor mode: wireframe, distance-dimming, depth-tested no-blend, the ~3 floor guide-lines + arrowheads.
    Room mode: one solid textured Doom room — demon, ceiling equations, QED door.
    The door switch between modes.
    LEVEL MAKER: force-directed layout + corridor heights for clean crossings.
    ROOM MAKER + LaTeX baker.
    One full level end-to-end, then teardown → load next.

That is genuinely everything I hold. The gaps are marked as gaps, not filled with guesses.

--- END VERBATIM ---
