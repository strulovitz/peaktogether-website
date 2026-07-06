"""The full M1 behavior suite — headless, deterministic, no audio files."""
import pytest

from core.audio import FakeAudioSink
from core.conductor import Conductor, ConductorState
from core.spell_model import SpellData, SpellNote
from core.tuning import ScrubTuning

T = ScrubTuning.default()   # guard 0.04, cap 4, retrigger 90 ms


def make_spell(spec=None, bpm=90.0):
    """spec: list of (start, duration); default = 8 flat notes."""
    spec = spec or [(float(i), 1.0) for i in range(8)]
    notes = tuple(SpellNote(i, 60 + i, s, d, f"s{i}.mp3", 0.9)
                  for i, (s, d) in enumerate(spec))
    return SpellData("test", bpm, notes, max(n.end_beat for n in notes), {})


GAPPY = [(0.0, 1.0), (1.0, 0.5), (1.5, 0.5), (2.5, 1.0), (3.5, 2.0)]  # rest [2, 2.5)


def collect(c, updates):
    """Run updates (list of dt seconds), return (frames, all crossed)."""
    frames = [c.update(dt) for dt in updates]
    crossed = [i for f in frames for i in f.crossed]
    return frames, crossed


def test_playing_advances_at_bpm():
    c = Conductor(make_spell(bpm=120), T)
    c.play()
    f = c.update(0.5)                       # 0.5 s at 120 bpm = 1 beat
    assert abs(f.playhead_beats - 1.0) < 1e-9
    assert f.state is ConductorState.PLAYING


def test_paused_and_stopped_hold_still():
    c = Conductor(make_spell(), T)
    for _ in range(3):
        assert c.update(0.1).playhead_beats == 0.0     # STOPPED
    c.play(); c.update(0.1); c.pause()
    ph = c.playhead_beats
    assert c.update(0.5).playhead_beats == ph          # PAUSED


def test_full_playback_fires_all_in_order_then_completes():
    c = Conductor(make_spell(), T)          # 8 beats at 90 bpm = 5.333 s
    c.play()
    frames, crossed = collect(c, [0.05] * 120)   # 6 s
    assert crossed == list(range(8))
    completes = [f for f in frames if f.completed]
    assert len(completes) == 1
    assert c.state is ConductorState.STOPPED
    assert c.playhead_beats == c.spell.total_beats


def test_playback_triggers_exactly_on_the_beat_no_guard():
    c = Conductor(make_spell(), T)
    c.play()
    f = c.update((1.0 + 1e-6) * 60 / 90)    # land a hair past beat 1.0
    assert 1 in f.crossed                   # guard must NOT delay playback


def test_play_after_end_rewinds():
    c = Conductor(make_spell(), T)
    c.play(); collect(c, [0.1] * 60)        # run to the end
    c.play()
    f = c.update(0.01)
    assert f.playhead_beats < 1.0 and 0 in f.crossed


def test_jump_fires_landing_note_only_and_keeps_state():
    c = Conductor(make_spell(GAPPY), T)
    c.play()
    c.jump_to_beats(2.7)                    # inside note 3
    f = c.update(0.0)
    assert f.crossed == (3,) and f.state is ConductorState.PLAYING
    c2 = Conductor(make_spell(GAPPY), T)
    c2.jump_to_beats(2.2)                   # inside the rest
    f2 = c2.update(0.0)
    assert f2.crossed == () and f2.active_note_index is None


def test_jump_respects_retrigger_min():
    c = Conductor(make_spell(), T)
    c.jump_to_beats(0.5); c.update(0.01)         # fires note 0; clock +10 ms
    c.jump_to_beats(0.6)
    assert c.update(0.01).crossed == ()          # 20 ms < 90 ms: suppressed
    c.update(0.2)                                # let the clock pass 90 ms
    c.jump_to_beats(0.7)
    assert c.update(0.0).crossed == (0,)


def test_scrub_guard_hysteresis_forward():
    c = Conductor(make_spell(), T)               # guard = 0.04 beats
    c.begin_scrub()
    c.scrub_to_beats(1.02)                       # past start, NOT past 1.04
    assert c.update(0.1).crossed == (0,)         # only note 0 (line at 0.04)
    c.scrub_to_beats(1.05)                       # now past 1.04
    assert c.update(0.1).crossed == (1,)


