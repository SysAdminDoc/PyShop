# PyShop v0.1.11

![Version](https://img.shields.io/badge/version-v0.1.11-7c3aed)
![License](https://img.shields.io/badge/license-MIT-blue)
![Language](https://img.shields.io/badge/language-Python-3776AB)
![Type](https://img.shields.io/badge/type-Desktop%20App-brightgreen)

An open-source alternative to Photoshop written in Python. Full-featured image editor with layers, filters, brushes, selections, and a familiar Photoshop-inspired workflow.

## Features

- **Layer System** — Create, reorder, merge, and manage multiple layers with blend modes and opacity
- **Selection Tools** — Rectangular, elliptical, lasso, and magic wand selections
- **Brush Engine** — Customizable brushes with size, opacity, and hardness controls
- **Filters & Effects** — Blur, sharpen, color adjustments, transforms, and more
- **File Support** — Open and save common image formats (PNG, JPG, BMP, TIFF)
- **Dark Theme** — Professional dark-themed interface
- **Undo/Redo** — Full history support

## Installation

```bash
python -m pip install -r requirements.txt
python pyshop_image_editor.py
```

For development and smoke tests:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Requirements

- Python 3.10-3.12
- PyQt5 5.15.x
- Pillow 10.x-12.x
- numpy 1.24.x-2.x

PyQt5 is available under GPL/commercial licensing from Riverbank. Keep that license boundary in mind before redistributing packaged builds.

## Manual QA Checklist

- Open an existing PNG or JPG and confirm the canvas renders with zoom and pan working.
- Paint with brush and eraser tools, then undo and redo the edits.
- Add, duplicate, reorder, hide, lock, and merge layers while confirming the canvas composite updates.
- Create rectangular, elliptical, lasso, and magic wand selections, then clear and invert selections.
- Apply one adjustment and one filter to the active layer.
- Save the document and export a PNG, then reopen the output image.

## Related Tools

| Tool | Type | Best For |
|------|------|----------|
| **PyShop** (this repo) | Python desktop app | Native desktop image editor with familiar app behavior |
| [Openshop](https://github.com/SysAdminDoc/Openshop) | Single-file browser app | Zero-install editing in any browser — 33 tools, PSD import, client-side AI, works offline |

If you want an image editor with no Python install required, see [Openshop](https://github.com/SysAdminDoc/Openshop) — a single HTML file that runs entirely in your browser.

## Project Planning

- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)
- [Completed work](COMPLETED.md)
- [Research report](RESEARCH_REPORT.md)
- [Archived detailed roadmap](docs/archive/roadmap/PYSHOP_ROADMAP.md)

## License

MIT License
