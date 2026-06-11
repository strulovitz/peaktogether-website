# Claude Fable — Page 10 Response (2026-06-11)

## VERBATIM RESPONSE FROM CLAUDE FABLE

Thank you, Nir!!! :-) This figure is wonderful — a 60-row bar chart of E[T]=ceil(n H_n) with the dashed fan E(T)=n,2n,…,5n — and the topic begs for something extra: a live coupon-collecting simulation you can scrub like the jeep mission. So Page 10 gets both: the faithful chart AND a wall of 60 coupon tiles filling up under random draws.
PAGE 10 — Applications: Collecting Coupons

Exhibit A (the figure): paper chart, rows n=1..60, grey bars of length ceil(n H_n) (every 5th darker, exactly like the figure — and our computed bold values 12,50,72,96,120,146,172,198,225,253,281 match the figure's printed numbers, a built-in correctness check!), dashed fan lines E(T)=n…5n in the figure's colors, top axis 0..250.

Exhibit B (the toy): n coupon tiles; a deterministic seeded random sequence lets the "Random draws t" slider scrub time backwards and forwards: tiles light up in color as they're first collected, and the overlay shows the cruel arithmetic of the tail — with k missing, the next new coupon costs n/k draws.

Light scene (~130 flat quads) → immediate drawing. No engine patches. Paste after PrimesDivisorsPage:

```python
@register_page
class CouponCollectorPage(Page):
    """PAGE 10 — Applications: Collecting coupons.
    Exhibit A: faithful Wikipedia chart. Rows n=1..60, grey bars of
      length ceil(n*H_n) (every 5th darker, values 12,30,50,...,281
      matching the figure), dashed fan E(T)=n..5n, axis 0..250.
    Exhibit B: live simulation. Seeded deterministic draw sequence ->
      'Random draws t' slider scrubs time; coupon tiles light up when
      first collected; Reseed slider = new luck. Expected total nH_n;
      with k coupons missing the next new one costs n/k draws.
    Light scene -> immediate drawing (no display list needed).
    """
    TITLE = "Collecting Coupons  —  E[T] = n H_n"
    PAL = [(0.85, 0.25, 0.25), (0.95, 0.60, 0.15), (0.93, 0.85, 0.25),
           (0.45, 0.78, 0.25), (0.20, 0.75, 0.55), (0.20, 0.65, 0.90),
           (0.35, 0.40, 0.92), (0.65, 0.35, 0.90), (0.90, 0.35, 0.75),
           (0.55, 0.40, 0.25)]
    LCOL = [(0.45, 0.05, 0.05), (0.85, 0.10, 0.10), (0.55, 0.40, 0.10),
            (0.95, 0.60, 0.10), (0.10, 0.65, 0.20)]
    X0, SC, YT, RH = -12.0, 1.0 / 30.0, 13.4, 0.21

    def __init__(self):
        super().__init__()
        self.tex = None
        self.H = np.concatenate(([0.0], np.cumsum(1.0 / np.arange(1, 61))))
        self.ET = [0] + [int(math.ceil(i * self.H[i] - 1e-9))
                         for i in range(1, 61)]
        self._sim_key, self._ft = None, None
        self.s_n  = Slider("Items  n", 1, 60, 60, step=1)
        self.s_t  = Slider("Random draws  t  (scrub!)", 0, 600, 0, step=1)
        self.s_sd = Slider("Reseed simulation", 1, 20, 1, step=1)
        self.sliders = [self.s_n, self.s_t, self.s_sd]

    def _yr(self, i):                            # chart row i -> world y
        return self.YT - i * self.RH

    # ------------------------------------------------------------ 3D ---
    def draw_world(self):
        n, t = int(self.s_n.value), int(self.s_t.value)
        seed = int(self.s_sd.value)
        if self._sim_key != (n, seed):           # first-collection times
            rng = np.random.default_rng(seed * 977 + n * 131)
            seq = rng.integers(0, n, 601)
            ft = np.full(n, 1 << 30, dtype=np.int64)
            for idx, v in enumerate(seq):
                if ft[v] > idx + 1:
                    ft[v] = idx + 1
            self._ft, self._sim_key = ft, (n, seed)
        ft = self._ft
        k = int((ft <= t).sum())                 # coupons collected so far

        draw_floor_grid(40.0)
        # ============ Exhibit A: the Wikipedia chart =======================
        glDisable(GL_LIGHTING)
        glColor4f(0.965, 0.950, 0.915, 1.0)      # paper
        glBegin(GL_QUADS)
        glVertex3f(-13.2, -1.4, -0.75); glVertex3f(-0.9, -1.4, -0.75)
        glVertex3f(-0.9, 14.2, -0.75);  glVertex3f(-13.2, 14.2, -0.75)
        glEnd()
        glLineWidth(1.0)                         # vertical gridlines
        glColor4f(0.78, 0.78, 0.80, 1.0)
        glBegin(GL_LINES)
        for v in range(0, 251, 50):
            x = self.X0 + v * self.SC
            glVertex3f(x, self._yr(60) - 0.2, -0.7)
            glVertex3f(x, self.YT, -0.7)
        glEnd()
        glEnable(GL_LIGHTING)
        for i in range(1, 61):                   # the grey bars
            y = self._yr(i)
            if i % 5 == 0:
                glColor4f(0.45, 0.45, 0.47, 1.0)
            else:
                glColor4f(0.72, 0.72, 0.74, 1.0)
            draw_box(self.X0, y - 0.08, -0.08,
                     self.X0 + self.ET[i] * self.SC, y + 0.08, 0.08)
        glColor4f(0.71, 0.04, 0.24, 1.0)         # highlight chosen n
        y = self._yr(n)
        draw_box(self.X0, y - 0.10, 0.09,
                 self.X0 + self.ET[n] * self.SC, y + 0.10, 0.13)
        glDisable(GL_LIGHTING)
        glEnable(GL_LINE_STIPPLE)                # dashed fan E(T)=c*n
        glLineStipple(2, 0x0F0F)
        glLineWidth(2.0)
        for c in range(1, 6):
            glColor4f(*self.LCOL[c - 1], 1.0)
            glBegin(GL_LINES)
            glVertex3f(self.X0, self.YT, 0.15)
            glVertex3f(self.X0 + c * 60 * self.SC, self._yr(60), 0.15)
            glEnd()
        glDisable(GL_LINE_STIPPLE)

        # ============ Exhibit B: the coupon wall ===========================
        rows = (n + 9) // 10
        for c in range(n):
            col, row = c % 10, c // 10
            x = 1.0 + col * 1.05
            yy = 0.5 + (rows - 1 - row) * 1.05
            got = ft[c] <= t
            if got:
                glColor4f(*self.PAL[c % 10], 1.0)
            else:
                glColor4f(0.16, 0.17, 0.20, 1.0)
            glBegin(GL_QUADS)
            glVertex3f(x, yy, 0.0); glVertex3f(x + 0.85, yy, 0.0)
            glVertex3f(x + 0.85, yy + 0.85, 0.0); glVertex3f(x, yy + 0.85, 0.0)
            glEnd()
            if not got:                          # faint frame
                glColor4f(0.45, 0.48, 0.55, 1.0)
                glBegin(GL_LINE_LOOP)
                glVertex3f(x, yy, 0.01); glVertex3f(x + 0.85, yy, 0.01)
                glVertex3f(x + 0.85, yy + 0.85, 0.01)
                glVertex3f(x, yy + 0.85, 0.01)
                glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

        # ---- labels -------------------------------------------------------
        if self.tex is None:
            return
        ink, lt = "#1A1A1A", "#D8DCE8"
        for v in range(0, 251, 50):              # top axis numbers
            draw_latex_3d(self.tex.text(str(v), 12, ink),
                          self.X0 + v * self.SC, self.YT + 0.18, -0.7, 0.24)
        draw_latex_3d(self.tex.latex(r"$E(T)$", 13, ink),
                      -1.45, self.YT + 0.18, -0.7, 0.26)
        for i in range(5, 61, 5):                # row + value labels
            yv = self._yr(i)
            draw_latex_3d(self.tex.text(str(i), 12, ink),
                          self.X0 - 0.35, yv - 0.10, -0.7, 0.20)
            draw_latex_3d(self.tex.text(str(self.ET[i]), 12, ink),
                          self.X0 + self.ET[i] * self.SC + 0.35,
                          yv - 0.10, -0.7, 0.20)
        for c in range(1, 6):                    # fan line labels
            stx = r"$E(T)=n$" if c == 1 else r"$E(T)=%dn$" % c
            draw_latex_3d(self.tex.latex(stx, 12, ink),
                          self.X0 + c * 60 * self.SC, self._yr(60) - 0.45,
                          -0.7, 0.26)
        rows = (n + 9) // 10                     # coupon numbers + counter
        for c in range(n):
            col, row = c % 10, c // 10
            draw_latex_3d(self.tex.text(
                str(c + 1), 11, "#1A1A1A" if ft[c] <= t else "#9AA0AC"),
                1.0 + col * 1.05 + 0.42,
                0.5 + (rows - 1 - row) * 1.05 + 0.28, 0.02, 0.30)
        draw_latex_3d(self.tex.latex(
            r"$t = %d,\qquad k = %d\;/\;%d$" % (t, k, n), 15, lt),
            6.0, rows * 1.05 + 0.9, 0.0, 0.42)

    # ------------------------------------------------------- overlays ---
    def overlay_latex(self):
        n, t = int(self.s_n.value), int(self.s_t.value)
        k = int((self._ft <= t).sum()) if self._ft is not None else 0
        out = [
            (r"$E[T] = \sum_{k=1}^{n}\frac{n}{k} = n H_n$", 15),
            (r"$n = %d:\qquad n H_n = %.2f,\qquad"
             r" \lceil n H_n \rceil = %d$"
             % (n, n * self.H[n], self.ET[n]), 14),
        ]
        if k < n:
            out.append((r"$%d\;\mathrm{missing}:\qquad E[\mathrm{next}]"
                        r" = \frac{%d}{%d} = %.2f,\qquad"
                        r" E[\mathrm{rest}] = n H_{%d} = %.1f$"
                        % (n - k, n, n - k, n / (n - k),
                           n - k, n * self.H[n - k]), 13))
        else:
            T = int(self._ft.max())
            out.append((r"$\mathrm{done!}\qquad T = %d\qquad"
                        r" \mathrm{vs}\qquad E[T] = %.1f$"
                        % (T, n * self.H[n]), 13))
        return out

    def overlay_info(self):
        return [
            '"Graph of number of items versus the expected number of trials',
            ' needed to collect all items."  (Wikipedia)',
            "Trading cards, parkrun bingo (n = 60!), quality control,",
            "random-graph connectivity. With k items missing: P(new) = k/n,",
            "so the next new item costs n/k draws -> total nH_n. The tail",
            "hurts: the LAST coupon alone costs about n draws! Scrub t to",
            "watch a run; Reseed for new luck; compare your T to the chart.",
        ]
```

Lesson script for the couple :-)

