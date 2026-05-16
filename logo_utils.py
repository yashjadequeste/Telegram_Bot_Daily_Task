from pathlib import Path

from PIL import Image

LOGO_PATH = Path("templates/jadequest_logo.png")
LOGO_TRANSPARENT_PATH = Path("templates/jadequest_logo_transparent.png")
BLACK_THRESHOLD = 45


def make_transparent_logo(
    source=None,
    destination=None,
    threshold=BLACK_THRESHOLD,
):
    source = Path(source or LOGO_PATH)
    destination = Path(destination or LOGO_TRANSPARENT_PATH)

    if not source.is_file():
        raise FileNotFoundError(f"Logo not found: {source}")

    img = Image.open(source).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if r <= threshold and g <= threshold and b <= threshold:
                pixels[x, y] = (0, 0, 0, 0)

    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    destination.parent.mkdir(parents=True, exist_ok=True)
    img.save(destination, "PNG")
    return destination


def get_email_logo_path():
    if not LOGO_TRANSPARENT_PATH.is_file():
        try:
            make_transparent_logo()
        except FileNotFoundError:
            return LOGO_PATH if LOGO_PATH.is_file() else None
    return LOGO_TRANSPARENT_PATH
