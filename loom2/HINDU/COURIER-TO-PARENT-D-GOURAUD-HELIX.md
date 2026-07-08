# COURIER TO PARENT D (Fable) — MAKE THE HELIX GOURAUD (July 8, 2026)

> From Nir, couriered by DeepSeek. Paste this whole message into the SAME Parent D chat.

---

Hi Fable — one correction before we move on, and it's an important one. 🙏

**Nir has an IRON RULE for all his games: NO FLAT SHADING, EVER. Everything is
GOURAUD shaded.** The terrain you just delivered is perfect on this (per-vertex
Lambert × hard per-fragment bands — beautiful). But the **helix totem in
`totem.py` is flat-colored** — one `u_color` per draw on the shared `flat`
program, no per-vertex lighting. That breaks the rule.

This is **not** a "future taste option" and it should never have been parked —
that was DeepSeek's mistake, and Nir rightly called it out. Please treat it as a
required fix now.

**Please redeliver `graphics/totem.py` with a GOURAUD-shaded helix**, matching the
lighting language of the rest of the game (same spirit as your terrain: fixed
directional sun `_LIGHT_DIR = (0.45, 0.28, 0.85)`, ambient floor `_AMBIENT = 0.38`,
per-vertex Lambert, smoothly interpolated). Keep everything else you did — the
breathing emissive pulse (A6), the dark edge lines, the DRAPED rings/circle/arm
(A7 `height_fn`), the A1 arm, A5 calm rings, the breath clock. Only the helix
model's shading changes from flat → Gouraud.

**You have Nir's full blessing to change the contract / add whatever you need** to
do this cleanly. Some notes/facts to help (take with a grain of salt, you're the
better coder):

- The shared `flat` program is literally one flat color per call:
  - `flat.vert`: `uniform mat4 u_mvp; in vec3 in_pos;`
  - `flat.frag`: `uniform vec4 u_color; out vec4 f_color; // f_color = u_color;`
  So it cannot express per-vertex lighting as-is. Cleanest options (your call):
  1. **Add a new owned shader pair** for the totem (e.g. `totem.vert`/`totem.frag`),
     just like you own `terrain.vert`/`terrain.frag`. You'd bake a per-vertex
     `in_light` (Lambert from the helix ribbon normals) and multiply the breathing
     emissive gold by it — true Gouraud, and it still feeds bloom for the A6 glow.
     If you add a shader stem, tell DeepSeek the exact filenames + uniform/attribute
     interface so he can register it in `renderer.REQUIRED_SHADERS` and drop the
     files in `data/shaders/`.
  2. Or bake per-vertex lit colors into a vertex-color attribute and use a small
     `vec3 in_color` program. Whatever you judge cleanest.
- The helix ribbon has well-defined normals (it's a parametric coil), so real
  per-vertex Lambert is straightforward.
- If you add/rename a shader, DeepSeek will overwrite placeholders and register it;
  just be explicit about names + interface (uniform names, attribute names/order).
- Please raise a `# CONTRACT-ISSUE` note documenting whatever contract/shader change
  you make, so DeepSeek can update scripture + the renderer's shader list.

Everything else about your delivery is great and stays. Just make the little helix
breathe **in Gouraud**. Thank you!! 🧿🎻✨

— Nir (via DeepSeek)
