================================================================================
DESCENT QED -- BRIEF #13: GAME STATE (the whole thing, one module, win-only)
SCOPE: build ONE module `game_state.py` holding the few BITS that make this a
GAME: which robots are dead, whether each corridor's couple is rescued, whether
each corridor is complete, whether the LEVEL is complete. Plus the rescue trigger
and the "HOSTAGES RESCUED" HUD beat. THERE IS NO LOSING. No death, no timer, no
fail. This finishes the game. Do it in ONE pass.
================================================================================

FRESH-CHAT GATE -- FIRST, before any code, ask Nir to paste VERBATIM & CURRENT:
  1. app.py            * the canonical frame loop (where update + draw + HUD run)
  2. hub_builder.py    * hub.corridors, hub.update, hub.draw_robots, spawn_pose
  3. corridor_builder.py * CorridorGeometry: its robots list + how a robot is
                          marked alive/dead today; _hostages list; update(...) and
                          draw_robots(...); entrance_pose / hostage geometry
  4. hostages.py       * Hostage (position, draw), build_hostages, near_hostages
  5. robots.py         how a robot exposes alive/dead (the existing bit)
  6. combat.py / whatever owns draw_hud  * the HUD draw path + existing text draw
  7. render.py         text/2D draw helpers (draw_plain_text_2d if it exists yet)
PASTED FILES ARE LAW. If this brief disagrees with a file, the FILE WINS -- flag it.

WHO'S INVOLVED: NIR = non-technical human courier + tester. DEEPSEEK = commits +
mechanical tuning ONLY (radii, colors). DeepSeek does NOT design; DeepSeek was
WRONG that there's a lose state -- THERE IS NO LOSING. PARENT = architecture.

PRIME LAW: the engine never interprets math/meaning. Game state tracks PROGRESS
BITS only -- never what a mathematical technique MEANS, never color->meaning.

------------------------------------------------------------------------------
WHAT THE GAME ALREADY HAS (do not rebuild)
------------------------------------------------------------------------------
- Robots already have an alive/dead bit (find the REAL field/flag in robots.py).
- near_hostages(hostage_list, ship_pos, radius) -> bool already works.
- Hostages already draw in the draw_robots slot, two per corridor, standing.
You are ADDING the thin layer that READS these bits and decides progress + shows
the rescue message. You are NOT redesigning robots, hostages, or corridors.

------------------------------------------------------------------------------
WHAT TO BUILD -- `game_state.py`
------------------------------------------------------------------------------
A small GameState that holds the bits and the rules. Win-only. No lose anywhere.

  class GameState:
      def __init__(self, hub):
          # one record per corridor: {rescued: False, complete: False}
          # (robot alive/dead stays where it lives today -- we just READ it)
      def update(self, hub, ship_pos, dt):
          for each corridor:
            # RESCUE TRIGGER (the one bit Nir wants):
            #   if not rescued and near_hostages(corridor._hostages, ship_pos,
            #       NEAR_RADIUS): mark rescued = True, set a brief HUD flash timer
            #       ("HOSTAGES RESCUED"), and make the couple DISAPPEAR (now aboard
            #       the ship) -- e.g. set corridor.hostages_rescued so draw_robots
            #       skips drawing them. (Choose the simplest real mechanism that
            #       fits the pasted draw_robots -- flag/skip-draw, no new render.)
            # CORRIDOR COMPLETE:
            #   complete = rescued AND all robots in this corridor dead.
            #   (Reading the existing robot alive/dead bit. If Nir wants rescue
            #   alone to complete it, that's a 1-line change -- but default:
            #   robots cleared AND couple rescued.)
          # LEVEL COMPLETE: all corridors complete -> self.level_complete = True
          # advance the HUD flash timer down by dt.

      # tiny read-only queries for the HUD:
      def rescued_count(self) -> (done:int, total:int)
      def corridors_complete(self) -> (done:int, total:int)
      def show_rescue_flash(self) -> bool        # True while flash timer > 0
      def is_level_complete(self) -> bool

NO lose method. NO damage. NO timer that can fail. NO death of the ship. The only
timers are the harmless rescue-message flash and (optionally) a level-complete
banner.

