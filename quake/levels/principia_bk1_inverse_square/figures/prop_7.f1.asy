// figure.prop_7.f1.asy -- If a body revolves in the circumference of a circle, find the law of centripetal force directed to any given point.
// Self-contained convention. Compile: asy -u "highlight=k" figure.prop_7.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen circblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen centerorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen radgreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen tanteal = rgb(0/255, 137/255, 123/255) + linewidth(1.6pt);
pen diampurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen constred = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair O = (0.0,0.0);
path circ = circle(O, 3.2);
pair P = (2.8,-1.5);
pair Q = (1.3,2.9);
pair _u_S = (0.7,-0.8);
path SP = _u_S--P;
pair V = (-1.65,0.3);
pair A = (1.65,-0.3);
real[] _ts_tanpz = times(circ, P);
pair _d_tanpz = dir(circ, _ts_tanpz[0]);
line tanpz = line(P, P + _d_tanpz);
path PV = P--V;
path VA = V--A;
path AP = A--P;
pair VPA = P + 0.7*unit((unit(V-P)+unit(A-P))/2);
pair _v_T = P - _u_S;
real _t_T = dot(Q - _u_S, _v_T) / dot(_v_T, _v_T);
pair T = _u_S + _t_T * _v_T;
pair _vd_QT = (_u_S == (0,0)) ? (1,0) : _u_S;
pair _perp_QT = (-_vd_QT.y, _vd_QT.x);
path QT = Q--(Q + 10*unit(_perp_QT));
pair _vd_LR = (_u_S == (0,0)) ? (1,0) : _u_S;
path LR = Q--(Q + 10*unit(_vd_LR));
pair R = (2.35,2.15);
pair L = (-2.9,1.35);
pair Z = (3.5,-1.0);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) draw(SP, STABILO_1_1);
  if (on2) draw(tanpz, STABILO_2_1);
  if (on3) draw(QT, STABILO_3_1);
  if (on3) draw(LR, STABILO_3_2);

  // ink pass
  draw(circ, on3 ? circblue : BLACK);
  dot(_u_S, on3 ? BLACK : BLACK);
  draw(tanpz, on3 ? tanteal : BLACK);
  draw(SP, on3 ? BLACK : BLACK);
  draw(T, on3 ? BLACK : BLACK);
  draw(QT, on3 ? constred : BLACK);
  draw(LR, on3 ? constred : BLACK);
  dot(R, on3 ? BLACK : BLACK);
  dot(L, on3 ? BLACK : BLACK);
  dot(Z, on3 ? BLACK : BLACK);
  draw(circ, on2 ? circblue : BLACK);
  dot(_u_S, on2 ? BLACK : BLACK);
  draw(tanpz, on2 ? tanteal : BLACK);
  draw(PV, on2 ? diampurple : BLACK);
  draw(VA, on2 ? diampurple : BLACK);
  draw(AP, on2 ? diampurple : BLACK);
  markangle(line(P,V), line(P,A), radius=0.5cm, on2 ? BLACK : BLACK);
  draw(circ, on1 ? circblue : BLACK);
  dot(_u_S, on1 ? centerorange : BLACK);
  draw(SP, on1 ? radgreen : BLACK);
  pair _lbl_circ = point(circ, 0.5);
  label("$VQPA$", _lbl_circ, W);
  label("$P$", P, SE);
  label("$Q$", Q, NW);
  label("$S$", _u_S, NE);
  pair _lbl_SP = point(SP, 0.5);
  label("$SP$", _lbl_SP, S);
  label("$P$", P, SE);
  label("$V$", V, W);
  label("$A$", A, E);
  label("$S$", _u_S, NE);
  pair _lbl_tanpz = point(tanpz, 0.5);
  label("$PRZ$", _lbl_tanpz, NE);
  pair _lbl_PV = point(PV, 0.5);
  label("$PV$", _lbl_PV, N);
  pair _lbl_VA = point(VA, 0.5);
  label("$VA$", _lbl_VA, S);
  pair _lbl_AP = point(AP, 0.5);
  label("$AP$", _lbl_AP, E);
  label("$P$", P, SE);
  label("$Q$", Q, NW);
  label("$S$", _u_S, NE);
  label("$V$", V, W);
  pair _lbl_QT = point(QT, 0.5);
  label("$QT$", _lbl_QT, E);
  pair _lbl_LR = point(LR, 0.5);
  label("$LR$", _lbl_LR, N);
  label("$R$", R, NE);
  label("$L$", L, W);
  label("$Z$", Z, E);
}
drawAll(highlight);
