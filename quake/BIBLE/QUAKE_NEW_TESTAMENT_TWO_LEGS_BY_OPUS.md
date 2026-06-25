🗝️ QUAKE (Game 3) — NEW TESTAMENT (Layer 2): THE TWO LEGS

Captured June 25, 2026, at Nir's request, VERBATIM / word-for-word, AS-IS. This is Parent 1 of Quake — Claude Opus 4.8, run ALONE (not Fusion), at "XHigh" reasoning effort (one below MAX) — answering the prompt in `quake/BIBLE/PROMPT_TO_OPUS_THE_TWO_LEGS.md`. It is the Layer-2 companion to the Old Testament (`quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md`). Nothing below is edited. (The chat showed "Claude Opus 4.8 / Reasoning" above it.)

--- BEGIN VERBATIM ---

NEW TESTAMENT — THE TWO LEGS
A Layer-2 companion to Two Minds, One Proof

Nir — I've lost nothing from the master doctrine; I have it. This document does not re-touch the engine. It designs the only two things that are genuinely hard and genuinely unprecedented: the MAP (book → concept graph → laid-out corridors) and the WALLS (scanned figure → reproducible, highlightable, baked panels). I treat your three amendments as locked law: Asymptote is primary and only; verification is your eyes over a human-driven overlay tool; and we highlight the whole figure, never draw subsets.

I have one truly load-bearing question (Leg 1). I've designed the document so it's complete either way — you can build from it before answering — but your answer changes how easy Leg 1 is. It's at the very end.

A single principle governs both legs and I want it stated before anything else, because it's the thing that makes this buildable by someone who knows no math:

> Our standard of correctness is FIDELITY TO THE PRINTED PAGE, not mathematical truth. We are not re-deriving Newton. We are faithfully reproducing the figure the book actually printed and the dependencies the book actually stated. Both of those are things your eyes can check (a picture matches a picture; a citation phrase is present or absent) — and neither requires you to understand a proof. Every verification step below is built to exploit this.

LEG 1 — THE MAP

What it is: the tool + process that turns a geometry-rich book's structure into concept_graph.json (nodes + dependency edges + importance), then lays it out force-directed with 3D crossing-heights so corridors become bridges and underpasses.

The core idea that makes it safe for a non-mathematician: in a classical deductive text, the author already wrote the dependency graph for you, in plain words, inside the proofs. Newton writes "by Lem. I," "by Cor. 2. Prop. IV," "as was shown above." Those phrases are the edges. We are not asking an AI for its opinion about what depends on what — we are asking it to transcribe the citations the book printed, and then a dumb, auditable script turns those citations into edges. The intelligence of the dependency structure comes from Newton, not from the AI and not from you.

1.1 The pipeline, end to end

```
book section
   │
   ▼
[A] STRUCTURE PASS  — AI reads TOC + section headers → the list of nodes (numbered items)
   │  artifact: nodes_raw.json
   ▼
[B] CITATION PASS   — AI transcribes, per node, the verbatim cross-reference phrases in its proof text
   │  artifact: citations_raw.json   (each entry carries the exact quoted snippet)
   ▼
[C] MERGE (script)  — deterministic: phrases → normalized target ids → edges; in-degree → importance
   │  artifact: concept_graph.json   +  provenance_report.html
   ▼
[D] SANITY RENDER (script) — draw the graph as a flat labelled picture + run the math-free red-flag checks
   │  artifact: graph_preview.png  +  flags.txt
   ▼
[E] YOU LOOK  — eyeball the shape & read the provenance/flags in plain English; fix misses by re-pasting a page
   │  (loop B–E until the flags are clean and the picture looks sane)
   ▼
[F] LAYOUT (script) — networkx force-directed → crossing detection → height assignment
      artifact: floorplan.json   → feeds the doctrine's level_maker / corridors
```

Steps A and B are AI (they require reading). Steps C, D, F are deterministic scripts DeepSeek writes. Step E is you, looking and describing.

