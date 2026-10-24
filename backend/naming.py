"""Đặt tên file khi Lưu thành."""
import os
import re
from datetime import date


def suggest_save_path(path, today=None):
    """<tên gốc>_modify_<yyyymmdd>.pdf (dấu * không hợp lệ trong tên file Windows)."""
    if not path:
        return ""
    today = today or date.today()
    folder, name = os.path.split(path)
    stem = re.sub(r"_modify_\d{8}$", "", os.path.splitext(name)[0])  # tránh nối đuôi nhiều lần
    return os.path.join(folder, f"{stem}_modify_{today:%Y%m%d}.pdf")
