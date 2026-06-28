import os
import tempfile
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image, UnidentifiedImageError

from .compositor import composite_layers
from .document import MAX_DOCUMENT_PIXELS
from .layer import Layer


ORA_FILE_SUFFIX = ".ora"
ORA_MIMETYPE = "image/openraster"

BLEND_TO_ORA = {
    "Normal": "svg:src-over",
    "Multiply": "svg:multiply",
    "Screen": "svg:screen",
    "Overlay": "svg:overlay",
    "Darken": "svg:darken",
    "Lighten": "svg:lighten",
    "Color Dodge": "svg:color-dodge",
    "Color Burn": "svg:color-burn",
    "Difference": "svg:difference",
}
ORA_TO_BLEND = {value: key for key, value in BLEND_TO_ORA.items()}


class ORAFormatError(RuntimeError):
    pass


@dataclass
class ORAImportResult:
    layers: list
    compatibility_report: list[str]


def save_ora(path, layers, composite_image=None, max_pixels: int = MAX_DOCUMENT_PIXELS) -> list[str]:
    if not layers:
        raise ORAFormatError("Cannot export an empty OpenRaster document.")
    width, height = layers[0].image.size
    _validate_pixels(width, height, max_pixels, "OpenRaster document")
    path = Path(path)
    if path.suffix.lower() != ORA_FILE_SUFFIX:
        path = path.with_suffix(ORA_FILE_SUFFIX)
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)

    report = _compatibility_report(layers)

    def write_archive(archive):
        archive.writestr("mimetype", ORA_MIMETYPE, compress_type=zipfile.ZIP_STORED)
        image = ElementTree.Element("image", {"w": str(width), "h": str(height)})
        stack = ElementTree.SubElement(image, "stack")
        for index, layer in enumerate(layers):
            layer_src = f"data/layer{index:04d}.png"
            archive.writestr(layer_src, _png_bytes(layer.image, "RGBA"))
            attrs = {
                "name": layer.name,
                "src": layer_src,
                "x": "0",
                "y": "0",
                "visibility": "visible" if layer.visible else "hidden",
                "opacity": f"{max(0, min(255, layer.opacity)) / 255:.6f}",
                "composite-op": BLEND_TO_ORA.get(layer.blend_mode, "svg:src-over"),
                "pyshop-index": str(index),
                "pyshop-blend-mode": layer.blend_mode,
            }
            if layer.mask is not None:
                mask_src = f"data/mask{index:04d}.png"
                archive.writestr(mask_src, _png_bytes(layer.mask, "L"))
                attrs["pyshop-mask-src"] = mask_src
                attrs["pyshop-mask-density"] = str(layer.mask_density)
                attrs["pyshop-mask-feather"] = str(layer.mask_feather)
            ElementTree.SubElement(stack, "layer", attrs)
        archive.writestr("stack.xml", ElementTree.tostring(image, encoding="utf-8", xml_declaration=True))
        merged = composite_image if composite_image is not None else composite_layers(layers)
        if merged is not None:
            archive.writestr("mergedimage.png", _png_bytes(merged, "RGBA"))

    _write_zip_atomic(path, write_archive)
    return report


def load_ora(path, max_pixels: int = MAX_DOCUMENT_PIXELS) -> ORAImportResult:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            mimetype = archive.read("mimetype").decode("utf-8").strip()
            if mimetype != ORA_MIMETYPE:
                raise ORAFormatError("File is not an OpenRaster document.")
            root = ElementTree.fromstring(archive.read("stack.xml"))
            width = int(root.attrib.get("w", "0"))
            height = int(root.attrib.get("h", "0"))
            _validate_pixels(width, height, max_pixels, "OpenRaster document")
            records = []
            for index, element in enumerate(root.findall(".//layer")):
                order = int(element.attrib.get("pyshop-index", index))
                records.append((order, element))
            layers = [_load_layer(archive, element, max_pixels) for _order, element in sorted(records, key=lambda item: item[0])]
            if not layers:
                raise ORAFormatError("OpenRaster document contains no layers.")
            return ORAImportResult(layers=layers, compatibility_report=_load_report(layers))
    except ORAFormatError:
        raise
    except (zipfile.BadZipFile, KeyError, OSError, ValueError, ElementTree.ParseError, UnidentifiedImageError) as exc:
        raise ORAFormatError(f"Failed to read OpenRaster document: {exc}") from exc


