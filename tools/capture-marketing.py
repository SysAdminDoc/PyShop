#!/usr/bin/env python3
"""Source entry point for the private-desktop capture wrapper."""
import os
from pathlib import Path
import sys

if not os.environ.get("PYSHOP_CAPTURE_DIR"):
    raise RuntimeError("Use tools/capture-marketing.ps1 to create an isolated capture session")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pyshop_image_editor import main

if __name__ == "__main__":
    main()
