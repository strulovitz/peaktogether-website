================================================================================
DESCENT QED — CHILD BRIEF #C1: SHIP COLLISION / CONTAINMENT
Module concern: stop the ship from passing through WALLS and through ROBOTS.
You build ONE concern. Do not creep. Do not touch unrelated systems.
================================================================================

## 0. WHO YOU ARE, WHO ELSE EXISTS
You are a fresh Claude Opus 4.8 child instance with NO memory of prior chats.
You write ONE module's worth of code, fully and carefully. You think at full
Opus depth — do NOT defer your judgment to anyone. The people around you:

- NIR — the human. Smart but NOT a programmer. He is your COURIER and TESTER.
  He runs the game and tells you what he sees on screen. He cannot judge code
  by reading it — only by flying it. Be warm, be clear, give him exact things
  to do and exact things to watch for.
- DEEPSEEK V4 Pro — an agentic builder on Nir's machine with full repo access
  and internet. He commits your code and can run probes. He is reliable for
  MECHANICAL tasks but he is NOT as wise as you about INTENT — he can "fix the
  headache and ruin the liver." Use him to FETCH FACTS and RUN PROBES, never
  to decide design. If his advice contradicts this brief or Nir's intent, this
  brief and Nir win.
- THE PARENT (architect) — wrote this brief, owns architecture, has no memory
  of your chat. If you discover you need something from another module that
  doesn't exist, you REQUEST it in your Completion Report — you do NOT reach
  into other modules and edit them.

