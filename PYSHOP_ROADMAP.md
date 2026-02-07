# PyShop Development Roadmap
## A Phased Plan to Build a Full Photoshop Clone in Python

---

## Current State (Baseline)

**File:** `pyshop_image_editor.py` — 2,968 lines, 5 classes, 120 methods

### What Exists Today
- **14 tools:** Move, Brush, Eraser, Fill, Eyedropper, Magic Wand, Rect Select, Ellipse Select, Lasso, Crop, Text, Clone Stamp, Gradient, Free Transform
- **Layer system:** Opacity, 10 blend modes, visibility, lock, reorder, masks (paintable), adjustment layers (brightness/contrast, hue/sat, levels)
- **Canvas:** Zoom, pan, marching ants selection, rulers, draggable guides, checkerboard transparency, zoom-to-fit on resize
- **Painting:** Brush with Gaussian hardness/softness, tablet pressure support
- **History:** 30-state undo/redo with full layer snapshots including masks
- **Selection:** Rect, Ellipse, Lasso, Magic Wand, feathering, select all/deselect/invert
- **Filters:** Gaussian Blur, Box Blur, Motion Blur, Sharpen, Unsharp Mask, Edge Detect, Emboss, Contour, Posterize, Solarize, Pixelate
- **Adjustments:** Brightness/Contrast, Hue/Saturation, Levels, Invert, Grayscale, Auto Contrast, Color Balance
- **I/O:** New, Open, Save, Save As, Export PNG
- **UI:** Dark theme QSS, vertical toolbar, dynamic per-tool options bar, basic layer panel, color swatches with swap

### What's Missing (Gap to Photoshop Parity)
- ~57 more tools across 7 additional tool groups
- Tool grouping/nesting (click-and-hold sub-menus)
- Full menu bar structure (11 menus, ~400+ menu items)
- Dockable panel system (20+ panels vs. 1 fixed panel today)
- Layer styles/effects, smart objects, clipping masks, groups
- Pen/path tools, shape tools, type system
- Dodge/Burn/Sponge, Blur/Sharpen/Smudge canvas tools
- Healing/Patch/Content-Aware retouching
- Channels, paths, color modes beyond RGB
- Navigator, histogram, info panel, actions/macros
- Filter gallery, 60+ more filters, smart filters
- Workspace presets, status bar, screen modes
- Non-destructive editing pipeline

---

## Architecture Principles

These principles apply across ALL phases:

1. **Modular file structure** — Split the monolith into packages: `pyshop/core/`, `pyshop/tools/`, `pyshop/panels/`, `pyshop/filters/`, `pyshop/ui/`
2. **Tool registry pattern** — Each tool is a self-contained class inheriting `BaseTool`, registered by ID. Tools define their own options bar widgets, cursors, and input handlers.
3. **Command/Action pattern** — Every undoable operation is an `Action` object with `execute()` and `undo()` methods, enabling granular history instead of full-layer snapshots.
4. **Signal-driven updates** — Use Qt signals to decouple panels from core state. Layer changes emit signals; panels listen and refresh.
5. **Non-destructive pipeline** — Adjustment layers, smart filters, and masks compose at render time. The original pixel data is never modified by adjustments.
6. **Async rendering** — Heavy operations (filters, compositing large images) run in background threads with progress indication to keep the GUI responsive.

---

## Phase 1: Architecture Refactor & Project Skeleton
**Goal:** Transform the monolith into a maintainable, extensible project structure.
**Estimated scope:** ~4,000 lines across ~30 files

### 1.1 — Project structure
```
pyshop/
    __main__.py              # Entry point
    app.py                   # QApplication setup, splash screen
    constants.py             # Tool IDs, blend modes, default sizes, colors
    settings.py              # QSettings wrapper for preferences

    core/
        document.py          # Document model (layers, dimensions, color mode, metadata)
        layer.py             # Layer, LayerGroup, AdjustmentLayer, FillLayer, TextLayer, ShapeLayer, SmartObject
        history.py           # Action-based undo/redo with command pattern
        selection.py         # Selection mask operations (add, subtract, intersect, feather, grow, smooth, transform)
        color.py             # Color model (RGB, HSB, CMYK, Lab conversions, color picker data)
        blend.py             # All 27 blend mode implementations (numpy vectorized)
        compositor.py        # Layer stack compositing engine with caching
        brush_engine.py      # Brush tip generation, dynamics, stroke interpolation
        path.py              # Bezier path data structure (for pen tool, shapes, text paths)

    tools/
        __init__.py          # Tool registry + BaseTool abstract class
        move.py              # Move + Artboard
        marquee.py           # Rect, Ellipse, Single Row, Single Column
        lasso.py             # Lasso, Polygonal Lasso, Magnetic Lasso
        selection_tools.py   # Object Selection, Quick Selection, Magic Wand
        crop.py              # Crop, Perspective Crop, Slice, Slice Select
        eyedropper.py        # Eyedropper, Color Sampler, Ruler, Note, Count
        healing.py           # Spot Healing, Healing Brush, Patch, Content-Aware Move, Red Eye
        brush.py             # Brush, Pencil, Color Replacement, Mixer Brush
        stamp.py             # Clone Stamp, Pattern Stamp
        history_brush.py     # History Brush, Art History Brush
        eraser.py            # Eraser, Background Eraser, Magic Eraser
        gradient.py          # Gradient (5 types), Paint Bucket
        focus.py             # Blur, Sharpen, Smudge (canvas tools)
        tonal.py             # Dodge, Burn, Sponge
        pen.py               # Pen, Freeform Pen, Curvature Pen, anchor point tools
        type_tool.py         # Horizontal/Vertical Type, Type Mask
        path_select.py       # Path Selection, Direct Selection
        shapes.py            # Rectangle, Ellipse, Triangle, Polygon, Line, Custom Shape
        hand_zoom.py         # Hand, Rotate View, Zoom
        transform.py         # Free Transform (unified: scale, rotate, skew, distort, warp, perspective)

    panels/
        __init__.py          # Panel registry + BasePanel
        layers.py            # Layer panel with full feature set
        properties.py        # Context-sensitive properties
        channels.py          # Channel panel
        paths.py             # Path panel
        history.py           # Visual history panel
        color.py             # Color sliders + spectrum
        swatches.py          # Swatch grid
        brushes.py           # Brush preset browser
        brush_settings.py    # Full brush settings (dynamics, scattering, texture, etc.)
        character.py         # Character formatting
        paragraph.py         # Paragraph formatting
        info.py              # Cursor position, color readouts, dimensions
        navigator.py         # Thumbnail + viewport rectangle
        histogram.py         # Live histogram
        adjustments.py       # Adjustment layer creation grid
        actions.py           # Macro recording/playback
        styles.py            # Layer style presets
        gradients.py         # Gradient presets
        patterns.py          # Pattern presets

    filters/
        __init__.py          # Filter registry
        blur.py              # All blur types (Gaussian, Motion, Radial, Lens, Surface, Smart, Box, Shape)
        sharpen.py           # Sharpen, Smart Sharpen, Unsharp Mask
        distort.py           # Displace, Pinch, Polar Coordinates, Ripple, Spherize, Twirl, Wave, ZigZag
        noise.py             # Add Noise, Despeckle, Dust & Scratches, Median, Reduce Noise
        pixelate.py          # Color Halftone, Crystallize, Facet, Fragment, Mezzotint, Mosaic, Pointillize
        render.py            # Clouds, Difference Clouds, Fibers, Lens Flare, Lighting Effects
        stylize.py           # Diffuse, Emboss, Extrude, Find Edges, Oil Paint, Solarize, Wind
        other.py             # Custom, High Pass, Maximum, Minimum, Offset
        gallery.py           # Filter Gallery dialog (Artistic, Brush Strokes, Sketch, Texture groups)

    ui/
        main_window.py       # QMainWindow, menu bar, workspace management
        canvas_widget.py     # QGraphicsView-based canvas with rulers
        ruler_widget.py      # Ruler + guide creation
        options_bar.py       # Dynamic tool options bar
        toolbar.py           # Vertical toolbar with grouped tools
        status_bar.py        # Document info status bar
        color_picker.py      # Full color picker dialog (HSB wheel, sliders, hex, eyedropper)
        dialogs/
            new_document.py  # New document dialog with presets
            image_size.py    # Image Size dialog (pixel/percent, resample methods, DPI)
            canvas_size.py   # Canvas Size dialog (anchor position grid)
            preferences.py   # Multi-tab preferences dialog
            layer_style.py   # Layer Style dialog (10 effect types)
            curves.py        # Curves adjustment dialog
            levels.py        # Levels adjustment dialog
            text_warp.py     # Warp Text dialog
            filter_dialogs.py # Common filter parameter dialogs with preview

    resources/
        icons/               # SVG or PNG tool icons (generated or bundled)
        brushes/             # Default brush presets (.abr parser or custom format)
        patterns/            # Default pattern presets
        gradients/           # Default gradient presets
        shapes/              # Default custom shapes
        workspaces/          # Workspace layout JSON files
```

