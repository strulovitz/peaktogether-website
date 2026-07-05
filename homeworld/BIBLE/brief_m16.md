MISSION BRIEF M16 (the SVD boss & the jump: "The Victory of Orthogonality")

BRIEF M16 — THE FINALE (Canon M16, Ch. 7; Mission 16, Hiigara).
File suggestion: m16_hiigara.py
Read briefs M8, M11, M13 — this is their reunion. Every skill the
campaign taught gets one final call.

FICTION. The Emperor's flagship hides inside a warp-shear field: a
transformation A that mangles all approach vectors. But every matrix
— EVERY one — factors as A = U Sigma V^T: a rotation, a pure stretch,
another rotation. Nothing the enemy does is anything but these three.
Decompose him, and he is ordinary. Meanwhile the fleet's own jump
home is THE SAME THREE MOVES performed willingly: the hyperspace
ritual is the SVD acting on space itself.

THE GAME — three phases, one truth:
 PHASE V^T (ALIGN): the shear field visibly swirls approach lanes
   (M11's test-arrow shell, at scale). The Navigator sounds the field
   (M13's ping skill) to find the input principal axes — the right
   singular vectors; locking them draws an orthogonal TRIAD in space.
   The Pilot rotates the fleet formation onto the triad (template's
   TRANSFORM zone with a rotation — his M8/M14 skill). Aligned: the
   swirl stops swirling; the field now only STRETCHES. Phase down.
 PHASE Sigma (COUNTER-STRETCH): along each locked axis the field
   scales by sigma_i (drawn as the field-ellipsoid, M13's shape).
   The Navigator dials three counter-scales 1/sigma_i on a diagonal-
   only TRANSFORM (the console locks off-diagonals — diagonal
   matrices as the tamest of all); mismatched dials wobble the fleet,
   matched dials flatten the field's ellipsoid into a perfect SPHERE
   — distortion neutralized. The biggest sigma is the boss's main
   gun: counter it first (singular values in descending order, felt).
 PHASE U (THE LAST TURN): one final rotation stands between the
   fleet and the flagship's core. Navigator reads it, Pilot fires
   the counter-rotation, the field dies: A undone as
   V Sigma^{-1} U^T, in playable pieces. The core is bare. One
   volley (M4's recipe, one last time). Done.
 THE JUMP. No new mechanic — the reward: the ritual animation.
   Space itself performs the three moves on the star field: rotate
   (V^T), stretch (Sigma), rotate (U) — the same triad glyphs the
   players just mastered, now cosmic and gentle, music swelling
   (if audio is out of scope, the visuals must carry it alone —
   slow, 20+ seconds, let it breathe). Hiigara resolves from the
   M15 Guidestone image into a rendered planet-disc. Final card
   (content, cited): "Every hard thing between us and home was only
   ever three simple things in disguise. Rotate. Stretch. Rotate.
   — The fleet, at last, in a good basis."

BUILD NOTES. All SVD math: referee.svd_partial + a small spec'd
addition if you need full U, Sigma, V^T triples (svd_frames(A) ->
(U, S, Vt), tolerance doctrine). Choose A = U Sigma V^T by
CONSTRUCTING it from chosen rotations and Sigma = diag(3, 1.5, 0.6)
— then the phase answers are known-good by construction; verify with
referee round-trip. Field visuals: reuse M11's arrow shell and M13's
ellipsoid (ask DeepSeek what those branches named their helpers).
Boss pressure: telegraphed, gentle, pausable — this mission's
difficulty is comprehension, not dodging. The finale is allowed to
be EASY. It is a graduation, not an exam.

ACCEPTANCE. A couple that finishes says two things: "that was the
whole game in one fight" and "so THAT's what a jump was, all along."
Then they sit through the credits quietly. That silence is the win.
