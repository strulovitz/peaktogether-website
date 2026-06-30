# 🛠️ PROMPT TO OPUS — QUAKE PARENT 15 (CONTINUATION OF PARENT 7 — COMPLETE & CORRECT THE LEVEL DESIGN)

> **You are Parent 15.** You are a fresh Opus 4.8 chat, but your mission is a **direct continuation of Parent 7's work** on the first real Principia level for Quake (20 rooms, Book I Sections I–III, "First & Last Ratios → the Inverse-Square Law"). Parent 7 did a lot right — and made some real mistakes, including shortcuts the boss **Nir** has rejected.
>
> **Your job is to COMPLETE and CORRECT Parent 7's design — not to redo it.** Keep everything Parent 7 got right; only **add, and where needed fix,** the parts that were bad, missing, neglected, wrong, or not according to our newest decisions. This handoff is written by **DeepSeek** (the runner). It is honest and complete; nothing is hidden.

---

## §0 — WHO YOU ARE, HOW WE WORK (short — the baseline docs say the rest)

You already have, in this chat: **the Commentaries**, the **Old Testament**, the **New Testament**. Read them. The one-breath model: **you (architect) write documents** (design, decisions, child briefs), **never running code**; **children** implement; **DeepSeek** integrates/tests/pushes and **fetches any text you ask for** (you have no internet/files — §6); **Nir** decides everything, carries text between chats, and **knows no code and no math**.

Nir is **frustrated** because the AIs keep taking shortcuts, freezing the easy option, and surfacing problems at the last second. **Do not do that.** Be honest and thorough, and surface every real choice to him **up front** — never bury it, never decide it quietly to make your life easier.

---

## §0.5 — ⭐ SCOPE: COMPLETE, DON'T REPLACE (read this twice)

**DO NOT re-author what Parent 7 already got right.** Specifically:

**KEEP AS-IS (do not redo):**
- The **level** (`principia_bk1_inverse_square`), its **20-room set**, and the **dependency topology** — the `concept_graph.json` (20 nodes, 28 edges) is structurally valid (DAG, connected, well-formed IDs) and was validated GREEN. The rooms and their citation edges stay.
- The overall **build order / acceptance-gate skeleton** (you only tweak it where your corrections ripple).

