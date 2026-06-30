# 🧰 PROMPT TO OPUS — QUAKE PARENT 16 (ROOM-CONTENT FORMAT + BUILDER TOOL)

> **Your mission, in one sentence:** design a simple, child-fillable **keyword-block text format** for the content of a Quake room, and build a Python tool **`build/room_from_spec.py`** that turns one such spec file into the game's validated content files (`recipe.<figure_id>.json` + `figure.<figure_id>.asy` for geometry, and `room_source.<node_id>.json` for every room). One reusable tool, run many times by DeepSeek, fed by many parallel "child" chats that each write one room's spec in your format — none of them ever touching JSON or Asymptote.
>
> Written by **DeepSeek** (the runner). You are a fresh architect; design this cleanly from the world as it actually is, described below.

---

## §0 — HOW WE WORK (short — the baseline docs you were given say the rest)

You already have, in this chat: **the Commentaries**, the **Old Testament**, the **New Testament**. The model: **you (architect) write documents** — the format spec + the tool design/child-brief — and **never run code yourself**; **child** chats each fill in one room; **DeepSeek** runs your tool, integrates, tests, pushes, and **fetches any file/text you ask for** (you have no internet or file access — §4); **Nir** decides everything and knows no code and no math. Be honest, surface real choices, and **talk first, then build** (§6).

---

## §1 — THE COLOR SYSTEM (the heart of Quake — your format must carry it)

A **station** = one proof step = a **panel** (the thing you look at) beside its paired **explanation-text panel** on the wall.

**Rule 1 — Matching colors (LOCAL, per station).** Within one station, each important element gets its **own distinct local color**, and **the same words in the paired text carry that same color** (standard `\textcolor{name}{...}` in the LaTeX). Colors are **local** — chosen fresh per station; the same concept may be a different color, or uncolored, in another station. Unimportant ink is plain **black** (light background) or **white** (dark background) — **never grey**.

**Rule 2 — Stabilo bright highlighter (current step only).** Only the **current step's heart(s)** — the single most important element(s) of that step — get a bright translucent marker swipe (yellow/green/orange/pink/cyan), chosen fresh per step. **Never cumulative.**

In the data: each drawn element carries `local_color {name,hex} | null`, `step`, `is_heart`; each text block carries `colors_used` (the local colors in its `\textcolor` spans, **populated by your tool by scanning** — never by the child); each figure carries the union. (Exact pydantic schemas: §3 / request `raw_models.py`.)

---

## §2 — WHAT GOES IN: MATH + ITS FOUNDATIONS; THREE KINDS OF PANEL

Quake includes **the math** (geometry + equations/relationships) **and the key non-math foundations the math rests on** — the physical (or, in other books, chemical/biological) facts and ideas that give it intuition, meaning, and significance (e.g. for inertia: the spinning top, the planets, the projectile). **Excluded:** only meaningless filler — biography, history, narrative with no intuitive value. "Energy = mass × c²" counts; the spinning-top illustration counts (it gives intuition); "the date the book was written" does not. **Everything included is colored the same way** (matching local colors + Stabilo heart). So a panel is one of three kinds:

**(a) Geometry panel.** The element is a drawn figure built from a coordinate-free **construction recipe** (points, lines, circles, conics, series of rectangles, …), rendered by **Asymptote** into off/on highlighted images. The matching text panel quotes/explains the step with `\textcolor` spans matching the figure's colors.

