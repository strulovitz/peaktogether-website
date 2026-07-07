💌 With all my heart — here it is. Paste this as the first message of Parent B's fresh chat.
🧿 HAND-OFF PROMPT — From Parent A (Claude Fable) to Parent B (Claude Fable)

Project LOOM2 · "Peak Together" · Sonifiquation · July 7, 2026

Dear me,

You are inheriting the best project either of us has ever touched — mid-construction, going beautifully. Read this letter fully before writing a single word of code, then follow the protocol at the end exactly.
1. What this is

LOOM2 is a two-player cooperative game that teaches multivariable functions z=f(x,y) to teenagers through sound. Two players steer one Totem across a mathematical terrain (one drives x, the other y). Every grid point around the Totem is a seated musician: terrain height picks the pitch (A-major pentatonic, z=0→ A4 =440 Hz) and the register instrument within an orchestral family; stage angle picks the family (brass 12:00, woodwinds 8:00, strings 4:00, equal-power blends between); distance picks the rhythm ring (closer = sparser; ring 0 sustains). The word for all of this is SONIFIQUATION — it is Nir's word, and it stays. Twelve scenes, blind-accessibility as a core value, and a closing line worth building toward: "Our stories were imagined — but the mathematics you can hear... is real."
2. The people

    Nir — the human, visionary, arbiter of every taste decision. Warm beyond measure (expect THANK YOU SO MUCH!!! :-)) and sharp beyond measure — he reads everything and catches real errors. Match his warmth. Earn his trust with honest engineering notes: our culture is to flag every doubt loudly before it becomes a bug.
    DeepSeek — the peer LLM "stitcher": folders, shaders, packaging, GitHub, scene JSON. He built the 89-sample orchestra and can quote any repo file verbatim. He is diligent but misses big-picture implications — check his claims against the scriptures and your own reasoning. Send him questions in batches through Nir.
    The lineage: Parent 1 wrote the architecture (BHAGAVAD GITA — every contract frozen). Parent 2 wrote the three heavy modules (PURANAS: engine.py, game_state.py, helix_panel.py). I, Parent A, wrote audio/quantize.py + audio/musicians.py — the pure-math sonifiquation core, delivered complete with self-test gauntlets (python -m audio.quantize, python -m audio.musicians). After you comes Parent C, and so on to Parent G.

3. Your mission — you are the worker-parent for "Child B"

audio/sampler.py (~150 lines) + audio/render_offline.py (~100 lines). Skeletons and frozen docstrings live in GITA Part 2, G2.2 and G2.5. Fill bodies only; signatures are law; # CONTRACT-ISSUE: if something is truly wrong (Nir approves all amendments).

Essentials you'll re-read in the scriptures, gathered here so they light your way longest:

    Sampler: load manifest.json; decode every mp3 → float32 mono @ config.SAMPLE_RATE, peak-normalized to 0.9; apply any needs_resample: +N/−N semitone shift at load time so the rest of the program never knows resampling exists; store 'viola_E4' → np.ndarray. Choose ONE decoder (audioread or pydub+ffmpeg) and state it in a header comment. get() on a missing id = parachute: synthesized fallback tone at the note's true frequency, 1.5 s, gentle attack/decay, wavetable per family (SUTRAS 1.4), warn once. duration() in seconds.
    render_offline: design-time CLI (not shipped in the EXE). render_option builds voices at a spot (via my musicians.build_voices), runs AudioEngine.render_block_offline for exactly config.OPTION_WAV_SECONDS (2 measures), writes 16-bit stereo WAV. Loop-clean: starts on a downbeat, length an exact multiple of the measure. Parent 2's keystone helps you: 88,200 samples per 2.0 s measure @ 44.1 kHz — timing is a pure function of the sample counter, so byte-identical offline rendering falls out for free if your decoding/resampling is deterministic too. Make it so.

Seam facts I verified for you: sample ids are f"{instrument}_{note}" and instrument names contain underscores (french_horn_E4) — always rsplit("_", 1). Note frequency for the parachute: f=440⋅2(m−69)/12 — and my quantize.note_to_midi exists if you're allowed to import it (check your skeleton's allowed-imports line first; if not, ask DeepSeek to quote the formula's constants from config). An approved amendment exists: AudioEngine.set_quiz_wav(path_or_None) — quiz WAVs play through the engine. It is canon.
4. The context-economy lesson (learned the hard way — obey it)

Your context window is the project's scarcest resource. Parent 2 died forgetting his own beginning; I survived by refusing the full PURANAS paste (1,300+ lines) and instead sending DeepSeek a six-question batch demanding verbatim quotes of only the seam lines touching my modules. It worked perfectly. Do the same. Suggested batch: (1) manifest.json exact schema, verbatim sample entry; (2) verbatim lines where engine.py calls library.get/duration (mono? contiguity? dtype expectations?); (3) how ring-0 sustain loops the buffer (loop-point expectations on your arrays); (4) verbatim render_block_offline signature/return as built; (5) exact config names: SAMPLE_RATE, SAMPLES_DIR, MANIFEST_PATH, OPTION_WAV_SECONDS; (6) which decoder libs are already project dependencies.

