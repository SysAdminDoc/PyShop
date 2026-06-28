import copy

from PIL import Image


class Layer:
    BLEND_MODES = [
        "Normal",
        "Multiply",
        "Screen",
        "Overlay",
        "Soft Light",
        "Hard Light",
        "Vivid Light",
        "Linear Light",
        "Pin Light",
        "Hard Mix",
        "Darken",
        "Lighten",
        "Darker Color",
        "Lighter Color",
        "Difference",
        "Exclusion",
        "Subtract",
        "Divide",
        "Color Dodge",
        "Color Burn",
        "Linear Dodge (Add)",
        "Linear Burn",
        "Hue",
        "Saturation",
        "Color",
        "Luminosity",
    ]

    def __init__(self, name: str = "Layer", width: int = 800, height: int = 600, image=None):
        self.name = name
        self.visible = True
        self.opacity = 255
        self.blend_mode = "Normal"
        self.locked = False
        self.mask = None
        self.mask_density = 100
        self.mask_feather = 0
        self.clipping = False
        self.adjustment = None
        self.is_group = False
        self.group_id = None
        self.group_expanded = True
        self.vector_shape = None
        self.image = image.convert("RGBA") if image is not None else Image.new("RGBA", (width, height), (0, 0, 0, 0))

    def copy(self):
        layer = clone_layer_state(self)
        layer.name = self.name + " copy"
        return layer


def clone_layer_state(layer: Layer) -> Layer:
    snapshot = Layer(layer.name)
    snapshot.image = layer.image.copy()
    snapshot.visible = layer.visible
    snapshot.opacity = layer.opacity
    snapshot.blend_mode = layer.blend_mode
    snapshot.locked = layer.locked
    snapshot.mask = layer.mask.copy() if layer.mask is not None else None
    snapshot.mask_density = layer.mask_density
    snapshot.mask_feather = layer.mask_feather
    snapshot.clipping = layer.clipping
    snapshot.adjustment = copy.deepcopy(layer.adjustment)
    snapshot.is_group = layer.is_group
    snapshot.group_id = layer.group_id
    snapshot.group_expanded = layer.group_expanded
    snapshot.vector_shape = copy.deepcopy(layer.vector_shape)
    return snapshot
