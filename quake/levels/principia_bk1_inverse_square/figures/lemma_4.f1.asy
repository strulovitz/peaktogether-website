// figure.lemma_4.f1.asy -- If corresponding parallelograms in two figures share one ultimate ratio each-to-each, then the whole figures are in that same ratio.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_4.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen figaviolet = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen curveblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen basegreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen figbteal = rgb(0/255, 137/255, 123/255) + linewidth(1.6pt);
pen curvered = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);
pen corrorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_3 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,5.0);
pair _u_E = (6.0,5.0);
pair B = (2.0,5.0);
pair C = (4.0,5.0);
pair ptA = (0.0,6.0);
pair ptb = (2.0,7.0);
pair ptc = (4.0,7.7);
pair ptE = (6.0,8.1);
path curveA = ptA--ptb--ptc--ptE;
path baseAE = A--E;
// series rankA: built in series-support block below
pair P = (0.0,0.0);
pair T = (6.0,0.0);
pair Q = (2.0,0.0);
pair R = (4.0,0.0);
pair ptP = (0.0,2.6);
pair ptr = (2.0,2.0);
pair pts = (4.0,1.3);
pair ptT = (6.0,0.6);
path curveB = ptP--ptr--pts--ptT;
path basePT = P--T;
// series rankB: built in series-support block below
pair m1 = (1.0,5.5);
pair m2 = (3.0,6.0);
pair m3 = (5.0,6.3);
pair n1 = (1.0,1.3);
pair n2 = (3.0,1.0);
pair n3 = (5.0,0.6);
path link1 = m1--n1;
path link2 = m2--n2;
path link3 = m3--n3;

// ---- series support (rect loops, gold lemma_2 pattern) ----
pair[] _P = {ptA, ptb, ptc, ptE};
real curveY(real x) {
  for (int i=0; i<_P.length-1; ++i) {
    if (x >= _P[i].x && x <= _P[i+1].x) {
      real t = (x - _P[i].x)/(_P[i+1].x - _P[i].x);
      return _P[i].y + t*(_P[i+1].y - _P[i].y);
    }
  }
  return _P[_P.length-1].y;
}
// rectangles for series rankA (kind=inscribed_rects, count=3)
path[] rankA;
real[] _xs_rankA = {ptA.x, ptb.x, ptc.x, ptE.x};
for (int i=0; i<_xs_rankA.length-1; ++i) {
  real x0=_xs_rankA[i], x1=_xs_rankA[i+1];
  real h = curveY(min(x0,x1));
  rankA.push((x0,0)--(x1,0)--(x1,h)--(x0,h)--cycle);
}
// rectangles for series rankB (kind=inscribed_rects, count=3)
path[] rankB;
real[] _xs_rankB = {ptP.x, ptr.x, pts.x, ptT.x};
for (int i=0; i<_xs_rankB.length-1; ++i) {
  real x0=_xs_rankB[i], x1=_xs_rankB[i+1];
  real h = curveY(min(x0,x1));
  rankB.push((x0,0)--(x1,0)--(x1,h)--(x0,h)--cycle);
}

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) for (path _r : rankA) draw(_r, STABILO_1_1);
  if (on2) for (path _r : rankB) draw(_r, STABILO_2_1);
  if (on3) draw(link1, STABILO_3_1);
  if (on3) draw(link2, STABILO_3_2);
  if (on3) draw(link3, STABILO_3_3);

  // ink pass
  draw(link1, on3 ? corrorange : BLACK);
  draw(link2, on3 ? corrorange : BLACK);
  draw(link3, on3 ? corrorange : BLACK);
  dot(P, on2 ? BLACK : BLACK);
  dot(T, on2 ? BLACK : BLACK);
  dot(Q, on2 ? BLACK : BLACK);
  dot(R, on2 ? BLACK : BLACK);
  draw(curveB, on2 ? curvered : BLACK);
  draw(basePT, on2 ? basegreen : BLACK);
  for (path _r : rankB) filldraw(_r, rgb(142/255,36/255,170/255)+opacity(0.12), on2 ? figbteal : BLACK);
  dot(A, on1 ? BLACK : BLACK);
  dot(_u_E, on1 ? BLACK : BLACK);
  dot(B, on1 ? BLACK : BLACK);
  dot(C, on1 ? BLACK : BLACK);
  draw(curveA, on1 ? curveblue : BLACK);
  draw(baseAE, on1 ? basegreen : BLACK);
  for (path _r : rankA) filldraw(_r, rgb(142/255,36/255,170/255)+opacity(0.12), on1 ? figaviolet : BLACK);
  label("$A$", A, SW);
  label("$E$", _u_E, SE);
  label("$B$", B, S);
  label("$C$", C, S);
  label("$a$", ptA, NW);
  label("$b$", ptb, N);
  label("$c$", ptc, N);
  label("$E$", ptE, NE);
  label("$P$", P, SW);
  label("$T$", T, SE);
  label("$Q$", Q, S);
  label("$R$", R, S);
  label("$p$", ptP, NW);
  label("$r$", ptr, N);
  label("$s$", pts, N);
  label("$T$", ptT, NE);
  label("$p_1$", m1, N);
  label("$p_2$", m2, N);
  label("$p_3$", m3, N);
  label("$q_1$", n1, S);
  label("$q_2$", n2, S);
  label("$q_3$", n3, S);
}
drawAll(highlight);
