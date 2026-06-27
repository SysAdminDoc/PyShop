import numpy as np
from PIL import Image

from pyshop.core import (
    DiffHistoryCommand,
    HistoryManager,
    HistoryCommand,
    Layer,
    blend_layers,
    build_marching_ants_path,
    create_document_layers,
    erase_brush_dab,
    iter_tile_boxes,
    named_background_rgba,
    paint_brush_dab,
    paint_brush_line,
    selection_mask_bounds,
)


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


def test_history_uses_bounded_command_objects():
    first = Layer("First", image=Image.new("RGBA", (1, 1), (1, 1, 1, 255)))
    second = Layer("Second", image=Image.new("RGBA", (1, 1), (2, 2, 2, 255)))
    history = HistoryManager(max_states=1)

    history.save_state([first], 0)
    history.save_state([second], 0)

    assert len(history.undo_stack) == 1
    assert isinstance(history.undo_stack[0], HistoryCommand)
    restored_layers, _ = history.undo([second], 0)
    assert restored_layers[0].name == "Second"


def test_history_compacts_previous_image_state_to_diff_command():
    before = Layer("Paint", image=Image.new("RGBA", (3, 3), (0, 0, 0, 0)))
    after = Layer("Paint", image=before.image.copy())
    after.image.putpixel((1, 1), (255, 0, 0, 255))
    history = HistoryManager(max_states=3)

    history.save_state([before], 0)
    history.save_state([after], 0)

    compacted = history.undo_stack[0]
    assert isinstance(compacted, DiffHistoryCommand)
    assert compacted.patches[0].bbox == (1, 1, 2, 2)

    restored_layers, _ = compacted.undo([after])
    assert restored_layers[0].image.getpixel((1, 1)) == (0, 0, 0, 0)


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


def test_document_factory_creates_background_layer():
    layers = create_document_layers(2, 1, named_background_rgba("Black"))

    assert len(layers) == 1
    assert layers[0].name == "Background"
    assert layers[0].image.getpixel((0, 0)) == (0, 0, 0, 255)


def test_brush_helpers_paint_and_erase_pixels():
    image = Image.new("RGBA", (5, 5), (0, 0, 0, 0))

    paint_brush_line(image, 0, 0, 4, 4, 3, (255, 0, 0, 255))
    paint_brush_dab(image, 2, 2, 1, (255, 0, 0, 255))
    assert image.getpixel((2, 2))[3] == 255

    erase_brush_dab(image, 2, 2, 1)
    assert image.getpixel((2, 2))[3] == 0


def test_selection_mask_bounds_returns_cropped_extent():
    mask = Image.new("L", (5, 5), 0)
    mask.putpixel((1, 2), 255)
    mask.putpixel((3, 4), 255)

    assert selection_mask_bounds(mask) == (1, 2, 4, 5)
    assert selection_mask_bounds(Image.new("L", (2, 2), 0)) is None


def test_iter_tile_boxes_covers_partial_edges():
    boxes = list(iter_tile_boxes(5, 3, tile_size=2))

    assert boxes[0].as_crop_box() == (0, 0, 2, 2)
    assert boxes[-1].as_crop_box() == (4, 2, 5, 3)
    assert sum(box.width * box.height for box in boxes) == 15
