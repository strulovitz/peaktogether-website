# 🔧 DEEPSEEK SELF-PROMPT — Hierarchical Force-Directed Layout

> Replace `networkx.spring_layout` (simultaneous, finds flattest arrangement) with
> hierarchical placement in `layout_force.py`. DeepSeek implements directly (no parent).
> Nir's design: planets freeze first, asteroids are pulled to them — natural crossings.

---

## §1 — THE PROBLEM

Current `place_nodes()` at `quake/map/layout_force.py:77` calls `nx.spring_layout()` on
the ENTIRE graph at once. spring_layout is a global energy minimizer — it naturally finds
the flattest, least-crossing embedding. On Parent 7's 20-node graph: **0 crossings**.

0 crossings = Doom, not Quake. We need bridges/underpasses.

The core insight (Nir): "like a solar system — big planets are already there, if a small
asteroid comes, he does not move them all, they move him." This is a real published
technique: **hierarchical (incremental) force-directed layout**.

---

## §2 — THE ALGORITHM (Nir's Design)

### Phase 1: Place the Planets
- Identify "planet" nodes: importance ≥ `planet_importance` (default 4) OR
  degree (undirected, from edges) ≥ `planet_degree` (default 3)
- Build subgraph of only planets + edges between them
- Run `spring_layout` on just this subgraph → planet positions
- Planets now have FIXED positions

### Phase 2: Add Asteroids One at a Time
- Remaining nodes are "asteroids"
- Sort asteroids by "connectedness": count how many ALREADY-PLACED nodes
  (planets + previously-placed asteroids) they connect to. Most-connected first.
- For each asteroid in order:
  1. Build a tiny subgraph: the asteroid + ALL its already-placed neighbors
     + edges connecting them
  2. Run `spring_layout` on this subgraph with neighbors FIXED in place.
     Use `networkx.spring_layout(G, pos=initial_pos, fixed=fixed_nodes)`.
     Only the asteroid moves; neighbors are pinned.
  3. Record the asteroid's resulting position. Now it's "placed."
  4. Next asteroid.

### Phase 3: Normalize (unchanged)
- Scale the full result via existing `_normalize_positions()`.
- All nodes get the same scale transform. Planet spread is preserved.

### Key Properties
- Asteroids don't pull planets — planets NEVER move after Phase 1
- Asteroids don't affect each other — placed sequentially, earlier ones frozen
- Edges from different asteroids to overlapping planet-subsets naturally criss-cross
  because planets are spread out and frozen
- No "inventing edges" or "graph redesign" needed — Parent 7's 20-node graph works as-is
- Deterministic: same (graph, seed, cfg) → same positions (sorted order for planets,
  sorted order for asteroids)

---

## §3 — EXACT IMPLEMENTATION PLAN

### 3.1 — Add Config Fields to `LayoutConfig`

In `quake/map/layout_force.py`, add to `LayoutConfig`:

```python
# Planet threshold: nodes with importance >= this OR degree >= planet_degree
# are placed in Phase 1 and frozen for Phase 2.
planet_importance: int = 4       # importance 4-5 = planet
planet_degree: int = 3           # degree >= 3 = planet (even if importance is lower)
```

These are defaulted (backward-compat: all nodes meet low thresholds → all become
planets → equivalent to old behavior, since all placed simultaneously).

### 3.2 — Compute Node Degrees

Add a helper:

```python
def _compute_degrees(graph: ConceptGraph) -> dict[NodeId, int]:
    """Undirected degree for each node (count of incident edges)."""
    deg: dict[NodeId, int] = {n.id: 0 for n in graph.nodes}
    for e in graph.edges:
        deg[e.source] += 1
        deg[e.target] += 1
    return deg
```

### 3.3 — Rewrite `place_nodes()`

#### Step 1: Classify nodes
```python
sorted_node_ids = sorted(n.id for n in graph.nodes)
sorted_edges = sorted(((e.source, e.target) for e in graph.edges),
                       key=lambda st: (st[0], st[1]))
n = len(sorted_node_ids)

# Degenerate guards (unchanged)
if n == 0: return {}
if n == 1: return {sorted_node_ids[0]: (0.0, 0.0)}

# Compute degrees
degrees = _compute_degrees(graph)
node_importance = {n.id: n.importance for n in graph.nodes}

# Classify planets vs asteroids
planet_ids = sorted(
    [nid for nid in sorted_node_ids
     if node_importance[nid] >= cfg.planet_importance
     or degrees[nid] >= cfg.planet_degree]
)
asteroid_ids = sorted([nid for nid in sorted_node_ids if nid not in planet_ids])
```

EDGE CASE: If `planet_ids` is empty (all nodes are asteroids), promote the
highest-degree node to planet. If still none (0 edges), all are planets
(fallback to old behavior).

