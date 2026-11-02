"""Vẽ thumbnail (dần dần bằng timer), có cache và thu phóng."""
from collections import deque

import pymupdf as fitz
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPixmap

from backend.entries import displayed_size, page_size

from .. import theme


CACHE_LIMIT_BYTES = 256 * 1024 * 1024


class ThumbnailMixin:
    def page_size(self, e):
        return page_size(self.docs, e)

    def placeholder(self, e):
        w, h = displayed_size(self.docs, e)
        pm = QPixmap(int(w * self.thumb_scale), int(h * self.thumb_scale))
        pm.fill(QColor(theme.colors()["placeholder"]))
        return pm

    def render_entry(self, e, scale):
        key = (e["src"], e["page"], e["rot"], round(scale, 3))
        if key in self.thumb_cache:
            return self.thumb_cache[key]
        if e["src"] < 0:
            w, h = displayed_size(self.docs, e)
            pm = QPixmap(int(w * scale), int(h * scale))
            pm.fill(Qt.white)
        else:
            page = self.docs[e["src"]][e["page"]]
            mat = fitz.Matrix(scale, scale).prerotate(e["rot"])
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pm = QPixmap.fromImage(img.copy())
        p = QPainter(pm)   # viền mảnh để trang trắng không chìm vào nền
        p.setPen(QColor(theme.colors()["page_border"]))
        p.drawRect(0, 0, pm.width() - 1, pm.height() - 1)
        p.end()
        # Giới hạn theo dung lượng ảnh (ảnh xem trước lớn hơn thumbnail rất nhiều), không chỉ theo số lượng.
        self.thumb_cache_bytes += pm.width() * pm.height() * 4
        if self.thumb_cache_bytes > CACHE_LIMIT_BYTES:
            self.thumb_cache.clear()
            self.thumb_cache_bytes = pm.width() * pm.height() * 4
        self.thumb_cache[key] = pm
        return pm

    def clear_thumb_cache(self):
        self.thumb_cache.clear()
        self.thumb_cache_bytes = 0

    def start_rendering(self):
        self.pending = deque(self.list.item(i) for i in range(self.list.count()))
        self.apply_icon_size()
        self.render_timer.start()

    def apply_icon_size(self):
        # Ô lưới cố định theo trang lớn nhất: kích thước từng item không còn tự tính nên không bị đè lên nhau.
        s = self.icon_size()
        self.list.setIconSize(s)
        grid = QSize(s.width() + 36, s.height() + 56)
        self.list.setGridSize(grid)
        for i in range(self.list.count()):   # nếu không, thẻ lấy cỡ của trang đầu và cắt trang rộng hơn
            self.list.item(i).setSizeHint(grid)

    def icon_size(self):
        mw = mh = 0
        for i in range(self.list.count()):
            w, h = displayed_size(self.docs, self.list.item(i).data(Qt.UserRole))
            mw, mh = max(mw, w), max(mh, h)
        s = self.thumb_scale
        return QSize(max(int(mw * s), 40), max(int(mh * s), 40))

    def render_next(self):
        for _ in range(4):
            if not self.pending:
                self.render_timer.stop()
                return
            it = self.pending.popleft()
            try:
                e = it.data(Qt.UserRole)
            except RuntimeError:  # item đã bị xóa
                continue
            self.set_thumbnail(it, self.render_entry(e, self.thumb_scale))

    def set_thumbnail(self, it, pm):
        # Đặt trang vào ô vuông cố định, canh giữa cả ngang lẫn dọc để các trang khác kích thước thẳng hàng.
        size = self.list.iconSize()
        if pm.width() < size.width() or pm.height() < size.height():
            canvas = QPixmap(max(size.width(), pm.width()), max(size.height(), pm.height()))
            canvas.fill(Qt.transparent)
            p = QPainter(canvas)
            p.drawPixmap((canvas.width() - pm.width()) // 2, (canvas.height() - pm.height()) // 2, pm)
            p.end()
            pm = canvas
        it.setSizeHint(self.list.gridSize())
        ic = QIcon(pm)
        ic.addPixmap(pm, QIcon.Selected)   # không phủ màu xanh lên ảnh khi chọn (đã có nền thẻ)
        it.setIcon(ic)

    def set_zoom(self, v):
        self.thumb_scale = v / 100
        self.start_rendering()
