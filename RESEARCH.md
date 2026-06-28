# Research - PyShop

## Executive Summary
PyShop is a PyQt5/Pillow/numpy desktop image editor that has grown quickly into a Photoshop-inspired shell with layers, masks, blend modes, selections, retouch tools, text/vector layers, panels, paths, macros, and tiled compositing. The strongest current shape is a native, local-first desktop editor with a broad UI surface; the highest-value direction is to make the document model, persistence, file safety, and async architecture trustworthy before adding more parity features. Top opportunities: harden image/PSD loading against vulnerable parser ranges and oversized files; stop lossy PSD saves from looking like round-trip saves; add a native layered project format; extract canvas/tool behavior from `pyshop_image_editor.py`; persist workspaces/macros with `QSettings`/document metadata; make destructive filters into an editable effect stack; add async progress/cancel for filters/import/export; cover GUI workflows with tests; and add open layered interchange via OpenRaster.

## Product Map
- Core workflows: create/open image, paint or retouch on layers, select/crop/transform, apply adjustments/filters, manage masks/groups/channels/paths, export/save.
- User personas: Windows/Linux desktop users who want a local Photoshop-like editor; hobby photo editors who need layers without a subscription; developers who want a hackable Python editor; privacy-sensitive users avoiding browser/cloud workflows.
- Platforms and distribution: Python 3.10-3.12, PyQt5 5.15.x, Pillow, numpy, psd-tools; source-run desktop app today, no installer/spec file yet.
- Key integrations and data flows: `pyshop_image_editor.py` owns UI state and file ops; `pyshop.core` owns layers/history/compositing helpers; Pillow handles raster formats; psd-tools imports PSD layers; exports currently flatten through Pillow.

## Competitive Landscape
- GIMP/GEGL: validates non-destructive filter stacks, graph-based operations, plug-ins, and large open-source editor longevity. Learn from its GEGL-backed editable effects and extension focus; avoid importing UI complexity before PyShop has a stable document model.
- Krita: strongest brush/resource ecosystem, tablet-first painting, dockers, scripting, and live brush previews. Learn from its resource preset model and brush editor depth; avoid becoming painting-only when PyShop's wedge is general photo/layer editing.
- Photopea: proves PSD, smart objects, scripts, and automation are table-stakes for Photoshop-compatible workflows. Learn from Photoshop-like scripting and smart-object automation; avoid network/server assumptions because PyShop should stay local-first.
- Affinity Photo / Pixelmator Pro: commercial users expect non-destructive RAW, effects, masks, batch/macros, and polished export. Learn from durable non-destructive editing and export UX; avoid prioritizing paid-cloud or platform-exclusive features.
- Paint.NET / Pinta / LazPaint: lightweight editors win by being predictable, fast, plugin-friendly, and easy to install. Learn from add-ins, layer UX, broad installers, and clear format support; avoid silent lossy behavior around layered files.
- Graphite: its node/procedural model is a leapfrog path for future non-destructive raster/vector editing. Learn from explicit operation graphs; avoid a full node UI until PyShop's basic document persistence is stable.
- darktable: sidecar/history-stack design is a strong model for never mutating originals and for recovery. Learn from edit-history persistence and read-only source handling; avoid forcing photo-library workflows into a layer editor.

## Security, Privacy, and Reliability
- Verified: `requirements.txt` allows Pillow `>=10.0,<13`, while public advisories report PSD-related out-of-bounds write fixes in Pillow 12.1.1/12.2.0; `pyshop_image_editor.py:1725` opens user-selected files directly through Pillow/psd-tools with no local preflight policy.
- Verified: `pyshop_image_editor.py:1754` saves `.psd` via `save_flattened_psd()` in `pyshop/core/psd.py`, so a layered document can be saved as a flattened PSD and lose masks, groups, text/vector metadata, paths, guides, channels, and adjustment layers.
- Verified: errors use `QMessageBox`/status text only (`pyshop_image_editor.py:1741`, `pyshop_image_editor.py:1763`); there is no crash log, import/export diagnostics panel, or recoverable session file.
- Verified: heavy operations run on the GUI thread (`pyshop_image_editor.py:1955`, filters at `pyshop_image_editor.py:2062` onward, PSD import at `pyshop_image_editor.py:1725`), so large files and filters can freeze the app.
- Verified: workspace presets and macros are memory-only (`pyshop_image_editor.py:1570`, `pyshop_image_editor.py:1609`), so automation and layout work disappear on restart.
- Missing guardrails: max pixel/count policy with user-facing recovery, dependency lower-bound security pin, atomic saves, autosave/recovery, explicit lossy-export labeling, file-format capability matrix, and log-backed error reporting.

