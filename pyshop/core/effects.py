from PIL import Image, ImageFilter, ImageOps


def apply_effect(image: Image.Image, effect: dict) -> Image.Image:
    kind = effect.get("type")
    if kind == "gaussian_blur":
        return image.filter(ImageFilter.GaussianBlur(float(effect.get("radius", 3.0))))
    if kind == "box_blur":
        return image.filter(ImageFilter.BoxBlur(int(effect.get("radius", 3))))
    if kind == "motion_blur":
        size = max(1, int(effect.get("size", 10)))
        kernel = [0] * (size * size)
        center = size // 2
        for index in range(size):
            kernel[center * size + index] = 1
        return image.filter(ImageFilter.Kernel((size, size), kernel, scale=size))
    if kind == "sharpen":
        return image.filter(ImageFilter.SHARPEN)
    if kind == "unsharp_mask":
        return image.filter(
            ImageFilter.UnsharpMask(
                float(effect.get("radius", 2.0)),
                int(effect.get("percent", 150)),
                int(effect.get("threshold", 3)),
            )
        )
    if kind == "edge_detect":
        return image.filter(ImageFilter.FIND_EDGES)
    if kind == "emboss":
        return image.filter(ImageFilter.EMBOSS)
    if kind == "contour":
        return image.filter(ImageFilter.CONTOUR)
    if kind == "posterize":
        red, green, blue, alpha = image.split()
        rgb = ImageOps.posterize(Image.merge("RGB", (red, green, blue)), int(effect.get("bits", 4)))
        red, green, blue = rgb.split()
        return Image.merge("RGBA", (red, green, blue, alpha))
    if kind == "solarize":
        red, green, blue, alpha = image.split()
        rgb = ImageOps.solarize(Image.merge("RGB", (red, green, blue)), int(effect.get("threshold", 128)))
        red, green, blue = rgb.split()
        return Image.merge("RGBA", (red, green, blue, alpha))
    if kind == "pixelate":
        block_size = max(2, int(effect.get("block_size", 8)))
        width, height = image.size
        small = image.resize((max(1, width // block_size), max(1, height // block_size)), Image.NEAREST)
        return small.resize((width, height), Image.NEAREST)
    return image


def effect_label(effect: dict) -> str:
    labels = {
        "gaussian_blur": "Gaussian Blur",
        "box_blur": "Box Blur",
        "motion_blur": "Motion Blur",
        "sharpen": "Sharpen",
        "unsharp_mask": "Unsharp Mask",
        "edge_detect": "Edge Detect",
        "emboss": "Emboss",
        "contour": "Contour",
        "posterize": "Posterize",
        "solarize": "Solarize",
        "pixelate": "Pixelate",
    }
    return labels.get(effect.get("type"), "Effect")
