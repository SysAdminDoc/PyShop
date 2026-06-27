import math

from PIL import Image, ImageDraw


def paint_brush_dab(image, x: int, y: int, size: int, color):
    if size <= 1:
        if 0 <= x < image.width and 0 <= y < image.height:
            image.putpixel((x, y), color)
        return
    half = size // 2
    ImageDraw.Draw(image).ellipse((x - half, y - half, x + half, y + half), fill=color)


def paint_brush_line(image, x1: int, y1: int, x2: int, y2: int, size: int, color):
    distance = max(1, int(math.hypot(x2 - x1, y2 - y1)))
    for step in range(distance + 1):
        t = step / distance
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        paint_brush_dab(image, x, y, size, color)


def erase_brush_dab(image, x: int, y: int, size: int):
    if size <= 1:
        if 0 <= x < image.width and 0 <= y < image.height:
            image.putpixel((x, y), (0, 0, 0, 0))
        return
    half = size // 2
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).ellipse((x - half, y - half, x + half, y + half), fill=255)
    image.paste((0, 0, 0, 0), (0, 0, image.width, image.height), mask)


def erase_brush_line(image, x1: int, y1: int, x2: int, y2: int, size: int):
    distance = max(1, int(math.hypot(x2 - x1, y2 - y1)))
    for step in range(distance + 1):
        t = step / distance
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        erase_brush_dab(image, x, y, size)
