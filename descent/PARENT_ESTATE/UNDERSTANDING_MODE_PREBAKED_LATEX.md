# DESCENT QED — DESIGN & BUILD HANDOFF (Understanding Mode → Pre-Baked LaTeX Images)

Author: Parent Opus, for future-Opus. Status: authoritative. Supersedes all prior notes on Understanding Mode rendering.

## 0. One-paragraph orientation

Descent QED is a desktop game (pygame/OpenGL — NOT a web app, never say web app). A couple flies one ship down corridors to rescue hostages. Robots block the way; each is destroyed by selecting+firing the one correct "mathematician-missile." The robot's hologram is just a stylized blue photo of a mathematician from Wikipedia — it shows NO math and must not be touched. The PRIME LAW remains: the engine is mathematics-blind; it matches opaque ids (robot.required_technique_id == fired_missile_id); meaning lives in data + the player's head. This handoff concerns Understanding Mode — the screen showing four layered explanations of a concept (mathematician / physicist / biologist / engineer), at four depths, that the player fades between.

## 1. The problem this handoff fixes

The original Understanding Mode tried to render colored math live, using matplotlib mathtext — a crippled subset of LaTeX that cannot color individual symbols (so a "colored background box" hack was invented as a second-best substitute) and cannot render advanced LaTeX (\tfrac, \binom, multiline align, matrices, \text{}, etc.). For a game about the hardest math, that ceiling is fatal. It also never actually drew the colors at all — the core educational visual had never appeared on screen.

## 2. The solution (decided, final)

Pre-bake the explanations into transparent PNG images on Nir's PC using FULL real LaTeX, ship the images, and have the game just stack & fade them. This gives both worlds: full LaTeX power + per-symbol color while authoring, and instant/offline/zero-LaTeX rendering for players.

