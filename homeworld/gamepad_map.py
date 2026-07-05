"""GamepadMapper — NOT IMPLEMENTED YET. Sanctioned future work for
DeepSeek (NEW_TESTAMENT 2.5). Implementation instructions, complete:

1. Enumerate with pyglet.input.get_controllers(); Xbox controllers
   expose named attributes (leftx, lefty, rightx, righty,
   lefttrigger, righttrigger, buttons a/b/x/y, bumpers, dpad, start).
2. Apply the dead-zone formula with d = 0.15 to every stick axis:
       v' = sign(v) * max(0, (|v| - d) / (1 - d))
3. Suggested Xbox PILOT mapping: leftx/lefty -> CAM_YAW/CAM_PITCH,
   rightx/righty -> TRIM_X/TRIM_Z, triggers -> CAM_ZOOM (RT - LT),
   A -> ORDER_CONFIRM, B -> ORDER_CANCEL, X -> ACTION_PRIMARY,
   Y -> FLIGHT_MODE_TOGGLE, bumpers -> SELECT_PREV/SELECT_NEXT,
   start -> PAUSE.
4. Xbox as NAVIGATOR device: left stick moves a virtual pointer
   (x += stick_x * speed * dt; synthesize PointerState), A = primary
   click, B = secondary, right stick vertical = wheel.
5. Implement ONLY the Mapper protocol (attach / poll_events /
   poll_axes / poll_pointer). DO NOT touch any file outside helm/.
   DO NOT rename any action. Test with: python helm/demo.py.
"""


class GamepadMapper:
    def __init__(self, settings):
        raise NotImplementedError(
            "GamepadMapper is not implemented yet — see this file's "
            "docstring. Helm will fall back to keyboard/mouse."
        )
