===========================================================
PATCH BRIEF — robots.py — expose a public bobbed position
Project: DESCENT QED engine. You are the maintainer of ONE module: robots.
===========================================================

WHO GETS THIS:
- If you ARE the chat that originally built robots.py: good — you have
  the file in context. Proceed directly.
- If you are a FRESH chat: STOP. Do NOT write or guess any code yet.
  Your FIRST action is to ask Nir:
    "Please paste the COMPLETE current contents of robots.py,
     verbatim, top to bottom, before I change anything."
  Do not reconstruct robots.py from this brief or from memory. Patch
  ONLY the real file Nir pastes. Continue only after you have it.

WHO ELSE IS INVOLVED:
DeepSeek commits your verbatim patched code to GitHub. Nir is courier/
tester (not technical, very smart). When done, write a short Completion
Report (template at end). You have no memory of other chats.

THE PRIME LAW (never violate):
The engine is MATHEMATICS-BLIND. A robot interprets no math; its only
meaning-color is its eye, taken from palette via its ledger key. This
patch changes nothing about that.

WHY THIS PATCH EXISTS (cross-module decision by the parent):
Other modules (a future game_state lock-on; the corridor demo) must be
able to read a robot's current world position WITHOUT reaching into a
private method. The existing code exposes the un-bobbed station anchor
as base_pos, but the live bobbed center is only available via a private
helper (your _world_center() or equivalent). Private coupling across
modules is forbidden, so we add a clean public accessor.

EXACTLY WHAT TO ADD (and nothing else):
A public, read-only property that returns the robot's CURRENT bobbed
world center for this frame — the SAME point your private helper
already computes. Example shape (adapt names to the real file):

  @property
  def position(self):
      # Public: the robot's bobbed world-center THIS frame.
      # Stable contract for lock-on / targeting / demos.
      return self._world_center()   # call the REAL private helper name

If your private helper has a different name in the pasted file, call
that one. If the bobbed center isn't currently factored into a single
helper, compute it in the property the same way draw() does, but do
NOT change draw()'s behavior.

KEEP base_pos exactly as-is (the un-bobbed station anchor stays public).

WHAT YOU MUST NOT DO:
- Do NOT change motion, bob, yaw, eye, hologram, explosion, or any
  visible behavior.
- Do NOT rename or remove base_pos.
- Do NOT add anything beyond the position property.
- Do NOT touch any other module's file.

TEST PLAN (how Nir verifies):
A one-line check Nir can run (or fold into robots_demo.py): after a few
update() calls, print robot.base_pos and robot.position and confirm
position oscillates around base_pos (because of bob) while base_pos
stays fixed.

WHEN DONE — COMPLETION REPORT (short):
  COMPLETION REPORT — robots patch (public position) — <date>
  FILE PATCHED: robots.py
  REAL PRIVATE HELPER USED: <name found in file>
  ADDED: robot.position (property) -> bobbed world center
  CONFIRMED: base_pos unchanged (un-bobbed station anchor); both are
     now the public contract (position = live/bobbed, base_pos = anchor).
  DEVIATIONS: none / list.
Nir carries this to the parent; DeepSeek commits the report to
/PARENT_ESTATE/reports/.
===========================================================