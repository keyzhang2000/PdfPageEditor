"""Khung xem trước trang đang chọn: tự co giãn vừa khít khung theo kích thước thực tế."""
from PySide6.QtCore import Qt

from backend.entries import displayed_size

MARGIN = 8          # chừa mép để không hiện thanh cuộn
MAX_ZOOM = 3.0
STEP = 0.05         # làm tròn tỉ lệ để bộ nhớ đệm ảnh không phình khi kéo thanh chia


class PreviewMixin:
    def preview_scale(self, pw, ph):
        """Tỉ lệ để cả trang (rộng x cao) vừa trong vùng nhìn của khung xem trước."""
        vp = self.preview_scroll.viewport()
        aw, ah = max(vp.width() - MARGIN, 50), max(vp.height() - MARGIN, 50)
        scale = min(aw / pw, ah / ph, MAX_ZOOM)
        return max(int(scale / STEP), 1) * STEP

    def update_preview(self):
        self.update_status()
        items = self.list.selectedItems()
        if not items:
            return
        e = items[-1].data(Qt.UserRole)
        pw, ph = displayed_size(self.docs, e)
        self.preview.setPixmap(self.render_entry(e, self.preview_scale(pw, ph)))

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if self.list.selectedItems():
            self.preview_timer.start()
