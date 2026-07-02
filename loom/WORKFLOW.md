# LOOM (Peak Together Arcade) — Project WORKFLOW & MEMORY for DeepSeek (OpenCode)

> ⭐ **ON RESTART, READ THIS FIRST.** Then read the **Commentaries** (`loom/COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`) — the map of the whole project. Then, only if needed for the task at hand, read the relevant scripture in `loom/BIBLE/`. Then ask Nir what's next. Do NOT try to read the whole book/summaries every time; they are large and on-demand.
>
> This is DeepSeek's own memory for the LOOM project. AGENTS.md is intentionally NOT modified (Nir's standing instruction across games).

---

## 0. WHERE LOOM SITS (the Peak Together lineage)

Peak Together (peaktogether.me) is a free, open-source, no-signup educational platform: it turns the hardest unsolved problems in science/math ("mountains") into lovingly-remade '90s co-op games ("the Arcade"). Repo root = the website; each game lives in its own top-level folder.
- **Descent QED** (`descent/`) — inspired by *Descent* (1995); teaches the Basel problem via 6-DOF proof-corridors. SHIPPED & playable.
- **Quake** (`quake/`) — inspired by *Quake* (1996); Newton's *Principia* as a true-3D concept-graph dungeon. In build phase (455 tests green; flat pivot shipped). Has its own `quake/WORKFLOW.md` + BIBLE.
- **LOOM** (`loom/`) — **THIS PROJECT.** Inspired (in name only) by *Loom* (1990); a cozy two-player game that teaches players to **hear the shapes of mathematical functions** via sonification (HSS from Nir's book *Sounding the Unknown*). Currently: **doctrine/BIBLE phase COMPLETE**; build phase not yet started.

---

## 1. WHAT LOOM IS (in one breath)

A cozy two-player time-travel game where a couple (Girlfriend & Boyfriend) visit moments in history, meet the people who first needed mathematics, and solve their problems by **learning to hear functions**: each function is compiled into a short melody (real orchestral Philharmonia samples), and players repeat it Simon-style on an on-screen piano (Echo Puzzle) or answer by-ear questions (Choice Puzzle), while the same melody lights up a graph, a 3D pitch helix, and the keys — and can be **scrubbed** freely (the "Wandering Ear"). Warm, forgiving, ~90% education / 10% play. See the Commentaries §4 for the full locked spine.

---

## 2. WHO'S WHO

- **Boss — Nir** (strulovitz): decides everything; carries text between AI chats by copy-paste; knows no code/math; loves emojis 😊.
- **Founding architect — Claude Fable** (Opus, "Parent 1", on OpenRouter): wrote the whole scripture trilogy. **Access is politically fragile** — last time the model was banned by the USA within ~2 days, so we front-load his doctrine work.
- **Future parents** — fresh Opus chats, one design area each, from the BIBLE.
- **Children** — fresh chats, one module each to a frozen contract + tests, discarded after.
- **Runner — DeepSeek (me, OpenCode)**: integrate/test/push, run engineering spikes (M0) on Nir's Windows PC, fetch material for parents, write prompts/handoffs, maintain the Commentaries + this WORKFLOW.

---

## 3. THE WORKING MODEL & IRON RULES (see Commentaries §1 for the full list)

1. Architects write **documents**; children write **code**; DeepSeek **integrates/tests/pushes** + runs spikes; Nir decides + carries text.
2. **Honesty:** invent nothing; mark gaps; never assert external APIs/file formats from memory.
3. **Copy-paste transfers = prose / bullets / fenced code blocks, NEVER Markdown tables.**
4. **Nir can't code or do math.** All understanding is done by AI; Nir's role is mechanical (paste, run, install, generate images, render LaTeX, listen, look, approve).
5. **Tone:** warm/forgiving; no punishment, timers, scores, or game over. ~90% education / 10% play.

---

## 4. THE SCRIPTURE (all by Claude Fable, saved verbatim in `loom/BIBLE/`)

- **Old Testament** — `LOOM_BIBLE_v1.1_BY_FABLE.md` (v1.1 replaces the deleted v1.0). The complete doctrine.
- **New Testament** — `LOOM_NEW_TESTAMENT_v1.0_BY_FABLE.md`. Deep design of the two riskiest systems (Compiler + Player heart), with the M0–M7 build order.
- **Apocrypha** — `LOOM_APOCRYPHA_v1.0_BY_FABLE.md`. The frozen Story Weaver prompt + Spell Catalog (the content factory).

Supporting: `loom/book/` (cleaned source book), `loom/chapter_summaries/` (Fable's summaries), `loom/MASTER_SUMMARY_STORY_SO_FAR.md` (v0→v10 accumulated), `loom/PROMPT_TO_FABLE_WRITE_THE_BIBLE.md`, `loom/SUMMARIES_BUNDLE_FOR_FABLE.md`, and the Commentaries.

---

## 5. LOCKED DECISIONS

The frozen spine is maintained in the **Commentaries §4** (identity/audience, five pillars, screen, core mechanics, heroes/content, sonification, architecture, audio/assets, formats/stack). Do not re-decide anything there without Nir. Amendment trail is Commentaries §5.

---

## 6. WHAT WE DID (July 2, 2026 — the full LOOM founding session)

This was a single long OpenCode session. Chronological:

1. **Startup:** read Quake memory (WORKFLOW + build handoff), created the `loom/` folder.
2. **Cleaned the source book.** Found Nir's book *Sounding the Unknown* as a .txt in Downloads (OCR-garbled export from Adobe). Per Nir: fix OCR, keep BOTH prose versions per chapter, skip setup sections, strip all code snippets + picture-content. Produced `loom/book/chapter_00.txt` (front matter: epigraphs, back cover, preface, ToC, detailed outline) through `chapter_10.txt`. Gave Nir GitHub **view** links (not raw) for each.
3. **Ran the "Fable reads the book" loop.** Nir pasted each cleaned chapter to a Claude Fable chat; Fable returned (a) a per-chapter summary and (b) a master-summary update. DeepSeek saved each chapter summary as its own file in `loom/chapter_summaries/` and **appended** each master version to `loom/MASTER_SUMMARY_STORY_SO_FAR.md`.
4. **Key process corrections learned this session (see §8).** Notably: the master summary must **ADD/accumulate** all versions (v0→v10), never overwrite; renamed the summary file; moved `book/` into `loom/book/`; Ch.7 came in TWO parts (kept both); fixed Fable's invented name "Yaroslav" → "Nir"; fixed a UTF-8 encoding mojibake in the summaries bundle.
5. **Wrote the mission prompt** `loom/PROMPT_TO_FABLE_WRITE_THE_BIBLE.md` (v2, with full Peak Together context from the home + about pages, co-op two-players-one-screen, Python-desktop tech reality, the LOOM plan, Fable's own seeds) + a one-paste `loom/SUMMARIES_BUNDLE_FOR_FABLE.md`.
6. **Fable wrote the scripture trilogy** (Nir pasted; DeepSeek saved verbatim + pushed):
   - **BIBLE v1.0**, then **v1.1** (after Nir answered 6 open questions; v1.0 deleted). Big adds: Scrubbing as a pillar; Laboratory in v1.
   - **New Testament v1.0** (Compiler + Player heart; the "Conductor" insight; M0–M7).
   - **Apocrypha v1.0** (Story Weaver prompt + Spell Catalog).
7. **Wrote this WORKFLOW + the Commentaries** and pushed everything.

Everything committed + pushed to `github.com/strulovitz/peaktogether-website` under `loom/` throughout.

---

## 7. CURRENT SITUATION (end of July 2, 2026)

- ✅ Doctrine phase **COMPLETE**: full scripture trilogy written, saved verbatim, pushed.
- ✅ Book cleaned; summaries + master summary saved; Commentaries + WORKFLOW written.
- ⏳ Build phase **NOT started** (deliberately — context windows are full; Nir will restart).
- 🧵 **Nir's immediate next intention:** restart OpenCode for a fresh DeepSeek, then **begin the BIBLE for ANOTHER game** with Claude Fable while access lasts (politically fragile).

### NEXT STEPS for LOOM (when we return to build it), per Fable's recommendation:
1. **DeepSeek runs Milestone 0** (New Testament §II.8): a ~50-line throwaway app — load 5 Philharmonia MP3s, click-trigger, try mixer buffer 256/512, measure/feel latency, confirm MP3 reliability on Nir's Windows PC. Output: short report + go/no-go on MP3 (fallback: compile-time OGG/WAV, pre-approved). Retires the two biggest unknowns before real code.
2. **Open Parent A** (BIBLE + New Testament Part I) → frozen module specs for the Compiler's child chats.
3. **Open Parent B** (BIBLE + New Testament Part II + M0 results) → the Player's core.
4. **Optionally test-drive the Story Weaver prompt** on the Square Root Wikipedia page — produces story/dialogue/images/specs with NO code yet; cheap way to find prompt polish needs. (First planned content pack: **Square Root**.)
- Also pending (build-time, DeepSeek): produce `library_profile.json` (decode Philharmonia filename token + instrument roster), and later extract the Story Weaver prompt to its canonical home `loom/prompts/story_weaver_v1.md`.

---

## 8. LESSONS LEARNED THIS SESSION (do not repeat mistakes)

- **"ADD" means accumulate, not replace.** The master summary keeps EVERY version (v0→v10) appended; Nir was (rightly) furious when I overwrote. Same spirit for any running log.
- **Always show Nir the COMPLETE text he asks for** — do not trim/summarize in the chat when he wants the whole thing (he caught me trimming the detailed ToC).
- **Give GitHub VIEW (blob) links, not RAW**, unless asked otherwise. One link when he asks for just a link.
- **Save collaborator outputs VERBATIM** when asked (word-for-word, including intro chatter and emojis).
- **Folder discipline:** everything for LOOM lives under `loom/` (Nir corrected an early misplacement into a root `book/`).
- **Encoding:** when concatenating UTF-8 files in PowerShell 5.1, read/write with explicit UTF-8 (`Get-Content -Encoding UTF8` / `System.IO.File]::WriteAllText` with UTF8 no-BOM) or em-dashes/emojis turn to mojibake.
- **Fable sometimes hallucinates context** (e.g., invented the name "Yaroslav" for Nir; assumed a kids' audience). Watch for it; fix on Nir's instruction.
- **Fable's answers can arrive split across messages** (Ch.7 came in two). Keep all parts as instructed.
- **Emojis + warmth always** (AGENTS.md). Nir is "Nir", never "boss".

---

## 9. RESTART PROTOCOL 🌙

On the next OpenCode restart (per AGENTS.md, the active game may still point to Quake — confirm with Nir):
1. Read this `loom/WORKFLOW.md` first.
2. Read `loom/COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md` (the map).
3. Read scripture in `loom/BIBLE/` only as the task requires.
4. Ask Nir what's next. **Likely:** start the BIBLE for a NEW game (same methodology as LOOM), OR begin LOOM's build phase with Milestone 0.
5. Never modify AGENTS.md. Commit + push after every meaningful step. Keep the Commentaries §7 frontier + this §7 current.
