// figure.prop_2.f1.asy -- Every body that moves in a curve and describes areas proportional to the times about a point is urged by a centripetal force directed to that point.
// Self-contained convention. Compile: asy -u "highlight=k" figure.prop_2.f1.asy
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
pen fanpurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen deflectblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen radialred = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_1_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_1_3 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair _u_S = (0.0,4.0);
pair A = (-6.0,0.0);
pair B = (-3.0,0.0);
pair C = (0.0,0.0);
pair D = (3.0,0.0);
pair _u_E = (6.0,0.0);
path _u_path = A--B--C--D--_u_E;
path SA = A--_u_S;
path SB = B--_u_S;
path SC = C--_u_S;
path SD = D--_u_S;
path _u_SE = _u_E--_u_S;
path triSAB = _u_S--A--B--cycle;
path triSBC = _u_S--B--C--cycle;
path triSCD = _u_S--C--D--cycle;
pair c = (3.0,0.0);
path Sc = c--_u_S;
path inertial = B--c;
path path1 = A--B;
path path2 = B--C;
path cC = c--C;
pair _vd_BSpar = (B == (0,0)) ? (1,0) : B;
path BSpar = B--(B + 10*unit(_vd_BSpar));
path fB = B--(shift(10*unit(_u_S-B))*B);
path fC = C--(shift(10*unit(_u_S-C))*C);
path fD = D--(shift(10*unit(_u_S-D))*D);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) draw(triSAB, STABILO_1_1);
  if (on1) draw(triSBC, STABILO_1_2);
  if (on1) draw(triSCD, STABILO_1_3);
  if (on2) draw(cC, STABILO_2_1);
  if (on3) draw(fB, STABILO_3_1);
  if (on3) draw(fC, STABILO_3_2);

  // ink pass
  draw(_u_path, on3 ? BLACK : BLACK);
  draw(fB, on3 ? radialred : BLACK);
  draw(fC, on3 ? radialred : BLACK);
  draw(fD, on3 ? radialred : BLACK);
  draw(SA, on3 ? BLACK : BLACK);
  draw(_u_SE, on3 ? BLACK : BLACK);
  draw(SA, on2 ? BLACK : BLACK);
  draw(SB, on2 ? BLACK : BLACK);
  draw(SC, on2 ? BLACK : BLACK);
  draw(Sc, on2 ? BLACK : BLACK);
  draw(inertial, on2 ? BLACK : BLACK);
  draw(path1, on2 ? BLACK : BLACK);
  draw(path2, on2 ? BLACK : BLACK);
  draw(cC, on2 ? deflectblue : BLACK);
  draw(BSpar, on2 ? deflectblue : BLACK);
  draw(_u_path, on1 ? fanpurple : BLACK);
  draw(SA, on1 ? BLACK : BLACK);
  draw(SB, on1 ? BLACK : BLACK);
  draw(SC, on1 ? BLACK : BLACK);
  draw(SD, on1 ? BLACK : BLACK);
  draw(_u_SE, on1 ? BLACK : BLACK);
  draw(triSAB, on1 ? fanpurple : BLACK);
  draw(triSBC, on1 ? fanpurple : BLACK);
  draw(triSCD, on1 ? fanpurple : BLACK);
  label("$S$", _u_S, N);
  label("$A$", A, SW);
  label("$B$", B, S);
  label("$C$", C, S);
  label("$D$", D, S);
  label("$E$", _u_E, SE);
  label("$S$", _u_S, N);
  label("$A$", A, SW);
  label("$B$", B, SW);
  label("$C$", C, SE);
  label("$c$", c, S);
  pair _lbl_inertial = point(inertial, 0.5);
  label("$Bc$", _lbl_inertial, S);
  pair _lbl_cC = point(cC, 0.5);
  label("$cC \\parallel BS$", _lbl_cC, NE);
  pair _lbl_BSpar = point(BSpar, 0.5);
  label("$\\parallel BS$", _lbl_BSpar, W);
  label("$S$", _u_S, N);
  label("$A$", A, SW);
  label("$B$", B, SW);
  label("$C$", C, S);
  label("$D$", D, SE);
  label("$E$", _u_E, SE);
  pair _lbl_fB = point(fB, 0.5);
  label("$BS$", _lbl_fB, W);
  pair _lbl_fC = point(fC, 0.5);
  label("$CS$", _lbl_fC, E);
  pair _lbl_fD = point(fD, 0.5);
  label("$DS$", _lbl_fD, E);
}
drawAll(highlight);
