"""
LOOM2 -- core/scene.py
Scene loading & validation. Allowed imports: json, os, config, core.types,
core.surfaces. Child chat scope: implement all bodies. ~130 lines expected.

------------------------------------------------------------------------------
IMPLEMENTATION NOTES (Parent G, 2026-07-08)

THE DOOR POLICY (Nir's ruling, 2026-07-08: STRICT -- option (a)):
  * ALL 13 SceneSpec fields are REQUIRED in scene.json. A missing field means
    the content author made a mistake; we say so immediately, at load.
  * The ONE lenient spot, per G3.2-A + DeepSeek Q5: camera_limits KEYS may be
    omitted -- missing keys are filled with the canonical G3.2-A defaults
    (target [0,0,0], zoom_min 0.5, zoom_max 2.5, distance 14.0). Wrong TYPES
    or bad RANGES (zoom_min >= zoom_max, non-numeric...) still fail loud.
  * UNKNOWN keys fail loud too -- at the top level, inside options, and
    inside camera_limits. Rationale: a typo like "totem_stat" or "corect"
    would otherwise silently become a missing/defaulted value. The ONLY
    tolerated extras are amendment G2.5-A's optional per-OPTION design-time
    keys: "domain", "step", "z_per_octave" (used by the offline WAV renderer;
    accepted here, validated lightly, NOT stored -- QuizOption has no fields
    for them and the game never reads them).

ERROR PHILOSOPHY -- every error message carries four things:
  (1) WHICH scene, (2) WHICH key, (3) WHAT was wrong, (4) what would be RIGHT.
  A content author fixing a scene at midnight should never need this file's
  source to understand its complaints. All failures raise SceneError
  (an additive subclass of ValueError -- catchable specifically, and any
  existing `except ValueError` still works).

PATHS (verified by DeepSeek, Q4): wav_path and equation_png are RELATIVE TO
THE REPO ROOT (cwd), e.g. "data/scenes/test_saddle/option_a.wav" -- opened
as-is, never re-anchored to the scene folder. config.SCENES_DIR is likewise
repo-root-relative. JSON files are read as UTF-8 explicitly: title lines and
explanations carry emoji, and they must survive every platform's default
encoding. 🐎

GROUND TRUTH: data/scenes/test_saddle/scene.json (live, pasted verbatim by
DeepSeek 2026-07-08) supplies all 13 fields and is the schema this loader
was written against. The self-test at the bottom loads the real campaign.
------------------------------------------------------------------------------
"""

import json
import os

import config
from core import surfaces
from core.types import SceneSpec, QuizOption


# =============================================================================
# CONSTANTS OF THE DOOR
# =============================================================================

# Canonical camera_limits keys and defaults -- amendment G3.2-A, verbatim.
# (OrbitCamera happens to carry the same fallbacks internally, camera.py:92-97,
# but scene.py fills them HERE so every SceneSpec that leaves this module is
# complete and self-describing -- no downstream guessing.)
_CAMERA_DEFAULTS = {
    "target":   [0.0, 0.0, 0.0],
    "zoom_min": 0.5,
    "zoom_max": 2.5,
    "distance": 14.0,
}

# The 13 required top-level keys == the 13 fields of the frozen SceneSpec
# dataclass (core/types.py:45-51; it has NO defaults, so neither do we).
_TOP_LEVEL_KEYS = frozenset({
    "scene_id", "title_lines", "surface_name", "equation_png", "totem_start",
    "domain", "mesh_step", "z_per_octave", "question", "hint_lines",
    "options", "camera_limits", "success_text",
})

_OPTION_REQUIRED_KEYS = frozenset({"label", "wav_path", "correct", "explain"})
_OPTION_OPTIONAL_KEYS = frozenset({"domain", "step", "z_per_octave"})  # G2.5-A

_OPTION_COUNT = 4          # exactly, per the frozen contract
_LINES_MIN, _LINES_MAX = 1, 3   # title_lines AND hint_lines, per the contract

