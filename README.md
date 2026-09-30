# ALIS DEJA VU

**Professional Portrait & Fashion Photo Editing Studio**

A modern, offline-first photo editing and retouching application built in Python for Windows 10/11.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

### Core Capabilities (Phase 1)
- 🖼️ **Professional Image Viewer** - Zoom, pan, fit-to-window
- 📂 **Multi-Format Support** - JPEG, PNG, TIFF, and RAW formats
- 🎚️ **Basic Adjustments** - Exposure, Brightness, Contrast
- 🎨 **Color Tools** - Saturation, Temperature
- ↩️ **Undo/Redo System** - Full editing history
- 💾 **Export** - Save to JPEG, PNG, TIFF
- 🎯 **Professional UI** - Dark theme, clean interface

### Planned Features (Future Phases)
- Layer system with masks
- Advanced color grading (Curves, HSL, LUT support)
- Retouching tools (Healing, Clone, Dodge, Burn)
- Frequency separation
- Skin retouching tools
- Portrait enhancement
- Presets and project system

---

## Requirements

### System Requirements
- **OS**: Windows 10 or Windows 11
- **Python**: 3.9 or later
- **RAM**: 4 GB minimum (8 GB recommended)
- **Disk Space**: 500 MB

### Python Packages
- PySide6 >= 6.4.0 (Qt6 for Python)
- NumPy >= 1.23.0
- Pillow >= 9.5.0
- OpenCV >= 4.7.0
- scikit-image >= 0.20.0
- rawpy >= 0.18.0 (for RAW support)
- imageio >= 2.25.0

---

## Installation

