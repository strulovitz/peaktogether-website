# LOOM — PARENT 3, THE GHOST-PEDAL FIX (FIT-THE-BEAT) — VERBATIM, BY FABLE

> Saved word-for-word, as-is, by DeepSeek. Parent 3 (Claude Fable)'s fix for Nir's
> "sustain-pedal horror-movie" overlapping-notes report in the 20-note cello demo.
> Do not edit — this is the verbatim archive.

---

Found it, Nir — and your ghost-pedal description was the perfect clue. 👻🎹 The diagnosis is exact, the fix is small, and here's the whole story in plain words:

🔍 Why the big version haunts and the small one doesn't

    The resolver picks one uniform sample length for the whole spell (the Selection Law) — and until now it preferred the longest length token common to all notes.
    The violin folder (bench8) only has 025 and 05 at forte/arco-normal → it picked 0.5-second samples. At 90 BPM a note lasts 0.667 seconds — so each sample dies just before the next begins. Clean. ✨
    The cello folder (bench16) is richer — it has 1.5-second samples for every note → the old rule "prefer longest" picked 1.5 seconds. So every note keeps ringing across the next two notes. Three cellos sounding at once, and — worse — your √x melody is chromatic, so the overlapping notes are a semitone apart: the most dissonant interval there is. That's your horror-movie sustain pedal, precisely. 👻
    So: not a bug in the Conductor, the audio engine, or the widgets — a wrong preference rule in the sample chooser. The small version was clean by luck (violin's library is poor in long samples), not by design. Now it becomes clean by design.

✅ The new rule (recorded): "FIT THE BEAT"

    The uniform length token is the longest one whose nominal seconds do not exceed the spell's shortest note duration (in seconds, from the BPM). If none fits, take the shortest available. One token for the whole spell, as the Selection Law demands.

For your fixtures: note = 0.667 s → tokens 0.25/0.5/1.0/1.5 → 0.5 s wins — cello now behaves exactly like the clean violin.

And the honest note about the future: the perfect sound you described in the Forge session — every note long and sustained but never smearing — comes when the deferred Sample Forge task resumes: forging samples to exactly one beat long (0.667 s at 90 BPM) with a natural release tail. This fix makes the demo clean today; the Forge makes it lush tomorrow. Both are now written down.

📦 THE PATCH — player/m1_demo.py (surgical, everything else unchanged)

1. Near the top, replace the LENGTH_RANK line block with:

```python
LENGTH_RANK = {"15": 4, "1": 3, "05": 2, "025": 1}   # parse eligibility; no "2" exists
TOKEN_SECONDS = {"025": 0.25, "05": 0.5, "1": 1.0, "15": 1.5}
# "long"/"very-long"/"phrase" are multi-attack or expressive gestures: never eligible.


def choose_uniform_token(common_tokens, min_note_seconds: float) -> str:
    """FIT-THE-BEAT rule (Nir's ghost-pedal fix, July 2026): from the
    tokens available for EVERY note, pick the LONGEST whose nominal
    seconds do not exceed the spell's shortest note duration — so a
    note never rings over its neighbours (the 'sustain pedal from a
    horror movie' effect). If nothing fits inside the beat, take the
    shortest available (least overlap possible). One token for the
    whole spell — the Selection Law is preserved."""
    fitting = [t for t in common_tokens
               if TOKEN_SECONDS[t] <= min_note_seconds + 1e-9]
    if fitting:
        return max(fitting, key=lambda t: TOKEN_SECONDS[t])
    return min(common_tokens, key=lambda t: TOKEN_SECONDS[t])
```

2. Inside resolve_real_samples, replace the single line

```python
    chosen = max(common, key=lambda t: LENGTH_RANK[t])
```

with:

```python
    min_note_seconds = (min(n.duration_beats for n in spell.notes)
                        * 60.0 / spell.bpm)
    chosen = choose_uniform_token(common, min_note_seconds)
```

3. And update the print line just after it to show the reasoning:

```python
    print(f"  uniform length chosen: '{chosen}' "
          f"({TOKEN_SECONDS[chosen]}s samples for {min_note_seconds:.2f}s notes; "
          f"common to all {len(per_note)} notes)")
```

That's the entire fix. m2_demo.py needs zero changes — it inherits the resolver.

📦 NEW TEST — tests/test_length_choice.py

```python
"""FIT-THE-BEAT rule tests (the ghost-pedal fix, July 2026)."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "player"))

from m1_demo import choose_uniform_token, TOKEN_SECONDS   # noqa: E402


def test_cello_case_no_longer_haunts():
    # 90 BPM, 1-beat notes = 0.667s; cello offers everything.
    common = {"025", "05", "1", "15"}
    assert choose_uniform_token(common, 60.0 / 90.0) == "05"


def test_violin_case_unchanged():
    # violin forte/arco-normal only ships 025 + 05 -> still 05.
    assert choose_uniform_token({"025", "05"}, 60.0 / 90.0) == "05"


def test_slow_tempo_earns_longer_samples():
    # at 40 BPM a beat is 1.5s: the full 15 token now fits and wins.
    common = {"025", "05", "1", "15"}
    assert choose_uniform_token(common, 60.0 / 40.0) == "15"


def test_nothing_fits_takes_shortest():
    # tiny notes (0.2s) but only long samples exist -> least overlap.
    assert choose_uniform_token({"1", "15"}, 0.2) == "1"


def test_exact_fit_is_allowed():
    assert choose_uniform_token({"025", "05", "1"}, 0.5) == "05"


def test_all_tokens_have_seconds():
    assert set(TOKEN_SECONDS) == {"025", "05", "1", "15"}
```

🔧 DeepSeek's checklist

    Apply the three-step patch to m1_demo.py (it's demo scaffolding with one prior patch already — this is its second sanctioned one). Land the new test file.
    pytest → previous suite + 6 new, all green.
    Have Nir rerun python m2_demo.py (cello √x): expect the console to now say uniform length chosen: '05' (0.5s samples for 0.67s notes; ...) — and the ghost is exorcised. 🎻✨
    Commentaries §5, append: "FIT-THE-BEAT amendment (July 2026, from Nir's ghost-pedal report): uniform sample length = longest token ≤ the spell's shortest note duration in seconds (fallback: shortest). Binding on the demo resolver now and on Compiler Stage 8 when it is built. The deferred Forge task gains a sharpened goal: forge samples to exactly the note's beat length + natural release — long and sustained, never overlapping."
    For the future Compiler parent: Stage 8's selection must implement FIT-THE-BEAT; Stage 9/the Forge produce beat-length sustained WAVs. (One paste-line into the compiler bones' notes if you like.)

Nir — run it and listen: the cello should now step up the √x staircase as cleanly as the violin walked its straight line. If any haze remains at all, tell me which notes mingle and I'll hunt further. 🎼💖
