"""Đổi vị trí trang bằng phím (Alt+←/→) và hộp thoại "Chuyển đến vị trí"."""
from PySide6.QtWidgets import QInputDialog, QMessageBox

from backend.entries import dest_for_position

from ..i18n import tr


class PageMoveMixin:
    def shift_selected(self, step):
        rows = sorted(self.list.row(i) for i in self.list.selectedItems())
        if not rows:
            return
        dest = rows[0] - 1 if step < 0 else rows[-1] + 2
        if dest < 0 or dest > self.list.count():
            return
        if self.list.move_rows(rows, dest):
            self.list.scrollToItem(self.list.selectedItems()[0])

    def move_to(self):
        rows = sorted(self.list.row(i) for i in self.list.selectedItems())
        if not rows:
            QMessageBox.information(self, tr("dlg.move_title"), tr("dlg.move_pick_first"))
            return
        n = self.list.count()
        pos, ok = QInputDialog.getInt(self, tr("dlg.move_input_title"),
                                      tr("dlg.move_input_label", n=n),
                                      rows[0] + 1, 1, n)
        if not ok:
            return
        dest = dest_for_position(rows, n, pos)
        if self.list.move_rows(rows, dest):
            self.list.scrollToItem(self.list.selectedItems()[0])
