"""Tạo installer/app.ico từ icon của ứng dụng (frontend/icons.py). Chạy: python installer/make_icon.py (trong .venv)"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PySide6.QtGui import QGuiApplication

from frontend.icons import app_icon

app = QGuiApplication([])
out = os.path.join(ROOT, "installer", "app.ico")
# Qt ghi file .ico từ pixmap lớn nhất; Windows tự thu nhỏ khi cần.
ok = app_icon().pixmap(256, 256).save(out, "ICO")
sys.exit(0 if ok else "không ghi được " + out)
