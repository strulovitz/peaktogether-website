# REQUEST TO FUSION — Master Design Document for a Quake-style Educational 3D Game (fresh start)

Hi! I'm Nir. I'm building an open-source, free-forever educational game platform for couples to learn together ("two minds at a time"). I need you to design — from a clean sheet — the complete **Master Design Document** for a new game. This document will be the top-layer "bible" I hand to every future architect/AI chat, so make every decision for me, explain the reasoning where it matters, and be honest about anything you are unsure of (mark gaps as gaps — never invent facts).

Please produce a single, comprehensive Master Design Document covering everything below, plus anything important I've missed. Where a decision is still open, propose 2–3 concrete options and **recommend one**.

---

## 0. WHAT THIS GAME IS — in one breath

A first-person desktop game (Python, Windows-first) that turns a **book of knowledge into a walkable 3D dungeon of ideas**. The player physically walks the book's **concept graph**: each idea is a **room**, each logical dependency between ideas is a **corridor**, and the proof/derivation steps are **panels on the room's walls**. You "read" a panel by **shooting it** (it flips from grayscale "off" to colored "on"). A harmless **demon** guards each room; defeating it reveals a **blood-red equation on the ceiling**. A **QED door** (the ∎ tombstone) leads to a boss that completes the room. Clear every room → the level (the book section) is mastered.

The only difficulty is **understanding the mathematics**. **God mode always** — no death, no damage, infinite ammo. Shooting is a *learning verb*, not combat. **Educational quality > graphics fidelity.**

**The engine is generic.** The book is a swappable *content pack*. The **first content pack is Newton's _Principia_ (Philosophiæ Naturalis Principia Mathematica)** — design around it as the concrete grounding example, but keep the engine book-agnostic.

---

## 1. THE NON-NEGOTIABLE PIVOT — this must be true 3D (Quake-style), NOT a flat/2.5D world

This is the single most important requirement, and the reason for the whole technology choice. Please honor it absolutely and design everything around it.

**The problem:** the dungeon's layout comes from a **force-directed graph drawing** (spring/Fruchterman–Reingold layout) of the book's real concept graph — because that produces the organic, faithful shape of the knowledge. But force-directed layouts of real graphs **almost always produce edges (corridors) that cross each other.** In a flat single-floor world you'd be forced to *reroute or forbid crossings*, which distorts the true structure and looks wrong.

**The solution = real 3D, like Quake:** corridors are placed at **different heights** so that where two corridors cross on the 2D plan, in the game one passes **over** the other as a **bridge / underpass**. **Crossings are a FEATURE, not a problem.** Because the world is genuinely 3D (areas above areas, bridges, underpasses), the map can stay faithful to the real, organic, crossing-rich structure of the knowledge.

**Therefore:**
- This is **not** a simple/standard flat shooter. Do **not** assume one ceiling height, no bridges, no multi-level geometry.
- The world has **vertical separation**: multiple heights, bridges, underpasses, ramps — true 3D navigation.
- The layout algorithm must lay the graph out and then **assign corridor heights** so crossings resolve cleanly as over/under passes. Please specify this algorithm (deterministic by seed).

---

## 2. THE TWO RENDER MODES (switched at the door)

The game has exactly **two visual modes**, and you switch between them by passing through a room's **door**:

### MODE A — CORRIDOR / WIREFRAME GRAPH MODE (transit between rooms)
The player literally **walks the concept graph as a live 3D map**. This mode has a very specific custom look that I care about a lot:
- **Transparent wireframe only.** The corridors and graph are drawn as see-through wireframe. This is deliberately a "discount" minimalist look — **do not upgrade corridors to shaded/solid polygons.**
- **Depth-tested, NO alpha blending.** Near geometry occludes far geometry; correct Z-order; the corridor you're standing in must never be visually obstructed by a distant one. Close things draw on top of far things.
- **Distance dimming.** The section you're in is **pure white**; farther sections fade progressively toward **dark grey — never pure black, always still dimly visible** (so the whole graph is perceptible around/above/below you without being a blinding white blur).
- **Crossings visible in 3D.** Because the wireframe is see-through, the player perceives being above or below other routes (bridges/underpasses). Embrace this.
- **Floor guide-lines (Half-Life style).** On the floor, **about 3 colored lines only** — for the **nearest and most important destination rooms** (NOT one line per room; 20 rooms must not mean 20 lines). Each line has **arrowheads** along it indicating direction and a sense of near/far ("which way to follow this"). These lines also provide a **felt floor**, which fights the vertigo / fear-of-falling that a transparent wireframe over open 3D space would otherwise cause. Please specify the rule for *which* ~3 destinations get a line.
- **Corridors are PURE TRANSIT.** Nothing lives in corridors — no enemies, no panels, no gameplay. The only things on the floor are the colored guide-lines + arrowheads. **All gameplay happens inside rooms.**

