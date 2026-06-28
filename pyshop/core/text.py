from PIL import Image, ImageDraw, ImageFont


def load_text_font(size: int, bold: bool = False):
    candidates = []
    if bold:
        candidates.extend(["DejaVuSans-Bold.ttf", "arialbd.ttf"])
    candidates.extend(["DejaVuSans.ttf", "arial.ttf"])
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_text_tile(text_item: dict, crop_box, size) -> Image.Image:
    tile = Image.new("RGBA", size, (0, 0, 0, 0))
    if not text_item or not text_item.get("text"):
        return tile
    crop_left, crop_top, _crop_right, _crop_bottom = crop_box
    x = int(text_item.get("x", 0)) - crop_left
    y = int(text_item.get("y", 0)) - crop_top
    font = load_text_font(int(text_item.get("size", 36)), bool(text_item.get("bold", False)))
    color = tuple(text_item.get("fill", (255, 255, 255, 255)))
    ImageDraw.Draw(tile).multiline_text((x, y), text_item["text"], fill=color, font=font, spacing=4)
    return tile
