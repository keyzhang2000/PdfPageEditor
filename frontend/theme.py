"""Giao diện: bảng màu sáng/tối (theo hệ thống) và stylesheet Qt."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

LIGHT = {
    "bg": "#f3f4f6", "panel": "#ffffff", "text": "#1f2937", "muted": "#6b7280", "border": "#e5e7eb",
    "accent": "#2563eb", "accent_soft": "#dbeafe", "hover": "#e5e7eb", "icon": "#374151",
    "page_border": "#cbd5e1", "placeholder": "#e5e7eb",
    "tab_strip": "#dfe3e8", "tab_sep": "#c4cad3",
}
DARK = {
    "bg": "#1b1d21", "panel": "#25282e", "text": "#e5e7eb", "muted": "#9ca3af", "border": "#33373f",
    "accent": "#3b82f6", "accent_soft": "#1e3a6e", "hover": "#32363e", "icon": "#d1d5db",
    "page_border": "#4b5563", "placeholder": "#32363e",
    "tab_strip": "#111317", "tab_sep": "#3a3f48",
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

/* Thanh tab kiểu Chrome: dải tab tối hơn nền, tab đang chọn sáng bằng vùng nội dung bên dưới và liền mạch với nó. */
QWidget#tabstrip {{ background: {c['tab_strip']}; }}
QTabBar {{ background: transparent; border: none; qproperty-drawBase: 0; }}
QTabBar::tab {{ background: transparent; color: {c['muted']}; padding: 7px 8px; margin: 6px 0 0 0;
               min-width: 120px; max-width: 240px; border: 1px solid transparent;
               border-top-left-radius: 10px; border-top-right-radius: 10px; }}
QTabBar::tab:!selected {{ margin-top: 8px; }}
QTabBar::tab:!selected:hover {{ background: {c['hover']}; color: {c['text']}; }}
QTabBar::tab:selected {{ background: {c['bg']}; color: {c['text']}; }}
QToolButton#tabclose {{ padding: 3px; border-radius: 9px; }}
QToolButton#tabclose:hover {{ background: {c['tab_sep']}; }}
QToolButton#tabplus {{ padding: 6px; border-radius: 9px; margin: 6px 2px 0 4px; }}
QToolButton#tabplus:hover {{ background: {c['hover']}; }}

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
