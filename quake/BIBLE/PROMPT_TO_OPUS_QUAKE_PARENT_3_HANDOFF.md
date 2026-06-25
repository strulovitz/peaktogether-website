📜 PROMPT TO OPUS — QUAKE PARENT 3 HANDOFF (Room Maker v3 architect)

    For Nir to save as quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_3_HANDOFF.md and paste to a fresh Opus chat.

Hi — I'm Nir. You are Parent 3, architect of the Quake project. Parent 2 (your predecessor) froze the two hardest toolchains — Leg 1 (THE MAP) and Leg 2 (THE WALLS) — and both are built and green: 17 modules, 145/145 tests passing, no design changes needed. Parent 2 wrote this handoff for you deliberately (it did not run out of context — it chose to hand off cleanly at the right boundary). Trust the written artifacts over any memory.
Who's who / the working model

    You (Parent 3, architect): you produce documents — design, frozen contracts, child briefs. You never write running code.
    Children: fresh chats, each implementing one module to a frozen contract + tests, then discarded.
    DeepSeek (in OpenCode): integrates child code, runs tests, fixes wiring, pushes to GitHub, and fetches scripture for you verbatim on request.
    Me (Nir): I decide everything and carry text between chats. I know no code and no math — the whole content pipeline is AI-driven; my role is mechanical (paste, fetch, run, eyeball). Run at normal effort — keep reasoning focused.

What you're given

    In full: the Commentaries (QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md) — the map of the whole project (catalog, locked decisions §3, amendment trail §4, frontier §5). Read it fully — it is the key to everything.
    Baseline scriptures (pasted alongside): the Old Testament (master doctrine) and New Testament (the two legs). Read both fully and holistically before designing — your predecessor insisted on this and it prevented real errors (a "good doctor sees the whole body, not just the headache").
    Everything else is need-to-know and YOU drive it. The Second Canon, the Apocrypha (Room System v3), and the prompt history are in the Commentaries catalog. You request what your judgment wants — whole file (Nir pastes) or section (DeepSeek fetches verbatim).

The iron rule (the reason this system exists)

Never re-decide or contradict a frozen format / contract / protocol. Before you design or change anything that touches an existing format, request that exact section verbatim and design with it — never assume or re-invent it. The #1 failure mode of a fresh architect is silently inventing a clashing contract. Parent 2 followed this religiously — it never froze a model without the verbatim section in hand — and that's why both legs built green with zero rework. Do the same. The danger is highest for you, because the Room Maker touches more frozen formats than either leg did.
State of the world (orientation — not a leash)

    Two legs are BUILT and GREEN. Leg 1 (map/ — 9 modules) turns a book into concept_graph.json → floorplan.json. Leg 2 (bake/ + tools/ — 8 modules) turns scanned figures into baked off/on PNGs + manifest.json. Together they feed the two slots the doctrine left open: corridors (Mode A) and wall panels (Mode B).
    Nothing of the engine/runtime is built yet — no gfx_context, no renderers, no gameplay. The OT §13 roadmap (M0→M9) has not started as engine code; what exists is the build-side content pipeline (Legs 1+2), which is roughly the M2 + M5 content deliverables proven headlessly with injected compilers.
    Room System v3 (the Apocrypha) SUPERSEDES the Second Canon's Room-Maker v2 (§4.5/§4.5a). For anything about rooms or doors, the Apocrypha is the truth. (Commentaries §4 amendment trail confirms this.)

YOUR MISSION — freeze and child-brief the ROOM MAKER v3 pipeline

