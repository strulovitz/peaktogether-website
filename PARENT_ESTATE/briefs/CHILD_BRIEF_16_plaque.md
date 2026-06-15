# CHILD BRIEF #16 — IN-WORLD PROOF PLAQUE (defeated robot leaves a readable proof billboard)

────────────────────────────────────────────────────────
0. WHAT YOU ARE BUILDING (ONE concern, nothing else)
────────────────────────────────────────────────────────
DESCENT QED is a 6-DOF flying game. A couple flies one spaceship down corridors to rescue
hostages. Robots block the corridor; each robot is destroyed by firing the correct
"mathematician-missile". EACH CORRIDOR IS A COMPLETE MATHEMATICAL PROOF (e.g. the Basel
problem: full infinite series, the Riemann zeta function, Fourier series, Parseval's
identity, contour integrals — real, dense, multi-line mathematics).

When a robot is defeated, it must leave a PLAQUE floating at its position in the corridor:
a transparent, beautiful, SINGLE-PANEL billboard that displays that robot's full
`explain['mathematician']` content (the full proof mathematics), rendered with the SAME
visual quality as the game's existing "Understanding Mode". The player flies up to it on
the way through/back and reads it. Title line reads "VICTORY #N" where N is the robot's
number. It has transparency and a dark translucent backing card, like a glowing road sign
floating in fog.

THE BUG TODAY: the plaque code calls `texcache.get_mathtext(text, ...)` on the explanation.
`get_mathtext` renders ONE pure-math expression — it cannot handle multi-line dense proof
text, so it produces a WHITE RECTANGLE. You will route the plaque through the RICH text path
instead (the same path Understanding Mode uses), and draw it as a 3D world-space billboard.

You build ONLY this. You write code; DeepSeek (the builder) commits/tunes it; Nir (the human,
non-technical, cannot read code) runs and flies it. Your demo must make success/failure
VISIBLE ON SCREEN — never ask Nir to debug.

────────────────────────────────────────────────────────
1. FRESH-CHAT GATE — DO THIS FIRST, BEFORE ANY CODE
────────────────────────────────────────────────────────
You have NO memory of this project. DO NOT GUESS ANY API. Your FIRST action is to ask Nir to
paste, verbatim and complete:
  (a) render.py  — you need the EXACT bodies/signatures of: draw_billboard, render_rich,
      get_rich, rich_to_surface (and whatever get_rich calls to build a surface),
      get_mathtext, latex_to_surface, surface_to_texture, the TexCache class, ship_right,
      ship_up. Also how billboards set/restore GL blend + texture state.
  (b) corridor_builder.py — the full file. You will edit the `_draw_plaques` method and you
      need the constants PLAQUE_SCALE and LABEL_LIFT and how `_draw_plaques` is called from
      `draw_labels`.
  (c) understanding.py — the full file. THIS IS YOUR VISUAL REFERENCE. It renders these exact
      proof explanations today via render_rich/get_rich. You will COPY its background color
      (BG_COLOR), its title+body composition pattern, fontsize, and alpha handling so the
      plaque looks like ONE Understanding-Mode layer.
  (d) corridors/maxwell.txt — the REAL fixture. You MUST read an actual EXPLAIN_MATHEMATICIAN
      block so you know what your renderer must survive: full multi-line proof mathematics,
      NOT "a little math". Do not start coding until you have read a real one.

PASTED FILES ARE LAW. If this brief disagrees with a pasted file, THE FILE WINS — and you
note the discrepancy in your Completion Report. Never reinvent an API that already exists.

────────────────────────────────────────────────────────
2. THE PRIME LAW — MATHEMATICS-BLINDNESS (never violate)
────────────────────────────────────────────────────────
The engine NEVER interprets what mathematics MEANS. For your module: you render whatever
LaTeX/math string the fixture provides, as OPAQUE content. You never parse, simplify,
validate, truncate-by-meaning, or interpret it. You never hardcode a color to a mathematical
meaning. A plaque is simply "render this robot's explain['mathematician']" — you do not care
what it says.

────────────────────────────────────────────────────────
3. ENGINE CANON — FRAME ORDER & THE CARDINAL FLUSH TRAP
────────────────────────────────────────────────────────
Canonical per-frame order (do not change it):
  1 glClear  2 ship.update  3 ship.apply_view  4 set_fog  5 cr=ship_right,cu=ship_up
  6 hub.update  7 hub.draw_world (QUEUES walls only)  8 render.flush_walls (EXACTLY ONCE)
  9 hub.draw_robots  10 hub.draw_labels  11 HUD/overlays  12 flip
