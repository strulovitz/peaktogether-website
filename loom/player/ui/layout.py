"""
layout.py — every fixed rectangle of the 1280x720 window. [M2 — Parent 3]

Scripture: BIBLE par.2 — window LOCKED at 1280x720; positions never
move (muscle memory is an accessibility feature). Top half = Scene
Stage (story image OR graph + helix + equation); bottom half = Music
Bench (keyboard, staff, OK/Cancel, transport).

STATUS: numbers below are STILL PROVISIONAL until Nir's eye-tuning
pass on the running m2_demo (screenshots back and forth). When Nir
says "freeze", DeepSeek flips this line to FROZEN and the numbers
become law. No widget invents its own geometry — every rect comes
from here, passed into widget constructors by the wiring. Widgets
never import this module themselves (testability).
"""

import pygame

WINDOW = pygame.Rect(0, 0, 1280, 720)

# --- top half: the Scene Stage ---
SCENE_STAGE = pygame.Rect(0, 0, 1280, 400)       # story image + caption
GRAPH = pygame.Rect(40, 30, 620, 330)            # puzzle mode: the graph
HELIX = pygame.Rect(700, 30, 280, 330)           # puzzle mode: the pitch helix
EQUATION = pygame.Rect(1000, 30, 240, 120)       # LaTeX-baked PNG
CAPTION = pygame.Rect(40, 360, 1200, 36)

# --- bottom half: the Music Bench ---
BENCH = pygame.Rect(0, 400, 1280, 320)
KEYBOARD = pygame.Rect(60, 430, 700, 170)        # 1 octave default, 2 max
STAFF = pygame.Rect(790, 430, 430, 170)          # noteheads only
OK_BUTTON = pygame.Rect(790, 615, 90, 40)
CANCEL_BUTTON = pygame.Rect(895, 615, 90, 40)
TRANSPORT = pygame.Rect(60, 620, 700, 60)        # play/pause/stop + timeline
