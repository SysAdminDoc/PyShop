# PyShop Roadmap

Native desktop Python/PyQt6 Photoshop alternative, complement to the browser-based OpenShop. Roadmap focuses on what a native app can do that a browser can't — tablet input, RAM-hungry operations, native file handlers.

## Planned Features

### Editor Core
- Non-destructive adjustment layers (Levels, Curves, HSL) above pixel layers
- Layer masks (not just alpha) with feather + density
- Smart objects with editable source reference
- Vector shape / path layers with Bezier editing
- Layer groups with nested visibility + opacity

### Brush & Input
- Pressure-sensitive stylus (Wacom / Windows Ink) with Krita-style brush engine
- Custom brush import (.abr PhotoShop brush files)
- Symmetry + mirror modes for painting
- Brush stabilizer (lag / moving-average / pull-string)
- Smudge + clone stamp with source alignment options

### Selections
- Color range (fuzziness slider + multiple eyedropper picks)
- Quick mask / edit-in-mask mode
- Select subject via rembg / mediapipe-selfie (local)
- Refine edge with contrast / feather / shift
- Save / load alpha channels

### AI (local-only)
- Background removal (rembg)
- Smart upscale (Real-ESRGAN via ONNX Runtime)
- Denoise / face restore (GFPGAN)
- Style transfer starter pack (fast neural style, few presets)

### File I/O
- PSD read + write with layer preservation (via `psd-tools`)
- Raw camera import via rawpy + basic demosaic preview
- Batch processor (folder → action recipe → output)
- ICC color profile support

### Native Integrations
- Windows Explorer Preview handler
- Shell context menu ("Edit with PyShop")
- Scanner / webcam import (WIA / OpenCV)
- Printer output with color management

## Competitive Research
- **GIMP** — feature-rich, GTK UX dated. Lesson: lean on native Qt look + PSD round-trip to win the switch.
- **Krita** — best FOSS digital painting. Lesson: don't compete head-on; borrow brush engine ideas and focus on general-purpose editor.
- **Affinity Photo** — gold standard paid app. Lesson: adjustment layers and non-destructive mask workflow are table stakes.
- **Photopea (web) + OpenShop** — browser peers. Lesson: PyShop's wedge is stylus input, RAM, and native file handlers.

## Nice-to-Haves
- Scriptable actions (Python recipe files, record + replay)
- Animation / frames panel for GIF + APNG export
- Touch-optimized toolbar layout
- Cloud sync hook (user-configurable folder → S3/WebDAV)
- Plugin API (discover `.py` plugins under `plugins/`)
- Dockable panels with saved workspace presets

## Open-Source Research (Round 2)

### Related OSS Projects
- https://github.com/viliusle/miniPaint — Browser-based Photoshop clone, layer engine reference.
- https://github.com/igorski/bitmappery — Vue-based non-destructive editor with PSD I/O.
- https://github.com/GNOME/gimp — GIMP 3.0, gold standard for GEGL graph-based compositing.
- https://github.com/krita/krita — Industry-grade brush engine + tile-based canvas, LGPL.
- https://github.com/OliverBalfour/SimplePaint — Canvas editor with stylus/tablet dynamics.
- https://github.com/photonstorm/phaser — Not an editor, but Pixi/WebGL rendering patterns apply.
- https://github.com/Photopea/Photopea — Closed-source but behavior is exemplary; study UX, not code.
- https://github.com/aseprite/aseprite — Tile/pixel art editor with top-tier layer/frame model.

### Features to Borrow
- GEGL-style graph compositing (GIMP 3.0) — swap layer stack for a node graph of operations.
- Krita's brush engine: pressure + velocity + tilt + bristle simulation.
- Non-destructive smart objects (BitMappery) — layer holds original + adjustment stack.
- PSD layer write path (BitMappery) — currently ecosystem-standard for interop.
- Animation timeline + frame/cel panel (aseprite) — GIF/APNG export falls out naturally.
- Plugin SDK with Python entrypoint (GIMP's script-fu → PDB model, but Pythonic).
- Symmetry + perspective guides (Krita).
- Content-Aware Fill via PatchMatch (public implementations exist in OpenCV contrib).

### Patterns & Architectures Worth Studying
- **Tile-based canvas** (Krita, 64x64 tiles) — bounded memory for arbitrarily huge images; unlocks 16K+ canvases.
- **GEGL node graph** (GIMP) — every filter is a node, undo = rewind graph, selective re-render per tile.
- **Command pattern + snapshot interval** — undo history with periodic full-state snapshots and inter-snapshot diffs.
- **GPU tile render via Qt RHI / OpenGL** — brush strokes and filters run on GPU, CPU only manages tile cache.
- **Layer blend mode plugin interface** — each blend mode a small shader + Python fallback.
