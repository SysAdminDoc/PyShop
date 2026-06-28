import colorsys

import numpy as np
from PIL import Image


def _rgb_float(image: Image.Image):
    return np.array(image.convert("RGB"), dtype=np.float32) / 255.0


def _image_from_float(pixels):
    return Image.fromarray((np.clip(pixels, 0.0, 1.0) * 255).astype(np.uint8), "RGB")


def _color_dodge(base, top):
    return np.where(top >= 1.0, 1.0, np.clip(base / np.maximum(1.0 - top, 1e-6), 0.0, 1.0))


def _color_burn(base, top):
    return np.where(top <= 0.0, 0.0, 1.0 - np.clip((1.0 - base) / np.maximum(top, 1e-6), 0.0, 1.0))


def _hard_light(base, top):
    return np.where(top <= 0.5, 2.0 * base * top, 1.0 - 2.0 * (1.0 - base) * (1.0 - top))


def _soft_light(base, top):
    return np.where(top <= 0.5, base - (1.0 - 2.0 * top) * base * (1.0 - base), base + (2.0 * top - 1.0) * (np.sqrt(base) - base))


def _luminance(pixels):
    return pixels[..., 0] * 0.299 + pixels[..., 1] * 0.587 + pixels[..., 2] * 0.114


def _hsl_blend(base, top, mode):
    base_flat = base.reshape(-1, 3)
    top_flat = top.reshape(-1, 3)
    output = []
    for base_rgb, top_rgb in zip(base_flat, top_flat):
        base_h, base_l, base_s = colorsys.rgb_to_hls(*base_rgb)
        top_h, top_l, top_s = colorsys.rgb_to_hls(*top_rgb)
        if mode == "Hue":
            output.append(colorsys.hls_to_rgb(top_h, base_l, base_s))
        elif mode == "Saturation":
            output.append(colorsys.hls_to_rgb(base_h, base_l, top_s))
        elif mode == "Color":
            output.append(colorsys.hls_to_rgb(top_h, base_l, top_s))
        else:
            output.append(colorsys.hls_to_rgb(base_h, top_l, base_s))
    return np.array(output, dtype=np.float32).reshape(base.shape)


def _blend_pixels(base, top, mode: str):
    if mode == "Multiply":
        return base * top
    if mode == "Screen":
        return 1.0 - (1.0 - base) * (1.0 - top)
    if mode == "Overlay":
        return np.where(base <= 0.5, 2.0 * base * top, 1.0 - 2.0 * (1.0 - base) * (1.0 - top))
    if mode == "Soft Light":
        return _soft_light(base, top)
    if mode == "Hard Light":
        return _hard_light(base, top)
    if mode == "Vivid Light":
        return np.where(top <= 0.5, _color_burn(base, 2.0 * top), _color_dodge(base, 2.0 * (top - 0.5)))
    if mode == "Linear Light":
        return np.clip(base + 2.0 * top - 1.0, 0.0, 1.0)
    if mode == "Pin Light":
        return np.where(top <= 0.5, np.minimum(base, 2.0 * top), np.maximum(base, 2.0 * (top - 0.5)))
    if mode == "Hard Mix":
        return (_blend_pixels(base, top, "Vivid Light") >= 0.5).astype(np.float32)
    if mode == "Darken":
        return np.minimum(base, top)
    if mode == "Lighten":
        return np.maximum(base, top)
    if mode == "Darker Color":
        return np.where(_luminance(base)[..., None] <= _luminance(top)[..., None], base, top)
    if mode == "Lighter Color":
        return np.where(_luminance(base)[..., None] >= _luminance(top)[..., None], base, top)
    if mode == "Difference":
        return np.abs(base - top)
    if mode == "Exclusion":
        return base + top - 2.0 * base * top
    if mode == "Subtract":
        return np.clip(base - top, 0.0, 1.0)
    if mode == "Divide":
        return np.clip(base / np.maximum(top, 1e-6), 0.0, 1.0)
    if mode == "Color Dodge":
        return _color_dodge(base, top)
    if mode == "Color Burn":
        return _color_burn(base, top)
    if mode == "Linear Dodge (Add)":
        return np.clip(base + top, 0.0, 1.0)
    if mode == "Linear Burn":
        return np.clip(base + top - 1.0, 0.0, 1.0)
    if mode in {"Hue", "Saturation", "Color", "Luminosity"}:
        return _hsl_blend(base, top, mode)
    return top


def blend_layers(base: Image.Image, top: Image.Image, mode: str) -> Image.Image:
    if mode == "Normal":
        result = base.copy()
        result.paste(top, (0, 0), top)
        return result

    blended = _image_from_float(_blend_pixels(_rgb_float(base), _rgb_float(top), mode))
    _, _, _, top_alpha = top.split()
    result = base.copy()
    blended_rgba = blended.convert("RGBA")
    blended_rgba.putalpha(top_alpha)
    result.paste(blended_rgba, (0, 0), blended_rgba)
    return result
