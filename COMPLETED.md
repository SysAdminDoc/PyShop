# PyShop Completed Work

This file tracks completed project state and keeps the root roadmap focused on future work.

## Application Baseline

- Desktop image editor implemented in `pyshop_image_editor.py`.
- Dark themed Qt interface with toolbar, options controls, layer panel, canvas, and status UI.
- Image editing stack uses Pillow and numpy for pixel operations.
- Supports common file workflows: new, open, save, save as, and PNG export.

## Editor Features

- Tooling includes move, brush, eraser, fill, eyedropper, magic wand, rectangular selection, elliptical selection, lasso, crop, text, clone stamp, gradient, and free transform.
- Layer workflows include opacity, blend modes, visibility, locking, ordering, masks, and adjustment layers.
- Canvas workflows include zoom, pan, selection outlines, rulers, guides, and checkerboard transparency.
- Painting supports brush size, opacity, hardness, softness, and tablet pressure handling.
- History supports bounded undo/redo snapshots.

## Filters and Adjustments

- Filters include Gaussian blur, box blur, motion blur, sharpen, unsharp mask, edge detect, emboss, contour, posterize, solarize, and pixelate.
- Adjustments include brightness/contrast, hue/saturation, levels, invert, grayscale, auto contrast, and color balance.
- Selection workflows include rectangular, elliptical, lasso, magic wand, select all, deselect, invert, and feathering.

## Documentation Consolidation

- Root planning is consolidated into `ROADMAP.md`, `COMPLETED.md`, and `RESEARCH_REPORT.md`.
- The long-form historical development plan was archived at `docs/archive/roadmap/PYSHOP_ROADMAP.md`.
- The Photoshop GUI reference was archived at `docs/archive/research/Adobe Photoshop GUI architecture a complete Python recreation reference.md`.
