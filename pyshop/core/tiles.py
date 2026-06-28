from dataclasses import dataclass
import math


DEFAULT_TILE_SIZE = 512


@dataclass(frozen=True)
class TileBox:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    def as_crop_box(self):
        return self.x, self.y, self.right, self.bottom


def iter_tile_boxes(width: int, height: int, tile_size: int = DEFAULT_TILE_SIZE):
    if width <= 0 or height <= 0:
        return
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            yield TileBox(x, y, min(tile_size, width - x), min(tile_size, height - y))


def iter_intersecting_tile_boxes(width: int, height: int, bounds, tile_size: int = DEFAULT_TILE_SIZE):
    if width <= 0 or height <= 0 or tile_size <= 0:
        return

    left, top, right, bottom = bounds
    left = max(0, min(width, math.floor(left)))
    top = max(0, min(height, math.floor(top)))
    right = max(0, min(width, math.ceil(right)))
    bottom = max(0, min(height, math.ceil(bottom)))
    if right <= left or bottom <= top:
        return

    start_x = (left // tile_size) * tile_size
    start_y = (top // tile_size) * tile_size
    for y in range(start_y, bottom, tile_size):
        for x in range(start_x, right, tile_size):
            yield TileBox(x, y, min(tile_size, width - x), min(tile_size, height - y))
