from PIL import Image, ImageChops, ImageEnhance


def apply_adjustment(image: Image.Image, adjustment: dict) -> Image.Image:
    kind = adjustment.get("type")
    if kind == "brightness_contrast":
        result = image
        brightness = adjustment.get("brightness", 0)
        contrast = adjustment.get("contrast", 0)
        if brightness:
            result = ImageEnhance.Brightness(result).enhance(1 + brightness / 100)
        if contrast:
            result = ImageEnhance.Contrast(result).enhance(1 + contrast / 100)
        return result.convert("RGBA")
    if kind == "hue_saturation":
        hue = adjustment.get("hue", 0)
        saturation = adjustment.get("saturation", 0)
        lightness = adjustment.get("lightness", 0)
        red, green, blue, alpha = image.split()
        rgb = Image.merge("RGB", (red, green, blue))
        if saturation:
            rgb = ImageEnhance.Color(rgb).enhance(1 + saturation / 100)
        if lightness:
            rgb = ImageEnhance.Brightness(rgb).enhance(1 + lightness / 100)
        if hue:
            hue_channel, sat_channel, value_channel = rgb.convert("HSV").split()
            hue_channel = hue_channel.point(lambda value: (value + hue) % 256)
            rgb = Image.merge("HSV", (hue_channel, sat_channel, value_channel)).convert("RGB")
        red, green, blue = rgb.split()
        return Image.merge("RGBA", (red, green, blue, alpha))
    if kind == "invert":
        red, green, blue, alpha = image.split()
        return Image.merge("RGBA", (ImageChops.invert(red), ImageChops.invert(green), ImageChops.invert(blue), alpha))
    if kind == "grayscale":
        red, green, blue, alpha = image.split()
        gray = Image.merge("RGB", (red, green, blue)).convert("L").convert("RGB")
        red, green, blue = gray.split()
        return Image.merge("RGBA", (red, green, blue, alpha))
    return image