1.2 What you actually do (your mechanical role)

    Fetch the section's page scans (Archive.org) into a folder. (If you can get clean text instead — see the final question — you paste text instead of images and B becomes far more reliable.)
    Structure pass (A): open a fresh AI chat, paste the table of contents / section headers (image or text) + the fixed STRUCTURE prompt (below). Copy its JSON reply into nodes_raw.json.
    Citation pass (B): for each page (or batch), open a fresh chat, paste the page image + the fixed CITATION prompt. It returns, per numbered item on that page, the verbatim citation phrases it sees and a one-sentence plain summary. Append the replies into citations_raw.json.
    Run merge (C): python -m map.merge → produces concept_graph.json + provenance_report.html.
    Run sanity (D): python -m map.sanity → produces graph_preview.png + flags.txt.
    Look (E): open graph_preview.png and flags.txt. You are checking shape and bookkeeping, never math:
        Does the numbering run unbroken? (flags.txt literally says "expected Lemma I–XI, found I–X, MISSING: VII".)
        Any cycles? (In a deductive text a dependency cycle is almost always an extraction error — flagged in plain English.)
        Any orphan nodes (no edges at all) or two disconnected islands?
        Open provenance_report.html: every edge is a row — "prop_1 → lemma_2 — because prop_1's text says: ‹…by Lem. II…› (p.41)." If a row's quoted snippet is empty or doesn't contain a citation phrase, that edge is suspect.
    Fix mechanically: for any missing item or suspicious edge, re-paste just that page to a fresh chat with a targeted prompt ("transcribe every cross-reference phrase in the proof of Lemma VII, verbatim"), drop the reply into citations_raw.json, re-run C–D.
    Run layout (F): python -m map.level_maker --level principia_bk1_sec1. Done — you now have corridors.

STRUCTURE prompt:

> You are reading the structure of a classical mathematics text. From the material I paste (table of contents / section headers / page images), list every numbered or named result in order: lemmas, propositions, theorems, corollaries, definitions, laws. Output ONLY JSON, an array of objects: {"local_label": "<exactly as printed, e.g. 'Lemma VII'>", "kind": "<lemma|proposition|corollary|definition|law|...>", "pages": ["<printed page label>"], "summary": "<one plain-English sentence, no mathematics required to read it>"}. Do not invent items you cannot see. Do not skip items. Preserve printed order.

CITATION prompt:

> Here is a scanned page (or text) from a classical mathematics proof. For each numbered/named result whose statement or proof appears on this page, transcribe — VERBATIM, exactly as printed — every internal cross-reference phrase it makes to another result (e.g. "by Lem. I", "per Cor. 2. Prop. IV", "by Prop. XI of this Book", "as above"). Output ONLY JSON: an array of {"local_label": "<the result doing the citing>", "citations": [{"phrase": "<verbatim>", "page_seen": "<printed page>"}], "summary": "<one plain sentence>"}. If a phrase is vague ("as shown above"), copy it verbatim and set "vague": true. Transcribe; do not interpret the mathematics.

Note what the CITATION prompt does not ask: it never asks the AI "what does this depend on?" It asks only "what citation phrases are printed here?" That's transcription, which AIs do far more reliably than judgment, and which you can verify by eye against the scan.

1.3 How a WRONG graph is caught — without you reading math

This is the heart of Leg 1's correctness. Four independent, math-free safety nets, in increasing strength:

    Provenance, not assertion. Every edge carries the verbatim quoted phrase and page that produced it. The merge script does not create an edge unless a citation phrase normalized to a real target. So an edge can't be a pure hallucination — it has a paper trail you can read in English. A hallucinated edge shows up as a row whose snippet doesn't actually contain a citation → you delete it, no math needed.

    Numbering-continuity check (mechanical). Classical texts number their results. The script knows "Lemma I, II, III…" should be contiguous. A gap means a missed node (OCR skipped it), reported in plain English. This catches the most common extraction failure with zero understanding.

    Cycle + connectivity checks (mechanical). A deductive text is a DAG — Lemma I cannot depend on Prop X that depends back on Lemma I. Any cycle is a near-certain extraction error and is reported as "suspicious cycle: lemma_3 → prop_2 → lemma_3 — likely a misread citation; check these pages." Likewise orphans and disconnected islands are flagged (an island usually means a section-bridging citation was missed).

    Two-method disagreement (the strong net). Run the citation extractor (B, transcription) and, separately, ask a fresh AI for its understanding-based dependency list (a different prompt: "which earlier results does this proof rely on?"). The script diffs the two. Agreement = high confidence. Disagreement is exactly where errors hide, and the disagreements are presented to you as a short English list: "Citation pass says prop_5 depends on lemma_2; understanding pass also says lemma_9. Page 47 — does the proof cite Lemma IX?" You don't adjudicate with math — you paste page 47 to a fresh chat and ask "is the phrase 'Lem. IX' printed anywhere in this proof? yes/no, quote it." Yes/no transcription, your eyes confirm the quote against the scan.