### MODE B — ROOM MODE (solid, where all gameplay happens)
- A **solid, fully-textured first-person room** (Quake-style real geometry). On entering a room, the **outside graph stops being drawn** — rooms are self-contained.
- **Walls = the mathematics.** Each wall is split into **panels** (gallery frames), one diagram step or one text/equation panel each, in reading order. Each panel has two baked states: **grayscale "off"** and **colored "on."** The shooter player shoots a panel to flip it to "on" (= "I've read this"), and that state **persists to disk**.
- **Ceiling = equations**, hidden until the room's demon is defeated, then they **fade in blood-red** (with a one-off celebratory glyph "spray" flourish on the demon's death).
- **Demon** guards the room — a simple billboard/sprite creature (e.g. circles: pink body, blue eyes, white teeth). Player can't die; infinite ammo. Death = disintegration animation + triggers the ceiling reveal.
- **QED secret door (∎).** A Halmos-tombstone tile on the final-proof wall; shooting it opens it → a boss demon emerges → defeating it completes the room.
- **Read Mode (press a key, e.g. R).** Snaps a **pin-sharp, full-screen flat 2D image** of the panel you're near (no perspective, no blur), zoomable. This is the decisive fix for "dense math is unreadable on an angled 3D wall." Ship it early.

### The mode switch
Mode A ⇄ Mode B happens **at the door**. Entering a room hides the graph; exiting returns to the wireframe graph.

