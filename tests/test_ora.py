import pytest
from PIL import Image

from pyshop.core import Layer, ORAFormatError, is_ora_path, load_ora, save_ora


def test_ora_round_trip_preserves_supported_layer_state(tmp_path):
    path = tmp_path / "document.ora"
    base = Layer("Base", image=Image.new("RGBA", (3, 2), (10, 20, 30, 255)))
    top = Layer("Top", image=Image.new("RGBA", (3, 2), (200, 10, 10, 128)))
    top.visible = False
    top.opacity = 128
    top.blend_mode = "Multiply"
    top.mask = Image.new("L", (3, 2), 64)
    top.mask_density = 50
    top.mask_feather = 1

    report = save_ora(path, [base, top])
    restored = load_ora(path)

    assert is_ora_path(path)
    assert any("mask stored as PyShop extension" in item for item in report)
    assert [layer.name for layer in restored.layers] == ["Base", "Top"]
    assert restored.layers[0].image.getpixel((0, 0)) == (10, 20, 30, 255)
    assert restored.layers[1].visible is False
    assert restored.layers[1].opacity == 128
    assert restored.layers[1].blend_mode == "Multiply"
    assert restored.layers[1].mask.getpixel((0, 0)) == 64
    assert restored.layers[1].mask_density == 50
    assert restored.layers[1].mask_feather == 1
    assert any("restored PyShop mask extension" in item for item in restored.compatibility_report)


def test_ora_export_reports_nonportable_pyshop_metadata(tmp_path):
    layer = Layer("Effect Text", image=Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
    layer.effect = {"type": "gaussian_blur", "radius": 2}
    layer.text_item = {"text": "Hi", "x": 0, "y": 0, "size": 12}
    layer.blend_mode = "Hard Mix"

    report = save_ora(tmp_path / "metadata.ora", [layer])

    assert any("effect metadata is not portable" in item for item in report)
    assert any("text metadata exported" in item for item in report)
    assert any("blend mode stored as PyShop extension" in item for item in report)


def test_ora_rejects_oversized_documents(tmp_path):
    layer = Layer("Large", image=Image.new("RGBA", (2, 2), (0, 0, 0, 0)))

    with pytest.raises(ORAFormatError, match="too large"):
        save_ora(tmp_path / "large.ora", [layer], max_pixels=3)
