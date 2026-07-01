// figure.lemma_10.f1.asy -- The spaces which a body describes from rest under any finite force are, from the very beginning of the motion, in the duplicate ratio of the times.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_10.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen timeblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen velgreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen spacered = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_1_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,0.0);
pair D = (1.4,0.0);
pair _u_E = (3.0,0.0);
pair B = (1.4,1.0);
pair C = (3.0,2.2);
path AE = A--E;
path AD = A--D;
path curve = A--B--C;
path DB = D--B;
path EC = E--C;
pair A = (0.0,0.0);
pair D = (1.4,0.0);
pair _u_E = (3.0,0.0);
pair B = (1.4,1.0);
pair C = (3.0,2.2);
path AE = A--E;
path curve = A--B--C;
path DB = D--B;
path EC = E--C;
path triABD = A--B--D--cycle;
path triACE = A--C--E--cycle;

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);

  // STABILO underlay (current step's heart only)
  if (on1) draw(DB, STABILO_1_1);
  if (on1) draw(EC, STABILO_1_2);
  if (on2) draw(triABD, STABILO_2_1);
  if (on2) draw(triACE, STABILO_2_2);

  // ink pass
  dot(A, on2 ? BLACK : BLACK);
  dot(D, on2 ? BLACK : BLACK);
  dot(_u_E, on2 ? BLACK : BLACK);
  dot(B, on2 ? BLACK : BLACK);
  dot(C, on2 ? BLACK : BLACK);
  draw(AE, on2 ? timeblue : BLACK);
  draw(curve, on2 ? BLACK : BLACK);
  draw(DB, on2 ? BLACK : BLACK);
  draw(EC, on2 ? BLACK : BLACK);
  draw(triABD, on2 ? spacered : BLACK);
  draw(triACE, on2 ? spacered : BLACK);
  dot(A, on1 ? BLACK : BLACK);
  dot(D, on1 ? BLACK : BLACK);
  dot(_u_E, on1 ? BLACK : BLACK);
  dot(B, on1 ? BLACK : BLACK);
  dot(C, on1 ? BLACK : BLACK);
  draw(AE, on1 ? timeblue : BLACK);
  draw(AD, on1 ? timeblue : BLACK);
  draw(curve, on1 ? BLACK : BLACK);
  draw(DB, on1 ? velgreen : BLACK);
  draw(EC, on1 ? velgreen : BLACK);
  label("$A$", A, SW);
  label("$D$", D, S);
  label("$E$", _u_E, S);
  label("$B$", B, NW);
  label("$C$", C, N);
  pair _lbl_AE = point(AE, 0.5);
  label("$AE$", _lbl_AE, S);
  pair _lbl_AD = point(AD, 0.5);
  label("$AD$", _lbl_AD, S);
  pair _lbl_curve = point(curve, 0.5);
  label("$ABC$", _lbl_curve, NW);
  pair _lbl_DB = point(DB, 0.5);
  label("$DB$", _lbl_DB, E);
  pair _lbl_EC = point(EC, 0.5);
  label("$EC$", _lbl_EC, E);
  label("$A$", A, SW);
  label("$D$", D, S);
  label("$E$", _u_E, S);
  label("$B$", B, NW);
  label("$C$", C, N);
  pair _lbl_AE = point(AE, 0.5);
  label("$AE$", _lbl_AE, S);
  pair _lbl_curve = point(curve, 0.5);
  label("$ABC$", _lbl_curve, NW);
  pair _lbl_triABD = point(triABD, 0.5);
  label("$ABD$", _lbl_triABD, E);
  pair _lbl_triACE = point(triACE, 0.5);
  label("$ACE$", _lbl_triACE, NE);
}
drawAll(highlight);
