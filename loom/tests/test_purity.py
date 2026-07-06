"""core/ must never import pygame (New Testament par.II.9)."""
import sys


def test_core_is_pygame_free():
    import core.spell_model    # noqa: F401
    import core.tuning         # noqa: F401
    import core.conductor      # noqa: F401
    import core.audio          # noqa: F401
    assert "pygame" not in sys.modules
