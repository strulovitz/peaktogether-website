# 📜 Mission Prompt for Claude Fable — Write the LOOM BIBLE

Hello Claude Fable! You are the **lead architect** of a new game project called **LOOM** (a modern re-imagining of the classic 1990 LucasArts game *Loom*, built around musical/sonification puzzles). You have just finished reading a book and writing a chapter-by-chapter summary of it — those summaries are pasted at the bottom of this message, and they are your memory of the source material. Please read them first.

This message asks you for a single, large, foundational deliverable. Please talk with me first (state your plan and any load-bearing questions), then write it.

---

## 1. HOW THIS PROJECT WORKS (the assembly line)

We build games with a small "assembly line" of AIs, and this method matters because it determines what your document must be:

- **Nir** — the boss. Decides everything and carries text between separate AI chats by copy-paste. **Nir knows no code and no math.** So nothing we design may ever require Nir to understand a proof, read code, or do math. Nir's role is mechanical: paste, run, install, eyeball, and judge by eye/ear.
- **You, Claude Fable** — the founding architect. You write **documents**: the master doctrine, then detailed designs of the hardest parts, then the spec for a build tool. You may reason about code and audio deeply, but your output is **design documents**, not a finished codebase.
- **Future "parent" chats (Claude Opus)** — fresh Opus chats that will each take your BIBLE (in full) plus need-to-know extras, and design one area in depth.
- **"Child" chats** — fresh chats that each implement ONE module to a frozen spec + tests, then are discarded.
- **DeepSeek (in OpenCode on Nir's PC)** — integrates all code, runs tests, fixes wiring, fetches reference material for the parents, and pushes everything to GitHub. (That's who is preparing this prompt for you.)

**Why the BIBLE must be excellent:** every future parent starts with zero memory and receives your BIBLE as their single source of truth. If it's vague, drift and contradiction creep in. If it's precise and complete, the whole project stays coherent.

### Iron rules for everything you write
- **Honesty first.** Invent nothing. Where something is genuinely undecided or unknown, mark it clearly as an OPEN QUESTION rather than papering over it. Don't assert external library/API details from memory as if certain — describe our own conventions and let the compile/test loop confirm externals later.
- **Formatting for copy-paste.** Anything meant to be transferred between chats must be **prose or fenced code blocks — NEVER Markdown tables** (tables lose their cell contents when Nir copies them). Use bullet lists instead of tables.
- **Ask only the few load-bearing questions** you truly need from Nir before writing. Batch them.
- **Audience of the game:** ~20-year-old players. This is NOT a kids' game — the full emotional/tension palette (dissonance, roughness, high-tempo tension) is in scope.
- **Don't invent website specifics.** The game will live under peaktogether.me, but you do not have reliable details about that site — if a decision depends on site/tech constraints, ask Nir rather than assuming.

---

## 2. WHAT THE GAME IS (the seed — you will expand this)

LOOM is a game where **spells are short musical phrases**, and each spell is the **sonic signature of a mathematical function**, produced by the Helical Sonification System (HSS) described in the attached book summaries. Players learn to **recognize, distinguish, and eventually "cast" functions by ear** (in the spirit of the original *Loom*, where the player wove spells as musical drafts).

Design ideas already surfaced while reading the book (from your own summaries — treat these as raw material, not fixed law; you are the architect and may refine, reorganize, or reject with reasoning):
- Sonification pipeline: sample a function → map value to pitch on the helix → snap to a musical scale → place notes on a beat grid → optional timbre/rhythm/emotional layers → play with real orchestral samples (Philharmonia).
- A **two-program architecture**: "Program A" = an offline **spell compiler** (function → note data as JSON), "Program B" = the in-game **player** (loads compiled spells, plays samples; Web Audio is likely enough, low latency).
- A **spellbook** of functions (line, parabola, sine, damped sine, exponential, cycloid, …) each with a distinct, learnable contour.
- **Difficulty tiers**: flat-melody basics → add timbre/rhythm → co-op polyrhythm ("boss") encounters → a darker/harder tier using the fear/tension toolbox.
- Signature mechanics candidates: comparative "which function is this / which grows faster" by-ear challenges; the brachistochrone "race by ear"; orbital-resonance co-op; consonant/dissonant feedback on casts; a calm study area vs. tense encounters; the pitch helix as an on-screen visual motif; eyes-free/accessible-by-design play.

