import numpy as np
from PIL import Image

from pyshop.core import (
    BrushSettings,
    DiffHistoryCommand,
    HistoryManager,
    HistoryCommand,
    Layer,
    blend_layers,
    build_marching_ants_path,
    composite_layers_tile,
    create_document_layers,
    erase_brush_dab,
    erase_brush_stroke,
    iter_brush_dabs,
    iter_intersecting_tile_boxes,
    iter_tile_boxes,
    named_background_rgba,
    paint_brush_dab,
    paint_brush_line,
    paint_brush_stroke,
    selection_mask_bounds,
    smoothed_brush_point,
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


def test_advertised_blend_modes_render_without_mutating_inputs():
    base = Image.new("RGBA", (2, 2), (50, 100, 150, 255))
    top = Image.new("RGBA", (2, 2), (200, 80, 40, 192))
    base_before = base.copy()
    top_before = top.copy()

    for mode in Layer.BLEND_MODES:
        result = blend_layers(base, top, mode)
        assert result.size == base.size
        assert result.mode == "RGBA"

    assert base.tobytes() == base_before.tobytes()
    assert top.tobytes() == top_before.tobytes()


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


def test_brush_settings_apply_pressure_and_spacing():
    settings = BrushSettings(size=20, opacity=200, spacing=50, pressure_size=True, pressure_opacity=True)

    assert settings.effective_size(0.5) == 10
    assert settings.effective_opacity(0.5) == 100
    assert settings.spacing_pixels(0.5) == 5


def test_iter_brush_dabs_respects_spacing():
    settings = BrushSettings(size=10, spacing=50)

    dabs = list(iter_brush_dabs(0, 0, 10, 0, settings))

    assert [(x, y, size) for x, y, size, _index in dabs] == [(0, 0, 10), (5, 0, 10), (10, 0, 10)]


def test_iter_brush_dabs_emits_one_dab_for_clicks():
    assert list(iter_brush_dabs(2, 3, 2, 3, BrushSettings(size=4))) == [(2, 3, 4, 0)]


def test_smoothed_brush_point_filters_toward_previous_point():
    assert smoothed_brush_point((0, 0), (10, 0), 50) == (5, 0)


def test_dynamic_brush_stroke_uses_pressure_opacity_and_eraser_stroke():
    image = Image.new("RGBA", (3, 1), (0, 0, 0, 0))
    settings = BrushSettings(size=1, opacity=200, spacing=100, pressure_opacity=True)

    paint_brush_stroke(image, 1, 0, 1, 0, settings, (255, 0, 0, 255), pressure=0.5)

    assert image.getpixel((1, 0)) == (255, 0, 0, 100)

    erase_brush_stroke(image, 1, 0, 1, 0, settings)

    assert image.getpixel((1, 0))[3] == 0


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


def test_iter_intersecting_tile_boxes_culls_to_visible_extent():
    boxes = list(iter_intersecting_tile_boxes(10, 10, (4.2, 4.2, 6.8, 6.8), tile_size=3))

    assert [box.as_crop_box() for box in boxes] == [
        (3, 3, 6, 6),
        (6, 3, 9, 6),
        (3, 6, 6, 9),
        (6, 6, 9, 9),
    ]


def test_composite_layers_tile_blends_only_requested_tile():
    bottom = Layer("Bottom", image=Image.new("RGBA", (4, 4), (0, 0, 255, 255)))
    top = Layer("Top", image=Image.new("RGBA", (4, 4), (255, 0, 0, 128)))
    tile_box = next(iter_tile_boxes(4, 4, tile_size=2))

    tile = composite_layers_tile([bottom, top], tile_box)

    assert tile.size == (2, 2)
    assert tile.getpixel((0, 0))[0] > 0
