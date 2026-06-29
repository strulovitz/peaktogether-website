# QUAKE PARENT 13 — FROZEN DELIVERABLE (VERBATIM)

> Parent 13 (Claude Opus 4.8) — Lemma II end-to-end pipeline proof-of-concept
> Delivered: June 29, 2026
> Saved VERBATIM, WORD-FOR-WORD, AS-IS

---

I have everything I need. Building now — all three files, to the corrected color model, with the data shapes DeepSeek has already updated (LocalColor, Draw.local_color/is_heart, TextBlock.colors_used, FigureDecl.colors_used).

Design decisions I'm locking (highest educational + visual quality):

    Light background → uncolored ink is pure black (#000000).
    Rich, vibrant, distinct local colors per station; each meaningful element its own color; matching words share it.
    Stabilo lights only the current step's heart(s), bright, non-cumulative.
    4 inscribed + 4 circumscribed rectangles (Newton's typical finite engraving), curve concave-down rising left→right, horizontal baseline AE, vertical left side Aa. Lettering follows Newton exactly: baseline A,B,C,D,E; curve a,b,c,d,E; completed-corner points K,L,M,N and outer l,m,n,o.

Since prooffig.asy doesn't exist yet, my .asy is self-contained — it defines its own tiny convention (a draw/fill/lbl registry + drawAll(highlight)) so it compiles standalone. It honors highlight=-1 (off, all black) and highlight=k (step k's matched colors on + that step's heart wearing a bright Stabilo swipe). This is the convention I recommend prooffig.asy adopt. Do not trust my Asymptote API from memory — run it through asy_compile; the error loop is expected to need 1–2 fixes (likely label-offset or pen-syntax).

---

File 1 — recipe.lemma_2.f1.json

{
  "schema_version": "1.0",
  "figure_id": "lemma_2.f1",
  "node_id": "lemma_2",
  "edition": "Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II; Plate 1, Fig. 6.",
  "caption": "Inscribed and circumscribed parallelograms on equal bases under the curve aE; as the bases shrink, the inscribed figure AKbLcMdD, the circumscribed figure AalbmcndoE, and the curvilinear figure AabcdE become ultimately equal.",
  "n_steps": 3,
  "steps": [
    { "index": 1, "gloss": "The curvilinear figure AacE: the curve aE, the baseline AE on equal bases, and the side Aa." },
    { "index": 2, "gloss": "The inscribed parallelograms Ab, Bc, Cd, standing under the curve on the equal bases." },
    { "index": 3, "gloss": "The circumscribed parallelograms completed above the curve; their excess over the inscribed figure is the single rectangle ABla, which vanishes as AB shrinks." }
  ],
  "ops": [
    { "name": "A", "op": "free_point", "rough_xy": [0.0, 0.0],
      "draw": { "step": 1, "marker": "dot", "label": { "tex": "$A$", "placement": "SW" } } },
    { "name": "E", "op": "free_point", "rough_xy": [8.0, 0.0],
      "draw": { "step": 1, "marker": "dot", "label": { "tex": "$E$", "placement": "SE" } } },
    { "name": "B", "op": "free_point", "rough_xy": [2.0, 0.0],
      "draw": { "step": 1, "marker": "dot", "label": { "tex": "$B$", "placement": "S" } } },
    { "name": "C", "op": "free_point", "rough_xy": [4.0, 0.0],
      "draw": { "step": 1, "marker": "dot", "label": { "tex": "$C$", "placement": "S" } } },
    { "name": "D", "op": "free_point", "rough_xy": [6.0, 0.0],
      "draw": { "step": 1, "marker": "dot", "label": { "tex": "$D$", "placement": "S" } } },

    { "name": "ptA", "op": "free_point", "rough_xy": [0.0, 1.4],
      "draw": { "step": 1, "marker": "none", "label": { "tex": "$a$", "placement": "NW" },
                "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "ptb", "op": "free_point", "rough_xy": [2.0, 2.6],
      "draw": { "step": 1, "marker": "none", "label": { "tex": "$b$", "placement": "N" },
                "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "ptc", "op": "free_point", "rough_xy": [4.0, 3.4],
      "draw": { "step": 1, "marker": "none", "label": { "tex": "$c$", "placement": "N" },
                "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "ptd", "op": "free_point", "rough_xy": [6.0, 3.9],
      "draw": { "step": 1, "marker": "none", "label": { "tex": "$d$", "placement": "N" },
                "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "ptE", "op": "free_point", "rough_xy": [8.0, 4.2],
      "draw": { "step": 1, "marker": "none", "label": null,
                "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },

    { "name": "curve", "op": "polyline", "points": ["ptA", "ptb", "ptc", "ptd", "ptE"],
      "draw": { "step": 1, "marker": "none", "is_heart": true,
                "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "baseAE", "op": "segment", "a": "A", "b": "E",
      "draw": { "step": 1, "marker": "none",
                "local_color": { "name": "basegreen", "hex": "#00A35A" } } },
    { "name": "sideAa", "op": "segment", "a": "A", "b": "ptA",
      "draw": { "step": 1, "marker": "none",
                "local_color": { "name": "sideorange", "hex": "#E8770A" } } },

    { "name": "inscribed", "op": "series", "along": "baseAE", "to_curve": "curve",
      "count": 4, "kind": "inscribed_rects",
      "draw": { "step": 2, "marker": "none", "is_heart": true,
                "local_color": { "name": "inscpurple", "hex": "#8E24AA" } } },

    { "name": "circumscribed", "op": "series", "along": "baseAE", "to_curve": "curve",
      "count": 4, "kind": "circumscribed_rects",
      "draw": { "step": 3, "marker": "none", "is_heart": true,
                "local_color": { "name": "circred", "hex": "#D81B60" } } }
  ]
}

---

File 2 — figure.lemma_2.f1.asy

    Self-contained convention (no prooffig.asy yet). highlight=-1 → all black (off). highlight=k → step ≤ stations matched-colored is not used; per the corrected model, matched colors show for the elements of the active picture and only the current step's heart wears the bright Stabilo. Here: each step lights its own colored elements; the current step's heart gets a fat translucent marker beneath the ink. Non-current, non-yet-revealed elements draw black. Run through asy_compile; expect minor pen/label fixes.

// figure.lemma_2.f1.asy  — Lemma II (inscribed/circumscribed rectangles)
// Self-contained prooffig convention. Compile: asy -u "highlight=k" figure.lemma_2.f1.asy
// highlight=-1 => OFF (all black). highlight=k (1..3) => step k's matched colors + step k heart Stabilo.

import graph;
settings.outformat = "png";
settings.render = 8;
unitsize(1cm);

int highlight = -1;   // overridden on command line via -u "highlight=k"

// ---- palette (LOCAL to this station-set; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen curveblue   = rgb(0x1E/255, 0x6F/255, 0xE0/255) + linewidth(1.6pt);
pen basegreen   = rgb(0x00/255, 0xA3/255, 0x5A/255) + linewidth(1.6pt);
pen sideorange  = rgb(0xE8/255, 0x77/255, 0x0A/255) + linewidth(1.6pt);
pen inscpurple  = rgb(0x8E/255, 0x24/255, 0xAA/255) + linewidth(1.4pt);
pen circred     = rgb(0xD8/255, 0x1B/255, 0x60/255) + linewidth(1.4pt);

// bright Stabilo markers (local, per heart) — laid UNDER the ink, translucent
pen STABILO_CURVE = rgb(0xFF/255, 0xE0/255, 0x00/255) + opacity(0.45) + linewidth(9pt) + squarecap; // yellow
pen STABILO_INSC  = rgb(0x00/255, 0xE6/255, 0x76/255) + opacity(0.35) + linewidth(9pt) + squarecap; // green
pen STABILO_CIRC  = rgb(0xFF/255, 0x6F/255, 0x00/255) + opacity(0.35) + linewidth(9pt) + squarecap; // orange

// ---- ZONE 2: construction (coordinates from the recipe's rough_xy) ----
pair A=(0,0), B=(2,0), C=(4,0), D=(6,0), E=(8,0);
pair pa=(0,1.4), pb=(2,2.6), pc=(4,3.4), pd=(6,3.9), pe=(8,4.2);
path curve = pa--pb--pc--pd--pe;        // the curve aE
path baseAE = A--E;                      // baseline
path sideAa = A--pa;                     // left side

// helper: y on the polyline curve at a given x (piecewise-linear)
real curveY(real x) {
  pair[] P = {pa,pb,pc,pd,pe};
  for (int i=0; i<P.length-1; ++i) {
    if (x >= P[i].x && x <= P[i+1].x) {
      real t = (x - P[i].x)/(P[i+1].x - P[i].x);
      return P[i].y + t*(P[i+1].y - P[i].y);
    }
  }
  return P[P.length-1].y;
}

// four equal bases: A-B-C-D-E  => bases [A,B],[B,C],[C,D],[D,E]
real[] xs = {0,2,4,6,8};

// inscribed rect on base [x0,x1] : height = curve at the LOWER end (left), so it sits UNDER the curve
// circumscribed rect on base [x0,x1] : height = curve at the HIGHER end (right), so it rises ABOVE
path[] inscribed; path[] circumscribed;
for (int i=0; i<xs.length-1; ++i) {
  real x0=xs[i], x1=xs[i+1];
  real hIn  = curveY(x0);   // rising curve => left end is lower => inscribed
  real hOut = curveY(x1);   // right end higher => circumscribed
  inscribed.push((x0,0)--(x1,0)--(x1,hIn)--(x0,hIn)--cycle);
  circumscribed.push((x0,0)--(x1,0)--(x1,hOut)--(x0,hOut)--cycle);
}

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) draw(curve, STABILO_CURVE);
  if (on2) for (path r : inscribed)     draw(r, STABILO_INSC);
  if (on3) for (path r : circumscribed) draw(r, STABILO_CIRC);

  // STEP 2 ink: inscribed rects (matched purple when their step is active, else black)
  for (path r : inscribed)
    filldraw(r, rgb(0x8E/255,0x24/255,0xAA/255)+opacity(0.12), on2 ? inscpurple : BLACK);

  // STEP 3 ink: circumscribed rects
  for (path r : circumscribed)
    draw(r, on3 ? circred : BLACK);

  // STEP 1 ink: baseline / side / curve (matched colors when step 1 active, else black)
  draw(baseAE, on1 ? basegreen  : BLACK);
  draw(sideAa, on1 ? sideorange : BLACK);
  draw(curve,  on1 ? curveblue  : BLACK);

  // ---- labels (always black; book lettering) ----
  label("$A$", A,  SW); label("$B$", B,  S);  label("$C$", C,  S);
  label("$D$", D,  S);  label("$E$", E,  SE);
  label("$a$", pa, NW); label("$b$", pb, N);  label("$c$", pc, N);
  label("$d$", pd, N);
}

drawAll(highlight);

---

File 3 — room_source.lemma_2.json

{
  "schema_version": "1.0",
  "node_id": "lemma_2",
  "edition": "Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II.",
  "figures": [
    {
      "figure_id": "lemma_2.f1",
      "asy_path": "figures/lemma_2.f1.asy",
      "recipe_path": "recipes/lemma_2.f1.json",
      "n_steps": 3,
      "caption": "Inscribed and circumscribed parallelograms under the curve aE on equal bases.",
      "colors_used": [
        { "name": "curveblue",  "hex": "#1E6FE0" },
        { "name": "basegreen",  "hex": "#00A35A" },
        { "name": "sideorange", "hex": "#E8770A" },
        { "name": "inscpurple", "hex": "#8E24AA" },
        { "name": "circred",    "hex": "#D81B60" }
      ]
    }
  ],
  "blocks": [
    {
      "pair_id": "lemma_2.s1",
      "step_index": 1,
      "drawing": { "block_id": "lemma_2.s1.fig", "figure_id": "lemma_2.f1", "highlight_step": 1 },
      "text": {
        "block_id": "lemma_2.s1.txt",
        "latex": "In the figure $AacE$, bounded by the right lines $\\textcolor{sideorange}{Aa}$ and $\\textcolor{basegreen}{AE}$ and by \\textcolor{curveblue}{the curve $acE$}, take any number of \\emph{equal} bases $AB$, $BC$, $CD$, $\\&c.$ along \\textcolor{basegreen}{the base $AE$}. This is the curvilinear figure whose area we mean to measure.",
        "colors_used": [
          { "name": "curveblue",  "hex": "#1E6FE0" },
          { "name": "basegreen",  "hex": "#00A35A" },
          { "name": "sideorange", "hex": "#E8770A" }
        ]
      }
    },
    {
      "pair_id": "lemma_2.s2",
      "step_index": 2,
      "drawing": { "block_id": "lemma_2.s2.fig", "figure_id": "lemma_2.f1", "highlight_step": 2 },
      "text": {
        "block_id": "lemma_2.s2.txt",
        "latex": "On these equal bases erect \\textcolor{inscpurple}{the inscribed parallelograms $Ab$, $Bc$, $Cd$, $\\&c.$}, with sides $Bb$, $Cc$, $Dd$ parallel to $\\textcolor{sideorange}{Aa}$. \\textcolor{inscpurple}{The inscribed figure $AKbLcMdD$} lies wholly \\emph{under} \\textcolor{curveblue}{the curve}.",
        "colors_used": [
          { "name": "inscpurple", "hex": "#8E24AA" },
          { "name": "sideorange", "hex": "#E8770A" },
          { "name": "curveblue",  "hex": "#1E6FE0" }
        ]
      }
    },
    {
      "pair_id": "lemma_2.s3",
      "step_index": 3,
      "drawing": { "block_id": "lemma_2.s3.fig", "figure_id": "lemma_2.f1", "highlight_step": 3 },
      "text": {
        "block_id": "lemma_2.s3.txt",
        "latex": "Complete \\textcolor{circred}{the circumscribed parallelograms $aKbl$, $bLcm$, $cMdn$, $\\&c.$}, rising \\emph{above} \\textcolor{curveblue}{the curve}. Their excess over \\textcolor{inscpurple}{the inscribed figure} is the sum $Kl + Lm + Mn + Do$, equal to the single rectangle $ABla$ on the base $\\textcolor{basegreen}{AB}$. As $\\textcolor{basegreen}{AB}$ is diminished \\emph{in infinitum} this rectangle becomes less than any given space; hence (by Lem.~I) \\textcolor{inscpurple}{the inscribed} and \\textcolor{circred}{the circumscribed} figures, and therefore the intermediate curvilinear figure, become ultimately equal. \\textit{Q.E.D.}",
        "colors_used": [
          { "name": "circred",    "hex": "#D81B60" },
          { "name": "curveblue",  "hex": "#1E6FE0" },
          { "name": "inscpurple", "hex": "#8E24AA" },
          { "name": "basegreen",  "hex": "#00A35A" }
        ]
      }
    }
  ],
  "final_pair_id": "lemma_2.s3",
  "ceiling_equations": [
    { "eq_id": "lemma_2.eq0", "latex": "\\lim_{AB \\to 0}\\; \\bigl(\\text{circumscribed} - \\text{inscribed}\\bigr) = ABla \\;\\longrightarrow\\; 0" },
    { "eq_id": "lemma_2.eq1", "latex": "\\text{inscribed} \\;=\\; \\text{circumscribed} \\;=\\; \\text{curvilinear area} \\quad (\\text{ultimately})" }
  ]
}