- **Toolchain (world-class, install once on Nir's machine):**
  - TeX Live (full, ~6.5 GB) — provides pdflatex, dvisvgm, standalone class, xcolor, soul. One-time, shared across every Descent game ever made.
  - `pip install pillow` — final RGBA verification/padding.
- **Why pre-baked, not live LaTeX:** live LaTeX launches a compiler per formula (≈1s) → stutter at 60fps. Formulas are authored ahead of time, so bake once. Players need no LaTeX at all — they get instant transparent PNGs; tiny download; fully offline. New games ship only new tiny text+image files; the LaTeX install is never re-shipped.
- **Transparency done right:** render onto native transparency (`dvisvgm --background=transparent`), do NOT knock out a black/white background (that muddies anti-aliased edges). Vector PDF → PNG keeps math razor-sharp at any DPI.
- The four layers become four transparent PNGs, stacked in depth; the game cross-fades/blends between them. Game-side change is therefore tiny and a simplification (load + stack + fade), and must not break the existing working blur / pan / depth / CTRL-unlock behavior. Game-side work is DEFERRED until the baker is proven.

## 3. The pipeline

```
Wikipedia page → Child Opus (writer) → corridor text file (LaTeX) → DEU "baker" (Python) → transparent colored PNGs
```

Two separate tools, different natures:

- **Tool 1 — the WRITER:** a child Opus + a rich prompt (NOT a script — requires judgment). Turns a Wikipedia page into a corridor text file in the exact format below, choosing techniques, writing four-depth explanations, and tagging stains & threads (§5). Output may have imperfect LaTeX; the baker must report failures precisely, never crash.
- **Tool 2 — the BAKER (deu/bake_corridor.py):** standalone, offline, zero game dependencies, zero intelligence. Reads ONE corridor file, compiles each layer in isolation via full LaTeX, emits one transparent colored PNG per (robot, layer), plus a `_report.txt` naming every success and — for any failure — the exact robot, layer, and raw LaTeX error. Like Doom's DEU utility: edits content, never the engine.

## 4. UNIT = ONE CORRIDOR (critical)

The baker processes one whole corridor at a time, sharing ONE stain ledger. Never one robot at a time — the stains' entire meaning is the continuity between robots. One-robot mode would destroy the design and is only a last resort if a corridor proves impossible.

## 5. THE TWO COLOR SYSTEMS — independent, two scales (the heart of the design)

### 5a. BACKGROUND "STAINS" — MACRO, sacred, ACROSS robots

- The big remembered concept-regions. A player recognizes a stain from room to room: concept A is a red stain here; the same red stain reappears in the next robot and flows into concept C; a blue stain (B) flows into D. One page may carry several stains; they branch independently down the corridor.
- **Scope:** whole corridor. **Meaning:** "this region of thought is the same ongoing concept as before."
- **SACRED.** Few. Specific. Intuitive. The only allowed combination logic — the Kindergarten Mixing — is exactly:
  - red+blue=purple
  - yellow+red=orange
  - yellow+blue=green
- Stains are the most important thing; everything else yields to them. Stain colors are NEVER altered for legibility.
- **Visual:** a broad background wash/highlight behind a phrase (LaTeX soul/\colorbox-style), readable at a glance, room after room.

### 5b. FOREGROUND "THREADS" — MICRO, page-local

- Local bookkeeping within one robot, one layer (one page). When a compact expression is "opened" into its longer form on the next line, the long form wears the same foreground color as the compact one that spawned it, so the eye links them. A different expression opens in a different thread color.
  - **Canonical example:** line 1 shows (a+b)²; line 2 shows a²+2ab+b²; both share one thread color → player sees they're the same thing unpacked.
- **Scope:** one page only; resets between robots/layers; does NOT travel.
- **Which color is NOT sacred** — only that it is the SAME within a page for the same expression-thread, and DISTINCT from sibling threads on that page. The tool may even auto-assign the actual hue. No fixed thread vocabulary (do NOT force "green = parentheses"); the writer invents as many distinct thread ids per page as needed. Nested parentheses → different colors, never all one color.

### 5c. INDEPENDENCE (must not be blurred)

A single span can have BOTH at once: a sacred stain (macro: where you are in the big story) AND a thread letter color (micro: what-opens-into-what on this page). They answer different questions at different scales. Treat them as two separate tag systems; never collapse one into the other.

### 5d. COLOR = MEANING, NOT MEDIUM

There is no distinction between text and math. Color attaches to concepts/spans, which may be prose, $math$, or both mixed. If symbol E is red at the graduate layer, the words "the electric field" are red at the high-school layer — the color is the thread connecting depths. A span's content is freely prose, math, or both; LaTeX renders all uniformly.

### 5e. LEGIBILITY RULE (one direction only)

Stains are sacred and untouchable. Foreground/threads yield. So:

- Keep each stain background color exactly as authored.
- Choose foreground letter shade/contrast so it stays readable on the stain (foreground yields, background never).
- Threads must remain distinct from each other on a page; the tool picks/adjusts thread hues to satisfy both "same-within-thread, distinct-between-threads, and legible-on-whatever-stain-it-sits-on."
- Neutral (un-threaded) prose carries no meaning → may be freely set to a safe light/dark for legibility.

## 6. CORRIDOR FILE FORMAT (the contract — critical; writer and baker MUST agree)

Plain UTF-8 text. Blocks use `KEYWORD { ... }` with brace-matching (LaTeX braces inside are fine). Real LaTeX (full, not mathtext) is allowed in explanation bodies.

```
TITLE { Maxwell's Equations }

# SACRED macro stains. Few. Only the 3 intuitive mixes allowed.
# name = r g b   (floats 0..1)
STAINS {
  electric = 0.85 0.12 0.12     # red
  magnetic = 0.12 0.30 0.85     # blue
  coupling = 0.55 0.10 0.65     # purple  (electric + magnetic)
}

ROBOT: 3
  NAME { Faraday }
  EXPLAIN_MATHEMATICIAN {
     ... real LaTeX prose+math, with \stain{} and \thread{} tags ...
  }
  EXPLAIN_PHYSICIST { ... }
  EXPLAIN_BIOLOGIST { ... }
  EXPLAIN_ENGINEER  { ... }

ROBOT: 4
  NAME { Ampère }
  EXPLAIN_MATHEMATICIAN { ... }
  ...
```

**Markers inside explanation bodies (the only color syntax):**

| Marker | Channel | Scope | Effect |
|--------|---------|-------|--------|
| `\stain{stainkey}{ ...content... }` | MACRO background | corridor-wide; key MUST exist in STAINS{} | colored highlight/wash behind content (sacred) |
| `\thread{threadid}{ ...content... }` | MICRO foreground | page-local; ids invented freely per page | colored letters; same id ⇒ same color on this page; distinct ids ⇒ distinct colors |
| nesting | both | — | `\stain{coupling}{ \thread{t1}{(a+b)^2} = \thread{t1}{a^2+2ab+b^2} }` — thread sits inside a stain |
| (unmarked) | — | — | neutral glue (light grey), no color |

- `\thread{}` colors are not declared in a ledger; they are page-local symbolic ids. The baker assigns each distinct id, per (robot, layer), an actual hue from an auto palette, chosen distinct-from-siblings and legible-on-its-stain.
- Content inside any marker is freely prose, `$...$`, or mixed.
- **Nested data model (per §5/Nir's request — "small structures inside big structures"):** conceptually each page is a tree — stain spans (big blocks of meaning) containing thread spans (expression links) containing content. The parser builds exactly this nesting via brace-matching; the renderer emits \colorbox/soul for stains and \color for threads accordingly.

## 7. THE BAKER — exact behavior (deu/bake_corridor.py)

- **Toolchain check:** require pdflatex and dvisvgm; if missing, fail loudly with the TeX Live install hint. (Pillow checked at import.)
- **Parse the corridor** (lenient, baker-owned reader, separate from the game's strict parser): TITLE, STAINS{} (name→rgb), and per ROBOT: the NAME and the four EXPLAIN_* blocks, via brace-matched `_grab_block`.
- **Per (robot, layer):** build a standalone-class LaTeX doc:
  - `\usepackage{amsmath,amssymb,xcolor,soul}`, [T1]{fontenc}.
  - `\definecolor` every stain from STAINS{}.
  - Two-pass marker expansion (brace-matched, like the existing \col expander but now two markers):
    - collect all distinct `\thread` ids in this page; assign each a distinct, legible auto-color (`\definecolor`), tracking which stain it sits on for contrast;
    - emit `\thread{id}{X}` → `{\color{thread_id} X}`;
    - emit `\stain{key}{X}` → highlight wash behind X (soul `\sethlcolor{key}\hl{X}` or `\colorbox`), key validated against STAINS{}; unknown stain key → render uncolored AND report (never crash).
  - Default prose color = light grey (descentprose), `\sffamily`, border=8pt, varwidth=… for tight transparent crop.
- **Compile:** `pdflatex -interaction=nonstopmode -halt-on-error` → PDF; on failure extract the `! ... / l.NN` lines from the .log (precise human error).
- **Rasterize:** `dvisvgm --pdf --png --png:dpi=<DPI> --background=transparent` → transparent PNG; handle out-1.png naming variants.
- **Verify/save:** Pillow `convert("RGBA")` → save `baked/<corridor>/robot<N>_<layer>.png`.
- **Report:** write `_report.txt` listing [ OK ] / [FAIL] / [skip] per layer; for FAIL print robot+layer+raw LaTeX error; flag unknown stain keys and any thread-legibility fallbacks. Exit nonzero if any failure.

CLI: `python deu/bake_corridor.py corridors/maxwell.txt --out baked/maxwell --dpi 600`

**Non-negotiables:** standalone & offline; zero game imports; trusts no input; one corridor (shared stain ledger) per run; stains sacred & untouched; threads page-local, auto-hued, distinct, legible; never crashes on bad LaTeX — reports precisely.

## 8. ACCEPTANCE TESTS (prove it, by eye)

1. **Maxwell corridor bakes:** run on a converted maxwell.txt; open the PNGs — confirm transparent backgrounds, sharp math, per-symbol/per-word color, stain washes behind concept regions, thread colors linking (a+b)²→a²+2ab+b² style openings on a page.
2. **Macro continuity by eye:** confirm a stain (e.g. electric red) appears recognizably across multiple robots in the corridor (the macro thread).
3. **Data-driven proof (anti-hardcode):** bake a second dummy corridor with a different STAINS{} ledger; confirm output colors follow the file, proving nothing is Maxwell-hardcoded.
4. **Failure clarity:** feed one deliberately broken formula; confirm `_report.txt` names the exact robot, layer, and LaTeX error, and the batch does not crash.

## 9. Status / next steps

- **Build the baker first** (full §5 stain+thread+legibility model, §6 format, §7 behavior). Already substantially coded in this conversation (the \col version) — extend \col→\stain+\thread, add soul, add per-page thread auto-coloring with legibility.
- **Then produce a converted sample maxwell.txt** in the §6 format (current file uses old mathtext + word-named colors; it must be rewritten with RGB STAINS{} and \stain/\thread tags) so Nir can bake tonight.
- **Then write the WRITER prompt** (Wikipedia → §6 file), context-rich, not castrated.
- **Then (DEFERRED) the tiny game-side swap:** Understanding Mode loads the 4 PNGs, stacks, fades — without breaking existing blur/pan/depth/CTRL-unlock.

**Hard reminders:** desktop game, never "web app." Hologram = blue photo, no math, untouched. Plaque untouched for now. Don't over-dramatize ("the law", "most important thing") — the whole system must work; this is one focused, correct fix. Stains sacred, foreground yields. Build the real tool, not a brief.

That's the complete brain-dump. Once DeepSeek has it safely in GitHub, tell me and I'll extend the baker to the full stain+thread model and hand you the convertible maxwell.txt. :-)
