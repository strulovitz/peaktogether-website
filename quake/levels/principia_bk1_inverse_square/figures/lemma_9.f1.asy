// figure.lemma_9.f1.asy -- The areas of triangles formed by ordinates under a curve are ultimately one to the other in the duplicate ratio of the sides.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_9.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen lineblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen curvegreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen ordorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen auxpurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen arearred = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_1_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,0.0);
pair D = (1.4,0.0);
pair _u_E = (3.0,0.0);
pair B = (1.4,1.0);
pair C = (3.0,2.2);
path AE = A--E;
path curve = A--B--C;
path BD = B--D;
path CE = C--E;
path triABD = A--B--D--cycle;
path triACE = A--C--E--cycle;
pair A = (0.0,0.0);
pair D = (1.4,0.0);
pair _u_E = (3.0,0.0);
pair d = (5.5,0.0);
pair e = (8.0,0.0);
pair f = (5.5,2.4);
pair g = (8.0,3.5);
pair b = (5.5,2.0);
pair c = (8.0,3.1);
path base = A--e;
path Ad = A--(shift(10*unit(d-A))*A);
path Ae = A--(shift(10*unit(e-A))*A);
path auxcurve = A--b--c;
path db = d--f;
path ec = e--g;
line tag = tangent(auxcurve, A);
pair A = (0.0,0.0);
pair d = (5.5,0.0);
pair e = (8.0,0.0);
pair f = (5.5,2.4);
pair g = (8.0,3.5);
path base = A--e;
path df = d--f;
path eg = e--g;
path Afd = A--f--d--cycle;
path Age = A--g--e--cycle;

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) draw(BD, STABILO_1_1);
  if (on1) draw(CE, STABILO_1_2);
  if (on2) draw(auxcurve, STABILO_2_1);
  if (on3) draw(Afd, STABILO_3_1);
  if (on3) draw(Age, STABILO_3_2);

  // ink pass
  dot(A, on3 ? BLACK : BLACK);
  dot(d, on3 ? BLACK : BLACK);
  dot(e, on3 ? BLACK : BLACK);
  dot(f, on3 ? BLACK : BLACK);
  dot(g, on3 ? BLACK : BLACK);
  draw(base, on3 ? lineblue : BLACK);
  draw(df, on3 ? arearred : BLACK);
  draw(eg, on3 ? arearred : BLACK);
  draw(Afd, on3 ? arearred : BLACK);
  draw(Age, on3 ? arearred : BLACK);
  dot(A, on2 ? BLACK : BLACK);
  dot(D, on2 ? BLACK : BLACK);
  dot(_u_E, on2 ? BLACK : BLACK);
  dot(d, on2 ? BLACK : BLACK);
  dot(e, on2 ? BLACK : BLACK);
  dot(f, on2 ? BLACK : BLACK);
  dot(g, on2 ? BLACK : BLACK);
  dot(b, on2 ? BLACK : BLACK);
  dot(c, on2 ? BLACK : BLACK);
  draw(base, on2 ? lineblue : BLACK);
  draw(Ad, on2 ? auxpurple : BLACK);
  draw(Ae, on2 ? auxpurple : BLACK);
  draw(auxcurve, on2 ? auxpurple : BLACK);
  draw(db, on2 ? auxpurple : BLACK);
  draw(ec, on2 ? auxpurple : BLACK);
  draw(tag, on2 ? auxpurple : BLACK);
  dot(A, on1 ? BLACK : BLACK);
  dot(D, on1 ? BLACK : BLACK);
  dot(_u_E, on1 ? BLACK : BLACK);
  dot(B, on1 ? BLACK : BLACK);
  dot(C, on1 ? BLACK : BLACK);
  draw(AE, on1 ? lineblue : BLACK);
  draw(curve, on1 ? curvegreen : BLACK);
  draw(BD, on1 ? ordorange : BLACK);
  draw(CE, on1 ? ordorange : BLACK);
  draw(triABD, on1 ? BLACK : BLACK);
  draw(triACE, on1 ? BLACK : BLACK);
  label("$A$", A, SW);
  label("$D$", D, S);
  label("$E$", _u_E, S);
  label("$B$", B, NW);
  label("$C$", C, N);
  pair _lbl_AE = point(AE, 0.5);
  label("$AE$", _lbl_AE, S);
  pair _lbl_curve = point(curve, 0.5);
  label("$ABC$", _lbl_curve, NW);
  pair _lbl_BD = point(BD, 0.5);
  label("$BD$", _lbl_BD, E);
  pair _lbl_CE = point(CE, 0.5);
  label("$CE$", _lbl_CE, E);
  label("$A$", A, SW);
  label("$D$", D, S);
  label("$E$", _u_E, S);
  label("$d$", d, S);
  label("$e$", e, S);
  label("$f$", f, N);
  label("$g$", g, N);
  label("$b$", b, NW);
  label("$c$", c, N);
  pair _lbl_auxcurve = point(auxcurve, 0.5);
  label("$Abc$", _lbl_auxcurve, NW);
  pair _lbl_db = point(db, 0.5);
  label("$db$", _lbl_db, E);
  pair _lbl_ec = point(ec, 0.5);
  label("$ec$", _lbl_ec, E);
  pair _lbl_tag = point(tag, 0.5);
  label("$Ag$", _lbl_tag, N);
  label("$A$", A, SW);
  label("$d$", d, S);
  label("$e$", e, S);
  label("$f$", f, NE);
  label("$g$", g, NE);
  pair _lbl_Afd = point(Afd, 0.5);
  label("$Afd$", _lbl_Afd, NW);
  pair _lbl_Age = point(Age, 0.5);
  label("$Age$", _lbl_Age, N);
}
drawAll(highlight);
