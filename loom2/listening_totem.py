"""
LOOM2 -- The Listening Prototype ("The Listening Totem")
=========================================================
A 2D surface z = f(x,y) with a musician seated on every grid point.
Plant the totem: every musician inside the hearing circle plays.
  height z -> pitch  (A4 = 440 Hz at z=0, pentatonic-quantized, +/-3 octaves)
  angle theta -> timbre (brass at 12 o'clock, strings at 4, woodwinds at 8, morphed)
  radius r -> rhythm ring (n pulses per 2.0s measure, half-and-half crossfade)
No sirens. No sweeping. The land plays a looping groove; moving the totem
re-orchestrates the whole song.

Run:  pip install numpy pygame sounddevice
      python listening_totem.py
"""
import math
import numpy as np
import pygame
import sounddevice as sd

# ---------------- configuration ----------------
SR        = 44100        # audio sample rate
BLOCK     = 1024         # audio block size
MEASURE   = 2.0          # seconds per measure (120 BPM, four beats) -- fixed
F0        = 440.0        # A4 at z = 0  (the origin-centered helix)
Z_OCT     = 2.0          # height units per octave
DOMAIN    = 5.0          # world is [-5,5] x [-5,5]
GRID_STEP = 1.0          # musician seating distance
RING_W    = 0.8          # width of one rhythm ring (world units)
NMAX      = 5            # fastest rhythm ring (pulses per measure)
PENTA     = (0, 2, 4, 7, 9)   # major pentatonic degrees

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

# ---------------- wavetables (the orchestra circle) ----------------
WT = 2048
def make_table(amps):
    t = np.arange(WT) / WT
    w = np.zeros(WT)
    for n, a in enumerate(amps, start=1):
        w += a * np.sin(2 * np.pi * n * t)
    return (w / np.max(np.abs(w))).astype(np.float32)

BRASS   = make_table([1.0 / n for n in range(1, 13)])                    # bright, all harmonics
STRINGS = make_table([1.0 / n ** 2 for n in range(1, 13)])               # soft, mellow
WOOD    = make_table([1.0 / n if n % 2 == 1 else 0.0 for n in range(1, 13)])  # hollow, odd harmonics
# anchors on the stage clock: brass 90deg (12:00), woodwind 210deg (8:00), strings 330deg (4:00)

def timbre(theta_deg):
    """Return (tableA, tableB, blend 0..1) for a stage angle."""
    a = theta_deg % 360.0
    if 90.0 <= a < 210.0:
        return BRASS, WOOD, (a - 90.0) / 120.0
    if 210.0 <= a < 330.0:
        return WOOD, STRINGS, (a - 210.0) / 120.0
    b = a - 330.0 if a >= 330.0 else a + 30.0
    return STRINGS, BRASS, b / 120.0

def snap_semi(s):
    """Clamp to +/-3 octaves and snap to the pentatonic scale. No sirens."""
    s = max(-36.0, min(36.0, s))
    base = 12.0 * math.floor(s / 12.0)
    cands = [base + p for p in PENTA] + [base + 12.0]
    return min(cands, key=lambda c: abs(c - s))

# ---------------- the seated musicians ----------------
_g = np.arange(-DOMAIN, DOMAIN + 1e-6, GRID_STEP)
GRID = [(i, j, float(px), float(py))
        for i, px in enumerate(_g) for j, py in enumerate(_g)]

