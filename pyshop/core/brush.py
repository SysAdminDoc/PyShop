import math
import random
from dataclasses import dataclass

from PIL import Image, ImageDraw


@dataclass(frozen=True)
class BrushSettings:
    size: int = 10
    opacity: int = 255
    spacing: int = 25
    smoothing: int = 0
    scatter: int = 0
    texture: int = 0
    color_jitter: int = 0
    pressure_size: bool = False
    pressure_opacity: bool = False

    def effective_size(self, pressure: float = 1.0) -> int:
        pressure = max(0.01, min(1.0, pressure))
        scale = pressure if self.pressure_size else 1.0
        return max(1, int(round(self.size * scale)))

    def effective_opacity(self, pressure: float = 1.0) -> int:
        pressure = max(0.01, min(1.0, pressure))
        scale = pressure if self.pressure_opacity else 1.0
        return max(0, min(255, int(round(self.opacity * scale))))

    def spacing_pixels(self, pressure: float = 1.0) -> float:
        return max(1.0, self.effective_size(pressure) * max(1, self.spacing) / 100)


def _clamped_channel(value: int) -> int:
    return max(0, min(255, value))


def _dynamic_color(color, settings: BrushSettings, dab_index: int):
    red, green, blue, alpha = color
    if settings.color_jitter <= 0 and settings.texture <= 0:
        return color

    rng = random.Random(dab_index)
    if settings.color_jitter > 0:
        amount = max(0, min(100, settings.color_jitter)) / 100
        spread = int(255 * amount)
        red = _clamped_channel(red + rng.randint(-spread, spread))
        green = _clamped_channel(green + rng.randint(-spread, spread))
        blue = _clamped_channel(blue + rng.randint(-spread, spread))

    if settings.texture > 0:
        texture = max(0, min(100, settings.texture)) / 100
        alpha = _clamped_channel(int(alpha * (1 - texture * rng.random())))

    return red, green, blue, alpha


def smoothed_brush_point(previous, current, smoothing: int):
    amount = max(0, min(95, smoothing)) / 100
    if amount <= 0:
        return current
    return (
        previous[0] * amount + current[0] * (1 - amount),
        previous[1] * amount + current[1] * (1 - amount),
    )


def iter_brush_dabs(x1: int, y1: int, x2: int, y2: int, settings: BrushSettings, pressure: float = 1.0):
    size = settings.effective_size(pressure)
    spacing = settings.spacing_pixels(pressure)
    distance = math.hypot(x2 - x1, y2 - y1)
    if distance <= 0:
        yield x1, y1, size, 0
        return
    steps = max(1, int(distance / spacing))
    scatter_radius = size * max(0, settings.scatter) / 100

    for step in range(steps + 1):
        t = step / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        if scatter_radius > 0:
            rng = random.Random(f"{x1}:{y1}:{x2}:{y2}:{step}:{settings.scatter}")
            angle = rng.random() * math.tau
            radius = rng.random() * scatter_radius
            x += math.cos(angle) * radius
            y += math.sin(angle) * radius
        yield int(round(x)), int(round(y)), size, step


def paint_brush_dab(image, x: int, y: int, size: int, color):
    if size <= 1:
        if 0 <= x < image.width and 0 <= y < image.height:
            image.putpixel((x, y), color)
        return
    half = size // 2
    ImageDraw.Draw(image).ellipse((x - half, y - half, x + half, y + half), fill=color)


def paint_brush_stroke(image, x1: int, y1: int, x2: int, y2: int, settings: BrushSettings, color, pressure: float = 1.0):
    opacity = settings.effective_opacity(pressure)
    base_color = (color[0], color[1], color[2], min(color[3], opacity))
    for x, y, size, dab_index in iter_brush_dabs(x1, y1, x2, y2, settings, pressure):
        paint_brush_dab(image, x, y, size, _dynamic_color(base_color, settings, dab_index))


def paint_brush_line(image, x1: int, y1: int, x2: int, y2: int, size: int, color):
    paint_brush_stroke(image, x1, y1, x2, y2, BrushSettings(size=size, opacity=color[3]), color)


def erase_brush_dab(image, x: int, y: int, size: int):
    if size <= 1:
        if 0 <= x < image.width and 0 <= y < image.height:
            image.putpixel((x, y), (0, 0, 0, 0))
        return
    half = size // 2
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).ellipse((x - half, y - half, x + half, y + half), fill=255)
    image.paste((0, 0, 0, 0), (0, 0, image.width, image.height), mask)


def erase_brush_stroke(image, x1: int, y1: int, x2: int, y2: int, settings: BrushSettings, pressure: float = 1.0):
    for x, y, size, _dab_index in iter_brush_dabs(x1, y1, x2, y2, settings, pressure):
        erase_brush_dab(image, x, y, size)


def erase_brush_line(image, x1: int, y1: int, x2: int, y2: int, size: int):
    erase_brush_stroke(image, x1, y1, x2, y2, BrushSettings(size=size))
