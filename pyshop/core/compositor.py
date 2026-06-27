from PIL import Image

from .blend import blend_layers


def _apply_opacity(image: Image.Image, opacity: int) -> Image.Image:
    if opacity >= 255:
        return image
    result = image.copy()
    red, green, blue, alpha = result.split()
    alpha = alpha.point(lambda value: int(value * opacity / 255))
    return Image.merge("RGBA", (red, green, blue, alpha))


def composite_layers_tile(layers, tile_box) -> Image.Image:
    result = Image.new("RGBA", (tile_box.width, tile_box.height), (0, 0, 0, 0))
    crop_box = tile_box.as_crop_box()
    for layer in layers:
        if not layer.visible:
            continue
        tile = layer.image.crop(crop_box)
        tile = _apply_opacity(tile, layer.opacity)
        result = blend_layers(result, tile, layer.blend_mode)
    return result


class TiledCompositeCache:
    def __init__(self):
        self._tiles = {}

    def invalidate(self):
        self._tiles.clear()

    def get_tile(self, layers, tile_box):
        key = tile_box.as_crop_box()
        if key not in self._tiles:
            self._tiles[key] = composite_layers_tile(layers, tile_box)
        return self._tiles[key]