------------------------------------------------------------------------------
THE HUD BEAT -- "HOSTAGES RESCUED"
------------------------------------------------------------------------------
In the existing draw_hud (combat.py or wherever it lives -- use the REAL one):
  - While game_state.show_rescue_flash(): draw a centered "HOSTAGES RESCUED"
    message for a couple seconds (use the existing 2D text path; if a
    draw_plain_text_2d exists use it, else use the existing HUD text call you see).
  - A small persistent status line is OK: e.g. "RESCUED 1/4" using rescued_count().
  - When is_level_complete(): a "LEVEL COMPLETE" banner. (Win-only celebration --
    NOT a screen lock, NOT a fail.)
Keep it minimal and readable. No new asset files.

------------------------------------------------------------------------------
WIRING -- give the PARENT the exact lines; DO NOT silently edit app.py
------------------------------------------------------------------------------
You will REQUEST (and show the exact lines) for the parent to add:
  - construct once: game_state = GameState(hub)  (near where hub is built)
  - in the loop, after hub.update(...): game_state.update(hub, ship_pos, dt)
  - in the HUD draw step: pass game_state to draw_hud (or call the message draw)
  - if rescue must skip drawing the couple, show the exact 1-line guard in
    corridor.draw_robots (e.g. `if not self.hostages_rescued:` around the hostage
    draw loop) -- built so it's a trivial one-line add.
Provide these as COPY-PASTE lines with file + location. Build game_state.py so the
wiring is a handful of one-liners, nothing more.

------------------------------------------------------------------------------
ENGINE CANON -- DO NOT BREAK
------------------------------------------------------------------------------
Frame order: events -> ship.update -> clear -> set_fog -> apply_view ->
hub.update -> hub.draw_world (QUEUE walls) -> flush_walls (EXACTLY ONCE) ->
hub.draw_robots -> hub.draw_labels -> flip.
game_state.update goes with the update phase (after hub.update). The HUD draws
in the existing HUD step. DO NOT TOUCH flush_walls -- if you add/move/remove/
duplicate it ALL WALLS VANISH SILENTLY (black screen, no error). game_state
draws NO world geometry; it only reads bits and the HUD draws text.

------------------------------------------------------------------------------
WHAT YOU MUST NOT DO
------------------------------------------------------------------------------
- NO lose state, NO ship damage/death, NO failing timer, NO game-over. WIN ONLY.
- Do NOT rebuild robots, hostages, or corridors. READ their existing bits.
- Do NOT touch flush_walls / reorder the loop.
- Do NOT change the corridor file format / parser.
- Do NOT interpret math/technique/color MEANING -- progress bits only.
- Do NOT add asset files. Use existing text/HUD draw.
- Do NOT split this into pieces or hand the design to DeepSeek. Build it whole.

------------------------------------------------------------------------------
DEMO -- `game_state_demo.py` (Nir RUNS this) -- must show the WHOLE loop working
------------------------------------------------------------------------------
Reuse app.py's real init/loop VERBATIM, add game_state. Acceptance Nir must SEE:
  1. Fly to a corridor's couple -> "HOSTAGES RESCUED" flashes, the two people
     DISAPPEAR (aboard ship), status shows RESCUED 1/N.
  2. Kill that corridor's robots (or if rescue-alone completes, skip) -> corridor
     marked complete.
  3. Do it for every corridor -> "LEVEL COMPLETE" banner appears. No fail ever.
  4. Walls still present (flush trap intact). Two people per corridor until saved.
  5. Flying away after rescue does NOT un-rescue them (bit is sticky).

------------------------------------------------------------------------------
COMPLETION REPORT
------------------------------------------------------------------------------
- FILES ADDED/CHANGED (game_state.py, demo; app/corridor/HUD UNCHANGED by you)
- RUN-VERIFIED? (Y/N)
- THE REAL robot alive/dead FIELD read (quote it)
- THE REAL HUD text call used (quote signature)
- HOW the couple is made to disappear on rescue (the exact mechanism)
- COMPLETE rule used (rescue+robots-dead, or rescue-only) -- state which
- FINAL GameState signatures
- EXACT WIRING LINES the parent must add (file + location, copy-paste)
- DEVIATIONS / file-wins flags
- DEEPSEEK tuning TODOs (NEAR_RADIUS, flash duration, banner text) with values
================================================================================
END OF BRIEF #13
================================================================================
