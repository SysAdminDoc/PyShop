# PyShop Roadmap

PyShop is a native desktop Python image editor with a Photoshop-inspired workflow. This roadmap is the active planning surface; older deep-dive plans and research snapshots live under `docs/archive/`.

## Planning Docs

- Current completed state: `COMPLETED.md`
- Research synthesis: `RESEARCH_REPORT.md`
- Historical implementation plan: `docs/archive/roadmap/PYSHOP_ROADMAP.md`
- Historical Photoshop GUI reference: `docs/archive/research/Adobe Photoshop GUI architecture a complete Python recreation reference.md`

## Current Baseline

- Single-file desktop application in `pyshop_image_editor.py`.
- PyQt/Pillow/numpy implementation with a dark desktop UI.
- Core editor surface includes tools, layer management, selections, filters, adjustments, export, and undo/redo.
- The next phase is architectural: split the monolith into packages before adding more Photoshop-parity features.

## Active Roadmap

### 1. Stabilize the Current App

- Fix import/runtime errors and document the supported Python and Qt binding versions.
- Add a smoke test that imports the app module without launching the GUI.
- Add a manual QA checklist for open, edit, layer, filter, save, and export workflows.
- Replace first-run dependency installation with documented install commands or a proper package manifest.

### 2. Project Skeleton and Architecture

- Create a `pyshop/` package with `core/`, `tools/`, `panels/`, `filters/`, `ui/`, and `resources/` modules.
- Move document, layer, selection, history, color, blend, brush, and path concerns out of the main window file.
- Introduce a tool registry with self-contained tool classes, options-bar builders, cursors, shortcuts, and input handlers.
- Replace full-layer snapshot history with command objects and bounded diff storage.
- Use Qt signals to decouple panels from document state.

### 3. Canvas, Layers, and Painting

- Replace the direct widget canvas with a tiled canvas/view architecture that can handle large images.
- Add cached compositing per tile and all Photoshop-style blend modes needed by the layer stack.
- Expand brush dynamics with pressure, smoothing, spacing, scatter, texture, and color dynamics.
- Add layer groups, clipping masks, layer masks with density/feather, and non-destructive adjustment layers.
- Add rulers, guides, grid settings, snapping, and navigator/histogram/info panels.

### 4. Tool and Menu Parity

- Add grouped toolbar slots for marquee, lasso, object selection, crop, eyedropper, healing, brush, stamp, eraser, gradient, blur/sharpen/smudge, dodge/burn/sponge, pen, type, shapes, hand, and zoom.
- Add a complete menu structure for file, edit, image, layer, type, select, filter, view, window, and help operations.
- Implement path, vector shape, type, retouching, channel, and panel workflows incrementally.
- Add actions/macros, workspace presets, and configurable keyboard shortcuts.

### 5. File I/O and Native Integrations

- Add PSD round-trip support with layer preservation where practical.
- Add RAW import, color profile handling, batch processing, and export presets.
- Add native Windows shell integration after the application package boundary is stable.
- Add plugin discovery under `plugins/` once the internal APIs are explicit.

## Deferred Ideas

- Local-only background removal, upscaling, denoise, face restoration, and style-transfer tools.
- Animation/timeline support for GIF and APNG export.
- Touch-optimized toolbar layout.
- User-configurable cloud sync targets.

## Definition of Done

- Active planning remains in this file.
- Completed work is added to `COMPLETED.md`.
- Research conclusions are added to `RESEARCH_REPORT.md`.
- Historical plans and references remain archived, not duplicated at the repo root.
