// figure.lemma_2.f1.asy -- Inscribed and circumscribed parallelograms on equal bases under the curve aE; as the bases shrink, the inscribed and circumscribed figures and the curvilinear figure become ultimately equal.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_2.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen curveblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen basegreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen sideorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen inscpurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen circred = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,0.0);
pair _u_E = (8.0,0.0);
pair B = (2.0,0.0);
pair C = (4.0,0.0);
pair D = (6.0,0.0);
pair ptA = (0.0,1.4);
pair ptb = (2.0,2.6);
pair ptc = (4.0,3.4);
pair ptd = (6.0,3.9);
pair ptE = (8.0,4.2);
path curve = ptA--ptb--ptc--ptd--ptE;
path baseAE = A--_u_E;
path sideAa = A--ptA;
// series inscribed: built in series-support block below
// series circumscribed: built in series-support block below

// ---- series support (rect loops, gold lemma_2 pattern) ----
pair[] _P = {ptA, ptb, ptc, ptd, ptE};
real curveY(real x) {
  for (int i=0; i<_P.length-1; ++i) {
    if (x >= _P[i].x && x <= _P[i+1].x) {
      real t = (x - _P[i].x)/(_P[i+1].x - _P[i].x);
      return _P[i].y + t*(_P[i+1].y - _P[i].y);
    }
  }
  return _P[_P.length-1].y;
}
// rectangles for series inscribed (kind=inscribed_rects, count=4)
path[] inscribed;
real[] _xs_inscribed = {ptA.x, ptb.x, ptc.x, ptd.x, ptE.x};
for (int i=0; i<_xs_inscribed.length-1; ++i) {
  real x0=_xs_inscribed[i], x1=_xs_inscribed[i+1];
  real h = curveY(min(x0,x1));
  inscribed.push((x0,0)--(x1,0)--(x1,h)--(x0,h)--cycle);
}
// rectangles for series circumscribed (kind=circumscribed_rects, count=4)
path[] circumscribed;
real[] _xs_circumscribed = {ptA.x, ptb.x, ptc.x, ptd.x, ptE.x};
for (int i=0; i<_xs_circumscribed.length-1; ++i) {
  real x0=_xs_circumscribed[i], x1=_xs_circumscribed[i+1];
  real h = curveY(max(x0,x1));
  circumscribed.push((x0,0)--(x1,0)--(x1,h)--(x0,h)--cycle);
}

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) draw(curve, STABILO_1_1);
  if (on2) for (path _r : inscribed) draw(_r, STABILO_2_1);
  if (on3) for (path _r : circumscribed) draw(_r, STABILO_3_1);

  // ink pass
  for (path _r : circumscribed) draw(_r, on3 ? circred : BLACK);
  for (path _r : inscribed) filldraw(_r, rgb(142/255,36/255,170/255)+opacity(0.12), on2 ? inscpurple : BLACK);
  dot(A, on1 ? BLACK : BLACK);
  dot(_u_E, on1 ? BLACK : BLACK);
  dot(B, on1 ? BLACK : BLACK);
  dot(C, on1 ? BLACK : BLACK);
  dot(D, on1 ? BLACK : BLACK);
  draw(curve, on1 ? curveblue : BLACK);
  draw(baseAE, on1 ? basegreen : BLACK);
  draw(sideAa, on1 ? sideorange : BLACK);
  label("$A$", A, SW);
  label("$E$", _u_E, SE);
  label("$B$", B, S);
  label("$C$", C, S);
  label("$D$", D, S);
  label("$a$", ptA, NW);
  label("$b$", ptb, N);
  label("$c$", ptc, N);
  label("$d$", ptd, N);
}
drawAll(highlight);
