import sys
import os
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    from app.ui.main_window import MainWindow as AppMainWindow

    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()
    sys.exit(app.exec())
