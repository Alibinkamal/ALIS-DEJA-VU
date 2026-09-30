# ALIS DEJA VU

**Professional Portrait, Beauty & Fashion Photo Editing Studio for Windows**

> **Current status:** v0.9.0 — modern UI/UX overhaul and expanded look library implemented. The project is in active development and is ready for hands-on testing, but it should not be treated as a fully validated production release until a Windows runtime/build pass has been completed.

ALIS DEJA VU is a local, offline-first desktop photo editor built with **Python + PySide6** for portrait, beauty, fashion and editorial photography. Its goal is to provide a serious non-AI retouching workflow based on classical image-processing techniques: layers, masks, healing, cloning, frequency separation, dodge & burn, color grading, presets and non-destructive project saving.

It is designed around a simple principle:

**Your original photo stays untouched. You work locally, keep your editing state in a project, and export the final result when you are ready.**

---

## What is ALIS DEJA VU?

ALIS DEJA VU is intended for photographers, retouchers and creators who want a focused desktop retouching workflow without mandatory cloud services, accounts or paid APIs.

The application currently provides:

- Professional dark desktop workspace with animated ambient canvas lighting
- Modern LOOKS / ADJUST / RETOUCH / LAYERS workspace navigation
- 80+ built-in editable looks across Cinematic, Portrait, Fashion, Film, Vintage, Moody, Warm, Cool, B&W, Editorial, Night and Clean families
- Look variants such as A1, A2, B1, B2, AB1, AB2, P1–P10 and more, with adjustable 0–100% intensity
- Professional Light / Color / Effects controls including Whites, Blacks, Clarity, Texture, Dehaze, Vignette and Grain
- Searchable visual look cards with category filtering and live application
- JPEG/JPG, PNG and TIFF workflows
- Optional RAW loading through `rawpy`
- Exposure and tonal adjustments
- Layers, masks and blend modes
- Healing and Clone Stamp retouching
- Dodge & Burn
- Frequency Separation
- Skin and color workflows
- Curves, HSL, Color Balance and Selective Color
- Split Toning and 3D LUT (.cube) loading
- Sharpening, noise reduction and film grain
- Presets
- Versioned `.alis` projects
- JPEG/PNG/TIFF export and resizing
- Preview caching and persistent settings
- Windows build support through PyInstaller

### Modern UI direction

The 0.9.0 workspace is intentionally inspired by the interaction patterns of modern mobile and professional editors, while using ALIS DEJA VU's own Python/PySide6 implementation. Looks are deterministic recipes generated from the current image rather than copied assets or third-party application code.

### What it deliberately does NOT do

Version 1 is deliberately **non-AI**.

There is currently no:

- Cloud image processing
- Generative fill
- AI face replacement
- AI skin segmentation
- Face recognition
- Mandatory online account
- Paid API
- Activation server

All core editing is performed locally on the user's machine.

---

# Quick Start — Run It on Windows

If you just want to test the application, this is the section you need.

## 1. Requirements

You need:

- **Windows 10 or Windows 11**
- **Python 3.9 or newer**
- The Windows Python Launcher: **`py`**
- Git (recommended if cloning the repository)

> The project uses the Windows Python Launcher, so the commands below intentionally use `py -m` rather than calling `python` directly.

---

## 2. Get the project

### Option A — Clone with Git

Open PowerShell:

```powershell
git clone https://github.com/Alibinkamal/ALIS-DEJA-VU.git
cd ALIS-DEJA-VU
```

### Option B — Download ZIP

On GitHub, choose **Code → Download ZIP**, extract the project, then open PowerShell in the extracted `ALIS-DEJA-VU` folder.

---

## 3. Install dependencies

From the project root, run:

```powershell
py -m pip install -r requirements.txt
```

This installs the application's Python dependencies, including PySide6, NumPy, Pillow, OpenCV, scikit-image, rawpy and imageio.

If you want to update pip first:

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

---

## 4. Start ALIS DEJA VU

### Recommended

