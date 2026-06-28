from dataclasses import dataclass


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    label: str
    icon_id: str
    options_group: str
    toolbar_group: str
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
        ToolSpec("move", "Move", "move", "navigation", "move", cursor="size_all"),
        ToolSpec("select_rect", "Rect Select", "select_rect", "selection", "marquee"),
        ToolSpec("select_ellipse", "Ellipse Select", "select_ellipse", "selection", "marquee"),
        ToolSpec("lasso", "Lasso", "lasso", "selection", "lasso"),
        ToolSpec("object_select", "Object Selection", "object_select", "selection", "lasso"),
        ToolSpec("crop", "Crop", "crop", "crop", "crop"),
        ToolSpec("eyedropper", "Eyedropper", "eyedropper", "sample", "sample"),
        ToolSpec("healing", "Healing Brush", "healing", "retouch", "retouch"),
        ToolSpec("brush", "Brush", "brush", "paint", "paint"),
        ToolSpec("clone_stamp", "Clone Stamp", "clone_stamp", "paint", "paint"),
        ToolSpec("eraser", "Eraser", "eraser", "paint", "paint"),
        ToolSpec("fill", "Paint Bucket", "fill", "fill", "paint"),
        ToolSpec("gradient", "Gradient", "gradient", "fill", "paint"),
        ToolSpec("blur", "Blur", "blur", "retouch", "blur"),
        ToolSpec("sharpen_tool", "Sharpen", "sharpen", "retouch", "blur"),
        ToolSpec("smudge", "Smudge", "smudge", "retouch", "blur"),
        ToolSpec("dodge", "Dodge", "dodge", "tone", "tone"),
        ToolSpec("burn", "Burn", "burn", "tone", "tone"),
        ToolSpec("sponge", "Sponge", "sponge", "tone", "tone"),
        ToolSpec("pen", "Pen", "pen", "path", "path"),
        ToolSpec("text", "Text", "text", "type", "type"),
        ToolSpec("shape", "Shape", "shape", "shape", "shape"),
        ToolSpec("hand", "Hand", "hand", "navigation", "navigation", cursor="open_hand"),
        ToolSpec("zoom", "Zoom", "zoom", "navigation", "navigation"),
        ToolSpec("magic_wand", "Magic Wand", "magic_wand", "selection", "selection"),
    ]
)