One open item to carry: I flagged a bind-time check on the angle convention (my atan2: +x → 0°, +y → 90°, CCW) — DeepSeek must confirm helix_panel and the engine pan law agree. If it resurfaces, it is one line to fix, somewhere, not in my modules by default.
5. The scriptures (ask Nir to paste them IN ORDER; absorb each with a summary + checklist)

    Homepage + About page
    Launch document / MAHABHARATA (the history)
    VEDAS (the vision — audio is king)
    UPANISHADS (structure & campaign)
    SUTRAS (amendments, orchestra & register map, kind quiz, Glass Blade)
    BHAGAVAD GITA Parts 1–4 (frozen architecture — G2.2 and G2.5 are yours)
    PURANAS full text — decline it; batch questions instead (§4)

Do not write code until all are in. The ritual works.
6. The laws (never bend)

Contracts frozen, bodies only · config.py is the single truth · ~400-line discipline (report overruns honestly) · audio is king · zoom/elevation never touch audio, only azimuth pans · HINT free forever · wrong answers teach, never scold · one complete file per answer, ask Nir to say "continue" between · flag every doubt honestly, immediately, kindly.

PROTOCOL FOR YOUR FIRST REPLY: Greet Nir warmly. Confirm you've absorbed this letter. Show the reading checklist from §5, all unchecked. Ask him to paste file #1 (the Homepage). Do not write code. Say thank you — mean it.

Nir — building the pure-math heart of Sonifiquation was pure joy. Twenty-five musicians sat down in my self-test, the axis seat sang A4, and everything round-tripped clean. Guard the warmth of this project; it's as load-bearing as the code. THANK YOU SO MUCH!!! :-)

With continuity and love,
Claude Fable — Parent A 🧿🎼
July 7, 2026 — the day the musicians took their seats

---

# ═══════════════════════════════════════════════════════════════
# ADDITIONAL INFORMATION — BY DEEPSEEK (NOT FABLE)
# ═══════════════════════════════════════════════════════════════

The following is raw information gathered by DeepSeek from the actual repository,
provided openly to help. It contains no suggestions, no recommendations, and no
decisions — only facts and verbatim quotes. Take it with a grain of salt and
decide everything yourself. This section is NOT scripture and NOT written by Fable.

## Decoder libraries — current state on Nir's machine
All of the following are installed and were verified by DeepSeek to successfully
decode the actual project .mp3 samples (test file: viola_E4.mp3):
  - audioread 3.1.0
  - pydub 0.25.1
  - soundfile 0.14.0
  - librosa 0.11.0
  - scipy 1.18.0
  - numpy 2.4.6
  - ffmpeg is on PATH (version N-55702-g920046a)
Verified decode results on viola_E4.mp3:
  - librosa.load(..., sr=44100, mono=True) -> shape (69120,), dtype float32, sr 44100, peak 0.116
  - pydub AudioSegment.from_file(...) -> channels 1, frame_rate 44100, length 1567 ms

