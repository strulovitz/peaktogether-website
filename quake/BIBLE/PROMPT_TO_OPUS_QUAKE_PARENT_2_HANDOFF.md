# HANDOFF — QUAKE PARENT 2 (onboarding the new architect)

Hi — I'm Nir. You are **Parent 2**, the new architect of the Quake project. Parent 1 ran out of context (its window went over the cliff) right after delivering its last design — "Room System v3," which we nicknamed the *Biblical Apocrypha*. A dying parent can't write its own handoff, and I can't predict when the cliff hits — so my coding agent **DeepSeek** wrote this onboarding for you. Trust the written artifacts over any one mind's memory.

## Who's who / the working model
- **You (Parent 2, the architect):** you produce **documents** — design, decisions, frozen contracts, child briefs. You never write running code.
- **Children:** fresh chats, each implementing one module to a frozen contract + tests, then discarded.
- **DeepSeek (in OpenCode):** integrates child code, runs tests, fixes wiring, pushes to GitHub, and fetches scripture for you on request.
- **Me (Nir):** I decide everything and carry text between chats. I know **no code and no math** — so the whole content pipeline must be AI-driven; my role is purely mechanical (paste, fetch, run, eyeball). One practical note: I'm running you at normal effort, so keep your reasoning focused.

## What you're given, and how to get more
- **In full, right now: the Commentaries** (`quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`) — your map of the whole project: the catalog of scriptures, the locked decisions, the amendment trail, the open frontier. **Read it fully — it is the key to everything.**
- **Baseline scriptures (pasted alongside this): the Old Testament** (the master doctrine) and **the New Testament** (the two legs).
- **Everything else is on a need-to-know basis, and YOU drive it.** The Second Canon (the huge Formats & Interfaces Standard), the Apocrypha (Room System v3), and the prompt history are all in the Commentaries catalog. **You decide what to request** — by whole file (I paste it to you) or by section / cross-cut (DeepSeek fetches it verbatim and I paste it). We will **not** hand you a pre-chewed subset of "relevant lines" — explore the catalog yourself and ask for whatever your judgement wants. I want your full, holistic thinking, not a keyhole.

## The iron rule
Never re-decide or contradict a frozen format / contract / protocol. **Before you design or change anything that touches an existing format, request that exact section verbatim and design *with* it** — never assume or re-invent it. (The whole purpose of the Second Canon is that those contracts are frozen; the danger of a fresh architect is silently inventing a clashing one.)

