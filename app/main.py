import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from app import APP_NAME,APP_VERSION
from app.ui.main_window import MainWindow

def resource_path(relative):
    base=Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parents[1]))
    return base/relative

def main():
    app=QApplication(sys.argv);app.setApplicationName(APP_NAME);app.setApplicationVersion(APP_VERSION);app.setStyle("Fusion")
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    icon=resource_path(Path("resources")/"alis_deja_vu.svg")
    if icon.exists():app.setWindowIcon(QIcon(str(icon)))
    w=MainWindow();w.setWindowIcon(QIcon(str(icon)) if icon.exists() else QIcon());w.show();return app.exec()

if __name__=="__main__":sys.exit(main())