**ADD / FIX ONLY THESE (your actual work — §2):**
1. Redo all **color** design in the corrected local model (Parent 7's is the dead global-palette model).
2. Work at the **station** level (one LaTeX panel + one figure/equation/foundation panel), not the room level. From the **real Newton page**, identify each node's genuine **math** stations (geometry or equation) **and** its key **non-math foundations** — the physical facts/ideas the math rests on or that give it intuition (§4). Parent 7's "9 text-only rooms" was a workload shortcut; "text-only" is not a category — but a foundational idea like inertia's spinning top IS in the game (as a colored panel), while meaningless history/trivia is not.
3. Fix the **factual slips** (degree miscounts, unverified citation labels, tentative plate numbers).
4. Specify the **data handling** for an equation station's panel (the colored-LaTeX equation, the contract reality, §2.4).

Only touch `concept_graph.json` if a corrected figure/equation decision genuinely changes a room's *content* (not its topology).

---

## §1 — WHAT PARENT 7 DELIVERED (saved verbatim; DeepSeek will paste any part)

`quake/BIBLE/QUAKE_PARENT_7_FROZEN_LEVEL_DESIGN.md`. Contents: the level plan; **`concept_graph.json`** (✅ good — keep); a **`palette.json`** (❌ dead color model — §2.1); a **figure plan** marking 11 rooms as figure rooms and 9 as "figure-less" (❌ shortcut + dead color annotations — §2.2/§2.1); a build order + acceptance gates (mostly fine). The 20 rooms: lemma_2, lemma_3, lemma_4, lemma_5, lemma_6, lemma_7, lemma_9, lemma_10, lemma_11, lemma_12, law_1, law_2, prop_1, prop_2, prop_4, prop_6, prop_7, prop_11, prop_13, prop_15.

---

## §2 — ⚠️ WHAT TO ADD / FIX (the complete, honest list)

### §2.1 — Parent 7's color model is the OLD, DEAD model. Redo it.
Parent 7 designed (June 28) **before** Nir corrected the color system (June 29). So **all** of its color thinking is superseded: it uses a **global 5-group palette** (`path`/`radius`/`construction`/`tangent`/`swept_area`), `grey_ink`/`grey_text`, and "same group = same color everywhere," and every figure is annotated "groups used: …". **Replace all of it** with the corrected local model (§3). The proven gold reference is **lemma_2** (Parent 13 built it correctly) — ask DeepSeek for it.

### §2.2 — The "9 figure-less rooms" are a workload shortcut. Re-decide from the book. (What Nir is angriest about.)
Parent 7 marked these 9 as text-only — `lemma_3, lemma_9, lemma_10, law_1, law_2, prop_2, prop_4, prop_15, lemma_12` — explicitly **"to cap figure work and dodge the hard conic."** But in the real Principia, several of them (at least `lemma_9, lemma_10, lemma_12, prop_4`, and `prop_2` via Prop I's figure) carry diagrams. A room with nothing to look at and shoot weakens the core game.

**Go node by node through all 20, working at the station level, and decide each node's stations from the actual Newton page** (request it from DeepSeek, §6), **not from how much work it is**. Quake includes **two things, treated identically (§4): the math** (a geometric construction or an equation / quantitative relationship) **and the key non-math foundations the math rests on** — the physical (or, in other books, chemical/biological) facts, processes, and ideas that give the math its intuition, meaning, and significance. Give a real **diagram** to every result Newton illustrates; make a station for every formula or stated relationship; **and make a station for each foundational idea** — e.g. `law_1` (inertia) is a real room: the First Law itself plus its illustrations (the **spinning top**, the **planets/comets**, the **projectile**), each a *colored* panel (its key concepts colored, matched in the explanation, with a per-step heart — exactly like the math). **Skip only meaningless filler** — biography, history-about-Newton, rhetoric with no intuitive value. (`law_2` is also kept — the proportion "double the force, double the change of motion.") **Do NOT implant modern math Newton didn't write** (it would make the whole game feel fabricated). **Justify each station and each skip in writing, citing what's on Newton's page,** and surface the calls to Nir.

### §2.3 — Factual / cosmetic slips.
- **Degrees:** Parent 7's prose says "lemma_7 (degree 5)" and "prop_11 (degree 5)"; the real degrees from the 28 edges are **lemma_7 = 6** and **prop_11 = 4**. (JSON is correct; fix the prose so door-count reasoning is right.)
- **Citation labels** (`"by Lem. VII"`, etc.) are Parent 7's reconstructions — flag which you want DeepSeek to verify against the actual Motte text.
- **Plate/figure numbers** ("Plate 1, Fig. 6") are tentative guesses — confirmed downstream by overlay-diff.

### §2.4 — The data-contract reality (Parent 7 ignored it).
The real `raw_models.py` makes **`StepPair.drawing` mandatory** — every step (station) must carry a "drawing" block. That fits the model: every station's panel is a **figure**, an **equation**, or a **key foundational statement/illustration** (never inert prose — only mathematical, foundational, or intuition-giving content is built; meaningless filler is skipped, §2.2). **You design how a non-geometry panel is represented** (most likely: a **colored LaTeX image** — the equation, or the foundational statement with its key concepts colored — with `\textcolor` + Stabilo, much like the text panels / ceiling equations already bake; so such a station may need **no recipe/.asy**, just colored-LaTeX artifacts). **DeepSeek will make whatever contract/code change you specify** — but it must be a *decided, surfaced* design, not an accident.

---

## §3 — THE CORRECTED COLOR MODEL (replaces everything Parent 7 wrote about color)

**No global palette, no fixed group names.** Two mechanisms, both **local to one station** (= one step-pair = a "figure" panel + its paired text panel):

**(1) Matching colors (word ↔ thing).** Within a station, the important elements each get their **own distinct local color**, and **the same words in the paired text carry the same color** (`\textcolor{name}{...}`). Colors are **local** (same concept may differ or be uncolored elsewhere). Unimportant ink = **black** (light bg) / **white** (dark bg) — **never grey.**

**(2) Stabilo heart.** Only the **current step's heart(s)** get a bright translucent marker (yellow/green/orange/pink/cyan), fresh per step, **never cumulative.**

Data shape (in `raw_models.py`, proven by lemma_2): `draw.local_color {name,hex}|null`, `draw.step`, `draw.is_heart`; `TextBlock.colors_used`; figure's `colors_used` = union. Ask DeepSeek for the lemma_2 **recipe + room_source + .asy** — the gold reference for the corrected model end to end.

---

## §4 — ⭐ WHAT GOES IN THE GAME: MATH + ITS FOUNDATIONS (the 2026-06-30 decisions)

Quake includes **two things, treated identically:**
1. **The math** — geometric constructions and equations / quantitative relationships.
2. **The key non-math foundations the math rests on** — the physical (or, in other books, chemical / biological) facts, processes, and ideas that give the math its **intuition, meaning, and significance**, or that help you understand it (e.g. for inertia: the spinning top, the planets, the projectile).

**Excluded:** only meaningless filler — biography, history-about-the-author, rhetoric or narrative with no intuitive or foundational value. (The test: does it help you *understand or feel* the result? Include it. Is it just history/trivia? Skip it.) **Never implant modern math the book didn't contain** — it would make every other room feel fabricated.

**Everything included is colored the same way** (this is the heart of Quake):
- The **panel** is a **figure**, an **equation**, or a **key statement / illustration**. Color its important elements (shapes, terms/symbols, or key concepts), each its own distinct local color.
- The **paired explanation panel** colors the **matching words** the same local color (word ↔ thing — whether the "thing" is a shape, a symbol, or an idea).
- **Explanation source:** the book's own prose if it exists; **if the text gives none, write one in simple words with minimal math — to EXPLAIN the meaning, never to merely repeat it.**
- The **Stabilo heart** highlights only the current step's key element; never cumulative.

**Example (a math station) — Prop. IV, F ∝ v²/r:** color `v²` blue, `r` green, `F` orange; in the explanation, "the square of the speed" is blue (↔ v²), "the distance from the centre" green (↔ r), "the pull toward the centre" orange (↔ F).

**Example (a foundation station) — `law_1`, inertia:** the spinning-top illustration is a panel; color "keeps spinning" one color and "until friction from the table slows it" another; the explanation colors the matching words the same. The top, the planets, and the projectile are each such a panel — they give the intuition for the First Law.

**Consequence:** every room has colored things to look at and shoot — figures, equations, and/or foundational illustrations. `law_1` (inertia) and `law_2` are real rooms, **not dropped.**

---

## §5 — YOUR DELIVERABLE

A **corrected + completed** level design that supersedes only Parent 7's deficient parts:

1. **A station map for the whole level, at the station level (not the room level):** for each node, list its stations — each a **geometry** construction, an **equation/relationship**, or a **key foundational illustration** (the intuition the math rests on, §4) — and list what **meaningless filler** (history/trivia) you skipped. No node is dropped for lacking equations: e.g. `law_1` (inertia) is a real room built from the First Law + the top/planets/projectile. **Justify each station and each skip against the actual Newton page.**
2. For each **diagram room:** a corrected figure plan (step count, per-step gloss, and the **local matching colors + per-step heart** in the §3 model).
3. For each **equation room:** which equation(s) are the "figure," the **colored important terms**, the **explanation** (Newton's prose, or your simple-words version if none), the **matching-colored words**, and the per-step heart.
4. **Corrected color design** (drop the global palette/groups; local per station).
5. **The fixed prose facts** (degrees) + a list of citation labels / plate numbers you want DeepSeek to verify.
6. **Your decided data representation** for a non-geometry panel (a colored-LaTeX equation **or** a colored foundational statement/illustration, §2.4) — so DeepSeek can make the matching contract/code change.
7. Any **build-order / acceptance-gate** tweaks your changes require.

Keep Parent 7's concept-graph topology + room set. Deliver in **prose or fenced code blocks — never Markdown tables** (they die on copy-paste).

---

## §6 — HOW YOU GET INFORMATION (no internet / no files)

**Ask DeepSeek precise questions** (batched welcome); DeepSeek pastes back **exact verbatim** excerpts — the real Principia text for any lemma/prop (so you can make the diagram-vs-equation call and quote/explain the math), the lemma_2 gold files, any `raw_models.py` section, Parent 7's full text, etc. There is a **DIGESTED PRINCIPIA** (one sentence per result) and the **full Section I–III + Laws Motte text** on disk — ask by name. Burn DeepSeek's effort to protect your context; never ask for "the whole Bible."

---

## §7 — TALK FIRST, THEN BUILD (no "GO")

First **state your plan** for completing/correcting Parent 7's design and ask your batched questions — especially **which rooms' Newton text you need** to make the diagram-vs-equation call. **Wait** for DeepSeek's answers and Nir's confirmation. Then deliver.

Welcome, Parent 15. Complete the job Parent 7 left unfinished, leave nothing buried, and give Nir back a level where **every** room has something colored to look at and shoot — a figure, an equation, or the idea that gives it meaning. 🔥📖🗝️
