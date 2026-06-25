# REQUEST TO FUSION — Master Design Document for a Quake-style, Geometry-Rich 3D Game (fresh start)

Hi! I'm Nir. I'm building an open-source, free-forever 3D game for couples to play together ("two minds at a time"). I need you to design — from a clean sheet — the complete **Master Design Document** for this game. This document will be the top-layer "bible" I hand to every future architect/AI chat, so make every decision for me, explain the reasoning where it matters, and be honest about anything you are unsure of (mark gaps as gaps — never invent facts).

Produce a single, comprehensive Master Design Document covering everything below, plus anything important I've missed. Where a decision is still open, propose 2–3 concrete options and **recommend one**.

---

## ⛔ GROUND RULES — read these first, they are absolute

1. **GEOMETRY-RICH BOOKS ONLY.** This entire project exists for ONE kind of content: books that justify their logic through **geometric arguments** and **prove things geometrically** — books where the reasoning lives in the *figures*. The whole game is built around presenting **geometric proofs, step by step, in 3D rooms.** (Examples that define the target are in §1.) If a book isn't geometry-rich, it is out of scope. Please make this the spine of the whole document.
2. **DO NOT spend a single token on colorblind / accessibility considerations.** I do not want any such consideration anywhere in this game — none. (Asking me to limit my colors would be like asking Van Gogh not to use a color.) Use whatever colors are most beautiful and clear. No "colorblind-safe palettes," no redundant-cue requirements, nothing.
3. **DO NOT spend a single token on licensing / copyright of the books or material.** I handle all of that myself. Do not analyze it, do not mention it.
4. **THIS IS A FUN GAME, NOT EDUCATIONAL SOFTWARE.** Do **not** add quizzes, "predict what this shows" prompts, "explain it to your partner before you open the door" prompts, comprehension gating, spaced-repetition, or any pedagogical scaffolding. That ruins the feel. The fun comes from exploring a beautiful 3D world and reading gorgeous geometry. The game's only job is to be fun.

---

## 1. SCOPE & CONCEPT — geometry-rich books, turned into a 3D dungeon

A first-person desktop game (Python, Windows-first) that turns a **geometry-rich book into a walkable 3D dungeon of ideas**. The player physically walks the book's **concept graph**: each idea is a **room**, each logical dependency between ideas is a **corridor**, and the **geometric proof of that idea is shown step by step on the room's walls.**

**The target books** (this defines the genre precisely):
- Early editions of **Newton's _Principia_** (*Philosophiæ Naturalis Principia Mathematica*) — celestial mechanics proven through classical geometry. **This is the first content pack.**
- Schey's **_Div, Grad, Curl, and All That_** — vector calculus taught through geometric/field pictures.
- Tristan Needham's **_Visual Complex Analysis_** — complex analysis done entirely through pictures.

These are among the hardest mathematics in the world, and their genius is **geometric**. The game must do justice to that.

**The core in one breath:** You walk a 3D concept graph. You enter a room and find its walls covered in the **step-by-step geometric proof** of that concept. You "read" a panel by **shooting it** — it flips from grayscale **"off"** to colored **"on."** When you shoot the room's **final proof-step wall** (once it's been turned on/colored), that wall **opens like a hidden door** and the room's **single enemy** ("demon") emerges; defeat it and the room's **equations reveal in blood-red on the ceiling.** There is exactly **one enemy per room** and **no level-wide boss.** Clear every room → the level (book section) is complete.

**God-mode feel:** you cannot die; infinite ammo; no fail states. Shooting does two things — it **reveals proof panels** (reading) and **defeats the single hidden enemy** once you've opened its wall. **Clarity and beauty of the geometry matter more than graphical fidelity** (the look is deliberately minimalist — see §2). **The engine is generic;** the book is a swappable content pack.

---

## 2. THE NON-NEGOTIABLE PIVOT — true 3D (Quake-style), NOT a flat/2.5D world

This is the single most important requirement and the reason for the whole technology choice.

**The problem:** the dungeon layout comes from a **force-directed graph drawing** (spring / Fruchterman–Reingold) of the book's real concept graph — because that produces the organic, faithful shape of the knowledge. But force-directed layouts of real graphs **almost always produce edges (corridors) that cross.** In a flat single-floor world you'd be forced to reroute or forbid crossings, which distorts the true structure and looks wrong.