# Sanity ceiling on the terrain grid implied by domain/mesh_step. A typo like
# "mesh_step": 0.0001 would ask TerrainMesh for billions of vertices and
# freeze the machine AT LOAD with no explanation -- this turns that into a
# one-line error instead. 2M vertices is ~60x the test_saddle grid (33x33):
# far beyond any sane scene, far below any freeze.
_MAX_GRID_VERTS = 2_000_000


class SceneError(ValueError):
    """Any invalid scene content or campaign file. Subclasses ValueError so
    generic handlers keep working; exists so callers CAN catch scene problems
    specifically. Raised only at load time -- never mid-game (the contract)."""


# =============================================================================
# SMALL VALIDATION HELPERS (module-private)
# =============================================================================

def _fail(ctx: str, msg: str):
    """Single exit for every complaint -- uniform '<where>: <what>' format."""
    raise SceneError(f"{ctx}: {msg}")


def _is_num(v) -> bool:
    """True for int/float but NOT bool (bool subclasses int in Python --
    without this guard, "mesh_step": true would validate as a number!)."""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _read_json(path: str, ctx: str):
    """Open + parse a JSON file with loud, specific errors. UTF-8 always."""
    if not os.path.isfile(path):
        _fail(ctx, f"file not found: '{path}' (paths are relative to the repo "
                   f"root; is the working directory the repo root?)")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as e:
        _fail(ctx, f"'{path}' is not valid JSON: {e.msg} "
                   f"(line {e.lineno}, column {e.colno})")


def _need_str(ctx: str, key: str, v, allow_empty: bool = False) -> str:
    if not isinstance(v, str):
        _fail(ctx, f"'{key}' must be a string, got {type(v).__name__}")
    if not allow_empty and not v.strip():
        _fail(ctx, f"'{key}' must be a non-empty string")
    return v


def _need_num(ctx: str, key: str, v) -> float:
    if not _is_num(v):
        _fail(ctx, f"'{key}' must be a number, got {type(v).__name__}")
    return float(v)


def _need_lines(ctx: str, key: str, v) -> list:
    """A list of 1-3 non-empty strings (title_lines / hint_lines contract)."""
    if not isinstance(v, list):
        _fail(ctx, f"'{key}' must be a list of strings, got {type(v).__name__}")
    if not (_LINES_MIN <= len(v) <= _LINES_MAX):
        _fail(ctx, f"'{key}' must have {_LINES_MIN}-{_LINES_MAX} lines, "
                   f"got {len(v)}")
    for i, line in enumerate(v):
        if not isinstance(line, str) or not line.strip():
            _fail(ctx, f"'{key}[{i}]' must be a non-empty string")
    return list(v)


def _need_file(ctx: str, key: str, path: str) -> str:
    """The file must exist AND be non-empty (a 0-byte WAV or PNG is a broken
    export -- catching it here beats a silent black image or dead speaker)."""
    if not os.path.isfile(path):
        _fail(ctx, f"'{key}' file not found: '{path}' (repo-root-relative)")
    if os.path.getsize(path) == 0:
        _fail(ctx, f"'{key}' file is empty (0 bytes): '{path}'")
    return path


# =============================================================================
# FIELD VALIDATORS (module-private, one per structured field)
# =============================================================================

def _validate_domain(ctx: str, raw) -> tuple:
    if not isinstance(raw, list) or len(raw) != 4 or not all(_is_num(v) for v in raw):
        _fail(ctx, "'domain' must be a list of 4 numbers [xmin, xmax, ymin, ymax]")
    xmin, xmax, ymin, ymax = (float(v) for v in raw)
    if xmin >= xmax:
        _fail(ctx, f"'domain' needs xmin < xmax, got xmin={xmin}, xmax={xmax}")
    if ymin >= ymax:
        _fail(ctx, f"'domain' needs ymin < ymax, got ymin={ymin}, ymax={ymax}")
    return (xmin, xmax, ymin, ymax)