## Architecture Assessment
- `pyshop_image_editor.py` remains the main integration bottleneck: `CanvasWidget` handles rendering/input/tools and `ImageEditor` owns document state, file I/O, panels, menus, history, macros, and filters. Extracting a `Document` object and `BaseTool` handlers is prerequisite work for safer persistence, testing, and plugin APIs.
- `pyshop/core/layer.py` is metadata-rich but not document-rich: resolution, color profile, bit depth, metadata, guides, paths, channels, macros, workspace state, and file provenance are editor attributes or absent.
- `pyshop/core/compositor.py` has useful tile paths, but `TiledCompositeCache` keys only by tile rectangle; correctness depends on manual invalidation from UI paths, so future background rendering needs document revision keys.
- `pyshop/core/psd.py` imports pixel descendants but skips group semantics and writes flattened PSD only; use it as an import/export adapter, not as the native project format.
- Test gaps: existing tests cover core helpers and import smoke, but not open/save loss, PSD warnings, macro replay, dock persistence, GUI tool flows, file-error recovery, accessibility labels/focus, or large-image guardrails.
- Documentation gaps: README claims common format save/open support but does not disclose layered PSD limitations or the absence of a native project format.

## Rejected Ideas
- Full Photoshop keyboard shortcut parity: rejected because repo rules explicitly require no keyboard shortcuts; source was the archived Photoshop GUI reference.
- Cloud sync targets: rejected for now because PyShop's best wedge is local-first privacy; source was existing ROADMAP deferred ideas and Photopea/cloud-server API comparisons.
- Generative Fill / Neural Filters as a near-term priority: rejected until document persistence, plugin boundaries, and local model cost controls exist; source was Adobe Photoshop generative feature pages.
- Full PyQt6 migration now: rejected because PyQt5 is the supported runtime in README/CLAUDE and the current risk is architecture/persistence, not widget API age; source was Riverbank PyQt5/PyQt6 release notes.
- Full node-graph editor UI now: rejected as premature; Graphite/GEGL show the value, but PyShop first needs a serializable effect stack and document revision model.
- Mobile/touch-optimized UI now: rejected because the project is a desktop PyQt app and current gaps are file safety, persistence, packaging, and GUI responsiveness.

## Sources
Competitors:
- https://developer.gimp.org/core/roadmap/
- https://www.gimp.org/release-notes/gimp-3.2.html
- https://gegl.org/
- https://krita.org/en/features/
- https://docs.krita.org/en/reference_manual/brushes/brush_engines.html
- https://www.photopea.com/learn/scripts
- https://www.photopea.com/learn/smart-objects
- https://github.com/viliusle/miniPaint
- https://github.com/PintaProject/Pinta
- https://lazpaint.github.io/documentation/
- https://github.com/GraphiteEditor/Graphite
- https://www.darktable.org/about/features/
- https://paint.net/features.html
- https://www.adobe.com/products/photoshop/generative-fill.html
- https://www.affinity.studio/photo-editing-software
- https://www.apple.com/pixelmator-pro/

Standards and dependencies:
- https://www.openraster.org/
- https://psd-tools.readthedocs.io/
- https://pillow.readthedocs.io/en/stable/releasenotes/index.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-25990
- https://security.snyk.io/package/pip/pillow/12.0.0
- https://numpy.org/devdocs/numpy_2_0_migration_guide.html
- https://riverbankcomputing.com/news/PyQt_v5.15.11_Released
- https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html

Techniques and adjacent systems:
- https://gmic.eu/
- https://developer.gimp.org/resource/writing-a-filter/architecture-install/
- https://gfx.cs.princeton.edu/pubs/Barnes_2009_PAR/
- https://www.cs.jhu.edu/~misha/Fall07/Papers/Perez03.pdf
- https://faculty.runi.ac.il/arik/site/papers/seam-carving-for-content-aware-image-resizing-2007/
- https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_photo/py_inpainting/py_inpainting.html

## Open Questions
- Which native layered format should be the default save target: a PyShop-specific zip package, OpenRaster-compatible `.ora`, or both?
- Should public releases remain source-only until the PyQt GPL/commercial redistribution boundary is explicitly resolved?
