# ALIS DEJA VU — Phases 9–17

## Phase 9 — Professional Masking
- Linear gradient masks
- Radial masks
- Mask inversion
- Existing brush/erase mask workflow remains available
- Masks remain attached to editable layers

## Phase 10 — Advanced Color Grading
- Three-way shadows / midtones / highlights color wheels
- Balance control
- Strength control
- Bloom and halation finishing controls
- Existing RGB curves, HSL, color balance, selective color, split toning and LUT support remain available

## Phase 11 — Transform, Crop & Geometry
- Pixel-accurate crop
- 90/180/270 degree rotation
- Horizontal / vertical flip
- Transforms are propagated through the layer stack and masks

## Phase 12 — Typography Studio
- Multiple text overlays
- Position controls
- Size
- Rotation
- Bold / italic
- Stroke
- Shadow
- Arabic/RTL support inherited from the typography pipeline
- Typography state is persisted in ALIS projects

## Phase 13 — Advanced Beauty Retouch
- Existing frequency separation
- Skin smoothing
- Skin-tone balancing
- Healing / Clone / Dodge / Burn
- Layer masks for localized retouching
- Deterministic local processing; no cloud or generative AI

## Phase 14 — History & Non-destructive Editing
- Existing undo/redo command architecture
- Pro grading, effects and typography are included in extended snapshots
- Layer-based editing is retained
- Original source remains separate from working layers

## Phase 15 — Presets & Export Studio
- Existing preset manager
- Export Studio
- JPEG quality
- Explicit output dimensions
- Aspect-ratio preservation
- JPEG / PNG / TIFF export
- ALIS project persistence for pro controls

## Phase 16 — Performance / Preview Architecture
- Existing preview cache
- Configurable worker-thread budget
- Preview resolution ceiling stored in the professional workspace
- Full-resolution export remains separate from preview intent
- Processing algorithms remain isolated from UI orchestration

## Phase 17 — Final Polish & Release Hardening
- Professional PRO STUDIO menu
- Centralized phase documentation
- Version 1.7.0
- Fujifilm-inspired look family
- Expanded deterministic look library
- Project metadata compatibility for new controls
- Release remains subject to real Windows end-to-end validation

## Fujifilm-inspired Look Family

ALIS DEJA VU includes a new FUJIFILM INSPIRED family with 60 graded variants derived from original deterministic recipes.

Families include:
- PROVIA
- VELVIA
- ASTIA
- CLASSIC CHROME
- REALA ACE
- PRO Neg. Hi
- PRO Neg. Std
- CLASSIC Neg.
- NOSTALGIC Neg.
- ETERNA
- ETERNA Bleach-style
- ACROS
- ACROS + Yellow / Red / Green
- Monochrome + Yellow / Red / Green
- Sepia

Each base look has three intensity character variants:
- S — restrained
- M — standard
- H — stronger

These are ALIS DEJA VU's own processing recipes, not copied Fujifilm LUT files. The naming communicates the intended visual direction.

FUJIFILM's public documentation describes Film Simulation families including PROVIA, Velvia, ASTIA, CLASSIC CHROME, REALA ACE, PRO Neg. modes, CLASSIC Neg., NOSTALGIC Neg., ETERNA, ACROS and monochrome filter variants. The ALIS implementation is intentionally independent and deterministic.

## Validation note

The project can be statically audited from the repository, but Windows runtime validation still needs to be performed on an actual Windows machine for:
- dependency installation
- application launch
- image opening
- large-image behavior
- RAW loading
- project save/reopen
- export
- PyInstaller EXE generation