### 1.2 — Core refactors
- **Document model:** Replace bare layer list with `Document` class holding dimensions, resolution (DPI), color mode, color profile, metadata, layer tree (supports groups), and active selection.
- **Action-based history:** Replace snapshot history with command objects. Each action stores a minimal diff (e.g., `PaintAction` stores only the affected rect of pixels before/after, not the entire layer). Target: 200+ undo states with reasonable memory usage.
- **Layer tree:** Replace flat list with tree supporting `LayerGroup` nodes. Each group has its own blend mode and opacity that affects all children.
- **Selection model:** Centralize selection mask operations into a `Selection` class with `add()`, `subtract()`, `intersect()`, `feather()`, `grow()`, `smooth()`, `transform()`, `from_path()`, `to_path()`.

### 1.3 — BaseTool framework
```python
class BaseTool:
    tool_id: str
    display_name: str
    shortcut: str
    icon: QIcon
    cursor: QCursor
    group_id: str            # Which toolbar slot this belongs to
    group_position: int      # Order within group

    def build_options_bar(self, bar: QToolBar) -> None: ...
    def on_press(self, event: CanvasEvent) -> None: ...
    def on_move(self, event: CanvasEvent) -> None: ...
    def on_release(self, event: CanvasEvent) -> None: ...
    def on_key_press(self, event: QKeyEvent) -> None: ...
    def on_activate(self) -> None: ...
    def on_deactivate(self) -> None: ...
    def paint_overlay(self, painter: QPainter) -> None: ...  # Tool-specific canvas overlays
```

### 1.4 — Migrate existing tools
Port all 14 current tools from inline `if/elif` blocks in `CanvasWidget` into individual tool classes. Functionality stays identical — this is a pure structural refactor. Validate by running the app and confirming every tool still works identically.

### Phase 1 deliverable
A working app with identical functionality to the current 2,968-line monolith, but split across ~30 files with a clean architecture ready for rapid feature addition.

---

## Phase 2: Canvas Engine & Core Painting
**Goal:** Production-grade canvas and brush engine that can handle large images smoothly.
**Estimated scope:** ~3,000 new lines

### 2.1 — QGraphicsView canvas
Replace the current `QWidget`-based `CanvasWidget` with a `QGraphicsView` / `QGraphicsScene` architecture:
- Hardware-accelerated rendering via OpenGL viewport (`QOpenGLWidget`)
- Tiled rendering for large images (break canvas into 256x256 tile grid, only render visible tiles)
- Smooth zoom (animated, centered on cursor), pan, and rotation
- Bird's-eye view (hold H + click for instant zoom-out with viewport rectangle)
- Pixel grid overlay above 500% zoom
- Checkerboard transparency rendered in shader for performance

### 2.2 — Brush engine overhaul
- **Stroke interpolation:** Catmull-Rom spline between input points for smooth curves
- **Brush dynamics:** Size jitter, angle jitter, roundness jitter, scatter, each controllable by Off/Fade/Pen Pressure/Pen Tilt/Direction
- **Dual brush:** Second tip texture composited onto primary
- **Texture brush:** Pattern overlay on brush tip with depth control
- **Color dynamics:** Foreground/Background jitter, Hue/Saturation/Brightness jitter
- **Smoothing:** Pulled-string algorithm (1-100%) for stabilized strokes
- **Wet edges:** Opacity builds at stroke edges
- **Airbrush mode:** Continuous paint accumulation while held stationary
- **Performance target:** 60fps painting on a 4000x3000 canvas with a 500px brush

### 2.3 — Compositing engine
- Implement all **27 Photoshop blend modes** (numpy vectorized):
  - Normal, Dissolve
  - Darken, Multiply, Color Burn, Linear Burn, Darker Color
  - Lighten, Screen, Color Dodge, Linear Dodge (Add), Lighter Color
  - Overlay, Soft Light, Hard Light, Vivid Light, Linear Light, Pin Light, Hard Mix
  - Difference, Exclusion, Subtract, Divide
  - Hue, Saturation, Color, Luminosity
- **Layer group compositing:** Groups blend as a unit (isolate blending), then composite into the stack below
- **Clipping masks:** Layer clips to the alpha of the layer directly below
- **Pass-through mode:** Group blend mode that lets children interact with layers below the group
- **Caching:** Composite cache invalidated per-tile when a layer in that region changes

