import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app import APP_NAME,APP_VERSION
from app.ui.main_window import MainWindow
def main():
 app=QApplication(sys.argv); app.setApplicationName(APP_NAME); app.setApplicationVersion(APP_VERSION); app.setStyle("Fusion"); QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough); w=MainWindow(); w.show(); return app.exec()
if __name__=="__main__": sys.exit(main())
