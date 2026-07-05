MISSION BRIEF M11 (eigenvectors: "The Calm Axis")

BRIEF M11 — EIGENVECTOR DOCKING (Canon M11, §6.1; the Act IV relic).
File suggestion: m11_relic.py

FICTION. An ancient relic tumbles under a fixed transformation T:
every pulse, the space AROUND it is stirred by T. Approach from any
direction and your approach vector is swung off course and you're
flung away — except along an eigenvector, where T x = lambda x keeps
your DIRECTION unchanged. Docking = finding the calm axis of a
spinning thing.

THE GAME.
 - The stirring is VISIBLE: a shell of ghost test-arrows around the
   relic redraws each pulse as T bends them (each arrow drawn from
   x toward T x, normalized) — a whirlpool of directions... except
   along one axis, where arrows lie still. The calm axis is
   findable BY EYE if you stare — that's intended.
 - Navigator's console: a PROBE widget — she aims a trial direction
   x (two angle sliders), and the console draws x and T x side by
   side with the angle between them; misaligned probes visibly
   scissor apart, and on the eigenvector they fuse into one line
   with a pure stretch readout (the lambda! shown as "x 1.7" —
   scale, not turn). A FIND button may exist but costs the mission's
   only scan charge (referee.real_eigen_axis) — probing by hand is
   cheaper and more fun.
 - Pilot: flies the docking ship onto the axis line (drawn once the
   Navigator locks a probe within tolerance), then approaches WITH
   THE AXIS. Drift off-axis and the relic's stir pushes the ship
   sideways (gentle spring, telegraphed — never a slam); on-axis,
   approach is glass-smooth. Contact: dock, relic powers up, the Key
   turns (content-cited end card: "Every spinning thing has an axis
   it cannot move. Find it, and it will hold you steady.").
 - Optional second relic (harder): negative lambda — the calm axis
   holds your LINE but reverses you each pulse; docking requires
   half-speed. Let them discover why.

BUILD NOTES. T: pick a rotation-plus-stretch with ONE real eigen-
direction dominant, integer-friendly; VERIFY with referee.
real_eigen_axis before hardcoding. The stir on the ship = shell-side
rule (per-pulse nudge proportional to how far the ship's relative
position direction is from the axis); the AXIS and all eigen verdicts
come from referee only. The test-arrow shell: ~60 pooled Arrow/Line
vobjects on a sphere, recomputed per pulse, interpolated per frame.
Ask DeepSeek: current Arrow pooling patterns from earlier branches
(M5's corridor, M9's residuals) to reuse.

ACCEPTANCE. A tester finds the axis BY EYE from the whirlpool before
touching the probe — and the probe then CONFIRMS what they saw.
Eigenvector = the direction the storm cannot turn.
