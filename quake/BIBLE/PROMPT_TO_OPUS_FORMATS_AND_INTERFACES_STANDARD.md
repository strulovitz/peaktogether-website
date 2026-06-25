# PROMPT TO OPUS 4.8 (alone) — THE FORMATS & INTERFACES STANDARD (lock every format verbatim)

Opus — it's Nir. You still have the master doctrine ("Two Minds, One Proof") and your New Testament ("The Two Legs"). If any of it has fallen out of your context, tell me and I'll paste it back rather than guess.

You did well on the two legs. Now I need the next thing, and I think it is the real foundation everything else rests on.

## The realization

We are building one machine out of many small modules and several content-authoring AI steps. Those pieces only compose if the things passed between them — the **interfaces between modules**, and **especially the exact structured text/data each authoring-AI must produce for each tool** — are pinned down as a single, consistent standard.

Here is the key point: **we have no external standard to lean on.** A JPEG file has a defined internal format because the world standardized it; we have nothing like that. Every format in this project — what the STRUCTURE / CITATION / READER / EMITTER AIs emit, the figure-source convention, the concept graph, the room source, the manifest, the savegame, the module signatures — is **ours to invent.** If we don't define them now, precisely, each one gets improvised inconsistently and the whole thing fails to fit together.

## Why ONLY you can do this (not a child)

Defining these formats requires **holistic, integrative understanding of how every piece fits the whole.** A child chat sees only its one module; it would invent a locally-convenient format that doesn't match its neighbors. The standard must be set **top-down by the one mind that holds the entire system — you — and then handed to each child frozen.** I am explicitly NOT asking you to delegate this or to tell a child to "decide the format." I am asking YOU to write every format out, literally and completely, now.

## What I want: THE FORMATS & INTERFACES STANDARD

A single authoritative document — think of it as the project's wire-format spec, Layer-3 of the bible — in which **every interface and every format is written out explicitly, verbatim, copy-paste-ready**, so that any future child can be handed the exact contract for its module and the exact formats it reads and writes, with **zero ambiguity and zero room to invent.**

Do NOT describe formats in prose, and never say "the child decides." For **EVERY item below**, give me, literally:

- **(a)** the COMPLETE schema — every field, its type, required/optional, default, allowed values, constraints (e.g. `extra="forbid"`, `schema_version`);
- **(b)** a FULLY FILLED real example — use real Principia content where natural (a real lemma, a real citation phrase, a plausible figure);
- **(c)** the VALIDATION rules — exactly what makes an instance invalid and must fail loudly at build time;
- **(d)** for anything an AI emits: the **exact instruction-snippet I paste to that authoring AI** so it produces precisely this format and nothing else.

Cover ALL of the following. Group them; miss none.

### PART A — THE AI-EMITTED FORMATS (most important — these have no external standard, so be the most exhaustive here)
- **STRUCTURE pass output** (`nodes_raw`).
- **CITATION pass output** (`citations_raw`). Note: I now HAVE clean OCR text of the Principia — the 1846 Andrew Motte English translation: a plain-text `_djvu.txt` of the entire book, plus per-page images and a leaf→printed-page-label JSON. So design the citation pass to read **TEXT primarily** (regex / structured extraction over real text), with the page image only as a fallback. Reflect this in both the format and the instruction-snippet.
- **INFERENCE pass output** (the understanding-based dependency list used for your two-method disagreement check).
- **READER AI output — THE CONSTRUCTION RECIPE for a figure.** This is the one I care about most and the one currently least specified. Define a precise, structured standard for it: the ordered construction expressed in **relative / constructive terms, never absolute coordinates** (the overlay tool absorbs global placement, so absolute position/scale/rotation must NOT be required); every element named and tagged with its **(color-group, proof-step)**; the proof's **step segmentation**; rough anchor hints only; and **how figure elements link to the paired explaining text.** Make it a real format, not "natural language."
- **EMITTER AI output — the `figure.asy` HOUSE CONVENTION** (against your `prooffig.asy` contract): the exact required file structure (construction section; registration via `elem`/`lbl` with `(group, step)`; the `highlight` parameter; draw order). Write the canonical template **verbatim** and the rules every figure file must obey.
- **The EXPLAINING-TEXT block** the text-authoring AI emits: the full-LaTeX paragraph PLUS exactly how it tags which words carry which color group (so figure↔prose color coupling works).
- **`palette.json`** — the named color-group definitions authored per pack/level.

### PART B — THE GENERATED DATA / FILE FORMATS (write each out fully)
`concept_graph.json` (Layer 1), `provenance.json` (build-world only), the room source `room_<id>.json` (Layer 2 — the coupled step-pairs), `floorplan.json`, `room_runtime.json`, `manifest.json` (baked assets), `savegame.json`.

### PART C — THE MODULE INTERFACES (make `contracts.py` real)
Every public pydantic model and every public function/class signature, for **every module across all three worlds** (content tooling, build, runtime), with exact types, defaults, and return types — including the **runtime co-op semantic-action contract** (the action set the input layer exposes for Mover and Shooter) and the **events the gameplay step emits.** These are the frozen signatures every child must implement against.

### PART D — THE SHARED INVARIANTS that bind it all (write once, authoritatively)
The **ID spine grammar** (the exact id forms — e.g. `<node_id>.s<step>.{fig|txt}`, edge ids, etc.); `schema_version` handling; the coordinate system + units; color-group naming rules; file/directory naming; and the standing **correctness rule** (fidelity to the printed page).

### Plus: a one-page DATA-FLOW MAP
Which tool or AI **produces** each format and which module **consumes** it — so the verbatim formats are visibly one coherent system, not a pile.

## The locked amendments still hold — reflect them in the formats
- Asymptote is the **only** geometry tool.
- Verification is **my human overlay-diff** → so recipes need only **relative construction + rough anchors, never absolute coordinates.**
- We **highlight the whole figure per step** (off = full figure in grey; on_k = step k highlighted), baked in advance.
- **importance 1–5** drives room **size AND map color.**
- Correctness = **fidelity to the printed page.**

## How to work
Think **long and hard** — your XHigh effort last time was excellent; use it. These formats are OURS to define, so for our own formats there are **no "unknowns" to defer** — define them **completely and verbatim**; that is the entire point of this document. The ONLY thing you may still refuse to invent is an **external library's exact API** (e.g. Asymptote's real function signatures) — for those, define OUR wrapper/convention fully and note that the real API names get pinned from the docs and caught by the compile loop, exactly as you already designed. Ask me only the **few genuinely load-bearing** questions. If anything from the doctrine or the two-legs document has dropped from your context, ask me to paste it back rather than guessing.

This document is **large by nature** — be as long as it takes. Completeness and verbatim precision matter far more than brevity. This is the standard that turns your two-legs design into something a room full of memoryless children can actually build without drifting apart. Thank you.
