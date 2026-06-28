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

### 2. Project Skeleton and Architecture

### 3. Canvas, Layers, and Painting

### 4. Tool and Menu Parity

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

## Research-Driven Additions

- [ ] P0 - Harden image and PSD import before broad format expansion
  Why: User-selected image parsers are the highest-risk input surface, and current dependency bounds allow Pillow versions with published PSD-related memory-safety advisories.
  Evidence: `requirements.txt`; `pyshop_image_editor.py:1725`; NVD CVE-2026-25990; Snyk Pillow advisory; Pillow release notes.
  Touches: `requirements.txt`, `README.md`, `pyshop_image_editor.py`, `pyshop/core/psd.py`, `tests/`
  Acceptance: Pillow lower bound excludes vulnerable ranges; oversized/decompression-bomb inputs fail with a clear in-app error and log entry; PSD/Pillow open failures are covered by tests without launching the GUI.
  Complexity: M

- [ ] P0 - Prevent silent layered-data loss on PSD save
  Why: Saving a layered PyShop document as `.psd` currently flattens the composite, which can discard masks, groups, text/vector layers, paths, channels, guides, and adjustments.
  Evidence: `pyshop_image_editor.py:1754`; `pyshop/core/psd.py`; psd-tools limitations; Photopea smart-object/PSD workflow docs.
  Touches: `pyshop_image_editor.py`, `pyshop/core/psd.py`, `README.md`, `tests/`
  Acceptance: `.psd` save/export is explicitly labeled flattened unless true layered export is implemented; layered data is never overwritten through an ambiguous save path; tests assert lossy export labeling and metadata preservation in native saves.
  Complexity: M

- [ ] P0 - Add a native layered project format
  Why: PyShop has non-destructive metadata that PNG/JPEG/BMP and flattened PSD cannot preserve, so users need a default save format before more layer/effect features ship.
  Evidence: `pyshop/core/layer.py`; `ImageEditor` state for guides/channels/paths/macros; OpenRaster specification; darktable sidecar/history model.
  Touches: `pyshop/core/document.py`, `pyshop/core/layer.py`, `pyshop_image_editor.py`, `tests/`
  Acceptance: a reopened native project preserves layers, masks, groups, text/vector metadata, adjustments, paths, channel visibility, guides, macro steps, document dimensions, and active layer without flattening.
  Complexity: L

- [ ] P1 - Extract document state out of the main window
  Why: File I/O, panels, tools, history, and compositor invalidation all depend on `ImageEditor` fields, making persistence, autosave, tests, and plugin APIs harder than necessary.
  Evidence: `pyshop_image_editor.py:1265`; `pyshop/core/document.py`; archived architecture plan; GIMP/GEGL and Graphite operation-model references.
  Touches: `pyshop/core/document.py`, `pyshop/core/history.py`, `pyshop/core/compositor.py`, `pyshop_image_editor.py`, `tests/`
  Acceptance: a `Document` object owns dimensions, layers, active index, selection/path/channel/guide metadata, dirty revision, and file provenance; existing UI behavior remains covered by tests.
  Complexity: L

- [ ] P1 - Move canvas tools behind concrete tool handlers
  Why: `CanvasWidget` still routes most mouse behavior through inline tool conditionals, which blocks reliable tool testing and future plugin/tool discovery.
  Evidence: `pyshop_image_editor.py:538`; `pyshop_image_editor.py:609`; `pyshop_image_editor.py:662`; `pyshop/tools/registry.py`; Krita brush/tool architecture; Pinta add-in discussion.
  Touches: `pyshop/tools/`, `pyshop/ui/canvas_view.py`, `pyshop_image_editor.py`, `tests/`
  Acceptance: brush, eraser, fill, selection, crop, pen, text, shape, and retouch behavior live behind registered handler objects with focused tests for press/move/release behavior.
  Complexity: L

