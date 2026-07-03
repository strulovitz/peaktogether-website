// figure.lemma_11.f1.asy -- The evanescent subtense of the angle of contact, in all curves of finite curvature, is ultimately in the duplicate ratio of the subtense of the conterminate arc.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_11.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen tanblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen arcgreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen subred = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);
pen auxpurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen relorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,0.0);
pair ptC = (1.8,1.4);
pair B = (3.4,2.3);
pair D = (5.4,0.0);
path arc = A--ptC--B;
path tanAD = A--D;
path chordAB = A--B;
pair Dfoot = (3.4,0.0);
pair G = (0.55,4.05);
pair J = (0.5,3.7);
path subBD = B--Dfoot;
path auxBG = B--G;
path auxAG = A--G;
path aux = circle(A, B, G);
path auxGJ = G--J;

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);

  // STABILO underlay (current step's heart only)
  if (on1) draw(tanAD, STABILO_1_1);
  if (on2) draw(subBD, STABILO_2_1);
  if (on3) draw(auxGJ, STABILO_3_1);

  // ink pass
  dot(A, on3 ? BLACK : BLACK);
  dot(B, on3 ? BLACK : BLACK);
  dot(D, on3 ? BLACK : BLACK);
  dot(Dfoot, on3 ? BLACK : BLACK);
  dot(G, on3 ? BLACK : BLACK);
  dot(J, on3 ? BLACK : BLACK);
  draw(arc, on3 ? arcgreen : BLACK);
  draw(tanAD, on3 ? tanblue : BLACK);
  draw(chordAB, on3 ? relorange : BLACK);
  draw(subBD, on3 ? relorange : BLACK);
  draw(auxAG, on3 ? auxpurple : BLACK);
  draw(auxGJ, on3 ? relorange : BLACK);
  draw(aux, on3 ? auxpurple : BLACK);
  dot(A, on2 ? BLACK : BLACK);
  dot(B, on2 ? BLACK : BLACK);
  dot(D, on2 ? BLACK : BLACK);
  dot(Dfoot, on2 ? BLACK : BLACK);
  dot(G, on2 ? BLACK : BLACK);
  dot(J, on2 ? BLACK : BLACK);
  draw(arc, on2 ? arcgreen : BLACK);
  draw(tanAD, on2 ? tanblue : BLACK);
  draw(chordAB, on2 ? arcgreen : BLACK);
  draw(subBD, on2 ? subred : BLACK);
  draw(auxBG, on2 ? auxpurple : BLACK);
  draw(auxAG, on2 ? auxpurple : BLACK);
  draw(aux, on2 ? auxpurple : BLACK);
  dot(A, on1 ? BLACK : BLACK);
  dot(B, on1 ? BLACK : BLACK);
  dot(D, on1 ? BLACK : BLACK);
  draw(arc, on1 ? arcgreen : BLACK);
  draw(tanAD, on1 ? tanblue : BLACK);
  draw(chordAB, on1 ? arcgreen : BLACK);
  label("$A$", A, SW);
  label("$C$", ptC, NW);
  label("$B$", B, NE);
  label("$D$", D, E);
  pair _lbl_tanAD = point(tanAD, 0.5);
  label("$AD$", _lbl_tanAD, SE);
  pair _lbl_chordAB = point(chordAB, 0.5);
  label("$AB$", _lbl_chordAB, NW);
  label("$A$", A, SW);
  label("$C$", ptC, NW);
  label("$B$", B, NE);
  label("$D$", D, E);
  label("$D$", Dfoot, S);
  label("$G$", G, N);
  label("$J$", J, W);
  pair _lbl_subBD = point(subBD, 0.5);
  label("$BD$", _lbl_subBD, E);
  pair _lbl_auxBG = point(auxBG, 0.5);
  label("$BG$", _lbl_auxBG, NE);
  pair _lbl_auxAG = point(auxAG, 0.5);
  label("$AG$", _lbl_auxAG, W);
  label("$A$", A, SW);
  label("$B$", B, NE);
  label("$D$", D, E);
  label("$D$", Dfoot, S);
  label("$G$", G, N);
  label("$J$", J, W);
  pair _lbl_auxAG = point(auxAG, 0.5);
  label("$AG$", _lbl_auxAG, W);
  pair _lbl_auxGJ = point(auxGJ, 0.5);
  label("$GJ$", _lbl_auxGJ, W);
}
drawAll(highlight);
