# Principia Descent

An open-source, two-player educational FPS that teaches Newton's *Principia*
(and other math books) by turning proofs into a walkable art-gallery dungeon.

- **Run the demo today:** `python m0_demo.py`
- **Run tests:** `pytest -q`
- License: code = MIT, content = CC-BY-SA 4.0

## How the code is organised
The runtime never needs to understand the math. It only loads pre-baked PNGs
+ JSON. Three worlds, kept separate:
1. CONTENT (book text/proofs)  -> authored by LLM "content children"
2. BUILD/OFFLINE (tools/)       -> bakes LaTeX/TikZ to PNG, lays out the graph
3. RUNTIME (principia/)         -> the game, loads baked assets only

Every module talks to others ONLY through the typed signatures in each file
and the pydantic data contracts in `principia/schema.py`. Do not import another
module's internals.

## Build order (each independently testable)
schema -> assets/manager -> content/loader -> layout/graph -> world/builder
-> world/rooms -> nav/navigator -> control/input -> player/mover
-> player/shooter -> walls/state -> enemy/demon -> ceiling/equations
-> doors/secret -> ui/* -> app
