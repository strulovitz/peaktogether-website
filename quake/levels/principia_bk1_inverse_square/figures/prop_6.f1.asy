// figure.prop_6.f1.asy -- In a space void of resistance, the centripetal force in the middle of a nascent arc is as the versed sine directly and the square of the time inversely.
// Self-contained convention. Compile: asy -u "highlight=k" figure.prop_6.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen centerorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen arcblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen tangreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen parblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen perpred = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);
pen measpurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_4_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair _u_S = (-2.6,-2.2);
pair P = (2.4,1.9);
pair Q = (1.55,2.55);
real _r_P = abs(P-S);
path P = arc(S, _r_P, degrees(P-S), degrees(Q-S), CCW);
path SP = S--P;
pair _u_S = (-2.6,-2.2);
pair P = (2.4,1.9);
pair Q = (1.55,2.55);
pair Z = (3.4,0.9);
pair R = (1.35,0.75);
real _r_P = abs(P-S);
path P = arc(S, _r_P, degrees(P-S), degrees(Q-S), CCW);
line ZPR = line(Z, R);
path SP = S--P;
path QR = Q--R;
pair _u_S = (-2.6,-2.2);
pair P = (2.4,1.9);
pair Q = (1.55,2.55);
pair Z = (3.4,0.9);
pair R = (1.9,1.05);
point _ft_T = foot(point(Q), line(point(S), point(P)));
pair T = _ft_T;
real _r_P = abs(P-S);
path P = arc(S, _r_P, degrees(P-S), degrees(Q-S), CCW);
line ZPR = line(Z, R);
path SP = S--P;
line QR = parallel(Q, S);
line QT = perpendicular(Q, S);
pair QTP = T + 0.7*unit((unit(Q-T)+unit(P-T))/2);
pair _u_S = (-2.6,-2.2);
pair P = (2.4,1.9);
pair Q = (1.55,2.55);
pair R = (1.9,1.05);
pair Z = (3.4,0.9);
point _ft_T = foot(point(Q), line(point(S), point(P)));
pair T = _ft_T;
real _r_P = abs(P-S);
path P = arc(S, _r_P, degrees(P-S), degrees(Q-S), CCW);
line ZPR = line(Z, R);
path SP = S--P;
line QR = parallel(Q, S);
line QT = perpendicular(Q, S);
path quad = S--Q--P--cycle;

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);
  bool on4 = (highlight==4);

  // STABILO underlay (current step's heart only)
  if (on1) draw(P, STABILO_1_1);
  if (on2) draw(ZPR, STABILO_2_1);
  if (on3) draw(QR, STABILO_3_1);
  if (on3) draw(QT, STABILO_3_2);
  if (on4) draw(quad, STABILO_4_1);

  // ink pass
  dot(_u_S, on4 ? BLACK : BLACK);
  dot(P, on4 ? BLACK : BLACK);
  dot(Q, on4 ? BLACK : BLACK);
  draw(T, on4 ? BLACK : BLACK);
  draw(P, on4 ? BLACK : BLACK);
  draw(ZPR, on4 ? BLACK : BLACK);
  draw(SP, on4 ? BLACK : BLACK);
  draw(QR, on4 ? BLACK : BLACK);
  draw(QT, on4 ? BLACK : BLACK);
  draw(quad, on4 ? measpurple : BLACK);
  dot(_u_S, on3 ? BLACK : BLACK);
  dot(P, on3 ? BLACK : BLACK);
  dot(Q, on3 ? BLACK : BLACK);
  draw(T, on3 ? BLACK : BLACK);
  draw(P, on3 ? BLACK : BLACK);
  draw(ZPR, on3 ? BLACK : BLACK);
  draw(SP, on3 ? BLACK : BLACK);
  draw(QR, on3 ? parblue : BLACK);
  draw(QT, on3 ? perpred : BLACK);
  markangle(line(T,Q), line(T,P), radius=0.5cm, on3 ? BLACK : BLACK);
  dot(_u_S, on2 ? BLACK : BLACK);
  dot(P, on2 ? BLACK : BLACK);
  dot(Q, on2 ? BLACK : BLACK);
  draw(P, on2 ? BLACK : BLACK);
  draw(ZPR, on2 ? tangreen : BLACK);
  draw(SP, on2 ? BLACK : BLACK);
  draw(QR, on2 ? BLACK : BLACK);
  dot(_u_S, on1 ? centerorange : BLACK);
  dot(P, on1 ? BLACK : BLACK);
  dot(Q, on1 ? BLACK : BLACK);
  draw(P, on1 ? arcblue : BLACK);
  draw(SP, on1 ? BLACK : BLACK);
  label("$S$", _u_S, SW);
  label("$P$", P, NE);
  label("$Q$", Q, N);
  label("$S$", _u_S, SW);
  label("$P$", P, E);
  label("$Q$", Q, N);
  label("$Z$", Z, SE);
  label("$R$", R, S);
  pair _lbl_ZPR = point(ZPR, 0.5);
  label("$\\text{tangent }ZPR$", _lbl_ZPR, E);
  label("$S$", _u_S, SW);
  label("$P$", P, E);
  label("$Q$", Q, N);
  label("$Z$", Z, SE);
  label("$R$", R, SE);
  label("$T$", T, SW);
  pair _lbl_QR = point(QR, 0.5);
  label("$QR\\parallel SP$", _lbl_QR, NE);
  pair _lbl_QT = point(QT, 0.5);
  label("$QT\\perp SP$", _lbl_QT, W);
  label("$S$", _u_S, SW);
  label("$P$", P, E);
  label("$Q$", Q, N);
  label("$R$", R, SE);
  label("$Z$", Z, SE);
  label("$T$", T, SW);
  pair _lbl_quad = point(quad, 0.5);
  label("$SP^2\\!\\cdot\\!QT^2/QR$", _lbl_quad, Center);
}
drawAll(highlight);