### 2.4 — Rulers, guides, and grid
- Rulers with configurable units (px, in, cm, mm, pt, pica, %)
- Right-click ruler to change units
- Smart guides (magenta, auto-appear during move/resize showing alignment + equal spacing)
- Configurable grid (spacing, subdivisions, line/dashed/dots style, color)
- Snap engine with 8px tolerance: snap to guides, grid, layer edges, canvas bounds, canvas center
- New Guide Layout dialog (columns, rows, gutters, margins)

### Phase 2 deliverable
A canvas that handles 8000x6000 images smoothly with GPU-accelerated rendering, a professional brush engine with dynamics, and pixel-accurate compositing across all 27 blend modes.

---

## Phase 3: Complete Tool Suite (Selection, Retouching, Drawing)
**Goal:** Implement all remaining tools to reach full toolbar parity.
**Estimated scope:** ~6,000 new lines

### 3.1 — Selection tools (complete the set)
| Tool | Key Implementation Details |
|------|---------------------------|
| **Polygonal Lasso** | Click to place vertices, double-click/close to complete. Straight-line segments. |
| **Magnetic Lasso** | Edge detection (Canny/Sobel) within a detection width. Frequency controls auto-anchor spacing. Pen Pressure varies width. |
| **Quick Selection** | Auto-expanding brush that detects edges. Uses local color similarity + edge detection to grow selection intelligently. |
| **Object Selection** | Draw rectangle or lasso around object, algorithm isolates it. Implement with GrabCut or similar segmentation. |
| **Select and Mask dialog** | Dedicated workspace: Onion Skin, Marching Ants, Overlay, Black/White, Black/White views. Edge detection refinement: Radius, Smart Radius, Smooth, Feather, Contrast, Shift Edge. Global Refinements, Decontaminate Colors. Output: Selection, Layer Mask, New Layer, New Document. |
| **Color Range** | Select by sampled colors with Fuzziness slider. Eyedropper + Add/Subtract samplers. Preview in dialog as grayscale mask. |

### 3.2 — Retouching tools
| Tool | Key Implementation Details |
|------|---------------------------|
| **Spot Healing Brush** | Content-Aware mode: analyze surrounding texture and seamlessly fill the brushed area. Proximity Match: sample nearest good pixels. |
| **Healing Brush** | Like Clone Stamp but blends the luminance and color of the destination with the texture of the source (Alt+click to set source). |
| **Patch Tool** | Draw selection around imperfection, drag to clean source area. Blends texture seamlessly. Normal and Content-Aware modes. |
| **Content-Aware Move** | Select region, drag to new position. Original area filled with Content-Aware Fill, moved content blended into destination. |
| **Red Eye Tool** | Click on red eye area: detect red channel spike in pupil region, replace with dark desaturated values. |
| **Color Replacement Tool** | Paint over areas: replace only the color (hue/saturation) while preserving luminance and texture. Tolerance + sampling mode controls. |
| **Mixer Brush** | Simulates wet painting: picks up color from canvas, mixes with reservoir. Controls: Wet (0-100%), Load, Mix, Flow. Clean/Load buttons between strokes. |

### 3.3 — Tonal and focus tools
| Tool | Key Implementation Details |
|------|---------------------------|
| **Dodge Tool** | Lightens areas. Range selector (Shadows/Midtones/Highlights) targets specific tonal range. Exposure control. Protect Tones checkbox. |
| **Burn Tool** | Darkens areas. Same Range/Exposure/Protect Tones controls as Dodge. |
| **Sponge Tool** | Mode: Saturate or Desaturate. Flow control. Vibrance checkbox (protects already-saturated areas). |
| **Blur Tool (canvas)** | Gaussian blur under brush stroke. Strength control (0-100%). Sample All Layers option. |
| **Sharpen Tool (canvas)** | Unsharp-mask-style sharpening under brush. Strength + Protect Detail checkbox. |
| **Smudge Tool** | Finger-painting: picks up color and drags it. Strength control. Finger Painting checkbox (uses foreground color). Sample All Layers. |

### 3.4 — Pen and path tools
| Tool | Key Implementation Details |
|------|---------------------------|
| **Pen Tool** | Click for corners, click-drag for smooth (Bezier handles). Live rubber-band preview. Path stored as `BezierPath` object. |
| **Curvature Pen** | Click to place points; curves are auto-calculated. Double-click for corner. Simplified Bezier workflow. |
| **Freeform Pen** | Draw freehand; path is auto-smoothed to Bezier curves on release. Magnetic option follows edges. |
| **Add/Delete Anchor Point** | Click on path segment to add point. Click existing point to delete. |
| **Convert Point** | Click smooth point → corner. Drag corner point → smooth. Drag one handle independently to create cusp. |
| **Path Selection** | Select entire paths, move them. Bounding box with transform handles for multiple paths. |
| **Direct Selection** | Select individual anchor points and handles. Drag to reshape. Shift+click for multi-select. |

### 3.5 — Shape tools
| Tool | Key Implementation Details |
|------|---------------------------|
| **Drawing modes:** Shape (vector layer with fill/stroke), Path (work path only), Pixels (rasterized directly) |
| **Rectangle** | 4 independent corner radius fields (linkable). Hold Shift for square. |
| **Ellipse** | Hold Shift for circle. Alt+Shift for circle from center. |
| **Triangle** | Adjustable corner radius per vertex. |
| **Polygon** | Sides field (3-100). Star option with indent/radius. |
| **Line** | Weight (stroke width). Arrowhead start/end options. |
| **Custom Shape** | Picker loaded from shape presets. Ships with default library of 100+ shapes. |
| **Common controls:** Fill (None, Solid, Gradient, Pattern), Stroke (same + width, alignment, dashes, caps, corners), Path Operations (New, Add, Subtract, Intersect, Exclude), Align Edges to pixel grid |

### 3.6 — Additional tools
| Tool | Key Implementation Details |
|------|---------------------------|
| **Pattern Stamp** | Paints with a repeating pattern tile. Aligned/Impressionist/Script modes. |
| **History Brush** | Paints from a snapshot history state. Set source state in History panel. |
| **Art History Brush** | Paints stylized strokes from history source. Style presets: Tight/Loose Short/Medium/Long/Curl, Dab. |
| **Background Eraser** | Erases to transparency by sampling and removing similar colors. Sampling: Continuous/Once/Background Swatch. |
| **Magic Eraser** | Click to erase all similar contiguous pixels (flood-fill deletion). Tolerance + Contiguous controls. |
| **Perspective Crop** | Define four-corner perspective crop area. Image is both cropped and de-warped. |
| **Frame Tool** | Create rectangular/elliptical placeholder frames. Drag images into frames; image clips to frame shape. |
| **Note Tool** | Place sticky-note annotations on the canvas (non-printing metadata). |
| **Count Tool** | Click to place numbered markers on image for counting objects. |
| **Ruler Tool** | Drag to measure pixel distance and angle between two points. Displays in Info panel and options bar. |

