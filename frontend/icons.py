"""Biểu tượng vẽ bằng SVG nội tuyến (nét mảnh), tô theo màu giao diện hiện tại."""
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from . import theme

# Mỗi biểu tượng là các đường vẽ trong khung 24x24.
PATHS = {
    "open": "M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
    "save": "M5 3h11l3 3v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z M7 3v5h8V3 M7 21v-7h10v7",
    "saveas": "M5 3h11l3 3v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z M7 3v5h8V3 M7 21v-7h6",
    "delete": "M4 7h16 M10 11v6 M14 11v6 M6 7l1 13h10l1-13 M9 7V4h6v3",
    "ins_pdf": "M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z M14 3v5h5 M12 12v6 M9 15h6",
    "ins_blank": "M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z M14 3v5h5",
    "dup": "M8 8h12v12H8z M4 16V4h12",
    "rot_l": "M3 12a9 9 0 1 0 3-6.7 M3 4v5h5",
    "rot_r": "M21 12a9 9 0 1 1-3-6.7 M21 4v5h-5",
    "move_l": "M15 6l-6 6 6 6",
    "move_r": "M9 6l6 6-6 6",
    "move_to": "M4 12h12 M12 7l5 5-5 5 M20 5v14",
    "extract": "M12 3v12 M7 10l5 5 5-5 M5 21h14",
    "undo": "M9 14L4 9l5-5 M4 9h10a6 6 0 0 1 0 12h-3",
    "redo": "M15 14l5-5-5-5 M20 9H10a6 6 0 0 0 0 12h3",
    "select_all": "M4 4h16v16H4z M8 12l3 3 5-6",
    "quit": "M9 4H5v16h4 M16 8l4 4-4 4 M20 12H9",
}


def _render(svg, size):
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    QSvgRenderer(QByteArray(svg.encode())).render(p)
    p.end()
    return pm


def icon(name):
    color = theme.colors()["icon"]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" '
           f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{PATHS[name]}"/></svg>')
    pm = _render(svg, 48)   # vẽ lớn rồi để Qt thu nhỏ → rõ nét trên màn hình độ phân giải cao
    return QIcon(pm)


def app_icon():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           '<rect width="64" height="64" rx="14" fill="#2563eb"/>'
           '<path d="M20 12h17l9 9v31a3 3 0 0 1-3 3H20a3 3 0 0 1-3-3V15a3 3 0 0 1 3-3z" fill="#fff"/>'
           '<path d="M37 12v9h9" fill="#bfdbfe"/>'
           '<rect x="23" y="30" width="18" height="3" rx="1.5" fill="#2563eb"/>'
           '<rect x="23" y="38" width="18" height="3" rx="1.5" fill="#93c5fd"/>'
           '<rect x="23" y="46" width="12" height="3" rx="1.5" fill="#93c5fd"/></svg>')
    ic = QIcon()
    for s in (16, 32, 64, 128, 256):
        ic.addPixmap(_render(svg, s))
    return ic