EDGE CASE: If `planet_ids` is all nodes (no asteroids), skip Phase 2 entirely.

#### Step 2: Phase 1 — Place planets
```python
G_planets = nx.Graph()
for nid in planet_ids:
    G_planets.add_node(nid)
for s, t in sorted_edges:
    if s in planet_ids and t in planet_ids:
        G_planets.add_edge(s, t)

# Use the SAME k formula (k_factor / sqrt(N)) for planets.
# If planet count < 2, place the single planet at origin.
if len(planet_ids) < 2:
    planet_pos = {nid: (0.0, 0.0) for nid in planet_ids}
else:
    k = cfg.k_factor / math.sqrt(len(planet_ids))
    planet_pos = nx.spring_layout(
        G_planets, k=k, seed=seed, iterations=cfg.iterations
    )
    planet_pos = {i: (float(p[0]), float(p[1])) for i, p in planet_pos.items()}
```

#### Step 3: Phase 2 — Place asteroids sequentially
```python
# Build adjacency lookup for fast neighbor queries
neighbors: dict[NodeId, set[NodeId]] = {nid: set() for nid in sorted_node_ids}
for s, t in sorted_edges:
    neighbors[s].add(t)
    neighbors[t].add(s)

# Sort asteroids by "connectedness" to already-placed nodes
# (planets are already placed, so connectedness = #planet neighbors)
def _connectedness(nid: str) -> int:
    return len(neighbors[nid] & set(planet_ids))

# Sort: most connected first, then by node_id for determinism
asteroid_order = sorted(asteroid_ids,
                        key=lambda nid: (-_connectedness(nid), nid))

# Place asteroids
all_pos = dict(planet_pos)  # starts with planets
for nid in asteroid_order:
    placed_neighbors = [nb for nb in neighbors[nid] if nb in all_pos]

    if len(placed_neighbors) == 0:
        # No placed neighbors → place at origin
        all_pos[nid] = (0.0, 0.0)
        continue

    if len(placed_neighbors) == 1:
        # One placed neighbor → place nearby (small random offset
        # for determinism, use seed-based offset)
        rng = random.Random(seed + sorted_node_ids.index(nid))
        angle = rng.uniform(0, 2 * math.pi)
        offset = cfg.scale_m * 0.05  # 5% of world scale
        nb_x, nb_y = all_pos[placed_neighbors[0]]
        all_pos[nid] = (nb_x + offset * math.cos(angle),
                        nb_y + offset * math.sin(angle))
        continue

    # Multiple placed neighbors → spring_layout with them fixed
    G_local = nx.Graph()
    G_local.add_node(nid)
    for nb in placed_neighbors:
        G_local.add_node(nb)
        # Check if edge exists between nid and nb
        if (nid, nb) in sorted_edges or (nb, nid) in sorted_edges:
            G_local.add_edge(nid, nb)

    # Initialize: neighbors at their known positions, asteroid starts at centroid
    init_pos = {nb: all_pos[nb] for nb in placed_neighbors}
    cx = sum(p[0] for p in init_pos.values()) / len(placed_neighbors)
    cy = sum(p[1] for p in init_pos.values()) / len(placed_neighbors)
    init_pos[nid] = (cx, cy)

    fixed = {nb: True for nb in placed_neighbors}
    fixed[nid] = False

    # Use a local k for this tiny subgraph
    local_k = cfg.k_factor / math.sqrt(len(placed_neighbors) + 1)

    result = nx.spring_layout(
        G_local, pos=init_pos, fixed=fixed,
        k=local_k, seed=seed, iterations=cfg.iterations
    )
    all_pos[nid] = (float(result[nid][0]), float(result[nid][1]))
```

IMPORTANT: `nx.spring_layout` with `fixed` parameter requires networkx >= 2.6.
Check if installed version supports it. If `fixed` kwarg is not supported:
fall back to manually running a simplified spring simulation (only the
unfixed node moves) — but networkx 2.6+ is very likely installed.

#### Step 4: Normalize (unchanged)
```python
if cfg.normalize_spread:
    scaled = _normalize_positions(all_pos, sorted_node_ids, cfg)
else:
    scaled = {
        i: (all_pos[i][0] * cfg.scale_m, all_pos[i][1] * cfg.scale_m)
        for i in sorted_node_ids
    }

return {i: (scaled[i][0], scaled[i][1]) for i in sorted_node_ids}
```

### 3.4 — Import `random`
Add `import random` at the top of the file (needed for single-neighbor case).

---

## §4 — WHAT MUST NOT CHANGE

- **`LayoutConfig` existing fields:** `scale_m`, `iterations`, `k_factor`,
  `normalize_spread`, `min_extent_m` — all preserved, all still work.