def test_scrub_backward_reverses_melody():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(8.0); c.update(0.2)         # sweep to the end (flushes)
    c.scrub_to_beats(0.0)
    f = c.update(0.2)
    assert list(f.crossed[-3:]) == [2, 1, 0]     # reverse traversal order


def test_boundary_jitter_cannot_machine_gun():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(1.10); c.update(0.2)        # fired notes 0 and 1
    for _ in range(20):                          # jitter +-0.02 around 1.08
        c.scrub_to_beats(1.06); c.update(0.02)
        c.scrub_to_beats(1.10); c.update(0.02)
    _, crossed = collect(c, [0.0])
    assert crossed == []                         # nothing refires


def test_lingering_never_retriggers():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(0.5); c.update(0.2)
    for _ in range(30):                          # wander INSIDE note 0
        c.scrub_to_beats(0.3); c.update(0.05)
        c.scrub_to_beats(0.7); c.update(0.05)
    _, crossed = collect(c, [0.0])
    assert crossed == []


def test_leave_and_reenter_refires_after_min_interval():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(0.5); c.update(0.2)         # fire note 0, clock +200 ms
    c.scrub_to_beats(1.5); c.update(0.2)         # leave (fires 1), re-arm 0
    c.scrub_to_beats(0.5)                        # re-enter from the right
    assert c.update(0.2).crossed == (0,)         # 200 ms > 90 ms: refires


def test_flurry_cap_trims_audio_not_visuals():
    c = Conductor(make_spell(), T)
    c.begin_scrub()
    c.scrub_to_beats(7.5)                        # one gesture across all 8
    f = c.update(0.1)
    assert f.crossed == tuple(range(8))          # the eye sees everything
    assert f.triggers == (4, 5, 6, 7)            # the ear gets the LAST 4


def test_end_scrub_is_paused_never_resumes():
    c = Conductor(make_spell(), T)
    c.play(); c.update(0.1)
    c.begin_scrub(); c.scrub_to_beats(3.2); c.end_scrub()
    f = c.update(0.5)
    assert f.state is ConductorState.PAUSED
    assert abs(f.playhead_beats - 3.2) < 1e-9


def test_active_note_index_tracks_regions_and_rests():
    c = Conductor(make_spell(GAPPY), T)
    c.jump_to_beats(1.7)
    assert c.update(0.0).active_note_index == 2
    c.jump_to_beats(2.2)
    assert c.update(0.0).active_note_index is None


def test_determinism_same_script_same_frames():
    def run():
        c = Conductor(make_spell(GAPPY), T)
        out = []
        c.play()
        out += [c.update(0.07) for _ in range(20)]
        c.begin_scrub()
        for b in (3.1, 0.4, 5.2, 2.2):
            c.scrub_to_beats(b); out.append(c.update(0.03))
        c.end_scrub()
        out += [c.update(0.07) for _ in range(5)]
        return out
    assert run() == run()


def test_wiring_with_fake_audio_sink():
    spell = make_spell()
    sink = FakeAudioSink()
    sink.preload("", spell.sample_paths)
    c = Conductor(spell, T)
    c.play()
    for _ in range(120):
        f = c.update(0.05)
        for i in f.triggers:
            sink.trigger(spell.notes[i].sample, spell.notes[i].gain)
    assert sink.triggered == [(f"s{i}.mp3", 0.9) for i in range(8)]


def test_set_bpm_changes_rate_not_position():
    c = Conductor(make_spell(bpm=120), T)     # 120 bpm
    c.play()
    c.update(0.5)
    pos = c.playhead_beats
    c.set_bpm(180.0)
    assert c.playhead_beats == pos                     # position untouched
    f = c.update(1.0)                                  # 180 bpm = 3 beats/s
    assert f.playhead_beats == pytest.approx(pos + 3.0, abs=1e-6)


def test_set_bpm_rejects_nonpositive():
    c = Conductor(make_spell(bpm=120), T)
    with pytest.raises(ValueError):
        c.set_bpm(0.0)
