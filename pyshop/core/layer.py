from PIL import Image


class Layer:
    BLEND_MODES = [
        "Normal",
        "Multiply",
        "Screen",
        "Overlay",
        "Darken",
        "Lighten",
        "Difference",
        "Color Dodge",
        "Color Burn",
    ]

    def __init__(self, name: str = "Layer", width: int = 800, height: int = 600, image=None):
        self.name = name
        self.visible = True
        self.opacity = 255
        self.blend_mode = "Normal"
        self.locked = False
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
    return snapshot
