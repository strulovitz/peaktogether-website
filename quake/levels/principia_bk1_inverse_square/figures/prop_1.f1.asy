// figure.prop_1.f1.asy -- The areas which revolving bodies describe by radii drawn to an immoveable centre of force are proportional to the times in which they are described.
// Self-contained convention. Compile: asy -u "highlight=k" figure.prop_1.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.

import geometry;
import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen centerorange = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen pathblue = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen radigreen = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen arearpurple = rgb(142/255, 36/255, 170/255) + linewidth(1.6pt);
pen impulsered = rgb(216/255, 27/255, 96/255) + linewidth(1.6pt);

// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----
pen STABILO_1_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_3 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_4 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_5 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_2_6 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_3_3 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_4_1 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;
pen STABILO_4_2 = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
pair _u_S = (0.5,4.8);
pair A = (1.0,0.4);
pair B = (3.2,0.9);
pair C = (5.0,2.2);
pair D = (5.8,4.0);
pair _u_E = (5.4,5.8);
pair F = (4.2,7.0);
path _u_path = A--B--C--D--_u_E--F;
path SA = _u_S--A;
path SB = _u_S--B;
path SC = _u_S--C;
path SD = _u_S--D;
path _u_SE = _u_S--_u_E;
path SF = _u_S--F;
pair c = (5.4,1.4);
path Bc = B--c;
path cC = c--C;
path SAB = _u_S--A--B--cycle;
path SBc = _u_S--B--c--cycle;
path SBC = _u_S--B--C--cycle;
path imp = c--(shift(10*unit(C-c))*c);

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  bool on1 = (highlight==1);
  bool on2 = (highlight==2);
  bool on3 = (highlight==3);
  bool on4 = (highlight==4);

  // STABILO underlay (current step's heart only)
  if (on1) draw(_u_path, STABILO_1_1);
  if (on2) draw(SA, STABILO_2_1);
  if (on2) draw(SB, STABILO_2_2);
  if (on2) draw(SC, STABILO_2_3);
  if (on2) draw(SD, STABILO_2_4);
  if (on2) draw(_u_SE, STABILO_2_5);
  if (on2) draw(SF, STABILO_2_6);
  if (on3) draw(SAB, STABILO_3_1);
  if (on3) draw(SBc, STABILO_3_2);
  if (on3) draw(SBC, STABILO_3_3);
  if (on4) draw(_u_path, STABILO_4_1);
  if (on4) draw(imp, STABILO_4_2);

  // ink pass
  dot(_u_S, on4 ? centerorange : BLACK);
  dot(A, on4 ? BLACK : BLACK);
  dot(B, on4 ? BLACK : BLACK);
  dot(C, on4 ? BLACK : BLACK);
  dot(D, on4 ? BLACK : BLACK);
  dot(_u_E, on4 ? BLACK : BLACK);
  dot(F, on4 ? BLACK : BLACK);
  dot(c, on4 ? BLACK : BLACK);
  draw(_u_path, on4 ? pathblue : BLACK);
  draw(Bc, on4 ? pathblue : BLACK);
  draw(SB, on4 ? radigreen : BLACK);
  draw(imp, on4 ? impulsered : BLACK);
  dot(_u_S, on3 ? centerorange : BLACK);
  dot(A, on3 ? BLACK : BLACK);
  dot(B, on3 ? BLACK : BLACK);
  dot(C, on3 ? BLACK : BLACK);
  dot(c, on3 ? BLACK : BLACK);
  draw(Bc, on3 ? arearpurple : BLACK);
  draw(cC, on3 ? arearpurple : BLACK);
  draw(SB, on3 ? radigreen : BLACK);
  draw(SAB, on3 ? arearpurple : BLACK);
  draw(SBc, on3 ? arearpurple : BLACK);
  draw(SBC, on3 ? arearpurple : BLACK);
  dot(_u_S, on2 ? centerorange : BLACK);
  dot(A, on2 ? BLACK : BLACK);
  dot(B, on2 ? BLACK : BLACK);
  dot(C, on2 ? BLACK : BLACK);
  dot(D, on2 ? BLACK : BLACK);
  dot(_u_E, on2 ? BLACK : BLACK);
  dot(F, on2 ? BLACK : BLACK);
  draw(_u_path, on2 ? pathblue : BLACK);
  draw(SA, on2 ? radigreen : BLACK);
  draw(SB, on2 ? radigreen : BLACK);
  draw(SC, on2 ? radigreen : BLACK);
  draw(SD, on2 ? radigreen : BLACK);
  draw(_u_SE, on2 ? radigreen : BLACK);
  draw(SF, on2 ? radigreen : BLACK);
  dot(_u_S, on1 ? centerorange : BLACK);
  dot(A, on1 ? BLACK : BLACK);
  dot(B, on1 ? BLACK : BLACK);
  dot(C, on1 ? BLACK : BLACK);
  dot(D, on1 ? BLACK : BLACK);
  dot(_u_E, on1 ? BLACK : BLACK);
  dot(F, on1 ? BLACK : BLACK);
  draw(_u_path, on1 ? pathblue : BLACK);
  label("$S$", _u_S, NW);
  label("$A$", A, SW);
  label("$B$", B, S);
  label("$C$", C, SE);
  label("$D$", D, E);
  label("$E$", _u_E, NE);
  label("$F$", F, N);
  pair _lbl__u_path = point(_u_path, 0.5);
  label("$ABCDEF$", _lbl__u_path, SE);
  label("$S$", _u_S, NW);
  label("$A$", A, SW);
  label("$B$", B, S);
  label("$C$", C, SE);
  label("$D$", D, E);
  label("$E$", _u_E, NE);
  label("$F$", F, N);
  pair _lbl__u_path = point(_u_path, 0.5);
  label("$ABCDEF$", _lbl__u_path, SE);
  pair _lbl_SA = point(SA, 0.5);
  label("$SA$", _lbl_SA, W);
  pair _lbl_SB = point(SB, 0.5);
  label("$SB$", _lbl_SB, S);
  pair _lbl_SC = point(SC, 0.5);
  label("$SC$", _lbl_SC, E);
  pair _lbl_SD = point(SD, 0.5);
  label("$SD$", _lbl_SD, E);
  pair _lbl__u_SE = point(_u_SE, 0.5);
  label("$SE$", _lbl__u_SE, E);
  pair _lbl_SF = point(SF, 0.5);
  label("$SF$", _lbl_SF, E);
  label("$S$", _u_S, NW);
  label("$A$", A, SW);
  label("$B$", B, S);
  label("$C$", C, SE);
  label("$c$", c, SE);
  pair _lbl_Bc = point(Bc, 0.5);
  label("$Bc$", _lbl_Bc, S);
  pair _lbl_cC = point(cC, 0.5);
  label("$Cc$", _lbl_cC, E);
  pair _lbl_SB = point(SB, 0.5);
  label("$SB$", _lbl_SB, W);
  pair _lbl_SAB = point(SAB, 0.5);
  label("$SAB$", _lbl_SAB, W);
  pair _lbl_SBc = point(SBc, 0.5);
  label("$SBc$", _lbl_SBc, SE);
  pair _lbl_SBC = point(SBC, 0.5);
  label("$SBC$", _lbl_SBC, E);
  label("$S$", _u_S, NW);
  label("$A$", A, SW);
  label("$B$", B, S);
  label("$C$", C, SE);
  label("$D$", D, E);
  label("$E$", _u_E, NE);
  label("$F$", F, N);
  label("$c$", c, SE);
  pair _lbl__u_path = point(_u_path, 0.5);
  label("$ABCDEF$", _lbl__u_path, NW);
  pair _lbl_Bc = point(Bc, 0.5);
  label("$Bc$", _lbl_Bc, S);
  pair _lbl_SB = point(SB, 0.5);
  label("$SB$", _lbl_SB, W);
  pair _lbl_imp = point(imp, 0.5);
  label("$Cc \\parallel SB$", _lbl_imp, SE);
}
drawAll(highlight);
