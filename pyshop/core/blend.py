import numpy as np
from PIL import Image, ImageChops


def blend_layers(base: Image.Image, top: Image.Image, mode: str) -> Image.Image:
    if mode == "Normal":
        result = base.copy()
        result.paste(top, (0, 0), top)
        return result
    if mode == "Multiply":
        blended = ImageChops.multiply(base.convert("RGB"), top.convert("RGB"))
    elif mode == "Screen":
        blended = ImageChops.screen(base.convert("RGB"), top.convert("RGB"))
    elif mode == "Overlay":
        base_pixels = np.array(base.convert("RGB"), dtype=np.float32) / 255
        top_pixels = np.array(top.convert("RGB"), dtype=np.float32) / 255
        low_mask = base_pixels < 0.5
        result_pixels = np.where(
            low_mask,
            2 * base_pixels * top_pixels,
            1 - 2 * (1 - base_pixels) * (1 - top_pixels),
        )
        blended = Image.fromarray((result_pixels * 255).clip(0, 255).astype(np.uint8), "RGB")
    elif mode == "Darken":
        blended = ImageChops.darker(base.convert("RGB"), top.convert("RGB"))
    elif mode == "Lighten":
        blended = ImageChops.lighter(base.convert("RGB"), top.convert("RGB"))
    elif mode == "Difference":
        blended = ImageChops.difference(base.convert("RGB"), top.convert("RGB"))
    elif mode == "Color Dodge":
        base_pixels = np.array(base.convert("RGB"), dtype=np.float32)
        top_pixels = np.array(top.convert("RGB"), dtype=np.float32)
        blended = Image.fromarray(
            np.where(top_pixels >= 255, 255, np.clip(base_pixels * 255 / (256 - top_pixels), 0, 255)).astype(np.uint8),
            "RGB",
        )
    elif mode == "Color Burn":
        base_pixels = np.array(base.convert("RGB"), dtype=np.float32)
        top_pixels = np.array(top.convert("RGB"), dtype=np.float32)
        blended = Image.fromarray(
            np.where(top_pixels <= 0, 0, np.clip(255 - (255 - base_pixels) * 255 / (top_pixels + 1), 0, 255)).astype(
                np.uint8
            ),
            "RGB",
        )
    else:
        result = base.copy()
        result.paste(top, (0, 0), top)
        return result

    _, _, _, top_alpha = top.split()
    result = base.copy()
    blended_rgba = blended.convert("RGBA")
    blended_rgba.putalpha(top_alpha)
    result.paste(blended_rgba, (0, 0), blended_rgba)
    return result
