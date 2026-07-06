"""FIT-THE-BEAT rule tests (the ghost-pedal fix, July 2026)."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "player"))

from m1_demo import choose_uniform_token, TOKEN_SECONDS   # noqa: E402


def test_cello_case_no_longer_haunts():
    # 90 BPM, 1-beat notes = 0.667s; cello offers everything.
    common = {"025", "05", "1", "15"}
    assert choose_uniform_token(common, 60.0 / 90.0) == "05"


def test_violin_case_unchanged():
    # violin forte/arco-normal only ships 025 + 05 -> still 05.
    assert choose_uniform_token({"025", "05"}, 60.0 / 90.0) == "05"


def test_slow_tempo_earns_longer_samples():
    # at 40 BPM a beat is 1.5s: the full 15 token now fits and wins.
    common = {"025", "05", "1", "15"}
    assert choose_uniform_token(common, 60.0 / 40.0) == "15"


def test_nothing_fits_takes_shortest():
    # tiny notes (0.2s) but only long samples exist -> least overlap.
    assert choose_uniform_token({"1", "15"}, 0.2) == "1"


def test_exact_fit_is_allowed():
    assert choose_uniform_token({"025", "05", "1"}, 0.5) == "05"


def test_all_tokens_have_seconds():
    assert set(TOKEN_SECONDS) == {"025", "05", "1", "15"}