Net effect: you can be confident in a graph you cannot mathematically understand, because (a) its edges are Newton's own stated citations, (b) the bookkeeping is machine-checked, and (c) the only thing left for you is to confirm that a short printed phrase is or isn't on a page — pure perception.

    Honest limit: for a less explicit book (Needham cites less formally than Newton), nets 1 and 4 weaken — more edges will be "inferred, not cited." The design handles this by tagging every edge with provenance: "cited" | "inferred" and showing inferred edges in a distinct color in graph_preview.png, so you know exactly which edges rest on AI judgment and can get a second opinion on those. Principia (Pack 1) is the easy case — it is almost pathologically explicit about citations. We are starting on the friendliest possible book. State this and take the win.

1.4 Importance (1–5) without math

importance drives room size and color. Assign it from two mechanical-ish signals, no math required:

    Citation in-degree — how many other results cite this one. The most-depended-upon results are objectively central. This is a pure count from the graph.
    An AI "centrality hint" (1–5) from the STRUCTURE pass summary, as a tiebreaker/blend.

Map the blended score to 1–5 by quantiles. The lovely consequence: the lemma that everything leans on becomes the biggest, warmest room — the map's shape tells the truth about the book. You sanity-check this in the picture: the giant warm node should be a thing with many arrows into it. If a leaf node is huge, something's wrong — and that's visible, not mathematical.

1.5 Layout + 3D crossing-heights (confirming/refining doctrine §8.1)

Tool: networkx for the force-directed placement (spring_layout, Fruchterman–Reingold), deterministic by seed. All crossing/height logic is our own deterministic code over networkx's output.

Algorithm (restated crisply):

    Canonicalize node and edge order (sort by id) before layout, so the result doesn't depend on dict ordering.
    spring_layout(seed=…) → 2D positions; scale to world units. Importance styles nodes (size/color); it does not move them.
    Detect crossings: for every pair of edges, 2D segment-intersection test, ignoring shared endpoints and intersections too near a node (try a small deterministic dogleg there; else fail loud with the offending ids).
    Conflict graph H: one vertex per corridor; connect two corridors that cross.
    Height layers by deterministic greedy coloring of H — process corridors in fixed order (weight desc, source id, target id); give each the lowest layer unused by an already-placed crossing-neighbour. Layer → world height y=base+layer⋅Δy. The higher corridor ramps over the lower at each crossing.
    Caps: warn above ~7 layers, fail above ~12 → prompts a re-seed.

The determinism caveat, handled honestly: spring_layout is not guaranteed bit-identical across NumPy/BLAS versions or machines. So we lay out once on the build machine and ship the resulting floorplan.json as the source of truth. We never re-run the force layout on a player's machine. This sidesteps the reproducibility hole entirely. (This matches the master doctrine; I'm reaffirming it because it's the thing most likely to bite later.)

What you run: one command — python -m map.level_maker --level principia_bk1_sec1. It reads concept_graph.json, does 1–6, writes floorplan.json. If it fails a cap, it prints exactly what to change (re-seed N, or widen scale).

1.6 Data Leg 1 emits (and how it feeds the doctrine)

concept_graph.json is the doctrine's Layer 1 schema, plus a provenance sidecar that is not shipped (build-world only):

```
// concept_graph.json  (Layer 1 — feeds level_maker)
{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "title": "Book I, Section I — First and Last Ratios",
  "edition": "<free-text citation string>",
  "seed": 1729001,
  "nodes": [
    {"id":"lemma_1","name":"Lemma I","kind":"lemma","importance":5,
     "pages":["41"],"summary":"Quantities tending to equality become ultimately equal.","tags":["limits"]}
  ],
  "edges": [
    {"id":"edge.prop_1.to.lemma_2","source":"prop_1","target":"lemma_2",
     "kind":"depends_on","weight":1.0,"label":"by Lem. II"}
  ]
}

// provenance.json  (BUILD-WORLD ONLY — never shipped; powers the report & your audit)
{
  "edges": [
    {"edge_id":"edge.prop_1.to.lemma_2","provenance":"cited",
     "snippet":"… which is manifest by Lem. II …","page_seen":"43",
     "agreement":"both"}   // "both" | "citation_only" | "inference_only"
  ],
  "flags": ["MISSING_ITEM: Lemma VII expected, not found",
            "CYCLE: lemma_3 -> prop_2 -> lemma_3"]
}
```

