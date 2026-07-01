// figure.law_1.f1.asy -- Law I -- Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impressed.
// Self-contained convention. Compile: asy -u "highlight=k" figure.law_1.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen restblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen motiongreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen forceorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen topblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen dragred = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);
pen planetpurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen freeteal = rgb(0/255, 137/255, 123/255) + linewidth(1.6pt);
pen projblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen gravorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_4_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair _phrasepos_1_1 = (0, 0.00);
pair _phrasepos_1_2 = (0, -0.90);
pair _phrasepos_1_3 = (0, -1.80);
pair _phrasepos_2_1 = (0, -3.50);
pair _phrasepos_2_2 = (0, -4.40);
pair _phrasepos_3_1 = (0, -7.00);
pair _phrasepos_3_2 = (0, -7.90);
pair _phrasepos_4_1 = (0, -10.50);
pair _phrasepos_4_2 = (0, -11.40);
pair _phrasepos_4_3 = (0, -12.30);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);
  bool on4 = (highlight==4);

  // STABILO underlay (current step's heart only)
  if (on1) label("forces impress'd", _phrasepos_1_3, STABILO_1_1);
  if (on2) label("a spinning top", _phrasepos_2_1, STABILO_2_1);
  if (on3) label("the planets and comets", _phrasepos_3_1, STABILO_3_1);
  if (on4) label("projectiles", _phrasepos_4_1, STABILO_4_1);

  // ink pass
  label("a state of rest", _phrasepos_1_1, on1 ? restblue : BLACK);
  label("uniform motion in a right line", _phrasepos_1_2, on1 ? motiongreen : BLACK);
  label("forces impress'd", _phrasepos_1_3, on1 ? forceorange : BLACK);
  label("a spinning top", _phrasepos_2_1, on2 ? topblue : BLACK);
  label("retarded by the air", _phrasepos_2_2, on2 ? dragred : BLACK);
  label("the planets and comets", _phrasepos_3_1, on3 ? planetpurple : BLACK);
  label("more free spaces", _phrasepos_3_2, on3 ? freeteal : BLACK);
  label("projectiles", _phrasepos_4_1, on4 ? projblue : BLACK);
  label("the resistance of the air", _phrasepos_4_2, on4 ? dragred : BLACK);
  label("gravity", _phrasepos_4_3, on4 ? gravorange : BLACK);
}
drawAll(highlight);