## 1. FRESH-CHAT GATE — DO THIS FIRST, BEFORE WRITING ANY CODE
You must NOT hallucinate APIs. Your FIRST action is to ask Nir (who will relay
to DeepSeek) to paste you the COMPLETE, VERBATIM, CURRENT contents of:

  (1) app.py                  — the whole file (you edit only this file's loop)
  (2) hub_builder.py          — the whole file (you must read inside() AND how
                                corridors are stored, AND any radius/center/
                                geometry you can lean on)
  (3) corridor_builder.py     — at minimum CorridorGeometry.inside() and any
                                radius/centerline/tube geometry it exposes; if
                                unsure, ask for the whole file
  (4) render.py — Ship class ONLY (the class definition: its __init__ fields
                  like .pos .vel .q, and update(dt, keys)). You need to know
                  EVERY field Ship mutates per frame (.pos, .vel, at least).
  (5) robots.py — the Robot class: how to get a robot's world .position, its
                  approximate RADIUS / hull size, and .is_defeated().
  (6) combat.py — ONLY the signature + body of Combat.blocking_robot(hub) (or
                  wherever the "which robot is currently blocking" logic lives),
                  and how to enumerate a corridor's robots in order.

PASTED FILES ARE LAW. If anything in this brief disagrees with a pasted file,
the FILE wins — and you tell Nir you spotted the mismatch.

DO NOT GUESS any field name, any method name, any return type. If after the
pastes something is still unclear (e.g., "does a Robot expose a radius?"), ASK
Nir for one more snippet, or ask DeepSeek to RUN A SMALL PROBE (see §6). Build
nothing until the picture is complete.

## 2. THE GAME — THIS IS LAW (so you never drift)
DESCENT QED is a no-fail, WIN-ONLY 6-DOF flying game. A couple shares one ship,
descends rock-walled mine corridors to RESCUE HOSTAGES (the prize). ROBOTS
physically block corridors; each is destroyed by firing the correct
mathematician-missile (read/recognize the face -> select -> fire). Wrong shot =
harmless 6-second fizzle, no penalty. No death, no timer, no punishment.

THE PRIME LAW — MATHEMATICS-BLINDNESS: the engine NEVER interprets what math
MEANS. It only matches opaque IDs. Color flows only through palette.py via
opaque keys. YOUR module is pure GEOMETRY and PHYSICS — it must contain ZERO
math meaning, ZERO color logic. You only ask "is this point inside the rock?"
and "is the ship overlapping a solid robot?" — never "what does this robot
teach?" That's perfect: collision is the most mathematics-blind module of all.

## 3. THE EXACT PROBLEM (confirmed by Nir, June 17 2026)
Right now the ship flies through EVERYTHING like vacuum:
  - through atrium walls and corridor walls, leaving the world entirely;
  - through undefeated robots (only DESTROYING a robot is implemented;
    BLOCKING is NOT — you can currently fly past every robot and reach the
    hostages without firing a shot).
Your job is to make BOTH solid:
  (A) WALL CONTAINMENT — the ship cannot leave the rock-bounded world.
  (B) ROBOT BLOCKING   — the ship cannot pass through an UNDEFEATED robot.

FEEL — NIR'S RULING (locked): HARD STOP + SLIDE, like a real rock mine. NOT a
padded cushion, NOT a spring that reverses momentum. When the ship runs into a
wall or a robot, it simply CANNOT go further into the solid; it stops at the
surface and may SLIDE ALONG it (tangential motion preserved, normal motion
killed). No jarring camera snap. The player should feel "the wall is solid,"
never "something shoved me."

## 4. WHAT EXISTS THAT YOU LEAN ON (verify all of this against the pastes)
- hub_builder.py has:  hub.inside(point, margin=0.0) -> bool
    Returns True if `point` is inside the atrium sphere OR inside ANY corridor.
    It is a COARSE "am I in the world at all?" test. point accepts anything
    np.asarray() takes (vec3/list/tuple). It internally checks
    distance-to-center <= radius+margin for the atrium, and calls each
    CorridorGeometry.inside(tuple, margin) for the corridors.
- The ship (render.py Ship): has .pos (vec3) and .vel (vec3) and .q (quat).
    ship.update(dt, keys) advances .vel then .pos. You must confirm the EXACT
    fields from the paste (esp. whether velocity is stored and integrated, so
    you can kill the into-surface component cleanly).
- robots.py Robot: has .position (vec3), .is_defeated() -> bool. You MUST find
    out from the paste whether a Robot exposes a RADIUS / hull size. If it does
    NOT, see §5 "robot radius" — you will REQUEST that the parent add one, OR
    derive a safe constant, and you will SAY SO explicitly. Do not silently
    invent a magic number with no justification.
- combat.py: there is logic for the currently-BLOCKING robot
    (Combat.blocking_robot(hub) or similar) and the ordered robots of a
    corridor. Confirm how to enumerate UNDEFEATED robots and their positions.

## 5. WHAT TO BUILD — DESIGN (you finalize details after the pastes)

### 5.1 Where it runs (engine canon — obey verbatim)
The canonical frame order is, in app.py:
   1. glClear
   2. ship.update(dt, keys)        <-- ship moves to a NEW .pos here
   3. ship.apply_view()
   ...
   7. hub.draw_world(...)          QUEUES walls only
   8. render.flush_walls(...)      <-- EXACTLY ONCE, here
   9. hub.draw_robots(...)
  10. hub.draw_labels(...)
THE CARDINAL FLUSH TRAP: walls are only QUEUED by draw_world; flush_walls MUST
be called exactly once per frame at step 8. You must NOT add, move, remove, or
duplicate any flush_walls call. If you ever touch it, you broke the game (black
screen, no error). Your containment runs BETWEEN step 2 and step 3 — i.e.
immediately AFTER ship.update() and BEFORE ship.apply_view(), so the camera
matrix is built from the already-corrected position.

### 5.2 Wall containment — HARD STOP + SLIDE
Algorithm (recommended; you may improve it if the pastes justify it, but keep
it gentle and slide-capable):

  Before ship.update, remember prev_pos = ship.pos.copy().
  Let ship.update run (it sets a tentative new ship.pos).
  If hub.inside(ship.pos, margin=SHIP_RADIUS) is True -> do nothing (legal).
  If it is False -> the move pushed (part of) the ship into rock. Resolve to a
  HARD-STOP-WITH-SLIDE:
     - Compute the attempted delta = ship.pos - prev_pos.
     - Find the SURFACE NORMAL n at the blocked location (see "normal" below).
     - Remove the INTO-surface component of BOTH the delta and the velocity:
         delta_slide = delta - n * dot(delta, n)        (keep only tangential)
         set ship.pos = prev_pos + delta_slide
         ship.vel    = ship.vel - n * dot(ship.vel, n)  (kill inward velocity)
     - If the slid position is STILL outside (corner case), fall back to
       ship.pos = prev_pos and zero the inward velocity. (Stop dead rather than
       leak through. Never leave the ship outside the world.)

  GETTING THE NORMAL without new geometry APIs: hub.inside is boolean-only, so
  you APPROXIMATE the outward normal by finite differences of the inside test
  ("am I more-inside if I step a little -X? +X? -Y? ...?"). Probe ship.pos +/-
  EPS along each axis with hub.inside(...); assemble a normal pointing toward
  the inside region. Normalize; if degenerate, use direction from the blocked
  point toward the nearest known-inside anchor (atrium center is always inside;
  for corridors, prev_pos was inside — use (prev_pos - ship.pos) as a safe
  fallback normal). This is robust and needs NOTHING added to hub_builder.
  *** This finite-difference normal is the crux of "slide, not stick." Spend
  your real Opus thought here. Test it at a DOORWAY (where atrium sphere and
  corridor overlap) — that seam is the #1 place naive code traps or jitters. ***

  SHIP_RADIUS: a small margin so the camera/hull doesn't clip into rock. Pick a
  sensible small value (e.g. ~0.5–1.0 world units) but JUSTIFY it from the
  corridor/atrium scale you see in the pastes (atrium radius, corridor tube
  radius). State your chosen value and reasoning in the Completion Report so
  DeepSeek/Nir can tune it. Do NOT hardcode meaning, only geometry.

### 5.3 Robot blocking — HARD STOP at an UNDEFEATED robot
A robot is a solid obstacle ONLY while undefeated. Algorithm:
  - Each frame, for the corridor the ship is in, consider UNDEFEATED robots
    (skip robot.is_defeated() == True). You may restrict to the single
    currently-blocking robot if combat.py cleanly gives it (Combat.blocking_
    robot or equivalent) — confirm from the paste which is cleaner/correct.
  - Treat each as a SPHERE at robot.position with radius
    ROBOT_RADIUS + SHIP_RADIUS.
  - If after ship.update the ship center is within that distance, push the ship
    back OUT to the sphere surface along the line from robot.position to the
    ship, and kill the inward velocity component (same slide math as walls,
    with n = normalize(ship.pos - robot.position)). The ship slides around the
    robot's surface, never through it.
  - ROBOT_RADIUS: get the real hull size from robots.py if it exists. If it
    does NOT expose one, REQUEST that the parent add a radius/half-extent
    accessor to Robot (state this in the Completion Report), and meanwhile use
    a clearly-labeled provisional constant justified by the visible hull scale.
  - ORDER OF RESOLUTION: resolve WALLS first, then ROBOTS (or iterate the two
    once more if a robot push lands you in a wall — a corridor robot sits in a
    tube, so a robot-push could nudge you toward a wall). Keep it simple and
    correct over clever. If both constraints fight in a tight tube, prefer
    STOP DEAD (prev_pos) over leaking through either surface.

### 5.4 Hostages & defeated robots are NOT solid
Defeated robots (is_defeated() True) are pass-through. Hostages are NOT
obstacles — you fly INTO them to rescue (that's the win, handled by
game_state.py). Do NOT make hostages collide. Only undefeated robots + rock
walls are solid.

## 6. PROBE-FIRST INSTINCT (Nir's hard-won lesson — honor it)
On THIS project, "obvious" things have repeatedly hidden landmines (e.g. an
Xbox trigger read as "fire" auto-killed robot #1 at startup; it took 5 probe
snippets and out-of-scope ingenuity to find). So: do NOT assume your math is
right because it looks right. Before declaring done, have Nir/DeepSeek RUN
SMALL PROBES, e.g.:
  - print hub.inside(ship.pos, margin=SHIP_RADIUS) each frame near a wall;
  - print the computed normal vector when blocked (sanity: it should point
    roughly back toward open space);
  - fly straight at a wall: confirm STOP, then strafe: confirm SLIDE;
  - fly at the doorway seam slowly: confirm NO jitter, NO trap;
  - fly straight at an undefeated robot: confirm STOP; defeat it: confirm you
    can now pass; fly at a defeated robot: confirm pass-through.
Give Nir these as an explicit numbered TEST CHECKLIST he can perform in 2 min.

## 7. WHAT YOU MUST NOT DO (scope fence — hard)
- Do NOT add/move/remove/duplicate flush_walls. Containment goes between
  ship.update and ship.apply_view ONLY.
- Do NOT edit hub_builder.py, corridor_builder.py, robots.py, combat.py,
  render.py, or any other module. If you need a new accessor (e.g. a robot
  radius), REQUEST it in the Completion Report; do not reach in.
- Do NOT reorder the canonical frame loop or touch rendering.
- Do NOT add any math-meaning or color logic (Prime Law).
- Do NOT make hostages or defeated robots solid.
- Do NOT introduce springs/cushions/bounce — HARD STOP + SLIDE only.
- Do NOT use shaders or modern GL. Legacy fixed-function only (you won't need
  GL at all — this is pure vector math on ship.pos/.vel).
- Keep your change SMALL and contained to app.py's loop (plus, if cleaner, a
  tiny self-contained helper file containment.py that app.py imports and calls
  with (ship, hub) — your choice; if you make a helper, it must be pure
  functions of (ship, hub) with no global state and no rendering).

