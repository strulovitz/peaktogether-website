# PROMPT TO OPUS 4.8 — QUAKE PARENT 22: BUILD THE DEMON (with MANY balls)

You are **Parent 22** of the QUAKE project. **Write code. Build it. Do not deliberate, do not ask permission, do not "propose an approach" — the design is already decided and proven.** We already built exactly this demon in our earlier **DOOM** prototype. Your job is to reproduce that same demon in QUAKE's renderer, but made of **many more balls**, plus its three surrounding effects. Everything below is decided by Nir and by the working DOOM code. Just implement it.

You have **no file access and no internet** — you only know what is in this prompt. Everything you need is here. Deliver complete, runnable Python in fenced code blocks (never Markdown tables). If one external API name is genuinely uncertain, say so in one line so DeepSeek confirms it on the machine — otherwise, write the code.

---

## 1. HOW WE ALREADY DID IT IN DOOM (the proven pattern — copy this design)

The DOOM demon was a cluster of colored spheres with a hit-count, a float/bob while alive, and a disintegration burst on death that then revealed a blood-red equation on the ceiling. Here is the **verbatim** DOOM demon (`doom/principia/enemy/demon.py`) so you copy the exact behavior:

```python
class Demon:
    def __init__(self, spec, position, parent=None):
        self._health = _Health(spec.hp)          # hp = 3
        self._t = 0.0
        self._base_y = position[1]
        self.root = Entity(position=position, rotation=(0, 180, 0))  # face the player
        self._circles = []
        # Big body drawn first; smaller features drawn after and pushed proud
        circles = sorted(spec.circles, key=lambda c: c.radius, reverse=True)
        body_radius = circles[0].radius if circles else 0.0
        for circle in circles:
            off = Vec3(*circle.offset)
            if circle.role != "body" and off.length() > 0:
                off = off.normalized() * (body_radius + circle.radius * 0.5)  # sit proud of body
            c = Entity(model="sphere", parent=self.root, position=off,
                       scale=circle.radius * 2, color=to_color(circle.color),
                       collider="sphere", double_sided=True)
            self._circles.append(c)

    def update(self, dt):                          # gentle bob while alive
        if self.is_dead(): return
        self._t += dt
        self.root.y = self._base_y + sin(self._t * 2.0) * 0.1

    def hit(self, point):
        if self.is_dead(): return
        if self._health.hit():                     # hp -= 1; True when it reaches 0
            self._die()

    def _die(self):
        for c in self._circles:                    # each piece flies off & shrinks to nothing
            wp = c.world_position
            c.world_parent = scene
            c.world_position = wp
            direction = Vec3(uniform(-1,1), uniform(-0.3,1.0), uniform(-1,1))
            direction = direction.normalized() * uniform(2.5, 4.0)
            c.animate_position(c.world_position + direction, duration=0.6)
            c.animate_scale(0, duration=0.6)       # shrink away over 0.6 s
            c.collider = None
            destroy(c, delay=0.7)                   # gone
        destroy(self.root, delay=0.7)
        if self._death_cb: self._death_cb()         # -> reveal the red ceiling equation
```

The demon's shape data model (`DemonCircle`) was simply: `offset: (x,y,z)`, `radius: float`, `color: "#hex"`, `role: "body"|"eye"|"pupil"|"glint"|"tooth"`. In the tiny M0 demo the whole demon was just 6 spheres (1 pink body, 2 blue eyes, 3 white teeth) and death was: `for part: animate_position(pos + random_dir*3, 0.6); animate_scale(0, 0.6); destroy(delay); then equation.enabled = True; equation.animate_scale(3, 0.5)`.

