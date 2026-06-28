from PIL import Image


def apply_channel_visibility(image: Image.Image, visibility: dict) -> Image.Image:
    red, green, blue, alpha = image.convert("RGBA").split()
    if not visibility.get("red", True):
        red = Image.new("L", image.size, 0)
    if not visibility.get("green", True):
        green = Image.new("L", image.size, 0)
    if not visibility.get("blue", True):
        blue = Image.new("L", image.size, 0)
    if not visibility.get("alpha", True):
        alpha = Image.new("L", image.size, 255)
    return Image.merge("RGBA", (red, green, blue, alpha))