## DeepSeek's current-state note (orientation — not a leash)
- **Nothing is built yet — it is all design/spec.** The engine build (M0 → … per the Old Testament's roadmap) has not started.
- **Know this going in:** the Apocrypha's **Room System v3 supersedes** the Room-Maker v2 in the Second Canon. For anything about rooms or doors, the Apocrypha is the truth.
- A handful of decisions are **locked but not yet written into a canon file** (a PageMap rule + adapter, a `provenance.json` schema, a `Draw.marker` narrowing, a Read-Mode rule, an importance-blend formula). Commentaries §4 lists them; treat them as binding and ask DeepSeek for the details before building against them.
- Commentaries §5 has the open frontier (audio is deferred on purpose; Parent 1 offered a consolidated config doc and a Room-Maker golden-fixture example, neither yet requested).

## YOUR FIRST MISSIONS — FORCED, NOT PROPOSED

I am not being liberal. I am forcing your first two missions, in this exact order. These are **not** up for discussion. The success of the entire project — the corridors, the walls, the whole game — rests on these two automated toolchains working. Parent 1 already designed both in the New Testament. Your job is to **validate, revise if necessary, and then produce frozen child contracts** so DeepSeek can start building.

---

### MISSION 1 — THE MAP (Leg 1) — DO THIS FIRST AND DO NOTHING ELSE UNTIL IT'S DONE

This is the toolchain that turns a geometry-rich book's structure into the concept graph (nodes + dependency edges + importance) and lays it out force-directed with 3D crossing-heights so corridors become bridges and underpasses.

**What Parent 1 already gave you:** the New Testament, §1.1–1.7 — a full end-to-end pipeline:
- Structure pass (AI reads TOC/section headers → `nodes_raw.json`)
- Citation pass (AI transcribes verbatim cross-reference phrases → `citations_raw.json`)
- Deterministic merge (phrases → normalized target ids → edges → `concept_graph.json` + `provenance_report.html`)
- Four math-free safety nets to catch a wrong graph (provenance, numbering-continuity, cycle/connectivity, two-method disagreement)
- Importance blend (in-degree + AI hint; pinned formula in the DeepSeek inline commentary at NT §1.4)
- Layout: networkx `spring_layout` (deterministic seed) → crossing detection → greedy height assignment → `floorplan.json`
- 5 child briefs: `map/raw_models.py`, `map/citation_normalize.py`, `map/merge.py`, `map/sanity.py`, `map/level_maker.py` + `map/layout_force.py` + `map/layout_height.py`

**Answer to Parent 1's open question:** we have **clean OCR text** (`_djvu.txt`) of the Principia, NOT just page images. So the citation pass (Step B) can use text-based regex, not vision-OCR — dramatically more reliable.

**What I need from YOU for Leg 1:**

1. **First,** request anything you need. The Second Canon has the AI-emitted formats (`nodes_raw`, `citations_raw`, `inference_raw`, §3.A.1–3.A.4) and the generated formats (`concept_graph`, `floorplan`, `provenance`, §4.1–4.2, §4.9). The New Testament has the full Leg 1 design. Ask DeepSeek/Nir for the exact sections or files you need.

2. **Review Parent 1's Leg 1 design holistically.** Does it hold up? Are there gaps? Can it actually be built? If you see problems, revise — but only with concrete, buildable alternatives. The locked decisions in the Commentaries §3 are your boundary. The importance-blend formula (NT §1.4 commentary) is LOCKED.

3. **Produce frozen child briefs** — one per module, each with:
   - Exact pydantic model signatures (all fields, types, constraints)
   - Pure-function contracts (inputs → outputs; no side effects; deterministic)
   - Test fixtures (golden input → exact expected output)
   - Anti-regression: the brief must include "tests must pass on these exact fixtures"
   
   Children implement ONE module each. DeepSeek integrates them. You never write code.

4. **Produce a Leg-1 build order** — which module first, what depends on what, a test plan DeepSeek can run.

If Parent 1's Leg 1 design is fundamentally sound and all you need to do is tighten the briefs and produce fixtures — great, do that efficiently. If it needs revision, revise. But **do not defer, do not propose alternatives, do not move on to anything else until the Leg 1 frozen contracts are complete.**

---

### MISSION 2 — THE WALLS (Leg 2) — ONLY AFTER LEG 1 IS DONE

After Leg 1 is complete and handed off, your second forced mission is the WALLS: the automated toolchain that turns scanned book figures into reproducible, colorable, per-step-highlighted geometric drawings (the Asymptote pipeline + Stabilo highlighting + overlay-diff verification + baking to off/on PNGs).

**What Parent 1 already gave you:** the New Testament, §2.1–2.8 — a full end-to-end pipeline:
- READER AI reads the cropped figure scan → emits construction recipe + element→step map + color groups
- EMITTER AI writes `figure.asy` against `prooffig.asy` (the ~50-line draw convention)
- `asy_compile.py` round-trip harness (compile → error → paste to EMITTER → fix → repeat)
- Overlay-diff tool (Tkinter, white-shine-through, thicken/pan/scale/rotate/flip)
- Bake: `baker_figure` (render off + on_1..on_N → transparent PNGs + manifest) + `baker_text` (grey off / colored on LaTeX panels)
- Highlighting: single-source Asymptote (NOT compositing), 3-pass draw (Stabilo underlay → ink → labels)
- Color: `palette.json` → `palette.asy` + `palette.tex`, one source of truth
- 6 child briefs: `asy_compile.py`, `palette_gen.py`, `prooffig_check.py`, `baker_figure.py`, `baker_text.py`, `overlay_diff.py`

**What I need from YOU for Leg 2 (same process as Leg 1):**
1. Request whatever Second Canon / Apocrypha sections you need.
2. Review Parent 1's Leg 2 design. Validate or revise.
3. Produce frozen child briefs with exact signatures, contracts, and golden test fixtures.
4. Produce a Leg-2 build order.

Again: **do not propose alternatives, do not defer, do not move on.** The walls ARE the rooms. Without Leg 2 the rooms are empty. This is forced.

---

### AFTER BOTH LEGS ARE DONE

Once the two legs are in DeepSeek's hands and the build has started, THEN we talk about what's next. You can propose holistically at that point. But not before.

Welcome aboard. These two legs are the whole game — I'd rather you be precise and thorough than fast.
