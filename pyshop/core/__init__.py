"""Core document, layer, selection, history, and rendering models."""

from .adjustments import apply_adjustment
from .blend import blend_layers
from .brush import (
    BrushSettings,
    erase_brush_dab,
    erase_brush_line,
    erase_brush_stroke,
    iter_brush_dabs,
    paint_brush_dab,
    paint_brush_line,
    paint_brush_stroke,
    smoothed_brush_point,
)
from .channels import apply_channel_visibility
from .color import named_background_rgba, qcolor_to_rgba
from .compositor import TiledCompositeCache, composite_layers, composite_layers_tile, render_layer_tile
from .document import (
    Document,
    ImageOpenError,
    MAX_DOCUMENT_PIXELS,
    create_document_layers,
    default_channel_visibility,
    flattened_document_layers,
    image_document_layers,
    open_raster_image,
)
from .effects import apply_effect, effect_label
from .history import DiffHistoryCommand, HistoryCommand, HistoryManager, PairedSnapshotCommand
from .layer import Layer, clone_layer_state
from .macros import (
    ALLOWED_MACRO_COMMANDS,
    MACRO_FILE_SUFFIX,
    MacroFormatError,
    load_macro_file,
    macro_steps_from_records,
    macro_steps_to_records,
    save_macro_file,
)
from .ora import ORA_FILE_SUFFIX, ORAFormatError, ORAImportResult, is_ora_path, load_ora, save_ora
from .path import selection_mask_bounds
from .project import (
    PROJECT_FILE_SUFFIX,
    ProjectFormatError,
    ProjectState,
    is_project_path,
    load_project,
    save_project,
)
from .psd import PSDExportError, PSDImportError, load_psd_layers, save_flattened_psd
from .retouch import apply_retouch_dab
from .selection import build_marching_ants_path
from .tiles import DEFAULT_TILE_SIZE, TileBox, iter_intersecting_tile_boxes, iter_tile_boxes
from .text import render_text_tile
from .vector import render_vector_shape_tile

__all__ = [
    "DEFAULT_TILE_SIZE",
    "DiffHistoryCommand",
    "Document",
    "ALLOWED_MACRO_COMMANDS",
    "HistoryManager",
    "HistoryCommand",
    "ImageOpenError",
    "MACRO_FILE_SUFFIX",
    "MAX_DOCUMENT_PIXELS",
    "MacroFormatError",
    "ORA_FILE_SUFFIX",
    "ORAFormatError",
    "ORAImportResult",
    "PairedSnapshotCommand",
    "PSDExportError",
    "PSDImportError",
    "PROJECT_FILE_SUFFIX",
    "BrushSettings",
    "ProjectFormatError",
    "ProjectState",
    "TileBox",
    "TiledCompositeCache",
    "Layer",
    "apply_adjustment",
    "apply_effect",
    "apply_channel_visibility",
    "apply_retouch_dab",
    "blend_layers",
    "build_marching_ants_path",
    "clone_layer_state",
    "composite_layers",
    "composite_layers_tile",
    "create_document_layers",
    "default_channel_visibility",
    "effect_label",
    "erase_brush_dab",
    "erase_brush_line",
    "erase_brush_stroke",
    "flattened_document_layers",
    "image_document_layers",
    "iter_brush_dabs",
    "iter_intersecting_tile_boxes",
    "iter_tile_boxes",
    "is_project_path",
    "is_ora_path",
    "load_psd_layers",
    "load_macro_file",
    "load_ora",
    "load_project",
    "macro_steps_from_records",
    "macro_steps_to_records",
    "named_background_rgba",
    "open_raster_image",
    "paint_brush_dab",
    "paint_brush_line",
    "paint_brush_stroke",
    "qcolor_to_rgba",
    "render_layer_tile",
    "render_text_tile",
    "render_vector_shape_tile",
    "save_flattened_psd",
    "save_macro_file",
    "save_ora",
    "save_project",
    "selection_mask_bounds",
    "smoothed_brush_point",
]
