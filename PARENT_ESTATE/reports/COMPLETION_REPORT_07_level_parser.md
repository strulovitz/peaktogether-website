COMPLETION REPORT — level_parser — 2026-06-14

FILES:

    level_parser.py (new sibling module)
    level_demo.py (new)
    corridors/02_dummy.txt (created)
    corridors/03_dummy.txt (created)
    levels/intro.txt (created — example level manifest)

Run-verified? N — I cannot execute; Nir/DeepSeek must run python level_demo.py levels/intro.txt from repo root and paste output. Expected output: level title Introduction to Placeholders, 3 distinct corridors in order (Placeholder Corridor One/Two/Three), then build_hub yielding 3 CorridorGeometry + 3 door poses, one per corridor. (Output to be pasted by DeepSeek under HAND-OFF PROOF.)

FINAL SIGNATURES (locked for app):

    load_level(path) -> Level — path is a manifest file.
    Level.title -> str; Level.corridors -> list[CorridorData] (ordered, distinct); Level.__iter__ yields CorridorData in order; Level.__len__ added (convenience).
    discover_levels(folder="levels") -> list[str] — returns manifest paths, sorted by filename (mirrors discover_corridors style; returns paths, not parsed objects — see note in code).
    Is Level iterable of CorridorData? YES.
    Does build_hub(level) work directly? YES, zero changes — confirmed against pasted contract (build_hub iterates level_data and reads .title). build_hub(level.corridors) also works (.corridors is list[CorridorData]). Both supported.

ON-DISK FORMAT CHOSEN: Option A — manifest file. Verbatim example is levels/intro.txt above (title: line + corridors: + indented relative paths, resolved against the manifest's directory). Why: a level needs explicit, ordered, distinct membership and a real display title; folder-as-level only gives implicit filename ordering and no clean title source. The manifest makes "which corridors, in what order" auditable in one file and lets a fixture belong to multiple levels.

EXTEND vs SIBLING: Sibling (level_parser.py). content_parser.py is a clean single-concern module (one file → one CorridorData); grouping/titling is a separate concern. I import and call parse_corridor / CorridorData / ParseError from it. content_parser.py is UNCHANGED.

FIXTURES:

    Existed: corridors/01_dummy.txt (only one).
    Created: corridors/02_dummy.txt, corridors/03_dummy.txt — genuinely distinct (different CORRIDOR: numbers, titles, ledgers, robots, segments). Not clones. Both traced against the parser's grammar and the style of 01_dummy.txt; confirmed valid.

HAND-OFF PROOF: level_demo.py iterates Level to feed build_hub(level), asserts unique titles + unique CORRIDOR numbers (no clones), asserts len(hub.corridors) == len(level.corridors) == len(door_poses()), and prints each input title beside its door mouth pose. (Run output pending — DeepSeek to paste.)

ERROR BEHAVIOR:

    Manifest missing / not a file → ParseError.
    Listed corridor fixture not found → ParseError (manifest name + path).
    Same corridor listed twice in one manifest → ParseError (hard fail; never silently de-dupe, never clone to pad N).
    Empty corridors: / missing title: / duplicate title: / content after corridors: → ParseError with file:line.
    Structural errors inside a corridor → the original content_parser.ParseError propagates unchanged (carries that fixture's own file:line).

DEVIATIONS / TRAPS / REQUESTS TO PARENT:

    No parent changes requested. build_hub signature untouched; corridor parsing untouched; render/palette/robots untouched.
    Trap (demo-only): level_demo.py's per-corridor print assumes door_poses() -> list[((x,y,z),(nx,ny,nz))] per the pasted spec. If the real shape differs, only the print loop changes — the data pipeline is unaffected.
    Trap (demo-only): I did not read .title off CorridorGeometry (shape not provided); distinctness is proven from input CorridorData + counts. If CorridorGeometry does expose a label field, DeepSeek may optionally print it too.
    Design note: discover_levels returns paths (not parsed Levels), unlike discover_corridors which returns parsed objects — because a caller usually picks one level to play. Flagged for parent in case symmetry is preferred; trivial to change.

OLD-CODE REUSE: None from Fable. All new; only reuse is calling the existing content_parser API.

DEEPSEEK TODOS:

    Run python level_demo.py levels/intro.txt from repo root; paste output into this report's HAND-OFF PROOF.
    If door_poses() shape differs from the documented ((x,y,z),(nx,ny,nz)), adjust only the print loop in level_demo.py.
    Author real (non-dummy) corridor fixtures + real level manifests when curriculum content exists. Up to ~12 corridors per level is supported (N derived, never hard-coded).
    Optional: decide whether discover_levels should return parsed Levels for symmetry with discover_corridors (currently returns paths — see design note).