Double-click:

**`run.bat`**

The launcher:

1. Moves into the project directory.
2. Checks that the Windows Python Launcher is available.
3. Checks that pip is available.
4. Starts the application with:

```powershell
py -m app.main
```

### Or start it manually

From the repository root:

```powershell
py -m app.main
```

If the application window opens, the installation is working.

---

# First Test Workflow

After launching the application, a simple first test is:

1. **Open an image**
   - Use **File → Open** or press `Ctrl+O`.
   - You can also drag an image onto the canvas.

2. **Check navigation**
   - Mouse wheel → Zoom
   - Middle mouse button → Pan
   - Fit/actual-size controls → inspect the image at different scales.

3. **Try basic adjustments**
   - Exposure
   - Brightness
   - Contrast
   - Highlights
   - Shadows
   - Temperature
   - Tint
   - Saturation
   - Vibrance

4. **Try a layer**
   - Create a new layer.
   - Change opacity or blend mode.
   - Add a mask and paint/erase on it.

5. **Try retouching**
   - Healing
   - Clone Stamp
   - Dodge
   - Burn

6. **Try advanced processing**
   - Frequency Separation
   - Curves / HSL / Color Balance
   - LUT loading
   - Sharpening / noise reduction / grain

7. **Save the project**
   - Press `Ctrl+S`.
   - Save it as an `.alis` project.

8. **Export the result**
   - Press `Ctrl+Shift+S`.
   - Export to JPEG, PNG or TIFF.

This workflow is useful for checking the complete application pipeline rather than testing isolated controls.

---

# Run Without Installing Anything Manually

If the dependencies are already installed, you can simply double-click:

```text
run.bat
```

If this is a fresh checkout, install the dependencies first with:

```powershell
py -m pip install -r requirements.txt
```

The repository does not currently ship a guaranteed prebuilt Windows installer. The included build script can create a standalone executable.

---

# Build a Windows EXE

The project includes:

```text
build_exe.bat
```

From Windows, double-click it or run it from PowerShell:

```powershell
.\build_exe.bat
```

The script:

1. Verifies the `py` launcher.
2. Installs/upgrades PyInstaller.
3. Installs project dependencies.
4. Cleans previous `build` and `dist` directories.
5. Builds a one-file, windowed Windows executable.
6. Collects the required RAW support and application resources.

The resulting executable is expected at:

```text
dist\ALIS DEJA VU.exe
```

### Important

The repository contains the build procedure, but a **Windows build should be considered validated only after the build has actually completed successfully on Windows**. The development environment used to maintain the repository is not itself a Windows runtime.

---

# Features by Development Phase

## Phase 1 — Foundation

- Python + PySide6 desktop application
- Windows Python Launcher workflow
- JPEG/JPG, PNG and TIFF
- Optional RAW loading through rawpy
- Dark professional UI
- Zoom, pan, fit and actual-size viewing
- Unicode/Arabic-path aware file handling

## Phase 2 — Basic Editing

- Exposure
- Brightness
- Contrast
- Highlights
- Shadows
- Temperature
- Tint
- Saturation
- Vibrance
- Histogram statistics
- Before/after comparison
- Undo/redo foundation

## Phase 3 — Layers, Masks & Brush

- Create, duplicate, delete and reorder layers
- Layer opacity
- Blend modes
- Normal, Multiply, Screen, Overlay, Soft Light, Add and Linear Light
- Grayscale masks
- Mask painting
- Mask erasing
- Mask inversion
- Soft brush falloff
- Layer-state history

## Phase 4 — Retouching

- Spot Healing
- Clone Stamp
- Alt-click source selection
- Dodge
- Burn
- Dedicated retouch layers
- Retouch masks
- Visible-composite sampling

## Phase 5 — Frequency, Skin & Color

- Frequency Separation
- Low Frequency / High Frequency layers
- Classical skin smoothing
- Deterministic skin-tone balancing
- RGB/master Curves
- HSL
- Vibrance
- Color Balance
- Selective Color
- Split Toning
- 3D LUT `.cube` loading
- Sharpening
- Noise reduction
- Film grain