- **`_normalize_positions()`:** untouched.
- **Function signature:** `place_nodes(graph, seed, cfg)` → unchanged.
- **Return type:** `dict[NodeId, Vec2]` — unchanged.
- **All imports and module dependencies:** unchanged (add only `random`).
- **`layout_height.py`, `level_maker.py`, `raw_models.py`:** ZERO TOUCHES.
- **`extra="forbid"` on `LayoutConfig`:** new fields MUST be defaulted so
  existing config literals still validate.

---

## §5 — TEST PLAN

### 5.1 — Existing tests must stay green (358/358)
Run: `python -m pytest quake/tests/ -v`

Key tests that exercise `place_nodes`:
- `tests/test_layout_force.py` (107 lines — small known graphs)
- `tests/test_layout_scale.py` (50 new scale tests from Parent 8)
- `tests/test_layout_height.py` (crossing detection tests)
- `tests/test_level_maker.py` (end-to-end: graph → floorplan)
- `tests/test_app.py` (smoke: golden pack)



### 5.2 — Backward compatibility
With default config (`planet_importance=4, planet_degree=3`), a small graph
(e.g., Golden Pack: 3 nodes, all importance 3) should produce identical or
near-identical output to the old algorithm. The Golden Pack has importance
values of 3 for its rooms — so they'd all be asteroids if planet_importance=4.
BUT with planet_degree=3, check if any nodes have degree ≥3.

Actually: the Golden Pack has 3 nodes with degrees: r_a=2, r_b=2, r_c=2.
So all are asteroids, no planets → fallback promotes the highest-degree to
planet → behavior diverges from old. THIS IS OK for the smoke test — the
app doesn't care about exact positions, just that the floorplan validates.

If the smoke test breaks: verify floorplan still validates (Gate 1-3 checks),
update test_app.py expected values minimally.

### 5.3 — Parent 7's 20-node graph (THE REAL TEST)
After implementation:
```python
# Load Parent 7's concept_graph.json
# Run place_nodes with default config
# Build floorplan
# Count crossings
```

**Target: 5–15 genuine crossings** (not 0, not 191 pathological).

If crossings < 5: lower `planet_importance` to 3 (more planets → more spread).
If crossings > 30: raise `planet_importance` to 5 (fewer planets).

### 5.4 — New targeted test (optional, if time)
```python
def test_hierarchical_produces_crossings():
    """A 6-node graph with 2 planets (4 edges each) and 2 asteroids
    connecting to both planets should produce at least 1 crossing."""
    # Build ConceptGraph with:
    #   planet_A (importance=5) ↔ planet_B (importance=5)
    #   asteroid_1 → planet_A, asteroid_1 → planet_B
    #   asteroid_2 → planet_A, asteroid_2 → planet_B
    # With planets frozen apart, edges asteroid1-A, asteroid1-B,
    # asteroid2-A, asteroid2-B must cross.
    ...
```

---

## §6 — ACCEPTANCE GATES

1. **358/358 tests green** (zero regressions)
2. **Parent 7's graph produces > 0 crossings** with default config
3. **`ConceptGraph` → places everywhere** (no orphan nodes with None coords)
4. **Deterministic** (same seed, same output, repeated 5x)
5. **Scale-free** (works on 3-node golden pack, 20-node Parent 7 graph,
   50-node synthetic graph from test_layout_scale)
6. **Config tunable** (changing `planet_importance` changes planet/asteroid split;
   lowering it increases crossings, raising it reduces them)

---

## §7 — NIR'S KNOB

After implementation, the PRIMARY knob Nir uses to tune crossing count:

- **`planet_importance` (default 4):** Lower = more planets = more spread = fewer
  crossings but wider map. Higher = fewer planets = tighter clusters = more
  crossings but smaller map. Try 3 and 5.

- **`planet_degree` (default 3):** Lower = more planets (hubs at degree 3+).
  Higher = fewer planets (only degree 4+ are planets).

- **`k_factor` (already exists, default 1.0):** >1 spreads planets more (fewer
  crossings, but may help visibility). <1 tightens planets (more crossings).

Nir doesn't need to understand any of this. DeepSeek runs the experiments,
reports "crossings with setting X = 5, with Y = 12, with Z = 3," and lets
Nir pick which looks right in the map viewer.

---

## §8 — DON'T-DO LIST

- Do NOT touch `layout_height.py`, `level_maker.py`, `raw_models.py`.
- Do NOT change any frozen pydantic model.
- Do NOT change the `place_nodes()` return type or signature.
- Do NOT remove existing config fields.
- Do NOT add fields without defaults (must be backward-compat).
- Do NOT use random without a seed (determinism is a hard requirement).
- Do NOT launch a parent for this — DeepSeek owns it.
- Do NOT commit until all 358 tests pass AND Parent 7's graph has crossings.
