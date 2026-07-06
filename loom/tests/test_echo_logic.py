"""Headless tests for core/echo_logic.py (M3). Style: test_conductor.py —
pure logic, no pygame, no audio, spells built directly in memory."""

import pytest

from player.core.spell_model import SpellData, SpellNote
from player.core.echo_logic import (
    EchoLogic, EchoPhase, SLOT_CONFIRMED, SLOT_PROVISIONAL,
    SLOT_PLACEHOLDER,
)


def make_spell(midis):
    notes = tuple(
        SpellNote(index=i, midi=m, start_beat=float(i), duration_beats=1.0,
                  sample=f"audio/fake_{i}.mp3", gain=1.0)
        for i, m in enumerate(midis))
    return SpellData(spell_id="test", bpm=110.0, notes=notes,
                     total_beats=float(len(midis)), raw={})


MELODY = (60, 64, 67, 72)   # C4 E4 G4 C5


# ---------------- construction ----------------

def test_bad_reveal_mode_raises():
    with pytest.raises(ValueError):
        EchoLogic(make_spell(MELODY), reveal_mode="banana")


def test_initial_grow():
    e = EchoLogic(make_spell(MELODY), "grow")
    assert e.phase() is EchoPhase.LISTENING
    assert e.notes_to_play() == (0,)
    assert e.prefix_len == 1
    assert e.cursor == 0
    assert e.preview_midi is None
    assert e.slot_states() == (SLOT_PLACEHOLDER,) * 4


def test_initial_whole():
    e = EchoLogic(make_spell(MELODY), "whole")
    assert e.notes_to_play() == (0, 1, 2, 3)
    assert e.prefix_len == 4


# ---------------- phase transitions ----------------

def test_listening_finished_and_stray_calls():
    e = EchoLogic(make_spell(MELODY))
    e.preview(60)                     # stray during LISTENING: ignored
    assert e.preview_midi is None
    e.listening_finished()
    assert e.phase() is EchoPhase.ECHOING
    e.listening_finished()            # idempotent no-op
    assert e.phase() is EchoPhase.ECHOING


def test_cancel_is_always_harmless():
    e = EchoLogic(make_spell(MELODY))
    e.cancel()                        # LISTENING: no-op
    e.listening_finished()
    e.cancel()                        # ECHOING, nothing to cancel: no-op
    e.preview(64)
    e.cancel()
    assert e.preview_midi is None


# ---------------- preview ----------------

def test_preview_overwrites_and_shows_in_slots():
    e = EchoLogic(make_spell(MELODY))
    e.listening_finished()
    e.preview(62)
    e.preview(64)                     # overwrite is fine (re-audition)
    assert e.preview_midi == 64
    assert e.slot_states()[0] == SLOT_PROVISIONAL
    assert e.slot_states()[1:] == (SLOT_PLACEHOLDER,) * 3


# ---------------- commit: guards ----------------

def test_commit_without_preview_raises():
    e = EchoLogic(make_spell(MELODY))
    e.listening_finished()
    with pytest.raises(ValueError):
        e.commit()


def test_commit_outside_echoing_raises():
    e = EchoLogic(make_spell(MELODY))
    with pytest.raises(ValueError):
        e.commit()


# ---------------- commit: judgment ----------------

def test_wrong_commits_gentle_and_unlimited():
    e = EchoLogic(make_spell(MELODY))
    e.listening_finished()
    for guess, kind in ((72, "too_high"), (50, "too_low"), (61, "too_high")):
        e.preview(guess)
        r = e.commit()
        assert (r.kind, r.target_index, r.puzzle_done) == (kind, 0, False)
        assert e.phase() is EchoPhase.ECHOING       # never thrown out
        assert e.preview_midi is None               # the note gently fades
        assert e.cursor == 0                        # strict order holds
    e.preview(60)                                   # still welcome to win
    assert e.commit().kind == "correct"


def test_grow_full_walkthrough():
    e = EchoLogic(make_spell(MELODY), "grow")
    for round_no in range(4):
        assert e.phase() is EchoPhase.LISTENING
        assert e.notes_to_play() == tuple(range(round_no + 1))
        e.listening_finished()
        assert e.cursor == round_no                 # only the NEW note
        e.preview(MELODY[round_no])
        r = e.commit()
        assert r.kind == "correct"
        assert r.target_index == round_no
    assert r.puzzle_done is True
    assert e.phase() is EchoPhase.COMPLETE
    assert e.slot_states() == (SLOT_CONFIRMED,) * 4
    assert e.notes_to_play() == (0, 1, 2, 3)        # the reward replay
    assert e.cursor is None


def test_whole_full_walkthrough_no_relisten():
    e = EchoLogic(make_spell(MELODY), "whole")
    e.listening_finished()
    for i, midi in enumerate(MELODY):
        assert e.phase() is EchoPhase.ECHOING       # never back to LISTENING
        assert e.cursor == i
        e.preview(midi)
        r = e.commit()
        assert r.kind == "correct"
    assert r.puzzle_done is True
    assert e.phase() is EchoPhase.COMPLETE


def test_single_note_spell_completes_immediately():
    e = EchoLogic(make_spell((60,)), "grow")
    e.listening_finished()
    e.preview(60)
    r = e.commit()
    assert r.puzzle_done is True
    assert e.phase() is EchoPhase.COMPLETE


def test_complete_is_final():
    e = EchoLogic(make_spell((60,)), "whole")
    e.listening_finished()
    e.preview(60)
    e.commit()
    e.preview(64)                     # stray after COMPLETE: ignored
    assert e.preview_midi is None
    with pytest.raises(ValueError):
        e.commit()


def test_confirmed_slots_survive_grow_relisten():
    e = EchoLogic(make_spell(MELODY), "grow")
    e.listening_finished()
    e.preview(60)
    e.commit()
    assert e.phase() is EchoPhase.LISTENING         # round 2 replay
    assert e.slot_states()[0] == SLOT_CONFIRMED     # stays locked
    assert e.slot_states()[1] == SLOT_PLACEHOLDER