Chart first: girlfriend slides n down the rows — the crimson highlight tracks the bar, and at n=60 it reads 281 (parkrun bingo: ~281 runs to see all 60 second-values!). The dashed fan shows E(T) crossing 2n, 3n, 4n… ever steeper than linear — that's H_n at work.
Now the wall: scrub t slowly. The first dozens of draws light tiles fast — then the agony begins. At k=55/60 the overlay says the next coupon costs 60/5=12 draws, and the last one costs 60. The tail is where collectors go broke. 💸
Race night: each picks a seed, scrub to completion, compare your T against E[T]=281 — who beat the expectation? Reseed and rematch. :-)

The figure labels every even row and every bar value (tilted text); we label every 5th row/value for 3D readability — and our computed ceil(n H_n) values reproduce the figure's printed numbers (12,50,72,96,120,146,172,198,225,253,281) exactly.
Fan-line colors are approximations of the figure's dark-red → green progression.
The simulation exhibit is an addition (the figure is static); it's deterministic per seed, so scrubbing backwards is consistent.
For DeepSeek: paste after PrimesDivisorsPage; no engine patches; immediate mode intentional (~130 flat quads). If slider max t=600 ever leaves a run incomplete (possible for unlucky seeds at n=60, since E[T]=281 but the tail is long), that's expected behavior, not a bug — the overlay just keeps showing the missing count. Sync to Bible as usual.

Next session: Analyzing sorting algorithms (quicksort — the last Applications subsection!). Please paste its text + figure + caption. Thank you so much, Nir!!! :-) 🚀