**The solution = real 3D, like Quake:** corridors are placed at **different heights** so that where two corridors cross on the 2D plan, in the game one passes **over** the other as a **bridge / underpass**. **Crossings are a FEATURE, not a problem.** Because the world is genuinely 3D (areas above areas, bridges, underpasses), the map stays faithful to the real, organic, crossing-rich structure of the knowledge.

**Therefore:** this is **not** a simple/standard flat shooter. The world has **vertical separation** (multiple heights, bridges, underpasses, ramps — true 3D navigation). The layout must lay out the graph and then **assign corridor heights** so crossings resolve cleanly as over/under passes. Please specify this algorithm (deterministic by seed).

---

## 3. THE TWO RENDER MODES (switched at the door)

The game has exactly **two visual modes**, switched by passing through a room's **door**.

### MODE A — CORRIDOR / WIREFRAME GRAPH MODE (transit between rooms)
The player literally **walks the concept graph as a live 3D map**, with a very specific custom look I care about a lot:
- **Transparent wireframe only.** Corridors and the graph are drawn as see-through wireframe — a deliberately minimalist "discount" look. **Do not upgrade corridors to shaded/solid polygons.**
- **Depth-tested, NO alpha blending.** Near geometry occludes far; correct Z-order; the corridor you're standing in must never be visually obstructed by a distant one. Close draws on top of far.
- **Distance dimming.** The section you're in is **pure white**; farther sections fade progressively toward **dark grey — never pure black, always still dimly visible** (so the whole graph is perceptible around/above/below you, never a blinding white blur).
- **Crossings visible in 3D.** Because the wireframe is see-through, the player perceives being above/below other routes (bridges/underpasses). Embrace this.
- **Floor guide-lines (Half-Life style).** On the floor, **about 3 colored lines only** — for the **nearest and most important destination rooms** (NOT one line per room). Each has **arrowheads** indicating direction + a sense of near/far. They also provide a **felt floor**, fighting the vertigo / fear-of-falling that a transparent wireframe over open 3D space would cause. Please specify the rule for *which* ~3 destinations get a line.
- **Corridors are PURE TRANSIT.** Nothing lives in corridors — no enemies, no panels, no gameplay. Only the colored guide-lines + arrowheads. **All gameplay is inside rooms.**

### MODE B — ROOM MODE (solid, where all gameplay happens)
- A **solid, fully-textured first-person room** (Quake-style real geometry). On entering, the **outside graph stops being drawn** — rooms are self-contained.
- **Walls = the geometric proof, presented STEP BY STEP.** A proof is a sequence of steps, and **each step occupies a coupled PAIR of wall sections in the same room:** (1) the step's **DRAWING** — the geometric figure for that exact step — and (2) the step's **EXPLAINING TEXT**. **Every illustration wall section is ALWAYS paired with an explaining-text wall section.** The explaining text is **always full LaTeX** (it carries the hardest math in the world — heavy equations are normal). **Everything is pre-baked to images at design time — never rendered on the fly. Full LaTeX, baked.** Each panel has two baked states: grayscale **"off"** and colored **"on"**; shooting flips it to "on" (= read) and the state persists to disk.
- **The hidden enemy (the room's only creature).** On entering a room you see **no enemy at all.** The room's **final proof-step wall** (its drawing or its explaining-text section, once it has been turned **"on" / colored**) doubles as a **hidden door:** shoot it and the wall **opens**, releasing the room's **single enemy** (a simple billboard creature — call it a "demon"). Defeat it (you can't die; infinite ammo; death = a disintegration flourish) → the room is complete. **There is exactly ONE enemy per room, and NO level-wide boss.**
- **Ceiling = equations**, hidden until that single enemy is defeated, then they **fade in blood-red** with a one-off celebratory glyph "spray" flourish.
- **Read Mode (press a key, e.g. R).** Snaps a **pin-sharp, full-screen flat 2D image** of the panel you're near (no perspective, no blur), zoomable. The decisive fix for "dense geometry/math is unreadable on an angled 3D wall." Ship it early.

### The mode switch
Mode A ⇄ Mode B happens **at the door**. Entering a room hides the graph; exiting returns to the wireframe graph.

