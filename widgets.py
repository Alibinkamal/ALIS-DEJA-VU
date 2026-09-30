"""
UI Widgets - Canvas, toolbar, and control panels
"""

import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, QFrame, QScrollArea
from PySide6.QtGui import QImage, QPixmap, QMouseEvent, QWheelEvent, QPainter, Qt, QFont
from PySide6.QtCore import Qt as QtCore, Signal, QTimer
from typing import Optional, Tuple

from app.ui.theme import Colors, Fonts


class ImageCanvas(QWidget):
    """
    Professional image canvas with:
    - Zoom and pan
    - Before/after comparison
    - High-quality rendering
    """
    
    zoom_changed = Signal(float)  # zoom level
    position_changed = Signal(int, int)  # x, y coordinates
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.image_data = None
        self.pixmap = None
        
        # Canvas state
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        
        # Display state
        self.show_before_after = False
        self.split_mode = False  # Side-by-side comparison
        
        # Set background
        self.setStyleSheet(f"background-color: {Colors.CANVAS_BACKGROUND.name()};")
        self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
    
    def set_image(self, image_array: np.ndarray) -> None:
        """
        Set image to display.
        
        Args:
            image_array: Image data (0-1 float range)
        """
        self.image_data = image_array
        self.update_pixmap()
    
    def update_pixmap(self) -> None:
        """Regenerate pixmap from image data"""
        if self.image_data is None:
            self.pixmap = None
            self.update()
            return
        
        # Convert to uint8 and create QImage
        uint8_data = np.clip(self.image_data * 255, 0, 255).astype(np.uint8)
        
        if len(uint8_data.shape) == 3 and uint8_data.shape[2] == 3:
            # RGB image
            height, width = uint8_data.shape[:2]
            q_image = QImage(uint8_data.data, width, height, 3 * width, QImage.Format.Format_RGB888)
            self.pixmap = QPixmap.fromImage(q_image)
        elif len(uint8_data.shape) == 2:
            # Grayscale image
            height, width = uint8_data.shape
            q_image = QImage(uint8_data.data, width, height, width, QImage.Format.Format_Grayscale8)
            self.pixmap = QPixmap.fromImage(q_image)
        
        # Reset zoom to fit
        self.fit_to_window()
        self.update()
    
    def fit_to_window(self) -> None:
        """Fit image to window"""
        if self.pixmap is None or self.pixmap.isNull():
            return
        
        img_width = self.pixmap.width()
        img_height = self.pixmap.height()
        
        if img_width <= 0 or img_height <= 0:
            return
        
        # Calculate zoom to fit
        x_scale = self.width() / img_width
        y_scale = self.height() / img_height
        
        self.zoom_level = min(x_scale, y_scale, 1.0)  # Don't zoom beyond 100%
        self.pan_x = 0
        self.pan_y = 0
        
        self.zoom_changed.emit(self.zoom_level)
        self.update()
    
    def zoom_in(self) -> None:
        """Zoom in (1.25x)"""
        self.set_zoom(self.zoom_level * 1.25)
    
    def zoom_out(self) -> None:
        """Zoom out (0.8x)"""
        self.set_zoom(self.zoom_level / 1.25)
    
    def set_zoom(self, zoom: float) -> None:
        """
        Set zoom level.
        
        Args:
            zoom: Zoom level (0.1 to 10.0)
        """
        self.zoom_level = max(0.1, min(10.0, zoom))
        self.zoom_changed.emit(self.zoom_level)
        self.update()
    
    def reset_view(self) -> None:
        """Reset to fit window"""
        self.fit_to_window()
    
    def actual_size(self) -> None:
        """Set zoom to 100%"""
        self.set_zoom(1.0)
    
    def paintEvent(self, event):
        """Paint the canvas"""
        if self.pixmap is None or self.pixmap.isNull():
            # Draw placeholder
            painter = QPainter(self)
            painter.fillRect(self.rect(), Colors.CANVAS_BACKGROUND)
            
            painter.setPen(Colors.TEXT_SECONDARY)
            painter.setFont(Fonts.get_default_font())
            painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, 
                           "No image loaded\nDrag and drop or use File > Open")
            return
        
        painter = QPainter(self)
        painter.fillRect(self.rect(), Colors.CANVAS_BACKGROUND)
        
        # Calculate scaled image size
        img_width = self.pixmap.width()
        img_height = self.pixmap.height()
        
        scaled_width = int(img_width * self.zoom_level)
        scaled_height = int(img_height * self.zoom_level)
        
        # Center image if smaller than canvas
        if scaled_width < self.width():
            x = (self.width() - scaled_width) // 2 + self.pan_x
        else:
            x = self.pan_x
        
        if scaled_height < self.height():
            y = (self.height() - scaled_height) // 2 + self.pan_y
        else:
            y = self.pan_y
        
        # Draw image
        scaled_pixmap = self.pixmap.scaledToWidth(
            scaled_width,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        
        painter.drawPixmap(x, y, scaled_pixmap)
        
        # Draw zoom indicator
        painter.setPen(Colors.TEXT_SECONDARY)
        painter.setFont(Fonts.get_small_font())
        zoom_text = f"{self.zoom_level * 100:.0f}%"
        painter.drawText(10, self.height() - 10, zoom_text)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for panning"""
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.pan_start_x = event.position().x()
            self.pan_start_y = event.position().y()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move for pan"""
        if self.is_panning:
            dx = int(event.position().x() - self.pan_start_x)
            dy = int(event.position().y() - self.pan_start_y)
            
            self.pan_x += dx
            self.pan_y += dy
            
            self.pan_start_x = event.position().x()
            self.pan_start_y = event.position().y()
            
            self.update()
        
        # Update position info
        if self.image_data is not None:
            height, width = self.image_data.shape[:2]
            self.position_changed.emit(width, height)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release"""
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == QtCore.Qt.Key.Key_Plus or event.key() == QtCore.Qt.Key.Key_Equal:
            self.zoom_in()
        elif event.key() == QtCore.Qt.Key.Key_Minus:
            self.zoom_out()
        elif event.key() == QtCore.Qt.Key.Key_1:
            self.actual_size()
        elif event.key() == QtCore.Qt.Key.Key_0:
            self.fit_to_window()
        else:
            super().keyPressEvent(event)


class ControlPanel(QFrame):
    """
    Control panel with adjustment sliders and options.
    """
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"background-color: {Colors.SURFACE.name()}; border: 1px solid {Colors.BORDER.name()}; border-radius: 4px;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(Fonts.get_title_font())
        title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY.name()};")
        layout.addWidget(title_label)
        
        self.setLayout(layout)
    
    def add_slider_control(
        self,
        label: str,
        min_val: float,
        max_val: float,
        default: float,
        callback
    ) -> Tuple[QSlider, QLabel]:
        """
        Add a labeled slider control.
        
        Args:
            label: Label text
            min_val: Minimum value
            max_val: Maximum value
            default: Default value
            callback: Function to call on value change
            
        Returns:
            Tuple of (slider, value_label)
        """
        layout = self.layout()
        
        # Row layout
        row_layout = QHBoxLayout()
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {Colors.TEXT_PRIMARY.name()};")
        label_widget.setMinimumWidth(80)
        row_layout.addWidget(label_widget)
        
        # Slider
        slider = QSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setMinimum(int(min_val * 100))
        slider.setMaximum(int(max_val * 100))
        slider.setValue(int(default * 100))
        slider.setMinimumWidth(150)
        row_layout.addWidget(slider)
        
        # Value label
        value_label = QLabel(f"{default:.2f}")
        value_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY.name()};")
        value_label.setMinimumWidth(50)
        row_layout.addWidget(value_label)
        
        # Connect slider to callback
        def on_slider_changed(value):
            actual_value = value / 100.0
            value_label.setText(f"{actual_value:.2f}")
            callback(actual_value)
        
        slider.valueChanged.connect(on_slider_changed)
        
        # Add to main layout
        layout.addLayout(row_layout)
        
        return slider, value_label