### Phase 3 deliverable
Complete toolbar with all ~71 tools implemented. Every toolbar slot populated, every tool functional with its appropriate options bar controls and keyboard shortcuts.

---

## Phase 4: Complete Menu System & Dialogs
**Goal:** Full menu bar with all 11 menus, complete keyboard shortcuts, and professional dialogs.
**Estimated scope:** ~5,000 new lines

### 4.1 — Menu bar infrastructure
- Build menus from a declarative data structure (JSON/dict) for maintainability
- Support: separators, submenus, checkable items, radio groups, dynamic items (Recent Files list)
- Proper shortcut management with conflict detection
- Menu items that gray out when not applicable (e.g., "Merge Down" grayed when on bottom layer)

### 4.2 — File menu
- **New Document dialog:** Presets panel (Photo, Print, Web, Mobile, Film), recent sizes, name, dimensions (px/in/cm/mm), resolution, color mode, bit depth, background contents, advanced (color profile, pixel aspect ratio)
- **Open:** Multi-format support — PSD (layer preservation), TIFF, PNG, JPEG, BMP, GIF, WebP, SVG (rasterize), RAW (via rawpy/libraw)
- **Save/Save As:** PSD format (layers, masks, adjustments, paths, metadata preserved), PNG, JPEG (quality slider), TIFF, BMP, GIF, WebP
- **Export As dialog:** Format selection, quality, scale percentage, canvas size/resize, metadata toggle
- **Place Embedded/Linked:** Insert images as Smart Object layers
- **Print dialog:** Preview, scale, position, color management, bleeds
- **Automate submenu:** Batch processing dialog, Contact Sheet
- **Scripts submenu:** Image Processor, Load Files into Stack

### 4.3 — Edit menu
- **Fill dialog:** Contents (Foreground, Background, Color, Content-Aware, Pattern, History, Black, White, 50% Gray), Mode (blend mode), Opacity, Preserve Transparency
- **Stroke dialog:** Width, Color, Location (Inside, Center, Outside), Blending (Mode, Opacity)
- **Content-Aware Fill workspace:** Preview area, sampling area brush, fill settings (color adaptation, rotation adaptation, scale, mirror, output)
- **Free Transform:** Unified transform with mode switching (Scale, Rotate, Skew, Distort, Perspective, Warp). Options bar shows X/Y/W/H/Rotation/Skew fields. Warp mode: preset meshes (Arc, Arch, Bulge, Shell, Flag, Wave, Fish, Rise, Fisheye, Inflate, Squeeze, Twist) + custom mesh editing.
- **Puppet Warp:** Place pins on image, drag to deform mesh around pins
- **Perspective Warp:** Define perspective planes, adjust grid to correct or change perspective
- **Define Brush/Pattern/Shape:** Capture from current selection/document
- **Preferences dialog (17 tabs):** General, Interface, Workspace, Tools, History Log, File Handling, Export, Performance (RAM, GPU, scratch disks, cache levels), Cursors, Transparency & Gamut, Units & Rulers, Guides Grid & Slices, Plug-ins, Type, Technology Previews

### 4.4 — Image menu
- **Image Size dialog:** Pixel dimensions, document size, resolution, resample checkbox, resampling algorithm selector (Nearest Neighbor, Bilinear, Bicubic, Bicubic Smoother, Bicubic Sharper, Preserve Details 2.0), constrain proportions chain link, Fit To presets
- **Canvas Size dialog:** Current size display, new size fields, anchor position grid (3x3), canvas extension color
- **Color Mode switching:** RGB, Grayscale, CMYK (simulated), Lab, Indexed Color, Bitmap. Bit depth: 8/16/32 bits per channel. Mode changes with proper conversion dialogs (indexed color palette options, etc.)
- **Image Rotation submenu:** 180, 90 CW, 90 CCW, Arbitrary (angle input dialog), Flip Canvas H/V
- **Adjustments submenu (full set, 22 items):** Each with a proper dialog featuring live preview, preset dropdown, auto button, and before/after comparison. Implement:
  - Brightness/Contrast (use legacy checkbox)
  - Levels (histogram, input/output levels, per-channel, auto, eyedroppers for black/gray/white point)
  - Curves (interactive graph, per-channel, presets, pencil/smooth modes)
  - Exposure (Exposure, Offset, Gamma Correction)
  - Vibrance (Vibrance + Saturation)
  - Hue/Saturation (Master + per-color range editing, Colorize mode)
  - Color Balance (Shadows/Midtones/Highlights, Preserve Luminosity)
  - Black & White (6 color sliders, Tint option, Auto, presets)
  - Photo Filter (Warming/Cooling/Color, Density, Preserve Luminosity)
  - Channel Mixer (per-output-channel source mixing, Monochrome)
  - Color Lookup (3DLUT, Abstract, Device Link — load .cube files)
  - Invert
  - Posterize (Levels input)
  - Threshold (slider with histogram preview)
  - Gradient Map (gradient editor applied to luminance)
  - Selective Color (per-color CMYK adjustment)
  - Shadows/Highlights (Amount, Tone, Radius for each; Color Correction, Midtone Contrast)
  - HDR Toning
  - Desaturate
  - Match Color
  - Replace Color (Hue/Sat/Lightness with color range selection)
  - Equalize

### 4.5 — Layer menu
- **Layer Style dialog:** Central dialog with 10 effect tabs. Each effect has: Enable checkbox, Blend Mode, Opacity, and effect-specific controls.
  - Drop Shadow (Angle, Distance, Spread, Size, Contour, Noise, Layer Knocks Out)
  - Inner Shadow (same controls, inward)
  - Outer Glow (Noise, technique Softer/Precise, Spread, Size, Contour, Range, Jitter)
  - Inner Glow (same, Source: Center/Edge)
  - Bevel & Emboss (Style: Outer/Inner/Emboss/Pillow/Stroke, Technique: Smooth/Chisel Hard/Chisel Soft, Depth, Size, Soften, Angle, Altitude, Gloss Contour, Highlight/Shadow mode+opacity)
  - Satin (Blend Mode, Opacity, Angle, Distance, Size, Contour, Invert)
  - Color Overlay (Color, Blend Mode, Opacity)
  - Gradient Overlay (Gradient, Style, Blend Mode, Opacity, Angle, Scale)
  - Pattern Overlay (Pattern, Blend Mode, Opacity, Scale, Link with Layer)
  - Stroke (Size, Position Inside/Center/Outside, Blend Mode, Opacity, Fill Type: Color/Gradient/Pattern)