Plaques are drawn inside step 10 (hub.draw_labels → _draw_plaques). YOUR CHANGES STAY INSIDE
`_draw_plaques`. You must NOT add, move, remove, or duplicate any flush_walls call. If
flush_walls is disturbed, ALL WALLS VANISH SILENTLY (black screen, no error). Do not touch it.

────────────────────────────────────────────────────────
4. THE CURRENT BROKEN CODE (verbatim, from corridor_builder.py _draw_plaques)
────────────────────────────────────────────────────────
def _draw_plaques(self, cr, cu, texcache):
    text_rgb = self._palette.text_color_on(self._dominant_key)
    for r, rdata, (pose, _yaw) in zip(self._robots, self._robots_data, self._station_poses):
        if not r.is_defeated():
            continue
        explain = getattr(rdata, "explain", {}) or {}
        text = explain.get("mathematician", "")
        if not text:
            text = (getattr(rdata, "briefing_hint", "") or "—")
        tex = texcache.get_mathtext(text, color=text_rgb, fontsize=13)   # ← THE BUG
        center = np.asarray(pose, dtype=float) + np.array([0.0, LABEL_LIFT, 0.0])
        render.draw_billboard(tex, tuple(center.tolist()), cr, cu,
                              scale=PLAQUE_SCALE, alpha=0.9)
Constants: PLAQUE_SCALE = 0.7, LABEL_LIFT = 2.2.
NOTE: rdata.number is the robot's number — use it for "VICTORY #N". VERIFY the field name
from the pasted file (parent says RobotData.number exists).

────────────────────────────────────────────────────────
5. THE FIX — EXACTLY WHAT TO DO
────────────────────────────────────────────────────────
The key fact: get_rich(...) returns the SAME (tid, w, h) texture tuple that get_mathtext
returns, and render_rich is the renderer Understanding Mode uses to display these exact proofs
correctly. Therefore a rich-text texture can be fed straight into draw_billboard to make a 3D
world-space proof plaque.

5.1 Build the texture via the RICH path, not the mathtext path:
    - Compose the plaque string as a title line "VICTORY #{rdata.number}" followed by the body
      explain['mathematician'] — composing them EXACTLY the way understanding.py composes its
      layer title + body (copy that pattern verbatim so the plaque matches a U-mode layer).
    - Call texcache.get_rich(...) (use its REAL signature from pasted render.py; parent says it
      is roughly get_rich(self, text, color, fontsize, blur) → (tid, w, h)). Match the fontsize
      and color/BG that understanding.py uses for a layer so quality is identical.

5.2 Draw a dark translucent BACKING CARD then the rich texture, as camera-facing billboards:
    - First draw a semi-transparent dark quad (use cr, cu; slightly larger than the text quad)
      using the SAME BG_COLOR/alpha understanding.py uses for its panel, so the plaque reads
      as a dark glowing card (the "road sign in fog" look) — NOT raw text floating in space.
    - Then draw the rich texture via draw_billboard(tex, center, cr, cu, scale, alpha).
    - IMPORTANT: read the pasted draw_billboard / rich_to_surface code. If the rich texture
      ALREADY bakes a background, do NOT double it — drop the backing quad and just tune alpha.
      Match whatever blend mode the surrounding billboard/label code uses, and RESTORE all GL
      state (blend, GL_TEXTURE_2D, glColor) exactly as you found it. Do not leak GL state.

5.3 Keep everything else as-is: still inside the _draw_plaques loop, still only for
    r.is_defeated() robots, still positioned at pose + LABEL_LIFT, still camera-facing.

