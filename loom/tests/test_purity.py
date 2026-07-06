"""core/ must never import pygame (New Testament par.II.9).

Checked in a CLEAN subprocess: sibling M2 test files (test_m2_widgets,
test_input_mapper) import pygame at module load, which pollutes this
process's sys.modules. The only honest way to prove core/ is pygame-free
is to import it fresh, alone, and inspect that child's sys.modules.
"""
import os
import subprocess
import sys


def test_core_is_pygame_free():
    player = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "player")
    code = (
        "import sys\n"
        "sys.path.insert(0, r'" + player + "')\n"
        "import core.spell_model, core.tuning, core.conductor, "
        "core.audio, core.notation, core.echo_logic\n"
        "assert 'pygame' not in sys.modules, 'core/ pulled in pygame!'\n"
    )
    result = subprocess.run([sys.executable, "-c", code],
                            capture_output=True, text=True)
    assert result.returncode == 0, (result.stdout + result.stderr)