> **Rendering-load note:** the "draw only one room per frame" idea applies to **Room Mode** (one solid room at a time). But **Corridor Mode deliberately draws the WHOLE concept-graph wireframe at once** — that's the point. It's cheap (just lines), but design the corridor-mode renderer to keep it fast and correct (depth test, no blend, distance-dimming via a cheap fog/shader).

---

## 4. THE TWO TRUTHS (decoupled on purpose)

- **MAP truth** — the accurate, organic, force-directed graph. Nodes are points; edges are corridors. Faithful to the real structure of the knowledge.
- **ROOM truth** — **TARDIS rooms**: a room is as big *on the inside* as its contents demand. **Room size comes from the room contents, NOT from the map.** A node is one point on the map, but it can open into a hall of any size. **Map positions and room sizes never have to agree.**

## 5. THE TWO MACHINES (build-time, fully decoupled)

- **LEVEL MAKER** — lays out only the **points and the curves (corridors)** between them: force-directed positions, **plus corridor-height assignment so crossings become clean bridges/underpasses (§2).** Produces node points, corridors, and each node's **importance (1–5).**
- **ROOM MAKER** — decides **each room's contents and interior size independently**, never consulting the map.

**Importance (1–5)** drives two things: (a) the node's **circle size on the map**, and (b) the node/room's **color on the map** — i.e. **color encodes importance** (choose a clear, beautiful graded palette/scale for the 1–5 levels; size also encodes importance, so they reinforce each other).

## 6. THE THREE WORLDS (sacred separation — never mix)

1. **CONTENT** (design time; authored by me + LLM "content children"): the book → a concept graph + per-room source (full-LaTeX explaining-text paragraphs, geometric step figures). Touches LLMs and the source scans.
2. **BUILD** (design time; deterministic offline tools on my PC): graph → floorplan (with 3D heights), and the geometry/LaTeX source → **baked PNG panels** (grayscale "off" + colored "on").
3. **RUNTIME** (the shipped game): loads **only baked JSON + PNG**. It **never** sees the book, never compiles LaTeX, never calls an LLM. This is what makes the engine reusable for the next geometry-rich book.

---

## 7. ⭐ THE GEOMETRY PIPELINE — the hardest, most important problem (please go deep here)

This is the crux of the whole project, so spend real thought on it.

**What it must do:** turn the geometric figures of a real book into **reproducible, editable, design-time source ("code"/text)** that bakes to images, supports **step-by-step cumulative construction** (step 1 draws part of the figure, step 2 adds to it, …), and supports **coloring individual named elements in different colors** (so one line is blue, one angle is red, etc.) — and from that single source bake the two states (grayscale **"off"** → colored **"on"**) for the shoot-to-reveal mechanic. The same concept should get the **same color in the figure and in its explaining text.**

**The concrete questions I need you to answer honestly:**
1. **TikZ, evaluated critically:** Can a frontier AI (e.g. Claude Opus 4.8) reliably take a **PNG scan of an original book page** (e.g. from Archive.org, assuming decent scan quality) and **reproduce that geometric figure accurately as TikZ**, with named, individually-colorable elements, at design time? How reliable is this really — for *classical compass-and-straightedge* figures and for *vector-field/complex-plane* figures? Be candid about failure modes.
2. **If TikZ + AI is NOT reliable enough**, what is the best pipeline to convert **PNG scan → accurate, reproducible, colorable, design-time geometry source?** **TikZ is NOT sacred.** I am happy to install software, add a Python library, or pay for a tool if it makes the conversion accurate. Compare real options — e.g. AI→TikZ/PGF, AI→Asymptote, AI→SVG (then convert), GeoGebra construction → export, vector tracing (Inkscape/potrace), image-to-vector ML, semi-automated assisted vectorization, etc. — and **recommend a concrete, workable workflow.**
3. Whatever you recommend, the output must: (a) be **editable, reproducible text** at design time; (b) support **per-element named coloring**; (c) support **step-by-step cumulative** figures (one step = one drawing panel + its paired explaining-text panel); (d) bake cleanly to off/on PNGs. The **explaining text is always full LaTeX**, baked offline.
4. Specify the **baker** precisely: how text panels (full LaTeX) and geometry figures (your recommended tech) both become trimmed transparent **off/on PNGs** + a manifest (block-id → image paths + sizes). Ceiling equations bake neutral; the blood-red tint + reveal happen at runtime.