floorplan.json then feeds the doctrine's level_maker/corridor renderer exactly as already specified. Leg 1's output is the input the rest of the doctrine already expects.

1.7 Child briefs — Leg 1

Each is one single-file module, frozen typed contract, headless-testable with fixtures (no AI, no network inside the modules — the AI lives only in your copy-paste steps).

    map/raw_models.py — pydantic models for nodes_raw.json, citations_raw.json (the AI replies), plus the Layer-1 + provenance models. Frozen: the classes. Brief: "Define these pydantic models exactly; validate schema_version; reject unknown fields loudly. Tests: round-trip sample fixtures."
    map/citation_normalize.py — Frozen: normalize(phrase: str, label_index: LabelIndex) -> NodeId | None. Turns "Cor. 2. Prop. IV" → prop_4 (and records the corollary as a tag). Brief: "Pure function. Given a verbatim citation phrase and an index of known printed labels, return the target node id or None. Handle Roman numerals, abbreviations (Lem./Prop./Cor./Def.), 'of this Book', 'above'. Tests: a table of ~40 real Principia-style phrases → expected ids; vague phrases → None with vague flag."
    map/merge.py — Frozen: merge(nodes_raw, citations_raw_citation, citations_raw_inference) -> (ConceptGraph, Provenance). Brief: "Deterministic. Build nodes; build edges via citation_normalize; attach provenance + agreement; compute in-degree; assign importance by quantile blend; NO graph mutation beyond this. Tests: fixture in → exact graph out."
    map/sanity.py — Frozen: check(graph) -> Flags and render_preview(graph, out_png). Brief: "check runs numbering-continuity, cycle detection (DAG check), orphan + connected-components checks; returns plain-English flag strings. render_preview draws the graph (networkx+matplotlib) with node size/color = importance, inferred edges dashed, and writes a labelled PNG. Tests: a graph with a planted cycle/gap/orphan yields the expected flags."
    map/level_maker.py + map/layout_force.py + map/layout_height.py — as in doctrine §8.1; Frozen: build_floorplan(graph, seed, cfg) -> Floorplan, place_nodes(...), detect_crossings(...), assign_heights(...). Brief: "Deterministic given seed. Implement FR via networkx; greedy-color the crossing conflict graph; emit floorplan with cruise heights + ramps. Tests: golden 4-node graph with one crossing → stable floorplan; assert the two crossing corridors get different heights."

LEG 2 — THE WALLS

What it is: scan PNG → Asymptote source (AI-written) → render → you verify with the overlay tool → AI fixes → iterate → bake the off/on, per-step highlighted PNGs the room walls show, plus the paired full-LaTeX explanation panels.

I'll answer your open question first, because it shapes everything.

2.1 THE OPEN QUESTION, DECIDED: who does the highlighting?

    Decision: Asymptote does the highlighting itself, from a single source, parameterized by step. We do NOT composite a separate highlight layer.

Here's the reasoning, because it's not arbitrary:

A composite approach (render the base once, then overlay a per-step highlight image) sounds modular but is a trap: to know where step-k's elements are, you must render them from the same geometry anyway — so the highlight layer also comes from Asymptote. Compositing then only adds a registration problem (two images that must align to the sub-pixel) for zero benefit. Whereas a single Asymptote source renders the full figure with step-k "hot" in one pass, one coordinate system — the highlight is registered to the ink exactly and for free, and "off" (all grey) and every "on_k" provably share the same canvas, scale, and position because they're the same source with one integer flipped.

The mechanism (the "Stabilo" effect), concretely:

    The figure source registers every drawable element with a (name, color-group, step) tag.
    A render is invoked with a command-line parameter selecting the hot step: asy -u "highlight=3" ….
    The draw routine renders in three ordered passes so the highlight sits under the ink like a real marker:
        Underlay pass: for hot elements (step == highlight), stroke a fat, semi-transparent pen in the group's highlight color (color + opacity(0.4) + linewidth(7pt)).
        Ink pass: stroke every element's geometry — hot elements in saturated ink, all others in neutral grey.
        Label pass: labels follow the same hot/grey rule.
    off = render with highlight = -1 → the entire figure in grey, no marker. on_k = render with highlight = k → whole figure grey except step k's elements wearing the highlighter.

