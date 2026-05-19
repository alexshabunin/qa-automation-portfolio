"""Generate docs/img/social-preview.png — 1280x640 PNG used as the
GitHub social card. Configured on the repo via Settings → Social preview.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "img" / "social-preview.png"

W, H = 1280, 640
BG = (15, 22, 36)
FG = (245, 247, 250)
DIM = (140, 160, 184)
ACCENT = (94, 178, 240)

LINES_TOP = [
    ("qa-automation-portfolio", 72, FG),
]
LINES_MID = [
    ("One SPA. Two UI architectures. + REST API suite.", 36, DIM),
]
LINES_LOW = [
    ("pytest + Playwright + POM", 28, FG),
    ("vedro + d42 + Webbricks", 28, FG),
    ("requests + ApiManager", 28, FG),
]


def _font(size: int) -> ImageFont.ImageFont:
    # try a few likely macOS/linux system fonts; fall back to default
    for path in [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # accent stripe on the left
    d.rectangle([(0, 0), (8, H)], fill=ACCENT)

    # top: title
    y = 110
    for text, size, color in LINES_TOP:
        f = _font(size)
        d.text((90, y), text, fill=color, font=f)
        y += size + 16

    # mid: tagline
    y += 14
    for text, size, color in LINES_MID:
        f = _font(size)
        d.text((90, y), text, fill=color, font=f)
        y += size + 12

    # divider
    y += 30
    d.rectangle([(90, y), (340, y + 3)], fill=ACCENT)
    y += 36

    # low: three stacks
    for text, size, color in LINES_LOW:
        f = _font(size)
        d.text((90, y), "•  " + text, fill=color, font=f)
        y += size + 14

    # bottom-right: link
    f_small = _font(22)
    link = "github.com/nightmarovvv/qa-automation-portfolio"
    bbox = d.textbbox((0, 0), link, font=f_small)
    tw = bbox[2] - bbox[0]
    d.text((W - tw - 60, H - 50), link, fill=DIM, font=f_small)

    img.save(OUT, optimize=True)
    print(f"ok: {OUT} size={OUT.stat().st_size:,}B {W}x{H}")


if __name__ == "__main__":
    main()
