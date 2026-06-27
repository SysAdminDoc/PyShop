from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    label: str
    icon_id: str
    options_group: str
    cursor: str = "default"
    input_handler: str = "canvas"


class ToolRegistry:
    def __init__(self, tools):
        self._tools = tuple(tools)
        self._by_id = {tool.tool_id: tool for tool in self._tools}

    def __iter__(self):
        return iter(self._tools)

    def get(self, tool_id: str) -> ToolSpec:
        return self._by_id[tool_id]

    def ids(self):
        return tuple(self._by_id)


DEFAULT_TOOL_REGISTRY = ToolRegistry(
    [
        ToolSpec("move", "Move", "move", "navigation", cursor="size_all"),
        ToolSpec("brush", "Brush", "brush", "paint"),
        ToolSpec("eraser", "Eraser", "eraser", "paint"),
        ToolSpec("fill", "Paint Bucket", "fill", "fill"),
        ToolSpec("eyedropper", "Eyedropper", "eyedropper", "sample"),
        ToolSpec("magic_wand", "Magic Wand", "magic_wand", "selection"),
        ToolSpec("select_rect", "Rect Select", "select_rect", "selection"),
        ToolSpec("select_ellipse", "Ellipse Select", "select_ellipse", "selection"),
        ToolSpec("lasso", "Lasso", "lasso", "selection"),
        ToolSpec("crop", "Crop", "crop", "crop"),
        ToolSpec("text", "Text", "text", "type"),
        ToolSpec("clone_stamp", "Clone Stamp", "clone_stamp", "paint"),
    ]
)
