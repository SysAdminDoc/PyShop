import numpy as np


def selection_mask_bounds(mask_image):
    selected = np.array(mask_image)
    ys, xs = np.where(selected > 127)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
