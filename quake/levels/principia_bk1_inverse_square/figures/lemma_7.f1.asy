// figure.lemma_7.f1.asy -- The ultimate ratio of the arc, the chord, and the tangent, any one to any other, is the ratio of equality.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_7.f1.asy
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
pen auxpurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen equalteal = rgb(0/255, 137/255, 123/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,0.0);
pair ptC = (1.1,1.0);
pair B = (2.2,1.5);
pair D = (2.7,0.7);
path arc = A--ptC--B;
path chordAB = A--B;
path tanAD = A--D;
pair A = (0.0,0.0);
pair ptC = (1.1,1.0);
pair B = (2.2,1.5);
pair D = (2.7,0.7);
path arc = A--ptC--B;
path chordAB = A--B;
path tanAD = A--D;
pair b = (5.5,3.75);
pair d = (6.75,1.75);
pair c = (2.75,2.5);
path Ab = A--(shift(10*unit(b-A))*A);
path Ad = A--(shift(10*unit(d-A))*A);
path secBD = B--D;
path bd = b--d;
path auxarc = A--c--b;
pair A = (0.0,0.0);
pair ptC = (1.1,1.0);
pair B = (2.2,1.5);
pair D = (2.7,0.7);
path arc = A--ptC--B;
path chordAB = A--B;
path tanAD = A--D;
pair b = (5.5,3.75);
pair d = (6.75,1.75);
pair c = (2.75,2.5);
path Ab = A--(shift(10*unit(b-A))*A);
path Ad = A--(shift(10*unit(d-A))*A);
path bd = b--d;
path auxarc = A--c--b;
pair dAb = A + 0.7*unit((unit(d-A)+unit(b-A))/2);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) draw(arc, STABILO_1_1);
  if (on2) draw(auxarc, STABILO_2_1);

  // ink pass
  dot(A, on3 ? BLACK : BLACK);
  dot(B, on3 ? BLACK : BLACK);
  dot(D, on3 ? BLACK : BLACK);
  draw(arc, on3 ? arcblue : BLACK);
  draw(chordAB, on3 ? equalteal : BLACK);
  draw(tanAD, on3 ? equalteal : BLACK);
  dot(b, on3 ? auxpurple : BLACK);
  dot(d, on3 ? auxpurple : BLACK);
  draw(Ab, on3 ? auxpurple : BLACK);
  draw(Ad, on3 ? auxpurple : BLACK);
  draw(bd, on3 ? auxpurple : BLACK);
  draw(auxarc, on3 ? auxpurple : BLACK);
  markangle(line(A,d), line(A,b), radius=0.5cm, on3 ? equalteal : BLACK);
  dot(A, on2 ? BLACK : BLACK);
  dot(B, on2 ? BLACK : BLACK);
  dot(D, on2 ? BLACK : BLACK);
  draw(arc, on2 ? arcblue : BLACK);
  draw(chordAB, on2 ? arcblue : BLACK);
  draw(tanAD, on2 ? arcblue : BLACK);
  dot(b, on2 ? auxpurple : BLACK);
  dot(d, on2 ? auxpurple : BLACK);
  draw(Ab, on2 ? auxpurple : BLACK);
  draw(Ad, on2 ? auxpurple : BLACK);
  draw(secBD, on2 ? arcblue : BLACK);
  draw(bd, on2 ? auxpurple : BLACK);
  draw(auxarc, on2 ? auxpurple : BLACK);
  dot(A, on1 ? BLACK : BLACK);
  dot(B, on1 ? BLACK : BLACK);
  dot(D, on1 ? BLACK : BLACK);
  draw(arc, on1 ? arcblue : BLACK);
  draw(chordAB, on1 ? arcblue : BLACK);
  draw(tanAD, on1 ? arcblue : BLACK);
  label("$A$", A, SW);
  label("$C$", ptC, NW);
  label("$B$", B, N);
  label("$D$", D, E);
  label("$A$", A, SW);
  label("$C$", ptC, NW);
  label("$B$", B, N);
  label("$D$", D, SE);
  label("$b$", b, N);
  label("$d$", d, E);
  label("$c$", c, NW);
  label("$A$", A, SW);
  label("$C$", ptC, NW);
  label("$B$", B, N);
  label("$D$", D, SE);
  label("$b$", b, N);
  label("$d$", d, E);
  label("$c$", c, NW);
  label("$\\angle dAb$", dAb, E);
}
drawAll(highlight);
