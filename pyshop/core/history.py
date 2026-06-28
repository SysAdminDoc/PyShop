from collections import deque
import copy
from dataclasses import dataclass

from PIL import ImageChops

from .layer import clone_layer_state


@dataclass
class LayerMetadata:
    name: str
    visible: bool
    opacity: int
    blend_mode: str
    locked: bool
    mask_density: int
    mask_feather: int
    clipping: bool
    adjustment: dict | None


@dataclass
class LayerPatch:
    before_metadata: LayerMetadata
    after_metadata: LayerMetadata
    bbox: tuple | None
    before_crop: object | None
    after_crop: object | None


def _metadata(layer) -> LayerMetadata:
    return LayerMetadata(
        layer.name,
        layer.visible,
        layer.opacity,
        layer.blend_mode,
        layer.locked,
        layer.mask_density,
        layer.mask_feather,
        layer.clipping,
        copy.deepcopy(layer.adjustment),
    )


def _apply_metadata(layer, metadata: LayerMetadata):
    layer.name = metadata.name
    layer.visible = metadata.visible
    layer.opacity = metadata.opacity
    layer.blend_mode = metadata.blend_mode
    layer.locked = metadata.locked
    layer.mask_density = metadata.mask_density
    layer.mask_feather = metadata.mask_feather
    layer.clipping = metadata.clipping
    layer.adjustment = copy.deepcopy(metadata.adjustment)


def _same_mask(before, after):
    if before.mask is None or after.mask is None:
        return before.mask is None and after.mask is None
    return before.mask.size == after.mask.size and ImageChops.difference(before.mask, after.mask).getbbox() is None


@dataclass
class HistoryCommand:
    layers: list
    active_index: int

    @classmethod
    def capture(cls, layers, active_index: int):
        return cls([clone_layer_state(layer) for layer in layers], active_index)

    def restore(self):
        return [clone_layer_state(layer) for layer in self.layers], self.active_index

    def compact_against(self, after_layers, after_index: int):
        return DiffHistoryCommand.capture(self.layers, self.active_index, after_layers, after_index)


@dataclass
class DiffHistoryCommand:
    before_index: int
    after_index: int
    patches: list[LayerPatch]

    @classmethod
    def capture(cls, before_layers, before_index: int, after_layers, after_index: int):
        if len(before_layers) != len(after_layers):
            return PairedSnapshotCommand.capture(before_layers, before_index, after_layers, after_index)

        patches = []
        for before, after in zip(before_layers, after_layers):
            if before.image.size != after.image.size:
                return PairedSnapshotCommand.capture(before_layers, before_index, after_layers, after_index)
            if not _same_mask(before, after):
                return PairedSnapshotCommand.capture(before_layers, before_index, after_layers, after_index)
            bbox = ImageChops.difference(before.image, after.image).getbbox()
            patches.append(
                LayerPatch(
                    before_metadata=_metadata(before),
                    after_metadata=_metadata(after),
                    bbox=bbox,
                    before_crop=before.image.crop(bbox) if bbox else None,
                    after_crop=after.image.crop(bbox) if bbox else None,
                )
            )
        return cls(before_index, after_index, patches)

    def compact_against(self, after_layers, after_index: int):
        return self

    def undo(self, current_layers):
        return self._apply(current_layers, before=True), self.before_index

    def redo(self, current_layers):
        return self._apply(current_layers, before=False), self.after_index

    def _apply(self, current_layers, before: bool):
        layers = [clone_layer_state(layer) for layer in current_layers]
        for layer, patch in zip(layers, self.patches):
            _apply_metadata(layer, patch.before_metadata if before else patch.after_metadata)
            crop = patch.before_crop if before else patch.after_crop
            if patch.bbox and crop is not None:
                layer.image.paste(crop, patch.bbox)
        return layers


@dataclass
class PairedSnapshotCommand:
    before: HistoryCommand
    after: HistoryCommand

    @classmethod
    def capture(cls, before_layers, before_index: int, after_layers, after_index: int):
        return cls(HistoryCommand.capture(before_layers, before_index), HistoryCommand.capture(after_layers, after_index))

    def compact_against(self, after_layers, after_index: int):
        return self

    def undo(self, current_layers):
        return self.before.restore()

    def redo(self, current_layers):
        return self.after.restore()


class HistoryManager:
    def __init__(self, max_states: int = 30):
        self.undo_stack = deque(maxlen=max_states)
        self.redo_stack = deque(maxlen=max_states)

    def save_state(self, layers, active_index):
        self._compact_latest(layers, active_index)
        self.undo_stack.append(HistoryCommand.capture(layers, active_index))
        self.redo_stack.clear()

    def undo(self, current_layers, current_index):
        if not self.undo_stack:
            return None, None
        command = self.undo_stack.pop().compact_against(current_layers, current_index)
        self.redo_stack.append(command)
        return command.undo(current_layers)

    def redo(self, current_layers, current_index):
        if not self.redo_stack:
            return None, None
        command = self.redo_stack.pop()
        self.undo_stack.append(command)
        return command.redo(current_layers)

    def _compact_latest(self, layers, active_index):
        if self.undo_stack:
            self.undo_stack[-1] = self.undo_stack[-1].compact_against(layers, active_index)
