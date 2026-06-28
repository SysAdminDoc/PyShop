import warnings
from dataclasses import dataclass, field

from PIL import Image, UnidentifiedImageError

from .layer import Layer


MAX_DOCUMENT_PIXELS = 100_000_000


class ImageOpenError(RuntimeError):
    pass


def default_channel_visibility():
    return {"red": True, "green": True, "blue": True, "alpha": True}


@dataclass
class Document:
    layers: list = field(default_factory=list)
    active_layer_index: int = 0
    selection_mask: object | None = None
    current_path: list = field(default_factory=list)
    current_path_closed: bool = False
    channel_visibility: dict = field(default_factory=default_channel_visibility)
    guides: list = field(default_factory=list)
    macro_steps: list = field(default_factory=list)
    file_path: str | None = None
    source_path: str | None = None
    color_profile: bytes | None = None
    dirty_revision: int = 0
    saved_revision: int = 0

    @property
    def dimensions(self) -> tuple[int, int]:
        if not self.layers:
            return (0, 0)
        return self.layers[0].image.size

    @property
    def has_unsaved_changes(self) -> bool:
        return self.dirty_revision != self.saved_revision

    def set_layers(self, layers):
        self.layers = list(layers)
        self.set_active_layer_index(self.active_layer_index)
        self.mark_dirty()

    def set_active_layer_index(self, index: int):
        if not self.layers:
            self.active_layer_index = 0
        else:
            self.active_layer_index = max(0, min(index, len(self.layers) - 1))

    def reset_metadata(self):
        self.selection_mask = None
        self.current_path = []
        self.current_path_closed = False
        self.channel_visibility = default_channel_visibility()
        self.guides = []
        self.macro_steps = []
        self.color_profile = None
        self.mark_dirty()

    def apply_project_state(self, state, path):
        self.layers = state.layers
        self.active_layer_index = state.active_layer_index
        self.selection_mask = state.selection_mask
        self.current_path = state.current_path
        self.current_path_closed = state.current_path_closed
        self.channel_visibility = state.channel_visibility
        self.guides = state.guides
        self.macro_steps = state.macro_steps
        self.color_profile = state.color_profile
        self.file_path = path
        self.source_path = path
        self.mark_saved()

    def project_save_kwargs(self):
        return {
            "layers": self.layers,
            "active_layer_index": self.active_layer_index,
            "selection_mask": self.selection_mask,
            "channel_visibility": self.channel_visibility,
            "guides": self.guides,
            "current_path": self.current_path,
            "current_path_closed": self.current_path_closed,
            "macro_steps": self.macro_steps,
            "color_profile": self.color_profile,
        }

    def mark_dirty(self):
        self.dirty_revision += 1

    def mark_saved(self):
        self.saved_revision = self.dirty_revision


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
                converted = image.convert("RGBA")
                converted.info.update(image.info)
                return converted
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
