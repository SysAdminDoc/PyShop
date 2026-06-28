import os
import tempfile
from pathlib import Path

from PIL import Image

from .compositor import render_layer_tile
from .document import MAX_DOCUMENT_PIXELS
from .layer import Layer


class PSDImportError(RuntimeError):
    pass


class PSDExportError(RuntimeError):
    pass


PSD_BLEND_MODES = {
    "Normal": "NORMAL",
    "Multiply": "MULTIPLY",
    "Screen": "SCREEN",
    "Overlay": "OVERLAY",
    "Darken": "DARKEN",
    "Lighten": "LIGHTEN",
    "Color Dodge": "COLOR_DODGE",
    "Color Burn": "COLOR_BURN",
    "Hard Light": "HARD_LIGHT",
    "Soft Light": "SOFT_LIGHT",
    "Difference": "DIFFERENCE",
    "Exclusion": "EXCLUSION",
    "Hue": "HUE",
    "Saturation": "SATURATION",
    "Color": "COLOR",
    "Luminosity": "LUMINOSITY",
}


def _require_psd_tools():
    try:
        from psd_tools import PSDImage
    except ImportError as exc:
        raise PSDImportError("PSD support requires psd-tools. Install requirements.txt before opening PSD files.") from exc
    return PSDImage


def _blend_mode_constant(blend_mode):
    try:
        from psd_tools.constants import BlendMode
    except ImportError as exc:
        raise PSDExportError("PSD support requires psd-tools constants.") from exc
    name = PSD_BLEND_MODES.get(blend_mode, "NORMAL")
    return getattr(BlendMode, name, BlendMode.NORMAL)


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
        psd_image = PSDImage.frompil(image.convert("RGBA"))
        _save_psd_atomic(path, psd_image)
    except Exception as exc:
        raise PSDExportError(f"Failed to export flattened PSD: {exc}") from exc


def save_layered_psd(path, layers, max_pixels: int = MAX_DOCUMENT_PIXELS):
    PSDImage = _require_psd_tools()
    if not layers:
        raise PSDExportError("Cannot export an empty PSD.")
    width, height = layers[0].image.size
    pixels = width * height
    if pixels > max_pixels:
        raise PSDExportError(
            f"PSD is too large to export safely ({width}x{height}, {pixels:,} pixels; "
            f"limit is {max_pixels:,} pixels)."
        )

    report = []
    try:
        psd = PSDImage.new("RGBA", (width, height), color=(0, 0, 0, 0))
        for layer in layers:
            if layer.is_group:
                report.append(f"{layer.name}: PSD group marker exported as flat layer order only")
                continue
            if layer.adjustment:
                report.append(f"{layer.name}: adjustment layer is not exported as live PSD adjustment")
                continue
            if layer.effect:
                report.append(f"{layer.name}: effect layer is not exported as live PSD effect")
                continue

            image = render_layer_tile(layer, (0, 0, width, height)) if (layer.vector_shape or layer.text_item) else layer.image
            if layer.vector_shape:
                report.append(f"{layer.name}: vector shape exported as raster pixels")
            if layer.text_item:
                report.append(f"{layer.name}: text layer exported as raster pixels")
            if layer.blend_mode not in PSD_BLEND_MODES:
                report.append(f"{layer.name}: unsupported PSD blend mode exported as Normal ({layer.blend_mode})")
            if layer.clipping:
                report.append(f"{layer.name}: clipping mask relationship is not exported")
            if layer.group_id:
                report.append(f"{layer.name}: group membership is not exported")

            psd_layer = psd.create_pixel_layer(
                image.convert("RGBA"),
                name=layer.name,
                opacity=max(0, min(255, int(layer.opacity))),
                blend_mode=_blend_mode_constant(layer.blend_mode),
            )
            psd_layer.visible = bool(layer.visible)
            if layer.mask is not None:
                psd_layer.create_mask(layer.mask.convert("L"))
                if layer.mask_density != 100 or layer.mask_feather:
                    report.append(f"{layer.name}: mask pixels exported; density/feather are PyShop-only")
            psd.append(psd_layer)
        _save_psd_atomic(path, psd)
        return report
    except Exception as exc:
        if isinstance(exc, PSDExportError):
            raise
        raise PSDExportError(f"Failed to export layered PSD: {exc}") from exc


def _save_psd_atomic(path, psd_image):
    path = Path(path)
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=path.suffix or ".psd", dir=str(path.parent or "."))
    os.close(fd)
    try:
        psd_image.save(temp_name)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
