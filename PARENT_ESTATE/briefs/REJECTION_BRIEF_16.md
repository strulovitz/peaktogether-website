REJECTION — Brief #16: Do it again. Properly this time.

Your code was tested on screen by Nir. It was REVERTED in full. Every file you
produced was rolled back. Here is what you need to know before you try again.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT YOU BROKE (3 fatal bugs, all visible on screen):

1. PLAQUE IS 28 WORLD-UNITS WIDE.
   Root cause: you used PIXEL dimensions (tw, th) directly as world-space
   scale. A 560px-wide texture with 14px line height gives aspect = 40.
   Multiplied by PLAQUE_SCALE = 0.7 → 28 world-units wide, 0.7 tall.
   Result: VICTORY #1 appears "far away ahead of the robot" and is an
   unreadable horizontal strip. The player cannot read it.

2. NO BLENDING ON THE BACKING CARD.
   Your code does glDisable(GL_TEXTURE_2D) then draws the dark backing quad
   but never calls glEnable(GL_BLEND). The card renders OPAQUE. The text
   billboards either don't show or fight with the card visually.

3. DEPTH-TEST FLICKERING.
   The plaque is billboarded with GL_DEPTH_TEST enabled. Near corridor walls
   cause z-fighting. The plaque flickers. Holograms in robots.py solve this by
   calling glDisable(GL_DEPTH_TEST) + glDepthMask(GL_FALSE). You didn't.

4. GL STATE LEAK.
   After the for-loop you restore glColor4f(1,1,1,1) but GL_TEXTURE_2D
   is still disabled. The next draw call (corridor titles, robot labels)
   inherits broken state.

5. CRASH: NameError: name 'GL_FALSE' is not defined.
   This was from a later fix attempt, but the pattern is the same: you
   call GL constants without importing them. Import EVERYTHING you use.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT YOU MUST DO DIFFERENTLY THIS TIME:

A) WORLD-SPACE WIDTH CAP.
   The PIXEL aspect ratio of the rich-text surface is NOT a world-space
   dimension. Add a PLAQUE_MAX_WORLD_WIDTH constant (suggest 3.5–4.5, tune
   it as a named constant for DeepSeek). Compute corrected_scale:
     pixel_aspect = tw / max(th, 1)
     if PLAQUE_SCALE * pixel_aspect > PLAQUE_MAX_WORLD_WIDTH:
         corrected_scale = PLAQUE_MAX_WORLD_WIDTH / pixel_aspect
     else:
         corrected_scale = PLAQUE_SCALE
   Use corrected_scale for BOTH the backing card AND draw_billboard calls.

B) BLEND + DEPTH.
   Before drawing anything in the plaque (backing card + billboards):
     glEnable(GL_BLEND)
     glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
     glDisable(GL_DEPTH_TEST)
     glDepthMask(GL_FALSE)
   After drawing everything in the plaque loop, RESTORE:
     glDepthMask(GL_TRUE)
     glEnable(GL_DEPTH_TEST)
     glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
     glDisable(GL_BLEND)
   Import every GL constant and function you use. NO NameErrors.

C) GL STATE MUST BE CLEAN AFTER THE METHOD.
   glEnable(GL_TEXTURE_2D) at the end. glColor4f(1,1,1,1) at the end.
   The code AFTER _draw_plaques must never know it ran.

D) THE DEMO MUST ACTUALLY WORK.
   Your plaque_demo.py auto-fires by calling handle_input(True, ...) every
   frame. This fires the FIRST weapon in the arsenal at the FIRST blocking
   robot. Test this: will it actually match and defeat? If not, make the demo
   USE the correct weapon. The demo must VISIBLY show a defeated robot + its
   plaque, without requiring Nir to manually fly and shoot.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE FILES YOU PRODUCE (same as last time):

- Changes to render.py (rich_to_surface_wrapped + helpers + get_rich_wrapped)
- Changes to corridor_builder.py (_draw_plaques rewritten + plaque constants)
- NEW plaque_demo.py (flyable demo)

KEEP the same fresh-chat gate. KEEP the same scope fence. KEEP the same
completion report. Do NOT change anything about the game flow, frame order,
or flush_walls. Same brief structure — just write code that WORKS this time.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ACCEPTANCE (Nir must see on screen, with ZERO code reading):
1. Run plaque_demo.py. Robot is defeated. Plaque appears at the robot's
   position (above it, not far ahead).
2. Plaque is a dark translucent card ~3-4 world-units wide, proportionally
   tall, readable at 5-15 world-units distance.
3. "VICTORY #1" title on top, full proof text below. NO flickering.
4. The same plaque works when defeating robots manually in app.py.
5. NO crashes. NO white rectangles. NO raw LaTeX source. NO NameErrors.

The code was already reverted on disk. Start from scratch.