**That is the entire behavior you are reproducing.** The ONLY differences for QUAKE:
- **Many more balls** (Nir's spec in §2).
- **QUAKE does not use Ursina.** QUAKE renders with **moderngl + pyglet** (custom pipeline). So you re-implement the same design with moderngl draw calls and a pure explosion-by-time function — you do NOT copy Ursina calls. The moderngl facts you need are in §4.

---

## 2. NIR'S DEMON — THE MANY-BALL SPEC (exact)

Build the demon out of MANY small spheres (NOT the old 6-sphere minimalism — Nir dislikes that):
- **~100 pink spheres** → the **body** (a dense rounded cluster that reads as a demon body).
- **~10 white spheres** → the **mouth**: **5 upper teeth + 5 lower teeth**.
- **2 bigger blue spheres** → the **eyes**; **inside each eye a smaller black sphere** (pupil); **inside each pupil a tiny white sphere** (glint). So each eye is three nested spheres, front-to-back: blue eyeball → black pupil → white glint, each smaller and pushed slightly proud of the one behind it (same "push features proud of the body" trick as DOOM).

Generate the ~100 body spheres **procedurally** (e.g. many small pink spheres jittered to fill a rounded blob volume centered on the demon's position) — do not hand-author 100 lines. The counts are the intended density; get the look. Use the DOOM ordering rule: **draw the big body spheres first, features after, features nudged outward so the opaque body never hides them.**

**Explosion:** the demon is killed on the **3rd hit** (`hp = 3`). On death, **every sphere flies off in a random direction and shrinks to nothing over ~0.6 s, then disappears** — identical to DOOM. In moderngl there is no `animate_*`; implement it as a **pure function of elapsed time since death**: give each sphere a random unit direction × random speed (2.5–4.0), then each frame `pos = start + dir*t`, `scale = radius * max(0, 1 - t/0.6)`; when `t ≥ ~0.7` the demon is fully gone.

While alive, give it the same **gentle vertical bob** (`y += sin(t*2)*0.1`).

---

## 3. THE OTHER THREE EFFECTS (all around the demon)

Per the Old Testament / locked decisions and Nir:

**A. Alcove reveal.** The final proof panel (the last station's drawing panel) is a **hidden door**. When the player lights the final panel and shoots it, the hidden door opens → the demon appears → and the small recessed **alcove** (the little room the demon was locked in) becomes **visible at that moment**. Before the demon appears the alcove must read as closed/hidden. (QUAKE already has `render_room._build_alcove()` — a 5-sided recessed box at the final pair's drawing placement — but today it is drawn every frame unconditionally. Gate it so it is revealed only once the demon has spawned, and deepen/shape it if needed so it reads as the demon's little room.)

**B. Demon appears in/just in front of the alcove.** The demon's `spawn_xyz` sits ~2.6 m out from the final panel's wall (see §4). Center the body cluster on `spawn_xyz`.

**C. Blood-red ceiling equations on the kill.** When the demon dies, **blood-red equations appear on the ceiling above each station** — the player looks up and reads that station's equation in red (for stations that have one). QUAKE already hangs `room.ceiling_equations` under the ceiling and already tints them blood-red `(1,0,0)` when `room.room_id in state.cleared`; make sure this fires on the kill and reads well above each station. Not every station has an equation — only render those that exist.

Story order the player sees: shoot panels to color them → light + shoot the **final** panel → hidden door opens, **alcove revealed + demon appears** → shoot demon **3×** → **explosion** → room cleared → **red equations on the ceiling**.

---

## 4. QUAKE INTEGRATION FACTS (moderngl reality — everything you need)

**Coordinates (law):** each room is an axis-aligned box, `dimensions_m = (W,H,D)`. X∈[−W/2,+W/2], Y∈[0,H] (Y up, floor at 0), Z∈[−D/2,+D/2]. Room-local axes parallel to map axes (no rotation). Walls: N z=+D/2 (inward −Z), S z=−D/2 (+Z), E x=+W/2 (−X), W x=−W/2 (+X).

**The renderer** is `render_room.py`. Its one public entry, called once per frame from `app.py`:
```python
def draw_room(view, room, pack, state) -> None
```
`view` is already `proj @ view` (world→clip, row-major float32; the shader transposes). It asserts GL state each frame (depth test on, LEQUAL, depth-write on, cull OFF, blend toggled per pass), builds+caches a per-room mesh, and renders walls/floor/ceiling, door jambs, the alcove, the textured panels, then the ceiling equations. **Add the demon drawing here** (or in a new `demon.py` module called from here).

**The shader** you use: `shaders.solid_program` (GLSL 330 core), uniforms: `u_mvp` (mat4), `u_tint` (vec3), `u_use_tint` (int; **2 = flat-lit solid base color** — perfect for colored spheres), `u_light_dir` (vec3), `u_ambient` (float), `u_tex` (sampler2D). Two-sided lighting. So a sphere = a small unit-sphere mesh (build one icosphere/UV-sphere on the CPU once), drawn per ball with `u_use_tint=2` and `u_tint` = the ball's color, transformed to `spawn_xyz + offset` and scaled by radius. Reuse it or author your own program (provide the GLSL if you do).

**The demon data** on each room: `room.enemy` = `EnemyRT(enemy_id: str, spawn_xyz: (x,y,z), health: int)`. Example (`lemma_2`): `spawn_xyz=(-13.73, 0.1, -11.04)` (on the floor), final pair `lemma_2.s3` whose drawing panel is on the **W** wall at center `(-16.33, 1.55, -11.04)` size `2.04×1.11`; room W,H,D = `32.66, 3.91, 25.12`. So the demon stands ~2.6 m in front of that wall. Size the body cluster ~1.0–1.4 m across so it fills that space and sits on the floor. (`health` is 3 for a 3-hit kill — DeepSeek will set that in data; the game logic already decrements HP and fires the kill on the 3rd hit.)

**Ceiling equations** on each room: `room.ceiling_equations` = list of `CeilingEqRT(eq_id, asset_id, pos_xyz, size_m)`. Example: `pos=(-1.0, 3.81, 0.0)`, `size=(1.0, 0.5)`.

**Game state** the renderer reads each frame: `state.lit` (set of lit **pair-ids**), `state.cleared` (set of cleared **room-ids**), `state.mode`, `state.current_room_id`, `state.pos`, `state.heading_rad`, `state.pitch_rad`. Whether the hidden door is open lives in `state.save.levels[level_id].rooms[room_id].hidden_door_open`.

**Events** emitted by `gameplay.step()` each frame (the frame loop in `app.py` has them, and has `dt`): `DemonSpawned(enemy_id, room_id)` (door opened → reveal alcove + show demon), `DemonHit(enemy_id, hp_remaining)`, `DemonKilled(enemy_id, room_id)` + `RoomCleared(room_id)` (killing hit → start the explosion + red ceiling). The demon's shoot/HP/kill LOGIC already exists in `gameplay.py` — you only render the results.

**Animation time:** track a per-room "time since death" (a module-level dict keyed by `room_id`, exactly like DOOM's `demon_alive` dict) and drive the explosion as a pure function of it; `app.py` provides `dt` each frame. Keep a clean split: **pure builders** (sphere positions/radii/colors; explosion transform as a pure function of `t` — unit-testable) + a **thin GL shell** (buffers/draws, guarded by `glguard.HAVE_GL` so it imports headless). All GL is headless-guarded, so tests only prove pure logic — DeepSeek verifies the look by rendering an **offscreen PNG** for Nir to eyeball. Center the body on `spawn_xyz` so the existing hit test (a small sphere around `spawn_xyz`) still lands; if the body is wider, note it and DeepSeek will widen the hit radius to match.

---

## 5. WHAT TO DELIVER (one focused pass, all code)

1. A `demon.py` module: pure builders that generate the demon's sphere set (the ~100 pink body via procedural jittered fill, 10 teeth, 2 layered eyes with pupils+glints), a unit-sphere mesh builder, the pure `explosion_transform(t)` (fly-out + shrink), and a thin moderngl shell to draw it (reusing `solid_program`, `u_use_tint=2`).
2. Edits to `render_room.py` (and `app.py` if needed) to: reveal the alcove on `DemonSpawned`, draw the demon while spawned+alive (with the bob), run the explosion on `DemonKilled`, and ensure the red ceiling equations show on clear. Thread the per-room death-clock from the frame loop.
3. If you add a shader, the full GLSL.
4. A short list of unit tests for the pure builders (deterministic sphere counts by role, explosion monotonic + fully shrunk by ~0.7 s).

Write it now. It's the DOOM demon with many more balls, in moderngl. 🩸👹
