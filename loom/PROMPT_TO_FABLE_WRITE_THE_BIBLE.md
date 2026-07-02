# 📜 Mission Prompt for Claude Fable — Write the LOOM BIBLE

Hello Claude Fable! 👋 You are the **founding architect** of a new game called **LOOM** — a modern re-imagining of the classic 1990 LucasArts adventure *Loom*, rebuilt around musical **sonification** puzzles. In an earlier conversation you read a book (*Sounding the Unknown*, about the Helical Sonification System) and wrote a chapter-by-chapter summary of it. That whole set of summaries — plus a running "master summary" — is pasted at the **bottom of this message**; it is your memory of the source material. Please read it first.

This message asks you for one large, foundational deliverable: **the LOOM BIBLE.** Please talk with me first (state your plan + any load-bearing questions), then write it.

---

## 1. THE PROJECT IT BELONGS TO — "Peak Together" (summary of the website)

**Peak Together** (peaktogether.me) is a free, open-source, no-signup educational project by **Nir** (that's me, the boss). Its mission: take the **hardest unsolved problems in science and math** and make them joyful for curious young people by turning each one into a **lovingly remade classic '90s game**. The framing:

- Each hard problem is a **"mountain"** to climb (the Riemann Hypothesis is our "Everest"); climbing = actually understanding a real idea. Seven of the mountains are the Millennium Prize Problems.
- It's pitched as a **theme park + science museum you play at home** — "the most epic date night your brain has ever been on."
- **Built for Two:** the signature format is **co-op, two players on one screen** (one on keyboard/joystick, one on controller/mouse) — *you have to talk to each other to win*. (Solo play is possible too.)
- **Always free, open-source, no signup/payment/ads.** (Nir does not care about sample licensing — the project is free and open; please don't raise licensing concerns.)
- The **Arcade** already has: **Descent QED** (playable — inspired by *Descent* 1995, teaches the Basel problem; you fly 6-DOF corridors made of proof steps) and **Quake** (in progress — Newton's *Principia* as a 3D concept-graph dungeon). LOOM will be the next Arcade title.
- A recurring Peak-Together idea worth knowing: **"Understanding Mode"** — the same idea explained four ways (graduate / undergrad / high-school / real-world). Getting something wrong is never punished — you get a gentle, friendly explanation.

**The heart of it (from the About page):** Nir built this for his girlfriend (a gamer). It began as interactive math demos she could "fly" through with a joystick; it became games because she's a gamer; it became games-first (nostalgic fun in front, the scary math behind) because she gave honest feedback that math-first scared people off. The dream is that the project supports a shared life of travel and a small family. So the tone is **warm, romantic, friendly, and encouraging** — never intimidating.

**Priority:** this is **~90% educational, ~10% "gameplay."** It is NOT built to satisfy hardcore gamers; it's built to *teach a real idea through play* and to be a lovely shared activity. Design for learning and wonder first.

---

## 2. WHAT LOOM (this game) IS

In the original *Loom* (1990), magic worked through **"drafts"** — short 4-note melodies played on a distaff; players learned to recognize and reproduce them **by ear**. Nir's twist: instead of arbitrary melodies, **each spell is the sonic signature of a real mathematical function**, produced by the Helical Sonification System (HSS) from the book you summarized. The player is trained, *Loom*-style, to **hear the difference between functions** — e.g.:
- linear growth vs. exponential growth,
- a sine vs. a damped sine (e^(−at)·sin(ωt) — the book's own Chapter 5.3 example),
- periodic vs. chaotic behavior,
- …and eventually more complex expressions (that's the stretch goal — Nir would love to reach it).

Instead of sterile beeps, spells use **real orchestral instrument samples** from the Philharmonia sound-sample library (free WAV files of essentially every instrument). Notes can be pitch-shifted, or we pick the nearest-pitch sample per note.

**Seeds you (Fable) already proposed** in the earlier chat — treat as raw material, refine freely:
- A **"signature extraction" step**: HSS produces continuous sound, but *Loom* drafts are short discrete motifs — so sample each function at ~4–8 key points to keep every spell short and memorable.
- **Difficulty ramp = the ear-training curriculum:** early spells maximally different (linear vs. sine), later spells subtly different (sine vs. damped sine).
- **Hear-and-cast, two-player:** one player hears/describes a signature, the other reproduces ("casts") it on an on-screen distaff (keyboard keys / controller buttons) — naturally co-op. ❤️
- **Two-program split:** an offline **spell compiler** (function → note data, e.g. JSON) and an in-game **player** that just loads and plays compiled spells (no math at play-time).
- Respect the book's hard-won pitfalls (siren sounds §3.4; mapping mistakes §5.2) so we don't repeat old errors.

**Which "mountain"/idea LOOM teaches** (function recognition by ear / the sonification idea itself, or a specific named problem) is an OPEN QUESTION for Nir — don't assume; ask.

---

## 3. HOW WE BUILD (the assembly line) — and why the BIBLE must be excellent

- **Nir** — the boss. Decides everything; carries text between separate AI chats by copy-paste. **Nir knows no code and no math.** Nothing we design may require Nir to understand a proof, read code, or do math. His role is mechanical: paste, run, install, and judge by eye/ear.
- **You, Claude Fable** — founding architect. You write **documents**: the master doctrine (this mission), then a deep design of the hardest parts, then a build-tool spec. You reason deeply about code/audio, but your *output* is design docs, not a finished codebase. (You code better than the older models that wrote the book's original code, so we'll rewrite fresh and better — but through the pipeline below.)
- **Future "parent" chats (Claude Opus)** — fresh Opus chats that each receive your BIBLE **in full** plus need-to-know extras, and design one area in depth.
- **"Child" chats** — fresh chats that each implement ONE module to a frozen spec + tests, then are discarded.
- **DeepSeek (in OpenCode on Nir's Windows PC)** — has internet + agentic access to the PC and the GitHub repo (github.com/strulovitz/peaktogether-website). DeepSeek stitches together the copy-pasted Python blocks you and the Opus parents produce, answers your questions, writes summaries, fixes bugs, runs tests, and pushes to GitHub. (You and the Opus parents don't have that access here — DeepSeek is your hands.) DeepSeek prepared this prompt.

**Why the BIBLE matters:** every future parent starts with zero memory and gets your BIBLE as their single source of truth. Precise + complete BIBLE = a coherent project; vague BIBLE = drift and contradiction.

### Iron rules for everything you write
- **Honesty first.** Invent nothing. Mark genuinely undecided things as **OPEN QUESTIONS** instead of papering over them. Don't assert external library/API details from memory as certain — define our own conventions and let the compile/test loop confirm externals later.
- **Formatting for copy-paste.** Anything transferred between chats must be **prose or fenced code blocks — NEVER Markdown tables** (tables lose their cells when Nir copies them). Use bullet lists.
- **Ask only the few load-bearing questions** you truly need, batched, before writing.
- **Audience:** curious young adults / couples (co-op "date night for your brain"). It's not for small children, so a tasteful full emotional palette is available — but the tone stays warm, friendly, and never punishing (wrong answers → gentle explanation).
- **Tech reality (important):** Peak Together games are **downloadable and run locally**, like Descent QED which runs via `python app.py` from GitHub — they are **not** browser/web games. So assume a **Python** desktop stack (Windows-first) with WAV sample playback, matching the existing Arcade. If you want to argue for something else, flag it as an OPEN QUESTION for Nir; don't silently assume web/Web-Audio.

---

## 4. YOUR MISSION NOW — WRITE THE LOOM BIBLE (the "Old Testament")

Write the **complete foundational doctrine** for LOOM — the master document every future architect reads in full before touching anything. Make it thorough, self-consistent, and unambiguous. Cover the substance of these (rename/reorganize sections as you see fit):

1. **Vision & pillars** — LOOM in one breath; 3–5 design pillars; the player fantasy; how it honors the original *Loom* while being new; how it fits Peak Together (educational-first, co-op, warm tone).
2. **The core loop** — moment-to-moment play: what the player hears, sees, and does; how "hearing a function" and "casting a spell" work; feedback (and the no-punishment / gentle-explanation principle).
3. **Co-op design** — the two-player, one-screen split for LOOM specifically (who does what; why you must talk to win); and how solo play still works.
4. **The sonification engine (the heart)** — a precise, implementable description of how a function becomes a playable spell: sampling / signature extraction, the helical pitch mapping, scale quantization, timbre, rhythm, dynamics/emotion, and how Philharmonia samples are chosen/pitched/triggered. Define every knob (parameter) and its meaning.
5. **The spell format** — the canonical data model for a compiled spell (what a spell *is* as data) so the compiler can write it and the player can play it. Give concrete field names + a schema **as a fenced code block** (not a table). Include versioning.
6. **The two-program architecture** — offline **spell compiler** vs. in-game **player**: responsibilities, boundary, what crosses between them, and why the runtime stays "dumb" (no math at play-time).
7. **Content: the spellbook & progression** — the function catalog, what each teaches the ear, the difficulty ramp (max-different → subtly-different), and how new mechanics/functions unlock. Ensure no two required spells are perceptually confusable at the same tier.
8. **Game modes & structure** — story/campaign, comparative/quiz "by-ear" challenges, hear-and-cast co-op, practice "laboratory," any harder tier — define each. Consider a Peak-Together "Understanding Mode" analog.
9. **Emotional & audio design** — how the book's emotional-shading toolbox is used tastefully (feedback, tension, mood) for this warm, couple-friendly, educational game; the overall audio aesthetic with real instruments.
10. **Accessibility** — how the game stays meaningful and playable by ear; what visual support exists and why (the pitch helix could be a signature on-screen visual).
11. **Tech stack & architecture** — your recommendation (with reasoning) for building the compiler and the player as a **Python desktop app** (Windows-first, `python app.py`-style, WAV playback), consistent with the rest of the Arcade and with DeepSeek's integration workflow. Flag uncertainties as OPEN QUESTIONS.
12. **Locked decisions vs. open questions** — end with two explicit lists: what you're freezing, and what still needs Nir's call (include "which mountain/idea does LOOM teach?").

Write it as one cohesive document in your reply, defining your terms, since it will be saved verbatim and handed to future architects.

---

## 5. AFTER THE BIBLE (same conversation) — the "New Testament"

Once the BIBLE is settled, I'll ask you to design **in full technical detail the 1–3 hardest / riskiest parts** (you propose which — likely the sonification engine and/or the spell format/compiler). This is the deep-dive companion to the BIBLE.

## 6. LATER — a build tool (the "Apocrypha")

After that, I'll ask you to specify **one build tool** (a "spell compiler" spec) so fresh implementer chats can build spells in parallel from a simple, well-defined input format.

Please don't start Parts 5 or 6 yet — just acknowledge they're coming. **For now: state your plan + any load-bearing questions, then write the BIBLE.**

---

## 7. YOUR MEMORY OF THE BOOK (pasted below by Nir)

Directly beneath this line, Nir will paste the full set of chapter-by-chapter summaries you wrote (front matter + Chapters 1–10) plus the running "master summary." That is your complete memory of the book's method — rely on it.

⬇️ (summaries pasted here by Nir) ⬇️
