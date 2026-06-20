# BRIEF #10 — ARSENAL / WEAPONS  (FINAL, self-contained)
# DESCENT QED · mission for a fresh child Claude
# Every interface below was verified against the live repo by DeepSeek.
# DO NOT research the repo. DO NOT explore other modules. DO NOT guess APIs.
# Everything you need is here. If something seems wrong, STOP and ask the parent.

## 0. WHAT YOU ARE BUILDING (one concern only)
Replace the temporary '['/']' selector and the hardcoded ARSENAL with a proper
per-corridor ARSENAL: mathematician-missiles DERIVED from the CURRENT corridor's
robots. The girlfriend selects with an Xbox controller (mouse as alternate).
Firing shows a visible projectile, then the existing match logic resolves.
Build ONLY this. Touch nothing else.

## 1. THE PRIME LAW — MATHEMATICS-BLINDNESS (inviolable)
The engine NEVER interprets math meaning, judges correctness, or maps color to
meaning. It matches OPAQUE ids only:
    loaded_id == robot.required_technique_id  -> kill.
The arsenal is just (technique_id, name, portrait_path). Names/portraits are
display only. If you find yourself "understanding" the math, stop — you are
breaking the law.

## 2. VERIFIED INTERFACES (real; use exactly)

# combat.py — methods app.py calls each frame, and the constant to DELETE:
#   DELETE this hardcoded constant entirely:
#       ARSENAL = [
#           ("gauss_e","Gauss"), ("gauss_m","Gauss"), ("faraday","Faraday"),
#           ("ampere","Ampere"), ("maxwell","Maxwell"),
#       ]
#   Existing method signatures (keep callable; params change per section 6):
#       def handle_input(self, fire_edge, prev_edge, next_edge, ship, hub):
#       def update(self, dt, ship, hub):
#       def draw_hud(self, cache, win_size):
#       @staticmethod
#       def blocking_robot(hub):

# Corridor robots (arsenal source):
#       hub.corridors[0].get_robots()   # list of runtime Robot objects, file order
#   Each Robot has: .name (str), .required_technique_id (str), .position

# render.py 2D primitives (call between begin_2d/end_2d):
#       def begin_2d(w, h):
#       def end_2d():
#       def draw_text_mathtext_2d(cache, latex, x, y, color=(0.7,0.7,0.7),
#                                 fontsize=15, scale=1.0, alpha=1.0):
#       def draw_texture(tex, x, y, scale=1.0, alpha=1.0):  # tex = (tid, w, h)
#   NO 2D rect/line primitives exist. For panel borders / projectile streak use
#   raw glBegin(GL_QUADS)/glBegin(GL_LINES) INSIDE begin_2d/end_2d. Do NOT use
#   draw_box_edges (it is 3D).

# Portrait texture loading (REUSE this — do NOT invent):
#   robots.py has a PUBLIC loader: load_portrait(name)  (robots.py line 173).
#   It returns a (tid, w, h) tuple (or None) and caches in module dict
#   _PORTRAIT_CACHE (key = filename str). Import and call it:
#       from robots import load_portrait
#       tex = load_portrait(weapon["name"])   # -> (tid, w, h) for draw_texture
#   The filename rule it uses internally is:
#       name.strip().replace(" ", "_") + "-hologram.png"   (PNGs in repo root)
#   You only need the inline filename rule for your arsenal dict; pass NAME to
#   load_portrait to get the tex. Do NOT touch _PORTRAIT_CACHE directly.

## 3. CORE CHANGE — DERIVE THE ARSENAL FROM THE CORRIDOR
Add (mathematics-blind; ids/names/filenames only):

    def build_arsenal(robots):
        """robots = hub.corridors[0].get_robots(), file order.
        Returns list of dicts {"id","name","png"}, de-duped by id, first-seen."""
        seen, arsenal = set(), []
        for r in robots:
            tid = r.required_technique_id
            if tid in seen:
                continue
            seen.add(tid)
            png = r.name.strip().replace(" ", "_") + "-hologram.png"
            arsenal.append({"id": tid, "name": r.name, "png": png})
        return arsenal

NOTES:
- technique_ids are unique only WITHIN a corridor -> per-corridor dedup is right.
- The same historical NAME may appear twice under two different ids (e.g. two
  Gauss laws). Those are TWO DIFFERENT weapons — keep both. Dedup by id, not name.
- Source is hub.corridors[0].get_robots(). Max 9 weapons (matches 3x3 grid).

## 4. THE FACE PANEL (2D overlay, cockpit-weapon feel)
In draw_hud, inside begin_2d/end_2d, draw one FACE THUMBNAIL per arsenal entry
in a 3x3 GRID (slot 0 top-left, left-to-right, top-to-bottom; slot order =
arsenal order). Get each face via:  tex = load_portrait(weapon["name"]); if tex
is not None: draw_texture(tex, x, y, scale=...). Draw the NAME under each face
with draw_text_mathtext_2d. Highlight the LOADED weapon with a bright border
(glBegin(GL_LINES) rectangle). DOCTRINE: show ONLY this corridor's weapons (from
build_arsenal); NEVER a global list. Think classic Descent cockpit "selected
weapon" readout — readable, not cluttered.

