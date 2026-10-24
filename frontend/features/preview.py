"""Khung xem trước trang đang chọn."""
from PySide6.QtCore import Qt



class PreviewMixin:
    def update_preview(self):
        self.update_status()
        items = self.list.selectedItems()
        if not items:
            return
        e = items[-1].data(Qt.UserRole)
        w = max(self.preview.parentWidget().width() - 20, 300)
        pw, ph = self.page_size(e)
        if e["rot"] % 180:
            pw, ph = ph, pw
        self.preview.setPixmap(self.render_entry(e, min(w / pw, 2.0)))

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if self.list.selectedItems():
            self.update_preview()
