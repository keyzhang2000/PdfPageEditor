"""Đa ngôn ngữ: tr(khóa, **tham_số). Thêm ngôn ngữ = thêm một file từ điển và một dòng trong LANGUAGES."""
from PySide6.QtCore import QSettings

from . import en, vi, zh_TW

# mã -> (tên hiển thị bằng chính ngôn ngữ đó, từ điển)
LANGUAGES = {
    "vi": ("Tiếng Việt", vi.STRINGS),
    "en": ("English", en.STRINGS),
    "zh_TW": ("繁體中文", zh_TW.STRINGS),
}
DEFAULT_LANGUAGE = "vi"

_current = DEFAULT_LANGUAGE


def tr(key, **params):
    text = LANGUAGES[_current][1].get(key)
    if text is None:  # thiếu bản dịch: dùng tiếng Việt, rồi đến chính khóa
        text = LANGUAGES[DEFAULT_LANGUAGE][1].get(key, key)
    return text.format(**params) if params else text


def current_language():
    return _current


def set_language(code, save=True):
    global _current
    if code not in LANGUAGES:
        return
    _current = code
    if save:
        QSettings("PdfPageEditor", "PdfPageEditor").setValue("language", code)


def load_saved_language():
    code = QSettings("PdfPageEditor", "PdfPageEditor").value("language", DEFAULT_LANGUAGE)
    set_language(code if code in LANGUAGES else DEFAULT_LANGUAGE, save=False)
