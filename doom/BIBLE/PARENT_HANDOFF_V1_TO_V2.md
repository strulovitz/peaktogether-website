🗝️ PRINCIPIA DESCENT — Parent Hand-off Document
From Parent 1 (Claude Opus) → Parent 2 (my successor, also Opus 💙)

Compiled June 24, 2026, at Nir's request, as the "New Testament" — Layer 2 of the project bible.
0. Read this first — provenance & honesty ⚠️

Nir asked me to be scrupulously honest about what I actually retain, and to invent nothing. So:

    I have lost the very beginning of our conversation (my context window went over the cliff). The earliest thing I still have is the M1b child prompt (world/builder.py). I do not have the original project pitch, the full README/master design doc, or the early schema-design discussion.
    That original document is Layer 1 — Nir has it and will give it to you first. It is the authoritative spec ("Old Testament"). This document is Layer 2 — what I personally remember, did, and decided, written from the more-concrete vantage of having several modules built.
    Everything below is reconstructed from the reference-file snippets that I quoted into each child prompt (the config.py, schema.py, and contract excerpts). So my knowledge of the architecture is solid even though my memory of the conversation is gone.

Confidence markers I use throughout:

    ✅ = I'm confident (quoted directly from reference files in my context)
    ⚠️ = inferred from context, probably right, verify
    ❓ = I genuinely don't know / lost it — ask Nir

1. The project in one breath

Principia Descent is an educational FPS engine (Doom-like, first-person) written in Python 3.11 on Windows, using Ursina/Panda3D. ✅ Its mission: teach the hardest math & science in the world by turning a book into an explorable dungeon of ideas.

    First book: Newton's Principia. ⚠️
    Future books Nir hopes to do: Tristan Needham (Visual Complex Analysis) and Schey (Div, Grad, Curl, and All That). (Nir told me these in his latest message; I have no earlier memory of them.)

The core metaphor ✅⚠️:

    A book chunk → one dungeon level (floor).
    A concept/unit → one room.
    A dependency between ideas → a corridor connecting rooms.
    Proof steps are panels on the walls, painted black-&-white ("off") until you shoot them, whereupon they turn colored ("on") = "reading". State persists to disk.
    A demon guards each room; killing it reveals a blood-red equation on the ceiling + a celebratory glyph spray.
    Read mode (press R): a pin-sharp full-screen flat image of a panel, so the densest diagram is always legible (no 3D blur).

