# PROMPT TO OPUS 4.8 (alone) — design the TWO LEGS, as the New Testament (Layer 2)

Opus — it's Nir. You just produced my Master Design Document for the geometry-rich 3D game (working title "Two Minds, One Proof"). You're no longer in Fusion mode — it's just you now, alone, and you can't consult the other models. I need you to think **really long and hard** and do one focused, critical thing for me.

## Why I'm writing — the real worry

Reading your doctrine back, I am **not** worried about the parts you treated as ordinary engineering — a solid room in OpenGL, a transparent wireframe corridor, the camera, packaging. I believe those will be fine. What I AM deeply worried about is this: **you decided NOT to start from the two tools/processes that the entire game literally stands on.** You parked both of them as "[GAP]" + "an AI will do it" + "a module to be written later." But without them **there is no corridor and there are no walls** — there is no game at all. They are the only genuinely hard, unprecedented part of this project, and they are the **two legs** the whole thing balances on. I need you to design them **properly, now, while it's all fresh in your mind.**

## THE TWO LEGS

- **LEG 1 — THE MAP.** The tool + process that turns a geometry-rich book's **outline of subjects into the concept graph** (the nodes, and the dependency edges between them), and then lays that graph out **force-directed with the 3D crossing-heights** (bridges/underpasses). Without this there are no corridors — there is no level.
- **LEG 2 — THE WALLS.** The tool + process that turns the book's **original scanned figures into reproducible, colorable, highlightable, step-by-step geometric drawings**, baked to the off/on PNGs the room walls show. Without this the rooms are empty.

## My hard constraint (it governs BOTH legs — never forget it)

I do not know how to code, and I do not know any mathematics, **at all.** Every part that requires *understanding* — reading the book outline, deciding which idea depends on which, reading a scanned figure, knowing what it depicts, getting the construction right — must be done **by AI** (the frontier models in OpenRouter, i.e. you and your siblings). My role is **purely mechanical**: copy-paste between chats, fetch PNG scans (e.g. from Archive.org), run scripts my coding agent (DeepSeek) writes, install software, and **eyeball whether two pictures match and describe the differences in plain words.** Never design anything that requires me to understand a proof or to draw / construct / trace a figure myself. If your answer ever amounts to "Nir thinks about the figure and recreates it," it is wrong and useless to me.

## My decisions — these AMEND your doctrine's §6. Treat them as locked.

