# CHILD PROMPT — Fix lemma_2 Asymptote pen/path name clash

> **⚠️ YOU WROTE lemma_2.room.** You already know the room, its colors, and its geometry. This is a bug in the build tool triggered by your color/geometry naming. Fix it in the shared builder so ALL rooms are safe, not just lemma_2.

## THE BUG

lemma_2's figure fails to compile in Asymptote with:
```
draw(curve, on3 ? curve : BLACK);
          ^
types in conditional expression do not match
```

`curve` is used as BOTH a path variable name AND a pen variable name in the same expression. Asymptote can't tell them apart and rejects the type mismatch.

## ROOT CAUSE

In `build/room_from_spec.py`:

- Line 857: pens are declared as `pen {c.name} = rgb(...)` — where `{c.name}` comes directly from the child's color name (e.g., `curve`, `base`, `insc`, `circ`, `excess`)

- Line 980: geometry paths are named `{g.name}` — which comes from the child's panel geo op names. If a child names a polyline `curve` (which is natural and correct), the path variable `curve` collides with the pen `curve`.

- `_draw_geom()` (lines 1262-1287) emits `draw({nm}, {on} ? {pen} : BLACK)` where both `{nm}` and `{pen}` can be the same string.

## THE FIX (EXACT)

**Step 1 — Prefix all pen names** at line 857:

Change:
```python
L.append(f"pen {c.name} = {_rgb(c.hex)} + linewidth(1.6pt);")
```
To:
```python
L.append(f"pen _p_{c.name} = {_rgb(c.hex)} + linewidth(1.6pt);")
```

**Step 2 — Update all pen references** in the file. Search for every `{pen}` and `{color}` that appears inside f-string Asymptote code, and change them to `_p_{pen}` or `_p_{color}` — BUT only when the value is not `"BLACK"`. `BLACK` is a separate pen that stays as-is.

Specifically, these locations need updating:

1. `_draw_geom()` (lines ~1269, 1277, 1278, 1284, 1286, 1287):
   - Where `{pen}` or `{color}` appears in draw/filldraw/markangle/dot calls
   - Change `{pen}` → `_p_{pen}` (when pen != "BLACK")
   - Easiest: compute a variable `p = f"_p_{pen}" if pen != "BLACK" else "BLACK"` once at the top of `_draw_geom` and use `{p}` everywhere

2. `_emit_ink_pass()` (lines ~1220-1222, 1252-1254, 1256-1258):
   - In label calls: `{on} ? {pen} : BLACK` → `{on} ? _p_{pen} : BLACK`
   - Same drill: compute `p = f"_p_{pen}" if pen != "BLACK" else "BLACK"`

3. `_emit_stabilo_underlay()` (lines ~1182-1207):
   - The `by[(st.n, "geo", g.name)]` entries are stabilo pen names — these are ALREADY unique (suffixed with step/heart info). Leave them alone.
   - But the TERM and PHRASE stabilo pens at lines ~1201, 1206 use `{pen}` from the `by` dict — these are also already unique stabilo pen names, not color names. Leave them alone.

**Actually — simpler approach:** Just create a helper function:
```python
def _pen_ref(name: str) -> str:
    return f"_p_{name}" if name != "BLACK" else "BLACK"
```
And use `_pen_ref(pen)` instead of bare `{pen}` in all the draw/label Asymptote f-strings listed above.

## VERIFICATION

After the fix, compile lemma_2's figure:
```
cd quake/levels/principia_bk1_inverse_square/figures
asy -u "highlight=1" lemma_2.f1.asy
```

Should produce `lemma_2.f1.0001.png` without errors. Test with highlight=1,2,3 and highlight=-1 (OFF).

## FILE TO MODIFY

`quake/build/room_from_spec.py` — ONLY this file. No other files change.

## OUTPUT

Return the COMPLETE modified file as a single fenced code block.
