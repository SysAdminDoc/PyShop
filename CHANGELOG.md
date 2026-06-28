# Changelog

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