1. **GEOMETRY TOOL = Asymptote, from the very start — NOT a fallback.** I reject building our own geometry kernel: that is just re-implementing Asymptote, it is out of scope, and we will not take on rebuilding a whole professional tool that expert people already made. Asymptote already computes exact geometry and handles **conics** (which we need for Newton's ellipses, parabolas, hyperbolas). Design Leg 2 around Asymptote as the **primary and only** geometry tool. (If you genuinely believe a *different finished, professional, AI-usable* tool beats Asymptote here, you may argue for it — but the rule is absolute: use an existing finished tool, never build one ourselves.)

2. **VERIFICATION = a human-driven visual overlay/diff tool — NOT "another AI checks it."** Here is the process I want; design it precisely and make it the heart of Leg 2's correctness:
   - The AI draws the figure (Asymptote → rendered image) — call it one transparency. My scanned book page (PNG) is the other transparency. A small program shows them **one over the other** so I can SEE the differences.
   - Concretely: paint the back image's ink **white** and the front image's ink **black**; wherever the black does NOT cover the white, the white **shines through** = a mismatch I can see.
   - Let me **thicken the black** (a tolerance knob, so tiny near-misses don't all light up), **pan / resize / rotate** each image independently to line them up, and **flip** which image is front and which is back (so I catch mismatches in both directions).
   - Then I describe the differences **in plain words** ("the curved line above the letter A, on the left, isn't connected to point B"), the AI regenerates the Asymptote, and we **iterate until it's more or less right.** This needs **zero math** from me.
   - This also defines our standard of correctness honestly: we are **faithfully reproducing the book's printed figure**, which my eyes can verify — not re-deriving the proof, which I can't.

3. **HIGHLIGHTING, not partial drawing.** Each proof step is shown by drawing the **WHOLE figure** and **HIGHLIGHTING just that step's elements** — like a Stabilo highlighter (any color the step needs) — NOT by drawing only the subset for that step. Reason: if we got a detail wrong, the **full figure is still visible** and the player repairs it in their own head. These highlighted versions are still **BAKED IN ADVANCE at design time** — so yes, still many renders (one per step's highlight), but each is **simpler** than a from-scratch cumulative re-derivation. This reconciles with the shoot-to-reveal mechanic: **off** = the full figure in grey; **on** = the full figure with this step's elements highlighted.

## The open question I specifically need you to solve (Leg 2)

**What actually does the highlighting?** Can **Asymptote itself** cleanly produce the per-step highlighted versions of the figure? Or is it better to render the base illustration **once** and then **composite a separate per-step highlight layer over it** (a highlight image combined with the illustration image)? Or do you have a better idea entirely? **Decide and specify the exact mechanism**, including how it bakes to the off/on PNGs.

## What I want you to PRODUCE

Write a **Layer-2 document — a "New Testament"** to sit beside the master doctrine. Do **not** re-cover the conventional engine. Focus **entirely and deeply on the two legs.** For **EACH leg** give me:

1. **The holistic, end-to-end design of the tool + process** — inputs, every step, every artifact produced, and clearly which steps are automated vs. which are a mechanical action I personally take.
2. **My exact mechanical role at each step** — what I copy-paste, what I fetch, what I run, what I look at, and what I describe.
3. **How correctness is achieved and verified WITHOUT me knowing math** — concretely. (Leg 2: the overlay-diff loop above. Leg 1: how an AI extracts the dependency graph and how a wrong graph is caught when I can't read the math.)
4. **The child briefs** — exactly what to ask the fresh child-AI chats that will build each piece, to your frozen-contract standard (modules, typed contracts, tests). DeepSeek will integrate their code.
5. **The data the leg emits and how it feeds the rest of the doctrine** — `concept_graph.json` for Leg 1; the baked figure PNGs + manifest for Leg 2.

### Deep questions — LEG 1 (the map)
- How does an AI turn a real book's outline / table of contents / propositions into the **correct dependency graph** (which idea depends on which)? What exactly do I paste to it, and how does it determine the dependencies — from the book's own cross-references ("by Lemma I…"), from structure, from its own understanding?
- **How do we catch a WRONG graph when I can't read the math?** (A review pass? Cross-checking the book's explicit internal citations? Showing me the graph as a picture so I can sanity-check its shape, not its content?)
- The deterministic **force-directed layout + 3D crossing-height assignment** — confirm/refine your §8.1, name the tool (networkx?), and tell me exactly what I run.
- Failure modes, and how I recover from them mechanically.

### Deep questions — LEG 2 (the walls)
- The **full Asymptote pipeline**, every step and artifact: scan PNG → (AI reads it) → Asymptote source → render → overlay-diff vs. the scan → I describe mismatches → AI fixes → iterate → bake.
- The **highlighting mechanism** (the open question above).
- How the per-step highlighted figures **and** their paired **full-LaTeX explanation text** get baked to **off/on PNGs** (connect this to the baker).
- The Asymptote **"medium AI fluency" risk** — how do we minimize compile/iteration pain mechanically (e.g. a compile-and-return-the-errors script my coding agent writes, fed straight back to the AI)?
- **Conics and Newton's limiting / "ultimate ratio" figures** — does Asymptote cover them, and how?

## How to work

You are **alone now** — no Fusion, no siblings to lean on. So think genuinely, long, and hard, and rely on your own judgment. Honesty rules still hold: never invent a fact; mark genuine unknowns honestly — **but do NOT use "[GAP]" to wave away the hard core. These two legs ARE the hard core. Solve them; do not defer them.** Ask me only the **few load-bearing questions** you truly need. If you've lost any of the master doctrine from your context, **tell me and I'll paste it back** rather than guessing.

Take your time. This New Testament — the design of the two legs — is the single most important thing you will write for this project. Thank you.
