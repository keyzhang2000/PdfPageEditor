"""Khung xem trước trang đang chọn: tự co giãn vừa khít khung theo kích thước thực tế."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from backend.entries import displayed_size

MARGIN = 8          # chừa mép để không hiện thanh cuộn
MAX_ZOOM = 3.0
MAX_SCALE = 5.0     # trần tỉ lệ vẽ (tránh ảnh quá lớn tốn bộ nhớ)
ZOOM_FACTOR = 1.25  # mỗi nấc thu phóng
ZOOM_MAX = 8.0      # bội số tối đa so với mức vừa khung
STEP = 0.05         # làm tròn tỉ lệ để bộ nhớ đệm ảnh không phình khi kéo thanh chia


class PreviewMixin:
    def preview_scale(self, pw, ph):
        """Tỉ lệ để cả trang (rộng x cao) vừa trong vùng nhìn của khung xem trước."""
        vp = self.preview_scroll.maximumViewportSize()   # kích thước khi chưa có thanh cuộn, để mức vừa khung không đổi khi phóng
        aw, ah = max(vp.width() - MARGIN, 50), max(vp.height() - MARGIN, 50)
        scale = min(aw / pw, ah / ph, MAX_ZOOM)
        scale = max(int(scale / STEP), 1) * STEP
        return min(scale * self.preview_zoom, MAX_SCALE)

    def zoom_preview(self, direction, anchor=None):
        """Phóng/thu một nấc quanh điểm `anchor` (tọa độ khung nhìn; mặc định giữa khung).
        Từ lăn chuột: gộp các nấc liên tiếp thành một lần vẽ lại để không bị giật."""
        self.preview_zoom = min(max(round(self.preview_zoom * (ZOOM_FACTOR if direction > 0 else 1 / ZOOM_FACTOR), 4), 1.0), ZOOM_MAX)
        if anchor is None:
            self.update_preview()
        else:
            self._zoom_anchor = anchor
            self.zoom_timer.start()

    def reset_preview_zoom(self):
        self.preview_zoom = 1.0
        self.update_preview()

    def _apply_zoom(self):
        self.update_preview(self._zoom_anchor)

    def update_preview(self, anchor=None):
        self.update_status()
        items = self.list.selectedItems()
        if not items:
            return
        e = items[-1].data(Qt.UserRole)
        pw, ph = displayed_size(self.docs, e)
        sc = self.preview_scroll
        hb, vb, lab = sc.horizontalScrollBar(), sc.verticalScrollBar(), self.preview
        vp = sc.viewport()
        ax, ay = (anchor.x(), anchor.y()) if anchor is not None else (vp.width() / 2, vp.height() / 2)
        # Điểm nội dung dưới `anchor` (tỉ lệ 0..1) phải giữ nguyên chỗ sau khi đổi kích thước.
        fx = min(max((ax - lab.x()) / max(lab.width(), 1), 0), 1)
        fy = min(max((ay - lab.y()) / max(lab.height(), 1), 0), 1)
        lab.setPixmap(self.render_entry(e, self.preview_scale(pw, ph)))
        lab.adjustSize()
        sc.widget().updateGeometry()
        QApplication.sendPostedEvents(sc, 0)
        hb.setValue(int(fx * lab.width() - ax))
        vb.setValue(int(fy * lab.height() - ay))

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if self.list.selectedItems():
            self.preview_timer.start()
