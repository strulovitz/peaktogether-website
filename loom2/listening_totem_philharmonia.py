"""
LOOM2 -- The Listening Prototype  (PHILHARMONIA EDITION ✨)
===========================================================
Enhanced version: swaps the synthesized wavetables for REAL Philharmonia
recordings.  Every musician in the hearing circle retriggers an actual
violin / trumpet / flute sample on each rhythm pulse — no synth, no
pitch-shift.  Samples pre-resolved once from the Philharmonia library
in Downloads/philharmonia/ (the same library used by LOOM v1's M1 demo).

  pip install numpy pygame sounddevice
  python listening_totem_philharmonia.py
"""
import math
import os
import numpy as np
import pygame
import sounddevice as sd

# ---------------- configuration ----------------
SR = 44100                          # audio sample rate
BLOCK = 1024                        # audio block size
MEASURE = 2.0                       # seconds per measure (120 BPM, four beats)
F0 = 440.0                          # A4 at z = 0
Z_OCT = 2.0                         # height units per octave
DOMAIN = 5.0                        # world is [-5,5] x [-5,5]
GRID_STEP = 1.0                     # musician seating distance
RING_W = 0.8                        # width of one rhythm ring (world units)
NMAX = 5                            # fastest rhythm ring (pulses per measure)
PENTA = (0, 2, 4, 7, 9)            # major pentatonic degrees

PHILHARMONIA = r"C:\Users\nir_s\Downloads\philharmonia"

# Mapping: stage family  ->  instrument folder name
FAMILY_MAP = {
    "strings": "violin",
    "brass":   "trumpet",
    "wood":    "flute",
}

_SILENCE = np.zeros(1, np.float32)

# ---------------- the surfaces ----------------
def s_ramp(x, y):   return 0.55 * x + 0.30 * y
def s_bowl(x, y):   return 0.16 * (x * x + y * y) - 1.0
def s_hill(x, y):   return 3.4 * np.exp(-(x * x + y * y) / 7.0) - 0.6
def s_ridge(x, y):  return 1.8 - 0.22 * x * x + 0.0 * y
def s_saddle(x, y): return 0.16 * (x * x - y * y)
def s_egg(x, y):    return 1.6 * np.sin(1.5 * x) * np.sin(1.5 * y)

SURFACES = [
    ("1. The Ramp    z = ax + by", s_ramp,
     ["Walk anywhere: the WHOLE groove transposes,",
      "but keeps its exact shape. Key changes, song stays.",
      "That is what slope sounds like."]),
    ("2. The Bowl    z = x^2 + y^2", s_bowl,
     ["Stand at the very bottom: every ring sings ONE",
      "note in unison -- you are HEARING level curves.",
      "Rings rise in pitch as they go outward."]),
    ("3. The Hill    z = Gaussian dome", s_hill,
     ["Stand on the summit: the chord hangs BELOW you.",
      "The bowl, upside-down. A maximum, by ear."]),
    ("4. The Ridge   z = -x^2  (no y!)", s_ridge,
     ["One player's movement changes the music.",
      "The other player's changes NOTHING.",
      "You are hearing partial derivatives."]),
    ("5. The Saddle  z = x^2 - y^2", s_saddle,
     ["Stand at the pass: notes BOTH above and below --",
      "a stretched, tense chord. Rings are never unison.",
      "Compare with the Bowl. That's the whole test."]),
    ("6. The Egg Carton  z = sin x * sin y", s_egg,
     ["Wander around: summit-groove, valley-groove and",
      "pass-groove repeat in a pattern. One surface,",
      "the complete zoo of critical points."]),
]

def snap_semi(s):
    """Clamp to +/-3 octaves and snap to the pentatonic scale. No sirens."""
    s = max(-36.0, min(36.0, s))
    base = 12.0 * math.floor(s / 12.0)
    cands = [base + p for p in PENTA] + [base + 12.0]
    return min(cands, key=lambda c: abs(c - s))


# ---------------- sample bank (load once at startup) ----------------
NOTE_NAMES = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']

