import numpy as np
from PIL import Image

from pyshop.core import HistoryManager, Layer, blend_layers, build_marching_ants_path


def test_layer_copy_preserves_pixels_and_marks_duplicate_name():
    layer = Layer("Base", image=Image.new("RGBA", (2, 2), (10, 20, 30, 255)))
    layer.visible = False
    layer.opacity = 128
    layer.blend_mode = "Multiply"
    layer.locked = True

    duplicate = layer.copy()
    layer.image.putpixel((0, 0), (255, 0, 0, 255))

    assert duplicate.name == "Base copy"
    assert duplicate.visible is False
    assert duplicate.opacity == 128
    assert duplicate.blend_mode == "Multiply"
    assert duplicate.locked is True
    assert duplicate.image.getpixel((0, 0)) == (10, 20, 30, 255)


def test_history_snapshots_preserve_layer_name_without_duplicate_suffix():
    layer = Layer("Background", image=Image.new("RGBA", (1, 1), (1, 2, 3, 255)))
    history = HistoryManager(max_states=2)
    history.save_state([layer], 0)
    layer.name = "Changed"

    restored_layers, restored_index = history.undo([layer], 0)

    assert restored_index == 0
    assert restored_layers[0].name == "Background"
    assert restored_layers[0].image.getpixel((0, 0)) == (1, 2, 3, 255)


def test_blend_layers_normal_does_not_mutate_base_image():
    base = Image.new("RGBA", (1, 1), (0, 0, 0, 255))
    top = Image.new("RGBA", (1, 1), (255, 0, 0, 128))

    result = blend_layers(base, top, "Normal")

    assert base.getpixel((0, 0)) == (0, 0, 0, 255)
    assert result.getpixel((0, 0)) != base.getpixel((0, 0))


def test_selection_path_is_none_for_empty_mask_and_present_for_selection():
    empty = np.zeros((3, 3), dtype=np.uint8)
    selected = empty.copy()
    selected[1, 1] = 255

    assert build_marching_ants_path(empty) is None
    assert not build_marching_ants_path(selected).isEmpty()