────────────────────────────────────────────────────────
6. THE REAL RISK — YOU MUST VERIFY, NOT ASSUME
────────────────────────────────────────────────────────
NOBODY HAS YET RENDERED A FULL PROOF through render_rich. Understanding Mode shows these
proofs, so it SHOULD hold — but you must CONFIRM against the real input:
  - When Nir pastes a real EXPLAIN_MATHEMATICIAN block, READ IT, and render it through the
    plaque path. Does render_rich handle the full MULTI-LINE, dense math? Does it wrap/lay out
    long content, or does it CLIP / OVERFLOW / produce garbage?
  - DO NOT TRUNCATE OR SIMPLIFY THE MATHEMATICS to make it fit. A truncated proof is worse than
    useless and violates the Prime Law's spirit. Render it FAITHFULLY in full, or report that
    you can't.
  - If render_rich CANNOT render a full proof billboard, build what renders faithfully, and in
    your Completion Report state EXACTLY what broke, paste the exact failing input, and add a
    REQUEST TO PARENT for the missing capability (e.g. "render_rich needs width-wrapping / a
    paged or scrollable billboard for full-proof-length content"). The parent will then write a
    renderer-upgrade brief. Reporting the limitation honestly is SUCCESS; faking it is failure.

────────────────────────────────────────────────────────
7. SCOPE FENCE — WHAT YOU MUST NOT DO
────────────────────────────────────────────────────────
  - Do NOT touch ship movement, walls, robot collision, joystick, game state, or combat. This
    brief is the plaque ONLY.
  - Do NOT build a new text renderer. Use the EXISTING get_rich/render_rich/draw_billboard. If
    they are insufficient for full proofs, REQUEST an enhancement from the Parent — do not hack
    a parallel renderer.
  - Do NOT turn this into Understanding Mode. It is ONE in-world billboard, not the 4-layer
    overlay, no key-press, no depth panels.
  - Do NOT change plaque triggering (still inside draw_labels, still for is_defeated robots).
  - Do NOT add, move, remove, or duplicate flush_walls. Do NOT reorder the frame loop.
  - Do NOT truncate/alter the mathematical content. Do NOT leak GL state.

────────────────────────────────────────────────────────
8. THE DEMO — `plaque_demo.py` (Nir RUNS this to verify on screen)
────────────────────────────────────────────────────────
Make one flyable demo. Reuse app.py's init/frame-loop VERBATIM where possible (copy, don't
reinvent) to avoid regressions. Acceptance, all visible on screen with NO code reading:
  1. Load the Maxwell level; fly to the first robot; fire the CORRECT mathematician → it dies.
  2. A plaque appears at the dead robot's position titled "VICTORY #1", showing the FULL
     mathematician explanation rendered beautifully (words + full equations), at the SAME
     quality as Understanding Mode — NOT a white rectangle, NOT raw LaTeX source, NOT clipped
     garbage.
  3. The plaque is a transparent dark card (road-sign look), faces the camera, readable as you
     fly up to it.
  4. Defeat a second robot → its plaque reads "VICTORY #2" with ITS own proof.
  5. If a full proof does NOT fit / render_rich breaks on it: the demo STILL RUNS, the plaque
     shows what it faithfully can, and the Completion Report documents the limitation with the
     exact failing input + a REQUEST TO PARENT. (No silent truncation.)
Expose tunables as named constants for DeepSeek: PLAQUE_SCALE, LABEL_LIFT, plaque BG color/alpha,
fontsize.

────────────────────────────────────────────────────────
9. COMPLETION REPORT (fill out, Nir carries it back to the Parent)
────────────────────────────────────────────────────────
FILES CHANGED/CREATED:
  - corridor_builder.py (_draw_plaques rewritten — describe)
  - plaque_demo.py (new)
RUN-VERIFIED ON SCREEN? (Nir flies it — describe what he sees for acceptance items 1–5)
ACTUAL SIGNATURES OBSERVED (verbatim from pasted render.py):
  - get_rich(...) = ...
  - render_rich(...) = ...
  - draw_billboard(...) = ...
HOW UNDERSTANDING MODE COMPOSES TITLE+BODY (the pattern I copied): ...
THE KEY QUESTION — DID render_rich SURVIVE A REAL FULL PROOF?
  - real EXPLAIN_MATHEMATICIAN block tested: <identify/paste it>
  - result: rendered fully / clipped / overflowed / broke (describe exactly what appeared)
  - if it broke: REQUEST TO PARENT = <the renderer capability needed, with the failing input>
GL STATE: confirmed all blend/texture/color state restored? (yes/no)
FLUSH: confirmed flush_walls untouched? (yes/no)
DEVIATIONS / DISCREPANCIES vs this brief: ...
DEEPSEEK TODOs (mechanical tuning): tune PLAQUE_SCALE, LABEL_LIFT, BG alpha, fontsize.
