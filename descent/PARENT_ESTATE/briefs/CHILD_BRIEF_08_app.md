===========================================================
CHILD BRIEF #8 — app.py  (MINIMAL — integration checkpoint)
Project: DESCENT QED engine. You assemble the WHOLE verified stack into
ONE runnable program for the first time. You write NO gameplay.
===========================================================

WHO YOU ARE / FRESH-CHAT GATE:
You are the integrator. Every module you use is REAL, BUILT, and
VERIFIED — you wire them together, you do not reinvent them. You must
NOT guess any API. Your FIRST actions, before writing app.py, are to
ask Nir:
  "Please paste the COMPLETE current contents of, verbatim:
     1. render.py        (Ship, camera, fog, queue/flush, quat_look_along)
     2. level_parser.py  (load_level, Level)
     3. hub_builder.py   (build_hub, HubGeometry: spawn_pose, update,
                          draw_world, draw_robots, draw_labels, etc.)
     4. palette.py       (CLEAR_COLOR, set_fog colors, etc.)
     5. content_parser.py (only if I must construct a Palette/ledger to
                          pass to draw calls — see LEDGER QUESTION below)
   And tell me: which level manifest to load (e.g. levels/intro.txt),
   and how to launch (python app.py ? any args?)."
Do not reconstruct any of these from memory. Pasted files are LAW. If a
reminder below disagrees with a pasted file, the FILE wins — say so.

