"""Giao diện: bảng màu sáng/tối (theo hệ thống) và stylesheet Qt."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

LIGHT = {
    "bg": "#f3f4f6", "panel": "#ffffff", "text": "#1f2937", "muted": "#6b7280", "border": "#e5e7eb",
    "accent": "#2563eb", "accent_soft": "#dbeafe", "hover": "#e5e7eb", "icon": "#374151",
    "page_border": "#cbd5e1", "placeholder": "#e5e7eb",
}
DARK = {
    "bg": "#1b1d21", "panel": "#25282e", "text": "#e5e7eb", "muted": "#9ca3af", "border": "#33373f",
    "accent": "#3b82f6", "accent_soft": "#1e3a6e", "hover": "#32363e", "icon": "#d1d5db",
    "page_border": "#4b5563", "placeholder": "#32363e",
}

_current = LIGHT


def colors():
    return _current


def is_dark(app):
    return app.styleHints().colorScheme() == Qt.ColorScheme.Dark


def _stylesheet(c):
    return f"""
QMainWindow, QSplitter {{ background: {c['bg']}; }}
QWidget {{ color: {c['text']}; font-size: 13px; }}

QMenuBar {{ background: {c['panel']}; border-bottom: 1px solid {c['border']}; padding: 2px 6px; }}
QMenuBar::item {{ padding: 5px 12px; border-radius: 6px; background: transparent; }}
QMenuBar::item:selected {{ background: {c['hover']}; }}
QMenu {{ background: {c['panel']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 6px; }}
QMenu::item {{ padding: 6px 28px 6px 14px; border-radius: 6px; }}
QMenu::item:selected {{ background: {c['accent_soft']}; }}
QMenu::item:disabled {{ color: {c['muted']}; }}
QMenu::separator {{ height: 1px; background: {c['border']}; margin: 5px 8px; }}

QToolBar {{ background: {c['panel']}; border: none; border-bottom: 1px solid {c['border']};
           padding: 6px 8px; spacing: 4px; }}
QToolBar::separator {{ width: 1px; background: {c['border']}; margin: 4px 8px; }}
QToolButton {{ padding: 6px 10px; border-radius: 8px; border: 1px solid transparent; background: transparent; }}
QToolButton:hover {{ background: {c['hover']}; }}
QToolButton:pressed {{ background: {c['accent_soft']}; }}
QToolButton:disabled {{ color: {c['muted']}; }}

QListWidget {{ background: {c['bg']}; border: none; outline: none; padding: 8px; }}
QListWidget::item {{ border-radius: 10px; padding: 8px; color: {c['muted']}; }}
QListWidget::item:hover {{ background: {c['hover']}; }}
QListWidget::item:selected {{ background: {c['accent_soft']}; color: {c['text']}; }}

QScrollArea {{ background: {c['bg']}; border: none; border-left: 1px solid {c['border']}; }}
QScrollArea > QWidget > QWidget {{ background: {c['bg']}; }}
QLabel {{ background: transparent; }}

QSplitter::handle {{ background: {c['border']}; width: 1px; }}
QSplitter::handle:hover {{ background: {c['accent']}; }}

QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px; }}
QScrollBar::handle {{ background: {c['page_border']}; border-radius: 4px; min-height: 30px; min-width: 30px; }}
QScrollBar::handle:hover {{ background: {c['muted']}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QSlider::groove:horizontal {{ height: 4px; background: {c['border']}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {c['accent']}; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {c['panel']}; border: 2px solid {c['accent']};
                             width: 12px; height: 12px; margin: -7px 0; border-radius: 8px; }}

QStatusBar {{ background: {c['panel']}; border-top: 1px solid {c['border']}; color: {c['muted']}; }}
QStatusBar::item {{ border: none; }}

QPushButton {{ background: {c['panel']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 6px 16px; }}
QPushButton:hover {{ background: {c['hover']}; }}
QPushButton:default {{ background: {c['accent']}; color: white; border-color: {c['accent']}; }}
QToolTip {{ background: {c['panel']}; color: {c['text']}; border: 1px solid {c['border']}; padding: 4px 8px; }}
"""


def apply_theme(app):
    """Gọi một lần lúc khởi động (trước khi dựng cửa sổ, để biểu tượng lấy đúng màu)."""
    global _current
    _current = DARK if is_dark(app) else LIGHT
    c = _current
    app.setStyle("Fusion")
    pal = QPalette()
    for role, key in ((QPalette.Window, "bg"), (QPalette.Base, "panel"), (QPalette.AlternateBase, "bg"),
                      (QPalette.Button, "panel"), (QPalette.ToolTipBase, "panel"),
                      (QPalette.WindowText, "text"), (QPalette.Text, "text"), (QPalette.ButtonText, "text"),
                      (QPalette.ToolTipText, "text"), (QPalette.Highlight, "accent")):
        pal.setColor(role, QColor(c[key]))
    pal.setColor(QPalette.HighlightedText, QColor("white"))
    app.setPalette(pal)
    app.setStyleSheet(_stylesheet(c))