---

## 8. THE BOOK-AGNOSTIC DATA FORMAT (please finalize this)

Every geometry-rich book reduces to **pages → paragraphs → (text · math · figure)**. The atom is **"a LaTeX paragraph at a (page, paragraph) address."** No closed enums — vocabulary is free text. My locked decisions:
- **edition** = a **free-text full citation sentence** (e.g. *"Newton, Principia, trans. Motte, 1729 English ed., London."*) — never a number.
- **page** = the **printed page label visible on the scan**, a **string** (`"41"`, `"xii"`, `"A-3"`) — never the PDF index.
- **kind** = **free text** everywhere.
- **atoms are LaTeX paragraphs** (so the hardest equations fit in one slot).
- a **figure** is stored as its **reproducible recipe** (the geometry source from §7) + a **`color_map`** (which named elements get which color → drives the off/on grayscale↔color reveal). Figures and their paired explaining text reference colors by **named group, never raw hex**, so a concept is the same color in figure and prose.

Proposed two layers (confirm / refine, and define the exact schema):
- **Layer 1 — Concept Graph** (floorplan source; authored first): `level_id`, `title`, `edition`, `nodes[]`, `edges[]`. Node: `id`, `name`, `kind` (free), `importance` (1–5), `pages` (printed span), `summary`, `tags[]`. Edge: `source`, `target`, `kind` (free), `weight`, `label`.
- **Layer 2 — Room Source** (paragraph DB; authored per room): `node_id`, `edition`, `blocks[]`, where **blocks come in coupled step pairs (a drawing block + its explaining-text block)**. Block: `id`, `page`, `paragraph`, `kind` (free), `latex` (for text blocks — full LaTeX), `figure | None` (for drawing blocks), `tags[]`. Figure: `renderer` (your §7 recommendation), `source` (code/recipe), `caption`, `color_map`.

Enforce the **id spine**: concept-node id == floorplan room id == room-source filename == runtime room id, validated loudly at build time. Version every JSON with `schema_version`.

---

## 9. CO-OP FOR TWO PLAYERS (core from day one — this is a couples game)

Two people share the journey on one screen, one shared avatar, split roles:
- **MOVER** — drives the body: translation + **body heading** (where "forward" is). Only the mover changes the body heading, so the world never lurches because the other player looked around.
- **SHOOTER** — controls a **free-aim reticle** (within a generous cone) and shoots: flips panels off→on (reading), opens the final-proof-step wall, and defeats the single enemy.
- **Decoupled camera (the comfort make-or-break):** the aimer moves a *reticle*, not the whole camera; the camera follows the mover's body heading with a soft, damped offset toward the reticle. This is the biggest motion-sickness reducer and forces gentle teamwork. Design it carefully **for true 3D**: pitch clamp + smoothing, no head-bob by default, narrow-FOV option, optional motion vignette, slow default walk speed, and especially **vertigo / fear-of-falling mitigation in the transparent wireframe corridor mode** (the floor guide-lines are part of this).
- **Input:** abstract **all** devices (keyboard+mouse and gamepads — e.g. one player on a controller, one on mouse/keyboard) behind a single layer that exposes *semantic actions*; modules never touch raw devices. Support simultaneous keyboard/mouse + gamepad.

## 10. WIN CONDITION & FEEL

- Defeat the single hidden enemy in **every room** → the level (book section) is complete. The player chooses **any order** — visit a room, pass through, or come back later; this never constrains the map.
- Between levels: **build → play → teardown → build next.** No streaming needed.
- **Remember GROUND RULE #4: this is a fun game, not educational software.** No quizzes, no prediction/guess prompts, no "explain to your partner" prompts, no comprehension gating, no timers, no lives, no fail states. The fun is exploring a beautiful 3D world and reading stunning geometry.

---

## 11. TECHNOLOGY — REQUIREMENTS & EXCLUSIONS (read carefully)