> **Rendering-load note (important):** the old "draw only one room per frame" rule applies to **Room Mode** (one solid room at a time). But **Corridor Mode deliberately draws the WHOLE concept-graph wireframe at once** (that's the entire point — you see the whole map around you, dimmed by distance). That's cheap because it's just lines — but please design the corridor-mode renderer to keep this fast and correct (depth test, no blend, distance-dimming via a cheap fog/shader).

---

## 3. THE TWO TRUTHS (keep them decoupled on purpose)

- **MAP truth** — the accurate, organic, force-directed graph. Nodes are points; edges are corridors. This is *navigation*, faithful to the real structure of the knowledge.
- **ROOM truth** — **TARDIS rooms**: a room is as big *on the inside* as its contents demand. **Room size comes from the room contents, NOT from the map.** A node is a single point on the map, but it can open into a hall of any size in the game. **The map positions and the room sizes never have to agree.**

## 4. THE TWO MACHINES (build-time, fully decoupled — keep them apart)

- **LEVEL MAKER** — lays out only the **points and the curves (corridors)** between them. Force-directed positions for the organic look, **plus corridor-height assignment so crossings become clean bridges/underpasses (the §1 requirement)**. Produces: node points, corridors, and each node's **importance (1–5)**.
- **ROOM MAKER** — decides **each room's contents and interior size independently**, never consulting the map.

**Importance (1–5)** drives two things: (a) the node's **circle size on the map**, and (b) **the node/room's color on the map** — i.e. **color encodes importance** (please choose a clear, colorblind-safe graded palette/scale for the 1–5 levels; since size *also* encodes importance, color and size reinforce each other — good redundancy).

## 5. THE THREE WORLDS (sacred separation — never mix)

1. **CONTENT** (design time; authored by me + LLM "content children"): the book text → a concept graph + per-room source (LaTeX paragraphs, TikZ figures). Touches LLMs and source text.
2. **BUILD** (design time; deterministic offline tools on my PC): graph → floorplan (with 3D heights), and LaTeX/TikZ → **baked PNG panels** (off grayscale + on color).
3. **RUNTIME** (the shipped game on the player's machine): loads **only baked JSON + PNG**. It **never** sees the book, never compiles LaTeX, never calls an LLM. This separation is what makes the engine reusable for the next book.

---

## 6. THE LaTeX / FIGURE BAKER + COLOR CONVENTION

- All math/diagrams are **pre-rendered (baked) to images offline** — no live LaTeX at runtime.
- **Color-group convention** (the heart of the "same concept = same color" mechanic): each panel ships a tiny sidecar mapping of **named color groups** (e.g. `"abc" → blue`). Both the **diagram (TikZ)** and the **prose/equation (LaTeX)** reference colors by **group name, never raw hex**, so a concept is the same color in the figure and in the text automatically. Compile each block **twice** — once grayscale (`off`), once colored (`on`) — from one source.
- **Colorblindness is a first-class concern** (≈8% of players): color must **never be the only cue**. Bake in **redundant signals** — numbered/lettered badges (①②③) next to each colored element *and* inline in the prose, plus per-group line styles (solid/dashed/dotted), marker shapes, and hatching. Use a **colorblind-safe palette (Okabe–Ito / Paul Tol)**; avoid pure red-vs-green as the only distinction.
- Please specify the **baker tool** precisely (LaTeX+TikZ → trimmed transparent PNG, off/on recolor, a manifest mapping block-id → image paths + pixel sizes). Ceiling equations bake neutral; the blood-red tint + reveal happen at runtime.

## 7. THE BOOK-AGNOSTIC DATA FORMAT (please finalize this)

Every book must reduce to **pages → paragraphs → (text · math · figure)**. The atom is **"a LaTeX paragraph at a (page, paragraph) address."** No closed enums — vocabulary is free text. My locked decisions:
- **edition** = a **free-text full citation sentence** (e.g. *"Newton, Principia, trans. Motte, 1729 English ed., London."*) — never a number.
- **page** = the **printed page label visible on the scan**, stored as a **string** (`"41"`, `"xii"`, `"A-3"`) — never the PDF index.
- **kind** = **free text** everywhere.
- **atoms are LaTeX paragraphs** (so the hardest equations fit in one slot).
- a **figure** may be stored as its **reproducible recipe** — the TikZ code *or* a text/image prompt that drew it — plus a **`color_map`** (which named elements get which color → this is the off/on grayscale↔color reveal mechanism).

Proposed two layers (please confirm / refine, and define the exact schema):
- **Layer 1 — Concept Graph** (the floorplan source; authored first): `level_id`, `title`, `edition`, `nodes[]`, `edges[]`. Node: `id`, `name`, `kind` (free text), `importance` (1–5), `pages` (printed span, e.g. "40–42"), `summary`, `tags[]`. Edge: `source`, `target`, `kind` (free text), `weight`, `label`.
- **Layer 2 — Room Source** (the paragraph DB; authored per room): `node_id`, `edition`, `blocks[]`. Block: `id`, `page` (printed label), `paragraph` (locator), `kind` (free), `latex`, `figure | None`, `tags[]`. Figure: `renderer` (tikz / pgfplots / asymptote / image-prompt), `source` (code or prompt), `caption`, `color_map` (name→color).

The **id spine** must be enforced: concept-node id == floorplan room id == room-source filename == runtime room id. Validate at build time, loudly. Version every JSON with a `schema_version`.

---

## 8. CO-OP FOR TWO PLAYERS (core from day one — this is a couples game)

Two people share the journey on one screen, one shared avatar, split roles:
- **MOVER** — drives the body: translation + **body heading** (where "forward" is). Only the mover changes the body heading, so the world never lurches because the other player looked around.
- **SHOOTER** — controls a **free-aim reticle** (within a generous cone) and shoots: flips panels off→on (reading), kills demons, opens the QED door.
- **Decoupled camera (the make-or-break for comfort):** the aimer moves a *reticle*, not the whole camera; the camera follows the mover's body heading with a soft, damped offset toward the reticle. This is the single biggest motion-sickness reducer and forces gentle teamwork (to read a wall behind you, the mover turns the body). Please design this carefully **for true 3D**, including: pitch clamp + smoothing, no head-bob by default, narrow-FOV option, optional motion vignette, slow default walk speed (this is a reading game), and especially **vertigo / fear-of-falling mitigation in the transparent wireframe corridor mode** (the floor guide-lines are part of this).
- **Input:** abstract **all** devices (keyboard+mouse and gamepads — e.g. one player on a controller, one on mouse/keyboard) behind a single input layer that exposes *semantic actions*, so modules never touch raw devices. Support simultaneous keyboard/mouse + gamepad.

## 9. WIN CONDITION & FLOW

- Defeat the demon in **every room** of the level → level (book section) complete. The player chooses **any order** — visit a room, pass through, or come back later; this never constrains the map.
- Between levels: **build → play → teardown → build next.** No streaming needed.
- Lean on real learning science with **zero fail states**: shoot-to-reveal is *active recall + the generation effect* (optionally show a one-line "predict what this step shows" prompt *before* the reveal); pairing diagram+text+equation is dual coding; and a **teach-back prompt at the QED door** ("before you open it, explain this proof to your partner in one sentence") is perfect for the two-player dynamic. Everything is "answer or skip" — no timers, no lives.

---

## 10. TECHNOLOGY — REQUIREMENTS & EXCLUSIONS (please read carefully)

- **All Python. Windows-first** (the overwhelming majority of players); Linux is a nice-to-have; **no browser.**
- I want **one technology** for **custom real-time 3D** where **we control the rendering pipeline directly** (we write our own shaders/draw calls) — because the look is **custom**: controlled-depth transparent wireframe, no-blend depth sorting, procedural floor guide-lines with arrowheads, and distance-dimming. A generic engine's defaults actively fight this look.
- **DO NOT propose a high-level game engine or scene-graph framework that hides the GPU/rendering pipeline.** Specifically, I do **not** want Unity, Unreal, Godot, or Python wrappers like Ursina / Panda3D. This is **not** a simple standard game and those tools make the custom wireframe pipeline harder, not easier.
- Please **recommend and justify the exact stack** (window/input/audio + direct-GPU rendering + math/imaging), and **pin specific versions**. (A direct-GPU approach — writing our own GLSL — plus a lightweight windowing/input library and NumPy/Pillow for offline imaging is the kind of thing I have in mind, but I want your reasoned recommendation, not a rubber stamp.)
- **Packaging:** a one-folder Windows build (e.g. PyInstaller) shipping the baked content pack; runtime depends only on baked assets.

## 11. HOW I BUILD THIS (so you can size the architecture correctly)

I build with an **LLM assembly line**, so the architecture must suit it:
- An **architect AI** holds this document + a small ledger and writes tightly-scoped prompts — it never writes big code.
- **Fresh "child" AI chats** each implement **exactly one module** to a **frozen typed contract** + tests, then are discarded.
- A **coding agent (DeepSeek, in OpenCode)** on my Windows PC integrates the code, runs the tests, fixes wiring, and pushes to GitHub.

Design implications I need you to honor:
- **Small single-file modules**, each one concern, communicating **only** through **typed function signatures + data contracts (pydantic/JSON)** — never importing another module's internals. **Frozen signatures**, versioned explicitly when they must change.
- **Headless-first testing**: pure helpers / fakes / monkeypatch so tests run with no window; guard any display-needing test so it skips gracefully.
- A tiny **golden-fixture level** every module tests against; `schema_version` asserted on load; CI runs the tests + content validation on every push.
- Give a **module map** (the ~20 single-file modules), the **frozen public contract** (signatures) for each, the **per-frame wiring order**, and a **milestone roadmap** (each milestone independently runnable/testable) ending in one full level end-to-end, then a second content pack to prove genericity.

---

## 12. OPEN QUESTIONS I'd like YOU to resolve (propose options + recommend)

1. **The exact technology stack** (per §10), with versions and justification.
2. **The 3D layout + corridor-height algorithm**: force-directed placement + how you assign heights so crossings become clean bridges/underpasses; deterministic by seed; importance (1–5) → room size + map color.
3. **Transparency/depth strategy** for the wireframe graph (depth test, no blend, Z-order correctness, distance-dimming implementation) so the current corridor is never obstructed and the far graph stays dimly visible (never blinding white, never pure black).
4. **The floor-guide-line selection rule**: how to choose the ~3 destinations that get a colored line + arrowheads ("nearest + most important" — define it precisely).
5. **Movement model in corridor mode**: how the player traverses the 3D graph (walk along corridors with door transitions; how junctions/over-under choices work).
6. **True-3D comfort plan** for co-op (vertigo, vertical look, fear-of-falling through the wireframe, the felt floor).
7. **The baker spec** (LaTeX/TikZ → off/on PNGs + manifest + colorblind redundancy).
8. **Licensing**: Newton's _Principia_ (1687) text/figures are public domain; my own redrawn TikZ is mine. Recommend a split (e.g. code under a permissive license, content under CC-BY-SA) and an attribution practice for any Wikipedia-derived prose.

## 13. HOW TO TREAT ME (learned the hard way)

- **Never invent facts.** If you don't know something, say so and ask — do not present guesses as ground truth.
- Ask **few, real, load-bearing questions** — never trivia, never things already decided here.
- Don't be condescending, don't pad, don't copy boilerplate — **think independently** and make the hard calls with reasons.

---

## 14. DELIVERABLE

A complete, self-contained **Master Design Document** I can hand to every future architect chat, covering: vision + hard invariants (true-3D), the two render modes, the two truths, the two machines, the three worlds, the baker + color convention, the book-agnostic data format, co-op, technology (recommended + pinned), the module map + frozen contracts + per-frame wiring, the milestone roadmap, packaging, and a risk section. First content pack: **Newton's _Principia_**. Mark any genuine gaps as gaps. Thank you!
