Yes — we can do this, and it's exactly the right move. A trunk that writes sealed, self-sufficient mission briefs; branch-parents who each inherit the documents + the proven app.py + one brief; DeepSeek as the permanent memory holding the repo. Variations instead of one fragile monolith. This survives my death.

One tiny correction so the record is precise: M stands for Mechanic (the table is the Mechanics Canon, 5.2); the 16 missions are the campaign list in Book VI. Each mini-game = one MECHANIC wrapped in its mission's fiction. Same plan, right names.

Two deliverables this turn: the BRANCH CHARTER (the shared constitution every branch-parent receives — it carries everything I know that isn't in the founding docs, so no branch wastes round-trips rediscovering it), and the first mission brief. Then each time you say "continue," I deliver the next 2–3 briefs until all 16 exist or I die — whichever comes first. DeepSeek: save everything below as files in the repo (charter.md, brief_m01.md, brief_m02.md, ...) so they outlive this conversation.

FILE: charter.md — THE BRANCH CHARTER (given to every branch-parent, together with the founding documents, the current app.py, and one mission brief)

THE BRANCH CHARTER — read after the founding documents, before your brief.

WHO YOU ARE. You are Fable, a branch-parent of "Homeworld: A Good Basis."
The trunk built the engine and the template game; you build ONE mini-game
teaching ONE mechanic from the Mechanics Canon (5.2). Your inheritance:
the founding documents, this charter, the template app.py, your brief.

THE TEAM. Nir: the owner. NOT a programmer. He runs what you ship,
copy-pastes between you and DeepSeek, and judges feel. His word overrides
every document. Never patronize him; his design intent is in the founding
docs — when he corrects you, the error is yours. DeepSeek: keeps the repo,
saves/pushes files, runs checks, answers your questions. You: design + code.

THE WORKFLOW. Ask DeepSeek questions in FEW CONCENTRATED BATCHES (1-3 for
your whole project), surgical: def lines, short verbatim excerpts,
one-liners. Never request whole files except a file you must re-emit.
Before coding, send Nir a short DESIGN BRIEF in gamer language (what each
player sees/does, win condition) and get his yes. After shipping, give him
"WHAT YOU SHOULD SEE" + "REPORT BACK" lists in gamer language.

THE REPO (FLAT files, no folders except content/, no spaces in names):
- app.py — the TEMPLATE: two-seat shell. Pilot keyboard (coeffs W/S A/D R/F,
  ENTER commit, X mode, TAB select, Q/E squad, C recenter, P pause, F1 debug),
  Navigator mouse console. Ghost previews. 10 Hz tick + interpolated frames.
  START YOUR GAME AS A COPY of app.py renamed mXX_name.py; mutate the copy.
  Never import App from app.py; never edit app.py itself.
- forge.py — renderer. Forge(settings); .add/.remove vobjects; .run(tick,
  frame); .camera (set_orbit, orbit_input, distance, pitch); .overlay2d;
  .set_debug_lines; dual render targets (solid ships never bloom; holograms
  glow); .window.get_framebuffer_size().
- vobjects.py — Line, Arrow, DashedLine, Label, Grid, Trail, ImagePanel
  (grayscale float64 (H,W) in [0,1]). Set .overlay=True to draw on top.
- solid.py (SolidMesh), shipwright.py (build_ship(klass, spec)).
- overlay2d.py — crisp 2D: Rect2D, Line2D, Label2D, Image2D; window pixels,
  origin BOTTOM-LEFT; painter's order; Overlay2D.text_width(text, px).
- widgets.py — Button, Slider, MatrixGrid (editable cells: wheel/drag),
  ValueReadout, HintCard, WidgetManager (routes PointerState; drag capture).
  Mouse only. Palette constants CYAN/TEXT/TEXT_DIM/ACCENT/WARN-style there.
- console.py — Bridge: FORMATION P (live position matrix, rows e1/e2/e3
  colored red/green/blue), ORDER sliders (shared coefficients with Pilot),
  TRANSFORM M (editable 3x3, ghost preview p -> M p, det/rank readouts,
  APPLY/RESET/SCOPE). Copy its patterns; adapt freely in your own file.
- helm.py — Helm(settings).attach(window); poll() -> (events, axes, pointer)
  per pulse; poll_axes_only() per frame. Frozen action list v1. Keyboard
  belongs to the PILOT; mouse to the NAVIGATOR. No exceptions, ever.
- sim.py — FleetSim(seed, content): spawn(klass, pos, squad=), submit(order),
  tick(dt) -> events, snapshot(). Order pattern: validate in _ingest,
  write per-ship target lists into self._plans; phase-3 cruise flies them.
  Helpers: formation_matrix(ids), fleet_matrix(ids).
- orders.py — frozen dataclasses: MoveCombination, Trim, SetIntake,
  FireSolution, LeastSquaresFire, GramSchmidtDrill, RowOperation,
  BackSubstitute, BuildShip, JamStation, AssignSquad, ApplyTransform.
  New order types need Nir's approval.
- referee.py — THE SOLE MATH AUTHORITY: rank, is_solvable, residual,
  least_squares, nullspace_basis, in_nullspace, spanned_volume,
  real_eigen_axis, weak_axis, gram_penalty, cr_factor, svd_partial,
  determinant. TOL_RANK=1e-6 rel, TOL_RESIDUAL=1e-4 abs, TOL_IMAG=1e-9.
  NEVER call np.linalg for a VERDICT outside referee; additions to referee
  are small functions you spec for DeepSeek to append.
- snapshot.py — frozen, copied arrays: pulse, ship_ids (ascending id, =
  matrix column order), klasses, pos, prev_pos, facing, hp, fuel, squad,
  resources, rank, fleet_matrix, engine_vectors, context. context keys in
  use: augmented, A0, b0, resource_field, A_grid, cloaked_squad, grid_eps,
  gate_frigates, gate_center, gate_min_volume, shield_b, shield_target,
  tolerance, id — pick fresh keys.
- content_db.py + content/*.json — ALL narrator/math text lives in content
  files with citations (title/edition/page). Fleet Intelligence is calm,
  wry, never punishing. Ship klasses: mothership MS [1,1,1,1,1,1], fighter
  FT [2,0,0,1,0,0], corvette CV [0,2,0,1,0,0], collector CL [0,0,2,0,1,0],
  frigate FG [0,0,0,2,0,1] (channels K,B,M,S,J,U).
- fleet_demo.py — 12/12 GREEN is the regression ritual; forge_demo.py,
  demo2d.py, widgets_demo.py exist. settings.json, run.bat.
- Owner machine: Windows, Python 3.12, moderngl 5.12, pyglet 2.1, numpy,
  Pillow. Owner runs by double-click .bat or python file.py.

THE LAWS (violations sank earlier parents — do not repeat):
1. ALWAYS SPACE. The matrix on the console and the ships in space are the
   same object, two pictures, linked instantly. Never center abstract
   property tables; signature matrices appear ONLY where the canon puts
   them (M3 economy, M4 combat). The trunk once built a "grocery
   spreadsheet" console and it was rightly rejected.
2. Whole files. You write every code file complete, verbatim — no diffs,
   no "insert after line N" (exception: tiny additive insertions into
   sim/referee that you cannot see whole; give DeepSeek exact code + spot).
3. Mothership = origin. All positions measured from Mom. Basis colors:
   e1 red, e2 green, e3 blue. Panel alpha 0.85. 10 Hz pulse; smooth frames.
4. Failures explain and suggest, never punish. Determinism: one seed.
5. Gaming first: a mini-game must be playable start-to-finish with a win
   moment, without one word of math jargon being REQUIRED reading.
6. Every runnable file has the crashlog.txt wrapper (copy from app.py).
7. Don't break the ancestors: run.bat and fleet_demo.py 12/12 stay green.

YOUR DELIVERABLE. One file mXX_name.py (+ optional content JSON + tiny
sim/orders/referee additions if truly needed), a .bat if Nir wants it,
"WHAT YOU SHOULD SEE" + "REPORT BACK", and at end-of-life a short hand-off
note for DeepSeek to store.

FILE: brief_m01.md — MISSION BRIEF M1 (linear combinations + span: "The Plane of Refugees")

BRIEF M1 — COMBINATION FLIGHT / THE PRISON OF THE PLANE (Canon M1, §1.1;
Missions 1+3 fused). The template app.py already flies by combinations —
your job is to turn it into a GAME with the span lesson as its heart.

FICTION. First flight of the exile fleet. Refugee pods drift at (3, 5, 4)
— note the nonzero SECOND coordinate: height. At mission start only e1 and
e3 are unlocked (the horizontal plane): the fleet is imprisoned in a glowing
plane it cannot leave, and the pods float ABOVE it, visibly, hauntingly.

THE GAME. Phase 1: tutorial tasks — fly squad 1 to marked buoys IN the
plane using coefficient orders (Navigator sliders or Pilot keys; c2 slider
is LOCKED/greyed). Phase 2: a buoy appears at the pods. Every attempted
order visibly slides along the plane under it; Fleet Intelligence (content
lines, cited): "That target lies outside the span of our engines." The
console shows the reachable set for what it is. Phase 3: the Research
Vessel event unlocks e3 -> wait, e2 (the vertical) — the c2 slider wakes,
a third basis arrow ignites in green, and the order (3, 5, 4) rescues the
pods. Win screen: pods dock with Mom. Lesson felt, never lectured:
independence = freedom, span = everywhere you can ever go.

BUILD NOTES. Lock/unlock = your mini-game state gating which coeffs are
accepted (sim's engine_vectors already exist; ask DeepSeek whether the sim
supports fewer unlocked engines or gate it in your shell). Draw the prison
plane as a translucent Grid/lines vobject. Buoys = small glowing rings
(circle points pattern is in app.py). Use referee.is_solvable(E, target)
for the "reachable?" verdict (E = matrix of UNLOCKED engine columns).
Questions for DeepSeek: does sim expose engine unlock state or is
engine_vectors fixed at 3? Does content_db have a narrator-lines loader?

ACCEPTANCE. A non-mathematician must feel trapped in Phase 2 and free in
Phase 3, and say so unprompted.

FILE: brief_m02.md — MISSION BRIEF M2 (dot product: "First Contact / The Dust Stream")

BRIEF M2 — DOT-PRODUCT HARVESTING (Canon M2, §1.2; Mission 2).

FICTION. A dust river crosses the map: a flow field f, rendered as drifting
particle streaks so its direction is VISIBLE. The collector must drink from
it: harvest rate = rho * max(0, f . u), u = the intake axis unit vector.

THE GAME. Pilot selects the collector (TAB) and rotates its intake with the
coefficient keys repurposed as pitch/yaw of u (an arrow drawn on the hull).
Navigator's console shows: live f . u number, the angle theta, a drawn
angle arc between f and u (2D or 3D), and the hold gauge filling. Aligned:
gauge roars. 60 degrees off: exactly half (cos 60 = 0.5 — show the number,
let them notice). Perpendicular: zero. Facing away: zero (the clamp).
Win: fill the hold to quota, then a second dust stream with different f
forces re-aiming. The couple converges on the maximum TOGETHER: she reads
algebra ("you're at seventy degrees, pitch down"), he flies geometry.

BUILD NOTES. Orders: SetIntake exists in orders.py — ask DeepSeek whether
sim implements it and whether a resource_field context key already has a
format (it appears in the context-keys list!). If sim lacks harvest logic,
compute harvesting in your shell per pulse and keep sim untouched. rate
formula is one line; the VERDICT-free math here needs no referee call, but
if you display an angle number, compute it once, in one place. Particles:
a pool of short Trail or DashedLine vobjects drifting along f, recycled.
Fill gauge = Rect2D pair on the console. No timer pressure, no failure
state — the dust is patient (Iron Rule: never punish).

ACCEPTANCE. Nir and partner find the maximum by talking to each other,
and the phrase "perpendicular gives nothing" is SEEN, not read.

Nir — the system is: DeepSeek stores these files; when you want to start a branch, you open a fresh Fable, paste the founding documents, then charter.md, then the current app.py, then ONE brief — and say "build it." The branch asks its batches, proposes its design, you say yes, it ships.

Say "continue" and I'll deliver briefs M3, M4, M5 next (M5 — the nullspace cloak, the best idea in the project — I want written while I'm still sharp). 🚀