### 1. Install Python
Download and install Python 3.9+ from [python.org](https://www.python.org/downloads/)

**Important**: During installation, check "Add Python to PATH"

### 2. Extract Project
Extract the ALIS DEJA VU project to your desired location.

### 3. Install Dependencies
Open Command Prompt in the project directory and run:

```bash
py -m pip install -r requirements.txt
```

---

## Running the Application

### Quick Start
Double-click `run.bat` in the project directory.

Or from Command Prompt:
```bash
run.bat
```

### Manual Launch
```bash
py -m app.main
```

---

## Building Windows Executable

Create a standalone `.exe` file:

```bash
build_exe.bat
```

The executable will be created in `dist/ALIS DEJA VU.exe`

---

## Usage

### Opening an Image
1. Click **File > Open Image** or press `Ctrl+O`
2. Select a supported image format
3. Image loads into the canvas

### Adjusting Images
1. Use sliders in the right panel to adjust:
   - **Exposure**: Overall brightness
   - **Brightness**: Lift or darken
   - **Contrast**: Increase or decrease tonal separation
   - **Saturation**: Color intensity
   - **Temperature**: Warm or cool tones

2. Changes update in real-time
3. Use **Ctrl+Z** to undo, **Ctrl+Y** to redo

### Navigating the Canvas
- **Scroll wheel**: Zoom in/out
- **Middle mouse button**: Pan/move image
- **Keyboard '+/-'**: Zoom in/out
- **'0' key**: Fit to window
- **'1' key**: 100% actual size

### Exporting
1. Click **File > Export As** or press `Ctrl+Shift+S`
2. Choose format (JPEG, PNG, TIFF)
3. Select save location
4. Image is saved to disk

### Resetting
- **Edit > Reset Image**: Clear all adjustments and return to original

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open Image |
| Ctrl+Shift+S | Export As |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl++ | Zoom In |
| Ctrl+- | Zoom Out |
| 0 | Fit to Window |
| 1 | Actual Size (100%) |
| Alt+F4 | Exit |

---

## Project Structure

```
alis_deja_vu/
├── run.bat              # Application launcher
├── build_exe.bat        # Build Windows executable
├── requirements.txt     # Python dependencies
├── README.md            # This file
│
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   │
│   ├── core/            # Core data structures
│   │   ├── image.py     # ImageData class
│   │   └── undo_redo.py # Undo/Redo system
│   │
│   ├── image/           # Image I/O
│   │   ├── loader.py    # Load images
│   │   ├── saver.py     # Save/Export
│   │   └── formats.py   # Format definitions
│   │
│   ├── processing/      # Image algorithms
│   │   └── adjustments.py # Adjustment functions
│   │
│   ├── ui/              # User Interface
│   │   ├── main_window.py # Main application window
│   │   ├── widgets.py   # UI components
│   │   └── theme.py     # Dark theme styling
│   │
│   ├── resources/       # Icons and assets
│   ├── utils/           # Helper functions
│   └── __init__.py
│
├── tests/               # Unit tests
│   ├── test_adjustments.py
│   ├── test_undo_redo.py
│   └── __init__.py
│
└── docs/                # Documentation
    ├── ARCHITECTURE.md
    ├── FEATURE_RESEARCH.md
    └── LICENSES.md
```

---

## Architecture

The application follows a clean architecture separating:

- **Core**: Image data and undo/redo system (independent of UI)
- **Image**: File I/O and format handling
- **Processing**: Image adjustment algorithms (pure functions)
- **UI**: Qt-based user interface (PySide6)
- **Utils**: Helper functions and utilities

This separation ensures:
- Processing logic is testable without GUI
- Easy to add new algorithms
- Future AI features can be added as separate modules

See `docs/ARCHITECTURE.md` for detailed information.

---

## Supported Formats

### Input Formats
- **Standard**: JPEG, PNG, TIFF
- **RAW** (when rawpy is installed):
  - Canon: CR2, CR3
  - Nikon: NEF
  - Sony: ARW
  - Fujifilm: RAF
  - Olympus: ORF
  - Panasonic: RW2
  - Other: DNG

### Export Formats
- JPEG (with quality control)
- PNG (lossless)
- TIFF (uncompressed)

---

## Performance

The application is optimized for performance:

- **NumPy vectorization** for fast processing
- **Efficient memory usage** - doesn't duplicate images unnecessarily
- **Real-time preview** - adjustments show instantly
- **Non-destructive editing** - original image always preserved

---

## Offline & Privacy

- ✅ **Completely offline** - no internet required
- ✅ **No cloud services** - images never uploaded
- ✅ **No AI services** - all processing local
- ✅ **No tracking** - completely private
- ✅ **No subscriptions** - free and open-source

---

## Development

### Running Tests
```bash
py -m pytest tests/
```

Or run individual tests:
```bash
py -m unittest tests.test_adjustments
py -m unittest tests.test_undo_redo
```

### Adding Features
1. Add processing functions to `app/processing/`
2. Create UI controls in `app/ui/main_window.py`
3. Add tests to `tests/`
4. Update documentation

---

## Troubleshooting

### "Python is not installed"
- Ensure Python 3.9+ is installed from [python.org](https://www.python.org)
- Run from Command Prompt: `py --version`

### Dependencies not installing
```bash
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

### RAW format not supported
- Install rawpy: `py -m pip install rawpy`

### Slow performance
- Reduce preview quality in Settings
- Close other applications
- Update graphics drivers

### Can't open image
- Ensure image format is supported
- Check image file is not corrupted
- Try converting to standard JPEG first

---

## License

ALIS DEJA VU is built using open-source components. See `docs/LICENSES.md` for complete dependency licenses.

**Key Dependencies**:
- PySide6 (LGPL)
- NumPy (BSD)
- Pillow (HPND)
- OpenCV (Apache 2.0)
- scikit-image (BSD)
- rawpy (MIT)

---

## Roadmap

### v0.2.0 (Next)
- [ ] Layers and layer masks
- [ ] Curves adjustment
- [ ] Histogram display
- [ ] Advanced color tools

### v0.3.0
- [ ] Retouching tools (Healing, Clone)
- [ ] Dodge & Burn
- [ ] Frequency separation

### v0.4.0
- [ ] Portrait retouching
- [ ] Skin enhancement
- [ ] Local adjustments

### v1.0.0
- [ ] Complete feature parity with professional tools
- [ ] Project system
- [ ] Preset system
- [ ] Full optimization

---

## Credits

Built using:
- [PySide6](https://wiki.qt.io/Qt_for_Python) - Qt bindings for Python
- [NumPy](https://numpy.org/) - Numerical computing
- [Pillow](https://python-pillow.org/) - Image processing
- [OpenCV](https://opencv.org/) - Computer vision
- [scikit-image](https://scikit-image.org/) - Image processing algorithms

---

## Support

For issues, feature requests, or questions:
1. Check the troubleshooting section above
2. Review existing issues in the repository
3. Create a new issue with detailed information

---

## Changelog

### v0.1.0 (Initial Release)
- ✅ Professional photo viewer with zoom/pan
- ✅ Basic adjustments (Exposure, Brightness, Contrast)
- ✅ Color adjustments (Saturation, Temperature)
- ✅ Undo/Redo system
- ✅ Multi-format support (JPEG, PNG, TIFF, RAW)
- ✅ Export capabilities
- ✅ Dark professional theme
- ✅ Windows batch launcher and builder

---

**Made with ❤️ for photographers, retouchers, and creatives.**

*ALIS DEJA VU - Dark. Elegant. Professional. Offline.*
