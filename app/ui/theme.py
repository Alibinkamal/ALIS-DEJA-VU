from PySide6.QtGui import QColor,QFont

class Colors:
    BACKGROUND=QColor("#090B10"); SURFACE=QColor("#11151D"); SURFACE_2=QColor("#171D27")
    SURFACE_3=QColor("#202837"); BORDER=QColor("#2A3444"); TEXT_PRIMARY=QColor("#F4F7FB")
    TEXT_SECONDARY=QColor("#9AA7B8"); TEXT_MUTED=QColor("#657286"); ACCENT=QColor("#8B5CF6")
    ACCENT_2=QColor("#06B6D4"); SUCCESS=QColor("#22C55E"); WARNING=QColor("#F59E0B")
    CANVAS_BACKGROUND=QColor("#07090D")

class Fonts:
    @staticmethod
    def get_default_font(): return QFont("Segoe UI",10)

class StyleSheet:
    @staticmethod
    def get_stylesheet():
        c=Colors
        return f"""
        * {{ font-family:'Segoe UI'; font-size:10pt; }}
        QMainWindow,QWidget {{ background:{c.BACKGROUND.name()}; color:{c.TEXT_PRIMARY.name()}; }}
        QToolTip {{ background:#0D1118; color:#F4F7FB; border:1px solid {c.BORDER.name()}; padding:7px; }}
        QMenuBar {{ background:#0B0E14; color:{c.TEXT_SECONDARY.name()}; padding:5px 8px; border-bottom:1px solid {c.BORDER.name()}; }}
        QMenuBar::item:selected,QMenu::item:selected {{ background:{c.ACCENT.name()}; color:white; border-radius:5px; }}
        QMenu {{ background:{c.SURFACE.name()}; border:1px solid {c.BORDER.name()}; padding:5px; }}
        QMenu::item {{ padding:7px 24px; }}
        QFrame#TopBar,QFrame#SidePanel,QFrame#Inspector,QFrame#Section {{ background:{c.SURFACE.name()}; border:1px solid {c.BORDER.name()}; border-radius:12px; }}
        QLabel#Brand {{ font-size:16pt; font-weight:700; color:white; }}
        QLabel#Subtle {{ color:{c.TEXT_SECONDARY.name()}; }}
        QLabel#SectionTitle {{ color:white; font-size:11pt; font-weight:700; padding:3px; }}
        QToolButton#Nav {{ background:transparent; color:{c.TEXT_SECONDARY.name()}; border:0; border-radius:8px; padding:8px 12px; }}
        QToolButton#Nav:hover {{ background:{c.SURFACE_3.name()}; color:white; }}
        QToolButton#Nav:checked {{ background:{c.ACCENT.name()}; color:white; }}
        QPushButton {{ background:{c.SURFACE_2.name()}; color:{c.TEXT_PRIMARY.name()}; border:1px solid {c.BORDER.name()}; border-radius:8px; padding:7px 10px; }}
        QPushButton:hover {{ background:{c.SURFACE_3.name()}; border-color:{c.ACCENT.name()}; }}
        QPushButton#Primary {{ background:{c.ACCENT.name()}; border-color:{c.ACCENT.name()}; color:white; font-weight:700; }}
        QPushButton#Primary:hover {{ background:#9B72F5; }}
        QToolButton#Icon {{ background:{c.SURFACE_2.name()}; border:1px solid {c.BORDER.name()}; border-radius:8px; padding:6px; }}
        QToolButton#Icon:hover {{ border-color:{c.ACCENT_2.name()}; }}
        QScrollArea {{ border:0; background:transparent; }}
        QScrollBar:vertical {{ background:transparent; width:9px; margin:4px; }}
        QScrollBar::handle:vertical {{ background:{c.SURFACE_3.name()}; border-radius:4px; min-height:30px; }}
        QSlider::groove:horizontal {{ height:4px; background:{c.BORDER.name()}; border-radius:2px; }}
        QSlider::handle:horizontal {{ width:14px; margin:-5px 0; background:{c.ACCENT.name()}; border-radius:7px; }}
        QComboBox,QSpinBox,QDoubleSpinBox {{ background:{c.SURFACE_2.name()}; border:1px solid {c.BORDER.name()}; border-radius:7px; padding:6px; }}
        QListWidget {{ background:{c.SURFACE_2.name()}; border:1px solid {c.BORDER.name()}; border-radius:8px; padding:4px; }}
        QListWidget::item {{ padding:8px; border-radius:6px; }}
        QListWidget::item:selected {{ background:{c.ACCENT.name()}; color:white; }}
        QLineEdit {{ background:{c.SURFACE_2.name()}; border:1px solid {c.BORDER.name()}; border-radius:7px; padding:7px; }}
        QStatusBar {{ background:#0B0E14; color:{c.TEXT_SECONDARY.name()}; border-top:1px solid {c.BORDER.name()}; }}
        """
