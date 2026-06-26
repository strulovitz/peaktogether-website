"""Pure unit tests for input_actions. No GPU/window context required.

Tests import directly from the module under test (not via contracts).
"""

import math

import pytest

from input_actions import EdgeTracker, RawSample, build_actions, _clamp, Actions


def _sample(
    *,
    mover_axis_x=0.0,
    mover_axis_y=0.0,
    mover_yaw_rate=0.0,
    mover_pitch_rate=0.0,
    shooter_aim_x=0.0,
    shooter_aim_y=0.0,
    shooter_fire_down=False,
    read_down=False,
    interact_down=False,
    pause_down=False,
) -> RawSample:
    return RawSample(
        mover_axis_x=mover_axis_x,
        mover_axis_y=mover_axis_y,
        mover_yaw_rate=mover_yaw_rate,
        mover_pitch_rate=mover_pitch_rate,
        shooter_aim_x=shooter_aim_x,
        shooter_aim_y=shooter_aim_y,
        shooter_fire_down=shooter_fire_down,
        read_down=read_down,
        interact_down=interact_down,
        pause_down=pause_down,
    )


def test_edge_fire_once():
    # fire_down goes F, T, T, F, T
    tracker = EdgeTracker()
    sequence = [False, True, True, False, True]
    expected_edges = [False, True, False, False, True]

    for down, exp_edge in zip(sequence, expected_edges):
        a = build_actions(
            _sample(shooter_fire_down=down),
            tracker,
            dt=0.016,
            cfg_yaw_sens=2.2,
            cfg_pitch_sens=1.8,
        )
        assert a.fire is exp_edge
        # fire_held mirrors the raw down-state.
        assert a.fire_held is down


def test_edges_independent():
    tracker = EdgeTracker()

    # Frame 1: press read only.
    a1 = build_actions(
        _sample(read_down=True),
        tracker, 0.016, 2.2, 1.8,
    )
    assert a1.read_toggle is True
    assert a1.interact is False
    assert a1.pause is False

    # Frame 2: read still held (no edge), press interact.
    a2 = build_actions(
        _sample(read_down=True, interact_down=True),
        tracker, 0.016, 2.2, 1.8,
    )
    assert a2.read_toggle is False        # held, no new edge
    assert a2.interact is True
    assert a2.pause is False

    # Frame 3: release everything, press pause.
    a3 = build_actions(
        _sample(pause_down=True),
        tracker, 0.016, 2.2, 1.8,
    )
    assert a3.read_toggle is False
    assert a3.interact is False
    assert a3.pause is True

    # Frame 4: pause held, re-press read.
    a4 = build_actions(
        _sample(pause_down=True, read_down=True),
        tracker, 0.016, 2.2, 1.8,
    )
    assert a4.pause is False              # held, no new edge
    assert a4.read_toggle is True
    assert a4.interact is False


def test_mover_owns_rotation():
    tracker = EdgeTracker()
    # Shooter aim cranked, mover look rates zero → rotation must stay 0.
    a = build_actions(
        _sample(
            shooter_aim_x=5.0,
            shooter_aim_y=5.0,
            mover_yaw_rate=0.0,
            mover_pitch_rate=0.0,
        ),
        tracker, 0.016, 2.2, 1.8,
    )
    assert a.heading_delta == 0.0
    assert a.pitch_delta == 0.0


def test_aim_clamped():
    tracker = EdgeTracker()
    a = build_actions(
        _sample(shooter_aim_x=5.0),
        tracker, 0.016, 2.2, 1.8,
    )
    assert a.aim_x == 1.0
    # also exercise the pure helper.
    assert _clamp(5.0, -1.0, 1.0) == 1.0
    assert _clamp(-5.0, -1.0, 1.0) == -1.0
    assert _clamp(0.25, -1.0, 1.0) == 0.25


def test_scaling():
    tracker = EdgeTracker()
    yaw_rate = 0.5
    pitch_rate = -0.3
    sens_yaw = 2.2
    sens_pitch = 1.8
    dt = 0.02

    a = build_actions(
        _sample(mover_yaw_rate=yaw_rate, mover_pitch_rate=pitch_rate),
        tracker, dt, sens_yaw, sens_pitch,
    )
    assert a.heading_delta == yaw_rate * sens_yaw * dt
    assert a.pitch_delta == pitch_rate * sens_pitch * dt


def test_actions_frozen():
    tracker = EdgeTracker()
    a = build_actions(_sample(), tracker, 0.016, 2.2, 1.8)
    # frozen pydantic model: assignment must raise.
    with pytest.raises(Exception):
        a.move_x = 0.9
