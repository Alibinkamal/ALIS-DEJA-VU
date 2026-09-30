# ALIS DEJA VU Architecture

Version 0.4.0 implements the Phase 1–4 foundation.

## Runtime
Python + PySide6 is the application runtime. Image data is represented as float32 NumPy RGB arrays in the 0–1 range.

## Layers
- app/core/layers.py — Layer, LayerStack and blend modes.
- Each editable layer can carry a grayscale transparency mask.
- Blank retouch layers start with a black mask, so they are transparent until painted.
- Composite rendering applies opacity, mask and blend mode without changing the source image.

## Brush engine
app/core/masks.py provides a deterministic circular brush with opacity and hardness-like falloff. It is used for paint, mask painting and erasing.

## Retouch engine
app/processing/retouch.py provides Spot Healing through OpenCV inpainting, Clone Stamp with source/destination geometry and soft falloff, Dodge/Burn with radial falloff, and frequency-separation primitives for future skin workflows.

## UI
app/ui/main_window.py connects the layer stack, masks, adjustment controls and retouch tools. app/ui/widgets.py provides the canvas and brush input.

## Undo/redo
CallableCommand stores reversible state transitions. Phase 3/4 edits snapshot the layer stack before and after an operation. The history is capped to prevent unlimited memory growth.

## Extension points
Future processing modules can be added without putting processing logic into Qt widgets. A future local-AI package can remain isolated and optional.
