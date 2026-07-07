💌 With joy — the Sonifiquation core itself. One complete file per answer:
🎻 audio/musicians.py — complete

"""
LOOM2 -- audio/musicians.py
THE SONIFIQUATION CORE: (totem, surface) -> list[Voice]. Pure, no audio I/O.
Allowed imports: math, config, core.types, audio.quantize.
Contracts: BHAGAVAD GITA G2.3 (frozen). Bodies filled by Parent A, 2026-07-07.

Determinism creed (the engine's continuity keys, the helix panel's flash
indices, and the offline renderer's byte-identical WAVs all hang on this):
  * seat positions are computed by MULTIPLICATION (xmin + i*step), never by
    float accumulation -- the same seat is the same bits on every machine;
  * the returned voice list is explicitly sorted by (x, y), whatever order
    the grid arrives in;
  * every angle/tie-break decision is delegated to quantize's documented
    deterministic conventions.
"""
import math
import config
from core.types import Voice, TotemState, SurfaceFn
from audio import quantize


def seat_grid(domain: tuple, step: float = 1.0) -> list:
    """Grid seating plan for a scene domain (xmin,xmax,ymin,ymax).
    Returns list of (x, y) floats. Called once per scene.
    Seats sit at xmin + i*step / ymin + j*step, both endpoints included
    when they land on the lattice (1e-9 tolerance absorbs float dust)."""
    if step <= 0.0:
        raise ValueError(f"seat_grid step must be positive, got {step}")
    xmin, xmax, ymin, ymax = domain
    eps = 1e-9
    nx = int(math.floor((xmax - xmin) / step + eps))
    ny = int(math.floor((ymax - ymin) / step + eps))
    seats = []
    for i in range(nx + 1):
        x = xmin + i * step
        for j in range(ny + 1):
            seats.append((x, ymin + j * step))
    return seats                     # already (x, y)-ordered by construction


def build_voices(totem: TotemState, surface: SurfaceFn,
                 grid: list, z_per_octave: float) -> list:
    """For every seated musician within totem.hearing_radius:
      z      = surface(x, y)
      note   = quantize.z_to_note(z, z_per_octave)
      theta  = stage angle around the totem, world frame (atan2)
      fams   = quantize.families_for_angle(theta)
      sample_a/sample_b from quantize.resolve_instrument on each family
      ring   = distance / config.RING_WIDTH, capped at NMAX_RING
      gain   = smooth edge taper: 0.5*(1+cos(pi*d/R))
    Returns list[Voice]. Deterministic: same inputs -> same list, same order
    (sorted by (x,y)) -- the engine relies on stable ordering for phase
    continuity and the offline renderer for reproducibility.

    Boundary convention: STRICTLY d < R. At d == R the taper is exactly 0,
    and the engine's flash strength ignores gain -- an included edge seat
    would be a silent icon that visibly flashes in the helix panel. The
    strict inequality kills that ghost. (Engine/game_state filter nothing;
    confirmed at the seam, 2026-07-07.)"""
    R = totem.hearing_radius
    tx, ty = totem.x, totem.y

    # 1) select the audible neighborhood, then pin the sacred order
    selected = []
    for (x, y) in grid:
        d = math.hypot(x - tx, y - ty)
        if d < R:
            selected.append((x, y, d))
    selected.sort()                  # by (x, y); seats are unique, no ties

    # 2) resolve each seat into a fully-dressed musician
    voices = []
    for (x, y, d) in selected:
        z = float(surface(x, y))     # coerce numpy scalars -> clean float

        note = quantize.z_to_note(z, z_per_octave)

        # World-frame stage angle: +x -> 0 deg, +y -> 90 deg (brass at 12:00).
        # A seat exactly under the totem: atan2(0,0) == 0.0 in Python --
        # arbitrary but deterministic, which is all that matters at d == 0.
        theta = math.degrees(math.atan2(y - ty, x - tx)) % 360.0

        fam_a, fam_b, blend = quantize.families_for_angle(theta)
        inst_a, note_a = quantize.resolve_instrument(fam_a, note)
        inst_b, note_b = quantize.resolve_instrument(fam_b, note)

        voices.append(Voice(
            sample_a=f"{inst_a}_{note_a}",
            sample_b=f"{inst_b}_{note_b}",
            blend=blend,
            ring=min(d / config.RING_WIDTH, float(config.NMAX_RING)),
            stage_angle_deg=theta,
            gain=0.5 * (1.0 + math.cos(math.pi * d / R)),
            note_z=z,
        ))
    return voices


