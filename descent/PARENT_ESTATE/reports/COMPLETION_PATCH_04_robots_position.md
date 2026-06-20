COMPLETION REPORT — robots patch (public position) — 2026-06-13
FILE PATCHED: robots.py
REAL PRIVATE HELPER USED: _world_center()
ADDED: robot.position (property) -> bobbed world center (delegates to
   _world_center(); no recomputation)
CONFIRMED: base_pos unchanged (un-bobbed station anchor); both are now
   the public contract (position = live/bobbed, base_pos = anchor).
   No change to motion/bob/yaw/eye/hologram/explosion or draw()/update().
   robots_demo.py NOT modified (out of scope for this patch; its
   internal _world_center() use is same-authorship and still valid).
DEVIATIONS: none.

Thank you, Nir — carry this to the parent, and DeepSeek can commit the verbatim property plus this report. 🙂