def _validate_mesh_step(ctx: str, raw, domain: tuple) -> float:
    step = _need_num(ctx, "mesh_step", raw)
    xmin, xmax, ymin, ymax = domain
    if step <= 0.0:
        _fail(ctx, f"'mesh_step' must be > 0, got {step}")
    if step > min(xmax - xmin, ymax - ymin):
        _fail(ctx, f"'mesh_step' ({step}) is larger than the domain itself -- "
                   f"the mesh would have no interior")
    nx = int((xmax - xmin) / step) + 1
    ny = int((ymax - ymin) / step) + 1
    if nx * ny > _MAX_GRID_VERTS:
        _fail(ctx, f"'mesh_step' {step} over this domain implies a {nx}x{ny} "
                   f"grid (~{nx * ny:,} vertices) -- above the sanity ceiling "
                   f"of {_MAX_GRID_VERTS:,}. Almost certainly a typo.")
    return step


def _validate_totem_start(ctx: str, raw, domain: tuple) -> tuple:
    if not isinstance(raw, list) or len(raw) != 2 or not all(_is_num(v) for v in raw):
        _fail(ctx, "'totem_start' must be a list of 2 numbers [x, y]")
    x, y = float(raw[0]), float(raw[1])
    xmin, xmax, ymin, ymax = domain
    if not (xmin <= x <= xmax and ymin <= y <= ymax):  # inclusive: edge is legal
        _fail(ctx, f"'totem_start' ({x}, {y}) is outside the domain "
                   f"x:[{xmin}, {xmax}], y:[{ymin}, {ymax}]")
    return (x, y)


def _validate_camera_limits(ctx: str, raw) -> dict:
    """G3.2-A: fill missing keys with canonical defaults; fail loud on wrong
    type, bad range, or unknown keys (DeepSeek Q5: 'option (b)' semantics)."""
    if not isinstance(raw, dict):
        _fail(ctx, f"'camera_limits' must be an object, got {type(raw).__name__}")
    unknown = set(raw) - set(_CAMERA_DEFAULTS)
    if unknown:
        _fail(ctx, f"'camera_limits' has unknown key(s) {sorted(unknown)}; "
                   f"valid keys are {sorted(_CAMERA_DEFAULTS)}")
    limits = {}
    tgt = raw.get("target", _CAMERA_DEFAULTS["target"])
    if not isinstance(tgt, list) or len(tgt) != 3 or not all(_is_num(v) for v in tgt):
        _fail(ctx, "'camera_limits.target' must be a list of 3 numbers")
    limits["target"] = [float(v) for v in tgt]
    for key in ("zoom_min", "zoom_max", "distance"):
        limits[key] = _need_num(ctx, f"camera_limits.{key}",
                                raw.get(key, _CAMERA_DEFAULTS[key]))
    if limits["zoom_min"] <= 0.0:
        _fail(ctx, f"'camera_limits.zoom_min' must be > 0, got {limits['zoom_min']}")
    if limits["zoom_min"] >= limits["zoom_max"]:
        _fail(ctx, f"'camera_limits' needs zoom_min < zoom_max, got "
                   f"{limits['zoom_min']} >= {limits['zoom_max']}")
    if limits["distance"] <= 0.0:
        _fail(ctx, f"'camera_limits.distance' must be > 0, got {limits['distance']}")
    return limits


