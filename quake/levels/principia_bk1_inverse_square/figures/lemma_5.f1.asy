// figure.lemma_5.f1.asy -- In similar figures all homologous sides are proportional, and the areas are in the duplicate ratio of the homologous sides.
// Self-contained convention. Compile: asy -u "highlight=k" figure.lemma_5.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen simblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen simgreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen sideorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_1_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair A = (0.0,0.0);
pair B = (4.0,0.0);
pair C = (1.2,3.0);
path fig1 = A--B--C--cycle;
pair D = (6.0,0.0);
pair _u_E = (8.0,0.0);
pair F = (6.6,1.5);
path fig2 = D--E--F--cycle;
pair A = (0.0,0.0);
pair B = (4.0,0.0);
pair C = (1.2,3.0);
path fig1 = A--B--C--cycle;
pair D = (6.0,0.0);
pair _u_E = (8.0,0.0);
pair F = (6.6,1.5);
path fig2 = D--E--F--cycle;
path sideAB = A--B;
path sideDE = D--E;

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);

  // STABILO underlay (current step's heart only)
  if (on1) draw(fig1, STABILO_1_1);
  if (on1) draw(fig2, STABILO_1_2);
  if (on2) draw(sideAB, STABILO_2_1);
  if (on2) draw(sideDE, STABILO_2_2);

  // ink pass
  dot(A, on2 ? simblue : BLACK);
  dot(B, on2 ? simblue : BLACK);
  draw(fig1, on2 ? simblue : BLACK);
  dot(D, on2 ? simgreen : BLACK);
  dot(_u_E, on2 ? simgreen : BLACK);
  draw(fig2, on2 ? simgreen : BLACK);
  draw(sideAB, on2 ? sideorange : BLACK);
  draw(sideDE, on2 ? sideorange : BLACK);
  dot(A, on1 ? simblue : BLACK);
  dot(B, on1 ? simblue : BLACK);
  dot(C, on1 ? simblue : BLACK);
  draw(fig1, on1 ? simblue : BLACK);
  dot(D, on1 ? simgreen : BLACK);
  dot(_u_E, on1 ? simgreen : BLACK);
  dot(F, on1 ? simgreen : BLACK);
  draw(fig2, on1 ? simgreen : BLACK);
  label("$A$", A, SW);
  label("$B$", B, SE);
  label("$C$", C, N);
  label("$D$", D, SW);
  label("$E$", _u_E, SE);
  label("$F$", F, N);
  label("$A$", A, SW);
  label("$B$", B, SE);
  label("$C$", C, N);
  label("$D$", D, SW);
  label("$E$", _u_E, SE);
  label("$F$", F, N);
}
drawAll(highlight);
