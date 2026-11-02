"""Xoay trang."""
from PySide6.QtCore import Qt
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
            self.set_thumbnail(it, self.render_entry(e, self.thumb_scale))
        if self.icon_size() != self.list.iconSize():   # hướng trang đổi làm ô lớn nhất đổi: dựng lại thumbnail
            self.start_rendering()
        self.update_preview()
