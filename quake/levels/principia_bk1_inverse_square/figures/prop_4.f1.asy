// figure.prop_4.f1.asy -- The centripetal forces of bodies, which by equoble motions describe different circles, tend to the centres of the same circles; and are one to the other, as the squares of the arcs described in equal times applied to the radii of the circles.
// Self-contained convention. Compile: asy -u "highlight=k" figure.prop_4.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);
defaultpen(fontsize(28pt));

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen force = rgb(31/255, 111/255, 235/255) + linewidth(1.6pt);
pen speed = rgb(209/255, 36/255, 47/255) + linewidth(1.6pt);
pen radius = rgb(149/255, 56/255, 0/255) + linewidth(1.6pt);
pen nil = rgb(0/255, 0/255, 0/255) + linewidth(1.6pt);
pen chord = rgb(209/255, 36/255, 47/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 214/255, 214/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 214/255, 214/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair _layoutpos_1 = (0, 0.00);
pair _layoutpos_2 = (0, -3.50);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);

  // STABILO underlay (current step's heart only)
  if (on1) fill(box(_layoutpos_1 + (-4, -0.5), _layoutpos_1 + (4, 0.5)), STABILO_1_1);
  if (on2) fill(box(_layoutpos_2 + (-4, -0.5), _layoutpos_2 + (4, 0.5)), STABILO_2_1);

  // ink pass
  label("$$F$ \\;\\propto\\; \\dfrac{$v^2$}{$r$}$", _layoutpos_1, on1 ? speed : BLACK);
  label("$$F$ \\;\\propto\\; \\dfrac{$v^2$}{$r$}$", _layoutpos_2, on2 ? chord : BLACK);
}
drawAll(highlight);
