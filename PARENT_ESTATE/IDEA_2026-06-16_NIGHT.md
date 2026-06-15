# Idea for tomorrow — June 16, 2026 NIGHT

## The real path to fix the plague white rectangle

The game already uses matplotlib to render text. matplotlib's `fig.text()` can
render BOTH English prose AND inline math (`$...$`) in a single call.

The bug: when you give a long paragraph to `fig.text()`, it draws it as ONE
very wide, very thin line. In world space this becomes an unreadable strip.

The fix: tell matplotlib to WRAP the text at a pixel width. matplotlib has
built-in text wrapping:
- `textwrap=True` or `wrap=True` parameter
- Or render into a fixed-width `fig.text()` box
- Or use `Text` object with `wrap=True`

Instead of children building their own tokenizers that split `$...$` from
prose manually, they should just tell matplotlib to wrap the text for them.

## What to ask Parent #5 tomorrow

"Can you write a brief where the child makes the renderer use matplotlib's
built-in text wrapping instead of trying to split `$` tokens manually?
matplotlib already knows how to handle mixed prose+math and wrap at a width.
Just pass the full EXPLAIN_MATHEMATICIAN text to matplotlib with a width
limit, and use the resulting surface as the plaque texture."

## Why this should work

- matplotlib's mathtext parser already understands `$...$` inline math
- matplotlib's text layout already supports word-wrapping
- No new parser, no tokenizer, no manual `$` splitting
- The child just needs to set a wrap width on the existing `fig.text()` call
