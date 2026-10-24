"""Xoay trang."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from backend.entries import rotated


class PageRotateMixin:
    def rotate(self, deg):
        sel = self.sorted_selected()
        if not sel:
            return
        self.push_undo()
        for it in sel:
            e = rotated(it.data(Qt.UserRole), deg)
            it.setData(Qt.UserRole, e)
            it.setIcon(QIcon(self.render_entry(e, self.thumb_scale)))
        self.update_preview()
