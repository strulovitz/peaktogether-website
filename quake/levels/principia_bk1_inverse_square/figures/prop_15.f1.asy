// figure.prop_15.f1.asy -- The periodic times in ellipses are in the sesquiplicate ratio of the greater axes — Kepler's Third Law.
// Self-contained convention. Compile: asy -u "highlight=k" figure.prop_15.f1.asy
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
pen axisorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen ratiopurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen meangreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(246/255, 211/255, 172/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(183/255, 233/255, 207/255) + opacity(0.45) + linewidth(9pt) + squarecap;

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
  label("$\\,T^2\\;\\propto\\;a^3\\qquad\\Longleftrightarrow\\qquad T\\;\\propto\\;a^{ 3/2 }\\,$", _layoutpos_1, on1 ? axisorange : BLACK);
  label("$\\,T \\propto \\pi a b\\;\\xrightarrow{\\;b^2=aL\\;}\\;T \\propto a\\sqrt{aL}\\;=\\;a^{3/2}\\sqrt{L}\\;\\Longrightarrow\\;T^2 \\propto a^3\\,$", _layoutpos_2, on2 ? meangreen : BLACK);
}
drawAll(highlight);
