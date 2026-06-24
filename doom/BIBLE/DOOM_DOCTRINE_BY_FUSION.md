Hello Nir! 😊 This is a wonderful, ambitious project — and the good news is it maps cleanly onto a workable architecture. Below is the complete Master Design Document you asked for: the top-layer file you'll hand to every "parent" chat in the future. I've made all the decisions for you, with the reasoning where it matters, and I've added a final section addressing five real risks that need solving before you build.

I'll offer at the end to generate the actual repo skeleton and a runnable "walking demo" for you.
PRINCIPIA DESCENT — MASTER DESIGN DOCUMENT

Top-layer specification for the peaktogether.me geometric-proof FPS engine. Paste the relevant sections into every parent/child chat.

Owner: Nir · License: open-source forever (MIT for code, CC-BY-SA for content — see §13)
0. HOW TO USE THIS DOCUMENT (the parent–child protocol)

There are three roles:

    PARENT (Opus, the architect): holds this document + a small project ledger (what's done, which level IDs, which seeds). Never writes big code. Decomposes work into self-contained child tasks, each scoped to ONE module, pasting only that module's interface contract (§6) and the relevant data schema (§7). This is what keeps the parent's context small.
    CHILD (a fresh chat): receives the relevant sections + ONE module's contract + the schemas it touches, and produces one big copy-paste file implementing exactly that, assuming all other modules behave per their contracts. The child's memory is expendable; it may ask you for whole source files or for book/Wikipedia text.
    RUNNER (DeepSeek in OpenCode): pastes child code into the GitHub repo, runs it, runs tests, reports errors up.

The Prime Directive that makes this work: Modules communicate ONLY through (1) typed function signatures and (2) JSON/dataclass data contracts. If a child never needs another module's internals, parents stay light and children stay parallelizable. All interfaces are frozen unless the parent explicitly versions them.

The project lives in three separate worlds — keep them apart at all costs:

    CONTENT (book text, proofs, color choices) — never touches Python rendering.
    BUILD/OFFLINE (LaTeX baking, graph layout, floor textures) — heavy work, run on your PC.
    RUNTIME (the game) — only loads already-baked PNGs + JSON. The runtime never needs to understand Newton. This is what makes the engine reusable for Needham and Schey later.

1. VISION & HARD INVARIANTS

A first-person "art-gallery dungeon" where the walls are the mathematics. Players walk an Obsidian-style concept map (painted on the floor), reading Newton's geometric proof steps on walls, with equations on the ceiling unlocked by slaying a harmless demon. Two players (a couple) cooperate: one drives, one aims/shoots-to-reveal. The only difficulty is understanding the math.

Invariants (never break without a version bump):

    Python, runs on Windows (required), Linux (nice-to-have).
    God mode always — no death, no damage, infinite ammo. Shooting is a learning verb, not combat.
    One room or one corridor rendered per frame (never the whole level).
    Flat world — one ceiling height everywhere, low ceiling (for readability), no jumping, no stairs/elevators/bridges/multi-floor. Mouse-look up/down only.
    Walls fully filled with content — one image per wall block.
    Heavy preprocessing is offline & free — diagrams/text/equations baked to PNG ahead of time; runtime only loads images.
    The engine is GENERIC. "Principia" is a content pack, not the engine.
    Educational quality > graphics fidelity.

2. ENGINE DECISION

Decision: Ursina (which runs on Panda3D underneath). Runner-up: raw Panda3D.
Rank	Library	Pros	Cons
1 ✅	Ursina	Tiny code per entity (Entity(model='quad', texture=png)) → ideal for LLM-generated code & small parent context. Built-in first-person controller, mouse-look, raycasting, billboards. Panda3D scene graph underneath gives clean per-room load/unload (entity.enable()/disable()).	Native gamepad handling is weak → we wrap it (see §8). Performance modest, but irrelevant since we draw one room.
2	Panda3D (direct)	Robust, explicit, excellent scene graph for room culling, good controller support, very stable.	More verbose → bigger child prompts, more parent context.
3	raylib / pyray	Fast, great built-in gamepad.	No scene graph; you'd hand-build room visibility, picking, billboards.
4	pygame + custom raycaster	Closest Doom feel, great joystick support.	You'd re-invent a textured 3D renderer; mouse-look up/down + rich wall textures get painful.
5	ModernGL / raw OpenGL	Max control.	Far too low-level for vibe coding. Rejected.

Why Ursina wins for this project: the entire world is textured quads (walls/floor/ceiling) + billboard sprites (demon circles) + an FPS camera with vertical look — Ursina's exact sweet spot, producible in a handful of lines per entity. Because we render one room at a time, its modest performance ceiling never bites. Panda3D underneath is there if a child ever needs lower-level control.

The one real downside — split co-op input and gamepads — is the most important design risk and is fully solved in §8 + §10·R2. We abstract ALL input behind one InputManager that reads gamepad/joystick via pygame's joystick subsystem (run alongside Ursina) and keyboard/mouse via Ursina. Modules never touch raw devices; they ask for semantic actions.

Pinned stack: Python 3.11+, ursina, panda3d (transitive), pygame (input + audio only), pillow, numpy, networkx, pydantic. Offline-only tools (not runtime deps): your LaTeX toolchain + pdftoppm/pdf2image.
3. GEOMETRY & LATEX PIPELINE DECISION

Decision: Diagrams in TikZ/PGF; text panels & equations in LaTeX (reusing your existing baker). Each wall block baked to two PNGs (off grayscale, on color) using a shared color-group convention so the same concept is the same color in diagram and text. Asymptote held in reserve for the future 3D figures in Schey's vector-calculus book; GeoGebra is only an optional human sketchpad that exports to TikZ; Manim / matplotlib / AlphaGeometry are out of the runtime asset path (Manim animates, matplotlib is poor for classical compass-and-straightedge figures, AlphaGeometry is a prover not a renderer).

Why TikZ: you already have LaTeX; it gives precise classical geometry, pure-text (git-friendly, LLM-authorable) source, native math labels, and trivial color-group control. LLMs write TikZ very well.
The color-group convention (the heart of the "same color everywhere" mechanic)

Every wall block ships a tiny sidecar colors.json:

{ "groups": { "abc": "#1f77ff", "bd": "#e63946" } }

Both the TikZ diagram and the LaTeX text reference colors by group name, never raw hex. The baker injects a generated \definecolor preamble from colors.json into both compiles, so "abc" is the same blue in figure and prose automatically, per wall. Compiling twice (off/on) gives both states from one source.

Standard preamble the baker injects:

% bake.py sets \ONtrue (color) or \ONfalse (grayscale)
% and injects \definecolor lines from colors.json, e.g.:
% \definecolor{cg_abc}{HTML}{1F77FF}
\newif\ifON
\newcommand{\cg}[2]{\ifON\textcolor{cg_#1}{#2}\else\textcolor{black!75}{#2}\fi}
% Use in TikZ nodes AND in prose: \cg{abc}{$\angle ABC$}

The baking process (offline, deterministic)

A single tools/bake.py walks the content pack:

    For each .tex block: Pass A (off) with \ONfalse → <id>_off.png; Pass B (on) with \ONtrue → <id>_on.png.
    pdflatex/lualatex → PDF → pdftoppm -png -r 300 (or your existing baker) → Pillow auto-trim transparent crop.
    Standardize aspect to the wall quad, record width/height.
    Ceiling equations: bake one neutral black PNG on transparent; the blood-red tint and reveal happen at runtime (Ursina tints the texture). Keeps "demonic reveal" a render concern.
    Emit manifest.json mapping each block id → {off_png, on_png, w_px, h_px}. The engine reads only this manifest.

(See §12·R1 for how the off/on states also encode redundant non-color cues for colorblind players.)
4. WORLD & GAMEPLAY MODEL

    Spatial model: flat plane at y=0, fixed low ceiling (e.g. 3.0 units; eye ~1.6). Rooms = axis-aligned rectangles; corridors = narrow rectangular hallways following b-splines. Only the occupied cell (+ optionally immediate neighbors) is instantiated.
    Floor (map of ideas): the whole concept graph painted as a big floor texture (Obsidian-style nodes + b-spline edges). Colored guide lines with arrowheads (Half-Life style) point toward each door. Each room's center has a big readable name tile. All baked offline (§7, §8).
    Walls (the math): each wall is split into wall blocks (gallery frames). Each block is one diagram step or one text panel, in reading order. Girlfriend's shot toggles off → on (sticky — records "read/understood").
    Ceiling (equations): a ceiling band above each wall section, hidden until the room's demon dies, then fades in blood-red. On demon death, equation glyphs also spray outward and vanish (pure flourish — not traced to final position; the placed ceiling band is the persistent copy).
    Enemy (demon): billboarded sprite circles (body pink, eyes blue, teeth white). Player can't die, infinite ammo. Death = disintegration: each circle flies a random direction and fades; triggers ceiling reveal + equation spray.
    Secret door (QED / ∎): the Halmos-tombstone tile on the final-proof wall. Shooting it opens it → boss demon emerges → kill it → room complete.
    Map mode: 2D wireframe automap (rooms as rects, corridors as lines, player marker, read/unread state), toggleable.
    Co-op: boyfriend = mover (joystick + keyboard); girlfriend = shooter (Xbox controller + mouse). One shared avatar, split responsibilities. (Camera/comfort details in §12·R2.)

5. RENDERING STRATEGY

    Each room/corridor is a separate scene-graph subtree (Ursina entity with children). On cell entry: enable() the current cell (+ optionally adjacent door surfaces), disable() the rest. This literally satisfies "draw one room per frame."
    Walls: textured quads from wall-segment + u_range + z_range; texture = off or on PNG; collision tag = block id. Shot → swap to on PNG.
    Floor: per-cell baked texture (keeps resolution high vs. one giant texture).
    Ceiling: low, textured. Equation bands are separate quads slightly below the ceiling (avoid z-fighting), hidden until reveal.
    Lighting: bright/unlit materials so panels stay legible. Style suggestion: dark stone room with emissive (self-lit) proof panels so text reads regardless of scene light. (Legibility settings in §12·R3.)

6. MODULE ARCHITECTURE & INTERFACES

Rules for children: Python 3.11, type hints mandatory, pydantic models for all data, no module imports another module's internals — only its public functions/classes below. One module = one file. Vec3 = tuple[float,float,float].

principia/
  app.py            # bootstrap + main loop wiring
  config.py         # constants & tunables (incl. comfort/legibility settings)
  schema.py         # pydantic models — THE data contracts
  content/loader.py # JSON pack -> models; validate_pack()
  layout/graph.py   # concept graph -> floorplan + floor-map image (offline-capable)
  world/builder.py  # models -> Ursina entities for ONE cell
  world/rooms.py    # RoomManager: load/unload current cell
  io/input.py       # InputManager: devices -> semantic actions (ONLY device-touching module)
  player/mover.py   # movement (boyfriend)
  player/shooter.py # aim + shoot raycast (girlfriend)
  walls/state.py    # wall block off/on toggle + save/load
  ceiling/equations.py # hidden/reveal + blood-red + spray
  enemy/demon.py    # sprite-circle demon + disintegration
  doors/secret.py   # QED secret door + boss spawn
  ui/mapmode.py     # 2D automap
  ui/hud.py         # reticle, prompts, progress
  ui/readmode.py    # crisp full-screen panel overlay (see R3)
  assets/manager.py # manifest.json -> textures
  audio/sound.py    # sfx
  nav/navigator.py  # which cell players are in; door transitions
tools/
  bake.py           # offline asset baker
  layout_render.py  # offline floor-map texture renderer
content_packs/principia/   # level*.json, walls/*.tex, manifest.json, png/...
tests/

Frozen interface contracts (abbreviated; full signatures handed per-child)

# content/loader.py
def load_level(pack_dir: str, level_id: str) -> Level: ...
def load_manifest(pack_dir: str) -> dict[str, AssetEntry]: ...
def validate_pack(pack_dir: str) -> list[str]: ...   # [] = OK

# layout/graph.py  (deterministic given seed)
def layout_level(graph: ConceptGraph, seed: int = 0) -> Floorplan: ...
def render_floor_map(fp: Floorplan, out_png: str, size_px: int = 4096) -> None: ...

# world/rooms.py
class RoomManager:
    def __init__(self, fp: Floorplan, assets: "AssetManager"): ...
    def enter_cell(self, cell_id: str) -> None: ...   # builds it, unloads others
    def current_cell(self) -> str: ...

# io/input.py  (the ONLY device-touching module)
class InputManager:
    def poll(self) -> None: ...
    def move_axis(self) -> tuple[float,float]: ...    # (strafe, forward) in [-1,1]   MOVER
    def aim_delta(self) -> tuple[float,float]: ...    # (yaw, pitch) deltas           SHOOTER
    def shoot_pressed(self) -> bool: ...              # edge-triggered
    def toggle_map_pressed(self) -> bool: ...
    def read_mode_pressed(self) -> bool: ...

# player/shooter.py
class Shooter:
    def update(self, dt: float) -> None: ...
    def register_hit_handlers(self, on_wall, on_demon, on_secret) -> None: ...

# walls/state.py
class WallStateManager:
    def register(self, block_id: str, entity, off_tex, on_tex) -> None: ...
    def toggle(self, block_id: str) -> bool: ...      # returns new state
    def progress(self, room_id: str) -> float: ...
    def save(self, path: str) -> None: ...
    def load(self, path: str) -> None: ...

# ceiling/equations.py
class CeilingManager:
    def reveal(self, room_id: str) -> None: ...       # blood-red fade-in
    def spray_from(self, origin: Vec3, glyph_texes: list) -> None: ...

# enemy/demon.py
class Demon:
    def hit(self, point: Vec3) -> None: ...
    def is_dead(self) -> bool: ...
    def on_death(self, callback) -> None: ...

# doors/secret.py
class SecretDoor:
    def shoot(self) -> None: ...                      # opens, spawns boss
    def on_boss_killed(self, callback) -> None: ...

# assets/manager.py
class AssetManager:
    def __init__(self, pack_dir: str): ...
    def wall_textures(self, block_id: str): ...       # (off, on)
    def equation_texture(self, eq_id: str): ...
    def floor_map_texture(self, level_id: str): ...

# nav/navigator.py
class Navigator:
    def update(self, player_pos: Vec3) -> None: ...   # detects door crossings -> enter_cell

app.py wiring order each frame: input.poll() → mover.update() → shooter.update() → navigator.update() → demon/ceiling updates → hud/map/readmode update.

Recommended build order (each independently testable): schema → assets/manager → content/loader → layout/graph → world/builder → world/rooms → nav/navigator → io/input → player/mover → player/shooter → walls/state → enemy/demon → ceiling/equations → doors/secret → ui/* → app.
7. DATA FORMATS (JSON, validated by pydantic in schema.py)

Two files per level keep authoring clean:

    Semantic level (human/LLM-authored): concept graph + room content + source refs. No coordinates.
    Playable level (tool-generated): geometry, wall placement, texture paths, doors, monsters. Runtime reads only this.

Concept graph (authoring input → §8 turns it into a floorplan)

{
  "level_id": "principia_book1_sec1",
  "nodes": [
    { "id": "lemma1", "name": "Lemma I", "importance": 5,
      "summary": "Quantities tending to equality become ultimately equal." }
  ],
  "edges": [
    { "source": "lemma1", "target": "lemma2", "weight": 2, "kind": "depends_on" }
  ]
}

importance 1–5 → room size. kind ∈ {depends_on, generalizes, example_of, related}.
Room content (the math; references baked assets)

{
  "room_id": "lemma1",
  "walls": [
    { "wall_id": "w_lemma1_N", "facing": "N",
      "blocks": [
        { "block_id": "l1_step1", "type": "diagram", "order": 1,
          "off_png": "png/l1_step1_off.png", "on_png": "png/l1_step1_on.png",
          "colors": { "abc": "#1f77ff", "bd": "#e63946" } },
        { "block_id": "l1_text1", "type": "text", "order": 2,
          "off_png": "png/l1_text1_off.png", "on_png": "png/l1_text1_on.png",
          "colors": { "abc": "#1f77ff", "bd": "#e63946" } }
      ] }
  ],
  "ceiling_bands": [
    { "band_id": "cb_l1_1", "above_wall": "w_lemma1_N",
      "equation_png": "png/eq_l1_1.png", "hidden_until_demon_dead": true }
  ],
  "demon": {
    "demon_id": "demon_lemma1", "position": [6,1.2,6], "hp": 3,
    "circles": [
      { "offset": [0,0,0], "radius": 0.6, "color": "#ff7ab6", "role": "body" },
      { "offset": [-0.2,0.25,0.55], "radius": 0.1, "color": "#3b6bff", "role": "eye" },
      { "offset": [ 0.2,0.25,0.55], "radius": 0.1, "color": "#3b6bff", "role": "eye" },
      { "offset": [0,-0.1,0.6], "radius": 0.06, "color": "#ffffff", "role": "tooth" }
    ],
    "spray_glyphs": ["png/eq_l1_1.png","png/eq_l1_2.png"]
  },
  "secret_door": {
    "door_id": "qed_lemma1", "wall_id": "w_lemma1_S",
    "tile_png": "png/qed_halmos.png", "position": [6,1.5,0.05],
    "boss": { "demon_id": "boss_lemma1", "position": [6,1.2,-3], "hp": 5, "circles": [] }
  }
}

Floorplan (output of layout_level)

{
  "level_id": "principia_book1_sec1", "ceiling_h": 3.0,
  "rooms": [
    { "id": "lemma1", "rect": {"x":0,"z":0,"w":12,"d":12}, "center":[6,0,6],
      "name_tile": "tiles/lemma1_name.png", "doors": ["door_l1_l2"] }
  ],
  "corridors": [
    { "id": "corr_l1_l2", "from": "lemma1", "to": "lemma2",
      "spline": [[6,0,12],[6,0,18],[10,0,24]], "width": 3.0, "guide_color": "#ffcc00" }
  ],
  "doors": [
    { "id": "door_l1_l2", "room": "lemma1", "corridor": "corr_l1_l2",
      "position": [6,0,12], "facing": "N", "width": 3.0 }
  ]
}

Save game

{ "level_id":"principia_book1_sec1",
  "blocks_on":["l1_step1","l1_text1"],
  "demons_dead":["demon_lemma1"],
  "secrets_open":["qed_lemma1"] }

8. GRAPH → FLOORPLAN LAYOUT ALGORITHM (deterministic by seed)

    Placement: networkx.spring_layout (Fruchterman–Reingold) with the given seed; edge spring length ∝ 1/weight (stronger relations sit closer).
    Room sizing: square side = base + k*importance (e.g. 8 + 2*importance). Also compute a panel-fit check: required wall length = Σ(panel preferred width + margin) + Σ(door widths); if it exceeds the room perimeter, enlarge the room and re-pack.
    De-overlap: snap centers to a coarse grid; iteratively push overlapping rectangles (+ margin) apart along their center-difference vector until stable. Guarantees walkable gaps.
    Corridors: for each edge, find the door points where the center-to-center line crosses each room's boundary (defines door facing/position/width). Build a smooth Catmull-Rom / b-spline through door_source → 1–2 offset midpoints → door_target; sample to a polyline. Width ∝ weight.
    No-bridge rule: if two corridors would cross, reroute one; only insert a small junction room if it's pedagogically meaningful.
    Guide lines: per door, a colored floor stripe with arrowheads from room center → door, color keyed by destination.
    Bake floor map: draw nodes/edges/labels + guide overlay into one big PNG, then either UV-map sub-rectangles per cell or bake per-cell tiles (recommended for resolution).
    Wall slotting: distribute a room's blocks across N/E/S/W (minus door gaps) in order; reserve the segment with the ∎ tile for the secret door (default S wall).

Store the seed in the level JSON so screenshots/content are reproducible.
9. CONTENT-AUTHORING "FOREVER PROMPT"

This is the reusable, book-agnostic methodology that turns (book text + Wikipedia) into a content pack, before any game code. Paste into a fresh child chat:

    ROLE: You are a Content-Authoring child for the Principia Descent educational FPS engine. You convert a chunk of a math book into a validated content pack following the engine's data contracts (Master Design Doc §4, §7, §8, plus the §3 color convention). You do NOT write game code.

    STEP 1 — GATHER. Ask Nir to paste: the exact book passage(s) (definitions, lemmas, propositions, proofs, figure descriptions) and the relevant Wikipedia text. If a referenced lemma/figure/symbol is missing, STOP and ask Nir to paste it. Read recursively until self-contained. Confirm before Step 2.

    STEP 2 — CONCEPT GRAPH. Output concept_graph.json (§7): one node per lemma/proposition/definition; edges = logical dependencies with kind/weight; importance 1–5 from dependency count; one-sentence summary.

    STEP 3 — ROOM CONTENT. For each node, output room JSON (§7) with placeholder PNG paths, PLUS:

        For each diagram step: a complete standalone TikZ file using \cg{group}{...} macros (never raw colors). Steps cumulative/readable left→right.
        For each text panel / equation: complete LaTeX, reusing the same group names so colors match the diagram.
        The per-wall colors map (group → hex), drawn from the colorblind-safe palette in §12·R1, with redundant cues per R1.
        Fill demon.circles and the secret_door (∎ tile) on the final wall.
        Optionally author one comprehension prompt per room per §12·R4.

    STEP 4 — SELF-CHECK. Every block has both color-group states; every equation maps to a wall section; reading order is sound; JSON validates. List assumptions. Output as copy-paste blocks grouped by file path.

    CONSTRAINTS: No invented mathematics — only what the source supports. One readable idea per panel. Prefer more, smaller steps over dense ones.

Run parallel "verification children" that mark each claim supported / unsupported / ambiguous against the numbered source packets, to curb hallucination. The parent keeps a ledger of done sections + seeds.
10. ROADMAP

    M0 Walking skeleton: Ursina app, one hard-coded textured room, FPS controller, mouse-look.
    M1 Data-driven room from JSON + placeholder PNGs.
    M2 Shoot-to-reveal: InputManager (mouse+kb first), Shooter raycast, WallStateManager off→on + save/load.
    M3 Demon + ceiling reveal + spray + read-mode overlay (R3).
    M4 Multi-room: layout/graph, RoomManager load/unload, Navigator, floor map + guide lines, map mode.
    M5 Secret door + boss.
    M6 Co-op input (Xbox + joystick split per R2 comfort scheme).
    M7 First real Principia content pack via §9; playtest with target couples (incl. assessment per R4).
    M8 Generalize: swap in a second pack (later Needham/Schey).

11. REPO, BUILD & RUN

    Offline build: python tools/bake.py content_packs/principia then python tools/layout_render.py content_packs/principia.
    Run: python -m principia.app --pack content_packs/principia --level principia_book1_sec1.
    Windows packaging: PyInstaller one-folder (Ursina/Panda3D package cleanly); ship the content pack alongside.
    CI: GitHub Actions runs pytest + validate_pack headless on every push. Add a tiny golden fixture level (2 rooms, 1 corridor, 1 panel, 1 QED panel, 1 demon, 1 equation) every module tests against. Freeze a schema_version string in every JSON and assert it on load — this is your defense against silent interface drift between child chats.

12. RISK SECTION — five problems the first design pass missed (with concrete fixes)

These are the things that will actually break the player experience if ignored. Bake these rules into the content and engine from day one.
R1 — Colorblindness (this threatens your core mechanic)

~8% of your boyfriend demographic is red–green colorblind, and your whole pedagogy is "this concept is blue, that one is red." Color must never be the only cue. Make every color-group carry redundant signals, baked into the TikZ/LaTeX:

    Numbered/lettered tags. Each color group gets a small integer-in-a-circle badge (①②③…) placed both next to the diagram element and inline in the prose. Now "the blue angle" is also "angle ①" — readable by anyone.
    Line styles for line groups. In TikZ, vary dash pattern per group: group 1 solid, group 2 dashed, group 3 dotted, group 4 dash-dot. (\draw[cg_abc, thick, densely dashed]).
    Glyph/marker shapes for point groups. Different point marks per group (circle, square, triangle, diamond) via TikZ mark=....
    Hatching/pattern fills for region groups (pattern=north east lines, pattern=dots).
    Colorblind-safe base palette. Use Paul Tol's "bright" or Okabe–Ito (both designed for CVD). A safe 8-color set (Okabe–Ito): black #000000, orange #E69F00, sky-blue #56B4E9, bluish-green #009E73, yellow #F0E442, blue #0072B2, vermillion #D55E00, reddish-purple #CC79A7. Avoid pure red-vs-green pairs as the only distinction.
    Implementation in the convention: extend \cg so it can also emit the badge/marker. Have your child author put a \groupbadge{abc} next to each tagged element. The baker reads colors.json, which now also stores { "abc": { "hex":"#0072B2", "badge":1, "dash":"solid", "mark":"circle" } }.
    Optional in-game colorblind mode (config.py): a cvd_mode flag that simply loads an alternate baked PNG set rendered with the badges enlarged / palette remapped. Because everything is pre-baked, this is just "swap texture folder," no shader work. Recommendation: always bake badges in (they help everyone via the generation/labeling effect) and make a high-contrast palette the default; the toggle is a bonus.

R2 — Split-control co-op comfort (the make-or-break for "romantic evening")

The dangerous question: if the aimer freely swings yaw/pitch while the mover walks "forward," is "forward" the aim direction? If yes, the mover gets yanked sideways every time their partner looks around → nausea + arguments. Decouple them.

Decided comfort scheme (museum mode):

    Two separate things: a body (position + a body heading) and an aim reticle (free yaw/pitch overlay).
    Mover controls the body heading and translation. "Forward" = the body heading, which only the mover changes (left stick / A&D rotates body, W/S walks). Strafing optional. The mover's world never lurches because someone else looked away.
    Aimer controls the reticle (a free-look cursor) within a generous cone, and shoots. The camera follows the body heading with a soft, damped/smoothed offset toward the reticle (so the partner can glance at a wall without spinning the whole view). Clamp pitch to ±70°. When the aimer wants to read a wall behind them, the mover turns the body — this forces gentle teamwork, which is exactly the couple dynamic you want.
    Comfort options in config.py: fov = 75–80 (narrower FOV reduces sickness; lower it further in an options menu), movement_smoothing (acceleration ramp, no instant velocity), turn_smoothing, optional vignette during motion, optional snap-turn for the body, head-bob OFF by default, slow default walk speed (this is a reading game). Provide a "comfort" preset that maxes all of these.
    Reticle, not crosshair-locked camera: because the aimer moves a reticle rather than the whole camera, neither player induces large involuntary view rotation in the other → this is the single biggest nausea reducer.
    Same-screen courtesy: keep vertical look gentle (the ceiling equations are just above, so small upward tilt suffices — the low ceiling is your friend).

R3 — Text legibility on 3D walls

LaTeX text on angled/distant quads blurs without care. Concrete rules:

    Texture resolution per wall: target ~256–384 px per real-world meter of wall. A 3 m wide panel → ~1024–1536 px wide; baking at 2048 wide is safe headroom. Bake panels at the size in §3 (e.g. 2048×1536) and don't exceed GPU max (4096) per quad.
    Mipmaps + anisotropic filtering (kills shimmer at grazing angles). In Panda3D/Ursina:

    from panda3d.core import SamplerState, Texture
    tex = entity.texture            # the Panda3D Texture
    tex.setMinfilter(SamplerState.FT_linear_mipmap_linear)
    tex.setMagfilter(SamplerState.FT_linear)
    tex.setAnisotropicDegree(16)

    In Ursina you can usually set
    entity.texture.filtering = 'bilinear' and then drop to the Panda3D handle (entity.model.getTexture() or the texture you loaded) for the mipmap/aniso lines above.
    LaTeX font size: author panels so the smallest glyph is ≥ ~28–32 px in the baked PNG at the chosen resolution (i.e. use large body font, \Large/\LARGE, short lines). One idea per panel (you already want this).
    Emissive panels so text reads regardless of room lighting (set the panel material unlit/full-bright).
    Minimum readable distance design: size blocks so a player standing ~1.5–2 m back reads comfortably; don't pack tiny paragraphs.
    The decisive fix — ui/readmode.py "focus/read mode": when players walk close to a block (or press the read button), snap a crisp full-screen 2D overlay of that panel's PNG (rendered as a flat UI image, no perspective, no mipmap loss) — perfectly sharp, zoomable. This sidesteps all 3D-text-blur problems for the actual reading, while the walls still look great in 3D. Strongly recommend shipping this from M3. (SDF text is overkill here since panels are pre-baked images, not live fonts.)

R4 — Does it actually teach? (and how to check, gently)

Walking-and-shooting doesn't automatically beat reading — but you can make it beat reading by leaning on real learning science, without adding fail states:

    The shoot-to-colorize IS active recall + the generation effect. Make it prompt before reveal: when the girlfriend shoots an off block, briefly show a one-line question or "what do you predict this step shows?" (from the room's authored comprehension prompt), then reveal the colored panel. Predicting-before-seeing is one of the most robust learning boosts.
    Dual coding: you already pair diagram + text + (later) equation — that's exactly the multimedia principle. The color-group linking (R1 badges) reinforces it.
    Teach-back / the two-player dynamic is your secret weapon. Add a tiny prompt at the QED tile: "Before you open the door, [mover] explain this proof to [aimer] in one sentence." Explaining to a partner (the protégé effect) is among the strongest known interventions — and it fits the romantic co-op perfectly.
    Optional "quiz demon": the room's demon can be made to only become vulnerable after the players have toggled all blocks on (i.e. read everything) — soft gating, no failure, just "you can't exorcise it until you've seen the proof." The boss at the QED door can pose one multiple-choice question (chosen by shooting the correct answer floating in the air); a wrong shot just bounces off (no penalty) — that's retrieval practice with zero stakes.
    Spaced retrieval across sessions: on revisiting a completed room, dim a couple of previously-colored blocks back toward off and ask the players to re-predict before re-coloring — lightweight spaced repetition baked into the save file.
    Keep it no-pressure: every check is "answer or skip," no timers, no lives. The fun is the exploration; the science just nudges retention.

R5 — Licensing (Wikipedia + LaTeX + open-source forever)

    Newton's 1687 Principia text & original figures: public domain — use freely (your own redrawn TikZ versions are your copyright, which you then license openly).
    Wikipedia text is CC-BY-SA. If you bake Wikipedia prose into panels, you incur attribution + share-alike: (a) credit the source article(s) and the CC-BY-SA license, (b) license that derived content under CC-BY-SA too. Practically: prefer paraphrasing/rewriting Wikipedia into your own explanatory prose (facts aren't copyrightable; your wording is yours) — this avoids share-alike entanglement entirely. Where you do quote/adapt directly, attribute it.
    Recommended split: code = MIT (or Apache-2.0); content (panels, diagrams, text, level packs) = CC-BY-SA 4.0 (compatible with incorporating Wikipedia material, and matches your "free forever" ethos). Keep a CREDITS.md / per-pack ATTRIBUTION.md listing every Wikipedia article used + its contributors link + the CC-BY-SA notice. Ship LICENSE (code) and LICENSE-CONTENT (CC-BY-SA) in the repo.
    Fonts/tools: stick to permissively licensed fonts in your LaTeX (Computer Modern / Latin Modern are fine). Note that output PNGs are your content; the LaTeX engine license doesn't restrict your output.

13. DECISIONS SUMMARY

    Engine: Ursina (on Panda3D); gamepad/co-op solved by a pygame-backed InputManager.
    Pipeline: TikZ diagrams + LaTeX text/equations → two baked PNGs (off/on) via a shared color-group convention; Asymptote reserved for future 3D; GeoGebra only as a sketch-to-TikZ aid.
    Architecture: ~20 single-file modules, communicating only via frozen function contracts (§6) + pydantic/JSON data contracts (§7) → bounds parent context to one module at a time.
    Data: semantic level → floorplan → room content → manifest → save (§7).
    Layout: spring placement → importance+panel-fit room sizing → de-overlap → b-spline corridors with boundary-crossing doors → guide lines → baked floor map (§8).
    Authoring: the reusable "Forever Prompt" (§9) drives book+Wikipedia → validated pack.
    Comfort/legibility/accessibility/efficacy/licensing: solved concretely in §12.

That's the full master document. A few honest cautions worth your attention as you proceed: the split-camera co-op is the riskiest part of the whole concept — build the R2 scheme early and playtest it with a real couple before investing in content; and schema-version every JSON so your parallel child chats can't silently drift apart.

Would you like me to now (a) generate the actual GitHub repo skeleton — all ~20 module files with the frozen signatures, docstrings, and NotImplementedError stubs, plus schema.py pydantic models and a tiny golden-fixture test level — and (b) write the M0 runnable "walking demo" app.py (one textured room, mouse-look, WASD) so you have something to run on Windows today? I can produce either or both right now as copy-paste blocks for DeepSeek. 🙂