## Phase 6 — Presets, Projects & Export

- Built-in starter presets
- User presets stored locally
- Versioned `.alis` project format
- Layer persistence
- Mask persistence
- Opacity persistence
- Blend-mode persistence
- Visibility persistence
- Adjustment-state persistence
- Original-image reference preservation
- JPEG/PNG/TIFF export
- JPEG quality control
- Export resizing

## Phase 7 — RAW, Performance & Polish

- Expanded RAW format detection
- rawpy camera/auto white-balance options
- Preview cache
- Configurable worker-thread budget
- Persistent settings
- Drag-and-drop image opening
- Before/after toggle
- Professional menus
- Dark workspace
- Developer logging

Background processing is structured around Qt's `QThreadPool` / `QRunnable` mechanisms so expensive work can remain outside the UI layer.

Reference: https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThreadPool.html

## Phase 8 — Testing, Packaging & Documentation

- Image-processing behavior tests
- Project workflow tests
- Windows GitHub Actions test workflow
- PyInstaller Windows build script
- Application resource/icon
- Architecture documentation
- Feature research documentation
- Third-party license documentation
- Phase status documentation

PyInstaller reference: https://pyinstaller.org/en/stable/usage.html

---

# Typical Retouching Workflow

ALIS DEJA VU is structured around a non-destructive editing workflow:

```text
Open Original
     │
     ▼
Basic Corrections
     │
     ▼
Layers & Masks
     │
     ├── Healing / Clone
     │
     ├── Dodge & Burn
     │
     └── Frequency Separation
     │
     ▼
Skin / Color Work
     │
     ├── Curves
     ├── HSL
     ├── Color Balance
     ├── Selective Color
     └── LUT / Split Toning
     │
     ▼
Preset (optional)
     │
     ▼
Save .alis Project
     │
     ▼
Export Final Image
```

The original image is kept as the source/reference for the editing project; project editing does not intentionally overwrite the original photograph.

---

# Project Files — `.alis`

An `.alis` project is a versioned, ZIP-based project container.

It stores project information such as:

- UTF-8 JSON manifest
- Image/layer data
- Float32 NumPy layer arrays
- Optional float32 masks
- Adjustment state
- Layer properties
- Visibility
- Opacity
- Blend mode
- Original-image reference

This allows an editing session to be saved and reopened rather than flattening everything into a single exported image.

### Recommended workflow

Use:

```text
.alis → working/editable project
.jpg/.png/.tiff → final exported image
```

Keep the `.alis` project if you expect to continue editing later.

---

