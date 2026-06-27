from collections import deque
from dataclasses import dataclass

from .layer import clone_layer_state


@dataclass
class HistoryCommand:
    layers: list
    active_index: int

    @classmethod
    def capture(cls, layers, active_index: int):
        return cls([clone_layer_state(layer) for layer in layers], active_index)

    def restore(self):
        return [clone_layer_state(layer) for layer in self.layers], self.active_index


class HistoryManager:
    def __init__(self, max_states: int = 30):
        self.undo_stack = deque(maxlen=max_states)
        self.redo_stack = deque(maxlen=max_states)

    def save_state(self, layers, active_index):
        self.undo_stack.append(HistoryCommand.capture(layers, active_index))
        self.redo_stack.clear()

    def undo(self, current_layers, current_index):
        if not self.undo_stack:
            return None, None
        self.redo_stack.append(HistoryCommand.capture(current_layers, current_index))
        return self.undo_stack.pop().restore()

    def redo(self, current_layers, current_index):
        if not self.redo_stack:
            return None, None
        self.undo_stack.append(HistoryCommand.capture(current_layers, current_index))
        return self.redo_stack.pop().restore()
