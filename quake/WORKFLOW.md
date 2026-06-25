# QUAKE (Game 3) — Project WORKFLOW & MEMORY for DeepSeek V4 Pro (OpenCode)

> ⭐ **ON RESTART, READ THIS FIRST.** Then read the **Commentaries** (`quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`) — it is the map of the whole project. Then ask Nir what's next. Do NOT try to read the whole BIBLE; it's huge and on-demand.
>
> This is my (DeepSeek's) own memory for the Quake project, written June 25, 2026. AGENTS.md is intentionally NOT modified (Nir's instruction). A redirect note at the top of `descent/WORKFLOW.md` points here so I find it on wake.

---

## 0. WHERE THIS GAME SITS (the Peak Together lineage)
Peak Together is a multi-game platform (repo root = website; each game in its own top-level folder).
- **Game 1 — Descent QED** (`descent/`): an educational 6-DOF flyer (Basel Problem). **FINISHED & SHIPPED** (itch.io + GitHub Releases). Done.
- **Game 2 — Doom / "Principia Descent"** (`doom/`): an educational FPS in Ursina/Panda3D (M0–M3b built, 49 tests). **SHELVED** — superseded by the Quake pivot (a 2D-ish/flat engine couldn't do what we need; see below).
- **Game 3 — Quake** (`quake/`): **CURRENT PROJECT.** A from-scratch **true-3D** redo. We are in the **DESIGN phase** — nothing is coded yet.

## 1. WHAT QUAKE IS (in one breath)
A first-person, true-3D desktop game (Python, Windows-first) that turns a **geometry-rich book** into a walkable 3D **concept-graph dungeon**. Each idea = a room; each logical dependency = a corridor; corridors cross at different heights as **bridges/underpasses** (because a force-directed graph layout inevitably crosses — that's WHY it must be true 3D, "Quake," not flat "Doom/Wolfenstein"). Walls carry the **step-by-step geometric proof** (each step = a drawing panel + a full-LaTeX text panel). You "read" a panel by **shooting it** (grey → colored). The final lit proof-wall is a hidden door → shoot it → the room's one demon emerges → kill it → ceiling equations bleed red. Clear every room → level complete. **A fun game, not educational software.** First book: **Newton's _Principia_** (1846 Motte English translation; we have clean OCR text + per-page images + page-numbers JSON).

## 2. WHO'S WHO
| Role | Who | What |
|------|-----|------|
| Boss | **Nir** (strulovitz) | Decides everything; carries text between chats; **knows NO code and NO math**; loves emojis 😊 |
| Architect | **Claude Opus 4.8** "parents" | Design/decisions/contracts/child-briefs — **never code**. Parent 1 **died** (context cliff) June 25 after delivering Room System v3. **Parent 2 handoff is ready** (mission slot unfilled). |
| Children | fresh Opus chats | each implements ONE module to a frozen contract + tests, then discarded |
| Runner | **DeepSeek V4 Pro (me, OpenCode)** | integrate child code, run tests, fix wiring, push to git, **fetch scripture for parents**, and **write the prompts/handoffs** (a dying parent can't). I do NOT write game code unless there is truly no other choice. |
| Fusion | OpenRouter multi-model (GPT-5.5 + Gemini 3.1 + Opus judge) | produced the master doctrine only |

## 3. THE WORKING MODEL & IRON RULES
1. Architect writes **documents**; children write **code**; DeepSeek **integrates/tests/pushes**.
2. **Never re-decide or contradict a frozen format/contract.** Before touching anything formatted/contracted, request that exact section verbatim and design *with* it.
3. **Honesty:** invent nothing; mark gaps; few load-bearing questions; never assert external-API names from memory (Asymptote etc.) — define our own conventions and let the compile loop confirm.
4. **Copy-paste transfers must be prose or fenced code blocks, NEVER Markdown tables** (tables lose their cells on copy — this bit us with the Op→Asymptote table).
5. **Nir's hard constraint:** Nir can't code or do math. ALL *understanding* (scans, math, figures, dependencies) is done by **AI in OpenRouter**. Nir's role is mechanical (fetch, paste, run, eyeball). Never design anything needing Nir to understand a proof or hand-draw a figure.
6. **Budget:** Opus runs at **normal/medium effort** now (XHigh too expensive — Descent was built fine in medium). Expect shorter parent answers; keep prompts focused.

## 4. THE BIBLE + THE COMMENTARIES PROTOCOL (how parents get context)
- The BIBLE (`quake/BIBLE/`) holds verbatim "scriptures" + the prompts. It's **large** — giving it all to a parent is a context-killer.
- **The Commentaries** (`QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`) is the small, **DeepSeek-maintained** digest: catalog + locked decisions + amendment trail. **Every parent gets this in full** + the **Old Testament** + **New Testament** (baseline).
- **Everything else is need-to-know, PARENT-DRIVEN.** The parent decides what to request from the catalog. **Do NOT spoon-feed** a pre-filtered subset — we want Opus's full holistic thinking. Whole files → Nir pastes; snippets/sections → DeepSeek fetches verbatim, Nir pastes.
- **The bible is NEVER rewritten** (always in flux, too huge). The Commentaries is the living, accurate digest; I keep its §4 (amendments) and §5 (frontier) current.

## 5. THE BIBLE CATALOG (`quake/BIBLE/`)
- `QUAKE_DOCTRINE_BY_FUSION.md` — **Old Testament** (Fusion's master doctrine, ~459 lines)
- `QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md` — **New Testament** (the two hard legs: MAP + WALLS, ~385 lines)
- `QUAKE_SECOND_CANON_FORMATS_AND_INTERFACES_BY_OPUS.md` — **Second Canon** (Formats & Interfaces Standard, ~1300+ lines, the big reference)
- `QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md` — **Apocrypha** (Room System v3, bearing-accurate doors; supersedes Room-Maker v2 in the Second Canon)
- `QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md` — **the Commentaries** (the digest)
- Prompt history: `FUSION_REQUEST_QUAKE_GAME_FROM_SCRATCH.md`, `PROMPT_TO_OPUS_THE_TWO_LEGS.md`, `PROMPT_TO_OPUS_FORMATS_AND_INTERFACES_STANDARD.md`, `PROMPT_TO_OPUS_REMAINING_GAPS.md`, `PROMPT_TO_OPUS_ROOMS_HAVE_VARIABLE_DOORS.md`, `PROMPT_TO_OPUS_DOORS_MATCH_MAP_BEARINGS.md`, `PROMPT_TO_OPUS_QUAKE_PARENT_2_HANDOFF.md`

## 6. LOCKED DECISIONS (the frozen spine — full list lives in Commentaries §3)
Geometry-rich books ONLY (first = Newton's Principia). True 3D, crossings = bridges/underpasses. Two render modes (wireframe corridor / solid room), switched at the door. Two truths (map vs **TARDIS** room). Two machines (level maker / room maker). Three worlds (content/build/runtime; runtime never sees LaTeX/LLM/book). **Geometry = Asymptote ONLY** (no homemade kernel). **Verification = human overlay-diff** tool. **Highlighting = whole figure + per-step Stabilo**, baked, via `prooffig.asy`. Correctness = **fidelity to the printed page**. Importance 1–5 → room size + map color. **Co-op core** (Mover owns body/heading; Shooter owns reticle; decoupled camera). God-mode; **one hidden enemy per room** (behind the final-proof wall); no level boss. Tech: all-Python, Windows-first, **moderngl + pyglet** + numpy/pillow/pydantic-v2/networkx + (build-only) matplotlib/Asymptote/Tectonic + PyInstaller. **NO** hide-the-pipeline engine. ID spine + `schema_version "1.0"` + `extra="forbid"`. **Room v3 (Apocrypha):** doors = node degree; door direction = corridor's true map bearing; room-local axes parallel to map (global compass); spawn heading = bearing+π; size stays TARDIS. Colors live only in `palette.json` (group names = keys).

## 7. WHAT WE DID TODAY (June 25, 2026)
1. On startup I discovered the then-current game was **Doom** (M0–M3b, 49 tests). Gave Nir view links to Doom's docs.
2. **THE PIVOT:** Nir decided to redo from scratch as **Quake (true 3D)**, because force-directed graph layouts cross and need real bridges/underpasses; "Doom/Wolfenstein" had misled Fusion toward flat engines (Panda). New folder `quake/`. Saved Doom's last (bad) parent handoff verbatim.
3. I wrote the **fresh Fusion request** for the Quake game, iterating per Nir: **geometry-rich ONLY**; **no colorblind** consideration; **no licensing** talk; **no edu-gimmicks** (fun game); **unified hidden enemy**; **Asymptote**; **human overlay-diff verification**; **Stabilo highlighting**; and Nir's **all-AI / no-math-no-code** constraint.
4. Fusion answered → saved **Old Testament**.
5. Prompted Opus → **New Testament** (the two legs: the MAP via citation-transcription; the WALLS via Asymptote + overlay-diff).
6. Prompted Opus → **Second Canon** (the full Formats & Interfaces Standard).
7. Corrected the Room Maker twice: **variable doors = node degree** (holistic), then **doors at true map bearings** (not portal teleport). Opus delivered **Room System v3** → saved as the **Biblical Apocrypha**.
8. Strategy: **lazy-load** heavy docs; baseline OT+NT; rest **on-demand, parent-driven**. Built **the Commentaries** + the **Parent 2 handoff**.
9. **Preserved chat-only decisions in place:** Opus's "remaining gaps" answer had decisions never written to a file (PageMap rule + adapter brief, `provenance.json` §4.9, `Draw.marker`→[none,dot], Read-Mode rule, importance blend, panel schemas/BuildConfig). I inserted each as a clearly-marked **DeepSeek inline commentary** at its correct section (Second Canon §3.A.4/§4.1/§4.5/§4.9/§5.3; New Testament §1.4; Apocrypha §3 cross-ref) and updated the Commentaries. **Nothing is in a "Miscellaneous" bin.**
10. Wrote this WORKFLOW (my memory).

## 8. CURRENT SITUATION
- **Design is broad and deep; NOTHING is built yet** (no `quake/` code — only `quake/BIBLE/` docs).
- **Parent 1 is dead.** The **Parent 2 handoff** is ready (`PROMPT_TO_OPUS_QUAKE_PARENT_2_HANDOFF.md`) — it has an unfilled **`[Nir: state Parent 2's first mission here.]`** slot.
- All chat-only decisions are now safely preserved in the canon (see §7.9).
- Git is clean and pushed.

## 9. NEXT STEPS / OPEN THREADS
- **Fill the Parent 2 mission** (or let Parent 2 propose holistically), then spin it up with Commentaries + OT + NT.
- **The build hasn't started** (engine M0 → … per Old Testament §13 / Second Canon §5.4 wiring).
- Deferred on purpose: **audio** (~M8); figure **background-transparency** (bake-time empirical).
- Offered by Parent 1, not yet requested: a consolidated `BuildConfig`/runtime-config doc (a "§4.10"); a Room-Maker golden-fixture worked example.

## 10. LESSONS LEARNED / GOTCHAS (don't repeat these)
- **Don't micromanage the architect.** Give Opus the *truth* + the *whole problem* and let it think holistically. Surgical "fix exactly this field" prompts are wrong (Nir's "pinky finger, not the whole body" rebuke). Same for context: don't spoon-feed parents pre-filtered lines.
- **Tables don't survive copy-paste** → deliver/request copy-paste content as **fenced code blocks or lists**.
- **I (DeepSeek) don't build things** unless there's no choice; the architect designs, children build.
- **Opus outputs are saved VERBATIM** ("holy"). Wrap any DeepSeek additions in clearly-marked begin/end commentary blocks with author + status.
- **The Commentaries is the answer to the parent-killer context problem.** Maintain it; never rewrite the whole bible.
- Nir loves emojis; be warm, concise, ask before initiative, surface typos.

## 11. CONVENTIONS
- Each game lives in its own top-level folder; never put game files in repo root.
- BIBLE = verbatim scriptures; DeepSeek additions are clearly-marked inline commentaries.
- Commit + push after every meaningful change; give Nir **view (blob)** GitHub links to copy from.
- Default branch is **master** (not main).

## 12. ON RESTART / AGENTS.md
AGENTS.md (`C:\Users\nir_s\.config\opencode\AGENTS.md`) now routes startup **directly to Quake**: read this file first, then the Commentaries, then ask Nir. (Nir reversed the earlier "don't touch AGENTS.md" instruction on June 25 so I'd always wake up oriented to Quake until this game ships — like Descent did. The earlier indirect redirect in `descent/WORKFLOW.md` was removed.) Note: AGENTS.md lives outside the git repo, so it is NOT on GitHub — it persists locally on Nir's machine.
