# QUAKE BIBLE — THE COMMENTARIES (catalog · locked decisions · amendment trail)

> Nicknamed **"the Commentaries"** (after Calvin's Commentaries on Scripture) — the small, maintained guide to the much larger Quake BIBLE. Maintained by **DeepSeek**; current as of **June 25, 2026**. This is the ONE document every new parent receives in full. It is **not** the scripture — it is the **map** of it: what exists, what is frozen, what has been amended. The scriptures themselves are large; you read only the parts you decide you need.

---

## §0 — HOW TO USE THIS (read first)

- You (the architect/parent) get **this Commentaries in full**, plus the two baseline scriptures: the **Old Testament** and the **New Testament**.
- **Everything else is on a need-to-know basis.** YOU decide what to pull from the catalog below — by whole file or by section. We will **not** spoon-feed you a pre-filtered subset; explore the catalog yourself and request whatever your judgement says you need. We want your *full, holistic* thinking, not a keyhole view.
- **How to get more:** ask (via Nir). **Whole files** → Nir pastes them to you. **Snippets / specific sections / cross-cuts** → DeepSeek fetches them verbatim and Nir pastes them.
- This Bible is **large and always evolving** (we change things constantly). The scriptures are **never rewritten**; instead this Commentaries records the **current truth and the amendment trail** (§4). When in doubt about what's current, trust §3–§4 here, then request the exact scripture section.

## §1 — THE IRON RULES (never violated)

1. **Working model.** The architect (you) writes **documents**: design, decisions, frozen contracts, child briefs — **never running code.** Fresh "child" chats implement one module each to a frozen contract + tests. **DeepSeek** integrates, tests, pushes to git. **Nir** decides everything and carries text between chats; Nir knows **no code and no math**.
2. **Never re-decide a frozen contract.** Before designing or changing anything that touches an existing format / protocol / contract, **request that exact section verbatim** and design with it — never assume or re-invent it. Silent contradiction of a pinned format is the #1 failure mode this whole system exists to prevent.
3. **Honesty.** Never invent facts. Mark genuine gaps as gaps. Ask only the few load-bearing questions you truly need. Refuse to assert external-library API names from memory (Asymptote, etc.) — define our own conventions fully and let the compile loop confirm the externals.
4. **Formatting for transfer.** Anything Nir will copy-paste must be **prose or fenced code blocks, never Markdown tables** — tables lose their cell contents on copy.
5. **Nir's hard constraint (governs the whole content pipeline).** Nir cannot code or do math. ALL *understanding* (reading scans, the math, the figures, the dependencies) is done by **AI in OpenRouter**. Nir's role is purely **mechanical**: fetch scans, run scripts, copy-paste, install tools, and eyeball whether two pictures match. Never design anything that needs Nir to understand a proof or hand-draw a figure.

## §2 — THE SCRIPTURE CATALOG (what to ask for)

**Baseline (you always have these):**

1. **Old Testament** — `quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md` (~459 lines). Fusion's master design doctrine, *"Two Minds, One Proof."* Sections: §0 one-breath pitch · §1 the spine (geometry-rich books ONLY) · §2 hard invariants · §3 the two render modes · §4 the two truths · §5 the two machines · §6 the geometry pipeline · §7 the baker · §8 3D layout/crossings/guide-lines/movement · §9 book-agnostic data format · §10 co-op & comfort · §11 technology stack · §12 architecture for the LLM assembly line · §13 milestone roadmap · §14 packaging · §15 risk section · §16 collected gaps. ⚠️ Some parts amended — see §4.

2. **New Testament** — `quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md` (~385 lines). Opus's design of the two genuinely hard "legs." LEG 1 — THE MAP: §1.1 pipeline · 1.2 your mechanical role · 1.3 catching a wrong graph (4 safety nets) · 1.4 importance · 1.5 layout + 3D heights · 1.6 data emitted · 1.7 child briefs. LEG 2 — THE WALLS: §2.1 highlighting decision · 2.2 Asymptote pipeline · 2.3 the overlay-diff tool · 2.4 baking · 2.5 Asymptote-fluency risk · 2.6 color · 2.7 conics & ultimate-ratio figures · 2.8 child briefs. Plus the handoff diagram and the one load-bearing question (text vs image — answered: we have clean text).

**On-demand reference (request by file or section):**

3. **Second Canon** — `quake/BIBLE/QUAKE_SECOND_CANON_FORMATS_AND_INTERFACES_BY_OPUS.md` (~1300 lines — the big one, a *parent-killer* if read whole; ask for the section you need). The Formats & Interfaces Standard. §1 data-flow map · §2 shared invariants (2.1 ID-spine grammar · 2.2 schema_version · 2.3 coordinates/units · 2.4 color rules · 2.5 file/dir layout · 2.6 correctness rule) · §3 AI-emitted formats (3.A.1 nodes_raw · 3.A.2 citations_raw · 3.A.3 inference_raw · 3.A.4 **the recipe** · 3.A.5 figure.asy + `prooffig.asy` + the Op→Asymptote list · 3.A.6 text block · 3.A.7 palette) · §4 generated data formats (4.1 page_map · 4.2 concept_graph · 4.3 room_source · 4.4 floorplan · 4.5 room_runtime · 4.6 manifest · 4.7 savegame · 4.8 pack/build_config) · §5 module interfaces (5.1 runtime contracts/Actions/Events · 5.2 build module signatures · 5.3 runtime module signatures · 5.4 per-frame wiring).

4. **Biblical Apocrypha** — `quake/BIBLE/QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md` (~241 lines). Room System v3, bearing-accurate doors. **SUPERSEDES the Room-Maker v2 / door material in the Second Canon (§4.5, §4.5a).** §1 corrected truth + coherence principle · §2 Two-Truths v3 · §3 data model (IncidentEdge, RoomPortalSpec, DoorRT, RoomRuntime, ModeSwitch) · §4 Room-Maker v3 algorithm · §5 guarantees · §6 build order · §7 downstream deltas · §8 validation · §9 child briefs · §10 changelog.

5. **The prompt history** (in `quake/BIBLE/`, optional context showing *intent*): `FUSION_REQUEST_QUAKE_GAME_FROM_SCRATCH.md`, `PROMPT_TO_OPUS_THE_TWO_LEGS.md`, `PROMPT_TO_OPUS_FORMATS_AND_INTERFACES_STANDARD.md`, `PROMPT_TO_OPUS_REMAINING_GAPS.md`, `PROMPT_TO_OPUS_ROOMS_HAVE_VARIABLE_DOORS.md`, `PROMPT_TO_OPUS_DOORS_MATCH_MAP_BEARINGS.md`.

## §3 — LOCKED DECISIONS (the frozen spine — do not re-decide)

- **Scope:** geometry-rich books ONLY (proofs carried by figures). First content pack = **Newton's _Principia_** (1846 Andrew Motte English translation; we have a clean `_djvu.txt` + per-page images + a leaf→printed-page JSON).
- **True 3D, Quake-style.** Force-directed layout → corridor crossings become **bridges/underpasses (a feature)**.
- **Two render modes**, switched at the door: (A) transparent **wireframe corridor** graph (depth-tested, no blend, distance-dimming white→grey, ~3 Half-Life floor guide-lines, pure transit) and (B) solid **room** (panels, demon, ceiling equations).
- **Two truths:** MAP truth (force-directed graph) vs **TARDIS room** (size from contents, not the map). **Two machines:** LEVEL MAKER / ROOM MAKER. **Three worlds:** CONTENT / BUILD / RUNTIME — runtime loads only baked JSON+PNG; never sees LaTeX, an LLM, or the book.
- **Geometry tool = Asymptote ONLY** (no homemade kernel). **Verification = a human overlay-diff tool** (white-back/black-front shine-through; pan/scale/rotate/thicken/flip). **Highlighting = whole figure, per-step Stabilo** (off = grey full figure; on_k = step k highlighted), baked in advance, done in Asymptote via `prooffig.asy` + a `highlight=k` parameter.
- **Correctness standard = FIDELITY TO THE PRINTED PAGE** (never "mathematical truth"; Nir cannot and need not verify math).
- **Importance 1–5** → room size **and** map color.
- **Co-op is core:** MOVER owns the body + heading; SHOOTER owns a free reticle (never rotates the camera); decoupled critically-damped camera. **God-mode** (cannot die, infinite ammo). **One enemy per room**, hidden behind the **final-proof wall** (shoot it once lit → it opens → demon emerges). **No level boss.**
- **Tech stack:** all-Python, Windows-first, custom real-time 3D with **direct pipeline control** — `moderngl` + `pyglet` + NumPy + Pillow + pydantic v2 + networkx + (build-only) matplotlib + Asymptote + Tectonic + PyInstaller. **NEVER** a hide-the-pipeline engine (no Unity/Unreal/Godot/Ursina/Panda3D).
- **ID spine:** concept-node id == floorplan room id == room-source filename stem == runtime room id. Every JSON: `schema_version "1.0"`, pydantic `extra="forbid"`.
- **Book-agnostic data format:** pages → paragraphs → (text · math · figure). `edition` = free-text citation; `page` = printed-label string; `kind` = free text; atoms = LaTeX paragraphs; figures = a construction recipe + color groups.
- **Color:** all hex lives in `palette.json`; content references **group names** only; the same group is the same color in figure and prose.
- **Room System v3 (Apocrypha):** door **count** = node degree; door **direction** = the corridor's true map bearing; **room-local axes are parallel to the map axes** (global compass, no rotation); spawn heading = bearing+π (no snap on entry); room **size** stays TARDIS. NOT teleportation.

## §4 — AMENDMENT / SUPERSESSION TRAIL (so you don't act on stale text)

- **Room-Maker v2 → v3.** The Second Canon's §4.5/§4.5a Room-Maker (single South `EntranceRT`) is **superseded** by the **Apocrypha** (variable, bearing-accurate doors). Use the Apocrypha for anything about rooms/doors.
- **Color model refined.** The Old Testament's per-figure `color_map` (hex per figure) is replaced by: **group names ARE the palette keys** (Second Canon §2.4).
- **Geometry approach changed.** The Old Testament §6 proposed "construction-not-coordinates + build an in-house geometry kernel." That homemade-kernel idea is **dropped** — it's **Asymptote only** (New Testament / Apocrypha). (The *construction-not-coordinates principle* survives, but via Asymptote, not a custom kernel.)
- **Op→Asymptote mapping restored.** Second Canon §3.A.5's mapping (originally lost as a blank table) is now present as a **list**.
- ⚠️ **DECIDED but NOT YET written into a canon file** (these live in the Parent-1 "remaining gaps" answer; treat as locked, request formalization before building against them): (a) **PageMap rule** — `leaf_index` is the unique, contiguous-from-0 key; `page_label` uniqueness applies only to non-empty labels; empty `""` allowed/repeats; + a `page_map_adapter.py` child brief. (b) **`provenance.json` / `Provenance` schema** (new §4.9). (c) **`Draw.marker`** narrowed to `["none","dot"]` (dropped `"tick"`). (d) **Read-Mode target rule:** raycast-hit panel, else nearest within a cone; `READ_MAX_DIST=6.0`, `READ_CONE_HALF_ANGLE=35°`. (e) **Importance blend:** `score = 0.6·(indeg/max_indeg) + 0.4·((hint−1)/4)`; `importance = clamp(round(1+4·score),1,5)`. (f) assorted **BuildConfig** additions.

## §5 — OPEN THREADS / CURRENT FRONTIER (nothing is built yet — design only)

- **No code exists yet.** Everything to date is design/spec. The build (engine M0 → … per the Old Testament §13 roadmap) has not started.
- **Deferred on purpose (not gaps):** audio / atmosphere (→ ~M8); figure background transparency (a bake-time empirical choice, both paths specified).
- **Offered by Parent 1, not yet requested:** a consolidated `BuildConfig` + runtime-config canonical file (a single "§4.10"); and a worked degree-5 golden-fixture example for the Room Maker (bearings → walls/door-centers/sub-segments/packed panels).
- **The unformalized amendments** in §4 still need folding into the canon (or a clean "amendments" doc) at some point.

---

*DeepSeek maintains this Commentaries and updates §4–§5 as decisions change. Ask for any scripture, whole or in part, at any time.*