def _validate_options(ctx: str, raw) -> list:
    """Exactly 4 options, exactly one correct, every WAV real. -> [QuizOption]"""
    if not isinstance(raw, list):
        _fail(ctx, f"'options' must be a list, got {type(raw).__name__}")
    if len(raw) != _OPTION_COUNT:
        _fail(ctx, f"'options' must have exactly {_OPTION_COUNT} entries, "
                   f"got {len(raw)}")
    options, labels = [], set()
    for i, entry in enumerate(raw):
        octx = f"{ctx}, options[{i}]"
        if not isinstance(entry, dict):
            _fail(octx, f"must be an object, got {type(entry).__name__}")
        missing = _OPTION_REQUIRED_KEYS - entry.keys()
        if missing:
            _fail(octx, f"missing required key(s): {sorted(missing)}")
        unknown = entry.keys() - _OPTION_REQUIRED_KEYS - _OPTION_OPTIONAL_KEYS
        if unknown:
            _fail(octx, f"unknown key(s) {sorted(unknown)}; required: "
                        f"{sorted(_OPTION_REQUIRED_KEYS)}, optional (G2.5-A): "
                        f"{sorted(_OPTION_OPTIONAL_KEYS)}")
        label = _need_str(octx, "label", entry["label"])
        if label in labels:
            _fail(octx, f"duplicate label '{label}' -- labels must be unique")
        labels.add(label)
        wav = _need_str(octx, "wav_path", entry["wav_path"])
        _need_file(octx, "wav_path", wav)
        if not isinstance(entry["correct"], bool):
            _fail(octx, f"'correct' must be true or false (a JSON boolean), "
                        f"got {type(entry['correct']).__name__}")
        # 'explain' may legitimately be empty -- the CORRECT option's praise
        # lives in success_text, so test_saddle ships explain="" for C.
        explain = _need_str(octx, "explain", entry["explain"], allow_empty=True)
        # G2.5-A design-time extras: light type check, then let them rest.
        for extra in _OPTION_OPTIONAL_KEYS & entry.keys():
            if extra == "domain":
                if (not isinstance(entry[extra], list) or len(entry[extra]) != 4
                        or not all(_is_num(v) for v in entry[extra])):
                    _fail(octx, "optional 'domain' must be 4 numbers (G2.5-A)")
            elif not _is_num(entry[extra]) or float(entry[extra]) <= 0.0:
                _fail(octx, f"optional '{extra}' must be a positive number (G2.5-A)")
        options.append(QuizOption(label=label, wav_path=wav,
                                  correct=entry["correct"], explain=explain))
    n_correct = sum(1 for o in options if o.correct)
    if n_correct != 1:
        _fail(ctx, f"'options' must have exactly ONE correct entry, "
                   f"got {n_correct}")
    return options


# =============================================================================
# PUBLIC API (frozen signatures)
# =============================================================================

def load_scene(scene_id: str) -> SceneSpec:
    """Read data/scenes/<scene_id>/scene.json -> SceneSpec.
    VALIDATE HARD, fail loud at load (never mid-game):
      - surface_name in surfaces.REGISTRY
      - exactly 4 options, exactly one correct
      - every option wav exists, equation.png exists
      - hint_lines: 1-3 lines; title_lines: 1-3 lines
      - totem_start inside domain; camera_limits keys present.

    (Parent G, beyond the frozen text above: PURE -- reads JSON, returns a
    fully-populated SceneSpec, no side effects, safe to call twice (main.py
    boot + GameState.__init__, DeepSeek Q1). All 13 fields required; only
    camera_limits keys are defaultable, per G3.2-A. Every failure raises
    SceneError with scene, key, problem, and remedy in one message.)
    """
    ctx = f"scene '{scene_id}'"
    folder = os.path.join(config.SCENES_DIR, scene_id)
    raw = _read_json(os.path.join(folder, "scene.json"), ctx)
    if not isinstance(raw, dict):
        _fail(ctx, f"scene.json must contain a JSON object, "
                   f"got {type(raw).__name__}")

    missing = _TOP_LEVEL_KEYS - raw.keys()
    if missing:
        _fail(ctx, f"missing required key(s): {sorted(missing)}")
    unknown = raw.keys() - _TOP_LEVEL_KEYS
    if unknown:
        _fail(ctx, f"unknown key(s) {sorted(unknown)}; valid keys are "
                   f"{sorted(_TOP_LEVEL_KEYS)}")

    inner_id = _need_str(ctx, "scene_id", raw["scene_id"])
    if inner_id != scene_id:
        _fail(ctx, f"scene_id inside the file is '{inner_id}' but the folder "
                   f"is '{scene_id}' -- they must match")

    surface_name = _need_str(ctx, "surface_name", raw["surface_name"])
    try:
        surfaces.get(surface_name)      # existence check; error lists all names
    except KeyError as e:
        _fail(ctx, str(e).strip('"'))

    title_lines = _need_lines(ctx, "title_lines", raw["title_lines"])
    hint_lines = _need_lines(ctx, "hint_lines", raw["hint_lines"])
    question = _need_str(ctx, "question", raw["question"])
    success_text = _need_str(ctx, "success_text", raw["success_text"],
                             allow_empty=True)   # empty is a legal choice
    equation_png = _need_file(
        ctx, "equation_png", _need_str(ctx, "equation_png", raw["equation_png"]))

    domain = _validate_domain(ctx, raw["domain"])
    mesh_step = _validate_mesh_step(ctx, raw["mesh_step"], domain)
    totem_start = _validate_totem_start(ctx, raw["totem_start"], domain)
    z_per_octave = _need_num(ctx, "z_per_octave", raw["z_per_octave"])
    if z_per_octave <= 0.0:
        _fail(ctx, f"'z_per_octave' must be > 0, got {z_per_octave}")
    camera_limits = _validate_camera_limits(ctx, raw["camera_limits"])
    options = _validate_options(ctx, raw["options"])

    return SceneSpec(
        scene_id=inner_id, title_lines=title_lines, surface_name=surface_name,
        equation_png=equation_png, totem_start=totem_start, domain=domain,
        mesh_step=mesh_step, z_per_octave=z_per_octave, question=question,
        hint_lines=hint_lines, options=options, camera_limits=camera_limits,
        success_text=success_text,
    )


