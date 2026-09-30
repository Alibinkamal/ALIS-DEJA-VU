from PySide6.QtGui import QColor,QFont
class Colors:
 BACKGROUND=QColor("#111214"); SURFACE=QColor("#181a1d"); SURFACE_LIGHT=QColor("#22252a"); BORDER=QColor("#30343a"); TEXT_PRIMARY=QColor("#e8e9eb"); TEXT_SECONDARY=QColor("#9aa0a8"); TEXT_DISABLED=QColor("#5d626a"); ACCENT_PRIMARY=QColor("#c6a15b"); ACCENT_HOVER=QColor("#dfbd77"); ACCENT_ACTIVE=QColor("#9e7c42"); CANVAS_BACKGROUND=QColor("#0b0c0e")
class Fonts:
 @staticmethod
 def get_default_font(): return QFont("Segoe UI",10)
class StyleSheet:
 @staticmethod
 def get_stylesheet():
  c=Colors; return f'''QWidget{{background:{c.BACKGROUND.name()};color:{c.TEXT_PRIMARY.name()};}} QMainWindow{{background:{c.BACKGROUND.name()};}} QPushButton{{background:{c.SURFACE.name()};color:{c.TEXT_PRIMARY.name()};border:1px solid {c.BORDER.name()};padding:6px;border-radius:4px;}} QPushButton:hover{{border-color:{c.ACCENT_PRIMARY.name()};}} QSlider::groove:horizontal{{height:4px;background:{c.BORDER.name()};}} QSlider::handle:horizontal{{width:14px;margin:-5px 0;background:{c.ACCENT_PRIMARY.name()};border-radius:7px;}} QComboBox,QSpinBox{{background:{c.SURFACE.name()};border:1px solid {c.BORDER.name()};padding:4px;}} QGroupBox{{border:1px solid {c.BORDER.name()};margin-top:8px;padding-top:10px;}} QGroupBox::title{{subcontrol-origin:margin;left:8px;padding:0 3px;}} QDockWidget::title,QMenuBar,QMenu{{background:{c.SURFACE.name()};}} QMenu::item:selected{{background:{c.ACCENT_PRIMARY.name()};color:{c.BACKGROUND.name()};}}'''
