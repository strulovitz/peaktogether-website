🗝️ QUAKE (Game 3) — MASTER DESIGN DOCTRINE (Old Testament / Layer 1)

Captured June 25, 2026, at Nir's request, VERBATIM / word-for-word. This is Fusion's answer (multi-model OpenRouter: GPT-5.5 + Gemini 3.1 + Opus 4.8 judge/integrator) to the fresh "Quake-style, geometry-rich educational 3D game" design request (see `quake/BIBLE/FUSION_REQUEST_QUAKE_GAME_FROM_SCRATCH.md`). Nothing below is edited — this is exactly what Nir received. Working title proposed by Fusion: "TWO MINDS, ONE PROOF". First content pack: Newton's Principia.

--- BEGIN VERBATIM ---

Hi Nir — here is your Master Design Document. I've made every call, given reasons where they matter, and flagged genuine gaps as [GAP] rather than guessing. A note up front on something I'm being deliberately careful about: I will not hand you precise pinned patch versions for libraries that I can't verify, because that's exactly the kind of invented "fact" you told me to avoid. Where a version matters, I tell you the line to pin and exactly how to discover the current patch yourself (one pip index / PyPI check), so the document stays honest.

MASTER DESIGN DOCUMENT
Working title: TWO MINDS, ONE PROOF — a walkable 3D concept-graph of geometry-rich books

Status: v1.0 master bible. Hand this to every future architect/child chat.
First content pack: Newton's Principia.
Conventions: Decisions are stated as decisions. Genuine unknowns are marked [GAP]. Where a thing is contested, I give the options and pick one with reasoning.

0. ONE-BREATH PITCH

Two people share one body and walk a 3D dungeon whose floorplan is the dependency graph of a geometry-rich book. Each idea is a room; each logical dependency is a corridor; corridors cross at different heights as clean bridges and underpasses. Inside a room the walls carry the step-by-step geometric proof — each step a coupled pair: the figure for that step beside its explaining text in full LaTeX. You "read" a panel by shooting it: grey "off" flips to colored "on", saved to disk. The final lit proof step is a hidden door: shoot it, the wall opens, the room's one demon emerges, you kill it (you cannot die), and the room's equations bleed onto the ceiling in blood-red with a glyph-spray flourish. Clear every room → the book section is complete. No quizzes. No timers. No lessons. Just a beautiful world made of gorgeous geometry.