def campaign_order() -> list:
    """The 12 scene_ids in UPANISHADS Act order, read from
    data/scenes/campaign.json (a simple ordered list -- content, not code).

    (Parent G: verified live format is a bare JSON array -- currently
    ["test_saddle"] -- and per DeepSeek Q6 this validates each entry's folder
    and scene.json EXIST, failing loud at load. Existence only: full content
    validation stays load_scene's job, so one broken future scene is reported
    by name the moment the game reaches for it, with maximum context.
    Duplicates are rejected -- a campaign that repeats a scene_id is a
    copy-paste accident, not a design.)
    """
    ctx = "campaign.json"
    path = os.path.join(config.SCENES_DIR, "campaign.json")
    data = _read_json(path, ctx)
    if not isinstance(data, list) or len(data) == 0:
        _fail(ctx, "must be a non-empty JSON array of scene_id strings, "
                   "e.g. [\"test_saddle\"]")
    seen = set()
    for i, sid in enumerate(data):
        if not isinstance(sid, str) or not sid.strip():
            _fail(ctx, f"entry [{i}] must be a non-empty string, got {sid!r}")
        if sid in seen:
            _fail(ctx, f"duplicate scene_id '{sid}' at entry [{i}]")
        seen.add(sid)
        scene_json = os.path.join(config.SCENES_DIR, sid, "scene.json")
        if not os.path.isfile(scene_json):
            _fail(ctx, f"entry [{i}] names scene '{sid}' but '{scene_json}' "
                       f"does not exist")
    return list(data)


# =============================================================================
# SELF-TEST -- run `python -m core.scene` from the repo root.
# Loads the REAL campaign and fully validates every listed scene against the
# live files on disk (today: test_saddle). Additive; never run by the game.
# (Negative cases -- bad JSON, missing keys -- are NOT tested here: that
# would mean writing broken temp files to disk, which a self-test should
# not do. The validators above are exercised positively end-to-end.)
# =============================================================================

if __name__ == "__main__":
    ids = campaign_order()
    print(f"campaign.json OK -- {len(ids)} scene(s): {ids}")
    for sid in ids:
        spec = load_scene(sid)
        assert spec.scene_id == sid
        assert sum(1 for o in spec.options if o.correct) == 1
        assert all(os.path.isfile(o.wav_path) for o in spec.options)
        assert set(spec.camera_limits) == set(_CAMERA_DEFAULTS)
        print(f"  scene '{sid}' OK -- surface={spec.surface_name}, "
              f"domain={spec.domain}, mesh_step={spec.mesh_step}, "
              f"{len(spec.options)} options "
              f"(correct: {next(o.label for o in spec.options if o.correct)})")
    print("core/scene.py self-test: ALL PASSED. The door is hung, "
          "and it only opens for true scenes.")