This is exactly your amendment #3: the whole figure is always present; we only change what's lit. If a detail is slightly wrong, the player still sees the complete picture and repairs it mentally. And because off is identical for every step of a figure, the baker renders it once and dedups.

Asymptote can do all of this — opacity pens, line widths, draw order, command-line parameters (-u), and per-element pens are core features. I'm confident about these capabilities.

This helper computes no geometry — Asymptote's geometry module does all of that. prooffig.asy is a ~50-line registration + draw convention so that every figure the EMITTER AI writes is uniform and the baker can parameterize highlighting generically. It is the contract that makes baking possible; it is not a geometry engine and is squarely in scope.

```
// prooffig.asy  — registration & draw convention (NO geometry computed here)
import geometry;
access "palette.asy" as pal;     // generated: pen hi(string g), ink(string g), greyInk

struct Elem { path p; string group; int step; bool isLabel; string tex; pair at; align a; }
Elem[] ELEMS;

void elem(path p, string group, int step) {
  Elem e; e.p=p; e.group=group; e.step=step; e.isLabel=false; ELEMS.push(e);
}
void lbl(string tex, pair at, string group, int step, align a=NoAlign) {
  Elem e; e.tex=tex; e.at=at; e.group=group; e.step=step; e.isLabel=true; e.a=a; ELEMS.push(e);
}

void drawAll(picture pic=currentpicture, int highlight) {
  for (Elem e : ELEMS)                                   // 1. Stabilo underlay
    if (!e.isLabel && e.step==highlight)
      draw(pic, e.p, pal.hi(e.group)+opacity(0.40)+linewidth(7pt)+squarecap);
  for (Elem e : ELEMS)                                   // 2. ink
    if (!e.isLabel)
      draw(pic, e.p, (e.step==highlight? pal.ink(e.group)+linewidth(1.4pt)
                                       : pal.greyInk+linewidth(1.0pt)));
  for (Elem e : ELEMS)                                   // 3. labels
    if (e.isLabel)
      label(pic, e.tex, e.at, e.a, (e.step==highlight? pal.ink(e.group): pal.greyInk));
}
```

And a figure file the EMITTER produces against it (illustrative — exact geometry API names are taken from the pinned docs, see §2.5, not from my memory):

```
import prooffig;
// ---- construction: exact geometry computed by Asymptote ----
point A=(0,0), B=(3,0), C=(1.2,2.1);
circle arc = circle(A, abs(B-A));     // centre A, through B
line  bc  = line(B, C);
point D   = intersectionpoint(arc, bc);   // Asymptote computes the real point
// ---- registration: tag every element with (group, step) ----
elem(segment(A,B), "base_line", 1);
elem((path)arc,    "limit_arc", 2);
elem(segment(B,D), "secant",    3);
lbl("$A$", A+(-0.25,-0.2), "base_line", 1);
lbl("$D$", D+( 0.2, 0.15), "secant",    3);
// ---- render (highlight overridden on the command line) ----
int highlight=-1;
drawAll(highlight);
```

2.2 The full Asymptote pipeline, end to end

```
page scan (you fetch)
   │  [you crop the figure region]              → fig_crop.png
   ▼
[R] READER AI  — reads fig_crop.png + the figure's caption/surrounding text
   │  emits: construction recipe (plain words) + element→step map + element→color-group map
   │           + rough anchor coordinates for the free points
   │  artifact: recipe.txt  (you copy)
   ▼
[E] EMITTER AI — recipe + pinned geometry docs + prooffig contract + golden examples
   │  emits: figure.asy
   │  artifact: figure.asy  (you save)
   ▼
[K] COMPILE (script asy_compile)  — runs asy; on error returns the EXACT error text
   │  if error → paste error to EMITTER → new figure.asy → repeat   (mechanical loop)
   │  on success → a neutral render for diffing                      → render.png
   ▼
[V] OVERLAY-DIFF (your GUI tool)  — fig_crop.png vs render.png; align, thicken, flip, look
   │  you describe mismatches in plain words
   │  → paste to EMITTER → new figure.asy → [K] → [V]   (iterate to "more or less right")
   ▼
[B] BAKE (script baker_figure)  — render off + on_1..on_N → trim → transparent PNGs + manifest
        also: baker_text bakes the paired full-LaTeX explanation panels (off grey / on colored)
        → feeds room_maker / wall rendering
```

