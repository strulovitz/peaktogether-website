// figure.law_2.f1.asy -- Law II --- The alteration of motion is ever proportional to the motive force impressed; and is made in the direction of the right line in which that force is impressed.
// Self-contained convention. Compile: asy -u "highlight=k" figure.law_2.f1.asy
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
pen motion = rgb(194/255, 24/255, 7/255) + linewidth(1.6pt);
pen force = rgb(27/255, 94/255, 156/255) + linewidth(1.6pt);
pen plain = rgb(0/255, 0/255, 0/255) + linewidth(1.6pt);
pen line = rgb(194/255, 24/255, 7/255) + linewidth(1.6pt);
pen old = rgb(106/255, 27/255, 154/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(194/255, 24/255, 7/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(194/255, 24/255, 7/255) + opacity(0.45) + linewidth(9pt) + squarecap;

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
  label("$\\Delta(\\text{motion})\\ \\;\\propto\\; F\\$", _layoutpos_1, on1 ? motion : BLACK);
  label("$\\Delta(\\text{motion})\\ \\;\\parallel\\; F\\$", _layoutpos_2, on2 ? line : BLACK);
}
drawAll(highlight);