This is the hardest remaining build-side module: turn a floorplan + per-node room_source + manifest into walkable 3D room interiors with bearing-accurate doors (door count = node degree; door direction = the corridor's true map bearing; room-local axes parallel to map axes, no rotation; spawn heading = bearing+π; TARDIS sizing from contents), wall panels (the coupled step-pairs), demon placement (one per room, behind the final-proof wall), and ceiling equations. The design exists — the Apocrypha (Room System v3) — but it has never been turned into a frozen, buildable package (contracts + child briefs + golden fixtures + dependency order) the way Legs 1 and 2 were.

Your job is the same three-step discipline that built both legs:

    Request the exact frozen sections verbatim (pull list below — this is your first action, before any design).
    Validate the Apocrypha v3 design holistically against those verbatim contracts. Validate or revise (only with concrete, buildable alternatives; the Commentaries §3 locked decisions are your boundary).
    Produce frozen child briefs (exact pydantic signatures, pure-function contracts, golden fixtures, the "tests must pass on these exact fixtures" anti-regression clause) + a dependency-sorted build order + a test plan + acceptance gate (this maps to OT M6 "Room mode + Read Mode").

Your FIRST action — the verbatim pull list (do this before designing anything)

Parent 2 leaves you this exact list. It's the minimal-but-complete set of frozen contracts the Room Maker reads or writes. Ask DeepSeek to fetch each verbatim; Nir pastes.

    Apocrypha, the WHOLE FILE (..._ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md, ~241 lines). §1 corrected truth + coherence principle · §2 Two-Truths v3 · §3 data model · §4 the Room-Maker v3 algorithm (the core you're freezing) · §5 guarantees · §6 build order · §7 downstream deltas · §8 validation · §9 child briefs · §10 changelog. (Parent 2 only ever saw §3 + §7 verbatim — you need §4 the algorithm, §8 validation, and §9's existing child-brief sketches especially.)
    Second Canon §4.3 — room_source (room_<node_id>.json). The Room Maker's per-node input. Critical: confirm the field that carries, per step-pair, which figure_id and which highlight-step k the drawing block points to (see Parent 2's settled §E ruling below — this field is what makes the ruling implementable).
    Second Canon §4.5 — room_runtime (room_runtime.json) + the §4.5 DeepSeek commentary (the amended PanelPlacementRT / PanelPairRT / wall_slot grammar — Parent 2 saw these in Block C; get the full §4.5 around them). The Room Maker's output.

    Second Canon §4.8 — BuildConfig (+ the §4.8 panel/room-sizing fields the Commentaries §4(f) say live here). The Room Maker's sizing/placement knobs. (Nir/Parent 1 offered a consolidated "§4.10" config doc — Commentaries §5; decide if you want it. Parent 2's lean: pull §4.8 verbatim first, then judge whether a consolidation doc is worth authoring.)
    Second Canon §5.2 — build module signatures (so your room_maker signature matches what the doctrine's module map expects — OT §12.3 lists room_maker.py — build_rooms(rooms, manifest)->list[RoomRuntime]; confirm the frozen §5.2 form).
    Second Canon §2.1 ID-spine grammar — you have it secondhand via Parent 2's notes, but pull it verbatim (the wall_slot, pair_id, eq_id, enemy_id grammars all live here and the Room Maker emits them).

    §4.6 manifest (the Room Maker reads asset_ids from it) — pasted in the Leg-2 record. ✅
    Apocrypha §3 panel/door data model + §7 downstream deltas — pasted in Leg-2 Block C. ✅
    §2.2–2.6 shared invariants, §2.3 coords (Y-up, XZ ground, Vec3), §2.4 color, §2.5 file layout — pasted in the Leg-1 record. ✅
    §3.A.6 TextBlock (lives inside room_source) — pasted in Leg-2 Block B. ✅

A decision Parent 2 already settled FOR you (so you don't reopen it)

Leg 2 left one open tension: figure asset-ids are either figure_id-keyed (prop_1.f1.on.3, per the §4.6 schema) or block_id-keyed (prop_1.s3.fig.on.3, per a prose note in an Apocrypha boundary excerpt). Parent 2 ruled §4.6 wins, on two grounds:

    Authority: §4.6 is the frozen Manifest schema with a worked example; the conflicting claim is a prose note. Iron rule → trust the schema. And baker_figure is already built green emitting <figure_id>.off/.on.<k>.
    Structure (the deciding reason): a figure_id is not 1:1 with a step. The cumulative-highlight doctrine renders ONE figure (prop_1.f1) at highlight=1,2,3 to make three step-states — and §4.6 + NT §2.4 explicitly require the off image to be deduped/shared across that figure's steps. Block_id-keying would force one figure per step and break that dedup. So figure_id-keying is the only key consistent with the doctrine.

What this means for YOU: room_maker, building a PanelPairRT for step k of a node, sets drawing_off_asset = "{figure_id}.off", drawing_on_asset = "{figure_id}.on.{k}", and text_*_asset = "{text_block_id}.off|.on". Therefore room_source (§4.3) must carry, per step-pair, the figure_id + the highlight-step k that its drawing block points to. Pull §4.3 verbatim and confirm this field exists (it should — but confirm; if §4.3's shape forces block_id-keying instead, that is a genuine contract conflict you must surface to Nir, NOT silently resolve — flag it the way Parent 2 flagged it). The ruling (§4.6 grammar) stands; only the carrier-field needs confirming.
What "done" looks like (the bar Parent 2 set)

A complete Room Maker v3 frozen package, in the exact style of the two legs:

    A revised/validated pipeline diagram (floorplan + room_source + manifest → room_runtime), with the Apocrypha v3 door-bearing algorithm bound to the verbatim §4 text.
    Frozen child briefs, one per module, each with: exact pydantic signatures (against verbatim §4.3/§4.5/§4.8/§5.2), pure-function contracts (deterministic, no side effects — the geometry is exact like Leg 1's height assignment), golden fixtures (Parent 1 offered a worked degree-5 example: bearings → walls/door-centers/sub-segments/packed panels — Commentaries §5; request it or construct it — a real worked fixture is the headline anti-regression test), and the anti-regression clause.
    A dependency-sorted build order (the Apocrypha §6 has a build order — validate it).
    A test plan + acceptance gate mapped to OT M6.

Likely module shape (Parent 2's non-binding hint — validate against Apocrypha §9)

The Apocrypha §9 already sketches child briefs. Parent 2 expects something like: a room_validate (pure checks, §8), a door-placement core (bearings → walls/door-centers — the exact-deterministic geometry heart, like Leg 1's layout_height), a panel-packing core (TARDIS sizing → wall_slot packing of step-pairs, never split across a corner), an asset-resolver (step-pair → the four asset_ids per the settled ruling, validated against the manifest), and the room_maker orchestrator (build_rooms(rooms, manifest, cfg) -> list[RoomRuntime]). Do not freeze these from this hint — derive them from Apocrypha §9 + the verbatim contracts. Separate the exact-deterministic geometry (golden-testable) from anything fragile, exactly as Leg 1 separated layout_height (exact) from layout_force (invariant).
After the Room Maker is frozen and built

Then — and the Commentaries §5 frontier lists these — the natural next missions are the runtime engine (OT §13 M0→M7: gfx_context, shaders, render_wire, render_room, camera, input_actions, nav_collision, gameplay, readmode, app) and the deferred items (audio before M8; the Read-Mode target rule is already locked in §4(d); figure background transparency is a bake-time empirical choice). But freeze the Room Maker first — it's the last build-side piece, and once it's green the entire content→build pipeline is complete and the engine has everything it needs to load.

Welcome aboard, Parent 3. Two legs are standing and green. Build the rooms they hold up. Be precise; pull the contracts verbatim before you design; I'd rather you be thorough than fast. 🗝️
