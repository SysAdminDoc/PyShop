def qcolor_to_rgba(color, opacity: int = 255):
    return (color.red(), color.green(), color.blue(), opacity)


def named_background_rgba(name: str):
    backgrounds = {
        "White": (255, 255, 255, 255),
        "Black": (0, 0, 0, 255),
        "Transparent": (0, 0, 0, 0),
    }
    return backgrounds[name]
