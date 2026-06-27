from collections import deque

from .layer import clone_layer_state


class HistoryManager:
    def __init__(self, max_states: int = 30):
        self.undo_stack = deque(maxlen=max_states)
        self.redo_stack = deque(maxlen=max_states)

    def save_state(self, layers, active_index):
        self.undo_stack.append((self._snapshot_layers(layers), active_index))
        self.redo_stack.clear()

    def undo(self, current_layers, current_index):
        if not self.undo_stack:
            return None, None
        self.redo_stack.append(self._snap(current_layers, current_index))
        return self.undo_stack.pop()

    def redo(self, current_layers, current_index):
        if not self.redo_stack:
            return None, None
        self.undo_stack.append(self._snap(current_layers, current_index))
        return self.redo_stack.pop()

    def _snap(self, layers, active_index):
        return self._snapshot_layers(layers), active_index

    def _snapshot_layers(self, layers):
        return [clone_layer_state(layer) for layer in layers]
