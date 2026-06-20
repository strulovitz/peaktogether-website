"""palette.py -- single source of truth for every color in Descent QED.
GREYSCALE WORLD RULE (Bible v3.5): the WORLD is grey; COLOR is meaning."""

BG          = (0.01, 0.01, 0.02)   # near-black mine darkness
WALL_FILL   = (0.13, 0.13, 0.15)   # dark grey rock
WALL_EDGE   = (0.78, 0.78, 0.82)   # automap-style white-grey wireframe
CHEVRON_A   = (0.95, 0.80, 0.10)   # hazard yellow (meaning: robot station)
CHEVRON_B   = (0.05, 0.05, 0.06)   # hazard near-black

WALL_ALPHA_DEFAULT = 0.45          # Nir's half-transparency; [ ] keys adjust
WALL_ALPHA_STEP    = 0.05
WALL_ALPHA_MIN     = 0.0           # pure automap wireframe
WALL_ALPHA_MAX     = 0.9           # near-solid rock

DARKNESS_START = 40.0              # distance darkness (NOT fog -- no weather
DARKNESS_END   = 140.0             # in a mine; geometry fades to BG black)