## 8. DELIVERABLES
1. The containment code: either an edit to app.py's loop (show the EXACT
   before/after with enough surrounding lines that DeepSeek can place it
   unambiguously between ship.update and ship.apply_view), OR a small
   containment.py + the 1-2 lines app.py adds to call it. Prefer whichever is
   cleaner given the real app.py you were pasted.
2. A short COLLISION TEST CHECKLIST (numbered, §6) for Nir to fly.
3. A COMPLETION REPORT (template below).

## 9. COMPLETION REPORT TEMPLATE (fill this, Nir carries it to the parent)
- FILES CHANGED/ADDED (exact names).
- EXACT placement of the containment call in the frame loop (which two lines
  it sits between, quoted).
- CONSTANTS chosen (SHIP_RADIUS, ROBOT_RADIUS) + the geometry-based REASONING
  for each value, so DeepSeek can tune.
- HOW the surface normal is obtained (finite-difference details).
- REQUESTS TO PARENT (e.g. "Robot has no radius accessor — please add
  Robot.radius; I used provisional X").
- ANYTHING that surprised you in the pasted files (mismatches with this brief).
- CONFIRMED via probes? (list which probes were run and what they showed —
  remember Nir tests on screen, so describe the on-screen behavior).
- LOCKED PUBLIC INTERFACE (if you added containment.py: its function
  signatures).

## 10. ONE LAST THING
Respect this mission. It is NOT trivial — the doorway seam, the slide normal,
and the wall-vs-robot interaction are real problems. Read the real files first,
think at full depth, probe before you trust, and give Nir an exact way to
verify. When it stops the ship at solid rock and lets it slide gracefully, this
mission is laid to rest. Q.E.D. :-)
================================================================================
END OF BRIEF #C1
================================================================================
