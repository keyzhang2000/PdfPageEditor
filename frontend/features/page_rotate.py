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
        self.list.doItemsLayout()   # kích thước thẻ đổi (ngang <-> dọc): xếp lại để không đè lên trang bên cạnh
        self.update_preview()
