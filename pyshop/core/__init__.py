"""Core document, layer, selection, history, and rendering models."""

from .blend import blend_layers
from .brush import erase_brush_dab, erase_brush_line, paint_brush_dab, paint_brush_line
from .color import named_background_rgba, qcolor_to_rgba
from .document import create_document_layers, flattened_document_layers, image_document_layers
from .history import HistoryCommand, HistoryManager
from .layer import Layer, clone_layer_state
from .path import selection_mask_bounds
from .selection import build_marching_ants_path

__all__ = [
    "HistoryManager",
    "HistoryCommand",
    "Layer",
    "blend_layers",
    "build_marching_ants_path",
    "clone_layer_state",
    "create_document_layers",
    "erase_brush_dab",
    "erase_brush_line",
    "flattened_document_layers",
    "image_document_layers",
    "named_background_rgba",
    "paint_brush_dab",
    "paint_brush_line",
    "qcolor_to_rgba",
    "selection_mask_bounds",
]
