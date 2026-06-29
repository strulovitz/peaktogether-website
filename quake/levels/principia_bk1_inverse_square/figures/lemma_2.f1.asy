// figure.lemma_2.f1.asy  — Lemma II (inscribed/circumscribed rectangles)
// Self-contained prooffig convention. Compile: asy -u "highlight=k" figure.lemma_2.f1.asy
// highlight=-1 => OFF (all black). highlight=k (1..3) => step k's matched colors + step k heart Stabilo.

import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
// Process command-line user settings: asy -u "highlight=1"
usersetting();

// ---- palette (LOCAL to this station-set; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen curveblue   = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen basegreen   = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen sideorange  = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen inscpurple  = rgb(142/255, 36/255, 170/255) + linewidth(1.4pt);
pen circred     = rgb(216/255, 27/255, 96/255) + linewidth(1.4pt);

// bright Stabilo markers (local, per heart) — laid UNDER the ink, translucent
pen STABILO_CURVE = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap; // yellow
pen STABILO_INSC  = rgb(0/255, 230/255, 118/255) + opacity(0.35) + linewidth(9pt) + squarecap; // green
pen STABILO_CIRC  = rgb(255/255, 111/255, 0/255) + opacity(0.35) + linewidth(9pt) + squarecap; // orange

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
    filldraw(r, rgb(142/255,36/255,170/255)+opacity(0.12), on2 ? inscpurple : BLACK);

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
