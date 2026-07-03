import math
import demon


def test_sphere_counts_by_role():
    sph = demon.build_demon_spheres(n_body=100, seed=1)
    roles = {}
    for s in sph:
        roles[s.role] = roles.get(s.role, 0) + 1
    assert roles["body"] == 100
    assert roles["tooth"] == 10          # 5 upper + 5 lower
    assert roles["eye"] == 2
    assert roles["pupil"] == 2
    assert roles["glint"] == 2
    assert len(sph) == 116


def test_body_drawn_before_features():
    # after the big-first body sort + feature append, the first 100 are body
    sph = demon.build_demon_spheres(n_body=100, seed=1)
    assert all(s.role == "body" for s in sph[:100])
    assert all(s.role != "body" for s in sph[100:])


def test_body_sorted_big_first():
    sph = demon.build_demon_spheres(n_body=100, seed=1)
    body = [s.radius for s in sph if s.role == "body"]
    assert body == sorted(body, reverse=True)


def test_features_are_proud_of_body_front():
    # eyes/pupils/glints/teeth sit toward +Z (the face) and each nested layer
    # is more proud than the last
    sph = demon.build_demon_spheres(seed=1)
    eyes = [s for s in sph if s.role == "eye"]
    pupils = [s for s in sph if s.role == "pupil"]
    glints = [s for s in sph if s.role == "glint"]
    # pupil in front of eye, glint in front of pupil (compare same side)
    left_eye = min(eyes, key=lambda s: s.offset[0])
    left_pupil = min(pupils, key=lambda s: s.offset[0])
    left_glint = min(glints, key=lambda s: s.offset[0])
    assert left_pupil.offset[2] > left_eye.offset[2]
    assert left_glint.offset[2] > left_pupil.offset[2]
    # nested spheres shrink
    assert left_pupil.radius < left_eye.radius
    assert left_glint.radius < left_pupil.radius


def test_determinism():
    a = demon.build_demon_spheres(seed=99)
    b = demon.build_demon_spheres(seed=99)
    assert [ (s.offset, s.radius, s.role) for s in a ] == \
           [ (s.offset, s.radius, s.role) for s in b ]


def test_bob_offset_range():
    for t in [0.0, 0.5, 1.0, 3.14, 10.0]:
        assert -0.1001 <= demon.bob_offset(t) <= 0.1001
    # non-trivial motion
    assert abs(demon.bob_offset(math.pi / 4)) > 0.0


def test_seed_explosion_unit_dirs_and_speed():
    sph = demon.build_demon_spheres(seed=1)
    demon.seed_explosion(sph, seed=7)
    dys = []
    for s in sph:
        dx, dy, dz = s.fly_dir
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        assert abs(length - 1.0) < 1e-6           # unit direction
        assert 2.5 <= s.fly_speed <= 4.0          # DOOM speed range
        assert -1.0 - 1e-9 <= dy <= 1.0 + 1e-9    # valid (post-normalize) range
        dys.append(dy)
    # dy is sampled in [-0.3, 1.0] before normalizing -> the burst biases UPWARD
    assert (sum(dys) / len(dys)) > 0.0


def test_explosion_monotonic_flyout_and_shrink():
    s = demon.DemonSphere(offset=(0,1,0), radius=0.1,
                          color=(1,0,0), role="body",
                          fly_dir=(0,1,0), fly_speed=3.0)
    prev_dist = -1.0
    prev_scale = 2.0
    for t in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        pos, scale = demon.explosion_transform(s, t)
        dist = pos[1] - s.offset[1]              # flew along +Y
        assert dist >= prev_dist                 # monotonic fly-out
        assert scale <= prev_scale               # monotonic shrink
        prev_dist, prev_scale = dist, scale


def test_explosion_fully_shrunk_by_end():
    s = demon.DemonSphere(offset=(0,0,0), radius=0.2,
                          color=(1,1,1), role="body",
                          fly_dir=(1,0,0), fly_speed=3.0)
    _, scale_at_dur = demon.explosion_transform(s, demon.EXPLODE_DUR)
    assert scale_at_dur == 0.0
    _, scale_past = demon.explosion_transform(s, 0.65)
    assert scale_past == 0.0
    assert demon.is_gone(0.7) is True
    assert demon.is_gone(0.6) is False


def test_unit_sphere_mesh_shape():
    verts, idx = demon.build_unit_sphere_mesh(lat_bands=6, lon_bands=8)
    assert verts.shape[1] == 6                   # pos + normal
    # every vertex lies on the unit sphere (position part normalized)
    import numpy as np
    p = verts[:, :3]
    r = np.linalg.norm(p, axis=1)
    assert np.allclose(r, 1.0, atol=1e-5)
    assert idx.ndim == 1 and len(idx) % 3 == 0