# Keyboard & Mouse Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+O` | Open image |
| `Ctrl+S` | Save project |
| `Ctrl+Shift+S` | Export |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Tab` | Before/original view |
| Mouse wheel | Zoom |
| Middle mouse | Pan |
| `Alt+Click` | Select Clone Stamp source |
| Drag & drop | Open image |

---

# Supported Image Workflows

| Format | Role |
|---|---|
| JPEG / JPG | Open / edit / export |
| PNG | Open / edit / export |
| TIFF | Open / edit / export |
| RAW | Open through rawpy when supported by the installed rawpy/libraw stack |
| `.cube` | 3D LUT input |
| `.alis` | Native editable project |

RAW compatibility depends on the camera format supported by the installed `rawpy` / LibRaw build.

---

# Project Structure

```text
ALIS-DEJA-VU/
│
├── app/
│   ├── core/          Image state, layers, masks, undo/redo
│   ├── image/         Image loading, saving and formats
│   ├── processing/    Adjustments, retouch and detail processing
│   ├── color/         Curves, HSL, color balance, selective color, LUTs
│   ├── retouch/       Frequency separation and skin workflows
│   ├── presets/       Built-in and user presets
│   ├── project/       Versioned project serialization
│   ├── export/        Export and resizing
│   ├── performance/   Preview cache
│   ├── utils/         Settings and logging
│   └── ui/            PySide6 workspace and canvas
│
├── resources/         Application artwork and icon
├── tests/             Behavior and workflow tests
├── docs/              Engineering and research documentation
│
├── requirements.txt
├── run.bat
├── build_exe.bat
└── README.md
```

---

# Testing

Run the repository's test suite from the project root:

```powershell
py -m unittest discover -s tests -v
```

A Windows GitHub Actions workflow is also included for the repository's test command.

### Validation status

The codebase contains automated tests and Windows CI/build support. However, the repository should not be described as a fully production-validated release until the complete application has been exercised on Windows, including:

- dependency installation
- application startup
- image opening
- editing operations
- project save/reopen
- export
- RAW loading where applicable
- standalone EXE build

---

# Troubleshooting

## `py` is not recognized

Install Python for Windows with the **Python Launcher** enabled, then reopen PowerShell.

Verify:

```powershell
py --version
```

## Dependencies fail to install

Upgrade pip and retry:

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

If a package still fails, record the complete terminal error before changing project code.

## The application does not start

Run it from PowerShell instead of double-clicking `run.bat` so the error remains visible:

```powershell
py -m app.main
```

## RAW files do not open

RAW support depends on the installed `rawpy` / LibRaw capabilities and the specific camera format. Test with a supported RAW file and keep the original RAW untouched.

## EXE build fails

Run:

```powershell
py -m pip install --upgrade pyinstaller
py -m pip install -r requirements.txt
.\build_exe.bat
```

Keep the full build output when diagnosing a failure.

## Arabic or Unicode paths

The application is designed to handle Unicode/Arabic paths. If an issue occurs, test again from a normal Windows path and preserve the exact error message for diagnosis.

---

# Privacy, Offline Operation & Cost

ALIS DEJA VU is designed to operate locally.

- No login required
- No cloud processing
- No mandatory internet connection
- No paid API
- No activation server
- No user account required by the application
- No AI model required for the current version

Your images are processed on your own computer by the application.

---

# Development Philosophy

The project follows several principles:

### Local first

Image processing should happen on the user's machine.

### Non-destructive workflow

Editing should preserve the original source and retain editable project state wherever the current feature supports it.

### Deterministic processing

The current version uses classical image-processing algorithms rather than generative AI.

### Separation of concerns

The UI should orchestrate editing; image algorithms should remain in processing/core modules rather than being embedded directly inside Qt widgets.

### Extensibility

The architecture is intended to leave room for future capabilities without making AI, cloud services or paid APIs mandatory.

---

# Current Limitations

This repository represents an actively developed application, not a claim of parity with commercial editors.

Important limitations include:

- Windows is the primary target.
- RAW support depends on the installed rawpy/LibRaw stack.
- Performance depends on image dimensions and available system resources.
- Some advanced processing can be computationally expensive.
- A standalone EXE is buildable from the repository, but a prebuilt installer is not currently guaranteed.
- Full production validation requires a real Windows end-to-end pass.

---

# Contributing / Development

For development, clone the repository and install the same dependencies:

```powershell
git clone https://github.com/Alibinkamal/ALIS-DEJA-VU.git
cd ALIS-DEJA-VU
py -m pip install -r requirements.txt
py -m unittest discover -s tests -v
py -m app.main
```

When changing image-processing behavior, add or update tests where practical.

---

# License & Third-Party Components

The repository contains third-party dependencies and documentation covering dependency/license considerations. Check the repository's documentation before redistributing a packaged build.

---

# Release Status

**v0.8.0 — Phases 1–8 implemented**

This release represents the current completed development phase, not a declaration that every possible edge case has been eliminated.

The next practical milestone is **Windows end-to-end validation and release hardening**.

---

## In one sentence

**ALIS DEJA VU is a local, non-AI, Python/PySide6 photo-retouching studio for portrait, beauty and fashion work — built around layers, masks, classical retouching, color control and editable `.alis` projects.**
