import warnings

from PIL import Image, UnidentifiedImageError

from .layer import Layer


MAX_DOCUMENT_PIXELS = 100_000_000


class ImageOpenError(RuntimeError):
    pass


def create_document_layers(width: int, height: int, background_rgba):
    background = Layer("Background", width, height)
    background.image.paste(background_rgba, (0, 0, width, height))
    return [background]


def image_document_layers(image):
    return [Layer("Background", image=image)]


def flattened_document_layers(composite_image):
    return [Layer("Background", image=composite_image)]


def open_raster_image(path, max_pixels: int = MAX_DOCUMENT_PIXELS):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                width, height = image.size
                pixels = width * height
                if pixels > max_pixels:
                    raise ImageOpenError(
                        f"Image is too large to open safely ({width}x{height}, {pixels:,} pixels; "
                        f"limit is {max_pixels:,} pixels)."
                    )
                image.load()
                return image.convert("RGBA")
    except ImageOpenError:
        raise
    except Image.DecompressionBombWarning as exc:
        raise ImageOpenError(f"Image is too large to open safely: {exc}") from exc
    except Image.DecompressionBombError as exc:
        raise ImageOpenError(f"Image is too large to open safely: {exc}") from exc
    except UnidentifiedImageError as exc:
        raise ImageOpenError(f"Unsupported or damaged image file: {path}") from exc
    except OSError as exc:
        raise ImageOpenError(f"Failed to read image file: {exc}") from exc
