# Claude Fable — Page 11 Response (2026-06-11)

## VERBATIM RESPONSE FROM CLAUDE FABLE

Nir, deal — we ditch the GIF and build it better. :-) And thank you for the detective work: 31 bars, a red pivot that changes each round, thin red curved arrows above the bars — combined with the official caption you pasted ("pivots (red items and blue lines) chosen as the last item in each subproblem", "recursive subproblems indicated by shaded arrows"), I now have everything I need. Also: good to know the big blue arrow was an OpenRouter upload artifact — mystery closed, it will NOT appear anywhere. 😄

One quick math note before the code: the Wikipedia formula uses \tfrac — forbidden (Bug #1!), so I converted it to \frac. And the sum has a lovely closed form I use for the live readout:

sum_{i=1}^{n-1} 2 H_i = 2n(H_n - 1) ≈ 187.7 for n=31

(a) Engine patches

None needed! 🎉 This page uses only existing idioms: paper trick, draw_box, draw_latex_3d, line strips. Zero new engine concepts. (random and math are already imported — the coupon collector uses them.)

(b) The complete page class

Paste location: in math_flyer.py, immediately after the end of class CouponCollectorPage (and before the App section). Same spot in BOTH the Bible and the working copy.

```python
# ============================================================================
# PAGE 11 — QUICKSORT (Applications: Analyzing algorithms)
# Wikipedia: Harmonic series -> Applications -> Analyzing algorithms.
# Reproduces the spirit of the Wikipedia animation: 31 grey bars (values
# 1..31 shuffled), pivot = LAST item of each subproblem (red item + blue
# line, per the caption), shaded band = current recursive subproblem,
# thin red curved arrow = the swap performed at the current step.
# The GIF's autoplay is replaced by Player 1's "Progress" slider: SHE is
# the animation. Expected comparisons: sum 2*H_i = 2n(H_n - 1).
# ============================================================================
@register_page
class QuicksortPage(Page):
    TITLE = "Quicksort: the harmonic price of sorting"

    N       = 31          # number of bars, faithful to the Wikipedia figure
    BAR_W   = 0.86        # bar width (bars sit on unit spacing)
    H_SCALE = 0.34        # world units of height per unit of value
    CAP_H   = 0.42        # the little black square cap on each bar
    DEPTH   = 0.60        # bar depth in z

    PAPER = (0.96, 0.95, 0.90)
    BAR_G = (0.76, 0.76, 0.78)
    INK   = (0.10, 0.10, 0.10)
    RED   = (0.78, 0.06, 0.16)
    BLUE  = (0.15, 0.25, 0.85)
    SHADE = (0.84, 0.84, 0.81)

    def __init__(self):
        self.sliders = [
            Slider("Progress %", 0.0, 100.0, 0.0, step=0.25),
            Slider("Shuffle (seed)", 1, 12, 1, step=1),
        ]
        self._trace_seed = None
        self._trace = []

    # ---- precompute the full quicksort trace for one shuffle ---------------
    def _build_trace(self, seed):
        rng = random.Random(1000 + seed)
        arr = list(range(1, self.N + 1))
        rng.shuffle(arr)
        steps, comps, swaps = [], [0], [0]

        def record(lo, hi, piv, swap):
            steps.append({"arr": tuple(arr), "lo": lo, "hi": hi, "piv": piv,
                          "swap": swap, "comps": comps[0], "swaps": swaps[0]})

        record(None, None, None, None)                 # frame 0: shuffled deal

        def qsort(lo, hi):
            if lo >= hi:
                return
            pval = arr[hi]                             # pivot = LAST item (caption)
            record(lo, hi, hi, None)                   # pivot chosen
            i = lo
            for j in range(lo, hi):                    # Lomuto partition
                comps[0] += 1
                if arr[j] < pval:
                    if i != j:
                        arr[i], arr[j] = arr[j], arr[i]
                        swaps[0] += 1
                        record(lo, hi, hi, (i, j))
                    i += 1
            if i != hi:
                arr[i], arr[hi] = arr[hi], arr[i]
                swaps[0] += 1
                record(lo, hi, i, (i, hi))             # pivot flies home
            else:
                record(lo, hi, i, None)
            qsort(lo, i - 1)
            qsort(i + 1, hi)

        qsort(0, self.N - 1)
        record(None, None, None, None)                 # final frame: sorted!
        return steps

    def _current_step(self):
        frac = self.sliders[0].value / 100.0
        idx = int(round(frac * (len(self._trace) - 1)))
        return idx, self._trace[idx]

    # ---- world ---------------------------------------------------------------
    def draw_world(self):
        seed = int(round(self.sliders[1].value))
        if seed != self._trace_seed:
            self._trace_seed = seed
            self._trace = self._build_trace(seed)

        idx, st = self._current_step()
        arr = st["arr"]
        top = self.N * self.H_SCALE + self.CAP_H

        # --- paper (ink-on-white trick, Page 3 style) ---
        glDisable(GL_LIGHTING)
        glColor3f(*self.PAPER)
        glBegin(GL_QUADS)
        glVertex3f(-1.5, -0.8, -0.32); glVertex3f(self.N + 1.5, -0.8, -0.32)
        glVertex3f(self.N + 1.5, top + 3.2, -0.32); glVertex3f(-1.5, top + 3.2, -0.32)
        glEnd()

        # --- shaded band: the active recursive subproblem ---
        if st["lo"] is not None:
            glColor3f(*self.SHADE)
            x0, x1 = float(st["lo"]), st["hi"] + 1.0
            glBegin(GL_QUADS)
            glVertex3f(x0, -0.5, -0.30); glVertex3f(x1, -0.5, -0.30)
            glVertex3f(x1, top + 0.6, -0.30); glVertex3f(x0, top + 0.6, -0.30)
            glEnd()
        glEnable(GL_LIGHTING)

        # --- grey bars with black caps; the pivot item is red ---
        pad = (1.0 - self.BAR_W) * 0.5
        for i, v in enumerate(arr):
            h = v * self.H_SCALE
            is_piv = (st["piv"] is not None and i == st["piv"])
            glColor3f(*(self.RED if is_piv else self.BAR_G))
            draw_box(i + pad, 0.0, 0.0, i + 1.0 - pad, h, self.DEPTH)
            glColor3f(*((0.92, 0.10, 0.16) if is_piv else self.INK))
            draw_box(i + pad, h, -0.02,
                     i + 1.0 - pad, h + self.CAP_H, self.DEPTH + 0.02)

        glDisable(GL_LIGHTING)

        # --- blue line at pivot height across the active range (caption) ---
        if st["piv"] is not None and st["lo"] is not None:
            pv = arr[st["piv"]] * self.H_SCALE
            glColor3f(*self.BLUE)
            glLineWidth(2.0)
            glBegin(GL_LINES)
            glVertex3f(float(st["lo"]), pv, self.DEPTH + 0.05)
            glVertex3f(st["hi"] + 1.0, pv, self.DEPTH + 0.05)
            glEnd()

        # --- thin red curved arrow above the bars: the swap of this step ---
        if st["swap"] is not None:
            a, b = st["swap"]
            xa, xb = a + 0.5, b + 0.5
            ya = arr[a] * self.H_SCALE + self.CAP_H + 0.25
            yb = arr[b] * self.H_SCALE + self.CAP_H + 0.25
            arc = 1.2 + 0.16 * abs(xb - xa)
            glColor3f(*self.RED)
            glLineWidth(2.0)
            glBegin(GL_LINE_STRIP)
            SEG = 28
            for s in range(SEG + 1):
                u = s / float(SEG)
                x = xa + (xb - xa) * u
                y = (1 - u) * ya + u * yb + arc * math.sin(math.pi * u)
                glVertex3f(x, y, self.DEPTH + 0.06)
            glEnd()
            for (xe, ye, sgn) in ((xa, ya, 1.0), (xb, yb, -1.0)):
                glBegin(GL_LINES)
                glVertex3f(xe, ye, self.DEPTH + 0.06)
                glVertex3f(xe + 0.28 * sgn, ye + 0.34, self.DEPTH + 0.06)
                glVertex3f(xe, ye, self.DEPTH + 0.06)
                glVertex3f(xe - 0.10 * sgn, ye + 0.38, self.DEPTH + 0.06)
                glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

        # --- in-world 'pivot' label (NOT in a display list -> safe) ---
        if st["piv"] is not None:
            lab = self.tex.latex(r"$\mathrm{pivot}$", fontsize=14, color="#B5093D")
            draw_latex_3d(lab, st["piv"] + 0.5,
                          arr[st["piv"]] * self.H_SCALE + self.CAP_H + 1.7,
                          self.DEPTH + 0.06, 0.7)

    # ---- overlays --------------------------------------------------------------
    def overlay_latex(self):
        n = self.N
        Hn = sum(1.0 / k for k in range(1, n + 1))
        expected = 2.0 * n * (Hn - 1.0)
        return [
            (r"$\sum_{i=2}^{n}\sum_{k=0}^{i-2}\frac{2}{k+2}"
             r"\;=\;\sum_{i=1}^{n-1}2H_i\;=\;O(n\log n)$", 16),
            (r"$\mathrm{separation}\;k\;\Rightarrow\;"
             r"\mathrm{Pr}\left(\mathrm{compared}\right)=\frac{2}{k+2}$", 14),
            (r"$n=31:\;\sum_{i=1}^{30}2H_i\;=\;2\cdot 31\;(H_{31}-1)"
             r"\;\approx\;%.1f$" % expected, 14),
        ]

    def overlay_info(self):
        if not self._trace:
            return []
        idx, st = self._current_step()
        n = self.N
        Hn = sum(1.0 / k for k in range(1, n + 1))
        return [
            'Wikipedia: "Animation of the average-case version of quicksort,',
            'with recursive subproblems indicated by shaded arrows and with',
            'pivots (red items and blue lines) chosen as the last item in',
            'each subproblem."',
            "",
            "Step %d / %d   |   comparisons so far: %d   |   swaps so far: %d"
            % (idx, len(self._trace) - 1, st["comps"], st["swaps"]),
            "Expected comparisons (random shuffle): 2n(Hn - 1) = %.1f"
            % (2.0 * n * (Hn - 1.0)),
            "",
            "P1: drag 'Progress %' to run quicksort by hand; 'Shuffle' re-deals.",
            "P2: fly along the wall and watch the staircase assemble itself.",
        ]
```

(c) Lesson moment — for the couple 💑

She drags Progress slowly from 0. A red bar lights up — the pivot, always the last bar of the shaded zone — and a blue line marks its height: every bar in the zone gets measured against that line. Red arcs flash as bars leap past each other. He flies low along the wall and watches the shaded zone split, split, split again — until, at 100%, a perfect staircase stands from 1 to 31.

Now the punchline: look at the counter. About 188 comparisons were expected — and why? Two bars that end up neighbors (k=0) are compared almost surely: probability 2/(0+2) = 1. Two bars destined to be far apart almost never meet: 2/(k+2) shrinks like a harmonic term. Sum all those harmonic crumbs over every pair, and out comes sum 2 H_i = O(n log n). The same series that built our towers and crossed our desert now sets the speed limit of sorting: because H_n diverges, no comparison sort can ever run in linear time.

(d) Honest deviations from the Wikipedia animation

Autoplay → scrub slider: the GIF plays itself; ours is driven by Player 1's Progress % slider. Deliberate — it's our whole philosophy.
"Shaded arrows" → shaded band: the original marks recursive subproblems with shaded arrow shapes; I use a shaded rectangle over the active range. Arrow silhouettes would be unreadable as 3D geometry; the band conveys the same information.
One arrow at a time: the GIF shows transient swap arrows; we show exactly the arc of the current step.
2D → 3D: flat lines with square dots become 3D grey boxes with black cap cubes (consistent with our house style; pivot bar + cap turn red, faithful to "red items").
Pivot rule is faithful: last item of each subproblem, exactly per the caption; blue line at pivot height, drawn across the active range.
\tfrac → \frac in the formula (mathtext, Rule #1). Bar count 31, per Nir's count.

What to tell DeepSeek

"New page from Fable: QuicksortPage, paste the whole block immediately after class CouponCollectorPage in the working copy. No engine patches. Verify random and math are imported at the top (they are). Run, Tab to page 11, scrub Progress % 0→100, flip Shuffle (seed), confirm: red pivot + blue line, shaded band shrinking with recursion, red arcs on swaps, sorted staircase at 100%. Report any bugs as usual."

One last thing, Nir: this is page 11 of 11 — the roadmap is complete! 🎉 Once DeepSeek confirms a clean build, the file is probably well past the ~2000-line mark (Rule 8), so our victory-lap session can be the folder+zip restructure proposal — or we just declare it done and let the couple fly. Your call, captain. :-)
