# /// script
# requires-python = ">=3.11"
# dependencies = ["segno>=1.6", "pillow>=11"]
# ///
"""Generate the generated files under site/: QR code, icons, preview card, vCard.

Usage (from the repository root):

    uv run tools/make_assets.py                      # regenerate everything
    uv run tools/make_assets.py --photo ~/profil.jpg # use a new profile photo
    uv run tools/make_assets.py --photo ~/profil.jpg --crop 137,40,1117,1020
                                                     # ... cut out a region first (pixels: left,top,right,bottom)

Without --photo an existing site/assets/profile.jpg is kept. If none exists,
a monogram placeholder is created. Photos are cropped to a square, resized
and saved without any metadata (EXIF, GPS, camera data).
"""

from __future__ import annotations

import argparse
import base64
import io
from pathlib import Path

import segno
from PIL import Image, ImageDraw, ImageFont, ImageOps

# --- Content -----------------------------------------------------------------
URL = "https://guido.glohn.de/"
DISPLAY_URL = "guido.glohn.de"
FIRST_NAME, LAST_NAME = "Guido", "Lohn"
FULL_NAME = f"{FIRST_NAME} {LAST_NAME}"
TITLE = "Senior Operations Engineer · AI Engineer"  # page and preview card
VCARD_TITLE = "Senior Operations Engineer"  # official job title, used with ORG in the vCard
ORG = "brickfox GmbH"  # legal name for the address book; the page shows the brand "brickfox"
EMAIL = "guido@glohn.de"  # personal contact address; kontakt@glohn.de stays in the privacy policy
MONOGRAM = "GL"
VCARD_LINKS = [
    ("Website", URL),
    ("LinkedIn", "https://www.linkedin.com/in/guido-lohn"),
    ("GitHub", "https://github.com/glohn"),
]

# --- Look --------------------------------------------------------------------
# Taken from the blueprint portrait (see site/assets/site.css)
ACCENT = "#00347d"        # blueprint blue
DARK_BG = "#0b0c10"       # near-black page background
MUTED = "#9da8bb"
ACCENT_LIGHT = "#7fb0ff"
GRID = (19, 91, 161)      # #135ba1, grid lines

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ASSETS = SITE / "assets"
PROFILE = ASSETS / "profile.jpg"
PLACEHOLDER_MARK = b"placeholder"


def font(size: int) -> ImageFont.FreeTypeFont:
    # Pillow ships a scalable font (Aileron); no system fonts needed.
    return ImageFont.load_default(size=size)


def draw_centered(draw: ImageDraw.ImageDraw, xy, text, size, fill, bold=False):
    stroke = max(1, size // 28) if bold else 0
    draw.text(xy, text, font=font(size), fill=fill, anchor="mm",
              stroke_width=stroke, stroke_fill=fill)


def monogram(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), ACCENT)
    draw_centered(ImageDraw.Draw(img), (size / 2, size / 2), MONOGRAM,
                  int(size * 0.42), "white", bold=True)
    return img


