// figure.prop_13.f1.asy -- If a body moves in the perimeter of a parabola, find the law of the centripetal force tending to the focus.
// Self-contained convention. Compile: asy -u "highlight=k" figure.prop_13.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen parabblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen fociorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen radgreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen constpurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen relgreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen resultred = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_1_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_4_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair D1 = (-5.0,-5.0);
pair D2 = (-5.0,5.0);
pair _u_S = (-3.0,0.0);
pair P = (2.0,4.6);
parabola par = parabola(_u_S, D1);
path SP = _u_S--P;
pair G = (2.0,-4.6);
pair Q = (1.3,3.9);
pair v = (1.55,4.2);
path PG = P--G;
point _tmp_tan = point(P);
line _ax_tan = line(par.V, par.F);
line _perp_tan = perpendicular(_tmp_tan, _ax_tan);
point[] _ips_tan = intersectionpoints(_perp_tan, par);
abscissa _absc_tan = angabscissa(par, _ips_tan[0]);
line tan = tangent(par, _absc_tan);
pair _vd_QR = (_u_S == (0,0)) ? (1,0) : _u_S;
path QR = Q--(Q + 10*unit(_vd_QR));
pair _vd_QT = (_u_S == (0,0)) ? (1,0) : _u_S;
pair _perp_QT = (-_vd_QT.y, _vd_QT.x);
path QT = Q--(Q + 10*unit(_perp_QT));
pair _vd_Qv = (P == (0,0)) ? (1,0) : P;
path Qv = Q--(Q + 10*unit(_vd_Qv));
pair M = (-3.0,4.6);
pair x = (1.05,3.5);
path SM = _u_S--M;
path Pv = P--v;
path Px = P--x;
path xv = x--v;
path tri1 = P--x--v--cycle;
path tri2 = _u_S--P--M--cycle;
pair _u_N = (-3.0,4.6);
pair T = (0.55,2.4);
path SN = _u_S--_u_N;
path Qx = Q--x;
path triQ = Q--x--T--cycle;
path triS = _u_S--P--_u_N--cycle;
path foc = circle(_u_S, 0.14);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);
  bool on4 = (highlight==4);

  // STABILO underlay (current step's heart only)
  if (on1) dot(_u_S, STABILO_1_1);
  if (on1) draw(SP, STABILO_1_2);
  if (on2) draw(tan, STABILO_2_1);
  if (on3) draw(Px, STABILO_3_1);
  if (on4) draw(foc, STABILO_4_1);

  // ink pass
  dot(_u_S, on4 ? BLACK : BLACK);
  dot(P, on4 ? BLACK : BLACK);
  dot(Q, on4 ? BLACK : BLACK);
  dot(T, on4 ? BLACK : BLACK);
  dot(x, on4 ? BLACK : BLACK);
  draw(par, on4 ? parabblue : BLACK);
  draw(SP, on4 ? BLACK : BLACK);
  draw(SN, on4 ? BLACK : BLACK);
  draw(QT, on4 ? BLACK : BLACK);
  draw(Qx, on4 ? resultred : BLACK);
  draw(triQ, on4 ? resultred : BLACK);
  draw(triS, on4 ? BLACK : BLACK);
  draw(foc, on4 ? resultred : BLACK);
  dot(P, on3 ? BLACK : BLACK);
  dot(v, on3 ? BLACK : BLACK);
  dot(x, on3 ? BLACK : BLACK);
  draw(par, on3 ? parabblue : BLACK);
  draw(SP, on3 ? BLACK : BLACK);
  draw(SM, on3 ? BLACK : BLACK);
  draw(Pv, on3 ? relgreen : BLACK);
  draw(Px, on3 ? relgreen : BLACK);
  draw(xv, on3 ? BLACK : BLACK);
  draw(tri1, on3 ? relgreen : BLACK);
  draw(tri2, on3 ? BLACK : BLACK);
  dot(P, on2 ? BLACK : BLACK);
  dot(Q, on2 ? BLACK : BLACK);
  dot(v, on2 ? BLACK : BLACK);
  draw(par, on2 ? parabblue : BLACK);
  draw(SP, on2 ? BLACK : BLACK);
  draw(PG, on2 ? BLACK : BLACK);
  draw(tan, on2 ? constpurple : BLACK);
  draw(QR, on2 ? constpurple : BLACK);
  draw(QT, on2 ? constpurple : BLACK);
  draw(Qv, on2 ? constpurple : BLACK);
  dot(_u_S, on1 ? fociorange : BLACK);
  dot(P, on1 ? BLACK : BLACK);
  draw(par, on1 ? parabblue : BLACK);
  draw(SP, on1 ? radgreen : BLACK);
  label("$S$", _u_S, SW);
  label("$P$", P, NE);
  pair _lbl_SP = point(SP, 0.5);
  label("$SP$", _lbl_SP, N);
  label("$P$", P, NE);
  label("$Q$", Q, NW);
  label("$v$", v, S);
  pair _lbl_QR = point(QR, 0.5);
  label("$QR$", _lbl_QR, NE);
  pair _lbl_QT = point(QT, 0.5);
  label("$QT$", _lbl_QT, E);
  pair _lbl_Qv = point(Qv, 0.5);
  label("$Qv$", _lbl_Qv, SW);
  label("$P$", P, NE);
  label("$v$", v, S);
  label("$x$", x, SW);
  pair _lbl_Pv = point(Pv, 0.5);
  label("$Pv$", _lbl_Pv, E);
  pair _lbl_Px = point(Px, 0.5);
  label("$QR=Pv$", _lbl_Px, SE);
  label("$S$", _u_S, SW);
  label("$P$", P, NE);
  label("$Q$", Q, NW);
  label("$T$", T, S);
  label("$x$", x, SW);
  pair _lbl_Qx = point(Qx, 0.5);
  label("$Qx$", _lbl_Qx, N);
}
drawAll(highlight);
