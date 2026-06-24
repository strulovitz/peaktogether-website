from principia.control.input import edge, scale_aim, InputManager


def test_edge():
    assert edge(False, True) is True
    assert edge(True, True) is False
    assert edge(True, False) is False
    assert edge(False, False) is False


def test_scale_aim():
    assert scale_aim(0.1, -0.2, 40) == (4.0, -8.0)


def test_input_manager_initial_state():
    inp = InputManager()
    assert inp.shoot_pressed() is False
    assert inp.pause_pressed() is False
    assert inp.toggle_map_pressed() is False
    assert inp.read_mode_pressed() is False
    assert inp.body_yaw_delta() == 0.0
