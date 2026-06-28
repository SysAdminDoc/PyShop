from pathlib import Path

from PIL import Image, ImageCms

from .document import MAX_DOCUMENT_PIXELS


RAW_EXTENSIONS = {
    ".3fr",
    ".arw",
    ".cr2",
    ".cr3",
    ".dcr",
    ".dng",
    ".erf",
    ".kdc",
    ".mef",
    ".mos",
    ".mrw",
    ".nef",
    ".orf",
    ".pef",
    ".raf",
    ".raw",
    ".rw2",
    ".sr2",
    ".srf",
    ".srw",
    ".x3f",
}


class RAWImportError(RuntimeError):
    pass


def is_raw_path(path) -> bool:
    return Path(path).suffix.lower() in RAW_EXTENSIONS


def load_raw_image(path, max_pixels: int = MAX_DOCUMENT_PIXELS):
    try:
        import rawpy
    except ImportError as exc:
        raise RAWImportError("RAW import requires rawpy. Install PyShop requirements before opening camera RAW files.") from exc

    try:
        with rawpy.imread(str(path)) as raw:
            rgb = raw.postprocess(
                use_camera_wb=True,
                output_bps=8,
                output_color=rawpy.ColorSpace.sRGB,
            )
    except Exception as exc:
        raise RAWImportError(f"Failed to decode RAW image: {exc}") from exc

    height, width = rgb.shape[:2]
    pixels = width * height
    if pixels > max_pixels:
        raise RAWImportError(
            f"RAW image is too large to open safely ({width}x{height}, {pixels:,} pixels; "
            f"limit is {max_pixels:,} pixels)."
        )

    image = Image.fromarray(rgb, "RGB").convert("RGBA")
    profile = srgb_profile_bytes()
    if profile:
        image.info["icc_profile"] = profile
    return image


def srgb_profile_bytes() -> bytes | None:
    try:
        return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    except Exception:
        return None
