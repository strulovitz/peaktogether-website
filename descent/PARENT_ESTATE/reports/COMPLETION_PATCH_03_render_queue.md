COMPLETION REPORT — render patch (translucency queue) — 2026-06-13
FILE PATCHED: render.py
REAL draw_wall SIGNATURE FOUND:
    def draw_wall(quad, fill_color, edge_color, fill_alpha):
ADDED SIGNATURES (verbatim):
    queue_wall(quad, fill_color, edge_color, fill_alpha)
    flush_walls(camera_pos)
USAGE CONTRACT:
    - draw_wall is UNCHANGED and still available for immediate single-wall use.
    - All ROCK-WALL geometry should be enqueued via render.queue_wall(...)
      during a module's draw(). Walls are NOT drawn at enqueue time.
    - The app frame loop calls render.flush_walls(ship.pos) EXACTLY ONCE per
      frame, AFTER all opaque + robot drawing, BEFORE billboards.
    - flush_walls sorts ALL queued walls far-to-near (squared centroid
      distance to the passed-in camera_pos), draws each via draw_wall, then
      clears the queue. render stores NO camera — stateless, camera passed in.
TRAP DOCUMENTED (loudly, in code + here):
    If a frame enqueues walls but nobody calls flush_walls(), those walls are
    SILENTLY NEVER DRAWN and the queue grows unbounded. The frame loop MUST
    call flush_walls() exactly once per frame.
DEVIATIONS: none.
    - Signature matched the brief's draft exactly; no adaptation needed.
    - numpy alias `np` (already imported) used.
    - No change to draw_wall, fog, billboards, TexCache, or any other function.
    - No other module's file touched. render remains mathematics-blind.