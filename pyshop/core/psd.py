from PIL import Image

from .document import MAX_DOCUMENT_PIXELS
from .layer import Layer


class PSDImportError(RuntimeError):
    pass


class PSDExportError(RuntimeError):
    pass


def _require_psd_tools():
    try:
        from psd_tools import PSDImage
    except ImportError as exc:
        raise PSDImportError("PSD support requires psd-tools. Install requirements.txt before opening PSD files.") from exc
    return PSDImage


def load_psd_layers(path, max_pixels: int = MAX_DOCUMENT_PIXELS):
    PSDImage = _require_psd_tools()

    try:
        psd = PSDImage.open(path)
    except Exception as exc:
        raise PSDImportError(f"Failed to read PSD file: {exc}") from exc
    width, height = psd.size
    pixels = width * height
    if pixels > max_pixels:
        raise PSDImportError(
            f"PSD is too large to open safely ({width}x{height}, {pixels:,} pixels; "
            f"limit is {max_pixels:,} pixels)."
        )

    layers = []
    for psd_layer in psd.descendants():
        if psd_layer.is_group():
            continue
        layer_image = psd_layer.composite()
        if layer_image is None:
            continue
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        rgba = layer_image.convert("RGBA")
        left = getattr(psd_layer, "left", 0)
        top = getattr(psd_layer, "top", 0)
        canvas.paste(rgba, (left, top), rgba)
        layer = Layer(psd_layer.name or "PSD Layer", image=canvas)
        layer.visible = psd_layer.visible
        layer.opacity = int(psd_layer.opacity * 255 / 255)
        layers.append(layer)
    if layers:
        return layers
    composite = psd.composite()
    if composite is None:
        return [Layer("Background", width, height)]
    return [Layer("Background", image=composite.convert("RGBA"))]


def save_flattened_psd(path, image):
    PSDImage = _require_psd_tools()

    try:
        PSDImage.frompil(image.convert("RGBA")).save(path)
    except Exception as exc:
        raise PSDExportError(f"Failed to export flattened PSD: {exc}") from exc
