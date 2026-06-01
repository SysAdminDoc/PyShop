# Adobe Photoshop GUI architecture: a complete Python recreation reference

Adobe Photoshop's interface follows a precise spatial hierarchy: a menu bar and context-sensitive options bar span the top, a vertical toolbar docks left, dockable panels stack right, and the canvas fills the center. **Every element described below reflects Photoshop 2024/2025 (v25.x–v26.x)** defaults. This document covers all seven structural areas — toolbar, menus, options bar, panels, workspace layout, status bar, and canvas — in the exact detail needed to reconstruct the application in Python with a GUI framework such as PyQt, PySide, or wxPython.

---

## 1. Complete toolbar: every tool in exact order

The toolbar is a single-column vertical strip docked to the left edge. Tools sharing a slot are accessed via click-and-hold (indicated by a small triangle on the icon's lower-right corner). Press **Shift+[shortcut letter]** to cycle through grouped tools. The toolbar is divided into seven sections separated by thin horizontal dividers.

### Section 1 — Move and selection tools

**Slot 1: Move group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Move Tool** | V | ✦ | Four-headed cross arrow |
| Artboard Tool | V | | Rectangle with corner + |

**Slot 2: Marquee group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Rectangular Marquee** | M | ✦ | Dotted rectangle |
| Elliptical Marquee | M | | Dotted ellipse |
| Single Row Marquee | — | | Horizontal dotted line |
| Single Column Marquee | — | | Vertical dotted line |

**Slot 3: Lasso / Selection Brush group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Lasso Tool** | L | ✦ | Rope loop |
| Polygonal Lasso | L | | Angular lasso |
| Magnetic Lasso | L | | Lasso with magnet |
| Selection Brush Tool | L | | Brush with selection indicator (added 2025) |

**Slot 4: Object Selection group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Object Selection Tool** | W | ✦ | Rectangle with cursor arrow |
| Quick Selection Tool | W | | Brush with dotted border |
| Magic Wand Tool | W | | Sparkle wand |

### ─── Divider ───

### Section 2 — Crop and slice tools

**Slot 5: Crop group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Crop Tool** | C | ✦ | Overlapping right angles |
| Perspective Crop Tool | C | | Crop with perspective grid |
| Slice Tool | C | | Knife over rectangle |
| Slice Select Tool | C | | Slice with selection arrow |

**Slot 6: Frame Tool (standalone)**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Frame Tool** | K | ✦ | Rectangle placeholder with X |

### ─── Divider ───

### Section 3 — Measurement and sampling tools

**Slot 7: Eyedropper group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Eyedropper Tool** | I | ✦ | Pipette |
| Color Sampler Tool | I | | Pipette with crosshair |
| Ruler Tool | I | | Diagonal ruler |
| Note Tool | I | | Sticky note |
| Count Tool | I | | Crosshair with # |

### ─── Divider ───

### Section 4 — Retouching and painting tools

**Slot 8: Healing group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Spot Healing Brush** | J | ✦ | Band-aid |
| Remove Tool | J | | Brush with sparkle (AI) |
| Healing Brush | J | | Band-aid with crosshair |
| Patch Tool | J | | Fabric patch with dotted border |
| Content-Aware Move Tool | J | | Cross arrows with dotted selection |
| Red Eye Tool | J | | Eye with crosshair |

**Slot 9: Brush group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Brush Tool** | B | ✦ | Paintbrush |
| Pencil Tool | B | | Pencil |
| Color Replacement Tool | B | | Brush with swap arrows |
| Mixer Brush Tool | B | | Brush with paint drip |
| Adjustment Brush Tool | B | | Brush with adjustment icon (added 2025) |

**Slot 10: Clone Stamp group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Clone Stamp Tool** | S | ✦ | Rubber stamp |
| Pattern Stamp Tool | S | | Stamp with pattern |

**Slot 11: History Brush group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **History Brush Tool** | Y | ✦ | Brush with curved arrow |
| Art History Brush Tool | Y | | Brush with curly stroke |

**Slot 12: Eraser group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Eraser Tool** | E | ✦ | Eraser block |
| Background Eraser | E | | Eraser with scissors |
| Magic Eraser | E | | Eraser with sparkle |

**Slot 13: Gradient / Paint Bucket group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Gradient Tool** | G | ✦ | Rectangle with gradient fill |
| Paint Bucket Tool | G | | Tilted paint bucket |

**Slot 14: Blur / Sharpen / Smudge group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Blur Tool** | — | ✦ | Water droplet |
| Sharpen Tool | — | | Triangle/prism |
| Smudge Tool | — | | Pointing finger |

**Slot 15: Dodge / Burn / Sponge group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Dodge Tool** | O | ✦ | Curved hand (dodging) |
| Burn Tool | O | | Pinching fist |
| Sponge Tool | O | | Sponge |

### ─── Divider ───

### Section 5 — Drawing and type tools

**Slot 16: Pen group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Pen Tool** | P | ✦ | Fountain pen nib |
| Freeform Pen Tool | P | | Wavy pen nib |
| Curvature Pen Tool | P | | Pen with curve |
| Content-Aware Tracing Tool | P | | Pen with dotted path |
| Add Anchor Point Tool | — | | Pen nib with + |
| Delete Anchor Point Tool | — | | Pen nib with – |
| Convert Point Tool | — | | Angle/arrow head |

**Slot 17: Type group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Horizontal Type Tool** | T | ✦ | Letter "T" |
| Vertical Type Tool | T | | Vertical "T" |
| Horizontal Type Mask Tool | T | | Dotted "T" |
| Vertical Type Mask Tool | T | | Dotted vertical "T" |

**Slot 18: Path Selection group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Path Selection Tool** | A | ✦ | Black/filled arrow |
| Direct Selection Tool | A | | White/outline arrow |

**Slot 19: Shape tools group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Rectangle Tool** | U | ✦ | Filled rectangle |
| Ellipse Tool | U | | Filled ellipse |
| Triangle Tool | U | | Filled triangle |
| Polygon Tool | U | | Filled pentagon |
| Line Tool | U | | Diagonal line |
| Custom Shape Tool | U | | Custom blob |
| Star Tool | U | | Five-pointed star (added Aug 2025) |

### ─── Divider ───

### Section 6 — Navigation tools

**Slot 20: Hand / Rotate View group**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Hand Tool** | H | ✦ | Open hand |
| Rotate View Tool | R | | Hand with circular arrow |

**Slot 21: Zoom Tool (standalone)**
| Tool | Shortcut | Default | Icon |
|------|----------|---------|------|
| **Zoom Tool** | Z | ✦ | Magnifying glass |

### ─── Divider ───

### Section 7 — Bottom controls

These are not tools but persistent interface elements at the toolbar's base:

- **Edit Toolbar (…)** — three-dot button opening the toolbar customization dialog
- **Foreground/Background Color Swatches** — two overlapping squares (default black/white). Swap shortcut: **X**. Reset shortcut: **D**. Click either to open Color Picker.
- **Quick Mask Mode toggle** — shortcut **Q**, circle-in-rectangle icon
- **Screen Mode cycle** — shortcut **F**, cycles Standard → Full Screen with Menu → Full Screen
- **Generate Image button** (2025+) — Adobe Firefly AI text-to-image generation

**Total: ~71 individual tools across ~21 toolbar slots.**

---

## 2. Complete menu bar structure

All shortcuts listed as Windows / Mac. Separators noted where they divide menu groups. An ellipsis (…) indicates the item opens a dialog.

### File menu

| Item | Shortcut | Notes |
|------|----------|-------|
| New… | Ctrl+N / Cmd+N | |
| Open… | Ctrl+O / Cmd+O | |
| Browse in Bridge… | Alt+Ctrl+O / Opt+Cmd+O | |
| Open As… | Alt+Shift+Ctrl+O | Windows only |
| Open as Smart Object… | — | |
| **── separator ──** | | |
| Open Recent ► | | Submenu: list of recent files + Clear Recent File List |
| **── separator ──** | | |
| Close | Ctrl+W / Cmd+W | |
| Close All | Alt+Ctrl+W / Opt+Cmd+W | |
| Close Others | Alt+Ctrl+P / Opt+Cmd+P | |
| **── separator ──** | | |
| Save | Ctrl+S / Cmd+S | |
| Save As… | Shift+Ctrl+S / Shift+Cmd+S | |
| Save a Copy… | Alt+Ctrl+S / Opt+Cmd+S | |
| Revert | F12 | |
| **── separator ──** | | |
| Export ► | | Export As… (Alt+Shift+Ctrl+W), Save for Web (Legacy)… (Alt+Shift+Ctrl+S), Export Preferences…, Artboards to Files/PDF…, Layers to Files/PDF…, Color Lookup Tables…, Data Sets as Files…, Paths to Illustrator…, Render Video…, Zoomify… |
| Generate ► | | Image Assets |
| **── separator ──** | | |
| Place Embedded… | — | |
| Place Linked… | — | |
| Package… | — | |
| **── separator ──** | | |
| Automate ► | | Batch…, PDF Presentation…, Create Droplet…, Crop and Straighten Photos, Contact Sheet II…, Conditional Mode Change…, Fit Image…, Merge to HDR Pro…, Photomerge…, Lens Correction… |
| Scripts ► | | Image Processor…, Delete All Empty Layers, Flatten All Layer Effects, Flatten All Masks, Script Events Manager…, Load Files into Stack…, Load Multiple DICOM Files…, Statistics…, Browse… |
| **── separator ──** | | |
| Import ► | | Variable Data Sets…, Video Frames to Layers…, Notes… |
| **── separator ──** | | |
| File Info… | Alt+Shift+Ctrl+I / Opt+Shift+Cmd+I | |
| **── separator ──** | | |
| Print… | Ctrl+P / Cmd+P | |
| Print One Copy | Alt+Shift+Ctrl+P / Opt+Shift+Cmd+P | |
| **── separator ──** | | |
| Exit / Quit | Ctrl+Q / Cmd+Q | |

### Edit menu

| Item | Shortcut | Notes |
|------|----------|-------|
| Undo | Ctrl+Z / Cmd+Z | Multiple undo |
| Redo | Shift+Ctrl+Z / Shift+Cmd+Z | |
| Toggle Last State | — | |
| Fade… | Shift+Ctrl+F / Shift+Cmd+F | |
| **── separator ──** | | |
| Cut | Ctrl+X / Cmd+X | |
| Copy | Ctrl+C / Cmd+C | |
| Copy Merged | Shift+Ctrl+C / Shift+Cmd+C | |
| Paste | Ctrl+V / Cmd+V | |
| Paste Special ► | | Paste in Place (Shift+Ctrl+V), Paste Into (Alt+Shift+Ctrl+V), Paste Outside |
| Clear | Delete / Backspace | |
| **── separator ──** | | |
| Search… | Ctrl+F / Cmd+F | |
| **── separator ──** | | |
| Check Spelling… | — | |
| Find and Replace Text… | — | |
| **── separator ──** | | |
| Fill… | Shift+F5 | |
| Stroke… | — | |
| Content-Aware Fill… | — | |
| **── separator ──** | | |
| Content-Aware Scale | Alt+Shift+Ctrl+C | |
| Puppet Warp | — | |
| Perspective Warp | — | |
| Free Transform | Ctrl+T / Cmd+T | |
| Transform ► | | Again (Shift+Ctrl+T), Scale, Rotate, Skew, Distort, Perspective, Warp ── Rotate 180°, Rotate 90° CW, Rotate 90° CCW ── Flip Horizontal, Flip Vertical |
| Auto-Align Layers… | — | |
| Auto-Blend Layers… | — | |
| **── separator ──** | | |
| Sky Replacement… | — | |
| **── separator ──** | | |
| Define Brush Preset… | — | |
| Define Pattern… | — | |
| Define Custom Shape… | — | |
| **── separator ──** | | |
| Purge ► | | Undo, Clipboard, Histories, All, Video Cache |
| **── separator ──** | | |
| Adobe PDF Presets… | — | |
| Presets ► | | Preset Manager…, Migrate Presets, Export/Import Presets… |
| Remote Connections… | — | |
| **── separator ──** | | |
| Color Settings… | Shift+Ctrl+K / Shift+Cmd+K | |
| Assign Profile… | — | |
| Convert to Profile… | — | |
| **── separator ──** | | |
| Keyboard Shortcuts… | Alt+Shift+Ctrl+K | |
| Menus… | Alt+Shift+Ctrl+M | |
| Toolbar… | — | |
| **── separator ──** | | |
| Preferences ► | Ctrl+K (General) | General, Interface, Workspace, Tools, History Log, File Handling, Export, Performance, Scratch Disks, Cursors, Transparency & Gamut, Units & Rulers, Guides Grid & Slices, Plug-ins, Type, Technology Previews, Camera Raw |

### Image menu

| Item | Shortcut | Notes |
|------|----------|-------|
| Mode ► | | Bitmap, Grayscale, Duotone…, Indexed Color…, RGB Color, CMYK Color, Lab Color, Multichannel ── 8 Bits/Channel, 16 Bits/Channel, 32 Bits/Channel ── Color Table… |
| **── separator ──** | | |
| Adjustments ► | | *See full submenu below* |
| **── separator ──** | | |
| Auto Tone | Shift+Ctrl+L | |
| Auto Contrast | Alt+Shift+Ctrl+L | |
| Auto Color | Shift+Ctrl+B | |
| **── separator ──** | | |
| Image Size… | Alt+Ctrl+I / Opt+Cmd+I | |
| Canvas Size… | Alt+Ctrl+C / Opt+Cmd+C | |
| Image Rotation ► | | 180°, 90° CW, 90° CCW, Arbitrary… ── Flip Canvas Horizontal, Flip Canvas Vertical |
| **── separator ──** | | |
| Crop | — | |
| Trim… | — | |
| Reveal All | — | |
| **── separator ──** | | |
| Duplicate… | — | |
| **── separator ──** | | |
| Apply Image… | — | |
| Calculations… | — | |
| **── separator ──** | | |
| Variables ► | | Define…, Data Sets… |
| Apply Data Set… | — | |
| **── separator ──** | | |
| Trap… | — | |
| Analysis ► | | Set Measurement Scale ►, Select Data Points ►, Record Measurements, Ruler Tool, Count Tool, Place Scale Marker… |

**Image > Adjustments submenu (complete, 22 items):**

Brightness/Contrast… → Levels… (Ctrl+L) → Curves… (Ctrl+M) → Exposure… ── Vibrance… → Hue/Saturation… (Ctrl+U) → Color Balance… (Ctrl+B) → Black & White… (Alt+Shift+Ctrl+B) → Photo Filter… → Channel Mixer… → Color Lookup… ── Invert (Ctrl+I) → Posterize… → Threshold… → Gradient Map… → Selective Color… ── Shadows/Highlights… → HDR Toning… ── Desaturate (Shift+Ctrl+U) → Match Color… → Replace Color… → Equalize

### Layer menu

| Item | Shortcut | Notes |
|------|----------|-------|
| New ► | | Layer… (Shift+Ctrl+N), Layer from Background…, Group…, Group from Layers…, Artboard…, Artboard from Group/Layers…, Frame from Layers… ── Layer Via Copy (Ctrl+J), Layer Via Cut (Shift+Ctrl+J) |
| **── separator ──** | | |
| Copy CSS / Copy SVG | — | |
| **── separator ──** | | |
| Duplicate Layer… | — | |
| Delete ► | | Layer, Hidden Layers |
| Rename Layer… | — | |
| **── separator ──** | | |
| Layer Style ► | | Blending Options… ── Bevel & Emboss…, Stroke…, Inner Shadow…, Inner Glow…, Satin…, Color Overlay…, Gradient Overlay…, Pattern Overlay…, Outer Glow…, Drop Shadow… ── Copy/Paste/Clear Layer Style ── Global Light…, Create Layer, Hide All Effects, Scale Effects… |
| Smart Filter ► | | Disable Smart Filters, Delete Filter Mask, Disable Filter Mask, Clear Smart Filters |
| **── separator ──** | | |
| New Fill Layer ► | | Solid Color…, Gradient…, Pattern… |
| New Adjustment Layer ► | | All 16 adjustment types (same as Image > Adjustments, minus the destructive-only items) |
| Layer Content Options… | — | |
| Layer Mask ► | | Reveal All, Hide All, Reveal Selection, Hide Selection, From Transparency ── Delete, Apply ── Disable/Enable, Unlink/Link |
| Vector Mask ► | | Reveal All, Hide All, Current Path, Delete, Enable/Disable |
| Create Clipping Mask | Alt+Ctrl+G / Opt+Cmd+G | |
| **── separator ──** | | |
| Smart Objects ► | | Convert to Smart Object, New Smart Object via Copy ── Edit Contents, Relink to File…, Relink to Library…, Replace Contents… ── Export Contents… ── Embed Linked, Embed All Linked ── Update Modified Content, Update All ── Convert to Layers ── Stack Mode ► (12 statistical modes), Rasterize |
| Video Layers ► | | New Video Layer from File…, New Blank Video Layer, Insert/Duplicate/Delete Frame, Replace/Interpret Footage…, Show Altered Video, Restore Frame/All |
| Rasterize ► | | Type, Shape, Fill Content, Vector Mask, Smart Object, Video, Layer Style, Layer, All Layers |
| **── separator ──** | | |
| New Layer Based Slice | — | |
| **── separator ──** | | |
| Group Layers | Ctrl+G / Cmd+G | |
| Ungroup Layers | Shift+Ctrl+G | |
| Hide Layers | — | |
| **── separator ──** | | |
| Arrange ► | | Bring to Front (Shift+Ctrl+]), Bring Forward (Ctrl+]), Send Backward (Ctrl+[), Send to Back (Shift+Ctrl+[) ── Reverse |
| Combine Shapes ► | | Unite, Subtract Front Shape, Intersect, Exclude Overlapping |
| Align ► | | Top Edges, Vertical Centers, Bottom Edges ── Left Edges, Horizontal Centers, Right Edges |
| Distribute ► | | Top/Vertical Centers/Bottom Edges ── Left/Horizontal Centers/Right Edges ── Distribute Spacing Vertically/Horizontally |
| **── separator ──** | | |
| Lock Layers… / Lock All Layers in Group… | — | |
| Link Layers / Select Linked Layers | — | |
| **── separator ──** | | |
| Merge Layers | Ctrl+E | |
| Merge Visible | Shift+Ctrl+E | |
| Flatten Image | — | |
| **── separator ──** | | |
| Matting ► | | Defringe…, Remove Black Matte, Remove White Matte |

### Type menu

Panels ► (Character, Paragraph, Character Styles, Paragraph Styles, Glyphs) → Anti-Aliasing ► (None, Sharp, Crisp, Strong, Smooth) → Orientation ► (Horizontal, Vertical) → OpenType ► (Standard Ligatures, Contextual Alternates, Discretionary Ligatures, Swash, Old Style, Stylistic Alternates, Titling Alternates, Ornaments, Ordinals, Fractions) → Font Preview Size ► (None through Huge) → Language Options ► → Create Work Path → Convert to Shape → Rasterize Type Layer → Convert to Point/Paragraph Text → Warp Text… → Match Font… → Add Fonts from Adobe Fonts… → Update All Text Layers → Replace All Missing Fonts → Manage Missing Fonts → Paste Lorem Ipsum

### Select menu

| Item | Shortcut |
|------|----------|
| All | Ctrl+A |
| Deselect | Ctrl+D |
| Reselect | Ctrl+Shift+D |
| Inverse | Ctrl+Shift+I |
| **── separator ──** | |
| All Layers | Ctrl+Alt+A |
| Deselect Layers | — |
| Find Layers | — |
| Isolate Layers | — |
| **── separator ──** | |
| Color Range… | — |
| Focus Area… | — |
| Subject | — (AI-based) |
| Sky | — (AI-based) |
| Select and Mask… | Ctrl+Alt+R |
| **── separator ──** | |
| Modify ► | Border…, Smooth…, Expand…, Contract…, Feather… (Shift+F6) |
| Grow | — |
| Similar | — |
| Transform Selection | — |
| **── separator ──** | |
| Edit in Quick Mask Mode | Q |
| **── separator ──** | |
| Load Selection… / Save Selection… | — |

### Filter menu

| Item | Shortcut |
|------|----------|
| Last Filter | Ctrl+F |
| Convert for Smart Filters | — |
| Neural Filters… | — (AI-powered: Skin Smoothing, Style Transfer, Colorize, Super Zoom, JPEG Artifacts Removal, Depth Blur, Landscape Mixer, Color Transfer, Harmonization, Photo Restoration) |
| **── separator ──** | |
| Filter Gallery… | — |
| **── separator ──** | |
| Adaptive Wide Angle… | — |
| Camera Raw Filter… | Ctrl+Shift+A |
| Lens Correction… | — |
| Liquify… | Ctrl+Shift+X |
| Vanishing Point… | Ctrl+Alt+V |

**Filter submenus:**

- **Blur ►**: Average, Blur, Blur More, Box Blur…, Gaussian Blur…, Lens Blur…, Motion Blur…, Radial Blur…, Shape Blur…, Smart Blur…, Surface Blur… ── *Blur Gallery:* Field Blur…, Iris Blur…, Tilt-Shift…, Path Blur…, Spin Blur…
- **Distort ►**: Displace…, Pinch…, Polar Coordinates…, Ripple…, Shear…, Spherize…, Twirl…, Wave…, ZigZag…
- **Noise ►**: Add Noise…, Despeckle, Dust & Scratches…, Median…, Reduce Noise…
- **Pixelate ►**: Color Halftone…, Crystallize…, Facet, Fragment, Mezzotint…, Mosaic…, Pointillize…
- **Render ►**: Clouds, Difference Clouds, Fibers…, Flame…, Lens Flare…, Lighting Effects…, Picture Frame…, Tree…
- **Sharpen ►**: Sharpen, Sharpen Edges, Sharpen More, Smart Sharpen…, Unsharp Mask…
- **Stylize ►**: Diffuse…, Emboss…, Extrude…, Find Edges, Oil Paint…, Solarize, Tiles…, Trace Contour…, Wind…
- **Video ►**: De-Interlace…, NTSC Colors
- **Other ►**: Custom…, High Pass…, Maximum…, Minimum…, Offset…

**Filter Gallery categories** (accessible through the gallery dialog or as top-level submenus when the preference "Show All Filter Gallery Groups and Names" is enabled): Artistic (15 filters), Brush Strokes (8), Distort/Gallery (3: Diffuse Glow, Glass, Ocean Ripple), Sketch (14), Stylize/Gallery (1: Glowing Edges), Texture (6).

### View menu

Proof Setup ► (Working CMYK, Cyan/Magenta/Yellow/Black Plates, Working CMY, sRGB, Monitor RGB, Color Blindness types, Custom…) → Proof Colors (Ctrl+Y) → Gamut Warning (Ctrl+Shift+Y) ── Pixel Aspect Ratio ► → Pixel Aspect Ratio Correction → 32-bit Preview Options… ── Zoom In (Ctrl++) → Zoom Out (Ctrl+–) → Fit on Screen (Ctrl+0) → 100% (Ctrl+1) → 200% → Print Size ── Screen Mode ► ── Extras (Ctrl+H) → Show ► (Layer Edges, Selection Edges, Target Path, Grid (Ctrl+'), Guides (Ctrl+;), Count, Smart Guides, Slices, Notes, Pixel Grid, Brush Preview, Mesh, Edit Pins, All, None, Show Extras Options…) ── Rulers (Ctrl+R) ── Snap (Ctrl+Shift+;) → Snap To ► (Guides, Grid, Layers, Slices, Document Bounds, All, None) ── Lock Guides (Ctrl+Alt+;) → Clear Guides → New Guide… → New Guide Layout… ── Lock Slices → Clear Slices

### Plugins menu

Plugins Panel → Browse Plugins… → Manage Plugins… ── (installed third-party plugins listed below separator)

### Window menu

Arrange ► (Tile All Vertically/Horizontally, 2-Up through 6-Up layouts, Consolidate All to Tabs, Cascade, Tile, Float in Window, Float All, Match Zoom/Location/Rotation/All, New Window) → Workspace ► (Essentials, Photography, Painting, Graphic and Web, Motion ── New/Delete Workspace…, Keyboard Shortcuts & Menus…, Lock Workspace, Reset) → Extensions ►

**Panel toggles (all listed in the Window menu):**
Actions (Alt+F9), Adjustments, Brush Settings (F5), Brushes, Channels, Character, Character Styles, Clone Source, Color (F6), Contextual Task Bar, Discover, Glyphs, Gradients, Histogram, History, Info (F8), Layer Comps, Layers (F7), Libraries, Measurement Log, Navigator, Notes, Options, Paragraph, Paragraph Styles, Paths, Patterns, Properties, Shapes, Styles, Swatches, Timeline, Tool Presets, Tools

### Help menu

Photoshop Help… (F1) → Hands-on Tutorials → What's New ── Home Screen ── System Info… → System Compatibility Report… ── Manage My Account… → Sign Out ── Updates… ── About Photoshop → About Plug-In ► → Legal Notices…

---

## 3. Tool options bar: context-sensitive controls per tool

The Options Bar is a horizontal strip immediately below the menu bar. Its far-left always shows a **Tool Preset Picker** (dropdown arrow beside the active tool icon). Right-click this for Reset Tool / Reset All Tools. The rest changes per tool.

### Move Tool (V)
Auto-Select checkbox + Layer/Group dropdown → Show Transform Controls checkbox → **6 Align buttons** (Top Edges, Vertical Centers, Bottom Edges, Left Edges, Horizontal Centers, Right Edges) → **6 Distribute buttons** (same directions, enabled with 3+ layers). When transform handles are engaged, the bar switches to numeric fields: X, Y, W%, H%, Rotation°, Skew, plus a Maintain Aspect Ratio link.

### Marquee Tools (M)
**4 selection mode buttons** (New, Add, Subtract, Intersect) → Feather field (0–1000 px) → Anti-alias checkbox (Elliptical only) → Style dropdown (Normal, Fixed Ratio, Fixed Size) → Width/Height fields → Select and Mask… button.

### Lasso Tools (L)
Selection mode buttons → Feather → Anti-alias → Select and Mask… button. **Magnetic Lasso** adds: Width (1–256 px), Contrast (1–100%), Frequency (0–100), Pen Pressure checkbox.

### Object Selection Tool (W)
Selection mode buttons → Mode dropdown (Rectangle / Lasso) → Sample All Layers checkbox → **Object Finder checkbox** (highlights detected objects on hover) → Select and Mask… button.

### Quick Selection Tool (W)
Selection mode buttons (3: New, Add, Subtract) → Brush size picker → Sample All Layers → Auto-Enhance → Select and Mask… button.

### Magic Wand Tool (W)
Selection mode buttons → Sample Size dropdown → **Tolerance field (0–255)** → Anti-alias → Contiguous checkbox → Sample All Layers → Select and Mask… button.

### Crop Tool (C)
Aspect Ratio dropdown (Ratio, W×H×Resolution, Unconstrained, 1:1, 4:5, 5:7, 16:9, etc.) → W/H/Resolution fields → Swap (↔) button → Clear → Straighten button → Overlay dropdown (Rule of Thirds, Grid, Golden Ratio, Golden Spiral, etc.) → Gear menu (Classic Mode, Show Cropped Area, Crop Shield) → **Delete Cropped Pixels checkbox** → Fill dropdown (Background, Generative Expand, Content-Aware) → Cancel/Commit buttons.

### Eyedropper Tool (I)
Sample Size dropdown (Point Sample, 3×3 through 101×101 Average) → Sample dropdown (Current Layer, Current & Below, All Layers, with/without Adjustments) → Show Sampling Ring checkbox.

### Brush Tool (B)
Brush Preset picker (Size slider, Hardness slider, brush tip thumbnails) → Toggle Brush Settings Panel button → **Mode dropdown (27 blend modes)** → **Opacity slider (0–100%)** → Pressure for Opacity toggle → **Flow slider (0–100%)** → Airbrush toggle → **Smoothing slider (0–100%)** → Brush Angle scrubby slider → Pressure for Size toggle.

### Pencil Tool (B)
Same as Brush minus Flow, Airbrush, and Smoothing. Adds **Auto Erase checkbox** (paints background color over foreground color areas).

### Clone Stamp Tool (S)
Brush Preset picker → Mode dropdown → Opacity → Pressure for Opacity → Flow → Airbrush → **Aligned checkbox** → **Sample dropdown** (Current Layer, Current & Below, All Layers) → Ignore Adjustment Layers toggle → Pressure for Size toggle.

### Eraser Tool (E)
Brush picker → **Mode dropdown (Brush, Pencil, Block)** → Opacity → Flow (Brush mode only) → Airbrush (Brush mode only) → **Erase to History checkbox** → Pressure toggles.

### Spot Healing Brush (J)
Brush picker → Mode dropdown → **Type radio buttons (Content-Aware, Create Texture, Proximity Match)** → Sample All Layers → Diffusion slider.

### Gradient Tool (G)
Gradient preset picker → **5 gradient type buttons** (Linear, Radial, Angle, Reflected, Diamond) → Reverse checkbox → Dither checkbox → Method dropdown (Perceptual, Linear, Classic). **Classic mode** adds: Mode dropdown, Opacity, Transparency checkbox.

### Paint Bucket Tool (G)
Fill source dropdown (Foreground, Pattern) → Pattern picker → Mode → Opacity → Tolerance → Anti-alias → Contiguous → All Layers.

### Pen Tool (P)
Drawing mode dropdown (**Shape, Path, Pixels**) → When Shape: Fill color, Stroke color, Stroke width, Stroke Options (alignment, caps, corners, dashes) → Path Operations dropdown → Path Alignment → Gear menu (Rubber Band toggle) → Auto Add/Delete checkbox → Make Selection button → Mask button.

### Type Tool (T)
Text Orientation toggle → **Font Family dropdown** (searchable, filterable) → **Font Style** → **Font Size** (scrubby slider on tT icon) → Anti-aliasing dropdown (None, Sharp, Crisp, Strong, Smooth) → **3 Alignment buttons** → Color swatch → Warp Text button → Toggle Character/Paragraph panels button.

### Shape Tools (U)
Tool Mode (Shape/Path/Pixels) → Fill color/type → Stroke color/type → Stroke width → Stroke Options → W/H fields → Link aspect ratio → Path Operations → Path Alignment/Arrangement → Gear menu → Align Edges checkbox. **Rectangle** adds corner radius fields (4 corners, linkable). **Polygon** adds Sides field + Star options. **Line** adds Weight field.

### Hand Tool (H)
Scroll All Windows checkbox → 100% button → Fit Screen button → Fill Screen button.

### Zoom Tool (Z)
Zoom In/Out radio buttons → Resize Windows to Fit checkbox → Zoom All Windows checkbox → **Scrubby Zoom checkbox** → 100% / Fit Screen / Fill Screen buttons.

### Controls shared across many tools

**Blend Mode dropdown** appears in: Brush, Pencil, Clone Stamp, Pattern Stamp, History Brush, Art History Brush, Eraser, Gradient (Classic), Paint Bucket, Spot Healing Brush, Healing Brush, Blur, Sharpen, Smudge. **Opacity** appears in all painting/retouching tools plus Gradient and Paint Bucket. **Flow** appears in Brush, Clone Stamp, Pattern Stamp, History Brush, Eraser (Brush mode). **Sample dropdown** (Current Layer / All Layers) appears in Clone Stamp, Healing Brush, Spot Healing, Eyedropper, Blur, Sharpen, Smudge. **Selection mode buttons** (New/Add/Subtract/Intersect) appear in all selection tools.

---

## 4. Panels system: internal structure of every panel

### Layers panel — the most complex panel

**Row 1 – Filter bar**: Filter type dropdown (Kind, Name, Effect, Mode, Attribute, Color, Smart Object, Selected, Artboard, Isolated) + text search field + toggle switch (lightswitch icon) to enable/disable filtering.

**Row 2 – Blend Mode and Opacity**: Blend mode dropdown on left (**27 modes** organized in 6 groups separated by dividers: Normal/Dissolve — Darken group — Lighten group — Overlay/Contrast group — Difference group — HSL group). Opacity slider+field on right (0–100%).

**Row 3 – Lock options** (5 icon buttons left to right): Lock Transparent Pixels (checkerboard) → Lock Image Pixels (paintbrush) → Lock Position (four-way arrow) → Lock Artboard/Frame (nested rectangles) → Lock All (padlock). **Fill** opacity field to the right (0–100%, affects only pixel content, not layer styles).

**Layer list area** (scrollable, bottom-to-top stacking order): Each layer row displays: visibility eye icon → layer thumbnail → link chain icon (if mask linked) → mask thumbnail (if exists) → layer name → smart object badge (small icon on thumbnail corner) → effects/styles indicator ("fx" with disclosure triangle). Layer types distinguished by icons: normal pixel layer, **Background** (padlock), **Text** ("T" on thumbnail), **Shape** (vector path), **Smart Object** (document icon on corner), **Adjustment** (half-circle icons per type), **Fill** (solid/gradient/pattern), **Group** (folder icon, expandable), **Artboard**.

**Bottom button row** (7 buttons, left to right): Link Layers (chain) → Add Layer Style (fx) → Add Layer Mask (rectangle-with-circle) → Create New Fill or Adjustment Layer (half-circle) → Create New Group (folder) → Create New Layer (+) → Delete Layer (trash can).

### Properties panel — context-sensitive

Changes completely based on selection. **Pixel layer selected**: transform fields (X, Y, W, H, Rotation), document properties, Quick Actions (Remove Background, Select Subject). **Adjustment layer selected**: full interactive adjustment controls (e.g., Curves graph, Levels histogram), presets dropdown, clip-to-layer button, visibility eye, reset and delete buttons. **Mask selected**: **Density slider (0–100%)**, **Feather slider (0–1000 px)**, Select and Mask button, Color Range button, Invert button, bottom icons (Load Selection, Apply Mask, Disable, Delete). **Type layer selected**: complete Character + Paragraph formatting. **Shape layer selected**: Fill/Stroke controls, corner radius, dimensions, path operations.

### Channels panel

**Channel list**: Composite channel at top (RGB/CMYK/Lab) followed by individual color channels (Red, Green, Blue for RGB — each with keyboard shortcut Ctrl+3/4/5), then Alpha channels and Spot channels below. Each row: eye icon + thumbnail + channel name. **Bottom buttons** (4): Load Channel as Selection (dotted circle) → Save Selection as Channel → Create New Channel → Delete Channel. **Maximum 56 channels** per image.

### Paths panel

**Path list**: Work Path (temporary, italicized), saved named paths, shape layer vector masks. Each row: thumbnail + path name. **Bottom buttons** (6): Fill Path with Foreground Color → Stroke Path with Brush → Load Path as Selection → Make Work Path from Selection → Create New Path → Delete Path.

### History panel

**Snapshot area** at top (separated): initial document state snapshot by default. **History states list** below (chronological, newest at bottom): each shows tool/action icon + descriptive name. Click any state to revert. **History Brush source column** on left (click to set source for History Brush). Default **50 states** (configurable 1–1000). **Bottom buttons** (3): Create New Document from Current State → Create New Snapshot (camera) → Delete (trash).

### Color panel

Foreground/Background swatches (overlapping squares, left) → Color sliders with gradient-filled tracks (right) → Color spectrum/ramp bar (bottom). **Slider modes** (via panel menu): HSB, RGB (default), Lab, CMYK, Web Color, Grayscale. **Spectrum options**: Hue Cube, Brightness Cube, Color Wheel, RGB/CMYK Spectrum, Grayscale Ramp, Current Colors. Alert indicators: CMYK gamut warning triangle, web-safe warning square.

### Swatches panel

Grid of clickable color squares organized in collapsible folders/groups. Click = set foreground, Ctrl+click = set background. Bottom buttons: Create New Swatch, Create New Group, Delete.

### Brush Settings panel (F5) — the most complex settings panel

**Left column**: category names with checkboxes to enable/disable + lock icons to preserve settings. **Right area**: detailed controls for selected category. **Bottom**: live stroke preview.

Categories: **Brush Tip Shape** (always visible — tip picker, Size 1–5000 px, Flip X/Y, Angle 0–360°, Roundness 0–100%, Hardness 0–100% for round brushes, Spacing 1–1000%) → **Shape Dynamics** (Size/Angle/Roundness Jitter with Control options: Off, Fade, Pen Pressure, Pen Tilt, Stylus Wheel, Direction) → **Scattering** (Scatter 0–1000%, Both Axes, Count 1–16, Count Jitter) → **Texture** (Pattern picker, Scale, Mode, Depth with jitter) → **Dual Brush** (second tip, Size, Spacing, Scatter, Count) → **Color Dynamics** (FG/BG Jitter, Hue/Saturation/Brightness Jitter, Purity) → **Transfer** (Opacity/Flow Jitter with Control) → **Brush Pose** (Tilt X/Y, Rotation, Pressure overrides). **Simple toggles** (checkbox only): Noise, Wet Edges, Build-up (Airbrush), Smoothing, Protect Texture.

### Character panel

**Row 1**: Font Family + Font Style dropdowns. **Row 2**: Font Size + Leading. **Row 3**: Kerning (Metrics/Optical/numeric) + Tracking. **Row 4**: Vertical Scale + Horizontal Scale. **Row 5**: Baseline Shift + Color swatch. **Row 6**: 8 style toggle buttons (Faux Bold, Faux Italic, All Caps, Small Caps, Superscript, Subscript, Underline, Strikethrough). **Row 7**: OpenType feature toggles. **Row 8**: Language dropdown + Anti-aliasing method.

### Paragraph panel

**Row 1**: 7 alignment buttons (Left, Center, Right, Justify Last Left/Center/Right, Justify All). **Row 2**: Indent Left/Right/First Line. **Row 3**: Space Before/After. **Row 4**: Hyphenate checkbox.

### Info panel

**Upper-left quadrant**: First color readout (configurable: Actual Color, RGB, HSB, CMYK, Lab, Web). **Upper-right**: Second color readout. **Lower-left**: Cursor X, Y coordinates. **Lower-right**: Selection W, H or document dimensions. During adjustments, shows before/after color values.

### Navigator panel

Thumbnail preview of entire document with **red viewport rectangle** overlaid (drag to pan). Zoom percentage field at lower-left. Zoom slider at bottom with zoom out (small mountains) and zoom in (large mountains) buttons at endpoints.

### Actions panel

**Action Sets** (folders) → **Actions** (expandable) → **Steps** (individual commands with tool icons). Left columns: checkbox (include/exclude from playback) + modal dialog icon. **Bottom buttons** (6): Stop → Record (red circle) → Play (triangle) → Create New Set → Create New Action → Delete. **Button Mode** toggleable via panel menu for one-click execution.

### Histogram panel

Three view modes: Compact (graph only), Expanded (graph + channel dropdown + statistics), All Channels (separate channel histograms). Channel dropdown: Composite, individual channels, Luminosity, Colors. Source dropdown: Entire Image, Selected Layer, Adjustment Composite. **Statistics**: Mean, Std Dev, Median, Pixels, Level, Count, Percentile, Cache Level.

### Adjustments panel

**4×4 grid of icons**, each creating an adjustment layer on click. Row 1 (Tonal): Brightness/Contrast, Levels, Curves, Exposure. Row 2 (Color): Vibrance, Hue/Saturation, Color Balance, Black & White. Row 3 (Advanced): Photo Filter, Channel Mixer, Color Lookup, Invert. Row 4 (Special): Posterize, Threshold, Gradient Map, Selective Color.

### Other panels (compact descriptions)

**Brushes panel**: Brush preset grid/list in collapsible folders, search field, size preview, create/delete buttons. **Gradients panel**: Gradient preset grid in folders. **Patterns panel**: Pattern preset grid in folders. **Styles panel**: Layer style preset thumbnails. **Glyphs panel**: Font selector, glyph grid, category filter, recently used row. **Timeline panel**: Video mode (horizontal tracks, playback controls, keyframes, trim bars) or Frame Animation mode (frame thumbnails, delay, looping). **Libraries panel**: Creative Cloud Libraries with synced assets (colors, styles, graphics). **Layer Comps panel**: Saved layer states for comparison. **Clone Source panel**: Up to 5 source references with offset/scale/rotation.

---

## 5. Workspace layout and docking system

### Default Essentials workspace

The interface uses a **top-to-bottom, left-to-right hierarchy**: Menu Bar (topmost) → Options Bar (below menu) → Toolbar (left edge, single column) → Canvas (center) → Panels (right edge) → Status Bar (bottom of canvas).

**Right-side panel arrangement in Essentials:**

| Position | Panel group | Display |
|----------|------------|---------|
| Narrow left column | History, Learn | **Collapsed to icons** (iconic view) |
| Main column, top | Color + Swatches (tabbed) | Expanded |
| Main column, middle | Properties + Adjustments (tabbed) | Expanded |
| Main column, bottom | **Layers + Channels + Paths** (tabbed) | Expanded |
| Far right column | Libraries | Expanded |

### Workspace presets and their differences

**Photography**: Histogram + Navigator replace Color/Swatches at top. History, Actions, Info, Clone Source, Properties in the narrow column (expanded to ~5 iconic panels). **Painting**: Swatches panel prominent, Brush Presets panel replaces Libraries/Adjustments, Tool Presets in iconic column. **Graphic and Web**: Character, Paragraph, Glyphs panels prominent for typography work. **Motion**: Timeline panel visible at bottom, video-relevant panels prioritized.

### Docking mechanics for Python implementation

**Panel docking** uses drop-zone detection. A **blue highlight line** (horizontal) indicates stacking position; a **blue highlight box** indicates tabbed grouping. Panels dock to left, right, or bottom edges. **Tab grouping**: drag a panel tab over another panel's tab area to create tabbed group. **Vertical stacking**: drag to bottom edge of a panel group. **Icon collapse**: double-arrow button (« ») at top of dock toggles expanded ↔ icons-only. Column width determines if icons show labels. **Auto-Collapse Iconic Panels** preference controls whether expanded icon panels collapse on outside click. Hold **Ctrl** while dragging to force floating (prevent docking). Panel minimum sizes enforced.

---

## 6. Status bar at the canvas bottom

**Location**: bottom-left of each document window, visible in Standard Screen Mode only.

**Zoom percentage field** (far left): editable — type a value and press Enter to jump to that zoom level. **Document information area** (right of zoom): displays one selectable info type via dropdown arrow.

| Status bar option | What it displays |
|-------------------|-----------------|
| **Document Sizes** | Flattened size / full layered size |
| **Document Profile** | Color profile name (default display) |
| **Document Dimensions** | Width × Height in current ruler units |
| **GPU Mode** | Active GPU rendering mode |
| **Measurement Scale** | Custom measurement scale if set |
| **Scratch Sizes** | Current RAM used / total RAM available |
| **Efficiency** | % time in RAM vs. scratch disk (100% = optimal) |
| **Timing** | Duration of last operation |
| **Current Tool** | Name of active tool |
| **32-bit Exposure** | HDR preview exposure slider (32-bit images only) |

**Click-and-hold** on the info area shows a popup with document width, height, channels, and resolution.

---

## 7. Canvas area: rulers, guides, grid, snap, zoom, and navigation

### Rulers
Toggle: **Ctrl+R**. Appear along top and left edges. Units: Pixels, Inches, Centimeters, Millimeters, Points, Picas, Percent. Right-click ruler to switch units. Drag from ruler onto canvas to create guides. Zero origin at upper-left; drag from ruler intersection to reposition, double-click to reset.

### Guides
**Default color: cyan**. Created by dragging from rulers, via View > New Guide (single) or New Guide Layout (grid of columns/rows/gutters/margins). Alt+drag from vertical ruler creates horizontal guide (toggles orientation). Style: Lines or Dashed Lines (configurable in Preferences > Guides, Grid & Slices). **Smart Guides**: magenta/purple, appear automatically during move/resize/transform showing alignment and spacing relative to other layers, canvas center, and canvas edges. Toggle: View > Show > Smart Guides. Lock guides: **Ctrl+Alt+;**. Clear all: View > Clear Guides.

### Grid
Toggle: **Ctrl+'**. Non-printing overlay. Configurable: gridline spacing (any unit), subdivisions count, color, style (Lines, Dashed Lines, Dots). **Pixel Grid** appears automatically above **500% zoom**, showing individual pixel boundaries (toggleable via View > Show > Pixel Grid).

### Snap behavior
Master toggle: **Ctrl+Shift+;**. Snap targets (View > Snap To): Guides, Grid, Layers, Slices, Document Bounds, All, None. Built-in **~8 pixel tolerance** at current zoom, not user-adjustable. Hold Ctrl while dragging to temporarily override. Separate preference "Snap Vector Tools and Transforms to Pixel Grid" for crisp vector edges.

### Zoom controls
**Ctrl++/–** for zoom in/out (jumps preset levels: 25%, 33.3%, 50%, 66.7%, 100%, 200%, etc.). **Ctrl+0** = Fit on Screen. **Ctrl+1** = 100%. **Alt+scroll wheel** = zoom in/out. **Scrubby Zoom**: click-drag right to zoom in, left to zoom out (with Zoom tool, toggleable in options bar). Click-drag rectangle to zoom to area (when Scrubby Zoom off). Maximum: **12,800%**. Minimum: ~0.5%.

### Hand tool navigation
**Spacebar** = temporary Hand tool from any tool. Click-drag to pan. **Flick Panning**: release quickly for inertial glide (toggleable preference). Scroll wheel = vertical pan. Ctrl+scroll = horizontal pan. "Scroll All Windows" option for multi-document pan.

### Bird's-eye view
While zoomed in, **hold H + click**: instantly zooms out to full view with a viewport rectangle. Drag the rectangle to target area, release mouse to zoom back in at new position. Extremely useful for large-image navigation.

### Canvas rotation (Rotate View tool, R key)
Non-destructive view rotation only. Click-drag to rotate freely. Compass overlay shows angle with red north indicator. Options bar: Rotation Angle field, Reset View button, Rotate All Windows checkbox. Requires GPU acceleration. Reset: click Reset View or press Esc.

### Panel visibility shortcuts
**Tab** = hide/show all panels, toolbar, and options bar. **Shift+Tab** = hide/show only right-side panels (toolbar stays). Moving cursor to screen edge temporarily reveals hidden panels.

### Screen modes (F key cycles)
**Standard**: full chrome with menu bar, tabs, scroll bars, OS taskbar. **Full Screen with Menu Bar**: centered image on dark gray, no scroll bars or tabs. **Full Screen**: black background, no UI visible (press Tab to show toolbar/panels, Esc to exit).

### Pasteboard and document tabs
The area outside canvas bounds is the **pasteboard** — default dark gray, customizable by right-clicking (Black, Dark Gray, Medium Gray, Light Gray, Custom). Drop shadow border around canvas toggleable in Preferences > Interface. **Document tab bar** sits below the Options Bar, showing one tab per open document (filename, zoom%, color mode, asterisk for unsaved changes). Ctrl+Tab cycles documents forward, Ctrl+Shift+Tab backward. Drag a tab out to float; drag back to re-dock. View > Arrange offers Tile, Cascade, 2-up through 6-up multi-document layouts.

---

## Implementation notes for a Python desktop clone

Building this in Python requires a framework supporting dockable panels, tabbed interfaces, and custom widgets. **PyQt6/PySide6 with QDockWidget** provides the closest native analog to Photoshop's panel docking system. Key architectural decisions for implementation:

- **Toolbar**: Implement as a vertical `QToolBar` with `QToolButton` widgets. Use `QMenu` on each button for grouped/nested tools (triggered by click-and-hold via `setPopupMode(QToolButton.DelayedPopup)`). Store tool groups as data structures mapping slot positions to ordered tool lists.
- **Options Bar**: Implement as a horizontal `QToolBar` that clears and repopulates its widgets whenever the active tool changes. Use a registry pattern mapping each tool ID to a factory function that returns the appropriate widget set.
- **Menu Bar**: Use `QMenuBar` with `QMenu` and `QAction` objects. The complete hierarchy documented above can be serialized as JSON/YAML and loaded dynamically.
- **Panels**: Each panel is a `QDockWidget` containing a custom `QWidget`. The Layers panel is the most complex, requiring a custom `QAbstractItemModel` with a `QTreeView` for the layer stack, plus custom delegate painting for thumbnails, visibility eyes, and lock icons.
- **Canvas**: Use a `QGraphicsView`/`QGraphicsScene` pair for zoom, pan, and rotation. Implement rulers as custom `QWidget` strips. Guides and grid as overlay items in the graphics scene.
- **Workspace presets**: Serialize panel positions, groupings, and visibility states using `QSettings` or `QMainWindow.saveState()`/`restoreState()`.

The **~71 tools, ~35 panels, and ~11 menus** with their complete hierarchies documented above provide the full structural blueprint needed to recreate Photoshop's interface at parity with the original.