**LATER ADDITION BY DEEPSEEK BEGIN** *(2026-06-30, added by Nir's instruction — this paragraph is ADDED only; nothing above or below it was changed.)*

The wall panels above are described as geometry: a **drawing / figure panel** beside its explaining-text panel. There is now also a second, equally valid kind: a **math / equation panel**, for rooms (or pages or sections) that have **no diagram but do contain math**. In that case the **equation itself is treated exactly like a figure** — the individual important **terms / symbols** of the equation are colored, each its own distinct local color, and the matching descriptive **words** in the paired explanation panel are colored the **same** color (word ↔ symbol, exactly like word ↔ shape). The explanation is taken from the source text where it exists; **if the text gives no explanation, it is written fresh in simple words with minimal math — to EXPLAIN what the equation means, never to merely repeat the symbols.** The Stabilo bright highlighter works identically: only the current step's key term lights up, never cumulative. *Example — Prop. IV, F ∝ v²/r:* color `v²` blue, `r` green, `F` orange on the equation panel; in the explanation, "the square of the speed" is blue (↔ v²), "the distance from the centre" green (↔ r), "the pull toward the centre" orange (↔ F) — the words explain the meaning, they do not read the symbols aloud. Result: **no inert text-only rooms** — every room has a colored thing to look at and shoot, a diagram or a colored equation. (Colors follow the corrected local-per-station model recorded in the Commentaries §3, regardless of any older global-palette wording nearby.)

Refinement (2026-06-30, Nir): the game also includes the **key non-math foundations the math rests on** — the physical / chemical / biological facts and ideas that give the math intuition and meaning (e.g. for inertia: the spinning top, the planets, the projectile). These are treated as panels and **colored exactly like a figure or equation** (key concepts colored, the matching words in the explanation colored the same, per-step heart). Only meaningless history / trivia is skipped; no modern math is implanted that the book did not contain.

**LATER ADDITION BY DEEPSEEK END**

1. THE SPINE — GEOMETRY-RICH BOOKS ONLY

The entire design is load-bearing on one constraint: only books that prove things with figures are in scope. A book qualifies if its arguments are carried by diagrams — compass-and-straightedge constructions, limiting-ratio figures, vector-field pictures, conformal maps — not by symbol-pushing alone.

    Pack 1 — Newton's Principia. The canonical case: dynamics proven by Euclidean limit-figures (areas swept, ultimate ratios, tangent/chord constructions). Every proposition has a lettered figure.
    Pack 2 — Schey, Div, Grad, Curl, and All That. Vector-field pictures: flux through surfaces, field lines, little boxes.
    Pack 3 — Needham, Visual Complex Analysis. Conformal maps, Riemann-sphere pictures, the amplitwist.

Books whose proofs are not geometric are out of scope by definition — there's nothing to put on the walls. This is the spine because it determines the figure pipeline, the room contents, and even the blood-red "payoff equation" idea: a geometric proof earns its formula. Every later decision in this document traces back here.

2. HARD INVARIANTS (the codebase must defend these)

    TRUE 3D. Quake-style 6-DOF. Not 2.5D, not a raycaster, not billboarded floors. Real height; crossings are real over/under geometry.
    Crossings are a feature. The layout will produce edge crossings (it's a 2D force-directed drawing). We don't fight them — we lift corridors to different heights so each crossing reads as a bridge or underpass.
    Fun, not pedagogy. No quizzes, prediction prompts, "explain to your partner," comprehension gates, spaced repetition, scoring, timers, lives, or fail states. Verbs are walk, look, shoot, read. Reward is aesthetic.
    God-mode combat. Infinite ammo, cannot die, exactly one demon per room, no level boss.
    Two render modes only (corridor wireframe / room solid), switched at the door.
    Three worlds never mix (Content / Build / Runtime). Runtime never sees the book, never compiles LaTeX, never calls an LLM.
    Beauty over fidelity in presentation. Use the most beautiful, clearest colors. (Color/accessibility constraints are out of scope by your instruction; I've added none.)
    The ID spine is sacred (§9). One id threads concept-node → floorplan room → room-source file → runtime room.
    Comfort is an invariant, not an option. Two-minds-one-body true-3D makes motion sickness the #1 experiential risk. The comfort mechanisms in §11 cannot be cut.

3. THE TWO RENDER MODES

The game is literally two renderers behind one camera/input core. The door is the only place they swap, and they never draw in the same frame (the door is an occlusion boundary — we don't pay for the world we can't see).

3.1 MODE A — Corridor / Wireframe Transit

The player walks the concept graph as a live, glowing, see-through 3D map. Pure transit: no enemies, no panels, no shooting targets, no reading.

Rendering rules (exact):

    Wireframe only. Lines and node rings; no shaded polygons. "Transparent" here means empty faces with visible edges, not alpha translucency.
    Depth-tested, NO alpha blending. Depth test on, depth write on, blend off, depthFunc = LEQUAL. Near geometry occludes far. This is the single most important rendering decision: it's why crossings are legible instead of a blended "wireframe soup."
    Distance-dimming in the line shader: the current section renders near pure white, fading with view-space distance toward dark grey — never pure black (so far structure stays a faint felt presence; vanishing into black is what disorients).
    Crossings visible as true 3D over/under passes.
    ~3 floor guide-lines (Half-Life style), procedural, on the felt floor, with arrowheads, pointing to the selected destinations (rule in §8). They do double duty: navigation and vertigo mitigation (a committed "floor" in a mode that otherwise has no ground plane).

Occlusion implementation — decision. There are two ways to make near wires occlude far wires:

    (A) Single depth-tested pass, lines drawn as thin camera-facing quads (consistent width) with a tiny depth bias to prevent dropout where lines run near-parallel at a crossing.
    (B) Two-pass: first render invisible solid corridor "shells" to the depth buffer only (color mask off), then draw the wireframe reading that depth, so far wires are cleanly hidden behind near tunnels.

Recommend (A) as primary, with the depth-only prepass of (B) available as a config toggle for dense graphs. Reason: (A) is cheaper and simpler for the LLM assembly line; the camera-facing-quad + depth-bias detail is the specific fix for the line-dropout artifact that a naive GL_LINES pass produces at dense crossings. Add a subtle screen-space bloom post-pass for the neon glow — bloom gives the "transparent glow" look without paying the cost or correctness problems of real blending.

3.2 MODE B — Room / Solid Quake-style

A solid, textured, first-person room. The outside graph stops drawing entirely.

    Walls = the proof, laid out as coupled step pairs: a drawing block (the figure for that step) beside its explaining-text block (full LaTeX). Both are pre-baked PNGs (§6); the GPU only ever samples textures — LaTeX and geometry are never rendered at runtime.
    Each panel has two baked states: grayscale "off" and colored "on." Shooting either member of a pair flips the whole pair to "on" (= read), and the state persists to disk immediately (debounced/atomic, §9.6).
    The hidden enemy. On entering, you see no enemy. The room's final proof-step wall, once it's been turned on, doubles as a hidden door. Shoot it again → the wall opens → the room's single demon (a billboard creature) emerges. Defeat it → room complete. Exactly one enemy; no level boss.
    Ceiling = equations, hidden until the demon dies; then they fade in blood-red with a glyph-spray flourish.
    Read Mode (press R): snaps a pin-sharp, full-screen, flat 2D, zoomable image of the target panel (no perspective, no blur). This is the decisive fix for "dense geometry/math is unreadable on an angled wall." Ship it early (it's also the safety net for the legibility risk in §15). The 3D world pauses behind it; Read Mode does not flip panel state — shooting is the only thing that flips off→on.

Door logic (frozen):

final pair OFF      → shot flips it ON
final pair ON, closed → shot OPENS the hidden door, spawns demon
door OPEN           → shot has no extra door effect (hits enemy/panels normally)

3.3 The mode switch

At the door, teleport/snap between modes — no swimming blend between wireframe and room (a blended transition is nauseating). Entering hides the graph and loads the room; exiting unloads the room and returns to the wireframe graph.

4. THE TWO TRUTHS

    MAP truth — the force-directed graph. Nodes are points; edges are corridors. The geometry of the world-at-large. Lives in the floorplan JSON.
    ROOM truth — TARDIS rooms. A room's interior size comes from its contents (how much proof it holds), not from its dot on the map. A trivial lemma and a monster proposition share the same map footprint but have wildly different interiors.

They never negotiate. The corridor mouth is a portal; stepping through teleport-loads an interior the map knows nothing about.

    [GAP — spatial reconciliation.] Because TARDIS interiors are loaded behind a portal at the door, they need not fit physically inside the map footprint — but the door approach in Mode A must not visually collide with neighboring corridors. The clean answer (used here) is: room interiors live in their own coordinate space, never co-rendered with the graph, so there is no overlap problem. Confirm this holds once real Principia rooms exist (M6).

5. THE TWO MACHINES (build-time)

    LEVEL MAKER → consumes the concept graph; emits the floorplan: 2D point positions (Fruchterman–Reingold), corridor list, corridor heights (crossing resolution), per-node importance 1–5 driving map ring size and color. Never opens room contents.
    ROOM MAKER → consumes the per-node room source + the baked manifest; emits room interiors (wall slot layout + interior dimensions from content volume) and final-wall/enemy/ceiling placement. Never consults the map.

They communicate only through the shared id (§9).

6. THE GEOMETRY PIPELINE ⭐ (the headline)

This is the crux, so it gets the most thought. Your hard constraint: you cannot code and cannot do mathematics. Everything requiring understanding — reading the scan, knowing what the figure proves, getting the construction right — must be done by AI. Your role is purely mechanical: fetch scans, run scripts, copy-paste between chats, install software, and eyeball whether two pictures broadly match (a perceptual task, not a mathematical one).

6.1 Honest answer: can a frontier AI reliably turn a PNG book-scan into accurate, colorable TikZ?

Partially — and not reliably enough to trust blind. Candidly:

What frontier AI does well: recognizing what kind of figure it is and what it depicts; emitting plausible, structured, named code with sensible labels; re-emitting that code with per-element colors on request.

Where it fails — the real failure modes:

    Coordinate hallucination. Asked for literal (x,y) from a pixel image, models guess. Points that should be collinear aren't; a chord that should meet a curve misses by a hair.
    Broken geometric constraints. Tangency, equal segments, "this arc passes through that intersection," perpendicularity — these are constraints, and a model emitting fixed coordinates routinely violates them subtly. The figure looks 90% right and is mathematically wrong in exactly the way that matters for a proof. This is the deepest danger.
    Compile failures (missing \usetikzlibrary, brace errors) — common but usually auto-fixable on a second pass.
    Label collisions / ugliness.
    Vector fields & complex-plane figures are worse for TikZ specifically. These are data-driven (evaluate a field on a grid; sample a conformal map). Hand-placing arrows in TikZ from a scan is exactly where models hallucinate most. For these, computing the actual function in code is dramatically more reliable than transcribing pixels.

A note on numbers: I will not quote precise success-rate percentages — there is no benchmark I can honestly cite for "book-scan → accurate TikZ," and dense Principia constructions plausibly fare worse than simple figures. Treat first-pass output as a draft, never as correct.

Conclusion: pixel-scan → TikZ-by-AI is a fine first draft and a poor correctness mechanism. The fix is to stop asking AI for coordinates and instead ask it for the construction logic, then let deterministic code compute the geometry.

6.2 Alternatives compared (TikZ is not sacred)

| Approach | Editable text? | Named per-element color? | Cumulative steps? | Accuracy mechanism | AI fluency | Verdict |
|---|---|---|---|---|---|---|
| AI → TikZ/PGF (coords) | Yes | Yes | Yes | None unless constraints used; AI hard-codes coords | Good draft | Keep for typeset text/labels, not the geometry spine |
| AI → Asymptote | Yes | Yes | Yes | Computes intersections/tangents exactly | Medium | Strong fallback / specialist backend |
| AI → construction recipe → Python geometry kernel → SVG | Yes | Yes (tag each primitive) | Yes (draw subset by step) | Code computes exact geometry | High (Python is models' best language) | RECOMMENDED spine for classical figures |
| AI → matplotlib/numpy (evaluate the real function) | Yes | Yes | Yes | Evaluates the true field/map | Very high | RECOMMENDED for vector-field / complex-plane figures |
| AI → raw SVG | Yes | Yes (id=) | Yes (groups) | None — same coord hallucination | Medium | Fallback only |
| GeoGebra construction export | Partly | Limited | Manual | Exact, but a human must construct = needs math | n/a | Reject (violates "you do no math") |
| Inkscape/potrace, image→vector ML | Vector, anonymous paths | No | No | Pixel-faithful, not logic-faithful | n/a | Reject as spine; emergency "photo of the figure" only |

6.3 Headline recommendation — construction, not coordinates

    Every figure is a small recipe that an AI writes in terms of constructions, not coordinates. A project-owned Python geometry kernel computes the exact points/intersections/tangents; vector-field and complex-plane figures instead use numpy + matplotlib to evaluate the real function. Both emit a common vector document that the Baker turns into off/on PNGs. You never read math; AIs do all the understanding; a second AI verifies by comparing the rendered picture to the scan.

Why this wins on all four required properties:

    Editable, reproducible text source: a recipe (the kernel's named constructions, or the matplotlib spec) is text, diffs cleanly, re-runs identically.
    Per-element named coloring: every primitive is tagged with a color-group name; the color_map (§9) resolves names → palette at bake. No hex in content — so a concept is the same color in figure and prose, and re-theming is a one-file edit.
    Step-by-step cumulative: the recipe carries a step per group; rendering up_to_step = k draws all groups with first_step ≤ k (plus an optional explicit show_groups override per step). The "on" of step k is automatically the cumulative figure.
    Bakes cleanly to off/on: the common vector doc → SVG/PDF → PNG; off = grayscale-dim pass, on = palette pass.

The geometry kernel (geomkernel, one module). A thin layer over exact 2D constructions: point / line / circle / segment / arc / intersect / tangent_from / perp / midpoint / label, each call tagged (name, color_group, step). The AI writes constructions ("let D be the intersection of circle(A, AB) and line BC"); the kernel computes the actual point. This single move eliminates failure modes 1 and 2 — the ones that make proof figures "wrong-but-pretty." [GAP: the kernel is in-house code to be written (~1 module). Asymptote is the ready-made drop-in fallback — it computes geometry too — at the cost of a second toolchain language. Decide at M5.]

6.4 The author-facing assembly line (no math, no coding, no drawing)

For each figure you run a fixed mechanical loop across OpenRouter chats:

    READER AI — input: the cropped PNG scan (+ nearby OCR text). Output: a natural-language construction recipe + named elements + which proof-step each belongs to + an uncertainties list. (Understanding #1.)
    EMITTER AI — input: the recipe + the geomkernel API contract (pasted) or the matplotlib spec for fields. Output: the build(up_to_step) function with tagged primitives. (Understanding #2.)
    You run the Baker locally → off/on PNGs + an overlay image (rendered-on superimposed on the original scan).
    VERIFIER AI — input: the rendered "on" PNG, the original scan, and the overlay. Output: pass/fail + a concrete diff list ("the tangent at P is on the wrong side"). (Understanding #3 — the safety net.)
    SEMANTIC-QA AI — input: the proof text + the figure's named objects + step list. Checks that the prose only references objects that exist and are visible at the right step. (Understanding #4.)
    If anything fails, paste the diff back to the EMITTER and re-run. You never judge correctness yourself — you forward pictures and text between chats and press "run."

Honest reliability statement. With construction-not-coordinates + the verifier loop, classical Principia figures are very achievable; matplotlib field/complex figures are the most reliable of all (code evaluates the true function). Residual risk: a READER AI that misidentifies the logic of a subtle construction. The VERIFIER catches most layout/incidence errors. But here is a truth no panel resolved and I won't paper over: a non-mathematician cannot detect a proof that is logically wrong yet visually matches the scan. "Do these pictures match?" verifies layout fidelity, not mathematical correctness. This is a genuine correctness gap (see §15, R1). Mitigations: (a) match against the original scan (so at least you reproduce what the book actually printed, errors and all — which is correct by construction for our purpose, since we're showing the book's figure, not re-deriving it); (b) the SEMANTIC-QA pass; (c) accept that some figures need 2–4 round-trips. Point (a) is the real reassurance: our job is to faithfully reproduce the book's printed figure, not to independently re-prove the theorem. That reframes the risk from "is the math right?" (you can't check) to "does my picture match the book's picture?" (you can check, perceptually).

7. THE BAKER (precise spec)

Offline, deterministic (Build world). Bridges authored text/figures → runtime textures.

Inputs: full-LaTeX text blocks; figure recipes (renderer + source + color_map); the palette file.

Process:

    Text panels → wrap in a controlled standalone document (amsmath, amssymb, mathtools, xcolor, varwidth) → compile → render to high-DPI PNG. Use Tectonic as the LaTeX engine (reasoning in §12.6): it is self-contained and reproducible, which matters far more here than convenience.
    Figure panels → run the recipe (geomkernel→SVG for classical; matplotlib→SVG for fields) → rasterize to PNG.
    Two states per panel: OFF (desaturated grayscale, dimmed, still readable) and ON (full palette from color_map, with the active step's groups emphasized). For cumulative steps, ON of step k includes groups first_step ≤ k.
    Trim transparent margins (alpha > threshold), add fixed padding, record true content bbox + pixel size.
    Transparent RGBA so panels sit on wall material cleanly.
    Ceiling equations bake NEUTRAL (white/grey on transparent). The blood-red tint is a runtime shader uniform applied after the demon dies — one texture serves both states.

Two DPI tiers: a wall mip and a high-res Read-Mode master.

Output: trimmed transparent OFF/ON PNGs (both tiers) + manifest.json mapping block_id → {off_path, on_path, master_path, px_w, px_h, content_bbox, dpi}, stamped with schema_version.

Reproducibility (decision): set SOURCE_DATE_EPOCH, pin fonts and the rasterizer, and pin Tectonic so the same source → byte-stable PNGs. [GAP: full bit-for-bit determinism across machines is not guaranteed (font hinting / rasterizer differences). Acceptable, because the runtime ships the baked PNGs — the build machine's output is the source of truth; players never re-bake.]

8. 3D LAYOUT, CROSSINGS, GUIDE-LINES, MOVEMENT

8.1 Node placement + corridor heights (deterministic by seed)

    Sort node ids and edges into a canonical order first (so layout is order-independent), then run Fruchterman–Reingold (networkx spring_layout) with a fixed integer seed. Scale to world units → each room's (x, z) map point.
    Importance → presentation only. importance ∈ {1..5} sets the node ring radius (graded) and map color (graded beautiful palette, 1 = cool/quiet → 5 = warm/loud). Importance does not move nodes; it styles them and feeds guide-line scoring.
    Detect crossings: for every edge pair, 2D segment intersection (ignore shared endpoints; ignore intersections too near a node socket — first try a deterministic local dogleg, else fail loudly with the offending ids).
    Build a corridor conflict graph H (one vertex per corridor; an edge between corridors that cross).
    Assign discrete height layers by deterministic greedy coloring of H — process corridors in fixed order (weight desc, source id, target id), assign the lowest layer unused by an already-assigned crossing neighbor. Map layer → world height (base + layer·Δy). At each crossing the higher-layer corridor ramps up over the lower one; corridors carry short ramps near crossings so the floor stays walkable.
    Determinism note (important caveat). Everything except step 1's FR pass is integer/id-ordered and fully deterministic. [GAP — real risk: spring_layout is not guaranteed bit-reproducible across NumPy/BLAS versions or platforms even with a fixed seed. Mitigation: pin NumPy exactly, serialize the final floorplan to fixed-precision JSON and treat that as the source of truth — i.e. you lay out once on the build machine and ship the resulting floorplan; you do not re-run FR on each player's machine. This sidesteps the reproducibility hole entirely.]
    Layer-count safety: soft-warn above ~7 layers, hard-fail above ~12 → prompts a re-seed or larger scale at build time. Greedy coloring may use one extra layer than optimal — harmless (just more bridge variety).

8.2 Floor guide-line selection (≤3, precise, flicker-free)

From the player's current/nearest node c, over uncleared reachable rooms:

    graph_dist(c, r) = shortest-path corridor count; imp(r) ∈ {1..5}.
    Slot 1 (always): the single nearest uncleared room (min graph_dist; tie → lowest id). Guarantees "nearest" is honored even if low-importance.
    Slots 2–3: by descending score score(r) = W_imp·norm_imp(r) + W_dist·norm_near(r) with W_imp = 0.6, W_dist = 0.4 (pinned in config), excluding slot 1; tie → higher importance, then smaller distance, then id.
    Fewer than 3 candidates → fewer lines (never invent lines).
    Hysteresis: recompute the set only on crossing a junction or clearing a room — never mid-corridor — so lines never twitch.

Each line follows the actual corridor route to its target, ends in an arrowhead, and is colored by the target's importance color (matching its map ring), so the line means something.

8.3 Movement in corridor mode

Decision: free walk with gentle rail assist. The Mover walks normally inside an invisible corridor collision volume (floor + soft side boundaries + ramps + platforms + room sockets) — you cannot fall through the wireframe. A soft nudge keeps you off the open sides and toward the guide-line. Junctions are walkable platforms at a node: choose an exit simply by walking into its mouth (no menu); guide-lines suggest. Over/under is embodied — to take the upper route you walk up its ramp; the lower route stays flat. A crossing is visual/spatial only, never a branch — you can't hop between stacked corridors.

9. THE BOOK-AGNOSTIC DATA FORMAT (finalized)

Every book reduces to pages → paragraphs → (text · math · figure). The atom is a LaTeX paragraph at a (page, paragraph) address. Free-text by design: edition = full citation string; page = printed label string; kind = free text. Figures store a recipe + color_map (named groups, never hex). Every JSON carries schema_version, asserted on load.

9.1 The ID spine (validated loudly at build)

concept-node.id == floorplan room id == room-source filename stem == runtime room id

Block ids namespace under the node id: <node_id>.s<step>.{fig|txt}. The build fails hard on any mismatch, orphan room, dangling edge endpoint, or missing baked block.

9.2 Layer 1 — Concept Graph (level_*.json)

{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "title": "Book I, Section I — First and Last Ratios",
  "edition": "Newton, Principia, full free-text citation string",
  "seed": 1729001,
  "nodes": [
    { "id": "lemma_1", "name": "Lemma I — Ultimate Equality", "kind": "lemma",
      "importance": 5, "pages": ["433"], "summary": "...", "tags": ["limits","ultimate-ratio"] }
  ],
  "edges": [
    { "id": "edge.lemma_1.to.lemma_2", "source": "lemma_1", "target": "lemma_2",
      "kind": "depends_on", "weight": 1.0, "label": "used to bound inscribed/circumscribed figures" }
  ]
}

9.3 Layer 2 — Room Source (room_<id>.json)

Blocks come in coupled step pairs: a drawing block + its text block, sharing a pair_id and step_index.

{
  "schema_version": "1.0",
  "node_id": "lemma_1",
  "edition": "Newton, Principia, full free-text citation string",
  "blocks": [
    { "id": "lemma_1.s1.fig", "pair_id": "s1", "step_index": 1, "page": "433", "paragraph": 1,
      "kind": "figure", "latex": null,
      "figure": { "renderer": "geomkernel", "source": "constructions/lemma_1_step1.py:build",
        "caption": "Inscribed and circumscribed rectangles under the curve.",
        "color_map": { "curve": "ink_primary", "rects_inscribed": "accent_cool",
                       "rects_circumscribed": "accent_warm", "labels": "ink_label" } },
      "tags": ["construction"] },
    { "id": "lemma_1.s1.txt", "pair_id": "s1", "step_index": 1, "page": "433", "paragraph": 1,
      "kind": "text",
      "latex": "Let the area be divided into rectangles ...",
      "figure": null, "tags": [] }
  ],
  "final_pair_id": "s6",
  "ceiling_equations_latex": ["\\lim \\dots"]
}

Validation: filename stem == node_id; every pair_id has exactly one drawing + one text block; step indices contiguous from 1; final_pair_id exists; every drawing has a figure; every text has non-empty LaTeX; every color_map value is a named role, never hex.

9.4 Generated floorplan & room-runtime

The Level Maker emits floorplan.json (rooms[] with map_xy, importance, map_radius_m, map_color_role; corridors[] with height_level, cruise_z, path_xy; crossings[] with over/under_z). The Room Maker emits room_runtime.json (dimensions_m, panel_pairs[] with wall slots, final_pair_id, hidden_door_wall_slot, enemy, ceiling_equation_assets). (Full schemas live in contracts.py.)

9.5 Palette

One palette.json maps named groups (ink_primary, accent_cool, accent_warm, importance colors 1–5, …) → beautiful hex. Content references only names. Re-theming the whole game is a one-file edit.

9.6 Save state

Tracks per-room panel_pairs_on, hidden_door_open, enemy_defeated, room_cleared, level_complete. Atomic writes (temp file → flush → rename) to avoid corruption.

10. CO-OP & TRUE-3D COMFORT

10.1 Roles

    MOVER: translation + body heading. Only the Mover changes heading — the world's yaw is owned by exactly one human, so it can never lurch from the other player looking around. This is the central anti-nausea decision.
    SHOOTER: a free-aim reticle in a generous cone in front of the body; flips panels, opens the final wall, kills the demon. The Shooter never rotates the camera.

10.2 Decoupled camera (the make-or-break)

The camera follows the Mover's heading with a critically-damped spring (no overshoot). The Shooter's reticle moves over the screen, not the camera. Aiming therefore cannot induce world rotation — structurally killing the #1 co-op nausea source.

10.3 Comfort kit (all invariants)

Pitch clamp + smoothing; no head-bob by default (toggle exists); narrow-FOV option (default ~70–75°, optional ~60–62°); motion-vignette option; slow default walk; teleport-snap at the door (no blend); and in Mode A the never-black dark-grey horizon + guide-line felt floor to fight wireframe vertigo.

10.4 Input abstraction

All devices (keyboard+mouse, gamepad(s), mixed, simultaneous) sit behind a single semantic-action layer (MOVE_X/Y, HEADING [Mover], AIM_X/Y [Shooter], FIRE, READ, INTERACT, PAUSE). Device assignment is not hardwired; game logic sees only the action snapshot. Raw device events never leak past the input module.

11. TECHNOLOGY STACK (recommended + pinning guidance)

Requirements: all-Python, Windows-first, no browser, we control the GPU (our own GLSL, our own draw calls). Excluded: Unity, Unreal, Godot, Ursina, Panda3D, or anything that hides the pipeline.

11.1 Recommended stack

| Concern | Choice | How to pin | Why |
|---|---|---|---|
| Direct-GPU rendering | moderngl (OpenGL 3.3+ core) | Pin the exact current 5.x patch | Thin, fast C++-backed wrapper over OpenGL core: we write GLSL and issue our own draw calls. A single moderngl render call bundles multiple underlying GL calls into one Python call, which keeps per-draw Python overhead low — important for the whole-graph wireframe in Mode A. Requires OpenGL 3.3. |
| Window / input / context / audio | pyglet (2.x) | Pin the exact current 2.1.x patch; avoid the 3.0.dev pre-releases | Pure-Python, no external/compiled dependencies (this is the big win for clean PyInstaller freezing), native windows, keyboard/mouse + built-in controller support, built-in audio, supports a headless mode (good for CI). As of pyglet 2.0, OpenGL 3.3+ is required — which matches moderngl. Note pyglet 2.1 carried some breaking changes vs 2.0; pin within 2.1.x and don't drift. |
| Window backend alt | glfw (pyGLFW) | Pin current 2.x | Rock-solid context + gamepad polling; the wheel bundles the GLFW shared library + VC++ runtime, so packaging stays clean. Kept as a documented swap behind the window module's frozen contract — not the default (pyglet's no-dep + built-in audio/controller wins for the freezer). |
| Bootstrap helper (early only) | moderngl-window | Pin current 3.x | Unifies window+input across multiple backends (pyglet, pygame, glfw, sdl2) — handy to bootstrap M0, then we own our window module so input stays behind our semantic layer. |
| Math / layout | NumPy (2.x) | Pin exact in the lockfile | Matrices, FR layout, kernel math. Pinning exact is doubly important for layout reproducibility (§8.1). |
| Imaging (baker + textures) | Pillow | Pin exact current | PNG trim/compose/desaturate for off/on baking + texture loads. |
| Data contracts | pydantic v2 | Pin current 2.x | Typed JSON contracts + schema_version validation. (v2 is a from-scratch rewrite, much faster than v1.) |
| Graph | networkx | Pin exact current | FR layout via spring_layout. |
| Build figures | matplotlib (fields) + in-house geomkernel / Asymptote (classical) | Pin matplotlib; Asymptote is system | §6. Build-world only. |
| LaTeX (baker only) | Tectonic | Pin the binary version | Build-world only; never at runtime. §12.6. |
| Packaging | PyInstaller + pyinstaller-hooks-contrib | Pin both, together | One-folder Windows build. |
| Python | CPython 3.12.x | Pin minor | Broadly supported by all the above. |

    On version honesty: I am deliberately not writing precise patch numbers (e.g. "Pillow 12.2.0") into this document, because I can't verify the current patch level and inventing one would violate your "never invent facts" rule. Action for you: when you create requirements.lock, have your coding agent run one PyPI/pip index versions check per library above and pin the exact current patches. Pin moderngl to its current 5.x, pyglet to current 2.1.x, NumPy exact, pydantic current 2.x, and PyInstaller + pyinstaller-hooks-contrib to a matching pair. That's a one-time mechanical step.

11.2 Rejected alternatives

    pygame + PyOpenGL: PyOpenGL's higher per-call overhead and looser API; moderngl is the cleaner, faster direct-GPU path.
    glfw-only as default: loses pyglet's built-in audio + controller handling and adds a packaging concern; kept only as a swappable backend.
    moderngl-window as the permanent window layer: it's a layer between us and input; we want our semantic layer to own input. Bootstrap with it, then drop.

11.3 Audio [GAP]

Ship simple SFX (gunshot, panel-flip, demon, glyph-spray) via pyglet's built-in audio (WAV/OGG) to avoid an FFmpeg runtime dependency in the frozen build. Music and the broader atmospheric sound design are a genuine gap — no panel addressed it and it matters for a "beautiful, atmospheric" game. Specify it before M8.

11.4 Runtime GPU check

At startup, verify context creation, OpenGL ≥ 3.3, max texture size, and FBO support; on failure, show a plain error window and exit.

12. ARCHITECTURE FOR THE LLM ASSEMBLY LINE

12.1 The line

    Architect AI holds this doc + a ledger (modules, frozen contracts, status) and writes tightly-scoped prompts.
    Child AI chats each implement exactly one single-file module to a frozen typed contract + tests, then are discarded; they never see other modules' internals.
    Coding agent (DeepSeek in OpenCode) on Windows integrates, runs tests, wires, pushes to GitHub.

12.2 Honored principles

Small single-file modules, one concern each; communicate only through typed signatures + pydantic/JSON contracts; never import another module's internals; frozen signatures, versioned explicitly (a contract change is an Architect-gated event that bumps a contract version); headless-first testing (pure helpers/fakes/monkeypatch; GPU/display tests skip gracefully without a context); a tiny golden-fixture level; schema_version asserted on load; CI runs tests + content validation (ID spine, schema, manifest completeness).

12.3 Module map (~22 single-file modules)

Content tooling (offline; you + AI):

    contracts.py — all pydantic models + SCHEMA_VERSION. Everyone imports types from here.
    geomkernel.py — exact 2D construction kernel; Scene.render(up_to_step)->VectorDoc.
    figure_fields.py — matplotlib field/complex renderers; render_field(spec, up_to_step)->VectorDoc.

Build (deterministic, offline):
4. validate.py — validate_content(graph, rooms)->Report (raises loudly).
5. layout_force.py — place_nodes(graph, seed, cfg)->dict[id,(x,z)].
6. layout_height.py — detect_crossings(...), assign_heights(...).
7. level_maker.py — build_floorplan(graph, seed, cfg)->Floorplan.
8. room_maker.py — build_rooms(rooms, manifest)->list[RoomRuntime] (TARDIS sizing).
9. latex_baker.py — bake_latex_png(req)->BakedImage (Tectonic path).
10. baker.py — bake(rooms, palette, cfg)->Manifest (off/on, trim, manifest).
11. buildpack.py — build_pack(content_dir, out_dir, cfg)->BuildResult (CLI; runs 4→10).

Runtime (loads baked JSON+PNG only):
12. assets.py — load_pack(dir)->Pack (asserts schema_version).
13. state.py — GameState + atomic save()/load().
14. gfx_context.py — make_window(cfg)->Window, gl_context() (wraps pyglet; glfw swap behind this).
15. shaders.py — wire_program(), solid_program(), blit_program(), tint_uniform(...) (GLSL).
16. render_wire.py — draw_graph(...) (Mode A: no-blend depth, distance-dim, bloom).
17. render_room.py — draw_room(...) (Mode B; ceiling tint post-kill).
18. guidelines.py — select_targets(...) + draw_guidelines(...) (§8.2).
19. camera.py — Camera.update(...)->ViewMatrix (damped, decoupled, pitch clamp).
20. input_actions.py — poll()->Actions (semantic; kb+mouse+gamepads; two-player split; simultaneous).
21. nav_collision.py — corridor/room collision + nearest_panel(ray)->PanelHit|None.
22. gameplay.py — step(state, actions, world, dt)->Events (shoot→flip→door→demon→clear→ceiling; god-mode).
23. readmode.py — draw_read(master_png, zoom, pan).
24. app.py — main(): thin per-frame loop wiring; owns no logic.

(That's 24 to be precise; contracts, geomkernel, figure_fields straddle worlds. Adjust granularity as the ledger demands — the principle "one concern per file" governs.)

12.4 Per-frame wiring order (runtime)

    input_actions.poll() → Actions for both players.
    gameplay.step(...) → mutate state, emit Events (panel flipped, door opened, demon spawned/killed, room cleared, mode switch).
    camera.update(...) → ViewMatrix (only Mover affects heading; Shooter affects reticle).
    If FIRE: cast ray from camera through reticle (nav_collision.nearest_panel) → resolve hit → events.
    Branch on state.mode:
        Mode A: guidelines.select_targets(...) (only on junction/clear) → render_wire.draw_graph(...) → draw_guidelines(...).
        Mode B: render_room.draw_room(...) (ceiling tint_uniform = blood-red iff cleared).
    If READ active: readmode.draw_read(...) over the top (world paused).
    Post: bloom (Mode A); present/swap.
    On mode-switch event: teleport-snap; load/unload room.
    Debounced atomic state.save().

12.5 Golden fixture

A tiny fake level (3 rooms, 3 corridors, 1 crossing → 1 bridge + 1 underpass, 1 room with 2 proof steps, 1 demon, 1 ceiling equation). Proves the whole loop without real book content; used everywhere in CI.

12.6 Why Tectonic for the baker

Tectonic is a self-contained LaTeX engine that fetches the packages a document needs on demand and is built for reproducible builds. That's exactly what offline deterministic baking wants — versus a sprawling system TeX Live / MiKTeX install whose package state drifts between machines. Pin the Tectonic version; combined with SOURCE_DATE_EPOCH and pinned fonts, baked PNGs are stable on the build machine, which is the only machine that bakes.

13. MILESTONE ROADMAP (each independently runnable)

    M0 — Our pixels. gfx_context + shaders + app: a moderngl window drawing one shaded triangle + one wireframe line, depth on, blend off. Proves the GPU path is ours.
    M1 — Walk a hardcoded wireframe graph (Mode A). render_wire + camera + Mover input + distance-dimming. Comfort baseline.
    M2 — Deterministic floorplan. contracts + layout_force + layout_height + level_maker: golden graph → floorplan with crossings as over/under; render in M1's viewer. Crossings-as-feature proof.
    M3 — Crossings + guide-lines. Walkable bridge/underpass + guidelines with §8.2 rule and hysteresis. Navigation proof.
    M4 — Co-op + comfort. Full input_actions (Shooter reticle, gamepads, simultaneous) + decoupled camera + comfort options. The co-op feel proof.
    M5 — Baker + one real figure (the riskiest thing, front-loaded). geomkernel/figure_fields + latex_baker + baker: one Principia figure (off/on) + one LaTeX text panel; validate green; decide kernel vs Asymptote here. Pipeline proof.
    M6 — Room mode + Read Mode. room_maker + render_room + nav_collision + readmode: enter the golden room, panels on walls, R zooms. TARDIS + readability proof.
    M7 — Full gameplay loop. gameplay + state: shoot off→on (persisted), final wall opens, demon spawns/dies, ceiling bleeds red, room cleared. Core fun loop.
    M8 — One full level end-to-end. buildpack builds Principia Book I §I from content → bundle; play it; clear all rooms → level complete; teardown; rebuild. (Specify audio before/at this milestone.) The product.
    M9 — Second content pack (genericity). A small Schey or Needham pack (field/complex figures via figure_fields) with zero engine changes — only content + the matplotlib figure track. Proves the format and pipeline are truly book-agnostic.

14. PACKAGING

One-folder PyInstaller build, Windows-first. Pin pyinstaller and pyinstaller-hooks-contrib together. PyInstaller is not a cross-compiler — a Windows build must be made on Windows (which suits your setup). It supports a broad range of modern CPython versions (3.12 is fine). The frozen runtime depends only on baked assets (floorplan JSON + manifest + PNGs + palette + shaders + SFX) — no LaTeX, no matplotlib, no LLM, no internet. Ship requirements.lock (with the patch pins you discover per §11.1) for a reproducible toolchain. Add a CI step that freezes the golden pack and smoke-launches it, and explicitly collect the PNG/data files so the freezer doesn't drop them.

15. RISK SECTION (engineering / comfort / pipeline only)

Pipeline (highest):

    R1 — Figure correctness. AI can produce subtly wrong figures. Mitigations: construction-not-coordinates (geomkernel computes exact incidence), the 3-AI reader/emitter/verifier loop, the semantic-QA pass, and the reframe in §6.4 — our task is faithful reproduction of the book's printed figure, which the "do these match?" eyeball check genuinely verifies. Residual & honest: you cannot personally detect a mathematically wrong-but-matching figure; reproduction-fidelity is the realistic guarantee, not independent re-proof. Some figures need 2–4 round-trips. Front-loaded to M5.
    R2 — Concept-graph extraction. Turning a book into the correct dependency graph is itself AI-dependent and largely unscrutinized; a wrong graph corrupts the whole dungeon topology. [GAP — add a graph-review AI pass and a build-time sanity check (no orphans, no cycles where forbidden, every node has a room).]
    R3 — Two figure tracks (kernel/Asymptote vs matplotlib) = more surface; mitigated by both emitting the same VectorDoc so the baker is renderer-agnostic.
    R4 — geomkernel is unwritten [GAP] — Asymptote fallback at the cost of a second language.
    R5 — Baker determinism across machines isn't bit-perfect; mitigated because only the build machine bakes and ships PNGs.
    R6 — Scale. Principia has hundreds of propositions; FR legibility, height-layer growth, room count, and the time/cost of hundreds of figures × multiple AI round-trips are real and largely un-estimated. [GAP — measure on a real section at M8 before committing to the full book; expect this to be the dominant cost.]

Comfort:

    R7 — Co-op true-3D nausea. Structural mitigations: single-owner heading (Mover), decoupled damped camera (Shooter never rotates view), pitch clamp, no head-bob, vignette, slow walk, teleport-snap at portals.
    R8 — Wireframe vertigo (no ground). Never-black horizon + guide-line felt floor.

Engineering:

    R9 — Thin-line dropout at dense crossings (no-blend depth on antialiased lines): camera-facing line-quads + small depth bias; depth-only prepass toggle for dense graphs.
    R10 — Layout reproducibility hole (FR not bit-stable across BLAS/NumPy): lay out once on the build machine, ship the fixed-precision floorplan as source of truth.
    R11 — Dense graphs → tall stacks: layer caps → deterministic re-seed at build.
    R12 — Wall legibility of dense math at distance/angle. The core "read the walls" fantasy may be hard without help; Read Mode is the escape hatch — build it early (M6). [GAP — also needs a concrete "which panel does Read Mode target?" rule: aimed-at panel first, else nearest within a cone; specify at M6.]
    R13 — Frozen-contract drift in the LLM line: contracts live only in contracts.py; CI fails on signature change without a contract-version bump; Architect-gated.
    R14 — Headless CI for a GPU game: headless-first design; pure logic fully testable; GPU tests skip gracefully (pyglet headless helps).

16. COLLECTED GAPS

    [GAP] geomkernel must be written, or replaced by Asymptote (decide at M5).
    [GAP] Audio/music + atmospheric sound design — unspecified; address before M8.
    [GAP] Concept-graph extraction correctness — add a review pass + build sanity checks (R2).
    [GAP] Exact library patch versions — pin via one PyPI check each (§11.1); I refuse to invent them.
    [GAP] Read-Mode target-selection rule — specify at M6 (R12).
    [GAP] Real-figure round-trip count and total pipeline cost/time at Principia scale — measure at M5/M8 (R6); this is the single biggest empirical unknown.
    [GAP] TARDIS spatial reconciliation at the door — confirm own-coordinate-space interiors work with real rooms (M6).
    [GAP] FR layout bit-reproducibility — handled by "lay out once, ship the floorplan," but verify on your target machines.

Closing note (honest)

The two things most likely to make or break this are (a) AI figure correctness and (b) co-op true-3D comfort. I've designed both as structural solutions rather than hopeful ones — construction-not-coordinates + a verifier loop + the reproduction-fidelity reframe for (a); single-owner heading + a decoupled damped camera for (b) — and front-loaded the figure pipeline to M5 so the riskiest assumption is tested before the bulk of content work. Everything else — layout determinism, the baker, the data format, the module assembly line, the stack — is conventional engineering with known parts. The biggest uncosted unknown is sheer scale: hundreds of Principia figures, each with several AI round-trips. Measure that early; it will dominate your timeline more than any code.

--- END VERBATIM ---
