// figure.lemma_3.f1.asy -- The same ultimate equality of inscribed and circumscribed figures holds even when the breadths of the parallelograms are unequal.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_3.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen stepblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen basegreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen boundred = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);
pen widthorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,0.0);
pair B = (3.0,0.0);
pair C = (4.6,0.0);
pair D = (6.6,0.0);
pair _u_E = (8.0,0.0);
pair ptA = (0.0,1.4);
pair ptb = (3.0,2.9);
pair ptc = (4.6,3.4);
pair ptd = (6.6,3.9);
pair ptE = (8.0,4.2);
pair A1 = (0.0,1.4);
pair B1 = (3.0,1.4);
pair C1 = (4.6,2.9);
pair D1 = (6.6,3.4);
path curve = ptA--ptb--ptc--ptd--ptE;
path baseAE = A--E;
path rect1 = A--B--B1--A1--cycle;
path rect2 = B--C--C1--B1--cycle;
path rect3 = C--D--D1--C1--cycle;
pair A = (0.0,0.0);
pair F = (3.0,0.0);
pair _u_E = (8.0,0.0);
pair ptA = (0.0,1.4);
pair fpt = (3.0,1.4);
path curve2 = ptA--fpt;
path baseAE = A--E;
path AF = A--F;
path FAaf = A--F--fpt--ptA--cycle;

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);

  // STABILO underlay (current step's heart only)
  if (on1) draw(rect1, STABILO_1_1);
  if (on2) draw(FAaf, STABILO_2_1);

  // ink pass
  dot(A, on2 ? BLACK : BLACK);
  dot(F, on2 ? BLACK : BLACK);
  dot(_u_E, on2 ? BLACK : BLACK);
  draw(curve2, on2 ? stepblue : BLACK);
  draw(baseAE, on2 ? basegreen : BLACK);
  draw(AF, on2 ? widthorange : BLACK);
  draw(FAaf, on2 ? boundred : BLACK);
  dot(A, on1 ? BLACK : BLACK);
  dot(B, on1 ? BLACK : BLACK);
  dot(C, on1 ? BLACK : BLACK);
  dot(D, on1 ? BLACK : BLACK);
  dot(_u_E, on1 ? BLACK : BLACK);
  draw(curve, on1 ? stepblue : BLACK);
  draw(baseAE, on1 ? basegreen : BLACK);
  draw(rect1, on1 ? stepblue : BLACK);
  draw(rect2, on1 ? stepblue : BLACK);
  draw(rect3, on1 ? stepblue : BLACK);
  label("$A$", A, SW);
  label("$B$", B, S);
  label("$C$", C, S);
  label("$D$", D, S);
  label("$E$", _u_E, SE);
  label("$a$", ptA, NW);
  label("$b$", ptb, N);
  label("$c$", ptc, N);
  label("$d$", ptd, N);
  label("$E$", ptE, NE);
  label("$A$", A, SW);
  label("$F$", F, S);
  label("$a$", ptA, NW);
  label("$f$", fpt, NE);
}
drawAll(highlight);
