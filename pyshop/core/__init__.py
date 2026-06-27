"""Core document, layer, selection, history, and rendering models."""

from .blend import blend_layers
from .brush import erase_brush_dab, erase_brush_line, paint_brush_dab, paint_brush_line
from .color import named_background_rgba, qcolor_to_rgba
from .compositor import TiledCompositeCache, composite_layers_tile
from .document import create_document_layers, flattened_document_layers, image_document_layers
from .history import DiffHistoryCommand, HistoryCommand, HistoryManager, PairedSnapshotCommand
from .layer import Layer, clone_layer_state
from .path import selection_mask_bounds
from .selection import build_marching_ants_path
from .tiles import DEFAULT_TILE_SIZE, TileBox, iter_tile_boxes

__all__ = [
    "DEFAULT_TILE_SIZE",
    "DiffHistoryCommand",
    "HistoryManager",
    "HistoryCommand",
    "PairedSnapshotCommand",
    "TileBox",
    "TiledCompositeCache",
    "Layer",
    "blend_layers",
    "build_marching_ants_path",
    "clone_layer_state",
    "composite_layers_tile",
    "create_document_layers",
    "erase_brush_dab",
    "erase_brush_line",
    "flattened_document_layers",
    "image_document_layers",
    "iter_tile_boxes",
    "named_background_rgba",
    "paint_brush_dab",
    "paint_brush_line",
    "qcolor_to_rgba",
    "selection_mask_bounds",
]
