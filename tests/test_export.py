from PIL import Image

from pyshop.core import (
    DEFAULT_EXPORT_PRESETS,
    Layer,
    batch_export_images,
    export_image_with_preset,
    is_raw_path,
    open_raster_image,
    preset_by_name,
    save_project,
)
from pyshop.core.raw import srgb_profile_bytes


def test_open_raster_image_and_layers_preserve_icc_profile(tmp_path):
    profile = srgb_profile_bytes()
    assert profile
    path = tmp_path / "profiled.png"
    Image.new("RGB", (1, 1), (10, 20, 30)).save(path, icc_profile=profile)

    image = open_raster_image(path)
    layer = Layer("Profiled", image=image)

    assert image.info["icc_profile"] == profile
    assert layer.image.info["icc_profile"] == profile


def test_export_preset_adds_extension_and_prepares_jpeg(tmp_path):
    preset = preset_by_name("JPEG - high quality")
    output = export_image_with_preset(
        tmp_path / "photo",
        Image.new("RGBA", (2, 2), (255, 0, 0, 128)),
        preset,
    )

    assert output == tmp_path / "photo.jpg"
    with Image.open(output) as image:
        assert image.mode == "RGB"


def test_batch_export_images_handles_raster_and_project_inputs(tmp_path):
    raster_path = tmp_path / "raster.png"
    project_path = tmp_path / "document.pyshop"
    output_dir = tmp_path / "exports"
    Image.new("RGBA", (2, 2), (1, 2, 3, 255)).save(raster_path)
    save_project(project_path, [Layer("Base", image=Image.new("RGBA", (2, 2), (4, 5, 6, 255)))])

    outputs = batch_export_images([raster_path, project_path], output_dir, DEFAULT_EXPORT_PRESETS[0])

    assert outputs == [output_dir / "raster.png", output_dir / "document.png"]
    assert all(path.exists() for path in outputs)


def test_raw_path_detection_is_case_insensitive():
    assert is_raw_path("camera.CR3")
    assert is_raw_path("negative.dng")
    assert not is_raw_path("flat.png")
