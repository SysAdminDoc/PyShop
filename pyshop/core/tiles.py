from dataclasses import dataclass


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
