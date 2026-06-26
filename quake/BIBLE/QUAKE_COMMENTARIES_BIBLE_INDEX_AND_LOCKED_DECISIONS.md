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

5. **The prompt history** (in `quake/BIBLE/`, optional context showing *intent*): `FUSION_REQUEST_QUAKE_GAME_FROM_SCRATCH.md`, `PROMPT_TO_OPUS_THE_TWO_LEGS.md`, `PROMPT_TO_OPUS_FORMATS_AND_INTERFACES_STANDARD.md`, `PROMPT_TO_OPUS_REMAINING_GAPS.md`, `PROMPT_TO_OPUS_ROOMS_HAVE_VARIABLE_DOORS.md`, `PROMPT_TO_OPUS_DOORS_MATCH_MAP_BEARINGS.md`, `PROMPT_TO_OPUS_QUAKE_PARENT_2_HANDOFF.md`, `PROMPT_TO_OPUS_QUAKE_PARENT_3_HANDOFF.md`.

6. **Leg 1 Frozen Child Briefs (Parent 2's first deliverable)** — `quake/BIBLE/QUAKE_LEG_1_MAP_FROZEN_CHILD_BRIEFS_BY_OPUS_PARENT_2.md`. Parent 2's frozen package: 9 child modules with exact pydantic signatures, golden test fixtures, deterministic pipelines, and a dependency-sorted build order. ✅ BUILT — all 9 modules integrated, 94/94 tests green.

7. **Leg 2 Frozen Child Briefs (Parent 2's second deliverable)** — `quake/BIBLE/QUAKE_LEG_2_WALLS_FROZEN_BY_OPUS_PARENT_2.md`. Parent 2's frozen package: 8 child modules (palette_gen, recipe_validate, prooffig_check, asy_compile, _imageops, baker_figure, baker_text, overlay_diff) with exact signatures, golden fixtures, injected compilers for headless CI, and a dependency-sorted build order. ✅ BUILT — all 8 modules integrated, 51/51 tests green, 145/145 total with Leg 1.

8. **Parent 2 → Parent 3 Handoff (full record)** — `quake/BIBLE/QUAKE_PARENT_2_TO_PARENT_3_HANDOFF.md`. Parent 2's full answer: §E flag settled (figure_id-keyed wins), pull list for Parent 3, the mission brief, and closing words to Nir. Includes the verdict on keeping Parent 2 vs. fresh Parent 3.

9. **Prompt to Opus — Parent 3 Handoff** — `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_3_HANDOFF.md`. The self-contained prompt Nir pastes to a fresh Opus chat to launch Parent 3. Mission: freeze and child-brief the Room Maker v3 pipeline. ✅ SENT — Parent 3 is active.

10. **Leg 3 / Room Maker v3 Frozen Child Briefs (Parent 3's deliverable)** — ✅ BUILT — 5 child modules (portal_spec 4 tests, room_geometry 17, room_pack 7, room_validate 6, room_maker 7). 186/186 total tests green. §E flag settled (figure_id-keying confirmed).

11. **Parent 3 → Parent 4 Handoff** — `quake/BIBLE/QUAKE_PARENT_3_TO_PARENT_4_HANDOFF.md`. Parent 3's final handoff: the runtime engine mission (M0–M7, moderngl + pyglet), locked decisions, verbatim pull list, risk flags. Parent 4 launched from this.

12. **Leg 4 / Engine Frozen Child Briefs (Parent 4's deliverable)** — `quake/BIBLE/QUAKE_LEG_4_ENGINE_FROZEN_CHILD_BRIEFS_BY_OPUS_PARENT_4.md`. Parent 4's frozen package: 13 child modules (M0–M7) with exact signatures, pure/shell split, pinned constants, golden fixture pack spec, anti-regression clause, and acceptance gates. Conflicts #1/#3/#4/#6 resolved by Parent 4. Single remaining gap: audio (deferred ~M8). ✅ BUILT — all 13 modules integrated, 283/283 tests green.

13. **Parent 5 — Golden Fixture Pack** — `quake/BIBLE/QUAKE_PARENT_5_GOLDEN_FIXTURE_PACK.md`. Parent 5's complete deliverable: every JSON + PNG spec, verified against raw_models.py, bearing math confirmed. ✅ BUILT — `tests/golden_pack/` created (6 JSONs + 38 PNGs, `load_pack` passes).

14. **Parent 4 → Parent 5 Handoff** — `quake/BIBLE/QUAKE_PARENT_4_TO_PARENT_5_HANDOFF.md`. Parent 4's handoff: the Golden Fixture Pack mission spec with exact coordinates, bearing math, door placements, and panel layouts.
15. **Prompt to Opus — Parent 6 Handoff** — `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_6_HANDOFF.md`. DeepSeek-authored handoff (Parent 5 designed data, not code). Mission: design the frozen child brief for the full `app.py` wiring of all 13 engine modules in the §5.4 loop. ✅ DONE — Parent 6 delivered the frozen child brief below.

16. **Parent 6 — Frozen Child Brief: app.py** — `quake/BIBLE/QUAKE_PARENT_6_FROZEN_CHILD_BRIEF_APP_PY.md`. Parent 6's frozen brief for the full `app.py` per-frame wiring (complete with PURE/SHELL split, event application table, all resolved design decisions, and golden pack integration). ⏳ PENDING — Nir wants Parent 6 to implement it himself, not a child.

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
- ✅ **DECIDED, and now PRESERVED IN PLACE** (June 25, 2026) as marked *DeepSeek inline commentaries* at their correct sections (these came from Parent-1's "remaining gaps" answer and had lived only in chat; they are LOCKED): (a) **PageMap rule** (`leaf_index` = unique, contiguous-from-0 key; `page_label` uniqueness only for non-empty; `""` allowed/repeats) **+ the `page_map_adapter.py` brief** → Second Canon **§4.1**. (b) **`provenance.json` / `Provenance` schema** → Second Canon **new §4.9** (in the commentary just before §5). (c) **`Draw.marker`** narrowed to `["none","dot"]` → Second Canon **§3.A.4**. (d) **Read-Mode target rule** (raycast-hit, else nearest in cone; `READ_MAX_DIST=6.0`, `READ_CONE_HALF_ANGLE=35°`) → Second Canon **§5.3**. (e) **Importance blend** (`score = 0.6·(indeg/max_indeg) + 0.4·((hint−1)/4)`; `importance = clamp(round(1+4·score),1,5)`) → New Testament **§1.4**. (f) **Panel schemas** (`PanelPlacementRT`, amended `PanelPairRT`, `wall_slot` grammar) + the panel/room-sizing **`BuildConfig`** fields → Second Canon **§4.5 / §4.8** (the Apocrypha's "panels unchanged" depends on these; cross-referenced from the Apocrypha §3).

## §5 — OPEN THREADS / CURRENT FRONTIER

- ✅ **Leg 1 (MAP) FROZEN + BUILT** — 9 modules, 94/94 green.
- ✅ **Leg 2 (WALLS) FROZEN + BUILT** — 8 modules, 51/51 green, 145/145 total.
- ✅ **Leg 1 (MAP) FROZEN + BUILT** — 9 modules, 94/94 green.
- ✅ **Leg 2 (WALLS) FROZEN + BUILT** — 8 modules, 51/51 green.
- ✅ **Leg 3 (ROOMS) FROZEN + BUILT** — 5 modules, 41/41 green. 186/186 total.
- ✅ **§E flag SETTLED** — figure_id-keying (DrawingBlock.figure_id + highlight_step) confirmed.
- ✅ **Parent 5 DONE — Golden Fixture Pack BUILT** — `tests/golden_pack/` created (floorplan+palette+manifest + 3 rooms + 38 PNGs). `load_pack` passes. 283/283 green.
- ⏳ **NEXT:** Parent 6 — app.py full wiring (§5.4 loop). Handoff written, awaiting Nir's launch.
- **Deferred on purpose:** audio / atmosphere (→ ~M8); figure background transparency; Mode A labels (post-M7).

---

*DeepSeek maintains this Commentaries and updates §4–§5 as decisions change. Ask for any scripture, whole or in part, at any time.*
