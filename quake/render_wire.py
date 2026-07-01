"""render_wire.py — QUAKE Mode A wireframe corridor renderer (FULL look).
PURE CORE: build_wire_mesh / hex_to_rgb / _flatten_segments — unchanged, zero GL.
THIN SHELL: render_mode_a (offscreen scene -> bright -> blur -> composite to screen).
Thick camera-facing line-quads (GS, CPU-billboard fallback), distance-dim white->grey
(never black), additive bloom glow.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from contracts import Floorplan, Hex, GameState, ViewMatrix

WIRE_BASE = (1.0, 1.0, 1.0)
RING_SEGMENTS = 48

# ---- tuning (NDC half-thickness; dimming distances in world metres) ----
LINE_HALF_PX = 0.0025      # half-thickness in NDC-Y (holds up at distance)
DIM_NEAR_M   = 8.0         # full white within this view distance
DIM_FAR_M    = 220.0       # reaches grey floor by here
GREY_FLOOR   = 0.22        # never pure black
BLOOM_THRESHOLD = 0.55
BLOOM_GAIN   = 0.9
BLOOM_DIV    = 2           # half-res blur

# ---------------- PURE CORE (verbatim-kept) ----------------
@dataclass
class WireMesh:
    line_segments: np.ndarray
    seg_colors: np.ndarray
    ring_segments: np.ndarray
    ring_colors: np.ndarray

def hex_to_rgb(h: Hex):
    s = h.lstrip("#")
    if len(s) != 6:
        raise ValueError(f"hex_to_rgb expects '#rrggbb', got {h!r}")
    return (int(s[0:2],16)/255.0, int(s[2:4],16)/255.0, int(s[4:6],16)/255.0)

def build_wire_mesh(fp: Floorplan) -> WireMesh:
    from corridor_height import height_at_vertex
    seg_list=[]; seg_col_list=[]; base=(1.0,1.0,1.0)
    rooms_list=list(fp.rooms)
    for cor in fp.corridors:
        pts=cor.path_xz
        for n in range(len(pts)-1):
            ay=height_at_vertex(cor, n, rooms_list)
            by=height_at_vertex(cor, n+1, rooms_list)
            ax,az=float(pts[n][0]),float(pts[n][1])
            bx,bz=float(pts[n+1][0]),float(pts[n+1][1])
            seg_list.append(np.array([[ax,ay,az],[bx,by,bz]],dtype=np.float32)); seg_col_list.append(base)
    line_segments=(np.stack(seg_list,0).astype(np.float32) if seg_list else np.zeros((0,2,3),np.float32))
    seg_colors=np.array(seg_col_list,np.float32) if seg_col_list else np.zeros((0,3),np.float32)
    ring_list=[]; ring_col_list=[]
    angles=(2.0*np.pi)*(np.arange(RING_SEGMENTS,dtype=np.float64)/float(RING_SEGMENTS))
    next_angles=(2.0*np.pi)*((np.arange(RING_SEGMENTS,dtype=np.float64)+1.0)/float(RING_SEGMENTS))
    for room in fp.rooms:
        cx,cz=float(room.map_xz[0]),float(room.map_xz[1]); r=float(room.map_radius_m)
        y=float(room.socket_y); rgb=hex_to_rgb(room.map_color)
        for k in range(RING_SEGMENTS):
            t0,t1=angles[k],next_angles[k]
            ring_list.append(np.array(
                [[cx+r*np.cos(t0),y,cz+r*np.sin(t0)],
                 [cx+r*np.cos(t1),y,cz+r*np.sin(t1)]],dtype=np.float32))
            ring_col_list.append(rgb)
    ring_segments=(np.stack(ring_list,0).astype(np.float32) if ring_list else np.zeros((0,2,3),np.float32))
    ring_colors=np.array(ring_col_list,np.float32) if ring_col_list else np.zeros((0,3),np.float32)
    return WireMesh(line_segments,seg_colors,ring_segments,ring_colors)

def _flatten_segments(segments, colors):
    n=segments.shape[0]
    if n==0: return np.zeros((0,3),np.float32), np.zeros((0,3),np.float32)
    pos=segments.reshape(-1,3).astype(np.float32)
    col=np.repeat(colors,2,axis=0).astype(np.float32)
    return pos,col

# ---------------- THIN GL SHELL ----------------
try:
    from glguard import HAVE_GL
except Exception:
    HAVE_GL = False

_GL_CACHE: dict = {}        # per-floorplan mesh/VAOs
_FBO_CACHE: dict = {}       # per-(w,h) framebuffers + blit VAO
_USE_GS = None              # tri-state: None=untested, True/False

def _mvp_bytes(view, proj):
    mvp = np.asarray(proj, np.float32) @ np.asarray(view, np.float32)   # world->clip
    return np.ascontiguousarray(mvp.T, np.float32).tobytes()           # transpose-on-upload

def _build_fbos(ctx, w, h):
    key=(w,h)
    res=_FBO_CACHE.get(key)
    if res is not None: return res
    import moderngl
    bw,bh=max(w//BLOOM_DIV,1),max(h//BLOOM_DIV,1)
    scene_tex=ctx.texture((w,h),4); scene_tex.repeat_x=False; scene_tex.repeat_y=False
    scene_depth=ctx.depth_renderbuffer((w,h))
    scene_fbo=ctx.framebuffer(color_attachments=[scene_tex],depth_attachment=scene_depth)
    bright_tex=ctx.texture((bw,bh),4); bright_tex.repeat_x=False; bright_tex.repeat_y=False
    bright_fbo=ctx.framebuffer(color_attachments=[bright_tex])
    blurA_tex=ctx.texture((bw,bh),4); blurA_tex.repeat_x=False; blurA_tex.repeat_y=False
    blurA_fbo=ctx.framebuffer(color_attachments=[blurA_tex])
    blurB_tex=ctx.texture((bw,bh),4); blurB_tex.repeat_x=False; blurB_tex.repeat_y=False
    blurB_fbo=ctx.framebuffer(color_attachments=[blurB_tex])
    # fullscreen NDC quad (two tris): pos.xy, uv
    quad=np.array([
        -1,-1, 0,0,   1,-1, 1,0,   1,1, 1,1,
        -1,-1, 0,0,   1,1, 1,1,  -1,1, 0,1],dtype=np.float32)
    quad_vbo=ctx.buffer(quad.tobytes())
    from shaders import bright_program, blur_program, composite_program
    bright_p=bright_program(ctx); blur_p=blur_program(ctx); comp_p=composite_program(ctx)
    def _vao(prog): return ctx.vertex_array(prog,[(quad_vbo,'2f 2f','in_pos','in_uv')])
    res=dict(scene_fbo=scene_fbo,scene_tex=scene_tex,
             bright_fbo=bright_fbo,bright_tex=bright_tex,
             blurA_fbo=blurA_fbo,blurA_tex=blurA_tex,
             blurB_fbo=blurB_fbo,blurB_tex=blurB_tex,
             bright_p=bright_p,blur_p=blur_p,comp_p=comp_p,
             bright_vao=_vao(bright_p),blurA_vao=_vao(blur_p),
             blurB_vao=_vao(blur_p),comp_vao=_vao(comp_p),
             bw=bw,bh=bh)
    _FBO_CACHE[key]=res
    return res

def _get_wire_resources(ctx, fp):
    global _USE_GS
    key=getattr(fp,"level_id",None) or id(fp)
    res=_GL_CACHE.get(key)
    if res is not None: return res
    import moderngl
    from shaders import wire_quad_program, wire_quad_cpu_program
    prog=None
    if _USE_GS in (None, True):
        try:
            prog=wire_quad_program(ctx)          # GS path
            _USE_GS=True
        except Exception:
            prog=None; _USE_GS=False
    if prog is None:
        prog=wire_quad_cpu_program(ctx)          # CPU-billboard fallback
        _USE_GS=False
    mesh=build_wire_mesh(fp)
    seg_pos,seg_col=_flatten_segments(mesh.line_segments,mesh.seg_colors)
    ring_pos,ring_col=_flatten_segments(mesh.ring_segments,mesh.ring_colors)
    pos=np.concatenate([seg_pos,ring_pos],0) if (seg_pos.shape[0]+ring_pos.shape[0]) else np.zeros((0,3),np.float32)
    col=np.concatenate([seg_col,ring_col],0) if pos.shape[0] else np.zeros((0,3),np.float32)
    res={"prog":prog,"vao":None}
    if pos.shape[0]>0:
        if _USE_GS:
            vbo_p=ctx.buffer(pos.tobytes()); vbo_c=ctx.buffer(col.tobytes())
            res["vao"]=ctx.vertex_array(prog,[(vbo_p,'3f','in_pos'),(vbo_c,'3f','in_color')],mode=moderngl.LINES)
        else:
            # CPU billboards need camera right/up per frame -> store raw line endpoints, expand at draw
            res["raw_pos"]=pos.reshape(-1,2,3) if pos.shape[0]%2==0 else pos
            res["raw_col"]=col.reshape(-1,2,3) if col.shape[0]%2==0 else col
    _GL_CACHE[key]=res
    return res

def _draw_wire(ctx, fp, view, proj, aspect):
    """Draw the thick dimming wireframe into the CURRENTLY-BOUND framebuffer."""
    import moderngl
    ctx.enable(moderngl.DEPTH_TEST); ctx.depth_func="<="; ctx.depth_mask=True
    ctx.disable(moderngl.BLEND)
    ctx.disable(moderngl.CULL_FACE)   # FIX: camera-facing quads — never cull (pyglet enables culling by default)
    res=_get_wire_resources(ctx,fp); prog=res.get("prog")
    if prog is None: return
    try: prog['u_mvp'].write(_mvp_bytes(view,proj))
    except Exception: pass
    for nm,val in (('u_aspect',float(aspect)),('u_half_px',float(LINE_HALF_PX)),
                   ('u_dim_near',float(DIM_NEAR_M)),('u_dim_far',float(DIM_FAR_M)),
                   ('u_grey_floor',float(GREY_FLOOR))):
        try: prog[nm].value=val
        except Exception: pass
    if _USE_GS:
        if res.get("vao") is not None:
            res["vao"].render()
    else:
        # CPU-billboard: expand each segment into 2 tris using camera right/up from view rows
        v=np.asarray(view,np.float32)
        right=v[0,:3]; up=v[1,:3]
        raw=res.get("raw_pos");  rawc=res.get("raw_col")
        if raw is not None and raw.shape[0]>0:
            tris=[]; cols=[]
            hw=LINE_HALF_PX*40.0   # world-ish half-width for fallback (looks consistent enough)
            for i in range(raw.shape[0]):
                a=raw[i,0]; b=raw[i,1]; ca=rawc[i,0]; cb=rawc[i,1]
                d=b-a; L=np.linalg.norm(d)
                if L<1e-6: continue
                n=np.cross(d/L, up); n=n/ (np.linalg.norm(n)+1e-9) * hw
                tris += [a+n,a-n,b-n, a+n,b-n,b+n]
                cols += [ca,ca,cb, ca,cb,cb]
            if tris:
                tp=np.array(tris,np.float32); tc=np.array(cols,np.float32)
                vbo_p=ctx.buffer(tp.tobytes()); vbo_c=ctx.buffer(tc.tobytes())
                vao=ctx.vertex_array(prog,[(vbo_p,'3f','in_pos'),(vbo_c,'3f','in_color')],mode=moderngl.TRIANGLES)
                vao.render()
                try: vao.release()
                except Exception: pass

def render_mode_a(ctx, window, view, proj, fp, state, guidelines_fn=None, targets=None):
    """Full Mode A: render wire (+guidelines) to offscreen, bloom, composite to screen."""
    if not HAVE_GL:
        return
    try:
        import moderngl
    except Exception:
        return
    w=int(getattr(window,"width",1280)); h=int(getattr(window,"height",720))
    aspect=w/max(h,1)
    try:
        fb=_build_fbos(ctx,w,h)
    except Exception:
        # If FBO setup fails for any reason, draw straight to screen (still thick+dimmed, no glow)
        ctx.screen.use()
        _draw_wire(ctx,fp,view,proj,aspect)
        if guidelines_fn is not None: guidelines_fn(view,proj,aspect)
        return
    # 1) scene -> offscreen
    fb["scene_fbo"].use()
    ctx.clear(0.05,0.06,0.08,1.0)
    _draw_wire(ctx,fp,view,proj,aspect)
    if guidelines_fn is not None:
        guidelines_fn(view,proj,aspect)          # guidelines share projection, draw into scene
    # 2) bright extract -> half-res
    fb["bright_fbo"].use(); ctx.disable(moderngl.BLEND); ctx.disable(moderngl.DEPTH_TEST)
    fb["scene_tex"].use(0)
    try: fb["bright_p"]['u_tex'].value=0; fb["bright_p"]['u_threshold'].value=BLOOM_THRESHOLD
    except Exception: pass
    fb["bright_vao"].render(mode=moderngl.TRIANGLES)
    # 3) blur H -> blurA
    fb["blurA_fbo"].use(); fb["bright_tex"].use(0)
    try: fb["blur_p"]['u_tex'].value=0; fb["blur_p"]['u_dir'].value=(1.0/fb["bw"],0.0)
    except Exception: pass
    fb["blurA_vao"].render(mode=moderngl.TRIANGLES)
    # 4) blur V -> blurB
    fb["blurB_fbo"].use(); fb["blurA_tex"].use(0)
    try: fb["blur_p"]['u_tex'].value=0; fb["blur_p"]['u_dir'].value=(0.0,1.0/fb["bh"])
    except Exception: pass
    fb["blurB_vao"].render(mode=moderngl.TRIANGLES)
    # 5) composite scene + bloom -> screen
    ctx.screen.use()
    ctx.clear(0.0,0.0,0.0,1.0)
    fb["scene_tex"].use(0); fb["blurB_tex"].use(1)
    try:
        fb["comp_p"]['u_scene'].value=0; fb["comp_p"]['u_bloom'].value=1
        fb["comp_p"]['u_bloom_gain'].value=BLOOM_GAIN
    except Exception: pass
    fb["comp_vao"].render(mode=moderngl.TRIANGLES)

# Back-compat thin entry kept (used by tests / direct-to-screen callers):
def draw_graph(view, proj, aspect, fp, state):
    if not HAVE_GL: return
    try:
        import moderngl
        ctx=moderngl.get_context()
    except Exception:
        return
    ctx.screen.use()
    _draw_wire(ctx,fp,view,proj,aspect)
