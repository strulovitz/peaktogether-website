// figure.prop_4.f1.asy -- The centripetal force of a body moving uniformly in a circle is as the square of the speed divided by the radius.
// Self-contained convention. Compile: asy -u "highlight=k" figure.prop_4.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen velblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen radgreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen forceorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair _termpos_1_1 = (-2.40, 0.00);
pair _termpos_1_2 = (0.00, 0.00);
pair _termpos_1_3 = (2.40, 0.00);
pair _termpos_2_1 = (-1.20, -3.50);
pair _termpos_2_2 = (1.20, -3.50);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);

  // STABILO underlay (current step's heart only)
  if (on1) label("$v^2$", _termpos_1_1, STABILO_1_1);
  if (on2) label("$v^2$", _termpos_2_1, STABILO_2_1);

  // ink pass
  label("$v^2$", _termpos_1_1, on1 ? velblue : BLACK);
  label("$F$", _termpos_1_2, on1 ? forceorange : BLACK);
  label("$r$", _termpos_1_3, on1 ? radgreen : BLACK);
  label("$v^2$", _termpos_2_1, on2 ? velblue : BLACK);
  label("$r$", _termpos_2_2, on2 ? radgreen : BLACK);
}
drawAll(highlight);
