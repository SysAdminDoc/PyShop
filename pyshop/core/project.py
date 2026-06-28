import json
import os
import tempfile
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .document import MAX_DOCUMENT_PIXELS
from .layer import Layer
from .macros import macro_steps_from_records, macro_steps_to_records


PROJECT_FILE_SUFFIX = ".pyshop"
PROJECT_FORMAT_VERSION = 1
PROJECT_MANIFEST_NAME = "manifest.json"


class ProjectFormatError(RuntimeError):
    pass


@dataclass
class ProjectState:
    layers: list
    active_layer_index: int
    selection_mask: object | None
    channel_visibility: dict
    guides: list
    current_path: list
    current_path_closed: bool
    macro_steps: list
    document_size: tuple


def save_project(
    path,
    layers,
    active_layer_index: int = 0,
    selection_mask=None,
    channel_visibility: dict | None = None,
    guides=None,
    current_path=None,
    current_path_closed: bool = False,
    macro_steps=None,
    max_pixels: int = MAX_DOCUMENT_PIXELS,
):
    if not layers:
        raise ProjectFormatError("Cannot save an empty project.")

    width, height = layers[0].image.size
    _validate_pixel_count(width, height, max_pixels, "Project")
    for layer in layers:
        _validate_pixel_count(layer.image.width, layer.image.height, max_pixels, f"Layer '{layer.name}'")
        if layer.mask is not None:
            _validate_pixel_count(layer.mask.width, layer.mask.height, max_pixels, f"Mask for '{layer.name}'")
    if selection_mask is not None:
        _validate_pixel_count(selection_mask.width, selection_mask.height, max_pixels, "Selection mask")

    path = Path(path)
    if path.suffix.lower() != PROJECT_FILE_SUFFIX:
        path = path.with_suffix(PROJECT_FILE_SUFFIX)
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)

    def write_archive(archive):
        layer_records = []
        for index, layer in enumerate(layers):
            image_name = f"layers/{index:04d}.png"
            archive.writestr(image_name, _image_png_bytes(layer.image, "RGBA"))
            mask_name = None
            if layer.mask is not None:
                mask_name = f"masks/{index:04d}.png"
                archive.writestr(mask_name, _image_png_bytes(layer.mask, "L"))
            layer_records.append(_layer_record(layer, image_name, mask_name))

        selection_name = None
        if selection_mask is not None:
            selection_name = "selection/selection.png"
            archive.writestr(selection_name, _image_png_bytes(selection_mask, "L"))

        manifest = {
            "format": "pyshop-project",
            "format_version": PROJECT_FORMAT_VERSION,
            "document": {"width": width, "height": height},
            "active_layer_index": int(active_layer_index),
            "selection_mask": selection_name,
            "channel_visibility": _channel_visibility(channel_visibility),
            "guides": _guides(guides),
            "current_path": _path_points(current_path),
            "current_path_closed": bool(current_path_closed),
            "macro_steps": macro_steps_to_records(macro_steps),
            "layers": layer_records,
        }
        archive.writestr(PROJECT_MANIFEST_NAME, json.dumps(manifest, indent=2, sort_keys=True))

    _write_zip_atomic(path, write_archive)
    return path


def load_project(path, max_pixels: int = MAX_DOCUMENT_PIXELS) -> ProjectState:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            manifest = _read_manifest(archive)
            _validate_manifest(manifest)
            document = manifest.get("document", {})
            width = int(document.get("width", 0))
            height = int(document.get("height", 0))
            _validate_pixel_count(width, height, max_pixels, "Project")

            layers = []
            for layer_record in manifest.get("layers", []):
                layers.append(_load_layer(archive, layer_record, max_pixels))
            if not layers:
                raise ProjectFormatError("Project contains no layers.")

            active = int(manifest.get("active_layer_index", 0))
            active = max(0, min(active, len(layers) - 1))
            return ProjectState(
                layers=layers,
                active_layer_index=active,
                selection_mask=_load_image(archive, manifest["selection_mask"], "L", max_pixels)
                if manifest.get("selection_mask")
                else None,
                channel_visibility=_channel_visibility(manifest.get("channel_visibility")),
                guides=_guides(manifest.get("guides")),
                current_path=_path_points(manifest.get("current_path")),
                current_path_closed=bool(manifest.get("current_path_closed", False)),
                macro_steps=macro_steps_from_records(manifest.get("macro_steps", [])),
                document_size=(width, height),
            )
    except ProjectFormatError:
        raise
    except (zipfile.BadZipFile, KeyError, OSError, ValueError, TypeError, UnidentifiedImageError) as exc:
        raise ProjectFormatError(f"Failed to read PyShop project: {exc}") from exc


