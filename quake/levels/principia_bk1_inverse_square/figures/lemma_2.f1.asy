// figure.lemma_2.f1.asy -- If in any figure AacE there be inscribed parallelograms on equal bases and circumscribed parallelograms completed: as the bases are diminished without limit, the inscribed, circumscribed, and curvilinear figures have the ultimate ratio of equality.
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
pen curve = rgb(31/255, 111/255, 235/255) + linewidth(1.6pt);
pen base = rgb(184/255, 134/255, 11/255) + linewidth(1.6pt);
pen insc = rgb(207/255, 59/255, 47/255) + linewidth(1.6pt);
pen circ = rgb(46/255, 160/255, 67/255) + linewidth(1.6pt);
pen excess = rgb(207/255, 59/255, 47/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_3 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_3 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,0.0);
pair _u_E = (9.0,0.0);
pair a = (0.0,4.0);
pair B = (3.0,0.0);
pair C = (6.0,0.0);
pair D = (9.0,0.0);
pair p1 = (1.5,3.6);
pair p2 = (4.5,2.6);
pair p3 = (7.5,1.3);
path ae = A--_u_E;
path aa = A--a;
path curv = a--p1--p2--p3--_u_E;
path ab = A--B;
path bc = B--C;
path cd = C--D;
pair b = (3.0,2.6);
pair c = (6.0,1.3);
path ae2 = A--_u_E;
path pa = A--B--b--a--cycle;
path pb = B--C--c--b--cycle;
path pc = C--D--_u_E--c--cycle;
pair l = (0.0,3.6);
pair e_top = (9.0,1.3);
pair c_bot = (6.0,1.3);
path ae3 = A--_u_E;
path pex = A--B--b--l--cycle;

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) draw(curv, STABILO_1_1);
  if (on2) draw(pa, STABILO_2_1);
  if (on2) draw(pb, STABILO_2_2);
  if (on2) draw(pc, STABILO_2_3);
  if (on3) draw(pa, STABILO_3_1);
  if (on3) draw(pb, STABILO_3_2);
  if (on3) draw(pc, STABILO_3_3);

  // ink pass
  draw(ae3, on3 ? BLACK : BLACK);
  draw(curv, on3 ? curve : BLACK);
  draw(pa, on3 ? circ : BLACK);
  draw(pb, on3 ? circ : BLACK);
  draw(pc, on3 ? circ : BLACK);
  draw(pex, on3 ? excess : BLACK);
  draw(ae2, on2 ? BLACK : BLACK);
  draw(curv, on2 ? curve : BLACK);
  draw(pa, on2 ? insc : BLACK);
  draw(pb, on2 ? insc : BLACK);
  draw(pc, on2 ? insc : BLACK);
  draw(ae, on1 ? base : BLACK);
  draw(aa, on1 ? BLACK : BLACK);
  draw(curv, on1 ? curve : BLACK);
  draw(ab, on1 ? base : BLACK);
  draw(bc, on1 ? base : BLACK);
  draw(cd, on1 ? base : BLACK);
  label("$A$", A, SW);
  label("$E$", _u_E, SE);
  label("$a$", a, NW);
  label("$B$", B, S);
  label("$C$", C, S);
  pair _lbl_ae = point(ae, 0.5);
  label("$AE$", _lbl_ae, S);
  pair _lbl_curv = point(curv, 0.5);
  label("$acE$", _lbl_curv, NE);
  label("$A$", A, SW);
  label("$E$", _u_E, SE);
  label("$a$", a, NW);
  label("$B$", B, S);
  label("$C$", C, S);
  label("$D$", D, SE);
  label("$b$", b, NE);
  label("$c$", c, NE);
  pair _lbl_curv = point(curv, 0.5);
  label("$acE$", _lbl_curv, NE);
  label("$A$", A, SW);
  label("$E$", _u_E, SE);
  label("$a$", a, NW);
  label("$l$", l, W);
  label("$B$", B, S);
  label("$C$", C, S);
  label("$b$", b, NE);
  label("$c$", c, NE);
  pair _lbl_curv = point(curv, 0.5);
  label("$acE$", _lbl_curv, NE);
  pair _lbl_pex = point(pex, 0.5);
  label("$ABla$", _lbl_pex, N);
}
drawAll(highlight);
