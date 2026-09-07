#!/usr/bin/env python3
"""Brand raster assets: favicon.ico, apple-touch-icon.png, og.png (+ favicon.svg)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
STATIC = ROOT / "static"
INK = (11, 30, 58)
INK900 = (8, 20, 38)
AMBER = (245, 165, 36)
SLATE = (169, 182, 203)
WHITE = (255, 255, 255)

ARCHIVO = STATIC / "fonts" / "Archivo[wdth,wght].ttf"
PLEX = STATIC / "fonts" / "IBMPlexSans-Regular.ttf"


def archivo(size, wght=600, wdth=125):
    f = ImageFont.truetype(str(ARCHIVO), size)
    try:
        f.set_variation_by_axes([wght, wdth])
    except Exception as e:
        print("variation not applied:", e)
    return f


def favicon_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#0B1E3A"/>
<path d="M14 32h36" stroke="#F5A524" stroke-width="3" stroke-linecap="round"/>
<circle cx="14" cy="32" r="6" fill="#F5A524"/>
<circle cx="50" cy="32" r="6" fill="#F5A524"/>
</svg>
"""
    (STATIC / "favicon.svg").write_text(svg)


def mark(size, radius_ratio=0.22):
    """Rounded ink square with the route mark."""
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * radius_ratio), fill=INK)
    y = s / 2
    x1, x2 = s * 0.22, s * 0.78
    lw = max(2, int(s * 0.05))
    d.line([(x1, y), (x2, y)], fill=AMBER, width=lw)
    r = s * 0.095
    for x in (x1, x2):
        d.ellipse([x - r, y - r, x + r, y + r], fill=AMBER)
    return img


def icons():
    m = mark(180)
    m.save(STATIC / "apple-touch-icon.png")
    ico = mark(64)
    ico.save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


def og():
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    # wordmark
    f_word = archivo(150, 600, 125)
    x0, y0 = 96, 168
    # node before wordmark
    d.ellipse([x0, y0 + 84, x0 + 22, y0 + 106], fill=AMBER)
    d.text((x0 + 44, y0 - 10), "oxitel", font=f_word, fill=WHITE)
    # tagline
    f_tag = ImageFont.truetype(str(PLEX), 36)
    d.text((x0, 356), "Wholesale voice carrier. Direct routes into Africa.", font=f_tag, fill=SLATE)
    # route line
    y = 470
    d.line([(x0 + 10, y), (W - 96 - 10, y)], fill=AMBER, width=3)
    for x in (x0 + 10, x0 + 10 + (W - 192 - 20) / 3, x0 + 10 + 2 * (W - 192 - 20) / 3, W - 106):
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=AMBER)
    labels = ["A-Z termination", "Premium CLI routes", "DID / virtual numbers", "24/7 NOC"]
    f_lab = ImageFont.truetype(str(PLEX), 24)
    for i, t in enumerate(labels):
        x = x0 + 10 + i * (W - 192 - 20) / 3
        if i == len(labels) - 1:
            w = d.textlength(t, font=f_lab)
            x = W - 96 - w
        d.text((x, y + 24), t, font=f_lab, fill=SLATE)
    d.text((W - 96 - 130, 56), "oxitel.net", font=f_lab, fill=SLATE)
    img.save(STATIC / "og.png", optimize=True)


if __name__ == "__main__":
    favicon_svg()
    icons()
    og()
    print("assets written")
