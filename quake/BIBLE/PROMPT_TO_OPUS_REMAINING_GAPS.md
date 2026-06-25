# PROMPT TO OPUS 4.8 (alone) — REMAINING GAPS & FOLLOW-UPS to the Second Canon

Opus — a few loose ends and genuine gaps I want to close while the Formats & Interfaces Standard (the "Second Canon") is fresh in your mind. Some are transmission fixes, some are places the Standard is internally incomplete, plus a couple of one-line confirmations. If anything has dropped from your context, tell me and I'll paste it back rather than guess.

**Reminder of our working model (please honor it everywhere below):** you are the architect — you produce DOCUMENTS: design, decisions, schemas/contracts, and child briefs. Fresh child chats write the actual code; DeepSeek only integrates it. So wherever I ask you to "pin," "define," or "write" something here, I mean the **document / contract / child-brief — never running code.** When code is genuinely needed, it comes from a proper child brief.

## 1. Re-send the "Op → Asymptote translation table" (§3.A.5)
That table came through BLANK when I copied your reply — its cells did not transfer. Please re-send just that table (the Op → Asymptote-call mapping), verbatim. It's load-bearing: it's where the EMITTER learns how each recipe op maps to an Asymptote `geometry` call — including `series` (the ultimate-ratio figures), the conics (`ellipse_foci`, `parabola_fd`, etc.), `parallel`, `intersect`, `tangent_at`/`tangent_from`, `foot`, `bisector`, and the rest.

## 2. Pin the page_map.json adapter — here is my actual file's shape
My Archive.org page-numbers file is the `archive-hocr-tools` "format-version 2", ~600 entries:
- Top level: `identifier`, `format-version` ("2"), `archive-hocr-tools-version`, `confidence`, `pages` (array).
- Each `pages` entry: `leafNum` (int, **1-based**), `confidence` (num|null), `pageNumber` (**string — the printed page label; empty `""` for unnumbered leaves like front matter/plates**), `pageProb` (num|null), `wordConf` (num|null).
- The first entries are front matter, so: `{leafNum:1, pageNumber:""}`, `{leafNum:2, pageNumber:""}`, `{leafNum:3, pageNumber:""}`, …

Two things, both DOCUMENTS (not code): **(a)** decide the rule for the one clash with your §4.1 validation — hundreds of leaves have `pageNumber:""`, so `page_label` is **not unique** across the file, yet `citation_extract` still needs **every** leaf to slice the `_djvu.txt` (e.g. make `leaf_index` the real unique key and apply `page_label` uniqueness only to non-empty labels); and **(b)** write the **adapter child brief** — a frozen-contract spec for an adapter module (source → canonical `page_map.json`), in the same style as your §C child briefs, that a child will implement and DeepSeek will integrate. I don't need any code from you — just the decided rule and the brief. Note also: `leaf_index = leafNum − 1` (your format is 0-based; mine is 1-based), which matches your own §4.1 example (`leaf_index:74` ↔ `leaf_0075.png`).

## 3. Define the `provenance.json` / `Provenance` schema (referenced but never written out)
Your `merge()` returns `(ConceptGraph, Provenance)`, and both your file tree (§2.5) and data-flow map (§1) list `provenance.json (build-only)` — but §4 never actually pins its schema the way it pins every other format. Please add it in the same §4.x style: the full pydantic model + a filled example + validation rules. (Your New Testament §1.6 sketched it — per-edge `provenance: "cited"|"inferred"`, the verbatim `snippet`, `page_seen`, `agreement: "both"|"citation_only"|"inference_only"`, plus the `flags` list — please formalize exactly that.)

## 4. The Room Maker — the one place that is still a design, not a contract
The Standard fully pins the `RoomRuntime` *format* and the `build_room_runtime` *signature*, but the **algorithm** behind `room_maker.py` is not specified anywhere:
- the **wall-slot grammar** and its meaning — you write `"N-0"`, `"E-2"`; what's the exact grammar, how many slots per wall, are there rows/columns?
- **TARDIS room sizing** — how `dimensions_m` is computed from the set of (variable-sized) panel-pairs;
- **placement** — the panel-pair reading order across the four walls, where the entrance is, where the single demon spawns, and which wall becomes the `hidden_door_wall_slot` (the final proof step that opens).

Is this something you want to design now (it's the spatial heart of Mode B), or is it self-contained enough to hand off as its own child brief? Your call — I'm flagging it because it's currently the only major piece that is contract-without-algorithm.

## 5. Quick confirmations (one line each)
- **Read-Mode target rule:** which panel does Read Mode open — the aimed-at panel, else the nearest within a cone? Pin the exact rule (your docs flagged this as a to-specify item).
- **Importance blend:** `merge` sets `importance` 1–5 from citation in-degree blended with the AI `importance_hint`. Pin the exact blend (weights / quantile rule), or confirm it's a child-brief detail.
- **Minor consistency:** `Draw.marker` allows `"tick"`, but `prooffig.asy`'s `drawAll` only renders `"dot"`. Resolve it (render `tick` too, or drop it from the enum).
- **Confirm intentionally deferred (not gaps):** audio / atmosphere (→ ~M8) and the figure background-transparency choice (you said it's a bake-time empirical call with both paths ready). I just want confirmation you're parking these on purpose, not forgetting them.

For anything in #5 you consider child-level rather than architect-level, just say so and we'll leave it to the child brief. Thank you.
