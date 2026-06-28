from PIL import Image, ImageFilter

from .adjustments import apply_adjustment
from .blend import blend_layers
from .effects import apply_effect
from .tiles import TileBox
from .text import render_text_tile
from .vector import render_vector_shape_tile


def _apply_opacity(image: Image.Image, opacity: int) -> Image.Image:
    if opacity >= 255:
        return image
    result = image.copy()
    red, green, blue, alpha = result.split()
    alpha = alpha.point(lambda value: int(value * opacity / 255))
    return Image.merge("RGBA", (red, green, blue, alpha))


def _effective_mask(layer, crop_box):
    if layer.mask is None:
        return None
    mask = layer.mask.crop(crop_box) if crop_box else layer.mask.copy()
    if layer.mask_feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(layer.mask_feather))
    density = max(0, min(100, layer.mask_density))
    if density < 100:
        mask = mask.point(lambda value: int(255 - ((255 - value) * density / 100)))
    return mask


def _apply_mask(image: Image.Image, layer, crop_box) -> Image.Image:
    mask = _effective_mask(layer, crop_box)
    if mask is None:
        return image
    red, green, blue, alpha = image.split()
    alpha = Image.composite(alpha, Image.new("L", alpha.size, 0), mask)
    return Image.merge("RGBA", (red, green, blue, alpha))


def _clip_to_base(image: Image.Image, base: Image.Image) -> Image.Image:
    red, green, blue, alpha = image.split()
    base_alpha = base.getchannel("A")
    alpha = Image.composite(alpha, Image.new("L", alpha.size, 0), base_alpha)
    return Image.merge("RGBA", (red, green, blue, alpha))


def _apply_group_controls(image: Image.Image, group, crop_box) -> Image.Image:
    image = _apply_mask(image, group, crop_box)
    return _apply_opacity(image, group.opacity)


def _adjustment_effect_mask(layer, base: Image.Image, crop_box):
    mask = Image.new("L", base.size, max(0, min(255, layer.opacity)))
    layer_mask = _effective_mask(layer, crop_box)
    if layer_mask is not None:
        mask = Image.composite(mask, Image.new("L", mask.size, 0), layer_mask)
    if layer.clipping:
        mask = Image.composite(mask, Image.new("L", mask.size, 0), base.getchannel("A"))
    return mask


def render_layer_tile(layer, crop_box) -> Image.Image:
    if layer.vector_shape:
        image = render_vector_shape_tile(layer.vector_shape, crop_box, (crop_box[2] - crop_box[0], crop_box[3] - crop_box[1]))
    elif layer.text_item:
        image = render_text_tile(layer.text_item, crop_box, (crop_box[2] - crop_box[0], crop_box[3] - crop_box[1]))
    else:
        image = layer.image.crop(crop_box)
    image = _apply_mask(image, layer, crop_box)
    return _apply_opacity(image, layer.opacity)


def composite_layers(layers) -> Image.Image | None:
    if not layers:
        return None
    width, height = layers[0].image.size
    return composite_layers_tile(layers, TileBox(0, 0, width, height))


def composite_layers_tile(layers, tile_box) -> Image.Image:
    result = Image.new("RGBA", (tile_box.width, tile_box.height), (0, 0, 0, 0))
    crop_box = tile_box.as_crop_box()
    index = 0
    while index < len(layers):
        layer = layers[index]
        index += 1
        if not layer.visible:
            if layer.is_group:
                while index < len(layers) and layers[index].group_id == layer.group_id:
                    index += 1
            continue
        if layer.is_group:
            children = []
            while index < len(layers) and layers[index].group_id == layer.group_id:
                children.append(layers[index])
                index += 1
            if children:
                group_tile = composite_layers_tile(children, tile_box)
                group_tile = _apply_group_controls(group_tile, layer, crop_box)
                if layer.clipping:
                    group_tile = _clip_to_base(group_tile, result)
                result = blend_layers(result, group_tile, layer.blend_mode)
            continue
        if layer.adjustment:
            adjusted = apply_adjustment(result, layer.adjustment)
            mask = _adjustment_effect_mask(layer, result, crop_box)
            result = Image.composite(adjusted, result, mask)
            continue
        if layer.effect:
            effected = apply_effect(result, layer.effect)
            mask = _adjustment_effect_mask(layer, result, crop_box)
            result = Image.composite(effected, result, mask)
            continue
        tile = render_layer_tile(layer, crop_box)
        if layer.clipping:
            tile = _clip_to_base(tile, result)
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
