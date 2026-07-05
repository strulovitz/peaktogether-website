"""JoystickMapper — NOT IMPLEMENTED YET. Sanctioned future work for
DeepSeek (NEW_TESTAMENT 2.5). Implementation instructions, complete:

1. Enumerate devices with pyglet.input.get_joysticks(); call
   device.open(). The Thrustmaster T16000M exposes .x, .y, .rz
   (twist), .z (throttle slider) and a .buttons list.
2. Apply the dead-zone formula to every analog axis with d = 0.15:
       v' = sign(v) * max(0, (|v| - d) / (1 - d))
3. Suggested T16000M pilot mapping: x -> CAM_YAW, y -> CAM_PITCH,
   twist rz -> TRIM_X, throttle z -> CAM_ZOOM, trigger ->
   ACTION_PRIMARY, thumb button -> ORDER_CONFIRM, hat switch ->
   TRIM_Y / TRIM_Z.
4. Implement ONLY the Mapper protocol below (attach / poll_events /
   poll_axes / poll_pointer). DO NOT touch any file outside helm/.
   DO NOT rename any action. Test with: python helm/demo.py after
   setting settings.json input.pilot_device to "joystick".
"""


class JoystickMapper:
    def __init__(self, settings):
        raise NotImplementedError(
            "JoystickMapper is not implemented yet — see this file's "
            "docstring. Helm will fall back to the keyboard."
        )