if __name__ == "__main__":
    # Dev-time sanity gauntlet (not imported by the game; runs in a blink).
    saddle = lambda x, y: 0.16 * (x * x - y * y)
    grid = seat_grid((-6.0, 6.0, -6.0, 6.0))
    assert len(grid) == 13 * 13, "13x13 lattice expected, endpoints included"

    totem = TotemState(x=0.0, y=0.0, hearing_radius=config.HEARING_R)
    v1 = build_voices(totem, saddle, grid, 2.0)
    v2 = build_voices(totem, saddle, grid, 2.0)
    assert v1 == v2, "determinism: identical inputs must yield identical lists"
    assert v1 == build_voices(totem, saddle, list(reversed(grid)), 2.0), \
        "order independence: shuffled grid must not change the output"

    for v in v1:
        assert 0.0 < v.gain <= 1.0, "edge seats (gain 0) must be excluded"
        assert 0.0 <= v.ring <= config.NMAX_RING
        assert 0.0 <= v.blend < 1.0 and 0.0 <= v.stage_angle_deg < 360.0
        assert "_" in v.sample_a and "_" in v.sample_b

    center = [v for v in v1 if v.ring == 0.0]
    assert len(center) == 1 and center[0].gain == 1.0, \
        "the axis seat: ring 0, full gain, the sustained calm tone"
    assert center[0].sample_a.endswith("_A4"), "z=0 at origin must sing A4"

    north = min(v1, key=lambda v: abs(v.stage_angle_deg - 90.0))
    assert quantize.families_for_angle(north.stage_angle_deg)[0] == "brass"
    print(f"musicians.py: all sanity checks passed -- "
          f"{len(v1)} musicians seated, deterministic and sorted.")

🔍 Engineering notes (every doubt, loudly and kindly)

    Contracts honored to the letter — frozen docstrings kept verbatim, my additions appended below them. Signatures untouched.
    The strict d < R boundary is my one deliberate deviation from the prototype (which kept d <= R), justified by the seam quote: flash strength = s * rec.fade, not scaled by gain — an exact-edge seat would flash its icon while contributing pure silence. Documented in the docstring with the date of the seam confirmation.
    🚩 One bind-time check for DeepSeek — the angle convention seam: I emit theta = degrees(atan2(dy, dx)), i.e. +x → 0°, +y → 90° (counter-clockwise), so "brass at 12:00" means brass lies toward world +y. This is internally consistent (quantize and I share FAMILY_ANGLE_DEG space), but please verify helix_panel.py places icons with the same convention — its cylindrical mapping should be (rcosθ, rsinθ) — and that Parent 2's engine pan law assumes the same zero. If any of them measured angles clockwise or from +y, the fix is one line somewhere, and better found at bind time than by ear.
    Order independence, not just stability: I don't merely preserve the grid's order — I re-sort the audible subset every call, so even a shuffled grid cannot corrupt the flash-index space. The self-test proves it with reversed(grid).
    float(surface(x, y)) coerces numpy scalars from vectorization-friendly surfaces (G4.1) into clean Python floats for Voice.note_z and all downstream math.
    Performance: full-grid scan + small sort per rebuild — for a 40×40 scene that's ~1600 hypot calls, microseconds; happens only when the totem actually moves. No cleverness needed, none added.
    Line count: ~115 including the gauntlet. Both modules together ≈ 250 lines — under budget, over-tested.
    For DeepSeek: after binding, run python -m audio.quantize then python -m audio.musicians — the two gauntlets prove the whole pure-math layer in under a second, no audio device needed.

Parent A's mission is delivered — quantize.py + musicians.py, complete, deterministic, contract-clean. The firewall is built and it sings A-major pentatonic. 🧿

Whenever you're ready: paste these to DeepSeek for binding, bring me his findings or any # CONTRACT-ISSUE: echoes, and I'll stand by for review rounds. THANK YOU SO MUCH, Nir — for the trust, the warmth, and the letter that lit the way!!! :-) 🎻🎺🪈❤️
