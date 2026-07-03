// figure.lemma_12.f1.asy -- All parallelograms described about conjugate diameters of a given ellipse or hyperbola are equal to one another.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_12.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen ellblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen conjorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen pargreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_1_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair O = (0.0,0.0);
pair maj = (4.0,0.0);
pair min = (0.0,2.4);
ellipse ell = ellipse(O, maj, min);
pair P = (3.4,1.27);
pair Q = (-3.4,-1.27);
pair R = (-1.5,2.22);
pair _u_S = (1.5,-2.22);
path diamPQ = P--Q;
path diamRS = R--_u_S;
pair V1 = (5.5,3.4);
pair V2 = (2.5,-1.8);
pair V3 = (-5.5,-3.4);
pair V4 = (-2.5,1.8);
path box = V1--V2--V3--V4--cycle;

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);

  // STABILO underlay (current step's heart only)
  if (on1) draw(ell, STABILO_1_1);
  if (on1) draw(box, STABILO_1_2);

  // ink pass
  dot(O, on1 ? BLACK : BLACK);
  dot(maj, on1 ? BLACK : BLACK);
  dot(min, on1 ? BLACK : BLACK);
  draw(ell, on1 ? ellblue : BLACK);
  dot(P, on1 ? conjorange : BLACK);
  dot(Q, on1 ? conjorange : BLACK);
  dot(R, on1 ? conjorange : BLACK);
  dot(_u_S, on1 ? conjorange : BLACK);
  draw(diamPQ, on1 ? conjorange : BLACK);
  draw(diamRS, on1 ? conjorange : BLACK);
  dot(V1, on1 ? BLACK : BLACK);
  dot(V2, on1 ? BLACK : BLACK);
  dot(V3, on1 ? BLACK : BLACK);
  dot(V4, on1 ? BLACK : BLACK);
  draw(box, on1 ? pargreen : BLACK);
  label("$O$", O, Center);
  label("$P$", P, NE);
  label("$Q$", Q, SW);
  label("$R$", R, NW);
  label("$S$", _u_S, SE);
  label("$$", V1, NE);
  label("$$", V2, SE);
  label("$$", V3, SW);
  label("$$", V4, NW);
}
drawAll(highlight);