WHO ELSE IS INVOLVED:
- DeepSeek (Nir's builder, agentic in OpenCode): commits your verbatim
  code, mechanical tuning. Reliable, less clever than you.
- Nir: courier + TESTER. NOT technical, very smart. He will RUN app.py
  and FLY it, then send screenshots. Speaks for the parent (another
  Claude) who owns architecture. You have NO memory of other chats.
- You write a Completion Report (template at bottom). Nir carries it up;
  DeepSeek commits to /PARENT_ESTATE/reports/.

THE PRIME LAW (never violate):
The engine is MATHEMATICS-BLIND. app wires modules and runs the loop. It
does NOT interpret math, assign color meaning, or invent gameplay. Color
meaning lives only in palette (via a ledger), decided upstream.

============================================================
WHAT MINIMAL app IS — and IS NOT
============================================================
IS: the smallest real program that:
  - opens a window (pygame + OpenGL, matching how the demos did it —
    REUSE the exact init the existing *_demo.py files use; ask Nir to
    paste one demo, e.g. hub_demo.py, as your init reference),
  - load_level(<manifest>) -> Level,
  - build_hub(level) -> HubGeometry,
  - spawns a Ship at hub.spawn_pose(), aimed via render.quat_look_along,
  - runs ONE clean frame loop honoring the CANONICAL FRAME ORDER,
  - lets Nir FLY (WASD/arrows) through the whole assembled level:
    atrium -> a doorway -> down a bent corridor -> blue cavern -> back.

IS NOT (do NOT add any of these — they are later briefs #9/#10/#11):
  - NO reading_system, NO plaque/hologram reading interaction,
  - NO weapons, NO firing, NO robot defeat triggering,
  - NO game_state, NO rules, NO lock-on, NO hostage rescue, NO win/lose,
  - NO menu/level-select UI (hardcode ONE level path; a constant is fine),
  - NO HUD beyond optional tiny debug text.
If you feel tempted to add gameplay: STOP. This brief is an INTEGRATION
PROOF. Its success = "the assembled world renders correctly and is
flyable." Nothing more.

============================================================
THE CANONICAL FRAME ORDER — THE SPINE OF THIS BRIEF (locked invariant)
============================================================
Per frame, EXACTLY this sequence (this is engine canon; obey verbatim):

  1. handle events (quit, etc.)
  2. ship.update(dt, pygame.key.get_pressed())
  3. clear color+depth buffers
  4. render.set_fog(...)           # fog params from palette (see below)
  5. ship.apply_view()             # set camera from ship.q / ship.pos
  6. hub.update(dt, ship.pos)
  7. hub.draw_world(cr, cu, tc)    # QUEUES atrium + all corridor walls
  8. render.flush_walls(ship.pos)  # <-- EXACTLY ONCE. far->near sort+draw
  9. hub.draw_robots(cr, cu, tc)   # robot hulls/scanners/holograms
 10. hub.draw_labels(cr, cu, tc)   # billboards / door titles / mathtext
 11. pygame.display.flip()

  cr, cu = render.ship_right(ship.q), render.ship_up(ship.q)  # camera
     right/up vectors for billboards. VERIFY exact accessor names from
     pasted render (ship_right/ship_up/ship_forward(q)).
  tc = the TexCache instance (however the demos construct it — REUSE).

THE CARDINAL TRAP (engine canon — restate it in your report as
understood): if walls are QUEUED (step 7) but flush_walls (step 8) is
NOT called exactly once per frame, ALL WALLS VANISH SILENTLY — black
screen, no error. If Nir reports a black/empty world, the FIRST suspect
is a missing/misplaced/duplicated flush_walls. Call it ONCE, in slot 8,
AFTER draw_world, BEFORE robots/labels. Do not call it in draw_world
(hub_builder was explicitly told NOT to flush internally).

DRAW-ORDER NOTE (already settled, don't re-litigate): corridor robots
are drawn in hub.draw_robots AFTER flush (their opaque hulls still depth-
sort correctly; scanners/holograms are emissive). This matches what
corridor_builder/robots verified. You do NOT need the opaque/emissive
split for THIS minimal app — the three hub draw calls in order 7/9/10
around the single flush at 8 is the verified-correct sequence.

============================================================
LEDGER / TEXCACHE QUESTION — resolve EARLY, report what you found
============================================================
The hub/corridor draw calls take (cr, cu, texcache). Some draws may also
need a Palette(ledger) for tints/text colors. From the pasted files,
determine and STATE CLEARLY:
  - Does hub.draw_*(cr,cu,tc) take ONLY (cr,cu,texcache), or also a
    palette/ledger arg? Match the EXACT signatures in pasted hub_builder.
  - How is TexCache constructed in the demos? REUSE that verbatim.
  - If a Palette/ledger is needed anywhere, how did the demos build it?
    REUSE that. Do NOT invent color meaning — app just passes through
    whatever the demos already passed. If something is ambiguous, ASK
    Nir rather than guessing.
Your job is to PASS THROUGH exactly what the verified demos passed. If a
demo ran correctly, copy its construction of tc/palette/ship verbatim.

============================================================
SHIP SPAWN — use the verified helper
============================================================
  (spos, (yaw, pitch)) = hub.spawn_pose()      # radians, forward=-Z conv
  fwd = direction implied by (yaw,pitch) OR — simpler & verified — get
        the spawn DIRECTION from the first door normal. Two clean paths:
    PATH 1: hub.spawn_pose() gives (yaw,pitch); convert to a forward
            vector, then ship.q = render.quat_look_along(fwd).
    PATH 2: simpler — first door points INTO atrium; ship should look
            toward a doorway. Use the first entry of hub.door_poses()
            -> (center, outward_normal); aim ship from spos toward that
            door: fwd = normalize(center - spos); ship.q =
            render.quat_look_along(fwd). VERIFY which reads cleaner from
            the pasted files; PATH 1 is canonical (spawn_pose exists for
            this). Set ship.pos = spos either way.
  quat_look_along is VERIFIED (forward=-Z, all directions + NaN edge
  passed). Use it; do not hand-roll quaternions.

============================================================
FLIGHT CONTROLS — reuse the demos' Ship exactly
============================================================
ship.update(dt, keys) already implements WASD/arrows flight (the demos
used it). REUSE verbatim — do NOT rewrite flight. If the demos bound
extra keys (roll, speed), keep them. Add ONLY: ESC/window-close to quit.

============================================================
FOG / CLEAR — from palette, like the demos
============================================================
  render.set_fog(start=?, end=?, color=CLEAR_COLOR)   # copy the demos'
     fog values; they were tuned for corridor/hub reveal. Clear color =
     palette.CLEAR_COLOR. Do NOT invent new fog numbers — reuse verified.

============================================================
OPTIONAL (only if trivial, else SKIP): tiny debug overlay
============================================================
A few lines of debug text (fps, ship.pos, "inside: T/F" via hub.inside)
are OK ONLY if your render/demo already has an easy 2D-text path. If it
needs new infrastructure, SKIP IT — not worth risking the integration
proof. State whether you added it.

============================================================
WHAT YOU MUST NOT DO
============================================================
- Do NOT add gameplay (reading/weapons/rules/rescue/win-lose/menu).
- Do NOT modify render, palette, robots, corridor_builder, hub_builder,
  level_parser, content_parser. app is a CONSUMER. If you NEED a change
  in any of them, STOP and report it as a request to the parent.
- Do NOT call flush_walls anywhere but slot 8, exactly once.
- Do NOT invent fog numbers, color meaning, TexCache/Palette
  construction — REUSE the verified demos verbatim.
- Do NOT hand-roll quaternions (use quat_look_along).
- Do NOT put mathtext texture ids into display lists.

============================================================
WHAT SUCCESS LOOKS LIKE (Nir's flythrough acceptance)
============================================================
Nir runs `python app.py`, and:
  - a window opens onto the GREY ATRIUM, ship facing a doorway,
  - he flies around the atrium; N doorways visible, spread on the sphere,
    each framed, with title labels readable,
  - he flies OUT through a doorway, down a BENT corridor (fog reveals it
    gracefully), reaches the BLUE cavern at the end, turns, flies back,
  - robots (if any in the corridors) bob/track; scanners/holograms glow;
  - NO black screen (flush is correct), NO crash, NO z-fighting chaos,
  - it FEELS like one coherent world, not separate demos.
This is the milestone: the DESCENT QED world, assembled and flyable.

============================================================
COMPLETION REPORT (write this at the end)
============================================================
  COMPLETION REPORT — app (minimal integration) — <date>
  FILE: app.py. Run-verified by Nir? (Y/N + screenshots) — likely N at
     write time; Nir flies it next.
  LAUNCH: exact command (python app.py), level loaded (manifest path),
     keys (flight + quit).
  FRAME ORDER: paste your actual loop (steps 1-11) and CONFIRM
     flush_walls is called exactly once in slot 8. Restate the cardinal
     trap as understood.
  SIGNATURES CONSUMED: exact hub.draw_*/update/spawn_pose/door_poses
     signatures you called; how cr,cu,tc (and palette/ledger if any)
     were constructed (verbatim from which demo).
  SPAWN: PATH 1 or 2; how ship.q was set via quat_look_along.
  REUSE: which demo's window/GL init + Ship + fog you copied verbatim.
  DEBUG OVERLAY: added? (Y/N + how).
  DEVIATIONS / TRAPS / REQUESTS TO PARENT (any change you needed in a
     consumed module — request, do NOT make it).
  OLD-CODE REUSE: anything from Fable.
  DEEPSEEK TODOS: tuning (fog/spawn distance/atrium radius if cramped),
     and the flythrough acceptance checklist above for Nir.
Nir carries this to the parent; DeepSeek commits to
/PARENT_ESTATE/reports/.
===========================================================