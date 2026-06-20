Handoff note for DeepSeek (paste alongside the three files)

DEEPSEEK — STEP 1 HANDOFF (supersedes everything previous for step 1)
Claude wrote palette.py / corridor.py / main.py. Do NOT redesign.
Your tasks, in priority order:
 1. requirements.txt (pygame, PyOpenGL, numpy) + README.md with run
    instructions for Nir (python main.py, key list).
 2. draw_overlay_text() in main.py — full recipe in its docstring.
 3. F3 wireframe toggle — two lines, hint at the TODO site in main.py.
 4. Run it; confirm 60 FPS and the acceptance list from the spec.
 5. AFTER Nir's test flight only: tune SEGMENTS values he complains
    about (lengths, pitches). Never change palette.py without Nir.
 6. Optional, last: diagonal chevron stripes (see _striped_frame).
