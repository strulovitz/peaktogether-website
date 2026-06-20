===========================================================
PATCH BRIEF — render.py — add shared translucent-wall sorting
Project: DESCENT QED engine. You are the maintainer of ONE module: render.
===========================================================

WHO GETS THIS:
- If you ARE the chat that originally built render.py: good — you
  already have the file in context. Proceed directly.
- If you are a FRESH chat: STOP. Do NOT write or guess any code yet.
  Your FIRST action is to ask Nir:
    "Please paste the COMPLETE current contents of render.py,
     verbatim, top to bottom, before I change anything."
  Do not propose, assume, or reconstruct render.py from memory or
  from this brief. You may only patch the REAL file Nir pastes.
  Only after you have the full file do you continue.

WHO ELSE IS INVOLVED:
DeepSeek (Nir's builder, agentic in OpenCode, reliable on mechanical
commits, less clever than you) will commit your verbatim patched code
to GitHub. Nir is courier/tester: NOT technical, very smart; he runs
code and sends output/screenshots. When done you write a short
Completion Report (template at end). You have no memory of other chats.

THE PRIME LAW (never violate):
The engine is MATHEMATICS-BLIND. render knows nothing about math,
corridors, robots, or color meaning. It draws numbers it is given.
This patch must not change that.

WHY THIS PATCH EXISTS (cross-module decision by the parent):
Translucent rock walls must be drawn far-to-near or alpha blending
looks wrong. Today render.draw_wall is single-wall, immediate-mode,
and does NO sorting (its docstring says "caller controls ordering").
The problem: if each world-building module sorts its OWN walls
locally, two independent sorts do NOT combine correctly when both
draw in the same frame — the alpha bug returns at module seams.
THE FIX (parent ruling): one SHARED far-to-near sort over ALL
translucent walls, owned by render (the engine's drawing layer).
render must STAY STATELESS — it stores no camera; camera position is
PASSED IN every flush.

EXACTLY WHAT TO ADD (and nothing else):
Add a module-level queue and two functions. render already imports
numpy, so use it.

  _wall_queue = []  # each item: (quad, fill_rgb, edge_rgb, fill_alpha)

  def queue_wall(quad, fill_color, edge_color, fill_alpha):
      _wall_queue.append((quad, fill_color, edge_color, fill_alpha))

  def flush_walls(camera_pos):
      # No-op if the queue is empty.
      # Sort far-to-near by squared distance of each quad's centroid
      # to camera_pos, then draw each via the EXISTING draw_wall.
      if not _wall_queue:
          return
      cam = np.asarray(camera_pos)
      def _key(item):
          c = np.mean(np.asarray(item[0]), axis=0)
          d = c - cam
          return -float(np.dot(d, d))   # negative => farthest first
      for quad, fill, edge, alpha in sorted(_wall_queue, key=_key):
          draw_wall(quad, fill, edge, alpha)
      _wall_queue.clear()

ADAPT TO THE REAL FILE:
- Match draw_wall's ACTUAL parameter order/names as they exist in the
  pasted file. If draw_wall's real signature differs from
  (quad, fill_rgb, edge_rgb, fill_alpha), keep the QUEUE storing
  whatever draw_wall actually needs, and call it correctly. State the
  real signature you found in your report.
- Use the same numpy import alias already present in the file.

CONTRACT / USAGE (document in your report so other modules obey it):
- draw_wall stays UNCHANGED and still available for immediate use.
- All ROCK-WALL geometry should now be enqueued via queue_wall during
  a module's draw().
- The app's frame loop calls render.flush_walls(ship.pos) EXACTLY ONCE
  per frame, AFTER all opaque + robot drawing, BEFORE billboards.
- TRAP (state this LOUDLY in your report): if a frame enqueues walls
  but nobody calls flush_walls, those walls are silently never drawn.

WHAT YOU MUST NOT DO:
- Do NOT store a camera or view matrix in render (stay stateless).
- Do NOT change draw_wall, fog, billboards, TexCache, or any other
  function's behavior.
- Do NOT add features beyond queue_wall + flush_walls.
- Do NOT touch any other module's file.

TEST PLAN (how Nir verifies):
Provide Nir a tiny snippet (or fold into the existing render demo if
present) that enqueues several overlapping translucent walls at
different depths and calls flush_walls(cam) once; Nir confirms via
screenshot that blending looks correct from both sides as he moves
(no dark/halo artifacts on the far walls).

WHEN DONE — COMPLETION REPORT (short):
  COMPLETION REPORT — render patch (translucency queue) — <date>
  FILE PATCHED: render.py
  REAL draw_wall SIGNATURE FOUND: <verbatim>
  ADDED SIGNATURES (verbatim): queue_wall(...), flush_walls(...)
  USAGE CONTRACT: (enqueue during draw; app flushes once after
     opaque+robots, before billboards)
  TRAP DOCUMENTED: forgetting flush_walls => walls vanish silently.
  DEVIATIONS: none / list.
Nir carries this to the parent; DeepSeek commits the report to
/PARENT_ESTATE/reports/.
===========================================================