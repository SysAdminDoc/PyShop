from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .channels import apply_channel_visibility
from .compositor import composite_layers
from .document import ImageOpenError, open_raster_image
from .ora import is_ora_path, load_ora
from .project import is_project_path, load_project
from .psd import load_psd_layers
from .raw import is_raw_path, load_raw_image
from .safeio import save_image_atomic


@dataclass(frozen=True)
class ExportPreset:
    name: str
    format_name: str
    extension: str
    quality: int | None = None
    lossless: bool | None = None
    include_icc: bool = True


DEFAULT_EXPORT_PRESETS = (
    ExportPreset("PNG - lossless", "PNG", ".png"),
    ExportPreset("JPEG - high quality", "JPEG", ".jpg", quality=92),
    ExportPreset("WebP - high quality", "WEBP", ".webp", quality=90),
    ExportPreset("WebP - lossless", "WEBP", ".webp", lossless=True),
)


def preset_by_name(name: str) -> ExportPreset:
    for preset in DEFAULT_EXPORT_PRESETS:
        if preset.name == name:
            return preset
    raise ValueError(f"Unknown export preset: {name}")


def export_path_for_preset(path, preset: ExportPreset) -> Path:
    path = Path(path)
    if path.suffix.lower() != preset.extension:
        path = path.with_suffix(preset.extension)
    return path


def export_image_with_preset(path, image, preset: ExportPreset, color_profile: bytes | None = None) -> Path:
    output_path = export_path_for_preset(path, preset)
    output_image = _image_for_format(image, preset.format_name)
    save_kwargs = _save_kwargs_for_preset(preset, color_profile)
    return save_image_atomic(output_path, output_image, preset.format_name, **save_kwargs)


def batch_export_images(input_paths, output_dir, preset: ExportPreset, progress_callback=None, is_cancelled=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [Path(path) for path in input_paths]
    outputs = []
    total = max(1, len(paths))
    for index, input_path in enumerate(paths, start=1):
        if is_cancelled and is_cancelled():
            return outputs
        if progress_callback:
            progress_callback(f"Exporting {input_path.name}", int((index - 1) * 80 / total) + 10)
        image, color_profile = load_exportable_image(input_path)
        output_path = output_dir / f"{input_path.stem}{preset.extension}"
        outputs.append(export_image_with_preset(output_path, image, preset, color_profile))
    return outputs


def load_exportable_image(path):
    path = Path(path)
    lower_path = str(path).lower()
    if is_project_path(path):
        state = load_project(path)
        composite = composite_layers(state.layers)
        if composite is None:
            raise ImageOpenError("Project contains no renderable layers.")
        return apply_channel_visibility(composite, state.channel_visibility), state.color_profile
    if is_ora_path(path):
        result = load_ora(path)
        composite = composite_layers(result.layers)
        if composite is None:
            raise ImageOpenError("OpenRaster file contains no renderable layers.")
        return composite, None
    if lower_path.endswith(".psd"):
        layers = load_psd_layers(path)
        composite = composite_layers(layers)
        if composite is None:
            raise ImageOpenError("PSD contains no renderable layers.")
        return composite, None
    if is_raw_path(path):
        image = load_raw_image(path)
        return image, image.info.get("icc_profile")
    image = open_raster_image(path)
    return image, image.info.get("icc_profile")


def _save_kwargs_for_preset(preset: ExportPreset, color_profile: bytes | None) -> dict:
    kwargs = {}
    if preset.quality is not None:
        kwargs["quality"] = preset.quality
    if preset.lossless is not None:
        kwargs["lossless"] = preset.lossless
    if preset.include_icc and color_profile:
        kwargs["icc_profile"] = color_profile
    return kwargs


def _image_for_format(image, format_name: str):
    if format_name == "JPEG":
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        background.alpha_composite(rgba)
        return background.convert("RGB")
    if format_name in {"PNG", "WEBP"}:
        return image.convert("RGBA")
    return image
