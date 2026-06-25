import subprocess
from pathlib import Path
from types import SimpleNamespace

from bake.asy_compile import AsyConfig, compile


def _fake_run_factory(recorded, returncode, expected_file, create_output,
                      stderr="", stdout=""):
    """Build a fake subprocess.run that records args and optionally writes
    the expected output file."""

    def fake_run(args, capture_output, text, timeout):
        recorded["args"] = args
        recorded["capture_output"] = capture_output
        recorded["text"] = text
        recorded["timeout"] = timeout
        if create_output:
            expected_file.write_bytes(b"fake-output")
        return SimpleNamespace(
            returncode=returncode, stderr=stderr, stdout=stdout
        )

    return fake_run


def test_params_sorted_and_flags_present(monkeypatch, tmp_path):
    src = tmp_path / "drawing.asy"
    src.write_text("// asy source")
    out_stem = tmp_path / "drawing"
    expected = out_stem.with_suffix(".png")

    params = {"b": "2", "a": "1"}
    cfg = AsyConfig(asy_binary="fake_asy", out_format="png", dpi=220)

    recorded = {}
    monkeypatch.setattr(
        subprocess,
        "run",
        _fake_run_factory(
            recorded, returncode=0, expected_file=expected, create_output=True
        ),
    )

    result = compile(src, out_stem, params, cfg)
    args = recorded["args"]

    # Sorted params: a=1 before b=2.
    idx_a = args.index("a=1")
    idx_b = args.index("b=2")
    assert idx_a < idx_b
    assert args[idx_a - 1] == "-u"
    assert args[idx_b - 1] == "-u"

    # Core flags present.
    assert "-f" in args
    assert "png" in args
    assert "-render" in args
    assert "-o" in args

    # render factor = ceil(220 / 72) = 4
    assert args[args.index("-render") + 1] == "4"

    assert result.ok is True
    assert expected in result.outputs


def test_nonzero_exit_means_not_ok(monkeypatch, tmp_path):
    src = tmp_path / "drawing.asy"
    src.write_text("// asy source")
    out_stem = tmp_path / "drawing"
    expected = out_stem.with_suffix(".png")

    cfg = AsyConfig(asy_binary="fake_asy", out_format="png", dpi=220)
    err = "Asymptote error: something went wrong"

    recorded = {}
    monkeypatch.setattr(
        subprocess,
        "run",
        _fake_run_factory(
            recorded,
            returncode=1,
            expected_file=expected,
            create_output=False,
            stderr=err,
        ),
    )

    result = compile(src, out_stem, {}, cfg)

    assert result.ok is False
    assert result.stderr == err
    assert result.outputs == []


def test_zero_exit_with_output_means_ok(monkeypatch, tmp_path):
    src = tmp_path / "drawing.asy"
    src.write_text("// asy source")
    out_stem = tmp_path / "drawing"
    expected = out_stem.with_suffix(".png")

    cfg = AsyConfig(asy_binary="fake_asy", out_format="png", dpi=220)

    recorded = {}
    monkeypatch.setattr(
        subprocess,
        "run",
        _fake_run_factory(
            recorded, returncode=0, expected_file=expected, create_output=True
        ),
    )

    result = compile(src, out_stem, {}, cfg)

    assert result.ok is True
    assert result.outputs == [expected]


def test_zero_exit_without_output_means_not_ok(monkeypatch, tmp_path):
    src = tmp_path / "drawing.asy"
    src.write_text("// asy source")
    out_stem = tmp_path / "drawing"
    expected = out_stem.with_suffix(".png")

    cfg = AsyConfig(asy_binary="fake_asy", out_format="png", dpi=220)

    recorded = {}
    monkeypatch.setattr(
        subprocess,
        "run",
        _fake_run_factory(
            recorded, returncode=0, expected_file=expected, create_output=False
        ),
    )

    result = compile(src, out_stem, {}, cfg)

    assert result.ok is False
    assert result.outputs == []
    assert not expected.exists()