def is_ora_path(path) -> bool:
    return str(path).lower().endswith(ORA_FILE_SUFFIX)


def _load_layer(archive, element, max_pixels):
    image = _load_image(archive, element.attrib["src"], "RGBA", max_pixels)
    layer = Layer(element.attrib.get("name") or "OpenRaster Layer", image=image)
    layer.visible = element.attrib.get("visibility", "visible") != "hidden"
    layer.opacity = max(0, min(255, round(float(element.attrib.get("opacity", "1")) * 255)))
    layer.blend_mode = element.attrib.get("pyshop-blend-mode") or ORA_TO_BLEND.get(element.attrib.get("composite-op"), "Normal")
    mask_src = element.attrib.get("pyshop-mask-src")
    if mask_src:
        layer.mask = _load_image(archive, mask_src, "L", max_pixels)
        layer.mask_density = int(element.attrib.get("pyshop-mask-density", "100"))
        layer.mask_feather = int(element.attrib.get("pyshop-mask-feather", "0"))
    return layer


def _compatibility_report(layers):
    report = []
    for layer in layers:
        if layer.blend_mode not in BLEND_TO_ORA:
            report.append(f"{layer.name}: blend mode stored as PyShop extension ({layer.blend_mode})")
        if layer.mask is not None:
            report.append(f"{layer.name}: mask stored as PyShop extension")
        if layer.adjustment:
            report.append(f"{layer.name}: adjustment metadata is not portable in OpenRaster")
        if layer.effect:
            report.append(f"{layer.name}: effect metadata is not portable in OpenRaster")
        if layer.vector_shape:
            report.append(f"{layer.name}: vector shape exported as its current pixel layer only")
        if layer.text_item:
            report.append(f"{layer.name}: text metadata exported as its current pixel layer only")
        if layer.is_group or layer.group_id:
            report.append(f"{layer.name}: group structure stored as flat layer order")
        if layer.clipping:
            report.append(f"{layer.name}: clipping-mask relationship is not portable in OpenRaster")
    return report


def _load_report(layers):
    report = []
    for layer in layers:
        if layer.mask is not None:
            report.append(f"{layer.name}: restored PyShop mask extension")
        if layer.blend_mode not in BLEND_TO_ORA:
            report.append(f"{layer.name}: restored PyShop blend extension ({layer.blend_mode})")
    return report


def _validate_pixels(width: int, height: int, max_pixels: int, label: str):
    pixels = width * height
    if width < 1 or height < 1:
        raise ORAFormatError(f"{label} has invalid dimensions ({width}x{height}).")
    if pixels > max_pixels:
        raise ORAFormatError(
            f"{label} is too large to open safely ({width}x{height}, {pixels:,} pixels; "
            f"limit is {max_pixels:,} pixels)."
        )


def _png_bytes(image, mode):
    buffer = BytesIO()
    image.convert(mode).save(buffer, "PNG")
    return buffer.getvalue()


def _load_image(archive, name, mode, max_pixels):
    with archive.open(name, "r") as handle:
        data = handle.read()
    with Image.open(BytesIO(data)) as image:
        _validate_pixels(image.width, image.height, max_pixels, name)
        image.load()
        return image.convert(mode)


def _write_zip_atomic(path: Path, callback):
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent or "."))
    os.close(fd)
    try:
        with zipfile.ZipFile(temp_name, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            callback(archive)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