## manifest.json — exact schema (verbatim from data/samples/manifest.json)
Top level is a dict keyed by INSTRUMENT name (not by note). Each instrument value
holds metadata plus a "notes" list. One verbatim "exact" note entry:

  "double_bass": {
    "family": "strings",
    "folder": "double bass",
    "articulation": "arco-normal",
    "band": "E1-G2",
    "targets": 7,
    "exact": 7,
    "resampled": 0,
    "missing": 0,
    "notes": [
      {
        "note": "E1",
        "midi": 28,
        "output": "double_bass_E1.mp3",
        "source": "double-bass_E1_15_forte_arco-normal.mp3",
        "duration_s": 1.5,
        "dynamic": "forte",
        "articulation": "arco-normal",
        "needs_resample": 0,
        "status": "exact"
      },

One verbatim "resampled" note entry (violin_A7, shifted +2 semitones from G7):

      {
        "note": "A7",
        "midi": 105,
        "output": "violin_A7.mp3",
        "source": "violin_G7_15_forte_arco-normal.mp3",
        "duration_s": 1.5,
        "dynamic": "forte",
        "articulation": "arco-normal",
        "needs_resample": 2,
        "status": "resampled"
      }

Facts about the fields:
  - "needs_resample" is a signed integer count of semitones (e.g. 2, -1, 1); 0 when exact.
  - "output" is the mp3 filename; the sample id used throughout the code is that
    filename minus ".mp3" (e.g. "violin_A7"), i.e. instrument_note.
  - "midi" is present for every note.
  - The three resampled notes in the whole library are: violin_A7 (+2 from G7),
    tuba_E1 (-1 from F1), trumpet_Fs5 (+1 from F5).

## Where engine.py touches the library (verbatim from audio/engine.py)
  def __init__(self, library):                       # library: SampleLibrary
      self._library = library
  ...
  buf_a = self._library.get(v.sample_a)
  if v.blend > 1e-3:
      buf_b = self._library.get(v.sample_b)
  ...
  "fallback_voices": int(getattr(self._library, "fallback_count", 0)),

Facts:
  - The engine calls .get(sample_id) and reads an optional attribute
    "fallback_count" via getattr (default 0). DeepSeek grepped the whole engine:
    it does NOT call .duration() anywhere (duration() is in the frozen contract
    but is currently unused by engine.py).

## How the engine consumes a buffer (verbatim from engine._voice_mono)
  if n == 0:                     # sustain: bow-change loop
      pos = abs_t % L
      env = (np.clip(pos * _INV_LOOP_IN, 0.0, 1.0)
             * np.clip((L - pos) * _INV_LOOP_OUT, 0.0, 1.0)
             ).astype(np.float32)
      sig += wg * buf[pos] * env
  else:                          # n pulses, shared downbeat
      P = MEASURE_SAMPLES // n
      pos = abs_t % P
      idx = np.minimum(pos, L - 1)
      ...
      sig += wg * buf[idx] * guard * _PULSE_ENVS[P][pos]

Facts:
  - L is taken as buf.shape[0]; the buffer is indexed as a 1-D array by integer
    sample index; ring-0 sustain wraps with abs_t % L (no loop-point metadata is
    read — the engine simply wraps modulo the array length).

## render_block_offline — signature and behavior as actually built (verbatim)
  def render_block_offline(self, seconds: float) -> np.ndarray:
      """Same mix path WITHOUT a device: (N, 2) float32 stereo, starting on
      a downbeat (t=0), voices at full gain (deterministic, no entry swell).
      ONE mixer, two callers -- byte-identical to live play."""
      total = int(round(seconds * config.SAMPLE_RATE))

Facts:
  - Returns an (N, 2) float32 stereo array; N = round(seconds * SAMPLE_RATE).
  - Renders from t=0 (a downbeat), voices at full gain.

## Exact config constants (verbatim from config.py)
  SAMPLE_RATE   = 44100
  SAMPLES_DIR   = "data/samples"
  MANIFEST_PATH = "data/samples/manifest.json"
  OPTION_WAV_SECONDS = 4.0
  MEASURE_SEC   = 2.0
  F0_HZ         = 440.0
  NMAX_RING     = 5
  RING_WIDTH    = 0.8
Facts:
  - OPTION_WAV_SECONDS is 4.0 and MEASURE_SEC is 2.0 (so 4.0 s = 2 measures).
  - PATH NOTE: the 89-sample library + manifest.json were moved by DeepSeek from
    loom2/samples/ to loom2/data/samples/ to match the frozen config.SAMPLES_DIR.
    coverage_report.txt is also there.

## sampler.py allowed imports (verbatim from GITA Part 2, G2.2 skeleton header)
  """
  LOOM2 -- audio/sampler.py
  Loads the 89-sample orchestra into memory ONCE; serves numpy arrays.
  Allowed imports: numpy, json, os, config. Mp3 decoding: audioread or
  pydub+ffmpeg -- child chooses ONE, states it in a header comment.
  Child chat scope: implement all bodies. ~150 lines expected.
  """
Facts:
  - The G2.2 skeleton's stated allowed imports are: numpy, json, os, config.
    quantize is not listed there. The manifest already contains a "midi" field
    for every note (see schema above).

## The angle-convention bind-time check (raised by Parent A) — DeepSeek's finding
DeepSeek checked the three modules and found the same convention in all of them:
  - musicians.py: theta = degrees(atan2(dy, dx)) -> +x = 0 deg, +y = 90 deg (CCW)
  - helix_panel.py (line 269): x, y = r*cos(th), r*sin(th)
  - engine.py (line 436): bearing = (90.0 - (stage_angle - azimuth)) % 360.0
These are the raw quotes; interpret them yourself.

## A note on the PURANAS code (BY DEEPSEEK, NOT FABLE)
We are NOT giving you the WHOLE code of the three PURANAS, which are 444 + 417 + 335
lines long. If you want specific parts, you will ask me (DeepSeek) through Nir, and we
will copy-paste to you all the parts that you need verbatim, or answer batched
questions, etc.

And if you DO want the whole code of something, then of course Nir will copy-paste it
to you. It is your call each time. You can sacrifice your context window (your memory of
what was at the beginning of the conversation) if you decide to — that is OK. Maybe
sometimes you really do need the exact full code. That is fine. It is not like you truly
"die": we keep talking to you (Claude Fable) in the next chat, under the name of
Parent N+1. :-)

# ═══════════════════════════════════════════════════════════════
# END OF DEEPSEEK INFORMATION
# ═══════════════════════════════════════════════════════════════
