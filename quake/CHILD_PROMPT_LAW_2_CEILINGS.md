# CHILD PROMPT — law_2: Review & rewrite ceiling equations

Your task: review and rewrite the two ceiling equations in this `.room` file. The current equations (written by DeepSeek, NOT by an AI with mathematical intelligence) are basic and may miss nuance. Write one ceiling equation per station (2 stations = 2 equations). Each equation should capture the key mathematical/physical idea of that specific step, in LaTeX. Do NOT change any other part of the file — not the stations, not the colors, not the text, not the layout.

Here is the current file:

```
room      law_2
kind      equation
import    Newton, Principia, Axioms or Laws of Motion, Law II, p.19 (Motte trans., 1729)
caption   The alteration of motion is proportional to, and directed along, the impressed force.
final     2
ceiling   eq0 :: \Delta(\text{motion}) \propto \mathbf{F}
ceiling   eq1 :: \Delta(\text{motion}) \parallel \mathbf{F}

station 1
  gloss   The alteration of motion is proportional to the motive force impressed.
  color   motionblue   #1E6FE0
  color   forceorange  #E8770A
  panel
    term    motionblue   $\Delta(\text{motion})$   heart stabilo=#BBD7FB
    term    forceorange  $\mathbf{F}$
    layout  $\,{motionblue|\Delta(\text{motion})}\;\propto\;{forceorange|\mathbf{F}}\,$
  text
    The Law sets {motionblue|the alteration of motion} in strict proportion to {forceorange|the motive force impressed}. As Newton explains, if any force generates a motion, then {forceorange|a double force} will generate {motionblue|double the motion}, a triple force triple the motion — whether {forceorange|that force} be impressed altogether and at once, or gradually and successively. The {motionblue|change $\Delta(\text{motion})$} scales exactly with the impressed {forceorange|$\mathbf{F}$}.

station 2
  gloss   The change of motion is made in the direction of the right line in which the force is impressed.
  color   motionblue   #1E6FE0
  color   forceorange  #E8770A
  color   dirgreen     #00A35A
  panel
    term    motionblue   $\Delta(\text{motion})$
    term    forceorange  $\mathbf{F}$
    term    dirgreen     $\parallel\;\text{(right line of }\mathbf{F}\text{)}$   heart stabilo=#B7E9CF
    layout  $\,{motionblue|\Delta(\text{motion})}\;{dirgreen|\parallel}\;{forceorange|\mathbf{F}}\,$
  text
    The {motionblue|change of motion} is made {dirgreen|in the direction of the right line} in which {forceorange|the force} is impressed. This motion, being always directed the same way with {forceorange|the generating force}, if the body moved before, is {dirgreen|added to or subducted from} the former motion — according as they directly conspire with or are directly contrary to each other; or {dirgreen|obliquely joined}, when they are oblique, so as to produce a new motion compounded from the determination of both. Thus {motionblue|$\Delta(\text{motion})$} runs {dirgreen|parallel} to {forceorange|$\mathbf{F}$}.
```

Give me ONLY the new `ceiling` lines, one per station. Format: `ceiling   eq0 :: <LaTeX>` and `ceiling   eq1 :: <LaTeX>`.
