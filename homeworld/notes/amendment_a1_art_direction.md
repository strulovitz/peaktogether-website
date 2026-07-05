AMENDMENT A1 — ART DIRECTION (owner decision, July 2026)

The owner has ruled: glowing wireframe ships FAIL Bible Law 1 (gaming
first). Amended visual identity, binding on all future work:

1. SHIPS are solid, opaque, lit triangle meshes: per-pixel Blinn-Phong
   (key + fill + rim + specular), flat-shaded paneled hulls with
   per-face color variation, emissive engine nozzles/windows feeding
   bloom. Hundreds to thousands of triangles per class. Never
   see-through. Meshes come from content/shipwright.py (procedural)
   today; OBJ import from Blender is a sanctioned future path.
2. THE MATH LAYER (arrows, grids, spans, ghosts, trails, labels)
   remains glowing holographic vector graphics, drawn additively OVER
   the solid world with depth testing (occluded correctly by hulls).
3. The render pipeline is: solid pass (depth write) -> glow pass
   (depth test, no write) -> bloom -> crisp overlay.
4. "It must look like a game a gamer would choose" outranks any
   aesthetic theory in any design document. The owner is the arbiter.