def note_to_midi(name):
    """violin_A4 -> 69.  name is case-preserved from the key."""
    lower = name.lower()
    # strip instrument prefix if any (the bank keys don't have it)
    parts = lower.split('_')
    note_part = parts[-1] if len(parts) > 1 else lower
    if len(note_part) < 2:
        return 60
    letter = note_part[0].upper()
    rest = note_part[1:]
    if 's' in rest:
        sharp = True
        rest = rest.replace('s', '')
    else:
        sharp = False
    octave_str = rest
    if not octave_str.isdigit():
        return 60
    octave = int(octave_str)
    pc = letter
    if sharp:
        pc += 's'
    try:
        idx = NOTE_NAMES.index(pc)
    except ValueError:
        return 60
    return (octave + 1) * 12 + idx


def load_bank():
    """Scan the three instrument folders, build a nested dict:
       bank[family] = { source_midi : sample_array_float32 }
    Keeps EVERY recorded note (octave preserved) so pitch = data.
    Picks the longest sustained, loudest sample available for each note.
    """
    bank = {"brass": {}, "wood": {}, "strings": {}}
    for family, instrument in FAMILY_MAP.items():
        folder = os.path.join(PHILHARMONIA, instrument)
        if not os.path.isdir(folder):
            print(f"  WARNING: {folder} not found — {family} will be silent.")
            continue
        files = [f for f in os.listdir(folder) if f.endswith('.mp3')]
        if not files:
            print(f"  WARNING: no mp3s in {folder}")
            continue
        # Group by note name; pick best candidate (longest, loudest, sustained)
        best = {}            # note_name_lower -> (path_str, score_int)
        for fn in files:
            base = fn[:-4]   # strip .mp3
            parts = base.split('_')
            if len(parts) < 2:
                continue
            note_raw = parts[1]   # e.g. "A4" or "Cs4"
            articulation = parts[-1] if len(parts) >= 5 else 'normal'
            if articulation not in ('arco-normal', 'normal', 'sustain', 'sustained'):
                continue
            score = 0
            if len(parts) >= 3:
                tok = parts[2]
                if tok in ('15', '2', 'long', 'very-long'):
                    score = 30
                elif tok == '1':
                    score = 20
                elif tok == '05':
                    score = 10
                elif tok == '025':
                    score = 5
                else:
                    continue   # phrase etc — skip
            if 'fortissimo' in base:
                score += 100
            elif 'forte' in base:
                score += 80
            elif 'mezzo-forte' in base:
                score += 60
            elif 'mezzo-piano' in base:
                score += 40
            elif 'piano' in base:
                score += 20
            elif 'pianissimo' in base:
                score += 10
            key = note_raw.lower()
            if key not in best or score > best[key][1]:
                best[key] = (os.path.join(folder, fn), score)
        # Load each best candidate, keyed by its true MIDI note
        loaded = 0
        for note_key, (path, _score) in best.items():
            try:
                snd = pygame.mixer.Sound(path)
                arr = pygame.sndarray.array(snd).astype(np.float32)
                if arr.ndim == 2:
                    arr = arr.mean(axis=1).astype(np.float32)   # mono
                peak = np.max(np.abs(arr))
                if peak > 0.0001:
                    arr *= 0.85 / peak
                fade_n = min(int(SR * 0.025), len(arr) // 2)
                if fade_n > 0:
                    arr[-fade_n:] *= np.linspace(1.0, 0.0, fade_n).astype(np.float32)
                midi = note_to_midi(note_key)
                bank[family][midi] = arr
                loaded += 1
            except Exception as e:
                print(f"  SKIP {note_key}: {e}")
        midis = sorted(bank[family].keys())
        rng = f"MIDI {midis[0]}..{midis[-1]}" if midis else "none"
        print(f"  {family:>8} -> {instrument:>8}: {loaded} notes ({rng})")
    return bank


def resample_to_midi(bank_family, target_midi):
    """Pick the nearest recorded note in this family and resample it to the
    EXACT target pitch (preserving octave/height). Returns float32 array or None."""
    if not bank_family:
        return None
    src_midi = min(bank_family.keys(), key=lambda m: abs(m - target_midi))
    arr = bank_family[src_midi]
    semis = target_midi - src_midi
    if semis == 0:
        return arr
    ratio = 2.0 ** (semis / 12.0)          # >1 = play faster = higher pitch
    new_len = max(2, int(len(arr) / ratio))
    idx = np.arange(new_len, dtype=np.float64) * ratio
    idx = np.clip(idx, 0, len(arr) - 1)
    return np.interp(idx, np.arange(len(arr)), arr).astype(np.float32)


# ---------------- the seated musicians (grid) ----------------
_g = np.arange(-DOMAIN, DOMAIN + 1e-6, GRID_STEP)
GRID = [(i, j, float(px), float(py))
        for i, px in enumerate(_g) for j, py in enumerate(_g)]


# ---------------- timbre blending (angle -> which two families, and blend 0..1) ----------------
def timbre(theta_deg):
    """Return (famA, famB, blend 0..1) for a stage angle.
    brass at 90deg (12:00), wood at 210deg (8:00), strings at 330deg (4:00)."""
    a = theta_deg % 360.0
    if 90.0 <= a < 210.0:
        return "brass", "wood", (a - 90.0) / 120.0
    if 210.0 <= a < 330.0:
        return "wood", "strings", (a - 210.0) / 120.0
    b = a - 330.0 if a >= 330.0 else a + 30.0
    return "strings", "brass", b / 120.0


# ---------------- the audio engine (real-time sample retrigger) ----------------
class Engine:
    def __init__(self, bank):
        self.bank = bank
        self.tx, self.ty = 0.0, 0.0
        self.radius = 2.5
        self.surf_idx = 1
        self.counter = 0
        # Precompute per-musician target pitch + resampled voices for current surface
        self._musicians = []       # list of (px, py, target_midi)
        self._voice_cache = {}     # (family, target_midi) -> resampled arr
        self._prev_surf = -1
        self._rebuild_musicians()

    def _rebuild_musicians(self):
        """For the current surface, precompute each musician's target MIDI note and
        resample the real samples to that EXACT pitch (once, off the audio thread)."""
        self._musicians.clear()
        self._voice_cache = {}      # (family, target_midi) -> resampled arr
        fn = SURFACES[self.surf_idx][1]
        for (i, j, px, py) in GRID:
            z = float(fn(px, py))
            semi = snap_semi(12.0 * z / Z_OCT)
            target_midi = 69 + int(round(semi))     # A4 = MIDI 69 at z=0
            for family in ("brass", "wood", "strings"):
                key = (family, target_midi)
                if key not in self._voice_cache:
                    self._voice_cache[key] = resample_to_midi(self.bank.get(family, {}),
                                                              target_midi)
            self._musicians.append((px, py, target_midi))
        self._pos = [-1] * len(self._musicians)      # per-musician playback read index
        self._prev_surf = self.surf_idx

    def _get_buf(self, family, target_midi):
        """Return the cached octave-accurate sample for this family+pitch (or None)."""
        return self._voice_cache.get((family, target_midi))

    def callback(self, out, frames, time_info, status):
        if self.surf_idx != self._prev_surf:
            self._rebuild_musicians()

        tx, ty, R = self.tx, self.ty, self.radius
        mix = np.zeros(frames, np.float32)
        active = 0
        c = self.counter
        MS = MEASURE * SR                       # samples per measure

        for k, (px, py, target_midi) in enumerate(self._musicians):
            dx, dy = px - tx, py - ty
            d = math.hypot(dx, dy)
            if d > R:
                self._pos[k] = -1               # left the circle -> silence
                continue
            active += 1

            # --- rhythm ring -> pulses per measure ---
            rr = min(d / RING_W, float(NMAX))
            n_ring = min(int(rr), NMAX)
            pm = max(n_ring, 1)                  # ring 0 (axis) = 1 long note/measure
            period = MS / pm                     # samples between retriggers

            # --- family blend at this angle ---
            angle = math.degrees(math.atan2(dy, dx))
            fa, fb, blend_w = timbre(angle)
            arr_a = self._get_buf(fa, target_midi)
            arr_b = self._get_buf(fb, target_midi)
            if arr_a is None:
                arr_a = _SILENCE
            if arr_b is None:
                arr_b = _SILENCE
            L = min(len(arr_a), len(arr_b))
            if L < 2:
                continue
            wa = np.float32(1.0 - blend_w)
            wb = np.float32(blend_w)
            taper = np.float32(0.5 * (1.0 + math.cos(math.pi * d / R)))

            # --- find an onset (at most one per block; period >> frames) ---
            pos = self._pos[k]
            onset_local = -1
            first_pulse = math.ceil(c / period) * period      # first pulse >= block start
            if c <= first_pulse < c + frames:
                onset_local = int(round(first_pulse - c))
            if pos < 0:                                        # just entered the circle
                onset_local = 0

            # --- continuation of the note already sounding (only read what we need) ---
            if pos >= 0:
                end = onset_local if onset_local > 0 else frames
                if end > 0 and pos < L:
                    n = min(end, L - pos)
                    seg = wa * arr_a[pos:pos + n] + wb * arr_b[pos:pos + n]
                    mix[0:n] += seg * taper
                pos += end

            # --- the freshly retriggered note (from the sample's attack) ---
            if onset_local >= 0:
                n = min(frames - onset_local, L)
                if n > 0:
                    seg = wa * arr_a[0:n] + wb * arr_b[0:n]
                    mix[onset_local:onset_local + n] += seg * taper
                pos = frames - onset_local

            self._pos[k] = pos

        if active > 0:
            mix *= 0.55 / math.sqrt(float(active))

        out[:, 0] = np.tanh(mix) * 0.85
        self.counter += frames


# ---------------- the map picture (unchanged from original) ----------------
def render_map(fn, size):
    n = 220
    xs = np.linspace(-DOMAIN, DOMAIN, n)
    ys = np.linspace(DOMAIN, -DOMAIN, n)
    X, Y = np.meshgrid(xs, ys)
    Z = fn(X, Y)
    img = np.zeros((n, n, 3), np.uint8)
    deep = np.clip(-Z / 3.5, 0, 1)
    water = Z < 0
    img[..., 0] = np.where(water, 20 + 30 * (1 - deep), 0)
    img[..., 1] = np.where(water, 60 + 80 * (1 - deep), 0)
    img[..., 2] = np.where(water, 140 + 90 * (1 - deep), 0)
    lo = (~water) & (Z < 1.4)
    u = np.clip(Z / 1.4, 0, 1)
    img[..., 0] = np.where(lo, 70 + 50 * u, img[..., 0])
    img[..., 1] = np.where(lo, 160 - 20 * u, img[..., 1])
    img[..., 2] = np.where(lo, 80 - 25 * u, img[..., 2])
    mid = (Z >= 1.4) & (Z < 3.0)
    v = np.clip((Z - 1.4) / 1.6, 0, 1)
    img[..., 0] = np.where(mid, 150 - 30 * v, img[..., 0])
    img[..., 1] = np.where(mid, 110 - 25 * v, img[..., 1])
    img[..., 2] = np.where(mid, 70 - 10 * v, img[..., 2])
    hi = Z >= 3.0
    img[..., 0] = np.where(hi, 232, img[..., 0])
    img[..., 1] = np.where(hi, 232, img[..., 1])
    img[..., 2] = np.where(hi, 238, img[..., 2])
    surf = pygame.surfarray.make_surface(np.transpose(img, (1, 0, 2)))
    return pygame.transform.smoothscale(surf, (size, size))


# ---------------- main ----------------
def main():
    pygame.init()
    pygame.mixer.init(frequency=SR, size=-16, channels=2, buffer=256)
    MAPS, MX, MY = 560, 20, 20
    screen = pygame.display.set_mode((940, 600))
    pygame.display.set_caption("LOOM2 -- The Listening Totem  (PHILHARMONIA)")
    font  = pygame.font.SysFont("consolas", 16)
    font2 = pygame.font.SysFont("consolas", 20, bold=True)
    clock = pygame.time.Clock()

    print("=" * 60)
    print(" LOOM2 — Listening Totem — PHILHARMONIA EDITION")
    print("=" * 60)
    print("Loading real instrument samples...")
    bank = load_bank()
    total_notes = sum(len(v) for v in bank.values())
    print(f"  Bank ready: {total_notes} real notes across {len(bank)} instrument families.")
    print()

    eng = Engine(bank)
    map_img = render_map(SURFACES[eng.surf_idx][1], MAPS)
    stream = sd.OutputStream(samplerate=SR, blocksize=BLOCK, channels=1,
                             callback=eng.callback)
    stream.start()
    print("🎧 Running! Arrows/WASD = move totem, 1-6 = surface, +/- = radius, Esc = quit.")
    print()

    def w2s(x, y):
        return (MX + (x + DOMAIN) / (2 * DOMAIN) * MAPS,
                MY + (DOMAIN - y) / (2 * DOMAIN) * MAPS)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                if pygame.K_1 <= ev.key <= pygame.K_6:
                    eng.surf_idx = ev.key - pygame.K_1
                    map_img = render_map(SURFACES[eng.surf_idx][1], MAPS)
                if ev.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    eng.radius = min(4.0, eng.radius + 0.5)
                if ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    eng.radius = max(1.0, eng.radius - 0.5)

        keys = pygame.key.get_pressed()
        sp = 2.2 * dt
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: eng.tx -= sp
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: eng.tx += sp
        if keys[pygame.K_UP]    or keys[pygame.K_w]: eng.ty += sp
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: eng.ty -= sp
        eng.tx = max(-DOMAIN, min(DOMAIN, eng.tx))
        eng.ty = max(-DOMAIN, min(DOMAIN, eng.ty))

        # ---- draw ----
        screen.fill((16, 16, 24))
        screen.blit(map_img, (MX, MY))
        for (_, _, px, py) in GRID:
            sx, sy = w2s(px, py)
            d = math.hypot(px - eng.tx, py - eng.ty)
            if d <= eng.radius:
                pygame.draw.circle(screen, (255, 255, 210), (int(sx), int(sy)), 4)
            else:
                pygame.draw.circle(screen, (40, 40, 50), (int(sx), int(sy)), 2)
        cx, cy = w2s(eng.tx, eng.ty)
        rpix = eng.radius / (2 * DOMAIN) * MAPS
        pygame.draw.circle(screen, (255, 230, 120), (int(cx), int(cy)), int(rpix), 2)
        for n in range(1, NMAX + 1):
            rw = n * RING_W / (2 * DOMAIN) * MAPS
            if rw < rpix:
                pygame.draw.circle(screen, (120, 110, 70), (int(cx), int(cy)), int(rw), 1)
        ang = 2 * math.pi * ((eng.counter / SR / MEASURE) % 1.0)
        ax = cx + rpix * math.sin(ang)
        ay = cy - rpix * math.cos(ang)
        pygame.draw.line(screen, (255, 240, 180), (cx, cy), (ax, ay), 2)
        pygame.draw.line(screen, (255, 90, 90), (cx - 7, cy), (cx + 7, cy), 3)
        pygame.draw.line(screen, (255, 90, 90), (cx, cy - 7), (cx, cy + 7), 3)
        for label, deg in (("BRASS", 90), ("WOOD", 210), ("STRINGS", 330)):
            lx = cx + (rpix + 16) * math.cos(math.radians(deg))
            ly = cy - (rpix + 16) * math.sin(math.radians(deg))
            txt = font.render(label, True, (255, 220, 140))
            screen.blit(txt, txt.get_rect(center=(lx, ly)))

        name, _, hint = SURFACES[eng.surf_idx]
        px_ui = MX + MAPS + 20
        screen.blit(font2.render("THE LISTENING TOTEM  (PHILHARMONIA)", True, (255, 230, 120)),
                    (px_ui, 24))
        screen.blit(font2.render(name, True, (230, 230, 240)), (px_ui, 70))
        for k, line in enumerate(hint):
            screen.blit(font.render(line, True, (180, 200, 180)), (px_ui, 110 + 22 * k))
        ctrl = ["Arrows / WASD : move the totem",
                "1..6          : choose surface",
                "+ / -         : hearing radius",
                "Esc           : quit",
                "",
                "PHILHARMONIA EDITION: real instruments!",
                "Violin / Trumpet / Flute samples.",
                "One sweep of the arm = one measure."]
        for k, line in enumerate(ctrl):
            screen.blit(font.render(line, True, (140, 150, 170)), (px_ui, 240 + 22 * k))
        pygame.display.flip()

    stream.stop(); stream.close(); pygame.quit()


if __name__ == "__main__":
    main()
