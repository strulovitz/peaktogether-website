# SESSION CONTEXT — June 20, 2026 NIGHT

> **Project:** DESCENT QED engine + Peak Together website
> **Repo:** `C:\Users\nir_s\peaktogether-website`
> **GitHub:** `https://github.com/strulovitz/peaktogether-website`
> **Builder:** DeepSeek V4 Pro (OpenCode)
> **Time:** ~12:30 AM Israel time. Nir is going to sleep.

---

## WHAT HAPPENED TODAY

### 1. Website redesign committed and pushed
The Fusion AI website redesign (from June 18 evening) had been sitting as uncommitted changes. We committed and pushed: new `index.html`, `style.css`, and 7 new images (hero, doom screenshots, theme park, hall of fame). Commit aa6a785.

### 2. CORRIDOR_CREATOR_PROMPT_FOREVER — the unified corridor-authoring prompt
Parent #9 (Opus 4.8) produced a unified "forever" prompt that tells a child Opus to produce ALL 3 corridor files (baker + game + manifest) from any Wikipedia topic. Two versions:
- v1: 54 lines — too compressed, Nir rejected it
- v2: 274 lines — proper detail, accepted

Saved as: `PARENT_ESTATE/CORRIDOR_CREATOR_PROMPT_FOREVER.md`
The OLD baker-only prompt `PARENT_ESTATE/CORRIDOR_WRITER_PROMPT.md` (132 lines) is UNTOUCHED.

### 3. Basel corridor 2 — "Every Even Zeta by Symmetric Polynomials"
A child Opus (using the FOREVER prompt) produced all 3 files for Basel corridor 2:
- **Baker file:** `levels/mathematics/basel_problem/basel_general.txt` (7 robots: Euler, Bernoulli, Newton, al-Khwarizmi, Girard, Weierstrass, Mengoli)
- **Game file:** `corridors/basel_general.txt` (42 fizzles, LEDGER with 6 colors, SEGMENTS, all fields present)
- **Manifest:** `levels/basel.txt` (updated to list both corridors)

All 3 files saved and pushed. Commit 4f4a321.

The old baker-only file from the previous prompt was renamed: `corridors/OLD_euler_even_zeta.txt` (so it doesn't get confused).

### 4. CRITICAL ISSUE FOUND — Baked image collision
Both corridors have robots 1-7. The manifest has ONE `baked:` path for the whole level. Baked images are named `robot1_mathematician.png` etc. — just by number. Baking corridor 2 into `baked/basel/` would OVERWRITE corridor 1's images.

**Root cause:** The architecture doesn't support per-corridor baked directories. The manifest format and level_parser.py only support one `baked:` line per level.

### 5. Parent Prompt #10 written — Generic Folder Architecture
Nir wants this fixed GENERICALLY — not just for Basel, but for ALL future subjects (Riemann, Navier-Stokes, Protein Folding, etc.). Each corridor's baked images must be isolated. Parent #10's mission is to design the generic folder convention and the manifest/parser changes needed.

Saved as: `PARENT_ESTATE/PARENT_PROMPT_10_GENERIC_FOLDERS_2026-06-20_NIGHT.md`
NOT YET DISPATCHED — Nir will paste it to a fresh Opus tomorrow.

### 6. 4 new portraits needed (Nir will do tomorrow)
- Jacob_Bernoulli-hologram.png
- Isaac_Newton-hologram.png
- Albert_Girard-hologram.png
- Pietro_Mengoli-hologram.png

Already have: Leonhard_Euler, al-Khwarizmi, Karl_Weierstrass (from corridor 1).

---

## WHAT TO DO TOMORROW — IN ORDER

1. **Dispatch Parent Prompt #10** to a fresh Opus: `PARENT_ESTATE/PARENT_PROMPT_10_GENERIC_FOLDERS_2026-06-20_NIGHT.md`. The parent will design the generic folder architecture. Apply the builder's brief.

2. **Bake corridor 2** once the folder architecture is fixed (so images go to the right per-corridor folder, not colliding with corridor 1).

3. **Test corridor 2** individually (point the game at it, play through all 7 robots, verify fizzles, Understanding Mode images).

4. **Get portraits** for the 4 new mathematicians.

5. **Continue making more corridors** for Basel (one at a time, each tested individually).

---

## CURRENT STATE OF THE REPO

| Item | Status |
|------|--------|
| Website redesign | COMMITTED & PUSHED |
| CORRIDOR_CREATOR_PROMPT_FOREVER | v2 (274 lines), saved |
| Basel corridor 1 (Euler's approach) | PLAYABLE, baked, tested |
| Basel corridor 2 (Even Zeta generalization) | 3 FILES SAVED, NOT YET BAKED (collision issue) |
| Generic folder architecture | PARENT PROMPT WRITTEN, not yet dispatched |
| 4 new portraits | Nir will get them tomorrow |
| Multi-corridor engine support | NOT YET — build corridors first, test individually, then do multi-corridor later |
| Git | Clean, pushed |

---

## NIR'S PLAN FOR MULTI-CORRIDOR (important context)

Nir's strategy: build corridors one at a time. Test each individually with the current single-corridor system. After several real corridors exist and work, THEN ask a parent to design the multi-corridor engine change. Test multi-corridor with REAL corridors (Basel proofs), NOT with the toy Maxwell placeholder. Maxwell was never a real corridor — it was a development placeholder.

---

## ON RESTART — Read these in order:
1. **WORKFLOW.md** (this project's memory)
2. **This file** (`SESSION_2026-06-20_NIGHT.md`)
3. `PARENT_ESTATE/PARENT_HANDOFF_V3.md` — THE LAW
4. `PARENT_ESTATE/PARENT_PROMPT_10_GENERIC_FOLDERS_2026-06-20_NIGHT.md` — Parent #10 (PASTE TO FRESH OPUS)

---

Good night Nir! Sleep well! Tomorrow we fix the folders and bake corridor 2! :-)
