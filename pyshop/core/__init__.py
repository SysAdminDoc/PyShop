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
from .diagnostics import app_data_dir, clear_recovery_project, recovery_project_path, write_error_log
from .effects import apply_effect, effect_label
from .export import (
    DEFAULT_EXPORT_PRESETS,
    ExportPreset,
    batch_export_images,
    export_image_with_preset,
    export_path_for_preset,
    load_exportable_image,
    preset_by_name,
)
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
from .psd import PSDExportError, PSDImportError, load_psd_layers, save_flattened_psd, save_layered_psd
from .raw import RAW_EXTENSIONS, RAWImportError, is_raw_path, load_raw_image
from .retouch import apply_retouch_dab
from .safeio import save_image_atomic
from .selection import build_marching_ants_path
from .tiles import DEFAULT_TILE_SIZE, TileBox, iter_intersecting_tile_boxes, iter_tile_boxes
from .text import render_text_tile
from .vector import render_vector_shape_tile

__all__ = [
    "DEFAULT_TILE_SIZE",
    "DEFAULT_EXPORT_PRESETS",
    "DiffHistoryCommand",
    "Document",
    "ALLOWED_MACRO_COMMANDS",
    "ExportPreset",
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
    "RAW_EXTENSIONS",
    "RAWImportError",
    "BrushSettings",
    "ProjectFormatError",
    "ProjectState",
    "TileBox",
    "TiledCompositeCache",
    "Layer",
    "app_data_dir",
    "apply_adjustment",
    "apply_effect",
    "apply_channel_visibility",
    "apply_retouch_dab",
    "batch_export_images",
    "blend_layers",
    "build_marching_ants_path",
    "clone_layer_state",
    "composite_layers",
    "composite_layers_tile",
    "create_document_layers",
    "clear_recovery_project",
    "default_channel_visibility",
    "effect_label",
    "erase_brush_dab",
    "erase_brush_line",
    "erase_brush_stroke",
    "export_image_with_preset",
    "export_path_for_preset",
    "flattened_document_layers",
    "image_document_layers",
    "iter_brush_dabs",
    "iter_intersecting_tile_boxes",
    "iter_tile_boxes",
    "is_project_path",
    "is_ora_path",
    "is_raw_path",
    "load_exportable_image",
    "load_psd_layers",
    "load_macro_file",
    "load_ora",
    "load_project",
    "load_raw_image",
    "macro_steps_from_records",
    "macro_steps_to_records",
    "named_background_rgba",
    "open_raster_image",
    "paint_brush_dab",
    "paint_brush_line",
    "paint_brush_stroke",
    "qcolor_to_rgba",
    "preset_by_name",
    "render_layer_tile",
    "recovery_project_path",
    "render_text_tile",
    "render_vector_shape_tile",
    "save_flattened_psd",
    "save_image_atomic",
    "save_layered_psd",
    "save_macro_file",
    "save_ora",
    "save_project",
    "selection_mask_bounds",
    "smoothed_brush_point",
    "write_error_log",
]
