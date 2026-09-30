"""
Main Window - Professional photo editing interface

Layout:
- Top: Menu bar and main controls
- Left: Tool and adjustment panels
- Center: Large image canvas
- Right: Properties/adjustment panels
- Bottom: Status bar with zoom and image info
"""

import sys
from pathlib import Path
from typing import Optional

import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QFileDialog, QDockWidget, QScrollArea,
    QStatusBar, QLabel, QSlider, QSpinBox, QComboBox, 
    QPushButton, QMessageBox, QSplitter, QFrame
)
from PySide6.QtGui import QIcon, QAction, QKeySequence, Qt, QColor, QFont
from PySide6.QtCore import Qt as QtCore, QSize

from app import APP_NAME, APP_VERSION
from app.core import ImageData, UndoRedoManager
from app.core.undo_redo import ImageAdjustmentCommand
from app.image import ImageLoader, ImageSaver, SUPPORTED_FORMATS_FILTER, EXPORT_FORMATS_FILTER
from app.processing import adjust_exposure, adjust_brightness, adjust_contrast, adjust_saturation, adjust_temperature
from app.ui.theme import Colors, Fonts, StyleSheet
from app.ui.widgets import ImageCanvas, ControlPanel


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setWindowIcon(self._create_app_icon())
        
        # Application state
        self.image_data: Optional[ImageData] = None
        self.undo_manager = UndoRedoManager(max_history=50)
        self.current_file_path: Optional[str] = None
        
        # Initialize UI
        self._setup_ui()
        self._connect_signals()
        
        # Apply theme
        self.setStyleSheet(StyleSheet.get_stylesheet())
        
        # Window size and position
        self.resize(1400, 900)
        self.center_window()
    
    def _create_app_icon(self) -> QIcon:
        """Create application icon"""
        # For now, create a simple gradient icon
        # In production, this would be a proper PNG file
        icon = QIcon()
        return icon
    
    def _setup_ui(self) -> None:
        """Setup the main UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main workspace
        workspace = QWidget()
        workspace_layout = QHBoxLayout()
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(8)
        
        # Left panel - Tools
        self.left_panel = self._create_left_panel()
        workspace_layout.addWidget(self.left_panel)
        
        # Center - Image canvas
        self.canvas = ImageCanvas()
        workspace_layout.addWidget(self.canvas, 1)
        
        # Right panel - Adjustments
        self.right_panel = self._create_right_panel()
        workspace_layout.addWidget(self.right_panel)
        
        workspace.setLayout(workspace_layout)
        main_layout.addWidget(workspace, 1)
        
        # Status bar
        self._create_status_bar()
    
    def _create_menu_bar(self) -> None:
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = file_menu.addAction("Open Image")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_image)
        
        file_menu.addSeparator()
        
        save_action = file_menu.addAction("Export As")
        save_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_action.triggered.connect(self.export_image)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = edit_menu.addAction("Undo")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.undo)
        self.undo_action = undo_action
        
        redo_action = edit_menu.addAction("Redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.redo)
        self.redo_action = redo_action
        
        edit_menu.addSeparator()
        
        reset_action = edit_menu.addAction("Reset Image")
        reset_action.triggered.connect(self.reset_image)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        zoom_in_action = view_menu.addAction("Zoom In")
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.canvas.zoom_in)
        
        zoom_out_action = view_menu.addAction("Zoom Out")
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.canvas.zoom_out)
        
        view_menu.addSeparator()
        
        fit_action = view_menu.addAction("Fit to Window")
        fit_action.setShortcut("0")
        fit_action.triggered.connect(self.canvas.fit_to_window)
        
        actual_size_action = view_menu.addAction("Actual Size")
        actual_size_action.setShortcut("1")
        actual_size_action.triggered.connect(self.canvas.actual_size)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
    
    def _create_left_panel(self) -> QFrame:
        """Create left toolbar panel"""
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {Colors.SURFACE.name()}; border-right: 1px solid {Colors.BORDER.name()};")
        panel.setMaximumWidth(200)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Quick tools section
        tools_panel = ControlPanel("Quick Tools")
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_image)
        tools_panel.layout().addWidget(reset_btn)
        
        layout.addWidget(tools_panel)
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def _create_right_panel(self) -> QFrame:
        """Create right adjustment panel"""
        panel = QFrame()
        panel.setStyleSheet(f"background-color: {Colors.SURFACE.name()}; border-left: 1px solid {Colors.BORDER.name()};")
        panel.setMaximumWidth(250)
        
        # Scroll area for adjustments
        scroll = QScrollArea()
        scroll.setStyleSheet(f"background-color: {Colors.SURFACE.name()}; border: none;")
        scroll.setWidgetResizable(True)
        
        # Adjustment panels
        adjustment_widget = QWidget()
        adjustment_layout = QVBoxLayout()
        adjustment_layout.setContentsMargins(8, 8, 8, 8)
        adjustment_layout.setSpacing(8)
        
        # Basic Adjustments
        basic_panel = ControlPanel("Basic")
        
        self.exposure_slider, _ = basic_panel.add_slider_control(
            "Exposure", -2, 2, 0, self._on_exposure_changed
        )
        self.brightness_slider, _ = basic_panel.add_slider_control(
            "Brightness", -1, 1, 0, self._on_brightness_changed
        )
        self.contrast_slider, _ = basic_panel.add_slider_control(
            "Contrast", -1, 1, 0, self._on_contrast_changed
        )
        
        adjustment_layout.addWidget(basic_panel)
        
        # Color Adjustments
        color_panel = ControlPanel("Color")
        
        self.saturation_slider, _ = color_panel.add_slider_control(
            "Saturation", -1, 1, 0, self._on_saturation_changed
        )
        self.temperature_slider, _ = color_panel.add_slider_control(
            "Temperature", -1, 1, 0, self._on_temperature_changed
        )
        
        adjustment_layout.addWidget(color_panel)
        
        # Add stretch
        adjustment_layout.addStretch()
        
        adjustment_widget.setLayout(adjustment_layout)
        scroll.setWidget(adjustment_widget)
        
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll)
        panel.setLayout(panel_layout)
        
        return panel
    
    def _create_status_bar(self) -> None:
        """Create status bar with image information"""
        status_bar = self.statusBar()
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY.name()};")
        self.zoom_label.setMinimumWidth(60)
        status_bar.addWidget(self.zoom_label)
        
        status_bar.addSeparator()
        
        self.info_label = QLabel("No image loaded")
        self.info_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY.name()};")
        status_bar.addWidget(self.info_label, 1)
    
    def _connect_signals(self) -> None:
        """Connect signals and slots"""
        self.canvas.zoom_changed.connect(self._on_zoom_changed)
        self.canvas.position_changed.connect(self._on_position_changed)
    
    # === File Operations ===
    
    def open_image(self) -> None:
        """Open image file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            SUPPORTED_FORMATS_FILTER
        )
        
        if not file_path:
            return
        
        self.load_image(file_path)
    
    def load_image(self, file_path: str) -> None:
        """Load image from file path"""
        try:
            # Check format support
            if not ImageLoader.can_load(file_path):
                QMessageBox.critical(
                    self,
                    "Unsupported Format",
                    f"The format is not supported.\n\nSupported formats: {', '.join(ImageLoader.get_supported_extensions())}"
                )
                return
            
            # Create ImageData
            self.image_data = ImageData(file_path)
            self.current_file_path = file_path
            
            # Reset adjustments
            self.undo_manager.clear()
            self._reset_sliders()
            
            # Update canvas
            self.canvas.set_image(self.image_data.get_working_image())
            
            # Update title
            filename = Path(file_path).name
            self.setWindowTitle(f"{APP_NAME} - {filename}")
            
            # Update status
            width, height = self.image_data.get_dimensions()
            self.info_label.setText(f"{filename} ({width}x{height})")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Image",
                f"Failed to load image:\n\n{str(e)}"
            )
    
    def export_image(self) -> None:
        """Export image to file"""
        if self.image_data is None:
            QMessageBox.warning(self, "No Image", "Please open an image first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Image",
            "",
            EXPORT_FORMATS_FILTER
        )
        
        if not file_path:
            return
        
        try:
            ImageSaver.save(
                self.image_data.get_working_image(),
                file_path,
                quality=95
            )
            self.info_label.setText(f"Exported: {Path(file_path).name}")
            QMessageBox.information(self, "Success", "Image exported successfully")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export image:\n\n{str(e)}")
    
    # === Editing Operations ===
    
    def _on_exposure_changed(self, value: float) -> None:
        """Handle exposure adjustment"""
        if self.image_data is None:
            return
        
        self._apply_adjustment(
            "Exposure",
            lambda img: adjust_exposure(img, value),
            {"exposure": value}
        )
    
    def _on_brightness_changed(self, value: float) -> None:
        """Handle brightness adjustment"""
        if self.image_data is None:
            return
        
        self._apply_adjustment(
            "Brightness",
            lambda img: adjust_brightness(img, value),
            {"brightness": value}
        )
    
    def _on_contrast_changed(self, value: float) -> None:
        """Handle contrast adjustment"""
        if self.image_data is None:
            return
        
        self._apply_adjustment(
            "Contrast",
            lambda img: adjust_contrast(img, value),
            {"contrast": value}
        )
    
    def _on_saturation_changed(self, value: float) -> None:
        """Handle saturation adjustment"""
        if self.image_data is None:
            return
        
        self._apply_adjustment(
            "Saturation",
            lambda img: adjust_saturation(img, value),
            {"saturation": value}
        )
    
    def _on_temperature_changed(self, value: float) -> None:
        """Handle temperature adjustment"""
        if self.image_data is None:
            return
        
        self._apply_adjustment(
            "Temperature",
            lambda img: adjust_temperature(img, value),
            {"temperature": value}
        )
    
    def _apply_adjustment(self, name: str, processor_func, params: dict) -> None:
        """Apply an adjustment to the image"""
        if self.image_data is None:
            return
        
        # Get current state
        previous_image = self.image_data.get_working_image().copy()
        
        # Process image
        processed_image = processor_func(self.image_data.original_image)
        
        # Apply all current adjustments
        current_exposure = self.image_data.get_adjustment("exposure", 0)
        current_brightness = self.image_data.get_adjustment("brightness", 0)
        current_contrast = self.image_data.get_adjustment("contrast", 0)
        current_saturation = self.image_data.get_adjustment("saturation", 0)
        current_temperature = self.image_data.get_adjustment("temperature", 0)
        
        # Reapply all adjustments in order
        result = self.image_data.original_image.copy()
        result = adjust_exposure(result, current_exposure)
        result = adjust_brightness(result, current_brightness)
        result = adjust_contrast(result, current_contrast)
        result = adjust_saturation(result, current_saturation)
        result = adjust_temperature(result, current_temperature)
        
        # Update image
        self.image_data.update_working_image(result)
        self.image_data.adjustments.update(params)
        
        # Update canvas
        self.canvas.set_image(self.image_data.get_working_image())
    
    def reset_image(self) -> None:
        """Reset image to original"""
        if self.image_data is None:
            return
        
        self.image_data.reset_to_original()
        self._reset_sliders()
        self.canvas.set_image(self.image_data.get_working_image())
        self.undo_manager.clear()
    
    def _reset_sliders(self) -> None:
        """Reset all adjustment sliders to 0"""
        for slider in [self.exposure_slider, self.brightness_slider,
                      self.contrast_slider, self.saturation_slider,
                      self.temperature_slider]:
            slider.blockSignals(True)
            slider.setValue(0)
            slider.blockSignals(False)
    
    def undo(self) -> None:
        """Undo last operation"""
        if self.undo_manager.undo():
            self.canvas.update_pixmap()
    
    def redo(self) -> None:
        """Redo last undone operation"""
        if self.undo_manager.redo():
            self.canvas.update_pixmap()
    
    # === UI Updates ===
    
    def _on_zoom_changed(self, zoom: float) -> None:
        """Update zoom label"""
        self.zoom_label.setText(f"{zoom * 100:.0f}%")
    
    def _on_position_changed(self, width: int, height: int) -> None:
        """Update position info"""
        if self.current_file_path:
            filename = Path(self.current_file_path).name
            self.info_label.setText(f"{filename} ({width}x{height})")
    
    # === Help ===
    
    def show_about(self) -> None:
        """Show about dialog"""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "Professional Portrait & Fashion Photo Editing\n\n"
            "Offline-first photo editing and retouching studio\n"
            "built in Python for Windows.\n\n"
            "© 2024 ALIS DEJA VU"
        )
    
    # === Window ===
    
    def center_window(self) -> None:
        """Center window on screen"""
        from PySide6.QtGui import QScreen
        screen = self.screen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