## 5. SELECTION — XBOX CONTROLLER (primary) + MOUSE (alternate)
Opened joystick: gamepads.manip_joy (in GamepadManager). Verified pygame indices:
    A=button 0, B=button 1, X=button 2, Y=button 3, LB=button 4, RB=button 5,
    LT=axis 4, RT=axis 5.

Grid nav (3x3, slots 0..8; current = loaded slot):
    Y -> UP (slot-=3)   A -> DOWN (slot+=3)   B -> RIGHT (slot+=1)   X -> LEFT (slot-=1)
Clamp/ignore moves leaving the grid or landing on an empty slot. On a valid move:
loaded_id = arsenal[slot]["id"].

Linear cycle:
    LB -> previous weapon (index-=1, wrap)    RB -> next weapon (index+=1, wrap)

Fire:
    LT or RT (axis 4 / axis 5; value > 0.5 == press) -> FIRE.

ALL controller input must be EDGE-DETECTED (act once per press). Store previous
button/axis states on the Combat object; compare each frame.

MOUSE (alternate): clicking a face loads that weapon. app.py will pass the click
edge + position into handle_input (see section 6). If the mouse coords fall
inside a face's rect, set loaded_id to that weapon.

## 6. INTEGRATION CONTRACT WITH app.py (the parent wires app.py — see below)
The parent has ALREADY confirmed these app.py edits (you do NOT make them, but
code against them):

  Mouse capture added inside the events loop (app.py ~line 181):
      elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
          mouse_click_edge = True
          mouse_x, mouse_y = ev.pos
  (with `mouse_click_edge = False; mouse_x = mouse_y = 0` before the loop)

  The handle_input call (app.py ~line 225) becomes:
      combat_state.handle_input(fire_edge, prev_edge, next_edge, ship, hub,
                                mouse_click_edge, mouse_x, mouse_y)

So your new signature MUST be:
      def handle_input(self, fire_edge, prev_edge, next_edge, ship, hub,
                       mouse_click_edge, mouse_x, mouse_y):

Inside handle_input:
  - Read gamepads.manip_joy buttons/axes for the controller scheme (section 5)
    and do your own edge detection there.
  - Use mouse_click_edge + (mouse_x, mouse_y) for mouse face selection.
  - fire_edge (SPACE) may remain as a keyboard fire fallback; prev_edge/next_edge
    ('['/']') are RETIRED — ignore them (the parent keeps the params only so the
    existing call site stays valid). Do not implement '['/']' selection.
  - Keep update, draw_hud, blocking_robot working.
State your final signature in the completion report so the parent can confirm.

## 7. PROJECTILE (cosmetic only)
On fire, show a projectile from ship toward the target robot, then run the
EXISTING resolve logic. If the parent provides a world billboard primitive, reuse
it; otherwise draw a bright streak with glBegin(GL_LINES). Purely visual — the
kill is still the opaque id match. Keep existing resolve: correct id -> robot
defeat + existing auto-face; wrong id -> existing 6-second gentle FIZZLE clue.
NO punishment ever — do not change fizzle behavior.

## 8. THE CANONICAL FRAME ORDER — DO NOT DISTURB
walls are only QUEUED by draw_world; render.flush_walls is called EXACTLY ONCE in
app.py. You MUST NOT add, move, or remove any flush_walls call. Your panel draws
in the HUD/overlay step (begin_2d/end_2d). A 3D projectile must draw AFTER
flush_walls and BEFORE the 2D overlays — confirm exact placement with the parent
rather than guessing.

## 9. SCOPE FENCE — DO NOT
- Do NOT interpret math / judge correctness / hardcode color->meaning.
- Do NOT keep or reintroduce a hardcoded global ARSENAL.
- Do NOT touch _PORTRAIT_CACHE directly; use load_portrait(name).
- Do NOT invent texture loading.
- Do NOT add/move/remove flush_walls.
- Do NOT edit app.py, render.py, robots.py, or any other module. The parent
  already wired the app.py mouse + call-site changes in section 6.
- Do NOT change fizzle/no-punishment behavior.
- Build ONLY: build_arsenal + face panel + controller/mouse selection +
  projectile. Nothing else.

## 10. COMPLETION REPORT (fill in for the parent)
- build_arsenal location + behavior: ____
- Final handle_input signature: ____
- Controller mapping (Y/A/B/X, LB/RB, LT/RT) — confirm edge-detected: ____
- Mouse selection implemented (hit-test against face rects): ____
- Face textures via load_portrait(name): confirm ____
- Projectile primitive used + frame placement: ____
- '['/']' selection removed (params ignored): confirm ____
- flush_walls untouched: confirm ____
- Anything you had to request from the parent: ____

END OF BRIEF #10
