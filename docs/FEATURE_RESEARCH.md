# Feature Research

Research was used to validate the Phase 3/4 workflow rather than copy another product's implementation.

## Krita
Krita documents layers as a central editing concept and masks as selective controls over layer visibility/effects. Its clone brush supports selecting a source and painting the duplicate elsewhere, with size and opacity controls.

## GIMP
GIMP documents Healing as a clone-related retouching operation that uses surrounding destination information, and documents Clone as a source-to-destination painting workflow. Its Dodge/Burn tool exposes brush size, opacity, hardness and tonal-range concepts.

## Design decisions for ALIS DEJA VU
1. Use Python/Qt for orchestration and UI.
2. Keep masks grayscale and separate from layer pixels.
3. Keep retouch operations local and deterministic.
4. Sample the visible composite for Healing/Clone.
5. Keep AI out of Version 1.
6. Keep the UI focused on portrait/fashion workflows rather than reproducing another editor's interface.

## Phase 3 delivered
- Layer creation/deletion/duplication.
- Layer ordering.
- Visibility and opacity state.
- Normal, Multiply, Screen, Overlay, Soft Light and Add blend modes.
- Editable transparency masks.
- Mask paint, erase and invert.
- Brush size/opacity controls.
- Reversible layer-stack history.

## Phase 4 delivered
- Spot Healing.
- Clone Stamp with Alt-click source selection.
- Dodge.
- Burn.
- Dedicated retouch layers and masks.
- Shared brush size/opacity controls.
- Undo/redo snapshots for retouch edits.
