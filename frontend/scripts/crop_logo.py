"""Asset prep: extract the globe graphic from the source logo PNG.

Run once: python scripts/crop_logo.py
Produces src/assets/logo-globe.png (512px) and public/favicon.png (64px).
"""
import os

import numpy as np
from PIL import Image

SRC = r"C:/Users/omerf/Downloads/PAK JOURNAL ARCHIVE 77 (3).png"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

im = Image.open(SRC).convert("RGBA")
arr = np.array(im).astype(int)
h, w = arr.shape[:2]
corner = arr[2, 2]

if corner[3] < 16:
    mask = arr[:, :, 3] > 24
else:
    dist = np.abs(arr[:, :, :3] - corner[:3]).sum(axis=2)
    mask = dist > 45

content = mask.sum(axis=1) > (w * 0.012)
blocks, start = [], None
for y in range(h):
    if content[y] and start is None:
        start = y
    elif not content[y] and start is not None:
        blocks.append((start, y - 1))
        start = None
if start is not None:
    blocks.append((start, h - 1))

print("background corner:", corner.tolist())
print("content blocks (y0,y1):", blocks)

y0, y1 = max(blocks, key=lambda b: b[1] - b[0])
cols = np.where(mask[y0:y1 + 1, :].sum(axis=0) > 0)[0]
x0, x1 = int(cols[0]), int(cols[-1])
print("globe bbox:", (x0, y0, x1, y1), "size:", (x1 - x0, y1 - y0))

crop = im.crop((x0, y0, x1 + 1, y1 + 1))
cw, ch = crop.size
side = max(cw, ch)
pad = int(side * 0.05)
sp = side + pad * 2
canvas = Image.new("RGBA", (sp, sp), (0, 0, 0, 0))
canvas.paste(crop, ((sp - cw) // 2, (sp - ch) // 2), crop)

logo_path = os.path.join(HERE, "src", "assets", "logo-globe.png")
fav_path = os.path.join(HERE, "public", "favicon.png")
os.makedirs(os.path.dirname(logo_path), exist_ok=True)
os.makedirs(os.path.dirname(fav_path), exist_ok=True)
canvas.resize((512, 512), Image.LANCZOS).save(logo_path)
canvas.resize((64, 64), Image.LANCZOS).save(fav_path)
print("saved:", logo_path)
print("saved:", fav_path)
