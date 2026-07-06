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

## 7. CURRENT SITUATION (July 6, 2026)

- ✅ Doctrine phase **COMPLETE**: full scripture trilogy written, saved verbatim, pushed.
- ✅ Book cleaned; summaries + master summary saved; Commentaries + WORKFLOW written.
- ✅ **M0 DONE (July 6, 2026):** DeepSeek built + ran the throwaway spike `loom/spikes/m0_latency_spike.py` on Nir's PC against the REAL Philharmonia MP3s. Result: MP3→buffer decode reliable (pygame.mixer.Sound, ~0.5–1 ms/file, 0 failures); output latency 256=5.80 ms / 512=11.61 ms (budget ≤30 ms → PASS, target 256); pygame 2.6.1 / SDL 2.28.4 / numpy 2.4.6 confirmed. **MP3 = GO** (OGG/WAV fallback not needed). Nir ear-confirmed real violin + oboe C-major scales — "sounds good", instant. Full result written into Commentaries §6/§7.
- ✅ **Philharmonia library present** at `C:\Users\nir_s\Downloads\philharmonia\` (compile-time only; never shipped). 20 instrument folders: banjo, bass clarinet, bassoon, cello, clarinet, contrabassoon, cor anglais, double bass, flute, french horn, guitar, mandolin, oboe, percussion, saxophone, trombone, trumpet, tuba, viola, violin. Filename grammar decoded: `instrument_note_length_dynamic_articulation.mp3` (length token = seconds; sharps = `s`; plain note = arco-normal/normal). See Commentaries §7.
- 🧵 **Nir's choice (July 6): Option 1 — work with Fable, open Parent 2** for the Player core.

### NEXT STEPS for LOOM (build phase):
1. ✅ **Milestone 0** — DONE (see above).
2. 🟡 **Parent 2 (fresh Fable) LAUNCHED — building the Player core, delivering in 3 parts.**
   - ✅ **Part 1 of 3 landed + integrated (July 6, 2026):** THE MAP (`loom/MAP.md`) + the four frozen "heart" files, all under a new package layout: `loom/player/core/{spell_model,tuning,audio,conductor}.py` + `loom/player/data/scrub_tuning.json` + empty `__init__.py` in player/, player/core/, player/ui/, compiler/. `.gitignore` now ignores `loom/fixtures/audio_beeps/`. py_compile OK; headless smoke test green (Play fires 0→1→2→3 & stops; scrub forward crosses all; release → PAUSED). Verbatim archive: `BIBLE/LOOM_PARENT_2_PART_1_skeleton_and_heart_BY_FABLE.md`. Map also saved for distribution at `BIBLE/PROJECT_MAP_BY_FABLE.md` (Nir's request).
   - ✅ **Part 2 of 3 landed + integrated + verified (July 6, 2026):** the real pygame audio engine `player/ui/audio_pygame.py` (16-voice pool, MP3→buffer, no synth), two real-instrument fixture spells `fixtures/spells/fixture_flat8.json` (violin) + `fixture_varied5.json` (oboe), emergency-only `fixtures/make_beeps.py`, the **M1 demo** `player/m1_demo.py` (drag the timeline), and the headless suite `tests/{conftest,test_purity,test_spell_model,test_conductor}.py`. **`python -m pytest loom/tests` → 28 PASSED.** DeepSeek ran Fable's real-library resolver headlessly against `Downloads\philharmonia`: every note of BOTH fixtures resolved to a real recording (violin + oboe) — so the demo WILL play real instruments, never beeps. Verbatim archive: `BIBLE/LOOM_PARENT_2_PART_2_audio_engine_fixtures_M1_demo_tests_BY_FABLE.md`.
     - ⏳ **AWAITING NIR'S EAR SESSION to formally "land" M1:** run `python loom/player/m1_demo.py` (violin) + `--spell loom/fixtures/spells/fixture_varied5.json` (oboe); do the 9-step acceptance script (printed on startup). Feel tweaks go ONLY into `player/data/scrub_tuning.json`. **Then** DeepSeek flips M1 in `MAP.md` + adds the Commentaries line (per Fable's run sheet — do this only after Nir confirms it feels right).
     - ✅ **Sample-LENGTH fix + THE SAMPLE FORGE (July 6, 2026):** Nir caught that the greedy "longest per-note" resolver stitched the violin scale from mixed take-lengths (some 1.5s, some 0.5s). DeepSeek reported the full Philharmonia layout to Fable; Fable answered with (a) **Layer-1** — a uniform-length resolver (patched into `m1_demo.py`: pick ONE length common to every note, prefer the longest → violin fixture now all `05`, oboe all `15`; 28 tests still green), and (b) **Layer-2** — `loom/forge/forge_samples.py`, a design-time tool that manufactures uniform-duration WAVs from the originals (TRUNCATE+release, or correlation LOOP-EXTEND, then set-wide RMS match). Ran it for the 8 violin notes @1.3s: 6 TRUNCATE, 2 LOOP-EXTEND (E4, C5); audition scale → git-ignored `loom/forge/forged/violin/_audition_scale_violin_forged13.wav`. Verbatim: `BIBLE/LOOM_PARENT_2_uniform_length_fix_and_SAMPLE_FORGE_BY_FABLE.md`. 3 Commentaries lines recorded (§5). `.gitignore` now also ignores `loom/forge/forged/`. **Pending Nir's ears:** (1) re-drag the demo (even now at 05); (2) listen to the forged audition scale — do the 2 loop-extended notes sound clean on violin vibrato? If yes, Fable adds a `--forged` demo mode ("say the word") and I report TRUNCATE/LOOP results back to him.
       - 🎧 **NIR'S AUDITION VERDICT (July 6, 2026) — DEFERRED, continue later:** (1) The forged audition scale (`forged13`, violin) is **NOT uniform** — the **6th note (C5) rings very short** (C5 was one of the two LOOP-EXTEND notes). So the Forge does not yet produce perceptually equal lengths. (2) The Layer-1 demo (uniform `05` violin) **is better than before**, but **all notes are short**, and **E4 and A4 ring noticeably LONGER** than the rest (their `05` takes have longer audio tails) — so those two now stick out (an ironic inversion of the original problem). (3) **NIR'S ULTIMATE GOAL: make EVERY note uniformly LONG (sustained) — like the Forge is meant to — not short.** So the real target is one long, clean, uniform duration for all notes, with loop-extend that actually holds (esp. C5). Revisit the Forge/demo audio here; not blocking Part 3.
   - ✅ **Part 3 of 3 landed + integrated (July 6, 2026):** the FULL SKELETON — every remaining module as a small "bone" with a frozen interface + "FATTEN ME" note naming its milestone + scripture. Files: `player/core/{notation[M2],echo_logic[M3],choice_logic[M5],lab_remap[M6],pack_model[M7],progress[M7]}.py`; `player/ui/{layout,input_actions,bench_keyboard,bench_staff,bench_transport,graph_view [all M2],helix_view[M4],story_view[M5],lab_view[M6],menu_view[M7]}.py`; `player/app.py[M7]`; `compiler/{compile_spell,pipeline,library_scan,emit,notation_gen}.py`; `player/data/input_mapping.json`. MAP patched (added `forge/` to the tree + the "Selection Law" rule) in BOTH `loom/MAP.md` and `BIBLE/PROJECT_MAP_BY_FABLE.md`. All 22 bones py_compile; `pytest` → 28 PASSED. Verbatim: `BIBLE/LOOM_PARENT_2_PART_3_full_skeleton_bones_BY_FABLE.md`.
   - 🏁 **PARENT 2 RETIRED (thanked by Nir, July 6, 2026).** He delivered the heart (M1), the audio engine + demo + tests, the Sample Forge, the uniform-length fix, and the full bone skeleton. His memory is fully externalized into the repo (MAP + bones + BIBLE archives), so he can die with nothing lost. **Do NOT reopen Parent 2.**
   - 🧱 **NOTE — LOOM is PACKAGED, not flat** (unlike Homeworld's RULE #0): Fable's design uses `loom/player/core/` etc. with relative imports (`from .spell_model import`) and `__init__.py`. This is correct for LOOM; the flat rule was Homeworld-only. `core/` imports stdlib ONLY; anything importing pygame lives in `player/ui/` or demo files.

### 🎯 IMMEDIATE NEXT ON RESTART (Nir's decision, July 6, 2026)
3. **Launch a FRESH Parent 3 for M2 — the Music Bench** (NOT Parent 2; he's retired + context-full). Rationale: the whole bone/MAP system exists so a fresh chat starts light and nobody's context dies — M2 is its first real proof. **Launch package for Nir to paste:** `loom/MAP.md` + the M2 bones (`player/ui/{layout,input_actions,bench_keyboard,bench_staff,bench_transport,graph_view}.py` + `player/core/notation.py`) + `player/m1_demo.py` (the proven transport/scrub logic to EXTRACT unchanged into `bench_transport.py`) + the BIBLE sections those bones name (BIBLE par.3–7 + New Testament par.II + Addendum A). M2 goal: keyboard + staff (noteheads only) + transport widget + graph scrub surface + sync bus → the game starts looking like LOOM. DeepSeek then flattens? NO — LOOM is packaged; just drop files, run `pytest`, keep MAP/Commentaries current.
4. **DEFERRED AUDIO TASK — "every note uniformly LONG":** revisit `loom/forge/forge_samples.py` so a whole scale renders LONG and perceptually EQUAL (fix the C5 loop-extend that came up short; note the Layer-1 demo's `05` set has E4/A4 sticking out longer). Nir's true goal = all notes long + identical length. Could be its own fresh chat or bundled with M2. See Nir's audition verdict above.
5. **Later parents (by number)** take the Compiler (New Testament Part I: pipeline/library_scan/emit/notation_gen) and the remaining milestones (M3 echo, M4 helix, M5 story+choice, M6 lab, M7 pack/menu/app/progress).
6. **Optionally test-drive the Story Weaver prompt** on the Square Root Wikipedia page — story/dialogue/images/specs with NO code yet. (First planned content pack: **Square Root**.)
- Also pending (build-time, DeepSeek): formalize `library_profile.json` (token already decoded); extract the Story Weaver prompt to `loom/prompts/story_weaver_v1.md`; when Nir ear-approves the M1 scrub feel, confirm M1 landed + add the Commentaries line.

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

On the next OpenCode restart:
1. Read this `loom/WORKFLOW.md` first (esp. §7 — current state + 🎯 IMMEDIATE NEXT).
2. Read `loom/COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md` (the map for everybody) + skim `loom/MAP.md` (the codebase map, MEAT/BONE tags).
3. Read scripture in `loom/BIBLE/` only as the task requires (do NOT read it all — it's large).
4. Sanity check: `cd loom` then `python -m pytest tests -q` should print **28 passed**.
5. Ask Nir what's next. **Most likely: launch a FRESH Parent 3 for M2 (the Music Bench)** — §7 "IMMEDIATE NEXT" has the exact launch package. **Parent 2 is RETIRED — do not reopen him.** The deferred "every note uniformly LONG" audio task (`loom/forge/`) is also open.
6. ⚠️ **AGENTS.md still routes startup to Homeworld (Game 4).** LOOM is Game 5 and its authoritative memory is THIS file. **Never modify AGENTS.md** (Nir's standing rule) — if I wake up pointed at Homeworld, Nir will say "read loom/WORKFLOW.md". Commit + push after every meaningful step; keep Commentaries §7 + this §7 current; save Fable answers VERBATIM; remember **LOOM is PACKAGED (not flat)**; give Nir GitHub blob (view) links; emojis + warmth always; he is "Nir", never "boss".
