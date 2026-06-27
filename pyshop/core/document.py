from .layer import Layer


def create_document_layers(width: int, height: int, background_rgba):
    background = Layer("Background", width, height)
    background.image.paste(background_rgba, (0, 0, width, height))
    return [background]


def image_document_layers(image):
    return [Layer("Background", image=image)]


def flattened_document_layers(composite_image):
    return [Layer("Background", image=composite_image)]
