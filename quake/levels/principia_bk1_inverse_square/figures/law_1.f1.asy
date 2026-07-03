// figure.law_1.f1.asy -- Law I — Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impress'd thereon.
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
pen rest = rgb(27/255, 111/255, 179/255) + linewidth(1.6pt);
pen uniform = rgb(46/255, 139/255, 87/255) + linewidth(1.6pt);
pen force = rgb(178/255, 34/255, 34/255) + linewidth(1.6pt);
pen top = rgb(199/255, 120/255, 0/255) + linewidth(1.6pt);
pen cohesion = rgb(106/255, 13/255, 173/255) + linewidth(1.6pt);
pen air = rgb(70/255, 130/255, 180/255) + linewidth(1.6pt);
pen bodies = rgb(139/255, 0/255, 0/255) + linewidth(1.6pt);
pen free = rgb(46/255, 139/255, 87/255) + linewidth(1.6pt);
pen motions = rgb(27/255, 111/255, 179/255) + linewidth(1.6pt);
pen proj = rgb(178/255, 34/255, 34/255) + linewidth(1.6pt);
pen resist = rgb(70/255, 130/255, 180/255) + linewidth(1.6pt);
pen gravity = rgb(106/255, 13/255, 173/255) + linewidth(1.6pt);

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
pair _phrasepos_2_3 = (0, -5.30);
pair _phrasepos_3_1 = (0, -7.00);
pair _phrasepos_3_2 = (0, -7.90);
pair _phrasepos_3_3 = (0, -8.80);
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
  if (on1) label("forces impress'd thereon", _phrasepos_1_3, STABILO_1_1);
  if (on2) label("a top", _phrasepos_2_1, STABILO_2_1);
  if (on3) label("planets and comets", _phrasepos_3_1, STABILO_3_1);
  if (on4) label("projectiles", _phrasepos_4_1, STABILO_4_1);

  // ink pass
  label("a state of rest", _phrasepos_1_1, on1 ? rest : BLACK);
  label("uniform motion in a right line", _phrasepos_1_2, on1 ? uniform : BLACK);
  label("forces impress'd thereon", _phrasepos_1_3, on1 ? force : BLACK);
  label("a top", _phrasepos_2_1, on2 ? top : BLACK);
  label("cohesion", _phrasepos_2_2, on2 ? cohesion : BLACK);
  label("the air", _phrasepos_2_3, on2 ? air : BLACK);
  label("planets and comets", _phrasepos_3_1, on3 ? bodies : BLACK);
  label("more free spaces", _phrasepos_3_2, on3 ? free : BLACK);
  label("motions both progressive and circular", _phrasepos_3_3, on3 ? motions : BLACK);
  label("projectiles", _phrasepos_4_1, on4 ? proj : BLACK);
  label("resistance of the air", _phrasepos_4_2, on4 ? resist : BLACK);
  label("force of gravity", _phrasepos_4_3, on4 ? gravity : BLACK);
}
drawAll(highlight);