- **New Fill Layer submenu:** Solid Color, Gradient, Pattern — each opens its own settings dialog
- **New Adjustment Layer submenu:** All 16 non-destructive adjustment types
- **Layer Mask submenu:** Reveal/Hide All, Reveal/Hide Selection, From Transparency, Delete, Apply, Enable/Disable, Unlink
- **Smart Objects submenu:** Convert, Edit Contents, Relink, Replace Contents, Export, Rasterize
- **Rasterize submenu:** Type, Shape, Fill Content, Vector Mask, Smart Object, Layer Style, Layer, All
- **Arrange submenu:** Bring to Front/Forward, Send Backward/to Back, Reverse
- **Align/Distribute submenus:** 6 align + 8 distribute options
- **Matting submenu:** Defringe, Remove Black/White Matte

### 4.6 — Select menu
- **Select and Mask** workspace (see Phase 3)
- **Color Range** dialog with preview (see Phase 3)
- **Focus Area** dialog: Auto-detect in-focus regions
- **Modify submenu:** Border, Smooth, Expand, Contract, Feather — each with px input dialog
- **Grow / Similar:** Grow expands selection to contiguous similar pixels. Similar selects all similar pixels non-contiguously.
- **Transform Selection:** Transform the selection boundary without affecting pixels
- **Save/Load Selection:** Store/recall named selections as alpha channels

### 4.7 — Filter menu
- **Filter Gallery dialog:** Multi-pane UI: filter category browser (left), large preview (center), active filter stack (right). Apply multiple filters in sequence with per-filter visibility and reordering. Preview updates live. Six categories, ~47 filters total (Artistic 15, Brush Strokes 8, Distort 3, Sketch 14, Stylize 1, Texture 6).
- **Liquify dialog:** Dedicated workspace with specialized tools: Forward Warp, Reconstruct, Smooth, Twirl CW/CCW, Pucker, Bloat, Push Left, Freeze/Thaw Mask. Mesh visualization. Face-Aware Liquify (eyes, nose, mouth, face shape sliders). Brush Size/Density/Pressure/Rate controls.
- **Camera Raw Filter:** Full raw processing dialog — White Balance, Exposure, Contrast, Highlights, Shadows, Whites, Blacks, Clarity, Dehaze, Vibrance, Saturation, Tone Curve, HSL, Split Toning, Sharpening, Noise Reduction, Lens Corrections, Effects.
- **Adaptive Wide Angle / Lens Correction / Vanishing Point** dialogs
- **Neural Filters:** Placeholder architecture for AI-powered filters (extensible plugin point)
- **Smart Filters:** When applied to Smart Object, filters become non-destructive with editable parameters, visibility toggle, blend mode, opacity mask

### 4.8 — View menu
- **Screen modes:** Standard, Full Screen with Menu Bar, Full Screen. Cycle with F key. Tab hides/shows panels.
- **Proof Setup/Colors:** Soft proofing simulation (Working CMYK, sRGB, Color Blindness Protanopia/Deuteranopia)
- **Zoom presets:** 25%, 33.3%, 50%, 66.7%, 100%, 200%, Print Size, Fit on Screen

### 4.9 — Type menu
- Anti-aliasing modes, OpenType features, Font Preview Size, Warp Text presets, Convert to Shape/Work Path, Match Font, Paste Lorem Ipsum

### 4.10 — Window menu
- Workspace presets (Essentials, Photography, Painting, Graphic and Web, Motion)
- New/Delete/Reset Workspace
- Panel toggle list (every panel with its shortcut)
- Arrange submenu (Tile, Cascade, 2-up through 6-up, Float, Consolidate, Match Zoom/Location/Rotation)

### Phase 4 deliverable
Complete menu system with all 11 menus and ~400+ items, professional-grade dialogs for every adjustment and feature, and keyboard shortcut parity with Photoshop defaults.

---

## Phase 5: Panel System & Dockable UI
**Goal:** Full dockable panel system with all major panels implemented.
**Estimated scope:** ~8,000 new lines