- [ ] P1 - Persist workspace presets and macros across restarts
  Why: Current macros and workspace presets are session-only, so automation and layout customization disappear after closing the app.
  Evidence: `pyshop_image_editor.py:1570`; `pyshop_image_editor.py:1609`; Qt `QMainWindow.saveState()`/`QSettings` documentation; Photopea scripts/actions model; Paint.NET history/plugins discussion.
  Touches: `pyshop_image_editor.py`, `pyshop/core/document.py`, `tests/`
  Acceptance: dock layout uses `QSettings` save/restore; macros can be saved, loaded, replayed, and stored in native projects; invalid macro commands fail with status/log feedback.
  Complexity: M

- [ ] P1 - Convert destructive filters into editable effect layers
  Why: Competitors and user expectations center on non-destructive effects, while PyShop filters currently mutate active layer pixels through `_apply_to_active()`.
  Evidence: `pyshop_image_editor.py:1955`; GIMP 3 non-destructive filter roadmap; GEGL architecture; Pixelmator/Affinity non-destructive feature pages.
  Touches: `pyshop/core/adjustments.py`, `pyshop/core/compositor.py`, `pyshop/core/layer.py`, `pyshop_image_editor.py`, `tests/`
  Acceptance: blur/sharpen/color filters can be added, reordered, disabled, edited, and serialized without mutating source pixels; destructive apply remains available as an explicit rasterize/apply command.
  Complexity: L

- [ ] P1 - Run long imports, exports, and filters asynchronously
  Why: PSD import, large raster open/save, and filters run on the GUI thread and can freeze the editor on large documents.
  Evidence: `pyshop_image_editor.py:1725`; `pyshop_image_editor.py:1754`; `pyshop_image_editor.py:2062`; Python stack async GUI convention; G'MIC/GEGL processing models.
  Touches: `pyshop_image_editor.py`, `pyshop/core/psd.py`, `pyshop/core/compositor.py`, `tests/`
  Acceptance: open/save/export/filter jobs report progress, support cancel where practical, keep the main window repaintable, and surface failures through status/log UI.
  Complexity: L

- [ ] P2 - Add OpenRaster import/export as an open layered interchange path
  Why: PSD round-trip is hard and psd-tools support is limited, while OpenRaster is designed for layered raster exchange between editors.
  Evidence: OpenRaster specification; LazPaint format support; `pyshop/core/psd.py`; existing active PSD round-trip roadmap item.
  Touches: `pyshop/core/document.py`, `pyshop/core/ora.py`, `pyshop_image_editor.py`, `tests/`
  Acceptance: `.ora` export/import preserves pixel layers, names, visibility, opacity, blend modes where supported, masks where practical, and produces a documented compatibility report for unsupported metadata.
  Complexity: M

- [ ] P2 - Add GUI workflow and accessibility regression tests
  Why: Current tests focus on core helpers/import smoke, but the product risk is in dock panels, dialogs, tool actions, no-shortcut behavior, focus order, and high-DPI layout.
  Evidence: `tests/`; `pyshop_image_editor.py`; Pinta UI bug/feature issues; PyQt high-DPI and QSettings references.
  Touches: `tests/`, `pyshop_image_editor.py`, `pyshop/ui/`
  Acceptance: pytest-qt covers new/open/save error paths, layer panel actions, macro replay, dock persistence, representative tool flows, accessible names for icon-only controls, and a no-registered-shortcuts assertion.
  Complexity: M

- [ ] P2 - Add crash/recovery logging and atomic save behavior
  Why: Current failures show modal errors or status text only, with no diagnostic trail or recovery path after filter/import/save failures.
  Evidence: `pyshop_image_editor.py:1741`; `pyshop_image_editor.py:1763`; Python GUI error-handling convention; darktable sidecar/recovery model.
  Touches: `pyshop_image_editor.py`, `pyshop/core/document.py`, `tests/`
  Acceptance: exceptions from import/export/filter jobs write a timestamped crash/error log; saves write atomically through a temp file; autosave/recovery files can restore an unsaved native project after restart.
  Complexity: M
