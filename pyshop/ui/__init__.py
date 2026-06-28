"""Application shell, canvas, widgets, and shared UI helpers."""

from .canvas_view import CanvasViewport
from .guides import snap_coordinate, snap_point_to_guides

__all__ = ["CanvasViewport", "snap_coordinate", "snap_point_to_guides"]