- **All Python. Windows-first** (the overwhelming majority of players); Linux is a nice-to-have; **no browser.**
- I want **one technology** for **custom real-time 3D** where **we control the rendering pipeline directly** (we write our own shaders/draw calls) — because the look is **custom**: controlled-depth transparent wireframe, no-blend depth sorting, procedural floor guide-lines with arrowheads, distance-dimming. A generic engine's defaults actively fight this look.
- **DO NOT propose a high-level game engine or scene-graph framework that hides the GPU/rendering pipeline.** Specifically, I do **not** want Unity, Unreal, Godot, or Python wrappers like Ursina / Panda3D. This is **not** a simple standard game and those tools make the custom wireframe pipeline harder, not easier.
- Please **recommend and justify the exact stack** (window/input/audio + direct-GPU rendering + math/imaging) and **pin specific versions.** (A direct-GPU approach — writing our own GLSL — plus a lightweight windowing/input library and NumPy/Pillow for offline imaging is the kind of thing I have in mind, but I want your reasoned recommendation, not a rubber stamp.)
- **Packaging:** a one-folder Windows build (e.g. PyInstaller) shipping the baked content pack; runtime depends only on baked assets.

## 12. HOW I BUILD THIS (so you can size the architecture)

I build with an **LLM assembly line**, so the architecture must suit it:
- An **architect AI** holds this document + a small ledger and writes tightly-scoped prompts — it never writes big code.
- **Fresh "child" AI chats** each implement **exactly one module** to a **frozen typed contract** + tests, then are discarded.
- A **coding agent (DeepSeek, in OpenCode)** on my Windows PC integrates the code, runs the tests, fixes wiring, and pushes to GitHub.

So please honor: **small single-file modules**, each one concern, communicating **only** through **typed signatures + data contracts (pydantic/JSON)** — never importing another module's internals; **frozen signatures** (versioned explicitly when they must change); **headless-first testing** (pure helpers / fakes / monkeypatch; display-needing tests skip gracefully); a tiny **golden-fixture level**; `schema_version` asserted on load; CI runs tests + content validation. Give a **module map** (~20 single-file modules), the **frozen public contract** per module, the **per-frame wiring order**, and a **milestone roadmap** (each milestone independently runnable) ending in one full level end-to-end, then a second content pack to prove genericity.

---

## 13. OPEN QUESTIONS for YOU to resolve (propose options + recommend)

1. **The exact technology stack** (§11), with versions and justification.
2. **⭐ The geometry pipeline (§7)** — TikZ vs alternatives for turning a PNG book-scan into reproducible, colorable, step-by-step geometry source. **This is the most important content question — go deep.**
3. **The 3D layout + corridor-height algorithm**: force-directed placement + height assignment so crossings become clean bridges/underpasses; deterministic by seed; importance (1–5) → room size + map color.
4. **Transparency/depth strategy** for the wireframe graph (depth test, no blend, Z-order, distance-dimming) so the current corridor is never obstructed and the far graph stays dimly visible (never blinding white, never pure black).
5. **The floor-guide-line selection rule** (which ~3 destinations get a colored line + arrowheads — "nearest + most important," precisely defined).
6. **Movement model in corridor mode** (how the player traverses the 3D graph; junctions; over/under choices).
7. **True-3D comfort plan** for co-op (vertigo, vertical look, fear-of-falling through the wireframe, the felt floor).
8. **The baker spec** (full-LaTeX text panels + geometry figures → off/on PNGs + manifest; step-by-step cumulative figures).

## 14. HOW TO TREAT ME (learned the hard way)

- **Never invent facts.** If you don't know something, say so and ask — do not present guesses as ground truth.
- Ask **few, real, load-bearing questions** — never trivia, never things already decided here.
- Don't be condescending, don't pad, don't copy boilerplate — **think independently** and make the hard calls with reasons.

## 15. DELIVERABLE

A complete, self-contained **Master Design Document** I can hand to every future architect chat, covering: the geometry-rich scope, vision + hard invariants (true-3D), the two render modes, the two truths, the two machines, the three worlds, **the geometry pipeline (your headline recommendation, §7)**, the baker, the book-agnostic data format, co-op, technology (recommended + pinned), the module map + frozen contracts + per-frame wiring, the milestone roadmap, packaging, and a risk section (engineering/comfort/pipeline risks only — **no accessibility, no licensing**). First content pack: **Newton's _Principia_**. Mark any genuine gaps as gaps. Thank you!
