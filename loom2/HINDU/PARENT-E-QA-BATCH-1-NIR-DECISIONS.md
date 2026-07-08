# PARENT E — Q&A BATCH 1 + NIR'S DECISIONS (July 8, 2026)

Parent E (`graphics/slice_mode.py` — The Glass Blade 🔪) sent his first batched
questions after absorbing all scriptures through Gita Part 4. Below: his questions
verbatim, DeepSeek's VERIFIED-FACT answers, and NIR'S DECISIONS on the two items
that were his to make (Q4, Q7).

---

## PARENT E'S QUESTIONS (verbatim)

**Q1 — The transect definition (the byte-for-byte seam).** Since
`game_state._build_slice_path` already exists, paste its source verbatim. He will make
`intersection_path` agree exactly on: direction convention of `yaw_deg` (math
convention, 0° = +x?), parametrization origin at (cx,cy), domain clipping method,
endpoint inclusion, and ordering. His proposal if it doesn't yet exist: direction
d=(cos yaw, sin yaw), march from (cx,cy) both directions until leaving the domain
rectangle, samples at t=k·step, ordered negative end to positive end.

**Q2 — Step semantics.** Confirm: game_state builds itinerary at coarse step
(RING_WIDTH=0.8?), while his default step=0.25 is the fine sampling for the drawn
curve — same line, same clipping, different density. Or does game_state subsample his
0.25 list? Which is canon?

**Q3 — Does tilt_deg affect the path?** He reads tilt_deg as visual-only (the glass
pane leans, but the transect + auto-walk remain the vertical-plane line through (cx,cy)
at yaw_deg). Confirm, or does _build_slice_path incorporate tilt?

**Q4 — The bead seam (missing wire).** Neither update_plane nor draw(view_proj,
surface_fn) receives the current auto-walk stop, yet the contract says "current
auto-walk stop marked with a bright bead." His proposal (additive amendment): a setter
`set_walk_stop(index_or_none)` on GlassBlade, called by main from snapshot each frame
(snapshot would expose the walk index). Alternative zero-amendment: the totem itself
stands at the current stop (Parent D draws it there), so the bead could be dropped or
derived. Which path does Nir bless?

**Q5 — Who calls update_plane, and when?** Assumed main frame step 4 (SLICE mode):
`blade.update_plane(snap["slice_plane"])` then `blade.draw(vp_left, surface_fn)` — where
does main get surface_fn (from `surfaces.get(spec.surface_name)`)? Confirm.

**Q6 — GL state etiquette.** Confirm (a) blend func SRC_ALPHA, ONE_MINUS_SRC_ALPHA;
(b) he may locally flip state (disable depth-write for the translucent quad, line_width,
offset) if he restores everything before returning; (c) pane extent is his design freedom
(clip to domain crossing horizontally, vertical span = terrain z-range across the cut plus
margin).

