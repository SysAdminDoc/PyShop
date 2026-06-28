def snap_coordinate(value: float, targets, threshold: float) -> float:
    best = value
    best_distance = threshold
    for target in targets:
        distance = abs(value - target)
        if distance <= best_distance:
            best = target
            best_distance = distance
    return best


def snap_point_to_guides(x: float, y: float, grid_size: int, guides, threshold: float):
    x_targets = []
    y_targets = []
    if grid_size > 0:
        x_targets.append(round(x / grid_size) * grid_size)
        y_targets.append(round(y / grid_size) * grid_size)
    for orientation, value in guides:
        if orientation == "vertical":
            x_targets.append(value)
        elif orientation == "horizontal":
            y_targets.append(value)
    return snap_coordinate(x, x_targets, threshold), snap_coordinate(y, y_targets, threshold)
