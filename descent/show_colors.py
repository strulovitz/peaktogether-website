"""Show the 6 palette colors as squares on screen."""
import tkinter as tk
import sys
sys.path.insert(0, ".")
from palette import Palette, PaletteError
from content_parser import parse_corridor

# Load fixture ledger
ledger = parse_corridor("corridors/01_dummy.txt").ledger
pal = Palette(ledger)

# Get tints and eyes
colors = [
    ("RED (alpha)",     pal.tint("alpha")[:3], pal.eye("alpha"),     pal.text_color_on("alpha")),
    ("YELLOW (beta)",   pal.tint("beta")[:3],  pal.eye("beta"),      pal.text_color_on("beta")),
    ("BLUE (gamma)",    pal.tint("gamma")[:3], pal.eye("gamma"),     pal.text_color_on("gamma")),
    ("ORANGE (delta)",  pal.tint("delta")[:3], pal.eye("delta"),     pal.text_color_on("delta")),
    ("PURPLE (r+b)",    pal.blend_rgb("alpha","gamma"), pal.blend_rgb("alpha","gamma"), pal.text_color_on("gamma")),
    ("GREEN (y+b)",     pal.blend_rgb("beta","gamma"),  pal.blend_rgb("beta","gamma"),  pal.text_color_on("beta")),
]

def to_hex(rgb):
    r, g, b = [max(0, min(255, int(c * 255))) for c in rgb]
    return f"#{r:02x}{g:02x}{b:02x}"

root = tk.Tk()
root.title("Palette Color Viewer — PeakTogether QED Engine 🏔️")
root.configure(bg="#0c0e1a")
sq = 140
pad = 16
cols = 3

tk.Label(root, text="TINT", fg="white", bg="#0c0e1a",
         font=("Consolas", 11)).grid(row=0, column=1, pady=(12,4))
tk.Label(root, text="EYE GLOW", fg="white", bg="#0c0e1a",
         font=("Consolas", 11)).grid(row=0, column=2, pady=(12,4))

for i, (name, tint, eye, txt_clr) in enumerate(colors):
    row = 1 + (i // cols) * 3
    col = i % cols

    tk.Label(root, text=name, fg="white", bg="#0c0e1a",
             font=("Consolas", 10, "bold")).grid(row=row, column=col, pady=(12,2))

    # Tint square
    f1 = tk.Frame(root, width=sq, height=sq, bg=to_hex(tint))
    f1.grid(row=row+1, column=col, padx=pad)
    f1.pack_propagate(False)

    # Eye glow square
    f2 = tk.Frame(root, width=sq, height=sq//2, bg=to_hex(eye))
    f2.grid(row=row+2, column=col, padx=pad, pady=(4,12))
    f2.pack_propagate(False)

    # Label tint RGB
    tk.Label(root, text=f"R:{tint[0]:.2f} G:{tint[1]:.2f} B:{tint[2]:.2f}",
             fg="grey", bg="#0c0e1a", font=("Consolas", 8)).grid(row=row+2, column=col, pady=(0,0))

root.mainloop()
