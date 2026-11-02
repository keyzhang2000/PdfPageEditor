"""Thanh tab: nút đóng vẽ bằng biểu tượng của app, bấm chuột giữa để đóng tab."""
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QTabBar, QToolButton

from .icons import icon


class TabBar(QTabBar):
    close_requested = Signal(int)

    def __init__(self):
        super().__init__()
        self.setDocumentMode(True)
        self.setMovable(True)
        self.setExpanding(False)
        self.setDrawBase(False)
        self.setElideMode(Qt.ElideMiddle)
        self.setUsesScrollButtons(True)
        self.setIconSize(QSize(16, 16))

    def add_document(self, text):
        idx = self.addTab(icon("pdffile"), text)
        btn = QToolButton()
        btn.setObjectName("tabclose")
        btn.setIcon(icon("close"))
        btn.setIconSize(QSize(12, 12))
        btn.setCursor(Qt.ArrowCursor)
        btn.clicked.connect(lambda _=False, b=btn: self.close_requested.emit(self._index_of(b)))
        self.setTabButton(idx, QTabBar.RightSide, btn)
        return idx

    def _index_of(self, btn):
        for i in range(self.count()):
            if self.tabButton(i, QTabBar.RightSide) is btn:
                return i
        return -1

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MiddleButton:
            i = self.tabAt(ev.position().toPoint())
            if i >= 0:
                self.close_requested.emit(i)
            return
        super().mouseReleaseEvent(ev)
