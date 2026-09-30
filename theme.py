"""
Application Theme - Dark professional styling
"""

from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt


class Colors:
    """Color palette for dark professional theme"""
    
    # Base colors
    BACKGROUND = QColor(25, 25, 28)          # Very dark gray
    SURFACE = QColor(35, 35, 40)             # Dark gray
    SURFACE_LIGHT = QColor(50, 50, 58)       # Lighter gray
    BORDER = QColor(60, 60, 68)              # Border color
    
    # Text colors
    TEXT_PRIMARY = QColor(240, 240, 245)     # Nearly white
    TEXT_SECONDARY = QColor(180, 180, 190)   # Medium gray
    TEXT_DISABLED = QColor(120, 120, 130)    # Disabled gray
    
    # Accent colors (minimal, elegant)
    ACCENT_PRIMARY = QColor(100, 180, 220)   # Soft blue
    ACCENT_HOVER = QColor(120, 200, 240)     # Brighter blue
    ACCENT_ACTIVE = QColor(80, 160, 200)     # Darker blue
    
    # Status colors
    SUCCESS = QColor(100, 200, 100)           # Green
    WARNING = QColor(240, 180, 60)            # Orange
    ERROR = QColor(240, 100, 100)             # Red
    INFO = QColor(100, 180, 220)              # Blue
    
    # Canvas/Image area
    CANVAS_BACKGROUND = QColor(20, 20, 22)   # Almost black
    
    # Histogram/Info
    HISTOGRAM_BG = QColor(30, 30, 35)
    HISTOGRAM_LINE = QColor(100, 180, 220)


class Fonts:
    """Font definitions"""
    
    @staticmethod
    def get_title_font() -> QFont:
        """Get title font (larger, regular)"""
        font = QFont("Segoe UI", 14)
        font.setWeight(QFont.Weight.Medium)
        return font
    
    @staticmethod
    def get_default_font() -> QFont:
        """Get default application font"""
        font = QFont("Segoe UI", 10)
        font.setWeight(QFont.Weight.Normal)
        return font
    
    @staticmethod
    def get_small_font() -> QFont:
        """Get small font for labels/info"""
        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.Weight.Normal)
        return font
    
    @staticmethod
    def get_monospace_font() -> QFont:
        """Get monospace font for coordinates/values"""
        font = QFont("Consolas", 9)
        font.setWeight(QFont.Weight.Normal)
        return font


class StyleSheet:
    """Application-wide stylesheet"""
    
    @staticmethod
    def get_stylesheet() -> str:
        """Get complete stylesheet"""
        return f"""
        * {{
            background-color: {Colors.BACKGROUND.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            border: none;
        }}
        
        QMainWindow {{
            background-color: {Colors.BACKGROUND.name()};
        }}
        
        QWidget {{
            background-color: {Colors.BACKGROUND.name()};
            color: {Colors.TEXT_PRIMARY.name()};
        }}
        
        QLabel {{
            color: {Colors.TEXT_PRIMARY.name()};
        }}
        
        QPushButton {{
            background-color: {Colors.SURFACE.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            border: 1px solid {Colors.BORDER.name()};
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 10px;
        }}
        
        QPushButton:hover {{
            background-color: {Colors.SURFACE_LIGHT.name()};
            border: 1px solid {Colors.ACCENT_HOVER.name()};
        }}
        
        QPushButton:pressed {{
            background-color: {Colors.ACCENT_ACTIVE.name()};
        }}
        
        QPushButton:disabled {{
            color: {Colors.TEXT_DISABLED.name()};
            background-color: {Colors.SURFACE.name()};
        }}
        
        QSlider::groove:horizontal {{
            border: 1px solid {Colors.BORDER.name()};
            height: 4px;
            background: {Colors.SURFACE.name()};
            margin: 2px 0;
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            background: {Colors.ACCENT_PRIMARY.name()};
            border: 1px solid {Colors.ACCENT_HOVER.name()};
            width: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {Colors.ACCENT_HOVER.name()};
        }}
        
        QSlider::sub-page:horizontal {{
            background: {Colors.ACCENT_PRIMARY.name()};
            border-radius: 2px;
        }}
        
        QSpinBox, QDoubleSpinBox {{
            background-color: {Colors.SURFACE.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            border: 1px solid {Colors.BORDER.name()};
            border-radius: 4px;
            padding: 4px;
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {Colors.BORDER.name()};
            background-color: {Colors.SURFACE_LIGHT.name()};
        }}
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid {Colors.BORDER.name()};
            background-color: {Colors.SURFACE_LIGHT.name()};
        }}
        
        QComboBox {{
            background-color: {Colors.SURFACE.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            border: 1px solid {Colors.BORDER.name()};
            border-radius: 4px;
            padding: 4px;
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {Colors.BORDER.name()};
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {Colors.SURFACE.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            selection-background-color: {Colors.ACCENT_PRIMARY.name()};
            border: 1px solid {Colors.BORDER.name()};
        }}
        
        QLineEdit {{
            background-color: {Colors.SURFACE.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            border: 1px solid {Colors.BORDER.name()};
            border-radius: 4px;
            padding: 4px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {Colors.ACCENT_PRIMARY.name()};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {Colors.BORDER.name()};
        }}
        
        QTabBar::tab {{
            background-color: {Colors.SURFACE.name()};
            color: {Colors.TEXT_SECONDARY.name()};
            padding: 6px 12px;
            border: 1px solid {Colors.BORDER.name()};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {Colors.SURFACE_LIGHT.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            border-bottom: 2px solid {Colors.ACCENT_PRIMARY.name()};
        }}
        
        QTabBar::tab:hover {{
            background-color: {Colors.SURFACE_LIGHT.name()};
        }}
        
        QScrollBar:vertical {{
            border: none;
            background-color: {Colors.SURFACE.name()};
            width: 12px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {Colors.BORDER.name()};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {Colors.ACCENT_PRIMARY.name()};
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background-color: {Colors.SURFACE.name()};
            height: 12px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {Colors.BORDER.name()};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {Colors.ACCENT_PRIMARY.name()};
        }}
        
        QMenuBar {{
            background-color: {Colors.SURFACE.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            border-bottom: 1px solid {Colors.BORDER.name()};
        }}
        
        QMenuBar::item:selected {{
            background-color: {Colors.SURFACE_LIGHT.name()};
        }}
        
        QMenu {{
            background-color: {Colors.SURFACE.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            border: 1px solid {Colors.BORDER.name()};
        }}
        
        QMenu::item:selected {{
            background-color: {Colors.ACCENT_PRIMARY.name()};
            color: {Colors.BACKGROUND.name()};
        }}
        
        QDockWidget {{
            color: {Colors.TEXT_PRIMARY.name()};
            titlebar-close-icon: url(close.png);
        }}
        
        QDockWidget::title {{
            background-color: {Colors.SURFACE.name()};
            color: {Colors.TEXT_PRIMARY.name()};
            padding: 6px;
            border-bottom: 1px solid {Colors.BORDER.name()};
        }}
        
        QGroupBox {{
            color: {Colors.TEXT_PRIMARY.name()};
            border: 1px solid {Colors.BORDER.name()};
            border-radius: 4px;
            padding-top: 12px;
            margin-top: 6px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }}
        """