def make_qr() -> segno.QRCode:
    qr = segno.make(URL, error="q", micro=False)
    # omitsize: viewBox instead of fixed width/height, so the SVG scales cleanly.
    qr.save(ASSETS / "qr.svg", kind="svg", scale=1, border=4, omitsize=True,
            dark="#000000", light="#ffffff", xmldecl=False,
            svgclass=None, lineclass=None, title=URL)

    # Image for the phone's photo library (offline fallback at events).
    buf = io.BytesIO()
    # Integer scale only, so every module stays exactly the same width.
    scale = 960 // (qr.symbol_size(border=4)[0])
    qr.save(buf, kind="png", scale=scale, border=4, dark="#000000", light="#ffffff")
    code = Image.open(buf).convert("RGB")
    card = Image.new("RGB", (1080, 1350), "white")
    card.paste(code, ((1080 - code.width) // 2, 1000 - code.height))
    draw = ImageDraw.Draw(card)
    draw_centered(draw, (540, 1110), FULL_NAME, 72, "#111111", bold=True)
    draw_centered(draw, (540, 1200), DISPLAY_URL, 48, "#555555")
    card.save(ASSETS / "guido-glohn-de-qr.png", optimize=True)
    return qr


def make_profile(photo: Path | None, crop: tuple[int, int, int, int] | None = None) -> bool:
    """Write site/assets/profile.jpg. Returns True if it is a real photo."""
    if photo:
        img = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")
        if crop:
            img = img.crop(crop)
        img = ImageOps.fit(img, (480, 480), Image.LANCZOS)
        # Saving without exif=/icc_profile= drops all metadata.
        img.save(PROFILE, "JPEG", quality=85, optimize=True, progressive=True)
        return True
    if not PROFILE.exists():
        monogram(480).save(PROFILE, "JPEG", quality=90, comment=PLACEHOLDER_MARK)
        return False
    with Image.open(PROFILE) as img:
        return img.info.get("comment") != PLACEHOLDER_MARK


def circle(img: Image.Image, size: int) -> Image.Image:
    img = ImageOps.fit(img.convert("RGB"), (size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * 4, size * 4), fill=255)
    img.putalpha(mask.resize((size, size), Image.LANCZOS))
    return img


def blueprint_grid(img: Image.Image) -> Image.Image:
    """Same grid as the page background: major lines every 120px, minor every 24px."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size
    for step, alpha in ((24, 15), (120, 41)):  # 6% and 16% opacity
        x0 = (w // 2) % step                   # centred like background-position: center
        for x in range(x0, w, step):
            draw.line([(x, 0), (x, h)], fill=(*GRID, alpha))
        for y in range(0, h, step):
            draw.line([(0, y), (w, y)], fill=(*GRID, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def make_icons() -> None:
    monogram(180).save(ASSETS / "apple-touch-icon.png", optimize=True)
    # Same round monogram as favicon.svg, for clients that request /favicon.ico directly.
    circle(monogram(256), 256).save(SITE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    og = blueprint_grid(Image.new("RGB", (1200, 630), DARK_BG))
    with Image.open(PROFILE) as profile:
        og.paste(circle(profile, 300), (110, 165), circle(profile, 300))
    draw = ImageDraw.Draw(og)
    draw.text((480, 185), FULL_NAME, font=font(76), fill="white",
              stroke_width=2, stroke_fill="white")
    # One title per line, so the long combined title never runs off the card.
    for i, part in enumerate(TITLE.split(" · ")):
        draw.text((482, 290 + i * 52), part, font=font(40), fill=MUTED)
    draw.text((482, 420), DISPLAY_URL, font=font(36), fill=ACCENT_LIGHT)
    og.save(ASSETS / "og-card.png", optimize=True)


def fold(line: str) -> str:
    """Fold a vCard line at 75 characters (RFC 6350 / 2426)."""
    parts = [line[:75]] + [" " + line[i:i + 74] for i in range(75, len(line), 74)]
    return "\r\n".join(parts)


def make_vcard(real_photo: bool) -> None:
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{LAST_NAME};{FIRST_NAME};;;",
        f"FN:{FULL_NAME}",
        f"TITLE:{VCARD_TITLE}",
        f"ORG:{ORG}",
        f"EMAIL;TYPE=INTERNET:{EMAIL}",
    ]
    for i, (label, url) in enumerate(VCARD_LINKS, start=1):
        lines += [f"item{i}.URL:{url}", f"item{i}.X-ABLabel:{label}"]
    if real_photo:
        with Image.open(PROFILE) as img:
            buf = io.BytesIO()
            img.convert("RGB").resize((256, 256), Image.LANCZOS).save(
                buf, "JPEG", quality=80, optimize=True)
        lines.append("PHOTO;ENCODING=b;TYPE=JPEG:" + base64.b64encode(buf.getvalue()).decode())
    lines.append("END:VCARD")
    data = "\r\n".join(fold(line) for line in lines) + "\r\n"
    (SITE / "guido-lohn.vcf").write_bytes(data.encode("utf-8"))


def parse_box(value: str) -> tuple[int, int, int, int]:
    left, top, right, bottom = (int(v) for v in value.split(","))
    if right <= left or bottom <= top:
        raise argparse.ArgumentTypeError("expected left,top,right,bottom with right>left, bottom>top")
    return left, top, right, bottom


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--photo", type=Path, help="new profile photo (any size, any format)")
    parser.add_argument("--crop", type=parse_box, metavar="L,T,R,B",
                        help="region of the photo to use, in pixels (left,top,right,bottom)")
    args = parser.parse_args()
    if args.crop and not args.photo:
        parser.error("--crop needs --photo")

    ASSETS.mkdir(parents=True, exist_ok=True)
    qr = make_qr()
    real_photo = make_profile(args.photo.expanduser() if args.photo else None, args.crop)
    make_icons()
    make_vcard(real_photo)

    print(f"QR code: {URL} (version {qr.version}, error correction {qr.error})")
    print(f"Profile image: {'photo' if real_photo else 'placeholder (monogram)'}")
    for path in sorted([*ASSETS.glob("*.png"), *ASSETS.glob("*.jpg"), ASSETS / "qr.svg", SITE / "guido-lohn.vcf"]):
        print(f"  {path.relative_to(ROOT)}  {path.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
