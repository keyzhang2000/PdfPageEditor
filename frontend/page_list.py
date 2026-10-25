"""Lưới thumbnail: chọn trang và kéo chuột để đổi vị trí."""
from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QAbstractItemView, QApplication, QListView, QListWidget

from . import theme


class PageList(QListWidget):
    """Lưới thumbnail; nhấn giữ chuột trên trang rồi kéo để đổi vị trí (vạch xanh chỉ chỗ thả)."""

    files_dropped = Signal(list, int)   # (đường dẫn PDF, vị trí chèn) khi kéo file từ Explorer vào

    def __init__(self, on_changed):
        super().__init__()
        self._on_changed = on_changed
        self._press_item = None
        self._press_pos = None
        self._dragging = False
        self._cursor_pos = None
        self._drop_row = None
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(False)   # tự xử lý kéo bằng sự kiện chuột
        self.viewport().setAcceptDrops(True)   # nhận file PDF kéo từ Explorer (sự kiện đến viewport)
        self._file_drag = False
        self.empty_text = ""        # chữ gợi ý khi chưa có trang nào
        self.setSpacing(10)
        self.setWordWrap(True)
        self.setUniformItemSizes(False)
        self.setMouseTracking(False)
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setInterval(30)
        self._scroll_timer.timeout.connect(self._autoscroll)

    # ----- tính toán vị trí / di chuyển -----
    def drop_row_at(self, pos):
        """Vị trí chèn (0..count) gần con trỏ nhất."""
        best, best_d = None, None
        for r in range(self.count()):
            c = self.visualItemRect(self.item(r)).center()
            # Ưu tiên cùng hàng: lệch dọc được nhân trọng số lớn.
            d = (pos.x() - c.x()) ** 2 + 4 * (pos.y() - c.y()) ** 2
            if best_d is None or d < best_d:
                best, best_d = r, d
        if best is None:
            return 0
        return best + (1 if pos.x() > self.visualItemRect(self.item(best)).center().x() else 0)

    def move_rows(self, rows, dest):
        rows = sorted(rows)
        if not rows:
            return False
        # Thả ngay tại chỗ cũ thì không làm gì.
        if rows == list(range(rows[0], rows[0] + len(rows))) and rows[0] <= dest <= rows[-1] + 1:
            return False
        self._on_changed("before_drop")
        taken = [self.takeItem(r) for r in reversed(rows)][::-1]
        dest -= sum(1 for r in rows if r < dest)
        for k, it in enumerate(taken):
            self.insertItem(dest + k, it)
            it.setSelected(True)
        self._on_changed("after_drop")
        return True

    # ----- xử lý chuột -----
    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        self._press_item = self.itemAt(ev.position().toPoint()) if ev.button() == Qt.LeftButton else None
        self._press_pos = ev.position().toPoint()

    def mouseMoveEvent(self, ev):
        if not (ev.buttons() & Qt.LeftButton) or self._press_item is None:
            return super().mouseMoveEvent(ev)
        pos = ev.position().toPoint()
        if not self._dragging:
            if (pos - self._press_pos).manhattanLength() < QApplication.startDragDistance():
                return
            self._dragging = True
            self.viewport().setCursor(Qt.ClosedHandCursor)
            self._scroll_timer.start()
        self._cursor_pos = pos
        self._update_drop_row()

    def mouseReleaseEvent(self, ev):
        if self._dragging:
            row = self.drop_row_at(ev.position().toPoint())
            sel = [self.row(i) for i in self.selectedItems()]
            pr = self.row(self._press_item) if self._press_item else -1
            self._end_drag()
            self.move_rows(sel if pr in sel else [pr], row)
            return
        self._press_item = None
        super().mouseReleaseEvent(ev)

    # ----- kéo file PDF từ Explorer vào -----
    @staticmethod
    def pdf_paths(mime):
        return [u.toLocalFile() for u in mime.urls() if u.toLocalFile().lower().endswith(".pdf")]

    def dragEnterEvent(self, ev):
        if ev.mimeData().hasUrls() and self.pdf_paths(ev.mimeData()):
            self._file_drag = True
            self._cursor_pos = ev.position().toPoint()
            self._update_drop_row()
            ev.acceptProposedAction()
        else:
            ev.ignore()

    def dragMoveEvent(self, ev):
        if not self._file_drag:
            return ev.ignore()
        self._cursor_pos = ev.position().toPoint()
        self._update_drop_row()
        self._autoscroll_file_drag()
        ev.acceptProposedAction()

    def dragLeaveEvent(self, ev):
        self._end_file_drag()

    def dropEvent(self, ev):
        paths = self.pdf_paths(ev.mimeData())
        row = self.drop_row_at(ev.position().toPoint())
        self._end_file_drag()
        if paths:
            ev.acceptProposedAction()
            self.files_dropped.emit(paths, row)

    def _end_file_drag(self):
        self._file_drag = False
        self._drop_row = None
        self.viewport().update()

    def _autoscroll_file_drag(self):
        y, h, bar = self._cursor_pos.y(), self.viewport().height(), self.verticalScrollBar()
        edge = 40
        if y < edge:
            bar.setValue(bar.value() - 15)
        elif y > h - edge:
            bar.setValue(bar.value() + 15)

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Escape and self._dragging:
            self._end_drag()
            return
        super().keyPressEvent(ev)

    def _end_drag(self):
        self._dragging = False
        self._press_item = None
        self._drop_row = None
        self._scroll_timer.stop()
        self.viewport().unsetCursor()
        self.viewport().update()

    def _update_drop_row(self):
        row = self.drop_row_at(self._cursor_pos)
        if row != self._drop_row:
            self._drop_row = row
        self.viewport().update()

    def _autoscroll(self):
        if not self._dragging or self._cursor_pos is None:
            return
        y, h, bar = self._cursor_pos.y(), self.viewport().height(), self.verticalScrollBar()
        edge = 40
        if y < edge:
            bar.setValue(bar.value() - max(8, (edge - y) // 2))
        elif y > h - edge:
            bar.setValue(bar.value() + max(8, (y - (h - edge)) // 2))
        else:
            return
        self._update_drop_row()

    def _paint_empty_hint(self):
        c = theme.colors()
        p = QPainter(self.viewport())
        p.setRenderHint(QPainter.Antialiasing)
        active = self._file_drag
        pen = QPen(QColor(c["accent"] if active else c["page_border"]), 2, Qt.DashLine)
        p.setPen(pen)
        p.setBrush(QColor(c["accent_soft"]) if active else Qt.NoBrush)
        box = QRectF(self.viewport().rect()).adjusted(24, 24, -24, -24)
        p.drawRoundedRect(box, 16, 16)
        p.setPen(QColor(c["accent"] if active else c["muted"]))
        p.drawText(box, Qt.AlignCenter | Qt.TextWordWrap, self.empty_text)
        p.end()

    def paintEvent(self, ev):
        super().paintEvent(ev)
        if self.count() == 0 and self.empty_text:
            self._paint_empty_hint()
            return
        if not (self._dragging or self._file_drag):
            return
        p = QPainter(self.viewport())
        r = self._drop_row
        if r is not None and self.count():
            if r < self.count():
                rect = self.visualItemRect(self.item(r))
                x = rect.left() - self.spacing() // 2
            else:
                rect = self.visualItemRect(self.item(self.count() - 1))
                x = rect.right() + self.spacing() // 2
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(theme.colors()["accent"]))
            p.drawRect(x - 1, rect.top(), 3, rect.height())
        if self._dragging and self._press_item is not None and self._cursor_pos is not None:
            pm = self._press_item.icon().pixmap(self.iconSize())
            p.setOpacity(0.6)
            p.drawPixmap(self._cursor_pos - pm.rect().center(), pm)
        p.end()