def is_project_path(path) -> bool:
    return str(path).lower().endswith(PROJECT_FILE_SUFFIX)


def _validate_pixel_count(width: int, height: int, max_pixels: int, label: str):
    pixels = width * height
    if width < 1 or height < 1:
        raise ProjectFormatError(f"{label} has invalid dimensions ({width}x{height}).")
    if pixels > max_pixels:
        raise ProjectFormatError(
            f"{label} is too large to open safely ({width}x{height}, {pixels:,} pixels; "
            f"limit is {max_pixels:,} pixels)."
        )


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


def _image_png_bytes(image, mode: str) -> bytes:
    buffer = BytesIO()
    image.convert(mode).save(buffer, "PNG")
    return buffer.getvalue()


def _load_image(archive, name: str, mode: str, max_pixels: int):
    with archive.open(name, "r") as handle:
        data = handle.read()
    with Image.open(BytesIO(data)) as image:
        _validate_pixel_count(image.width, image.height, max_pixels, name)
        image.load()
        return image.convert(mode)


def _read_manifest(archive) -> dict:
    with archive.open(PROJECT_MANIFEST_NAME, "r") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _validate_manifest(manifest: dict):
    if manifest.get("format") != "pyshop-project":
        raise ProjectFormatError("File is not a PyShop project.")
    version = int(manifest.get("format_version", 0))
    if version != PROJECT_FORMAT_VERSION:
        raise ProjectFormatError(f"Unsupported PyShop project format version: {version}.")


def _layer_record(layer, image_name: str, mask_name: str | None) -> dict:
    return {
        "name": layer.name,
        "visible": bool(layer.visible),
        "opacity": int(layer.opacity),
        "blend_mode": layer.blend_mode,
        "locked": bool(layer.locked),
        "mask_density": int(layer.mask_density),
        "mask_feather": int(layer.mask_feather),
        "clipping": bool(layer.clipping),
        "adjustment": _jsonable(layer.adjustment),
        "is_group": bool(layer.is_group),
        "group_id": layer.group_id,
        "group_expanded": bool(layer.group_expanded),
        "vector_shape": _jsonable(layer.vector_shape),
        "text_item": _jsonable(layer.text_item),
        "image": image_name,
        "mask": mask_name,
    }


def _load_layer(archive, record: dict, max_pixels: int) -> Layer:
    image = _load_image(archive, record["image"], "RGBA", max_pixels)
    layer = Layer(str(record.get("name") or "Layer"), image=image)
    layer.visible = bool(record.get("visible", True))
    layer.opacity = max(0, min(255, int(record.get("opacity", 255))))
    layer.blend_mode = str(record.get("blend_mode") or "Normal")
    layer.locked = bool(record.get("locked", False))
    mask_name = record.get("mask")
    layer.mask = _load_image(archive, mask_name, "L", max_pixels) if mask_name else None
    layer.mask_density = max(0, min(100, int(record.get("mask_density", 100))))
    layer.mask_feather = max(0, int(record.get("mask_feather", 0)))
    layer.clipping = bool(record.get("clipping", False))
    layer.adjustment = _restore_metadata(record.get("adjustment"))
    layer.is_group = bool(record.get("is_group", False))
    layer.group_id = record.get("group_id")
    layer.group_expanded = bool(record.get("group_expanded", True))
    layer.vector_shape = _restore_metadata(record.get("vector_shape"))
    layer.text_item = _restore_metadata(record.get("text_item"))
    return layer


def _jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    raise ProjectFormatError(f"Unsupported project metadata value: {type(value).__name__}")


def _restore_metadata(value, key: str | None = None):
    if isinstance(value, dict):
        return {item_key: _restore_metadata(item_value, item_key) for item_key, item_value in value.items()}
    if isinstance(value, list):
        restored = [_restore_metadata(item) for item in value]
        if key in {"box", "fill"}:
            return tuple(restored)
        return restored
    return value


def _channel_visibility(value) -> dict:
    value = value if isinstance(value, dict) else {}
    return {key: bool(value.get(key, True)) for key in ("red", "green", "blue", "alpha")}


def _guides(value) -> list:
    guides = []
    for item in value or []:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            orientation, position = item
        elif isinstance(item, dict):
            orientation, position = item.get("orientation"), item.get("position")
        else:
            continue
        if orientation in {"vertical", "horizontal"}:
            guides.append((orientation, int(position)))
    return guides


def _path_points(value) -> list:
    points = []
    for item in value or []:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            points.append((item[0], item[1]))
    return points

