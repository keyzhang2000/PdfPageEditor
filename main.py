"""PDF Page Editor - điểm vào của ứng dụng.

backend/  : xử lý PDF thuần (không dùng Qt)
frontend/ : giao diện PySide6, mỗi chức năng một file trong frontend/features/
"""
import os
import sys

from PySide6.QtWidgets import QApplication

from frontend.icons import app_icon
from frontend.main_window import MainWindow
from frontend.theme import apply_theme


def main():
    app = QApplication(sys.argv)
    apply_theme(app)
    app.setWindowIcon(app_icon())
    w = MainWindow()
    w.show()
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        w.load_pdf(sys.argv[1])
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