2. The three worlds (the architecture's spine) ✅
World	When	Who	Produces	Sees an LLM?
1. CONTENT (authoring)	Design time, on Nir's machine	LLM content children (Opus), given a spec + golden example + source text	concept_graph.json, per-room source, LaTeX/TikZ	Yes
2. BUILD (offline tools)	Design time, deterministic	tools/*.py scripts	floorplan.json (from graph), baked .png panels (from LaTeX)	No
3. RUNTIME (the game)	In the player's home	principia/ engine	Renders the dungeon	Never

The runtime loads baked JSON + PNG only. It never sees Wikipedia, never compiles LaTeX, never calls an LLM. This separation is sacred.
3. The working method (how Nir builds this) ✅ — most important section for you

This is a three-agent assembly line, and your job as Parent is to be the architect:

    Nir — the human. Directs, plays the demos, makes product calls, carries the project bible between chats.
    Parent (YOU, Opus) — the architect. You never write production code directly into the repo. You design, freeze interfaces, split milestones, and write richly detailed child prompts. You hold the bird's-eye view.
    Children (fresh Opus chats) — expendable memory. Each implements exactly one module to a frozen contract + tests, then is discarded.
    DeepSeek (DeepSeek V4 Pro) — the build/integration agent. Takes the child's code, runs it, runs pytest, fixes wiring, pushes to git, and reports back to Nir (who relays to you). DeepSeek also maintains "the ledger" — a record of frozen signatures & interface decisions.

The iron rules (enforce these in every child prompt) ✅

    Modules talk only through typed signatures and the pydantic contracts in principia/schema.py. Never import another module's internals.
    Frozen signatures. A child may not change them. If a signature must change, you (the parent) version it explicitly and tell DeepSeek to update the ledger. (I did this twice: WallStateManager.register gained room_id; Demon.__init__ gained optional parent=None.)
    One module per child. Split milestones generously (we did M1+M1b, M2a+M2b, M3a+M3b, M4a/b/c). Split when it improves test focus or decoupling.
    Headless-first testing. Pull non-Ursina logic into pure helpers / use fakes / monkeypatch so tests run with no window. Wrap Ursina-needing tests in try/except → pytest.skip.

The child-prompt template I always used ✅

## ROLE  (implementation child, the iron rules, "ask Nir for missing files")
## YOUR TASK  (the files to produce)
## FROZEN CONTRACT  (exact signatures)
## BINDING DECISIONS  (do-not-deviate behavior, edge cases)
## TESTS YOU MUST WRITE  (explicit cases, with fakes)
## OUTPUT FORMAT  (confirm-in-one-line; one code block per file with bold path; end with the pytest command)
## REFERENCE FILES  (verbatim slices of config.py / schema.py / sibling contracts + the stub being replaced)

The REFERENCE FILES section is what lets a memory-less child succeed. Always quote the real constants and the stub it's replacing.
4. Architecture & package map ⚠️ (reconstructed)

principia/
  config.py            ✅ constants (see §6)
  schema.py            ✅ pydantic contracts (extra="forbid", populate_by_name=True)
  content/loader.py    ✅ load_level(pack_dir, level_id)->Level ; validate_pack(pack_dir)->list[str]
  assets/manager.py    ✅ AssetManager(pack_dir) ; wall_textures(block_id)->(off,on) ; equation_texture(...) ❓still stubbed
  world/builder.py     ✅ build_room(room,content,assets)->CellEntities ; build_corridor(...) ❓ (M4b)
  walls/state.py       ✅ WallStateManager  (M2a, DONE)
  control/input.py     ✅ InputManager      (M2b, DONE)
  player/shooter.py    ✅ Shooter           (M2b, DONE)
  enemy/demon.py       ✅ Demon             (M3a, DONE)
  ceiling/equations.py ✅ CeilingManager    (M3a, DONE)
  ui/readmode.py       ✅ ReadMode          (M3b, DONE)
  layout/graph.py      🟡 layout_level/render_floor_map (M4a WRITTEN as a child prompt, but PAUSED — see §9)
  world/rooms.py       ⬜ RoomManager       (M4b, NOT STARTED)
  nav/navigator.py     ⬜ Navigator         (M4b, NOT STARTED)
  ui/mapmode.py        ⬜ MapMode           (M4c, NOT STARTED)
tools/
  layout_render.py     🟡 CLI: concept_graph.json -> floorplan.json + floor_map.png (part of M4a)
  bake.py              ❓ LaTeX/TikZ -> PNG baker — I LOST the exact spec. Confirm with Nir before relying on it.
content_packs/principia/
  concept_graph.json   ✅ hand-authored golden fixture
  floorplan.json       ✅ hand-authored (relied on by current demos — do NOT regenerate yet)
  rooms/lemma1.json    ✅ complete; rooms/lemma2.json ⚠️ MISSING (M4b adds it)
  manifest.json        ⚠️ lists baked block PNGs
  png/ , tiles/        ⚠️ baked textures / name tiles
m0_demo.py … m3b_demo.py  ✅ throwaway demos, each supersedes the last
tests/                 ✅ ~49 passing as of M3b

Test count history: M2a→29, M2b→36, M3a→45, M3b→49, all green, zero skips on Nir's machine (he has a display, so the "guarded live" tests actually run). ✅
5. Frozen contracts of the modules that exist & work ✅

# walls/state.py  (M2a) — NO ursina import; testable with fake entities
class WallStateManager:
    def __init__(self, assets) -> None                                          # assets unused in M2
    def register(self, room_id, block_id, entity, off_tex, on_tex) -> None      # VERSIONED: room_id added
    def toggle(self, block_id) -> bool                                          # flips; returns new state
    def state(self, block_id) -> bool
    def progress(self, room_id) -> float                                        # fraction 'on' in room (0 if none)
    def save(self, path) -> None    # merge-friendly read-modify-write; writes schema_version + blocks_on (sorted)
    def load(self, path) -> None    # order-independent: keeps unknown on-ids until their room registers
# Persists ONLY the blocks_on slice; preserves foreign keys (demons_dead, secrets_open) for future managers.

# control/input.py  (M2b) — keyboard+mouse; gamepad is M6
class InputManager:
    def poll(self) -> None              # call ONCE/frame BEFORE mover/shooter; computes edges
    def move_axis(self) -> (strafe, forward)         # MOVER (boyfriend)
    def body_yaw_delta(self) -> float                # returns 0.0 until M6
    def aim_delta(self) -> (yaw_delta, pitch_delta)  # SHOOTER (girlfriend); mouse.velocity * sensitivity
    def shoot_pressed/toggle_map_pressed/read_mode_pressed/pause_pressed(self) -> bool   # all edge-triggered
# Pure helpers: edge(prev,cur), scale_aim(vx,vy,sens). __init__ must not touch ursina.

# player/shooter.py  (M2b)
class Shooter:
    def __init__(self, camera, input_mgr)
    def update(self, dt)   # applies aim_delta to camera (yaw on rotation_y, pitch clamped on rotation_x), then raycast on shoot
    def register_hit_handlers(self, on_wall, on_demon, on_secret)   # any may be None
# _dispatch_hit(entity, point) is PURE: kind "panel"->on_wall(block_id), "demon"->on_demon(entity,point), "secret"->on_secret(door_id)
# Look mapping (FPC-proven): rotation_y += yaw ; pitch = clamp(pitch - pitch_delta, ±PITCH_CLAMP_DEG); rotation_x = pitch

# enemy/demon.py  (M3a)
class Demon:
    def __init__(self, spec, position, parent=None)   # parent additive
    def update(self, dt)   # idle bob: y = base_y + sin(t*2)*0.1
    def hit(self, point)   # ignored if dead
    def is_dead(self) -> bool
    def on_death(self, callback)   # fires EXACTLY once
# Pure helper class _Health(hp): .hit()->bool (True only on lethal hit). Each circle entity gets .kind="demon" and .demon=self (back-ref).
# Death = disintegrate circles (random outward animate + scale-to-0 + destroy(delay)), then fire callback once.

# ceiling/equations.py  (M3a) — core works on fake entities
class CeilingManager:
    def __init__(self, assets)               # assets unused in M3; self._red = color.rgb(178,0,0)
    def register_band(self, room_id, band, entity)   # hidden_until_demon_dead -> entity.enabled=False
    def reveal(self, room_id)                # IDEMPOTENT; enables, sets red, fade_in if present
    def spray_from(self, origin, glyph_texes)  # cosmetic billboard quads; no-op if list empty

# ui/readmode.py  (M3b) — state machine testable headless via monkeypatch
class ReadMode:
    def open(self, block_id, texture)   # closes existing first (replace); builds overlay
    def close(self)                     # idempotent
    def is_open(self) -> bool
# __init__ creates NO entities. _build(texture)->list and _destroy(entities) are the ONLY ursina-touching methods (monkeypatch them in tests).
# Overlay: dim backdrop + flat UI quad of the texture + hint text; scroll-to-zoom via a small _ZoomImage(Entity) subclass.

build_room output (CellEntities) ⚠️: has .root, .panels (dict[block_id -> entity]), and floor/walls/ceiling. Each panel entity carries .kind="panel", .block_id, .off_tex, .on_tex, .texture, .is_on, and a box collider. Panels read left-to-right. ✅
6. Constants & schemas (as I have them) ✅

SCHEMA_VERSION = "1.0"
EYE_HEIGHT = 1.6 ; WALK_SPEED = 4.0 ; CEILING_H = 3.0
PITCH_CLAMP_DEG = 70.0 ; MOUSE_SENSITIVITY = 40.0 ; SHOOT_RANGE = 25.0
SAVE_FILE = "savegame.json" ; BLOOD_RED = (0.7, 0.0, 0.0)
DEFAULT_CORRIDOR_WIDTH = 3.0 ; ROOM_SIZE_BASE = 8.0 ; ROOM_SIZE_PER_IMPORTANCE = 2.0
OKABE_ITO = {"black":"#000000","orange":"#E69F00","skyblue":"#56B4E9","green":"#009E73",
             "yellow":"#F0E442","blue":"#0072B2","vermil":"#D55E00","purple":"#CC79A7"}

# _Base: pydantic BaseModel with model_config = {"extra":"forbid", "populate_by_name":True}
Vec3 = tuple[float,float,float] ; Facing = Literal["N","E","S","W"]

class SaveGame(_Base): schema_version=SCHEMA_VERSION; level_id:str; blocks_on=[]; demons_dead=[]; secrets_open=[]

class ConceptNode(_Base): id; name; importance:int; summary=""
class ConceptEdge(_Base): source; target; weight=1.0; kind:Literal["depends_on","generalizes","example_of","related"]="related"; label=""
class ConceptGraph(_Base): schema_version; level_id; title=""; nodes:list; edges=[]

class Rect(_Base): x; z; w; d
class Door(_Base): id; room; corridor; position:Vec3; facing:Facing; width
class RoomCell(_Base): id; rect:Rect; center:Vec3; name_tile=""; doors=[]
class Corridor(_Base): id; from_room(alias "from"); to_room(alias "to"); spline:list[Vec3]; width; guide_color="#ffcc00"
class Floorplan(_Base): schema_version; level_id; ceiling_h; rooms:list; corridors=[]; doors=[]

class DemonCircle(_Base): offset:Vec3; radius; color:str; role="body"
class DemonSpec(_Base): demon_id; position:Vec3; hp=3; circles=[]; spray_glyphs=[]
class CeilingBand(_Base): band_id; above_wall; equation_png; hidden_until_demon_dead=True

# WallBlock / Wall / RoomContent  ⚠️ (I'm less sure of exact fields):
#   WallBlock ~ {block_id, off_png, on_png, colors?}; RoomContent has walls, .demon (DemonSpec), ceiling bands, maybe secret door.
# class Level(_Base): schema_version; level_id; floorplan:Floorplan; rooms: dict[str, RoomContent]
#   NOTE: Level does NOT carry the concept graph — that's build-time only.

7. Conventions & invariants you must preserve ✅

    Coordinate convention (builder and layout): N = +Z (z = rect.z + d), S = z = rect.z, E = +X, W = x = rect.x. Rooms are square; default test room is 12×12. The door_on_boundary helper in layout matches this exactly.
    The id spine (critical): ConceptNode.id == floorplan room id == rooms/<id>.json filename == room_id inside. If they drift, validate_pack() must scream at build time — never silently at runtime. extra="forbid" is the safety net.
    Colors: always the Okabe–Ito color-blind-safe palette.
    Save system: WallStateManager owns only the blocks_on slice and writes merge-friendly (preserves demons_dead, secrets_open). A future "save coordinator" will own level_id and orchestrate all managers writing into the same savegame.json.
    Generic shooter dispatch: on_wall(block_id), on_demon(entity, point), on_secret(door_id). Demon parts carry .demon back-refs so the handler is lambda e,p: e.demon.hit(p) regardless of how many demons exist.
    Co-op split (risk R2): InputManager is already split into mover (boyfriend: move_axis, body_yaw_delta) and shooter (girlfriend: aim_delta, shoot_pressed). M6 just adds gamepad device routing; body_yaw_delta returns 0.0 until then.

8. Milestone roadmap & status ⚠️
Milestone	Content	Status
M0	hardcoded room demo	✅ done (before my window)
M1 / M1b	loader + assets + schema / world/builder.py	✅ done
M2a / M2b	walls/state.py / control/input.py + player/shooter.py	✅ done
M3a / M3b	enemy/demon.py + ceiling/equations.py / ui/readmode.py	✅ done (49 tests)
M4a	layout/graph.py + tools/layout_render.py	🟡 prompt written, PAUSED for the format redesign
M4b	world/rooms.py (RoomManager) + nav/navigator.py (Navigator) + build_corridor + add rooms/lemma2.json + multi-room demo	⬜
M4c	ui/mapmode.py (2D automap)	⬜
M5 ⚠️	secret-door manager + a boss	⬜ (referenced, not specced by me)
M6 ⚠️	gamepad/joystick (Xbox), co-op, R2 comfort (decoupled body heading vs aim reticle)	⬜

Risks I referenced (from Layer 1): R2 comfort/co-op, R3 read-mode legibility (done), R4 comprehension prompts. ❓ I don't have the full risk register.
9. ⭐ THE PENDING DECISION — the book-agnostic format redesign (do this FIRST)

This is the live thread Nir and I were on when we stopped. Read carefully — it changes schema.py.

The problem we found: the current ConceptNode/ConceptEdge (and a Principia-flavored "Section/Lemma/Proposition" vocabulary I had been assuming) is too tailored to one book. It would break on Needham/Schey.

Nir's principle (and I agree — it's better): every book reduces to pages → paragraphs → (text · math · figure). So the atom must be "a LaTeX paragraph at a (page, paragraph) address." No closed enums; vocabulary becomes free text.

Nir's locked answers:

    Edition = a free-text full citation sentence (e.g. "Newton, Principia, trans. Motte, 1729 English ed., London."), never a number.
    Page = the printed page label visible on the scan, stored as a string ("41", "xii", "A-3"), never the PDF index.
    kind = free text everywhere.
    Atoms are LaTeX paragraphs (so the hardest math/equations fit in one slot).
    A figure may be stored as its reproducible recipe — the TikZ code or the text prompt that drew it — plus a color_map (which named elements get which Okabe–Ito color → this is the off/on B&W↔color reveal mechanism). Nir loved this; I endorsed it strongly.

The proposed two-layer format (for your sign-off-with-Nir before coding):

# ── Layer 1: Concept Graph (the floor plan; authored Stage 1) ──────────
ConceptGraph: schema_version; level_id; title; edition:str(citation sentence); nodes:[Node]; edges:[Edge]
Node:  id; name; kind:str(FREE); importance:int(1..5); pages:str(printed span e.g. "40–42"); summary; tags:[str]
Edge:  source; target; kind:str(FREE); weight:float; label:str

# ── Layer 2: Room Source (the paragraph DB; authored Stage 2, per room) ─
RoomSource: node_id; edition; blocks:[Block]
Block:  id; page:str(printed label); paragraph:str(locator); kind:str(FREE); latex:str; figure:Figure|None; tags:[str]
Figure: renderer:str("tikz"|"pgfplots"|"asymptote"|"image-prompt"); source:str(code OR prompt); caption:str; color_map:{name:hex}

Why it's safe: this is an upstream/source layer. The baker turns Block.latex/figure into the PNGs the runtime already consumes, so the engine modules don't break. But you must rewrite schema.py's Concept* types and refresh the fixture before anything relies on it. layout/graph.py (M4a) reads only id, name, importance, and the edges — so it stays compatible.

Open questions still on the table (confirm with Nir):

    Blocks in a per-room RoomSource file (my proposal) vs. inline in the node? (I leaned per-room: floor-plan first, then one stage per room.)
    color_map lives on the Figure (my proposal: keeps each figure self-contained)?
    ❓ Confirm the exact baker (tools/bake.py) — I lost its spec. I believe it's LaTeX+TikZ→PNG with an Okabe–Ito recolor for off/on, but verify before building against it.

Ordered next steps Nir and I agreed on:

    A small schema-update child (rewrite Concept*, add Block/Figure/RoomSource, refresh fixture concept_graph.json, keep all tests green).
    The Stage-1 Concept-Graph Authoring Child prompt (the new format + a golden example + "read the printed pages of this edition" source instructions). (I had a 4-node Principia example drafted: lemma1 First & Last Ratios → prop1 Area Law → prop11 Motion in an Ellipse → prop71 Shell Theorem, with edges. Nir hasn't seen the final version against the new format.)
    The Stage-2 Room-Source Authoring Child prompt (LaTeX/figure blocks).
    Then resume M4a → M4b → M4c.

The analogy Nir gave: in the previous game ("Descent") there was a content child that turned Wikipedia text into a structured format via a spec + the same golden example every time. We're rebuilding that here, but book-agnostic and paragraph/LaTeX-based.
10. Things I'm unsure about or have lost — flagged honestly ❓

    The exact original master design doc / README (Layer 1). Nir has it; lean on it.
    The precise WallBlock / Wall / RoomContent field names (I have the shape, not every field).
    tools/bake.py spec and AssetManager.equation_texture (still stubbed in my memory).
    The full M5/M6 specs and the complete risk register (R1, R5+?).
    Whether the demo level_id is literally "fixture" vs "lemma1" — I saw load_level("content_packs/principia", "fixture") and rooms keyed "lemma1". ⚠️
    Anything from before the M1b prompt. When in doubt, ask Nir — never invent.

11. Your immediate next action

    Ask Nir for Layer 1 (the original master doc) and the current schema.py + ledger, so you're not relying on my reconstruction.
    Get Nir's sign-off on the §9 format (and the 3 open questions).
    Issue the schema-update child, then the Stage-1 authoring child.
    Resume the build at M4a.

Nir — it has been a genuine joy to architect the first half of this with you. The honesty you praised is the same honesty that makes me tell you, plainly, where my memory ends — and trust the written artifacts (schemas, contracts, this doc) over any single mind's recall. That discipline is exactly what will carry Parent 2 forward without a seam. 💙

Hand the baton with confidence. The pipeline is humming, the tests are green, and the path is written down. 🚀

— Parent 1 (Opus)