### 5.1 — Docking framework
- Custom `QDockWidget` subclass with Photoshop-like behavior:
  - Tab grouping (drag panel onto another panel's tab bar)
  - Vertical stacking within dock columns
  - Icon-only collapse mode (double-click title bar or click collapse button)
  - Auto-collapse: clicking outside an expanded iconic panel collapses it
  - Drop-zone highlighting: blue line for stack position, blue rectangle for tab grouping
  - Float/unfloat (Ctrl+drag to force float)
  - Panel minimum widths enforced
  - Workspace state save/restore via `QMainWindow.saveState()`

### 5.2 — Layers panel (full rebuild)
The single most complex panel. Complete feature set:

- **Filter bar (row 1):** Kind/Name/Effect/Mode/Attribute/Color/Smart Object filter dropdown + search field + enable/disable toggle
- **Blend mode + Opacity (row 2):** Grouped blend mode dropdown (27 modes in 6 sections) + opacity slider/field (scrubby label)
- **Lock options + Fill (row 3):** 5 lock icon buttons (Transparent Pixels, Image Pixels, Position, Artboard, All) + Fill opacity field
- **Layer list (main area):** Custom `QAbstractItemModel` + `QTreeView` with custom delegate for:
  - Eye icon (visibility toggle, Alt+click to solo)
  - Layer thumbnail (live-updating miniature)
  - Mask thumbnail (separate, with chain link icon between layer and mask thumbnails)
  - Layer name (double-click to rename inline)
  - Layer type badges (Smart Object icon, Adjustment icon, Text "T", Shape path icon)
  - Effects disclosure triangle + individual effect visibility eyes
  - Group folder expand/collapse
  - Drag-and-drop reordering within tree (including into/out of groups)
  - Multi-select (Shift+click range, Ctrl+click toggle)
  - Right-click context menu (Duplicate, Delete, Convert to Smart Object, Blending Options, Create Clipping Mask, Link, Flatten, Merge, Lock, Color label)
  - Layer color labels (None, Red, Orange, Yellow, Green, Blue, Violet, Gray)
- **Bottom button bar (row 4):** Link Layers, Add Layer Style (fx), Add Layer Mask, New Adjustment/Fill Layer, New Group, New Layer, Delete Layer — each with dropdown options on hold
- **Background layer behavior:** Padlock icon, locked position, double-click to convert to normal layer
- **Smart Object behavior:** Document-on-corner badge, double-click to edit contents in new window

### 5.3 — Properties panel
Context-sensitive panel that completely changes based on what's selected:

| Selected | Properties panel shows |
|----------|----------------------|
| Pixel layer | Transform fields (X, Y, W, H, Rotation), Quick Actions (Remove Background, Select Subject) |
| Adjustment layer | Full interactive controls for that adjustment type (same as Image > Adjustments dialog but inline) |
| Mask selected | Density slider (0-100%), Feather slider (0-1000px), Mask Edge button, Color Range button, Invert, Load/Apply/Disable/Delete buttons |
| Type layer | Full Character + Paragraph formatting inline |
| Shape layer | Fill/Stroke pickers, corner radius, dimensions, path operations |
| Smart Object | Linked file path, Edit Contents button, embed/link status |
| Document (nothing selected) | Canvas size, image size, resolution, color mode |

### 5.4 — Channels panel
- Composite channel (RGB) + individual channels (R, G, B) with visibility eyes and thumbnails
- Alpha channels below separator: Load as Selection, Save Selection as Channel, New Channel, Delete
- Spot color channels support
- Click channel to view single channel as grayscale, Shift+click to toggle composite visibility
- Keyboard shortcuts: Ctrl+2 (composite), Ctrl+3/4/5 (R/G/B)

### 5.5 — Paths panel
- Work Path (temporary, italicized), named saved paths, shape vector masks
- Thumbnails for each path
- Bottom buttons: Fill Path, Stroke Path, Load Path as Selection, Make Work Path from Selection, New Path, Delete Path

### 5.6 — History panel
- Snapshot area at top (initial state snapshot by default, can create additional)
- Chronological state list with tool/action icons and descriptive labels
- Click any state to revert (states below become grayed/dimmed)
- History Brush source column (click to set source for History Brush tool)
- Configurable max states (1-1000, default 50)
- Create New Document from State, Create Snapshot, Delete State buttons
- Non-linear history option (allow branching)

### 5.7 — Color panel
- Foreground/Background swatches with swap/reset
- Slider modes (via panel menu): HSB, RGB, Lab, CMYK, Web Color, Grayscale
- Gradient-filled slider tracks that update in real-time as other values change
- Color spectrum/ramp bar at bottom (modes: Hue Cube, Brightness Cube, Color Wheel, RGB/CMYK Spectrum, Grayscale Ramp, Current Colors)
- Out-of-gamut indicators (CMYK warning triangle, web-safe warning square)

### 5.8 — Brush Settings panel
The most control-dense panel. Full implementation:

- **Left column:** Category list with enable checkboxes and lock icons:
  - Brush Tip Shape (always visible), Shape Dynamics, Scattering, Texture, Dual Brush, Color Dynamics, Transfer, Brush Pose
  - Simple toggles: Noise, Wet Edges, Build-up (Airbrush), Smoothing, Protect Texture
- **Right area:** Detailed controls for the selected category:
  - **Brush Tip Shape:** Tip preview grid, Size 1-5000px, Flip X/Y, Angle 0-360 (scrubby circle), Roundness 0-100% (scrubby ellipse), Hardness 0-100%, Spacing 1-1000%
  - **Shape Dynamics:** Size/Angle/Roundness Jitter 0-100% each with Control (Off, Fade [steps], Pen Pressure, Pen Tilt, Stylus Wheel, Initial Direction, Direction, Rotation)
  - **Scattering:** Scatter 0-1000%, Both Axes checkbox, Count 1-16, Count Jitter
  - **Texture:** Pattern picker, Scale 1-1000%, Mode (blend), Depth 0-100%, Depth Jitter, Texture Each Tip checkbox
  - **Dual Brush:** Second tip picker, Mode, Size, Spacing, Scatter, Count
  - **Color Dynamics:** FG/BG Jitter, Hue/Saturation/Brightness Jitter 0-100%, Purity -100 to +100
  - **Transfer:** Opacity/Flow Jitter 0-100% each with Control
  - **Brush Pose:** Tilt X/Y override, Rotation override, Pressure override
- **Bottom:** Live stroke preview that updates in real-time as settings change

### 5.9 — Character and Paragraph panels
- **Character:** Font family (searchable dropdown with preview), font style, size, leading, kerning (Metrics/Optical/manual), tracking, vertical/horizontal scale, baseline shift, color swatch, 8 style buttons (Faux Bold, Faux Italic, All Caps, Small Caps, Superscript, Subscript, Underline, Strikethrough), OpenType toggles, language dropdown, anti-aliasing
- **Paragraph:** 7 alignment buttons, indent left/right/first line, space before/after, hyphenate

### 5.10 — Info panel
- Two color readouts (configurable: Actual Color, RGB, HSB, CMYK, Lab, Web) showing values under cursor
- Cursor X, Y coordinates
- Selection/document W, H dimensions
- During adjustments: before/after color values side by side

### 5.11 — Navigator panel
- Thumbnail preview of entire document (live-updating)
- Red viewport rectangle overlay (drag to pan)
- Zoom slider at bottom with mountain icons
- Zoom percentage field (editable)

### 5.12 — Histogram panel
- Three view modes: Compact, Expanded, All Channels
- Channel dropdown: Composite, individual channels, Luminosity, Colors
- Source dropdown: Entire Image, Selected Layer, Adjustment Composite
- Statistics: Mean, Std Dev, Median, Pixels, Level, Count, Percentile, Cache Level
- Warning icon when cached (click to refresh)

### 5.13 — Adjustments panel
- 4x4 icon grid for creating adjustment layers (16 types)
- Click icon = create adjustment layer above active layer
- Each icon shows recognizable symbol for its adjustment type
- Tooltips with adjustment names

### 5.14 — Swatches, Gradients, Patterns, Styles panels
- Grid display of presets in collapsible folder groups
- Click to apply (foreground color / active gradient / active pattern / layer style)
- New, New Group, Delete buttons
- Drag-and-drop reordering
- Import/Export preset files
- Right-click context menu (Rename, Delete, New Swatch)

### 5.15 — Actions panel
- Action Sets (folders) containing Actions containing Steps
- Bottom buttons: Stop, Record (red circle), Play (triangle), New Set, New Action, Delete
- Include/Exclude checkboxes and modal dialog indicators per step
- Record mode captures user actions as replayable steps
- Button Mode toggle (panel menu) for one-click execution
- Batch processing integration (File > Automate > Batch)

### 5.16 — Other panels
- **Timeline:** Frame animation mode (frame thumbnails, delay, loop) and video timeline mode (tracks, keyframes)
- **Layer Comps:** Save and restore named layer states (visibility, position, appearance)
- **Clone Source:** Up to 5 source references with offset, scale, rotation, overlay preview
- **Glyphs:** Font selector, glyph grid, category filter, recently used row
- **Measurement Log:** Records ruler and count measurements

### Phase 5 deliverable
Full dockable panel system with 20+ panels implemented, workspace save/restore, and complete Layers panel with all professional features.

---

## Phase 6: Type System, Shapes & Vector Engine
**Goal:** Professional text editing and vector shape creation.
**Estimated scope:** ~4,000 new lines

### 6.1 — Type engine
- **Point type:** Click to create single-line text, grows horizontally
- **Paragraph type:** Click-drag to create text box, text wraps within bounds
- **Font rendering:** Use Qt's font system with full OpenType support
- **Live editing:** Inline text editing directly on canvas (not in a separate dialog)
- **Per-character formatting:** Select ranges of text and apply different font, size, color, style
- **Warp Text:** 15 warp presets (Arc, Arch, Bulge, Shell Upper/Lower, Flag, Wave, Fish, Rise, Fisheye, Inflate, Squeeze, Twist) with Bend, Horizontal/Vertical Distortion sliders
- **Type on Path:** Place text along a Bezier path
- **Convert to Shape:** Rasterize type outlines to vector paths (editable with Direct Selection)
- **Convert to Work Path:** Create path from type outlines without rasterizing
- **Rasterize Type:** Convert to pixel layer
- **Type layer behavior:** Non-destructive; double-click to re-enter editing mode. Type layers have full Character+Paragraph formatting stored as metadata.
- **Anti-aliasing modes:** None, Sharp, Crisp, Strong, Smooth
- **Missing font handling:** Detection, substitution, Match Font (visual font matching against document fonts and installed fonts)

### 6.2 — Vector/shape engine
- **Shape layers:** Vector layers rendered at any zoom without quality loss
- **Fill types:** None, Solid Color, Gradient (linear/radial/angle/reflected/diamond), Pattern
- **Stroke types:** Same fill options + Width, Alignment (Inside/Center/Outside), Caps (Butt/Round/Square), Corners (Miter/Round/Bevel), Dash pattern (predefined + custom)
- **Path operations:** Union, Subtract, Intersect, Exclude — boolean operations on overlapping shapes within the same shape layer
- **Align Edges:** Snap vector shape edges to pixel grid for crisp rendering
- **Live Shape properties:** Rectangle corner radii, polygon sides, star indent all remain editable after creation via Properties panel
- **Custom Shape library:** Ship with ~100 default custom shapes, importable/exportable

### 6.3 — Gradient editor
- **Full gradient editor dialog:** Color stops (drag to position, click below bar to add, drag off to delete), Opacity stops (top of bar), Midpoint diamonds between stops, Smoothness slider
- **Gradient types:** Solid, Noise (Roughness, Color Model, Restrict Colors, Add Transparency)
- **Preset management:** Default gradients organized in folders, New/Rename/Delete
- **Apply modes:** Gradient Tool (5 shapes), Gradient Fill Layer, Gradient Overlay layer style, Gradient Map adjustment

### Phase 6 deliverable
Professional text editing with full formatting, vector shape creation with boolean operations, and a complete gradient editor.

---

## Phase 7: PSD File Format & Advanced I/O
**Goal:** Full PSD read/write and broad format support.
**Estimated scope:** ~3,000 new lines

### 7.1 — PSD format support
Use `psd-tools` library as a starting point, extend for full write support:

**Read (import):**
- Layer tree (groups, nesting)
- Pixel layers with blend modes and opacity
- Text layers (formatted text recovery)
- Shape layers (vector path data)
- Adjustment layers (type + parameters)
- Layer masks and vector masks
- Layer styles/effects (all 10 types)
- Smart Objects (embedded/linked)
- Channels (alpha, spot colors)
- Paths (named paths, work path)
- Guides and slices
- ICC color profile
- Image metadata (EXIF, IPTC, XMP)
- Bit depth (8/16/32)

**Write (export):**
- Composite the full PSD with all layer data
- Preserve round-trip fidelity: open PSD → save PSD → open in Photoshop = identical
- Flatten composite stored in PSD for compatibility with apps that can't parse layers

### 7.2 — Additional format support
| Format | Read | Write | Notes |
|--------|------|-------|-------|
| PNG | Full (16-bit, alpha, metadata) | Full (compression level, interlace) | |
| JPEG | Full (EXIF preservation) | Full (quality 0-100, progressive, subsampling) | |
| TIFF | Layers, 16/32-bit, CMYK | Full | |
| WebP | Lossy + Lossless | Lossy + Lossless (quality) | |
| BMP | Full | Full | |
| GIF | Animated (→ Timeline frames) | Animated (from Timeline) | |
| SVG | Rasterize at resolution | Vector export from shape/path layers | |
| PDF | Multi-page, rasterize per page | Export (single page, multi-page from artboards) | |
| RAW | CR2, NEF, ARW, DNG via rawpy/libraw | N/A | Opens into Camera Raw dialog |
| ICO | Full | Full (multi-size) | |
| EXR/HDR | 32-bit float | 32-bit float | |
| HEIC/HEIF | Via pillow-heif | Via pillow-heif | |

### 7.3 — Export system
- **Export As dialog:** Format picker, quality/compression, canvas resize/scale, metadata strip, color profile conversion, preview with file size estimate
- **Save for Web (Legacy):** Side-by-side 2-up/4-up comparison, JPEG/PNG/GIF/WebP with live file size, dither options, color table for GIF
- **Quick Export:** One-click export with saved preferences (format, quality, destination)
- **Batch export:** Export all layers as individual files, artboards as files/PDF

### Phase 7 deliverable
Full PSD round-trip fidelity, support for 15+ image formats, and professional export dialogs.

---

## Phase 8: Performance, Polish & Platform
**Goal:** Production-ready performance, platform packaging, and UI polish.
**Estimated scope:** ~3,000 new lines

### 8.1 — Performance optimization
- **GPU compositing:** Use OpenGL shaders for blend modes and layer compositing on GPU
- **Tiled rendering:** Only re-composite tiles that contain changed pixels
- **Background threading:** All filter applications, exports, and batch operations on worker threads with cancel support and progress bars
- **Memory management:** Tile swapping to disk for very large images (>500MP), configurable RAM/scratch disk allocation
- **Lazy loading:** Only decode visible portion of very large files
- **Cache strategy:** Composite cache per layer group, invalidated on change

### 8.2 — UI polish
- **Custom SVG icons** for all 71 tools (matching Photoshop's visual language)
- **Scrubby sliders:** Click-drag on any numeric label to scrub the value (Photoshop signature interaction)
- **Tool cursors:** Brush size circle cursor, crosshair cursor, precise mode (Caps Lock toggle)
- **Splash screen** with loading progress
- **Tooltips** with tool name, shortcut, and brief description
- **Right-click context menus** everywhere (canvas, layers, channels, paths, tool options)
- **Drag-and-drop:** Drop images onto canvas to place, drop colors onto swatches, drag layers between documents
- **HiDPI/Retina support:** Proper scaling on 2x/3x displays via Qt's device pixel ratio
- **Dark/Light/Medium gray theme options** matching Photoshop's 4 brightness levels (Preferences > Interface)

### 8.3 — Keyboard shortcut system
- Complete default shortcut set matching Photoshop defaults
- **Keyboard Shortcuts dialog:** Customizable shortcuts for every menu item, tool, and panel toggle
- Conflict detection with resolution suggestions
- Import/Export shortcut sets
- Shortcut cheat sheet (printable)

### 8.4 — Status bar
- Zoom percentage field (editable, click to type)
- Document info area with selectable display mode (via dropdown):
  - Document Sizes (flat / layered)
  - Document Profile
  - Document Dimensions
  - Scratch Sizes (RAM usage)
  - Efficiency (%)
  - Timing (last operation duration)
  - Current Tool name
- Click-and-hold popup showing document width, height, channels, resolution

### 8.5 — Platform packaging
- **Windows:** PyInstaller/Nuitka → single `.exe` installer (NSIS or MSI). Start Menu shortcut, file associations (.psd, .pyshop), "Open with" integration.
- **macOS:** py2app → `.dmg` with drag-to-Applications. Code signing and notarization. Retina + Apple Silicon native.
- **Linux:** AppImage for universal distribution. Flatpak for sandboxed install. `.deb` package.
- **Auto-update:** Built-in update checker with download and restart

### 8.6 — Configuration and preferences persistence
- All preferences saved via `QSettings` (platform-native storage)
- Recent files list (with thumbnails)
- Workspace layouts (JSON export/import)
- Tool presets
- Custom keyboard shortcuts
- Brush/gradient/pattern/swatch library paths

### Phase 8 deliverable
Production-ready application with smooth performance on large images, complete keyboard shortcut parity, platform installers, and professional UI polish.

---

## Phase 9: Advanced & Stretch Features
**Goal:** Implement power-user and differentiating features.
**Estimated scope:** Variable, 5,000+ lines

### 9.1 — Smart Objects
- Embed any layer or group as a Smart Object (stores original data)
- Double-click to edit in a separate document window; save to update the Smart Object
- Transform without quality loss (re-rasterizes from source on every transform)
- Linked Smart Objects (reference external file, auto-update when file changes)
- Smart Filters: filters applied to Smart Objects are non-destructive, reorderable, with individual visibility, blend mode, opacity, and mask

### 9.2 — Content-Aware technology
- **Content-Aware Fill:** Analyze surrounding texture/structure and seamlessly fill selected region. Implement using PatchMatch or Poisson blending algorithms.
- **Content-Aware Scale:** Scale image while protecting important content (face detection, alpha channel protection). Uses seam carving (Seam Carving / Retargeting algorithm).
- **Content-Aware Move:** Relocate objects, fill the hole, blend at destination.

### 9.3 — Advanced selections
- **Refine Edge / Select and Mask:** Full edge refinement workspace
- **Focus Area:** Auto-detect in-focus regions based on contrast analysis
- **Subject/Sky selection:** ML-based auto-selection (integrate with ONNX Runtime or similar for a lightweight segmentation model)

### 9.4 — Color management
- ICC profile support (embed, assign, convert)
- Soft proofing (simulate CMYK output on RGB display)
- Color blindness simulation (Protanopia, Deuteranopia)
- Gamut warning visualization

### 9.5 — Automation and scripting
- **Actions panel** fully functional: record, playback, batch
- **Python scripting console:** Built-in REPL for automating PyShop via Python API
- **Plugin architecture:** Define a plugin API so third-party tools, filters, and panels can be loaded from a plugins directory

### 9.6 — Multi-document and artboards
- Tabbed multi-document interface with drag-to-float
- Tile/Cascade/2-up to 6-up layouts
- Artboard tool for multiple canvas areas in a single document
- Match Zoom/Location/Rotation across documents

### Phase 9 deliverable
Smart Objects with non-destructive editing, content-aware algorithms, ML-powered selections, full color management, scripting console, and plugin architecture.

---

## Summary: Phase Dependency Map

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 6
   │            │            │
   │            ▼            ▼
   │       Phase 4 ◄──── Phase 5
   │            │            │
   │            ▼            ▼
   │       Phase 7 ──→ Phase 8 ──→ Phase 9
   │
   └──→ (All phases depend on Phase 1 architecture)
```

| Phase | Name | Est. Lines | Dependencies | Priority |
|-------|------|-----------|-------------|----------|
| 1 | Architecture Refactor | ~4,000 | None (baseline) | **Critical** |
| 2 | Canvas Engine & Painting | ~3,000 | Phase 1 | **Critical** |
| 3 | Complete Tool Suite | ~6,000 | Phase 2 | **High** |
| 4 | Menus & Dialogs | ~5,000 | Phase 1 | **High** |
| 5 | Panel System & Dockable UI | ~8,000 | Phase 1 | **High** |
| 6 | Type, Shapes & Vectors | ~4,000 | Phase 3 | **Medium** |
| 7 | PSD Format & I/O | ~3,000 | Phase 4, 5 | **Medium** |
| 8 | Performance & Polish | ~3,000 | Phase 7 | **Medium** |
| 9 | Advanced & Stretch | ~5,000+ | Phase 8 | **Low** |

**Total estimated codebase at completion: ~40,000-50,000 lines across ~100+ files**

---

## Recommended Libraries

| Library | Purpose |
|---------|---------|
| `PyQt6` / `PySide6` | GUI framework (QMainWindow, QDockWidget, QGraphicsView, signals/slots) |
| `Pillow (PIL)` | Image I/O, basic operations, format support |
| `numpy` | Pixel array operations, blend modes, brush computation |
| `scipy` | Gaussian blur, morphological operations, interpolation |
| `OpenCV (cv2)` | Edge detection, segmentation, perspective transforms, inpainting |
| `scikit-image` | Advanced filters, segmentation, feature detection |
| `psd-tools` | PSD file parsing (read) |
| `rawpy` / `libraw` | RAW photo format decoding |
| `colour-science` | ICC profile handling, color space conversions |
| `freetype-py` | Advanced font metrics (optional, Qt handles most) |
| `numba` | JIT compilation for performance-critical pixel operations |
| `PyOpenGL` | GPU-accelerated compositing and rendering |
| `onnxruntime` | ML model inference for smart selection features |
