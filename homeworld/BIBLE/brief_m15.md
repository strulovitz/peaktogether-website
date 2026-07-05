MISSION BRIEF M15 (SVD compression: "Transmit the Map Home")

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
