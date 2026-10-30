"""Khung xem trước: Ctrl+lăn chuột để thu phóng, kéo chuột (trái hoặc nhấn giữ con lăn) để di chuyển khi đã phóng, nhấp đúp để vừa khung."""
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QScrollArea


class PreviewScroll(QScrollArea):
    zoom_requested = Signal(int, QPoint)   # (+1 phóng to / -1 thu nhỏ, điểm con trỏ trong khung nhìn)
    zoom_reset = Signal()

    def __init__(self):
        super().__init__()
        self._pan_from = None
        self._wheel_acc = 0

    def wheelEvent(self, ev):
        if ev.modifiers() & Qt.ControlModifier:
            # Cộng dồn: chuột thường 120/nấc, touchpad gửi nhiều sự kiện nhỏ → vẫn đúng một nấc cho mỗi 120.
            self._wheel_acc += ev.angleDelta().y()
            steps = int(self._wheel_acc / 120)
            self._wheel_acc -= steps * 120
            for _ in range(abs(steps)):
                self.zoom_requested.emit(1 if steps > 0 else -1, ev.position().toPoint())
            ev.accept()
        else:
            super().wheelEvent(ev)

    def _can_pan(self):
        return self.horizontalScrollBar().maximum() > 0 or self.verticalScrollBar().maximum() > 0

    def mousePressEvent(self, ev):
        if ev.button() in (Qt.LeftButton, Qt.MiddleButton) and self._can_pan():
            self._pan_from = ev.position().toPoint()
            self.viewport().setCursor(Qt.ClosedHandCursor)
            ev.accept()   # phải nhận sự kiện thì mới được giao các lần di chuyển chuột tiếp theo
            return
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._pan_from is not None:
            if not ev.buttons() & (Qt.LeftButton | Qt.MiddleButton):   # nhả chuột ngoài cửa sổ → thôi kéo
                self._end_pan()
                return
            d = ev.position().toPoint() - self._pan_from
            self._pan_from = ev.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - d.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - d.y())
            ev.accept()
            return
        super().mouseMoveEvent(ev)

    def _end_pan(self):
        self._pan_from = None
        self.viewport().unsetCursor()

    def mouseReleaseEvent(self, ev):
        self._end_pan()
        super().mouseReleaseEvent(ev)

    def mouseDoubleClickEvent(self, ev):
        self.zoom_reset.emit()
