"""
layout.py — every fixed rectangle of the 1280x720 window. [M2 — Parent 3]

Scripture: BIBLE par.2 — window LOCKED at 1280x720; positions never
move. Top half = Scene Stage; bottom half = Music Bench.

REVISED per Nir's eye feedback (July 2026): keyboard + staff span
almost the full width; staff sits directly above the piano and is a
FULL GRAND STAFF always (Nir's amendment); transport + OK/Cancel share
the bottom strip. HELIX keeps its reserved home for M4.

STATUS: FROZEN by Nir (2026-07-06) after his eye pass on m2_demo — he
approved the layout as-is; these numbers are now permanent (do not move
the keyboard/staff/etc). Every widget takes its rect from here via the
wiring; widgets never import this module (testability).
"""

import pygame

WINDOW = pygame.Rect(0, 0, 1280, 720)

# --- top half: the Scene Stage ---
SCENE_STAGE = pygame.Rect(0, 0, 1280, 400)       # story image + caption
GRAPH = pygame.Rect(30, 14, 640, 356)            # puzzle mode: the graph
HELIX = pygame.Rect(700, 14, 310, 356)           # reserved: M4 pitch helix
EQUATION = pygame.Rect(1030, 14, 230, 140)       # LaTeX-baked PNG
CAPTION = pygame.Rect(40, 374, 1200, 24)         # story mode text strip

# --- bottom half: the Music Bench ---
BENCH = pygame.Rect(0, 400, 1280, 320)
STAFF = pygame.Rect(20, 404, 1240, 150)          # full grand staff, full width
KEYBOARD = pygame.Rect(20, 562, 1240, 118)       # 1 octave default, 2 max
TRANSPORT = pygame.Rect(20, 686, 950, 30)        # play/pause/stop + timeline
OK_BUTTON = pygame.Rect(1000, 684, 120, 34)
CANCEL_BUTTON = pygame.Rect(1140, 684, 120, 34)