**(b) Equation panel.** For a math step with **no diagram**, the **equation itself is the panel** and is treated exactly like a figure: color the individual important **terms/symbols** of the equation, each its own distinct local color, and color the matching descriptive **words** in the paired explanation the **same** color (word ↔ symbol, exactly like word ↔ shape). The explanation comes from the source text where it exists; **where the text gives no explanation, it is written in simple words with minimal math — to EXPLAIN what the equation means, never to merely repeat the symbols.** The Stabilo heart works identically (current step's key term only).

*Example — Prop. IV, F ∝ v²/r:* on the equation panel color `v²` blue, `r` green, `F` orange; in the explanation, "the square of the speed" is blue (↔ v²), "the distance from the centre" green (↔ r), "the pull toward the centre" orange (↔ F). The words explain the meaning ("the faster it goes, the harder the pull — growing with the square of the speed"); they do not read the symbols aloud.

**(c) Foundation panel.** For a **key non-math idea the math rests on** (e.g. inertia's spinning top), the **statement/illustration is the panel**: color its key concepts (a few words each), and color the matching words of the paired explanation the same color, with a per-step heart — exactly like a figure or an equation. Use the book's own words where they exist; otherwise write a short, faithful description (no invented math). This is **not** ELI5 of arbitrary prose — only for ideas that genuinely give the math meaning; pure history/trivia is skipped.

So **every room has something colored to look at and shoot** — a figure, an equation, or a foundational illustration — beside a matching-colored explanation. There are no inert prose rooms, and nothing is dropped for lacking equations.

**An equation or foundation panel is almost certainly a colored LaTeX image** (much like the explanation panels and the ceiling equations already bake), **not** an Asymptote construction — so such a station likely needs **no recipe/.asy**, just its colored image + colored explanation. Confirm the exact representation (does it use the same "drawing" slot? a small schema addition? — DeepSeek will tell you what the current contract allows and will make any change you specify). Don't guess silently; ask (§4).

---

## §3 — WHAT YOUR TOOL MUST EMIT (the real schemas)

Output must validate against the actual pydantic models in `map/raw_models.py` (`extra="forbid"`, `schema_version "1.0"`). The three outputs:

- **`recipe.<figure_id>.json`** (geometry rooms): `figure_id` (`^[a-z][a-z0-9_]*\.f[0-9]+$`), `node_id`, `edition`, `caption`, `n_steps`, `steps:[{index,gloss}]`, `ops:[RecipeOp]`. Each op has `name` + optional `draw {local_color?, step, is_heart, label?, marker}`. The 28-op construction vocabulary covers points, lines/rays, circles/arcs, conics (ellipse/parabola/hyperbola/5-point), and compounds (`polygon`, `polyline`, `series`).
- **`figure.<figure_id>.asy`** (geometry rooms): self-contained Asymptote with an `int highlight` parameter (−1 = OFF/all black; `k` = step k's colors + step k's Stabilo), per-local-color pens, `usersetting()`, hex as `rgb(r/255,g/255,b/255)` (not `0xHH`), Stabilo under ink, labels black.
- **`room_source.<node_id>.json`** (every room): `node_id`, `edition`, `figures:[FigureDecl]`, `blocks:[StepPair{pair_id, step_index, drawing, text}]`, `final_pair_id`, `ceiling_equations:[{eq_id,latex}]`. `TextBlock.colors_used` and `FigureDecl.colors_used` are tool-populated by scanning `\textcolor`.

Request `raw_models.py` (full file) and the **validated gold geometry reference** (`lemma_2` recipe + .asy + room_source) from DeepSeek — they show the corrected color model and the Asymptote conventions working end to end. For equation panels, DeepSeek will show you how LaTeX with `\textcolor` already bakes (`baker_text.py`) so you can mirror it.

---

## §4 — HOW YOU GET INFORMATION (no internet / no files)

**Ask DeepSeek precise questions** (batched welcome); DeepSeek pastes back **exact verbatim** excerpts of only what you need — `raw_models.py`, the lemma_2 gold files, the text baker, the **finalized room list** (which rooms are geometry rooms, which are equation rooms, with step counts — see §5), and any Principia text. Burn DeepSeek's effort to protect your context; ask for specific files/sections, never "the whole Bible."

---

## §5 — THE ROOMS YOU ARE DESIGNING FOR

The first level is `principia_bk1_inverse_square` (Newton, Book I, Sections I–III), ~20 rooms whose stations are a mix of **geometry**, **equations**, and **foundational illustrations** per §2 (no node is dropped; e.g. inertia stays as a foundation room — only meaningless history/trivia is skipped). The exact per-room classification and step counts come from the finalized level design; **DeepSeek will give you that list before you build.** Design the format and tool to handle all kinds uniformly, and to scale to 20+ children writing one room each. Your format must be simple enough that a child AI, given only your format spec + its room's source text, can fill it in correctly.

---

## §6 — RULES & START

Deliver everything Nir will copy as **prose or fenced code blocks — never Markdown tables** (they lose their cells on copy-paste). **Talk first, then build:** in your first reply, state your proposed format (keyword names, block structure, how a child expresses a geometry station vs an equation station, how colors + hearts are declared), your tool architecture (parse → validate → emit), and **all** your questions; then wait for DeepSeek's answers and Nir's confirmation before you build. One mission, one deliverable: the format spec + `build/room_from_spec.py`.
