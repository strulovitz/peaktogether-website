# LOOM — PARENT 2 — REAL INSTRUMENTS, ON THE RECORD — BY FABLE (VERBATIM)

> Saved by DeepSeek **word-for-word, as-is** (chat UI chrome only removed).
> Fable's signed, on-the-record answer to Nir's four questions guaranteeing the
> finished game uses the REAL Philharmonia instrument MP3s (never beeps/synth).
> Nir's question message treated as the source of truth. Dated **July 6, 2026.**

---

Nir — DeepSeek is right to put this on the record, and I'm happy to sign it. This worry is exactly the kind that should be locked down in writing. Here are the four answers, treating THIS message as the source of truth: 🎻

1. Real instruments — confirmed, and it's already unbreakable doctrine. The finished game plays your real Philharmonia MP3 recordings, verbatim, with their original filenames — never beeps, never sine waves, never synthesis. This isn't just my promise; it's LOCKED in BIBLE §7.3 and §15: "verbatim Philharmonia MP3s with original filenames... no pitch-shifting ever... no runtime DSP." Stronger still: there is no synthesizer anywhere in the Player's design. The only thing the audio engine knows how to do is "load this MP3 file into memory and play it." It literally has no code path that could produce a beep. A beep in the finished game isn't a risk we're avoiding — it's a thing the architecture cannot do.

2. Exactly where in the code a note becomes a real file — the full chain, module by module:

    loom/compiler/library_scan.py (Program A, on your PC): scans your C:\Users\nir_s\Downloads\philharmonia\ folders and picks, for each note of each spell, one concrete file — e.g. violin_C4_1_forte_arco-normal.mp3. This is the ONE place in the entire project where "a note" is turned into "a filename."
    The Compiler writes that exact filename into the spell JSON — the "sample" field of each note — and copies the file into the pack's audio/ folder.
    loom/player/core/spell_model.py (already delivered, Part 1): reads that filename into SpellNote.sample. It chooses nothing; it carries the Compiler's choice.
    loom/player/ui/audio_pygame.py (coming in Part 2): preload() decodes those exact MP3s into memory at load time; trigger() plays them. M0 already proved this works on your machine (your violin and oboe scales — "notes fire instantly").

So: the Compiler chooses, the JSON remembers, the Player obeys. No module ever improvises a sound.

3. Beeps — I'm demoting them below even what you feared. Here is the honest truth about why beeps existed in the plan at all: so automated tests could run on a machine that doesn't have your 20-folder library. But look — the headless tests use FakeAudioSink, which records trigger calls and never opens an audio file at all. So the tests don't need beeps either! The only remaining purpose of make_beeps.py is: emergency scaffolding for some hypothetical future machine with no library (it stays in the repo for that, clearly labeled "never used when the real library is present"). There is no milestone where beeps are the plan and real instruments come "later." Real instruments arrive at M1 — the first demo — because your machine has the library and M0 already proved pygame loads it.

4. Yes — the very first thing you touch will be a real violin. I'm building Part 2 exactly this way: the M1 demo takes a --library argument defaulting to C:\Users\nir_s\Downloads\philharmonia\, and at startup it resolves each fixture note to a real file in your violin folder (tolerantly, the way the Commentaries recorded your filename grammar: violin_C4_*_forte_arco-normal.mp3, preferring the longer recorded lengths so scrubbing has a beautiful natural decay to play with). The second fixture will use a second real instrument — I'll use oboe, since M0 already ear-verified both. If a file is missing it stops with a plain-language message naming the note and the folder — it will never silently fall back to a beep. Your first drag across the timeline = real violin ringing under your hand. 🎻

One small honest note, so nothing is oversold: which length variants (the 025/05/1/15/2 tokens) exist for each individual note in your folders, I cannot know from here — that's why the demo searches tolerantly instead of hardcoding, and why the message-on-failure names exactly what it looked for. That's the Iron-Rule way: I define the convention, DeepSeek's run on your real folders confirms it.

We are on the same page — and the page is now on the record for DeepSeek to hold me to. 💪

Say "continue" and Part 2 arrives: the pygame audio engine, the two fixture melodies (violin + oboe), the real-library resolver, the demo window, and the test suite. 😊
