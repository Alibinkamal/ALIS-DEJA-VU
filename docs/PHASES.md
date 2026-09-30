# Development Status

The Master Prompt defines eight internal development phases. The repository now implements the requested scope of all eight phases.

## Phase 1 — Foundation
Python/Qt entrypoint, Windows launcher, image loading/export, dark workspace and canvas.

## Phase 2 — Basic Editing
Exposure, brightness, contrast, highlights, shadows, saturation, temperature, tint, vibrance, histogram statistics, zoom/pan and before/after.

## Phase 3 — Layers / Masks / Brush
Layer creation, duplication, deletion, reordering, opacity, blend modes, masks, mask inversion, brush painting/erasing and state history.

## Phase 4 — Retouching
Healing, Clone Stamp, Dodge and Burn using dedicated masked layers and visible-composite sampling.

## Phase 5 — Frequency / Skin / Color
Frequency Separation, natural skin smoothing, skin-tone balancing, RGB curves, HSL, color balance, selective color, split toning, LUT loading, sharpening, denoise and grain.

## Phase 6 — Presets / Project / Export
Built-in and user presets, versioned ALIS project files, layer/mask serialization, original-image references and JPEG/PNG/TIFF export with quality control.

## Phase 7 — RAW / Performance / Polish
Expanded rawpy format support, configurable RAW post-processing, bounded preview cache, worker-thread budget, settings persistence, drag/drop, before/after and UI workflow polish.

## Phase 8 — Testing / Packaging / Documentation
Behavior tests, Windows CI workflow, PyInstaller build configuration, architecture/research/license documentation and project status documentation.

## Validation note
The development environment used for implementation is not Windows, so Windows runtime/build validation is delegated to the repository CI workflow or the user's Windows machine. The repository does not claim a Windows build passed unless that result is actually observed.