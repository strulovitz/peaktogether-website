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
pair _termpos_1_1 = (-1.20, 0.00);
pair _termpos_1_2 = (1.20, 0.00);
pair _termpos_2_1 = (-2.40, -2.20);
pair _termpos_2_2 = (0.00, -2.20);
pair _termpos_2_3 = (2.40, -2.20);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);

  // STABILO underlay (current step's heart only)
  if (on1) label("$\\Delta(\\text{motion})$", _termpos_1_1, STABILO_1_1);
  if (on2) label("$\\parallel\\;\\text{(right line of }\\mathbf{F}\\text{)}$", _termpos_2_3, STABILO_2_1);

  // ink pass
  label("$\\Delta(\\text{motion})$", _termpos_1_1, on1 ? motionblue : BLACK);
  label("$\\mathbf{F}$", _termpos_1_2, on1 ? forceorange : BLACK);
  label("$\\Delta(\\text{motion})$", _termpos_2_1, on2 ? motionblue : BLACK);
  label("$\\mathbf{F}$", _termpos_2_2, on2 ? forceorange : BLACK);
  label("$\\parallel\\;\\text{(right line of }\\mathbf{F}\\text{)}$", _termpos_2_3, on2 ? dirgreen : BLACK);
}
drawAll(highlight);