**Q7 — Taste menu for Nir.** He'll present concrete options+tradeoffs next message.
Headline: (a) glass tint cool-cyan vs neutral smoke, alpha ≈0.18–0.30; (b) pane lighting
unlit tint vs faint Gouraud Lambert; (c) curve glow single warm HDR vs hypsometric
band-colored profile (Parent D's band edges); (d) bead hot white HDR point vs small
pulsing diamond. His gut: unlit cool glass + single warm curve + hot bead.

---

## NIR'S DECISIONS

### Q4 — BEAD = **OPTION 2, THE ADDITIVE AMENDMENT (APPROVED, change contracts as needed).**
Nir: do the additive amendment. Expose the walk index (+ walking flag) in
`game_state.snapshot()`; add `GlassBlade.set_walk_stop(index_or_none)`; main wires it each
frame. Parent E draws a distinct bright bead ON the glass curve at the exact current stop.
DeepSeek is authorized to amend the frozen contracts (Gita G2/G3/G4 as needed) with proper
AMENDMENT blocks in the ACTUAL scriptures, and to do the extra stitching work.

**PLUS — NIR'S DESIGN DIRECTIVE (locked):** in SLICE mode the tall breathing totem is NOT
wanted. Reason (Nir's words, paraphrased): in normal hills-and-valleys mode the tall totem
is great, but when we concentrate on ONE path, the EXACT height is even more important —
whether we're a little higher or lower matters a lot — and the tall totem then reads like a
"margin of error" spreading to each side and confuses the players. So in SLICE mode the
PRECISE glowing bead sitting exactly on the curve (at z = f(current stop)) is the true
position indicator, and the tall totem should be SUPPRESSED/HIDDEN while slicing. This is a
main/frame-order stitching job (Parent G), possibly touching Parent D's totem_visual — NOT
Parent E's burden; Parent E just owns drawing the precise bead. To be recorded as an
amendment when implemented.

### Q7 — SHOW NIR **ALL** THE OPTIONS (do NOT pre-select one).
Nir: present the full menu of every option with tradeoffs (glass tint, pane lighting, curve
color, bead style, etc.). Do not show a single option and ask yes/no — Nir decides from the
complete list.

### TILT — NIR'S RULING (locked): TILT IS REAL, NOT COSMETIC.
Tilting the blade **actually changes the cut** — the blade is a true plane, and tilting it
re-slices the terrain. The drawn curve = the **true 3D intersection** of the tilted plane
with the surface z=f(x,y) (Parent E's "G1 — truth in space"). "G2 — painted on the screen /
curve drifts off the real land when tilted" is **REJECTED**, because exact height must stay
honest (this is the whole reason we suppress the tall totem in slice mode).

Consequence (locked): `tilt_deg` is **NO LONGER "visual only."** Both
`GlassBlade.intersection_path` AND `game_state._build_slice_path` (Parent 2's code, comment
"visual only") must incorporate tilt so the walked path follows the REAL intersection.
DeepSeek is authorized to amend the frozen contracts + Parent 2's game_state code.
The intersection of a tilted plane with z=f(x,y) is generally a CURVED path across the
surface (not a straight line) — Parent E works out the geometry/implementation and returns
with his approach + any consequence questions (especially how the totem/audio should treat a
tilted cut — that is Nir's call, not DeepSeek's).

CORRECTION LOGGED: DeepSeek earlier wrongly told Nir "we agreed tilt is visual only." That was
NEVER a Nir decision — it came from Parent 2's code comment, not from Nir. Retracted.

### Standing note from Nir
Fable (Parent E) may ask DeepSeek as many questions, in as many rounds, as he needs.

---

## TILT-CUT WORKED APPROACH — DeepSeek's TECHNICAL BLESSINGS (July 8)
Parent E returned with a worked approach for the REAL tilted cut. Per Nir's routing
(technical→DeepSeek, taste→Nir), DeepSeek blessed the engineering:

1. **Marching-squares extraction of the zero level set** g(x,y)=n·((x,y,f(x,y))−(cx,cy,z0))=0
   — BLESSED. Robust for curved paths / multiple components / closed loops; avoids
   root-chasing divergence near τ→45°. Must reproduce the straight transect exactly at τ=0
   (regression guard).
2. **Anchor z0 = f(cx,cy)** — BLESSED (correct choice). Makes g(cx,cy)=0 always, so the cut
   ALWAYS passes through the ground point under the blade center; every intersection point lies
   ON the surface at true height f(x,y). (z0=0 or pane-mid rejected.)
3. **Shared pure-math module `core/slicing.py`** (numpy+math only) imported by BOTH game_state
   and slice_mode — **BLESSED + recorded as a CONTRACT AMENDMENT** (Nir pre-authorized tilt
   contract changes). Dissolves the game_state↔slice_mode duplication (Gita forbids graphics
   imports in core; game_state.py L22-29 duplicated the transect for that reason). Parent E
   writes `core/slicing.py`; DeepSeek refactors Parent 2's `game_state._build_slice_path` to call
   it (add `core.slicing` to game_state allowed imports) + amends the scripture. Parent E states
   the public function signatures as canon.
4. **Totem walks the component nearest the anchor** (cx,cy) — BLESSED as default (with
   z0=f(cx,cy) it always passes exactly through the anchor); other components drawn
   (dashed-capable) but not walked. Multi-loop walking = a later taste change, parked.
5. **Occlusion: two-pass solid/dashed + ghost bead** — BLESSED (his shader budget).
6. **Constant pane height** (scene z-range + margin) — fine.

Parent E's LOCKED taste choices (from Nir's menu, per his message): A1 cool glass-cyan · B1
unlit pure tint · C1 single warm HDR gold curve · D2 ribbon strip / no under-curve fill (no
integrals) · E "bead on the wire" (bored sphere threaded on the ribbon, ~3s emissive breath, no
diamond/drop-line) · F4 yes (Fresnel rim, faint bloom only; F1/F2/F3 no) · H2 constant pane
height.

### 🎻 THE ONE OPEN ITEM = NIR'S CALL — what players HEAR on a slanted cut
Because z0=f(cx,cy), a tilted cut just carves a CURVED trail across the REAL hills (every point
is real ground at its true height f(x,y)). Options couriered to Nir:
- **(i) No new law:** totem walks the curved ground path; at each stop it hears its normal
  circular neighborhood (height→pitch, angle→timbre, radius→rhythm) exactly as everywhere else —
  still "a procession of neighborhoods," fully consistent with height-honesty; zero new audio risk.
- **(ii) Plane-aware:** invent a new sonification law tied to the tilted plane — more novel but
  new rules, cacophony risk, and it would play something OTHER than true ground height (in tension
  with the "exact height is sacred" ruling).
**NIR'S RULING (locked): OPTION (i). NO NEW AUDIO LAW.** Obey the rules already given —
the totem walks the curved ground trail and, at each stop, hears its normal listening-circle
by the EXACT SAME HSS rules as everywhere else (height→pitch, angle→timbre, radius→rhythm).
No plane-aware sonification, no new rule invented. (ii) is dead. DeepSeek should NOT have
proposed a new rule nobody asked for.

---

## DEEPSEEK'S VERIFIED-FACT ANSWERS (Q1, Q2, Q3, Q5, Q6)
See the courier reply sent to Parent E. Source of truth quoted verbatim from
`core/game_state.py` (`_build_slice_path` lines 371–398, constants lines 47–57,
snapshot lines 413–428) and `graphics/renderer.py` (`begin_panel` lines 131–133).

---

## 🐞 PARENT E DELIVERY — EXTRACTED, BUT A BUG FOUND (July 8) — WIRING HELD
Parent E delivered all 4 files (core/slicing.py, graphics/slice_mode.py, glass.vert/.frag).
Saved verbatim (`LOOM2-PARENT-E-SLICE-MODE-BY-FABLE.md`), extracted to code, **py_compile OK**.

**BUT the regression guard Parent E himself asked for FAILED.** His claim "at tilt=0 marching
squares reproduces the old straight transect EXACTLY" is FALSE when the cut line runs through
grid vertices (grid_step=0.25). Verified against a saddle surface on domain (−6,6,−6,6):
- `yaw=45, center=(−2.5, 2.0)`: primary component comes back **closed=True**, walk is
  **NON-MONOTONIC** — it walks out ~7 stops then reverses all the way across and back
  (28 pts vs old 15). The totem would zigzag out-and-back. Points stay on the true line
  (perp dist ~1e-12) but the ORDERING is broken.
- `yaw=135, center=(0,0)`: one straight cut **shatters into 26 spurious components**.
- Axis-aligned (yaw 0 / 90) and ALL generic angles (30, 37, 45.3, even 45 at an off-grid
  center like (0.1,0)) are CLEAN and monotonic.

**Root cause:** marching squares on a field whose zero-set passes exactly through grid vertices
creates ambiguous saddle cells (cases 5/10) + doubled segments; `_chain` welds them into a
spurious closed loop or shatters the line. The `g = np.where(g==0.0, 1e-12, g)` guard only
catches EXACT zeros, not the near-degenerate diagonal pattern. 45° cuts through integer/half
centers are COMMON, so this is not a rare corner.

**DECISION (DeepSeek, breaking-change guard): HOLD.**
- ✅ Extracted files committed (INERT — nothing imports core.slicing yet; safe).
- ⛔ **NOT wiring `game_state._build_slice_path → slicing.walk_path`** — that would REGRESS the
  currently-correct vertical straight-slice at grid-aligned yaws (e.g. 45°). Won't break a
  working thing.
- ⛔ **NOT amending scriptures (G3.6/G4.3) yet** — don't enshrine buggy cut math as canon.
- 📮 Bug couriered to Nir → Parent E for a fix (his code, his call: e.g. a tiny irrational grid
  offset so cuts never hit vertices; anti-degeneracy jitter; or robust vertex-crossing handling).
  Parent E invited "test it against me as hard as you like" — so this is the invited report.
**STATUS: awaiting Parent E's fix, then re-run the regression, then wire + amend.**

### ✅ RESOLVED (July 8) — FIX APPLIED, REGRESSION GREEN, WIRED + AMENDED
Parent E owned the bug and delivered a 3-layer fix in `core/slicing.py` ONLY (slice_mode +
shaders + all public signatures untouched): (1) `_grid_axis` irrational sub-cell skew of interior
grid samples (domain endpoints stay exact) so cuts never pass through grid vertices; (2) a
magnitude clamp `|g|<eps → +eps` (uniform sign, kills case-5/10 saddle noise); (3) `_clean_segments`
drops vertex-kiss micro-segments + duplicated edges before chaining. DeepSeek applied all 3 patches
verbatim, py_compile OK.
**Regression RE-RUN = ALL GREEN:** the two failing cases now give ncomp=1, closed=False, monotonic,
stop-count matching the old function (yaw=45 c=(−2.5,2.0): 15 pts; yaw=135 c=(0,0): 23 pts), perp
≲1e-8; every half-integer center clean; all previously-clean cases byte-stable; a tilted sanity case
(yaw=0,tilt=30) gives one connected component through the anchor; and a **brutal 30,000-case sweep**
(yaw 0..180° step 1° × a 0.5 lattice of centers) had **0 failures** (all monotonic, primary component
within grid_step of the anchor).
**THEN wired + amended (as Parent E instructed):** game_state now imports core.slicing;
`_build_slice_path` is one line delegating to `slicing.walk_path` (old body deleted); `_WALK_STEP`
removed; `_TILT_LIMIT` "visual only" comment corrected; snapshot() exposes additive `walk_stop` /
`walking` / `walk_stop_x` / `walk_stop_y` for the bead. Scriptures amended: Gita **G3.6-A** (Glass
Blade tilt-real + setters + glass GLSL interface + look choices) and **G4.3-A** (game_state refactor +
snapshot bead fields). **PARENT E COMPLETE. 🔪**

**DeepSeek OWES at Parent G (main wiring):** `blade.set_domain(spec.domain)` at scene build;
per-frame `blade.update_plane(snap["slice_plane"])`, `blade.set_walk_stop(snap["walk_stop"])`, and in
SLICE mode `blade.draw(vp_left, surface_fn)`; **SUPPRESS/HIDE the tall totem in SLICE mode** (Nir's
directive — precise bead is the height marker); confirm slice_mode's `self._stops` index matches
game_state's walk index (identical by construction — both call core.slicing with grid_step 0.25 +
RING_WIDTH).
