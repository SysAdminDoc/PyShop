# Changelog

## PyShop v0.1.34 - 2026-06-28

- Added OpenRaster `.ora` import/export with layer names, pixels, visibility, opacity, supported blend modes, PyShop mask extensions, and compatibility reporting.

## PyShop v0.1.33 - 2026-06-28

- Moved image open/save/export and effect rasterize work onto status-bar background jobs with progress reporting and cancel requests.

## PyShop v0.1.32 - 2026-06-28

- Added editable non-destructive effect layers for blur, sharpen, stylize, posterize, solarize, and pixelate filters, including serialization and explicit rasterize-down support.

## PyShop v0.1.31 - 2026-06-28

- Added QSettings-backed workspace preset persistence plus validated macro save/load/replay support using `.pyshopmacro` files and native project macro storage.

## PyShop v0.1.30 - 2026-06-28

- Moved canvas mouse behavior behind registered tool-handler objects with focused handler tests for paint, selection, crop, path, text, shape, and retouch workflows.

## PyShop v0.1.29 - 2026-06-28

- Extracted document state into a core `Document` model with layer, active index, selection, path, channel, guide, macro, file provenance, and dirty-revision ownership.

## PyShop v0.1.28 - 2026-06-28

- Added native `.pyshop` layered project save/open support with metadata round-tripping for layers, masks, groups, text/vector layers, adjustments, paths, guides, channels, active layer, and macro steps.

## PyShop v0.1.27 - 2026-06-28

- Hardened raster and PSD file I/O with safe pixel-count checks, psd-tools-backed flattened PSD export, and Save/Save As guardrails that prevent accidental layered PSD data loss.

## PyShop v0.1.26 - 2026-06-28

- Added action macro recording/replay and session workspace presets while preserving the no-keyboard-shortcut action contract.

## PyShop v0.1.25 - 2026-06-28

- Added a Pen path workflow with point capture, canvas preview, Paths dock actions, and path-to-selection conversion.

## PyShop v0.1.24 - 2026-06-28

- Added channel visibility compositing and a Channels dock for red, green, blue, and alpha channel workflow toggles.

## PyShop v0.1.23 - 2026-06-28

- Converted text insertion into non-destructive text layers rendered by the compositor, with text-layer cloning and render tests.

## PyShop v0.1.22 - 2026-06-28

- Added non-destructive vector rectangle shape layers, compositor rendering, shape-tool drag creation, and vector-layer tests.

## PyShop v0.1.21 - 2026-06-28

- Added core retouch dab operations and canvas workflows for healing, blur, sharpen, dodge, burn, and sponge toolbar tools.

## PyShop v0.1.20 - 2026-06-28

- Added the complete top-level menu structure for File, Edit, Image, Layer, Type, Select, Filter, View, Window, and Help workflows.

## PyShop v0.1.19 - 2026-06-28

- Added grouped toolbar slot metadata and UI separators for marquee, lasso, crop, sample, retouch, paint, blur, tone, path, type, shape, hand, and zoom tool groups.

## PyShop v0.1.18 - 2026-06-28

- Added ruler overlays plus Navigator, Histogram, and Info dock panels with composite previews, RGB histograms, and cursor/document readouts.

## PyShop v0.1.17 - 2026-06-28

- Added grid and guide overlays, snap-to-grid/guide math, View menu controls, and tests for snapping behavior.

## PyShop v0.1.16 - 2026-06-28

- Added layer group metadata, group-aware compositing, layer-panel grouping controls, and tests for grouped child rendering.

## PyShop v0.1.15 - 2026-06-28

- Added non-destructive adjustment layer metadata, compositor rendering, layer-panel creation, and core tests for adjustment compositing.

## PyShop v0.1.14 - 2026-06-28

- Added layer mask and clipping-mask metadata, compositor support, layer-panel controls, mask-aware transforms, and an alpha-compositing regression fix.

## PyShop v0.1.13 - 2026-06-28

- Added dynamic brush settings for pressure, smoothing, spacing, scatter, texture, and color jitter, with toolbar controls and core stroke tests.

## PyShop v0.1.12 - 2026-06-28

- Capped canvas paint work to the visible image extent with viewport bounds and intersecting tile iteration.

## PyShop v0.1.11 - 2026-06-28

- Extracted canvas viewport zoom, pan, coordinate conversion, fit, and anchored zoom math into `pyshop.ui.CanvasViewport`.

## PyShop v0.1.10 - 2026-06-28

- Expanded layer compositing with Photoshop-style blend modes including soft/hard light, linear/pin/vivid light, color compare, arithmetic, and HSL modes.

## PyShop v0.1.9 - 2026-06-27

- Added tile-level layer compositing and a canvas tile cache for bounded paint operations.

## PyShop v0.1.8 - 2026-06-27

- Added core tile geometry helpers and routed canvas composite painting through bounded image tiles.

## PyShop v0.1.7 - 2026-06-27

- Added editor-level Qt signals for layer and active-layer changes, then routed layer panel refresh through those signals.

## PyShop v0.1.6 - 2026-06-27

- Added diff-backed history commands for same-structure layer edits, with snapshot fallback for structural changes.

## PyShop v0.1.5 - 2026-06-27

- Replaced raw history tuple stacks with explicit bounded `HistoryCommand` objects while preserving undo/redo behavior.

## PyShop v0.1.4 - 2026-06-27

- Added a `pyshop.tools` registry for toolbar metadata, options grouping, cursor metadata, and input-handler routing.
- Removed installed keyboard shortcuts from menu, toolbar, and swap-color actions while preserving clickable controls.

## PyShop v0.1.3 - 2026-06-27

- Extracted document construction, color conversion, brush/eraser painting, and selection bounds helpers into `pyshop.core`.
- Completed the first architecture extraction pass while preserving the current single-window UI entrypoint.
- Fixed eraser strokes so transparent brush dabs clear existing alpha instead of leaving painted pixels intact.

## PyShop v0.1.2 - 2026-06-27

- Extracted layer state, bounded history, selection contour generation, and blend-mode compositing into `pyshop.core`.
- Added focused core tests for layer copies, history snapshots, blend immutability, and selection path generation.

## PyShop v0.1.1 - 2026-06-27

- Added the initial `pyshop/` package skeleton with core, tools, panels, filters, ui, and resources namespaces.
- Moved app identity and icon discovery into `pyshop.app_info` while preserving the existing desktop entrypoint.

## PyShop v0.1.0 - 2026-06-27

- Fixed the top-level Qt import syntax error that prevented the app from compiling.
- Added explicit runtime and development dependency manifests.
- Added a pytest import smoke test that verifies the module imports without launching a GUI.
- Documented supported Python/PyQt versions and the manual desktop QA checklist.
