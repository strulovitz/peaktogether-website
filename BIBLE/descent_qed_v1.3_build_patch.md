One function changes, nothing else. DeepSeek: replace _build() in corridor.py with the following, byte for byte — no other edits anywhere:

def _build():
    pos, yaw = np.zeros(3), 0.0
    prev = None              # (f, w, h) of previous segment, for collars
    prev_f, prev_L = None, 0.0
    for idx, (sid, kind, w, h, L, pitch, turn) in enumerate(SEGMENTS):
        if turn != 0:
            # PIVOT RULE (v1.3): a turn rotates around the CENTER of the
            # preceding elbow, not its end face. Retreat half its length;
            # the corner then becomes two tunnels sharing one exact cube:
            # the new tunnel's back face sits flush on the elbow's side
            # wall, its side wall sits flush on the elbow's far face.
            pos = pos - prev_f * (prev_L / 2.0)
        yaw += turn
        f, r, u = _frame(yaw, pitch)
        ext = 0.0 if idx == 0 else (TURN_EXTEND if turn else BACK_EXTEND)
        start, end = pos - f * ext, pos + f * L
        SEG_BOUNDS.append((pos.copy(), f, r, u, ext, L, w / 2.0, h / 2.0))
        cs, ce, quads = _box(start, end, r, u, w, h)
        wall_quads.extend(quads)
        for i in range(4):
            edge_lines.append((cs[i], ce[i]))
            edge_lines.append((cs[i], cs[(i + 1) % 4]))
            edge_lines.append((ce[i], ce[(i + 1) % 4]))
        if idx == 0:
            cap_quads.append(tuple(cs))
            SIGN_SLOTS[sid] = pos + f * 1.0
        if idx == len(SEGMENTS) - 1:
            # Cap ONLY the true dead end. A pre-turn cap is no longer
            # needed: the corner's far face is covered by the new
            # tunnel's wall (capping it too would double-layer the
            # plane and show as a darker patch).
            cap_quads.append(tuple(ce))
        if kind == "station":
            ROBOT_SLOTS[sid] = pos + f * (L / 2.0)
            _striped_frame(pos, r, u, w, h, CHEVRON_T)
            _striped_frame(end, r, u, w, h, CHEVRON_T)
        if kind == "gallery":
            SIGN_SLOTS[sid] = end - f * 2.0
        if prev is not None:
            pf, pw, ph = prev
            if np.allclose(pf, f) and (pw, ph) != (w, h):
                _collar(pos, r, u, min(pw, w), min(ph, h), max(pw, w), max(ph, h))
        prev, prev_f, prev_L = (f, w, h), f, L
        pos = end
