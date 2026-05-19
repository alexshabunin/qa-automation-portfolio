"""Wide banner for the top of the qa-automation-portfolio README."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "img" / "banner.png"

W, H = 1600, 420
BG_TOP = (12, 18, 32)
BG_BOTTOM = (22, 32, 54)
FG = (245, 247, 250)
DIM = (140, 160, 184)
ACCENT = (94, 178, 240)
ACCENT2 = (110, 220, 160)
ACCENT3 = (220, 130, 220)


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = (
        [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        if bold
        else [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG_TOP)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        d.rectangle([(0, y), (W, y + 1)], fill=(r, g, b))
    return img


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = _gradient_bg()
    d = ImageDraw.Draw(img)

    # subtle grid of dots (very faint) for texture
    dot = (255, 255, 255, 8)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(40, W, 32):
        for y in range(40, H, 32):
            od.ellipse([(x - 1, y - 1), (x + 1, y + 1)], fill=dot)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)

    # left vertical accent bar
    d.rectangle([(0, 0), (10, H)], fill=ACCENT)

    # title
    f_title = _font(96, bold=True)
    d.text((90, 80), "qa-automation-portfolio", fill=FG, font=f_title)

    # tagline
    f_sub = _font(40)
    d.text(
        (94, 200),
        "One SPA.  Two UI architectures.  + REST API suite.",
        fill=DIM,
        font=f_sub,
    )

    # tags row
    chips = [
        ("pytest", ACCENT),
        ("Playwright", ACCENT2),
        ("Page Object Model", ACCENT),
        ("vedro", ACCENT3),
        ("d42", ACCENT3),
        ("ApiManager", ACCENT2),
        ("Allure", ACCENT),
    ]
    f_chip = _font(26, bold=True)
    x = 94
    y = 290
    for text, color in chips:
        bbox = d.textbbox((0, 0), text, font=f_chip)
        tw = bbox[2] - bbox[0]
        pad_x = 18
        pad_y = 10
        rect_w = tw + pad_x * 2
        rect_h = 44
        # chip outline
        d.rounded_rectangle(
            [(x, y), (x + rect_w, y + rect_h)], radius=10, outline=color, width=2
        )
        d.text((x + pad_x, y + 4), text, fill=FG, font=f_chip)
        x += rect_w + 12

    img.save(OUT, optimize=True)
    print(f"ok: {OUT} size={OUT.stat().st_size:,}B {W}x{H}")


if __name__ == "__main__":
    main()
