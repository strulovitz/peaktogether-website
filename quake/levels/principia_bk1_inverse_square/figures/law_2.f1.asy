// figure.law_2.f1.asy -- The alteration of motion is proportional to, and directed along, the impressed force.
// Self-contained convention. Compile: asy -u "highlight=k" figure.law_2.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen motionblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen forceorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen dirgreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(187/255, 215/255, 251/255) + opacity(0.45) + linewidth(9pt) + squarecap;
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
  label("$\\,\\Delta(\\text{motion})\\;\\propto\\;\\mathbf{F}\\,$", _layoutpos_1, on1 ? motionblue : BLACK);
  label("$\\,\\Delta(\\text{motion})\\;\\parallel\\;\\mathbf{F}\\,$", _layoutpos_2, on2 ? dirgreen : BLACK);
}
drawAll(highlight);
