# ALIS DEJA VU

Professional Portrait, Beauty & Fashion Photo Editing Studio

Current release: v0.8.0 — Master Prompt Phases 1–8.

## Vision

ALIS DEJA VU is a Python/PySide6 Windows desktop retouching studio for portrait, beauty, fashion and editorial photography. It is offline-first, deterministic and deliberately non-AI for version 1.

No account, paid API, cloud service, activation server or mandatory internet connection is required.

## Implemented phases

### Phase 1 — Foundation
- Python + PySide6 desktop workspace
- Windows Python Launcher workflow
- JPEG/JPG, PNG and TIFF
- Optional RAW loading through rawpy
- Dark professional UI
- Zoom, pan, fit and actual-size viewing
- Unicode/Arabic-path aware file handling

### Phase 2 — Basic Editing
- Exposure, brightness, contrast
- Highlights and shadows
- Temperature and tint
- Saturation and vibrance
- Histogram statistics
- Before/after comparison
- Undo/redo foundation

### Phase 3 — Layers, Masks & Brush
- Create, duplicate, delete and reorder layers
- Opacity and blend modes
- Normal, Multiply, Screen, Overlay, Soft Light, Add and Linear Light
- Grayscale masks
- Mask painting, erasing and inversion
- Soft brush falloff
- Layer-state history

### Phase 4 — Retouching
- Spot Healing
- Clone Stamp with Alt-click source selection
- Dodge
- Burn
- Dedicated retouch layers and masks
- Visible-composite sampling

### Phase 5 — Frequency, Skin & Color
- Frequency Separation with Low Frequency and High Frequency layers
- Natural skin smoothing
- Deterministic skin-tone balancing
- RGB/master curves
- HSL
- Vibrance
- Color Balance
- Selective Color
- Split Toning
- 3D LUT .cube loading
- Sharpening
- Noise reduction
- Film grain

The skin workflow is classical and mask-based. There is no AI skin segmentation, face recognition or generative editing.

### Phase 6 — Presets, Projects & Export
- Original starter presets
- User presets stored locally
- Versioned .alis project format
- Layer/mask/opacity/blend/visibility persistence
- Original-image reference preservation
- JPEG/PNG/TIFF export
- JPEG quality control
- Export resizing service

### Phase 7 — RAW, Performance & Polish
- Expanded RAW format detection
- rawpy camera/auto white-balance options
- Preview cache
- Configurable worker-thread budget
- Persistent settings
- Drag-and-drop image opening
- Before/after toggle
- Professional menus and dark workspace
- Developer logging

Qt documents QThreadPool and QRunnable as the mechanism for background work; the application keeps that architecture available for expensive processing without putting image algorithms into Qt widgets.
https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThreadPool.html

### Phase 8 — Testing, Packaging & Documentation
- Behavior tests for image-processing and project workflows
- Windows GitHub Actions test workflow
- PyInstaller Windows build script
- Packaged application resource/icon
- Architecture documentation
- Feature research documentation
- Third-party license documentation
- Phase status documentation

PyInstaller documents one-file Windows builds and resource collection; the build script follows those mechanisms.
https://pyinstaller.org/en/stable/usage.html

## Requirements

- Windows 10/11
- Python 3.9+
- Windows Python Launcher: py
- Dependencies from requirements.txt

Install:
py -m pip install -r requirements.txt

Run:
py -m app.main

or double-click run.bat.

Build:
build_exe.bat

## Project structure

app/core — image state, layers, masks and undo/redo
app/image — loading, saving and formats
app/processing — adjustments, retouch and detail
app/color — curves, HSL, color balance, selective color and LUTs
app/retouch — frequency separation and skin workflows
app/presets — built-in and user presets
app/project — versioned project serialization
app/export — export and resize
app/performance — preview cache
app/utils — settings and logging
app/ui — Qt workspace and canvas
resources — application artwork/icon
tests — behavior tests
docs — engineering and research documentation

## Shortcuts

Ctrl+O — Open image
Ctrl+S — Save project
Ctrl+Shift+S — Export
Ctrl+Z — Undo
Ctrl+Y — Redo
Tab — Before/original
Mouse wheel — Zoom
Middle mouse — Pan
Alt+click — Clone source
Drag image onto canvas — Open

## Project format

An .alis project is a ZIP-based, versioned container containing a UTF-8 JSON manifest, float32 NumPy layer arrays, optional float32 masks, adjustment state and the original-image reference.

The original photo is never overwritten by project editing.

## Validation

Run:
py -m unittest discover -s tests -v

The repository contains a Windows CI workflow for the same command. The current development environment is not Windows, so a Windows runtime/build pass is not claimed unless it is observed through CI or on a Windows machine.

## Privacy and cost

Offline-first.
No login.
No cloud processing.
No paid API.
No mandatory internet.
No AI models in version 1.

ALIS DEJA VU — Dark. Elegant. Professional. Offline.
