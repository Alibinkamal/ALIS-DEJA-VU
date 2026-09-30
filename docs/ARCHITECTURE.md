# ALIS DEJA VU Architecture

## Runtime
Python is the primary application runtime. PySide6 owns the desktop UI; NumPy, OpenCV and Pillow provide deterministic local image processing. Internal images are float32 RGB arrays in the 0–1 range.

## Modules
- app/core — image state, layers, masks and undo/redo
- app/image — standard and RAW loading plus export format definitions
- app/processing — adjustments, retouch primitives and detail operations
- app/color — curves, HSL, vibrance, color balance, selective color, split toning and LUT parsing
- app/retouch — frequency separation and skin workflows
- app/presets — built-in and user preset serialization
- app/project — versioned .alis project container
- app/export — resize and JPEG/PNG/TIFF export
- app/performance — bounded preview cache
- app/utils — persistent settings and developer logging
- app/ui — Qt orchestration and canvas interaction

UI code calls processing services. Processing code does not import Qt, so algorithms remain independently testable.

## Data flow

Original file -> ImageLoader -> ImageData -> Adjustment/Color Pipeline -> LayerStack -> Composite -> ImageCanvas

Project flow:

Original reference + project manifest + layer arrays/masks -> ProjectFile -> ImageData/LayerStack -> Composite

Export flow:

LayerStack composite -> export_image -> JPEG/PNG/TIFF

## Non-destructive model

The source file is never overwritten. The background layer represents the adjustment pipeline during rendering. When a project is saved, the background layer is stored from the original image and the adjustments are stored separately.

Retouch layers remain independent and can carry masks.

## Frequency Separation

Frequency Separation creates two editable layers:
- Low Frequency stores color and tone.
- High Frequency stores texture encoded around 0.5.

High Frequency uses Linear Light blending, where the encoded detail reconstructs the original image when untouched. The workflow is informed by documented high-pass/detail-layer concepts.

GIMP high-pass reference:
https://docs.gimp.org/3.0/en/gimp-filter-high-pass.html

## Color

Curves are represented as interpolated 256-sample lookup tables. HSL/vibrance and color-balance operations use bounded HSV/luminance calculations. LUT support parses standard .cube 3D LUT tables.

The design was informed by documented RGB curve and professional color-balance workflows in darktable:
https://docs.darktable.org/usermanual/5.6/en/module-reference/processing-modules/rgb-curve/
https://docs.darktable.org/usermanual/4.6/en/module-reference/processing-modules/color-balance/

## Retouching

Healing, clone and Dodge/Burn operate on the visible composite and write to dedicated masked layers. This follows the general non-destructive/sample-merged concepts documented by GIMP without copying implementation code.

## RAW

RAW decoding is optional through rawpy. RawOptions controls camera white balance, auto white balance, half-size preview, automatic brightness suppression and output bit depth.

Reference:
https://letmaik.github.io/rawpy/api/rawpy.Params.html

## Performance

PreviewCache provides bounded caching. Application settings expose cache size and worker-thread budget. QThreadPool/QRunnable is the intended mechanism for moving expensive operations off the GUI thread.

Reference:
https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThreadPool.html

## Project serialization

The .alis format is a ZIP container containing manifest.json, layer_N.npy and optional mask_N.npy. NumPy arrays are stored with allow_pickle=False.

## Error handling

UI-level file/project/export failures are presented as user-facing messages and logged to ~/.alis_deja_vu/app.log.

## Future AI extension

A future local-AI subsystem can be isolated behind the processing layer. Version 1 deliberately contains no AI runtime or model dependency.
