import numpy as np
from PyQt5.QtGui import QPainterPath


def build_marching_ants_path(mask_np):
    h, w = mask_np.shape
    if mask_np.max() == 0:
        return None
    binary = (mask_np > 127).astype(np.uint8)
    path = QPainterPath()

    padded_h = np.pad(binary, ((1, 1), (0, 0)), mode="constant", constant_values=0)
    diff_h = padded_h[1:, :] != padded_h[:-1, :]

    for y in range(h + 1):
        row = diff_h[y]
        if not np.any(row):
            continue
        padded_row = np.concatenate(([0], row.astype(np.uint8), [0]))
        row_diff = np.diff(padded_row)
        starts = np.where(row_diff == 1)[0]
        ends = np.where(row_diff == -1)[0]
        for start, end in zip(starts, ends):
            path.moveTo(start, y)
            path.lineTo(end, y)

    padded_v = np.pad(binary, ((0, 0), (1, 1)), mode="constant", constant_values=0)
    diff_v = padded_v[:, 1:] != padded_v[:, :-1]

    for x in range(w + 1):
        col = diff_v[:, x]
        if not np.any(col):
            continue
        padded_col = np.concatenate(([0], col.astype(np.uint8), [0]))
        col_diff = np.diff(padded_col)
        starts = np.where(col_diff == 1)[0]
        ends = np.where(col_diff == -1)[0]
        for start, end in zip(starts, ends):
            path.moveTo(x, start)
            path.lineTo(x, end)

    return path