# ---------------- the audio engine ----------------
class Engine:
    def __init__(self):
        self.tx, self.ty = 0.0, 0.0        # totem position
        self.radius = 2.5                  # hearing radius
        self.surf_idx = 1                  # start on The Bowl
        self.phases = {}                   # per-musician oscillator phase
        self.counter = 0                   # global sample counter

    def callback(self, out, frames, time_info, status):
        t = (self.counter + np.arange(frames)) / SR
        mph = (t / MEASURE) % 1.0          # measure phase 0..1
        # pulse envelopes for each rhythm ring (ring 0 = sustained tone)
        envs = [np.ones(frames, np.float32)]
        for n in range(1, NMAX + 1):
            loc = (mph * n) % 1.0
            env = np.clip(loc / 0.012, 0.0, 1.0) * np.exp(-6.0 * loc)
            envs.append(env.astype(np.float32))

        tx, ty, R = self.tx, self.ty, self.radius
        fn = SURFACES[self.surf_idx][1]
        mix = np.zeros(frames, np.float32)
        count = 0
        for (i, j, px, py) in GRID:
            dx, dy = px - tx, py - ty
            d = math.hypot(dx, dy)
            if d > R:
                continue
            count += 1
            z = float(fn(px, py))
            semi = snap_semi(12.0 * z / Z_OCT)
            freq = F0 * 2.0 ** (semi / 12.0)
            ta, tb, w = timbre(math.degrees(math.atan2(dy, dx)))
            rr = min(d / RING_W, float(NMAX))
            n0 = min(int(rr), NMAX)
            n1 = min(n0 + 1, NMAX)
            wr = rr - n0
            env = (1.0 - wr) * envs[n0] + wr * envs[n1]
            ph0 = self.phases.get((i, j), 0.0)
            ph = (ph0 + freq * np.arange(1, frames + 1) / SR) % 1.0
            self.phases[(i, j)] = float(ph[-1])
            idx = (ph * WT).astype(np.int32) % WT
            wave = (1.0 - w) * ta[idx] + w * tb[idx]
            taper = 0.5 * (1.0 + math.cos(math.pi * d / R))   # smooth edge fade
            mix += wave * env * np.float32(taper)
        if count:
            mix *= 0.7 / math.sqrt(count)
        out[:, 0] = np.tanh(mix) * 0.85
        self.counter += frames

# ---------------- the map picture ----------------
def render_map(fn, size):
    n = 220
    xs = np.linspace(-DOMAIN, DOMAIN, n)
    ys = np.linspace(DOMAIN, -DOMAIN, n)          # +y is up on screen
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
    MAPS, MX, MY = 560, 20, 20
    screen = pygame.display.set_mode((940, 600))
    pygame.display.set_caption("LOOM2 -- The Listening Totem (prototype)")
    font  = pygame.font.SysFont("consolas", 16)
    font2 = pygame.font.SysFont("consolas", 20, bold=True)
    clock = pygame.time.Clock()

    eng = Engine()
    map_img = render_map(SURFACES[eng.surf_idx][1], MAPS)
    stream = sd.OutputStream(samplerate=SR, blocksize=BLOCK, channels=1,
                             callback=eng.callback)
    stream.start()

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
        for (_, _, px, py) in GRID:                      # the seated musicians
            sx, sy = w2s(px, py)
            d = math.hypot(px - eng.tx, py - eng.ty)
            if d <= eng.radius:
                pygame.draw.circle(screen, (255, 255, 210), (int(sx), int(sy)), 4)
            else:
                pygame.draw.circle(screen, (40, 40, 50), (int(sx), int(sy)), 2)
        cx, cy = w2s(eng.tx, eng.ty)
        rpix = eng.radius / (2 * DOMAIN) * MAPS
        pygame.draw.circle(screen, (255, 230, 120), (int(cx), int(cy)), int(rpix), 2)
        for n in range(1, NMAX + 1):                     # rhythm rings
            rw = n * RING_W / (2 * DOMAIN) * MAPS
            if rw < rpix:
                pygame.draw.circle(screen, (120, 110, 70), (int(cx), int(cy)), int(rw), 1)
        ang = 2 * math.pi * ((eng.counter / SR / MEASURE) % 1.0)  # conductor's arm
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
        px = MX + MAPS + 20
        screen.blit(font2.render("THE LISTENING TOTEM", True, (255, 230, 120)), (px, 24))
        screen.blit(font2.render(name, True, (230, 230, 240)), (px, 70))
        for k, line in enumerate(hint):
            screen.blit(font.render(line, True, (180, 200, 180)), (px, 110 + 22 * k))
        ctrl = ["Arrows / WASD : move the totem",
                "1..6          : choose surface",
                "+ / -         : hearing radius",
                "Esc           : quit",
                "",
                "z=0 sounds A4=440Hz. Water (blue)",
                "sounds BELOW A4 -- negative numbers!",
                "One sweep of the arm = one measure."]
        for k, line in enumerate(ctrl):
            screen.blit(font.render(line, True, (140, 150, 170)), (px, 240 + 22 * k))
        pygame.display.flip()

    stream.stop(); stream.close(); pygame.quit()

if __name__ == "__main__":
    main()