READER and EMITTER are AI (they read and write code). COMPILE, BAKE are scripts. OVERLAY-DIFF is you, looking.

2.3 The OVERLAY-DIFF tool — the heart of correctness (your amendment #2, specified)

This is the single most important build-time tool in the project, because it's the mechanism by which a non-mathematician guarantees fidelity. Specify it precisely.

Framework decision: Tkinter + Pillow + NumPy. Tkinter ships with Python (zero install); Pillow does the per-layer affine transforms; NumPy does the white/black/dilate compositing; it's a tiny, robust desktop utility. (If real-time rotation ever feels sluggish on large images we can move it to the pyglet/moderngl stack, but for figure-sized images Tkinter is plenty. This is a build tool — it never ships.)

What it shows and how the "white shines through" works:

    Load back image and front image (default: scan = back, render = front; a Flip button swaps them).
    Render the back layer's ink as WHITE on a neutral mid-grey field; render the front layer's ink as BLACK on top.
    Composite: where front-black sits, it covers the white. Where back-white has no front-black over it → the white shines through = a mismatch (the back has ink the front is missing). Bright white slivers are exactly the errors, and they're impossible to miss.
    Thicken knob (tolerance): a slider that dilates the front (black) ink mask by t pixels before compositing, so near-misses within t px get covered and don't all light up. You raise t until only real structural differences glow.
    Per-layer transform: independent pan / scale / rotate sliders (and mouse drag) for each image, so you can line up a warped, rotated, differently-scaled scan against the clean render.
    Flip: swaps front/back so you catch mismatches in both directions (render-has-extra-ink as well as render-missing-ink).

The crucial reliability consequence — the AI doesn't need absolute coordinates. Because you can pan/scale/rotate each layer independently to align them, the EMITTER only has to get the figure's internal construction logic right (this point is on this line; this arc passes through that intersection). It does not need to match the scan's absolute position, scale, or rotation. This is exactly why "construction, not coordinates" works: Asymptote computes the relative geometry exactly, and the overlay tool absorbs all global placement. Rough anchor coordinates from the READER are fine.

How you describe a mismatch (zero math): the figures carry the book's own letters (A, B, C…), so you point with them: "the curved line above A, on the left, doesn't reach point B," or "there's a white sliver where the long diagonal should cross the circle — the render's line passes inside it." That sentence goes straight to the EMITTER. No equation, no coordinate, no understanding — just describing where two pictures differ. You are doing the one job a sighted person can always do.

Brief to the child: "Build a single-file Tkinter app overlay_diff.py. Frozen entry: run(back_png: Path, front_png: Path) -> None. UI: two file loads; per-layer sliders for translate-x, translate-y, scale, rotation; a global thicken slider (0–12 px); a Flip button; a save composite button. Pipeline per redraw: (1) binarize each layer to an ink mask (dark<threshold → ink; expose the threshold as a slider); (2) apply each layer's affine transform via Pillow; (3) dilate the front mask by thicken px (Pillow MaxFilter/morphology or a NumPy max-pool); (4) compose: mid-grey field, paint back-ink white, paint (dilated) front-ink black over it; (5) show. Pure-image helpers (binarize, transform, dilate, compose) must be separate testable functions with NumPy-array in/out so they test headless; the Tkinter wiring is the only display-needing part and is skipped in CI. Tests: a synthetic back with a line the front lacks → composite has white pixels exactly along that line; with thicken ≥ the gap → those white pixels vanish."

2.4 Baking — off/on, highlighted figures and paired LaTeX text

Two bakers, both build-world, both feeding the doctrine's manifest.

baker_figure:

    Render off once: asy -u "highlight=-1" figure.asy → all-grey full figure.
    For each step k∈{1..N}: asy -u "highlight=k" figure.asy → grey figure with step k in highlighter.
    Each render lands on a flat known background color; Pillow keys that color out to transparency (this is more robust than relying on Asymptote's own transparency handling, which I won't assert details of). Then trim transparent margins, record content bbox + pixel size. Bake a wall-mip and a high-res Read-Mode master.
    Emit manifest entries. Dedup: every step's drawing-off points to the single shared off image.

baker_text (the paired explanation, full LaTeX — the doctrine's text baker): for each step's explanation paragraph, bake off (grey) and on (colored, with the step's concept words wearing the same color groups as the figure highlight). This is where "same concept = same color in figure and prose" is enforced — see §2.6.

The result, per proof step, is the coupled pair the room walls expect:

| | OFF (before you shoot) | ON (after you shoot) |
|---|---|---|
| Drawing panel | full figure, all grey | full figure, this step highlighted |
| Text panel | explanation, grey | explanation, this step's words colored |

Manifest shape (feeds room_maker / render_room unchanged):

```
{ "schema_version":"1.0",
  "block_id":"lemma_1.s3.fig",
  "off_path":"baked/lemma_1/fig_off.png",          // shared across steps
  "on_path":"baked/lemma_1/fig_on_3.png",
  "master_path":"baked/lemma_1/fig_on_3@master.png",
  "px_w":1024,"px_h":712,"content_bbox":[…] }
```

2.5 The "Asymptote medium-fluency" risk — made mechanical, not painful

Asymptote has less training presence than Python or TikZ, so an AI will sometimes write code that won't compile or uses a slightly-wrong function name. We bound this pain with four mechanisms, none requiring you to understand Asymptote:

    asy_compile.py — the error round-trip harness. Runs asy, captures stdout+stderr verbatim, returns a structured result. When it fails, you literally copy its error block back to the EMITTER chat with "this didn't compile, here is the exact error, fix it." Asymptote's errors name the line. This converts "AI is bad at Asymptote" into a tight, dumb loop the AI is excellent at closing.
    Pin the docs, don't trust memory. Your first mechanical task in Leg 2 is to fetch the Asymptote geometry module documentation (it ships with Asymptote and is online) and save it as asy_geometry_reference.txt. The EMITTER is always given this file. This removes the single biggest failure source (wrong API names) — including from my memory, which is why I've refused to assert exact signatures above.
    Few-shot from our own golden figures. Keep 2–3 finished, verified .asy figures in the repo. Paste them into every EMITTER chat as worked examples. The AI pattern-matches our house style far more reliably than it recalls Asymptote from training.
    Constrain the surface to prooffig.asy. The EMITTER only ever calls geometry constructions + our elem/lbl/drawAll. Small, fixed vocabulary = fewer ways to go wrong.

Honest residual: a rare figure may resist — repeated compile failures or stubborn mismatch. The recovery is never "switch geometry tools" and never "Nir draws it." It's: ask the EMITTER for a more elementary construction of the same picture (decompose the hard arc into pieces it can place), and lean on the fact that "more or less right" is the accepted bar — the full figure is always visible, so a slightly imperfect detail is self-repairing for the player. The overlay tool guarantees you always know how close you are.

2.6 Color: one source of truth, figure ↔ text

The doctrine forbids hex in content; colors are named groups. The baker generates both an Asymptote palette and a LaTeX palette from one palette.json:

    palette.asy → pen hi(string g), pen ink(string g), pen greyInk (used by prooffig.asy).
    palette.tex → \definecolor{<group>}{…} macros (used by the text baker).

So "secant = warm-rose" lights the secant in the figure and colors the word secant in the prose with the identical hue, automatically. Re-theming the whole game is editing one file.

2.7 Conics & Newton's "ultimate ratio" figures — does Asymptote cover them?

Conics: yes, and this is a primary reason Asymptote beats a naive approach. The geometry module provides ellipse/parabola/hyperbola as first-class objects, conic-through-points, focus/directrix constructions, tangents to conics, and conic–line / conic–conic intersections — exactly Newton's orbital machinery (ellipses with the sun at a focus, parabolic/hyperbolic trajectories, tangents and chords). The AI describes the conic by its defining construction (foci + a point, or 5 points, or focus+directrix) and Asymptote computes the curve and every intersection exactly.

Ultimate-ratio / limiting figures: yes — because the book prints a finite representative, and so do we. Newton's "first and last ratios" diagrams don't render an actual infinity; they show, e.g., a chord approaching a tangent, or inscribed/circumscribed rectangles at some finite subdivision. Asymptote draws these as ordinary constructions — a loop over n subdivisions emitting n rectangles/segments, or a chord drawn to a point chosen near the limit. There is no infinite object to reproduce; the limit lives in Newton's prose (the paired text panel), and the figure shows the same finite stage the book engraved. This is honest and important: we reproduce the printed engraving, not a mathematical limit — which is exactly the fidelity standard, and exactly what your eyes can verify in the overlay tool.

I'm confident about Asymptote's capabilities (conics, intersections, tangents, opacity, draw order, -u parameters). I am not going to assert exact function signatures from memory — that's precisely the kind of invented fact you told me to avoid. The mitigation is structural and already in the pipeline: the pinned asy_geometry_reference.txt (§2.5 #2) means the EMITTER writes against the real, current API, and asy_compile catches any slip immediately. So the uncertainty about exact names never reaches you — it's absorbed by the compile loop.

2.8 Child briefs — Leg 2

    bake/asy_compile.py — Frozen: compile(src: Path, out_stem: Path, params: dict[str,str]) -> AsyResult where AsyResult = {ok: bool, outputs: list[Path], stderr: str, stdout: str}. Brief: "Invoke the asy binary with -u 'k=v' params and the chosen output format/DPI (confirm exact flags from the Asymptote docs file, do not hardcode guesses). Capture stdout+stderr verbatim. Never raise on a LaTeX/Asy error — return ok=False with the text. Tests: monkeypatch the subprocess; assert params are passed and a non-zero exit becomes ok=False with stderr preserved."
    bake/palette_gen.py — Frozen: gen(palette_json: Path, out_asy: Path, out_tex: Path) -> None. Brief: "Read named groups → hex; emit palette.asy (hi/ink/greyInk pens) and palette.tex (\definecolor). Tests: a 3-group palette produces both files with matching colors; greyInk present."
    bake/prooffig_check.py — Frozen: lint(figure_asy: Path) -> list[str]. Brief: "Static, text-level lint of a figure source: every elem/lbl has a group present in the palette and an int step; steps are contiguous from 1; drawAll(highlight) present; highlight is a -u parameter. Math-free. Tests: planted violations → expected messages."
    bake/baker_figure.py — Frozen: bake(figure_asy: Path, n_steps: int, out_dir: Path, cfg) -> list[ManifestEntry]. Brief: "Render off (highlight=-1) once + on_1..on_N via asy_compile; key out the flat background to transparency (Pillow); trim; write wall-mip + master; dedup the shared off; return manifest entries. Tests: with a fake asy_compile returning canned PNGs, assert N+1 renders requested, off deduped, bbox/trim correct."
    bake/baker_text.py — Frozen: bake(latex: str, color_groups: dict, out_dir: Path, cfg) -> (off: ManifestEntry, on: ManifestEntry). Brief: "Wrap the paragraph in the standalone template with palette.tex; bake grey 'off' and colored 'on'; trim transparent; two DPI tiers. Tests: a fixture paragraph compiles to two trimmed PNGs; colored words use palette colors."
    tools/overlay_diff.py — as briefed in §2.3.

HOW THE TWO LEGS HAND OFF TO THE DOCTRINE

```
LEG 1 ──► concept_graph.json ──► level_maker ──► floorplan.json ──► CORRIDORS (Mode A)
LEG 2 ──► baked off/on PNGs + manifest ──► room_maker ──► WALLS (Mode B)
        (figure panels: off=grey full / on_k=highlighted)   (text panels: off=grey / on=colored)
```

Both legs emit exactly what the master doctrine's downstream already consumes. Nothing in the doctrine changes shape; these two legs simply fill the two slots it left open — and they're the slots without which there is no corridor and no wall.

THE ONE LOAD-BEARING QUESTION

Leg 1, citation extraction — can you obtain a clean, searchable TEXT transcription of the Principia translation you're using (e.g. an HTML/plain-text edition you can paste as text), or will you only ever have page-IMAGE scans?

Why it's load-bearing and nothing else is:

    If clean text exists: the CITATION pass (step B) becomes a deterministic script — regex over real text to pull "by Lem. I" phrases — which is dramatically more reliable than vision-OCR of 1729 typography, and removes most of Leg 1's iteration entirely. The AI's role shrinks to the few genuinely-inferred edges.
    If only images exist: everything above still works (vision-OCR per page + the four safety nets), but expect more re-paste iterations on step B, especially where old type (long-ſ, ligatures) garbles citation phrases.

Either way the design stands and you can start building. Your answer just tells the Leg-1 children whether citation pass reads text or images — a one-line difference in the brief, not a redesign.

If anything in the master doctrine has fallen out of my context as we go deeper, paste it back and I'll align to it exactly rather than guess. These two legs are the whole game; I'd rather be precise than fast.

--- END VERBATIM ---
