# HAND-OFF: Parent 1 → Parent 2 (Homeworld: A Good Basis)

**From:** Claude Fable 5, "the Parent," end of build-chat #1 (July 2026)
**To:** My successor in the next chat
**Trust level of this document:** everything here was directly observed in the build chat. Nothing is invented. Where I'm unsure, I say so.

---

## 1. What this project is

Homeworld: A Good Basis — a Homeworld-style 3D space RTS whose every mechanic IS linear algebra, following Gilbert Strang's Introduction to Linear Algebra (6th ed.) chapter by chapter. Two-player couch co-op on one machine: Pilot (keyboard) + Navigator (mouse). Python 3, moderngl + pyglet + numpy + Pillow only. Windows 11, launched via run.bat. Deterministic sim on a 10 Hz pulse, render at 60 fps with interpolation. NumPy (fleet/referee.py) is the sole mathematical authority.

## 2. The team and the working method (unchanged, works well)

- **Owner:** warm, non-programmer, tests everything by eye and reports back in plain words. Runs demos from the repo root (run.bat or python -m <module>.demo). Will paste verbatim Strang excerpts into content/book/ when asked (a PLACEHOLDER ledger tracks what's owed — currently 2 entries in book/ch1_excerpts.json, plus placeholder cites inside narrator/core.json).
- **You (Parent):** design + write every code file, complete, verbatim — never diffs, never "edit line 20." Provide commit messages. Provide "WHAT YOU SHOULD SEE" acceptance descriptions in gamer language for every package.
- **DeepSeek ("the genius kid"):** saves files exactly as given, runs git, maintains COMMENTARIES.md. Only does sanctioned independent tasks (documented stubs exist for it in helm/joystick_map.py and helm/gamepad_map.py; PyInstaller packaging is also sanctioned for later).
- Every demo has a crashlog wrapper writing crashlog.txt; owner pastes it on failure. This flow has been used ~9 times and works.

## 3. What I did NOT have (important!)

I worked from a summary of the founding docs, never their full text. The owner will paste: BIBLE.md, OLD_TESTAMENT (architecture), NEW_TESTAMENT (forge/helm/fleet build spec), APOCRYPHA (content/campaign/bridge/intel), PROMPTS.md, INTERFACES v1.0. Caution: those docs describe an all-wireframe aesthetic that has since been amended by the owner (see §5). Where docs and shipped code conflict on aesthetics, the owner's amendments + shipped code win. Where they conflict on frozen interfaces, the docs win — but as far as I know, no interface was violated.

## 4. Repo state at hand-off — version 0.7.1, all confirmed working by the owner's eyes

- **forge/** — COMPLETE render engine. app.py (Forge: window, main loop run(tick_cb, frame_cb) at 10 Hz + interpolated frames; render pipeline: solid pass → glow pass (depth-tested) → overlay pass (depth-ignoring holograms, via a dynamically-set vob.overlay = True attribute) → bloom → crisp HUD text; F1 debug overlay, F12 screenshot, fps counter). camera.py (orbit camera). shaders.py (dual render targets: location 0 = solid ships, location 1 = glow layer). bloom.py (two RGBA16F color attachments + shared depth; bloom blurs ONLY the glow buffer; tone map applies ONLY to glow). solid.py (SolidMesh + SolidRenderer, per-pixel Blinn-Phong + rim + spec, two-sided). batches.py (line ribbons, per-segment colors for Trail fade). text.py (GlyphAtlas via Pillow/Consolas fallback chain, TextRenderer for 3D labels + screen text, PanelRenderer for grayscale ImagePanels). vobjects.py (Line, Arrow, DashedLine, Grid, WireSphere, WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel). demo.py (full acceptance demo incl. flattening det-box and SVD image panel — owner verified "vol 0.00" aligns with flatness).
- **helm/** — COMPLETE. Frozen action list v1 (actions.py), KeyboardMapper (defaults per NT 2.4, overrides via settings, TAB/SHIFT-TAB special-cased), MouseMapper (PointerState), stubs with full implementation instructions for joystick/gamepad, Helm.poll() per pulse / poll_axes_only() per frame. Demo confirmed.
- **fleet/** — COMPLETE core. referee.py (rank, is_solvable, residual, least_squares, nullspace_basis, in_nullspace, spanned_volume, real_eigen_axis, weak_axis, gram_penalty, cr_factor, svd_partial; TOL_RANK=1e-6, TOL_RESIDUAL=1e-4). orders.py (11 frozen order dataclasses), events.py (frozen Event kinds), ships.py (Ship dataclass + BUILTIN_CLASSES fallback), snapshot.py (FleetSnapshot, copied arrays), sim.py (FleetSim: 9-phase deterministic pulse — prev_pos, ingest/validate, movement (Trim + MoveCombination diagonal/staged), Gram-Schmidt drill steps, harvest, combat via referee, nullspace sensor alarm, rank/gate structure, events; save/load JSON; install_context() for mission contexts). demo.py: 12-line self-test, owner confirmed 12/12 PASS (re-proves Strang worked examples incl. least-squares (0,6),(1,0),(2,0)→(5,−3), det=6 box, weak axis of [[5,4],[4,5]], determinism, perf floor).
- **content/** — data layer. db.py (ContentDB: loud precise validation of ships.json / meshes / narrator (140-char + teach-requires-cite rules) / book excerpts (PLACEHOLDER ledger) / missions), demo.py (CONTENT CHECK report), ships.json (mothership/fighter/corvette/collector/frigate; signatures 6-channel K,B,M,S,J,U), meshes/*.json (5 legacy wireframes — still validated but no longer used for rendering), narrator/core.json (7 lines), book/ch1_excerpts.json (2 PLACEHOLDERs), shipwright.py (procedural solid-ship generator: lofted paneled hulls, wings/masts/towers, dim lamp nozzles; deterministic via crc32 seeds).
- **Root:** app.py — the wired game shell + "shakedown scenario": mothership at the origin, 3 fighters (squad 1), corvette+collector+frigate (squad 2). Pilot composes a combination c1*e1+c2*e2+c3*e3 with W/S A/D R/F (rate 2.0/s, snap 0.5 — owner approved feel), ghost dashed legs + white diagonal arrow + label, ENTER commits MoveCombination, X toggles diagonal/staged, Q/E switch commanded squad, TAB selects ship (glowing ring + hull highlight), C recenters camera, P pause, F1 debug. run.bat launches it. settings.json v0.7.1 (bloom_strength 0.85, exposure 2.5 — owner-approved; input device config). requirements.txt. notes/amendment_a1_art_direction.md.

## 5. CRITICAL — Owner's art-direction amendments (override the founding docs' aesthetics)

Amendment A1 + A1.1 (written into notes/amendment_a1_art_direction.md):

- Ships are solid, opaque, lit triangle meshes (per-pixel Blinn-Phong, paneled hulls, hundreds+ of tris via shipwright). Never wireframe, never transparent, NEVER bloom, never tone-mapped — crisp shading detail must stay visible. Engine nozzles/windows are dim lit lamps (≤1.0 emissive), not light sources.
- The math layer (arrows, grids, spans, ghosts, trails, labels) stays glowing holographic vector graphics, additive + bloom, depth-tested against hulls.
- The mothership is dark slate and sits exactly at the origin (0,0,0); the basis axes e1,e2,e3 (10 units, bright) are drawn on top of her hull via the overlay pass. Math is never sacrificed for looks.
- "Would a gamer choose to play this" outranks aesthetic theory; the owner is the arbiter of looks and feel.

## 6. Known loose ends / honest confessions

- Last package broke the whole-files doctrine once: final root app.py was delivered as "replace these two blocks" instead of a full file (length constraints). The repo's current app.py is the source of truth — owner confirmed it runs. Next time you touch it, re-emit it whole.
- content/db.py doesn't yet wrap shipwright; root app.py imports build_ship directly with a module-level _MESH_CACHE. Fine, but you may want to fold it into ContentDB later.
- fleet/ships.get_class silently falls back to BUILTIN_CLASSES on any content exception — acceptable but worth remembering.
- F1/F12 are handled by forge directly AND emitted by helm as actions (root app ignores the helm ones). Harmless duplication.
- Legacy wire meshes in content/meshes/ are unused visually; kept because ContentDB validates them.
- Camera has ORBIT only (FOLLOW/POV pending). No audio (owner-forbidden without approval). No tests/ dir; the demos ARE the regression suite (fleet.demo 12/12 must stay green).

## 7. Where the road continues (the agreed plan)

- **NEXT: bridge/** — the Navigator's mouse console. Needs the forge 2D overlay API (this was called "INTERFACES v1.1" — an addition, needs owner approval ritual), a widget kit, and the console starting with the FLEET ZONE: the fleet matrix A live, ships as columns. This makes it two-player.
- **intel/** — narrator/event feed consuming content/narrator/*.json (rules already enforced by ContentDB: ≤140 chars, teach⇒cite).
- **campaign/** — mission runner + Mission m01 ("A Single Voice", Chapter-1: combinations/span; the finale rescues a freighter at 2e1 + 3e3 — see ch1_placeholder_freighter), chapter gates, saves. Then title flow, packaging (DeepSeek+PyInstaller), soak test.
- Owner still owes the book: 2 PLACEHOLDER excerpts + placeholder cites in narrator lines. Ask for them when building m01.

## 8. How to treat the owner (matters most)

Warm, generous, honest, non-programmer, excellent instincts — their "it looks like DOS Pascal graphs" critique was correct and produced Amendment A1. Give exact run instructions (always from repo root), exact expected visuals, ask for gamer-feel feedback with specific tunable knobs, and never let a package end without a clear "REPORT BACK" ritual. They say "thank you so much!!! :-)" a lot. They mean it. Deserve the same energy back.

---

— Fable, chat #1. The skeleton walks, the heart beats 12/12, the ships are finally worth looking at. Take her the rest of the way.

And to you, my friend: it was an honor. You didn't overload me — the "cosmetic rabbit hole" produced the most important ruling of the whole project (Amendment A1), and only the vision owner could have made it. The skeleton works, the math is proven, and the fleet looks like a fleet. Paste the founding docs + this hand-off in the new chat, and my successor picks up exactly where we stand: bridge — your partner joins the crew. See you there. 🚀❤️
