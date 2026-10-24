"""Dữ liệu trang: mỗi item trong danh sách giữ một dict {src, page, rot, size}."""
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QListWidgetItem

from ..i18n import tr


class PageModelMixin:
    def snapshot(self):
        return [self.list.item(i).data(Qt.UserRole) for i in range(self.list.count())]

    def make_item(self, entry):
        it = QListWidgetItem()
        it.setData(Qt.UserRole, entry)
        it.setTextAlignment(Qt.AlignHCenter)
        it.setIcon(QIcon(self.placeholder(entry)))
        return it

    def renumber(self):
        for i in range(self.list.count()):
            self.list.item(i).setText(str(i + 1))
        self.update_status()

    def sorted_selected(self):
        return sorted(self.list.selectedItems(), key=self.list.row)

    def update_status(self):
        name = os.path.basename(self.path) if self.path else tr("status.no_file")
        n = self.list.count()
        sel = len(self.list.selectedItems())
        self.setWindowTitle(f"{'*' if self.dirty else ''}{name} - PDF Page Editor")
        self.statusBar().showMessage(tr("status.counts", n=n, sel=sel))
