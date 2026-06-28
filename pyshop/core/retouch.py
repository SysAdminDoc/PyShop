from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


def apply_retouch_dab(image: Image.Image, x: int, y: int, size: int, mode: str):
    if size <= 0:
        return
    half = max(1, size // 2)
    box = (
        max(0, x - half),
        max(0, y - half),
        min(image.width, x + half + 1),
        min(image.height, y + half + 1),
    )
    if box[0] >= box[2] or box[1] >= box[3]:
        return

    patch = image.crop(box)
    if mode == "blur":
        patch = patch.filter(ImageFilter.GaussianBlur(max(1, size // 8)))
    elif mode == "sharpen_tool":
        patch = patch.filter(ImageFilter.SHARPEN)
    elif mode == "healing":
        patch = patch.filter(ImageFilter.MedianFilter(3))
    elif mode == "dodge":
        patch = ImageEnhance.Brightness(patch).enhance(1.18)
    elif mode == "burn":
        patch = ImageEnhance.Brightness(patch).enhance(0.82)
    elif mode == "sponge":
        patch = ImageEnhance.Color(patch).enhance(0.65)
    else:
        return

    mask = Image.new("L", patch.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, patch.width - 1, patch.height - 1), fill=255)
    image.paste(patch, box, mask)