---

## 3. YOUR MISSION NOW — WRITE THE LOOM BIBLE (the "Old Testament")

Write the **complete foundational doctrine** for LOOM: the master document that every future architect will read in full before touching anything. Make it thorough, self-consistent, and unambiguous. It should include (adapt/rename sections as you see fit, but cover the substance):

1. **Vision & pillars** — what LOOM is in one breath; the 3–5 design pillars; the player fantasy; how it honors the original *Loom* while being genuinely new.
2. **The core loop** — moment-to-moment play: what the player hears, sees, and does; how a "cast" works; win/lose/feedback.
3. **The sonification engine (the heart)** — a precise, implementable description of how a mathematical function becomes a playable spell: sampling, the helical pitch mapping, scale quantization, timbre, rhythm, dynamics/emotion, and how real instrument samples are chosen and triggered. Define the exact knobs (parameters) and their meaning.
4. **The spell format** — the canonical data model for a compiled spell (what a spell *is* as data), so that Program A can write it and Program B can play it. Propose concrete field names and a schema (as a fenced code block, not a table). Include versioning.
5. **The two-program architecture** — Program A (offline compiler) vs. Program B (runtime): responsibilities, boundaries, what crosses between them, why the runtime should stay "dumb" (no math at play-time).
6. **Content: the spellbook & progression** — the function catalog, what each teaches the ear, the difficulty tiers, and how new mechanics unlock.
7. **Game modes** — story/campaign, comparative/quiz challenges, co-op, dark tier, study/practice ("laboratory") — whatever you propose, define each clearly.
8. **Emotional & audio design** — how the book's emotional-shading and fear/tension toolbox is used tastefully for an adult audience (feedback, tension, boss encounters), and the overall audio aesthetic.
9. **Accessibility** — how the game stays playable and meaningful by ear; what visual support exists and why.
10. **Tech stack & platform** — your recommendation (with reasoning) for how Program A and Program B are built, given: Nir can't code; DeepSeek integrates in Python on Windows; the game likely ships on the web under peaktogether.me; assets are Philharmonia samples. Flag anything you're unsure of as an OPEN QUESTION.
11. **Locked decisions vs. open questions** — end with two explicit lists: decisions you are freezing, and questions that still need Nir's call.

Write it as one cohesive document in your reply. Assume it will be saved verbatim and handed to future architects, so define your terms.

---

## 4. AFTER THE BIBLE (same conversation) — the "New Testament"

Once the BIBLE is settled, I'll ask you to zoom in and design **in full technical detail the 1–3 hardest / riskiest parts** of the project (you propose which ones — likely the sonification engine and/or the spell format/compiler). This is the deep-dive companion to the BIBLE.

## 5. LATER — a build tool (the "Apocrypha")

After that, I'll ask you to specify **one build tool** (in the spirit of a "spell compiler" spec) so that fresh implementer chats can build spells in parallel from a simple, well-defined input format.

Please don't start Parts 4 or 5 yet — just acknowledge they're coming, and for now: **state your plan + any load-bearing questions, then write the BIBLE.**

---

## 6. YOUR MEMORY OF THE BOOK (attached below)

Nir will paste, directly beneath this line, the full set of chapter-by-chapter summaries you wrote for the source book (front matter + Chapters 1–10) plus the running "master summary." That is your complete memory of the book's method — rely on it.

⬇️ (summaries pasted here by Nir) ⬇️
