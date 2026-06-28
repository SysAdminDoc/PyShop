import os
import tempfile
from pathlib import Path


def save_image_atomic(path, image, format_name=None):
    path = Path(path)
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=path.suffix or ".tmp", dir=str(path.parent or "."))
    os.close(fd)
    try:
        if format_name:
            image.save(temp_name, format=format_name)
        else:
            image.save(temp_name)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
    return path
