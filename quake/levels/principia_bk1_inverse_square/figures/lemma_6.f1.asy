// figure.lemma_6.f1.asy -- As a point B on a curve approaches the point of contact A, the angle between the chord AB and the tangent AD is diminished without limit and ultimately vanishes.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_6.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen arcblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen chordgreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen tanorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen anglered = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,0.0);
pair ptC = (2.4,2.0);
pair B = (5.0,3.0);
path arc = A--ptC--B;
path chordAB = A--B;
pair D = (5.6,1.4);
path tanAD = A--D;
pair BAD = A + 0.7*unit((unit(B-A)+unit(D-A))/2);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) draw(arc, STABILO_1_1);
  if (on2) draw(chordAB, STABILO_2_1);

  // ink pass
  dot(A, on3 ? BLACK : BLACK);
  dot(B, on3 ? BLACK : BLACK);
  dot(D, on3 ? BLACK : BLACK);
  draw(arc, on3 ? arcblue : BLACK);
  draw(chordAB, on3 ? chordgreen : BLACK);
  draw(tanAD, on3 ? tanorange : BLACK);
  markangle(line(A,B), line(A,D), radius=0.5cm, on3 ? anglered : BLACK);
  dot(A, on2 ? BLACK : BLACK);
  dot(B, on2 ? BLACK : BLACK);
  draw(arc, on2 ? arcblue : BLACK);
  draw(chordAB, on2 ? chordgreen : BLACK);
  dot(A, on1 ? BLACK : BLACK);
  dot(B, on1 ? BLACK : BLACK);
  draw(arc, on1 ? arcblue : BLACK);
  label("$A$", A, SW);
  label("$C$", ptC, NW);
  label("$B$", B, NE);
  label("$A$", A, SW);
  label("$C$", ptC, NW);
  label("$B$", B, NE);
  label("$A$", A, SW);
  label("$C$", ptC, NW);
  label("$B$", B, NE);
  label("$D$", D, E);
  label("$\\angle BAD$", BAD, E);
}
drawAll(highlight);
