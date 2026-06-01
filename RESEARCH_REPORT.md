# PyShop Research Report

This report summarizes the research that informs the current roadmap. Full historical notes are archived under `docs/archive/`.

## Product Direction

PyShop should prioritize native desktop strengths instead of trying to mirror browser-based editors:

- Better stylus/tablet input.
- Larger local documents and RAM-heavy operations.
- Native shell, scanner, webcam, printer, and file-handler integration.
- Local-only processing for privacy-sensitive image workflows.

## Competitive Lessons

- GIMP proves that deep open-source image editing is viable, but PyShop should avoid inheriting a dated UX and should keep Qt-native desktop polish central.
- Krita is strongest for digital painting; PyShop should borrow brush-engine concepts while staying focused on general-purpose photo and layer editing.
- Affinity Photo sets expectations for non-destructive editing, adjustment layers, masks, and fast professional workflows.
- Photopea and OpenShop show that browser editors can cover a large amount of functionality, so PyShop's wedge must be native app behavior and heavier local processing.

## Open-Source References

- GIMP and GEGL: graph-based compositing, filters as nodes, and tile invalidation.
- Krita: tile-based rendering, brush dynamics, symmetry guides, and large-canvas performance.
- miniPaint: browser layer-engine behavior and approachable Photoshop-style UX.
- BitMappery: non-destructive editor ideas and PSD I/O patterns.
- Aseprite: layer/frame modeling for future animation workflows.
- SimplePaint: focused canvas and tablet interaction examples.

## Architecture Findings

- The current monolith should be split before major feature expansion.
- A document model should own dimensions, resolution, metadata, color mode, layer tree, and active selection.
- Tool behavior should move behind a registry of `BaseTool` implementations.
- Undo should shift from whole-layer snapshots to command/action objects with targeted diffs.
- Layer rendering should use cached compositing and eventually tile-based invalidation.
- Panels should listen to document signals rather than reaching directly into canvas internals.

## Feature Priorities

- Stabilization and packaging come first because the application is currently a single-file desktop app.
- Non-destructive layer workflows are the first major product differentiator.
- Brush, selection, retouching, type, shape, and path parity should be delivered incrementally after the package boundary exists.
- Local AI should remain optional and local-only, with model downloads and runtime costs kept explicit.

## Archived Source Material

- `docs/archive/roadmap/PYSHOP_ROADMAP.md`
- `docs/archive/research/Adobe Photoshop GUI architecture a complete Python recreation reference.md`
