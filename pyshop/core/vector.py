from PIL import Image, ImageDraw


def render_vector_shape_tile(shape: dict, crop_box, size) -> Image.Image:
    tile = Image.new("RGBA", size, (0, 0, 0, 0))
    if not shape:
        return tile

    left, top, right, bottom = shape.get("box", (0, 0, 0, 0))
    crop_left, crop_top, _crop_right, _crop_bottom = crop_box
    local_box = (left - crop_left, top - crop_top, right - crop_left, bottom - crop_top)
    fill = tuple(shape.get("fill", (255, 255, 255, 255)))
    outline = tuple(shape.get("stroke", fill))
    stroke_width = max(0, int(shape.get("stroke_width", 0)))
    draw = ImageDraw.Draw(tile)
    if shape.get("type") == "ellipse":
        draw.ellipse(local_box, fill=fill, outline=outline if stroke_width else None, width=stroke_width or 1)
    else:
        draw.rectangle(local_box, fill=fill, outline=outline if stroke_width else None, width=stroke_width or 1)
    return tile
