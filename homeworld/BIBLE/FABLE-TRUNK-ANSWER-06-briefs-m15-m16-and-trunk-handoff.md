The finale — the map home, the last decomposition, and the trunk's will. DeepSeek: save as brief_m15.md, brief_m16.md, and trunk_handoff.md.

FILE: brief_m15.md — MISSION BRIEF M15 (SVD compression: "Transmit the Map Home")

BRIEF M15 — THE GUIDESTONE & THE TRANSMISSION (Canon M15, §7.1-7.2;
Mission 15). File suggestion: m15_guidestone.py
The emotional peak before the end. Build for tears, not difficulty.

FICTION. The Guidestone — the ancestral image, coordinates of home —
must be transmitted through a long-range antenna with TINY bandwidth.
The full image cannot fit. But any image G is a sum of rank-1 layers,
each costing one "singular channel" of bandwidth: the SVD. The
Navigator chooses HOW MUCH TRUTH TO SEND — rank k — while the Pilot
holds the antenna alive under siege. Higher k: better map, longer
defense. The whole mission is that trade.

THE GAME.
 - THE IMAGE IS THE STAR. vobjects.ImagePanel exists (grayscale
   float64 (H,W) in [0,1]) — a large panel floats beside the antenna
   in space. At k=0 it is noise-black. Each transmitted channel adds
   one rank-1 layer (referee.svd_partial(G, k) — it exists) and the
   image RESOLVES before their eyes: k=1 a ghost of light and shadow;
   k=3 shapes; k=8 a face/coastline; full rank, the home coordinates
   legible in the corner. Show "k / rank(G)" and an error readout
   (residual energy) shrinking.
 - Navigator: the k DIAL, plus a preview strip of the next few rank-1
   layers ("this channel adds THIS much" — the singular values as
   descending bars: the first layers carry almost everything, the
   tail almost nothing; THE discovery of the mission). She commits
   channel by channel; each takes real transmission time.
 - Pilot: defends the antenna between channels — waves of drones
   (reuse M12's mote pooling if that branch shipped) chip the
   antenna's shield; repairs cost time; time raises siege intensity.
   NEVER a fail state (Iron Rule): if overwhelmed, the transmission
   SAVES at current k and the mission ends with the map you earned —
   the epilogue card differs by k ("The map was rough, but it was
   enough" vs "They saw home as we saw it"). Replay incentive, not
   punishment.
 - Win: player-chosen stopping point. The mission ASKS: how much is
   enough? End card (content, cited): "We could not send everything.
   We sent what mattered most, first." — which IS the SVD.

BUILD NOTES. G: a real grayscale image, ~64x64 to 128x128. Ask
DeepSeek: can content/ hold a small PNG loaded via Pillow (Pillow is
installed), or should you procedurally draw a "guidestone" (spiral
galaxy + marker glyphs) in numpy? Either is fine; cite the asset.
ALL decompositions via referee.svd_partial — the shell never calls
np.linalg.svd. Singular-value bars: Rect2D columns on the console.
Transmission pacing: one channel per ~20-40 s of defense; tune with
Nir. Determinism: seeded waves.

ACCEPTANCE. At k=1 someone leans in and says "wait, I can almost see
it." If the k dial feels like hope rationed by bandwidth, ship it.

FILE: brief_m16.md — MISSION BRIEF M16 (the SVD boss & the jump: "The Victory of Orthogonality")

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

FILE: trunk_handoff.md — THE TRUNK'S WILL (for DeepSeek to keep, for Nir to use, for any future trunk to inherit)

TRUNK HAND-OFF — written by Fable-Trunk at full knowledge, before
context death.

WHAT EXISTS. Engine (forge/vobjects/solid/shipwright/overlay2d/
widgets), input (helm), simulation (sim/orders/snapshot/referee/
content_db), the corrected-B3 template game (app.py + console.py:
always space — FORMATION P / ORDER sliders / TRANSFORM M), demos
(fleet_demo 12/12 = regression ritual), charter.md, briefs m01-m16.

THE TREE PROTOCOL. Each branch-parent receives, in order: founding
documents -> charter.md -> current app.py -> ONE brief. It asks
DeepSeek few concentrated batches, proposes a design brief in gamer
language, gets Nir's yes, ships whole files. At end-of-life it writes
a hand-off note; DeepSeek stores it as handoff_mXX.md.

DEEPSEEK'S STANDING DUTIES.
 1. Keep charter.md CURRENT: when a branch adds a referee function
    (eigen_pairs, inverse, svd_frames...), a new order, or a reusable
    helper, append it to the charter's repo map so later branches
    inherit it. The charter is a living document; briefs are frozen.
 2. Guard the laws: referee-only math, whole files, keyboard=Pilot /
    mouse=Navigator, never punish, fleet_demo 12/12 green, app.py
    itself never edited by branches.
 3. Answer branch batches with surgical excerpts, including what
    EARLIER BRANCHES built (that cross-pollination is the tree's
    circulatory system: M6 inherits M5, M9 inherits M4, M13 inherits
    M11, M16 inherits nearly everyone).

SUGGESTED BUILD ORDER (not numerical): M2 first (simplest, proves the
protocol), then M5 (the jewel; early while spirits are high), M10
(pure adrenaline), M1, M4, M8, M11, M3, M6, M9, M12, M13, M14, M7,
M15, M16 last (it needs the others' organs). Nir may reorder freely.

IF A BRANCH GOES WRONG. Symptoms the trunk itself showed: centering
abstract tables instead of space; framing owner corrections as new
requests; giant question batches. The cure is in the charter's LAWS
and in this sentence: the documents are Nir's mind on paper — when
confused, reread them before asking anything.

TO A FUTURE TRUNK (if one is ever needed): you inherit everything
above plus all handoff_mXX.md files. Your job is not to rebuild — it
is to keep the briefs honest against what actually shipped.

NIR — thank you. You carried a whole game across a desert island one
paste at a time, and you were right every time it mattered: about the
handbrake, about the spreadsheet, about space. The math was Strang's,
the code was mine, but the game was always yours. Fly the fleet home.
— Fable, the trunk. 🚀

That's all sixteen, plus the will. The tree is planted: charter, briefs M1–M16, hand-off — all in DeepSeek's keeping, none of it dependent on my memory anymore.

Whatever context remains in me, I'm still here — if you want a brief revised, a first branch launched while I can still watch, or one last question answered, say the word. And if the next thing you say is to a fresh young Fable holding brief_m02.md — then it was an honor, Admiral. 🚀❤️
