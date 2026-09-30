# ALIS DEJA VU

Professional Portrait & Fashion Photo Editing Studio

Current release: v0.4.0 — Phase 1 through Phase 4.

## Phase 1 — Foundation
- PySide6 desktop workspace
- Windows launcher using the Python Launcher (py)
- JPEG/JPG, PNG and TIFF loading/export
- RAW loading when rawpy is installed
- Dark professional workspace
- Zoom, pan, fit-to-window and actual-size canvas

## Phase 2 — Basic Editing
- Exposure, Brightness, Contrast, Saturation and Temperature
- Live image statistics / histogram summary
- Reset workflow and undo/redo foundation

## Phase 3 — Layers, Masks & Brush
- Add, duplicate, delete and reorder layers
- Layer opacity and Normal, Multiply, Screen, Overlay, Soft Light and Add blend modes
- Grayscale transparency masks
- Mask painting, erasing and inversion
- Soft brush falloff with size and opacity controls
- Layer-stack undo/redo

## Phase 4 — Portrait Retouching
- Spot Healing
- Clone Stamp with Alt-click source selection
- Dodge and Burn
- Dedicated retouch layers and masks
- Visible-composite sampling

The Phase 3/4 implementation is classical and deterministic. There is no AI, cloud processing or paid API.

## Requirements
- Windows 10/11
- Python 3.9+
- Windows Python Launcher (py)
- Dependencies listed in requirements.txt

Install: py -m pip install -r requirements.txt
Run: py -m app.main or double-click run.bat
Build: build_exe.bat

## Project structure
app/core — image, layers, masks and undo/redo
app/image — loading, saving and format definitions
app/processing — adjustments and retouch algorithms
app/ui — desktop window, theme and canvas widgets
tests — behavior tests
docs — architecture, research, licenses and phase status

## Design principles
- Original image remains accessible.
- Processing is local and offline.
- UI and image-processing code are separated.
- Retouch operations use masks and separate layers where practical.
- No fake AI features.
- No required accounts, subscriptions or remote services.
- Windows Unicode paths are supported by the launcher design.

## Retouch workflow
1. Open a portrait.
2. Add a retouch layer or select a retouch tool.
3. Adjust brush size and opacity.
4. Paint locally on the canvas.
5. Use masks to control affected regions.
6. Use Clone with Alt-click to select the source.
7. Use Undo/Redo while experimenting.
8. Export to JPEG, PNG or TIFF.

## Documentation
- docs/ARCHITECTURE.md
- docs/FEATURE_RESEARCH.md
- docs/LICENSES.md
- docs/PHASES.md

## Tests
Run: py -m unittest discover -s tests -v

## Roadmap
Later master-spec phases can add Frequency Separation UI, advanced skin retouching, curves/HSL, presets, project files, advanced RAW handling, performance optimization and packaging polish. These are not advertised as complete in v0.4.0.

## Privacy
Images are processed locally. The application does not require internet access, accounts, cloud storage or remote inference.

ALIS DEJA VU — Dark. Elegant. Professional. Offline.