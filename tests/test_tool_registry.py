from pyshop.tools import DEFAULT_TOOL_REGISTRY


def test_default_tool_registry_has_stable_unique_tool_ids():
    tool_ids = [tool.tool_id for tool in DEFAULT_TOOL_REGISTRY]

    assert len(tool_ids) == len(set(tool_ids))
    assert tool_ids[:3] == ["move", "brush", "eraser"]
    assert "magic_wand" in tool_ids


def test_tool_registry_carries_options_and_input_metadata_without_shortcuts():
    brush = DEFAULT_TOOL_REGISTRY.get("brush")
    crop = DEFAULT_TOOL_REGISTRY.get("crop")

    assert brush.options_group == "paint"
    assert brush.input_handler == "canvas"
    assert crop.options_group == "crop"
    assert not hasattr(brush, "shortcut")
