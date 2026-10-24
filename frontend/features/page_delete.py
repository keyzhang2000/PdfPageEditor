"""Xóa trang."""
from PySide6.QtWidgets import QMessageBox

from ..i18n import tr


class PageDeleteMixin:
    def delete_selected(self):
        rows = sorted((self.list.row(i) for i in self.list.selectedItems()), reverse=True)
        if not rows:
            return
        if len(rows) == self.list.count():
            QMessageBox.information(self, tr("dlg.cannot_delete_title"), tr("dlg.cannot_delete_text"))
            return
        self.push_undo()
        self.list.setUpdatesEnabled(False)
        self.list.blockSignals(True)
        for r in rows:
            self.list.takeItem(r)
        self.list.blockSignals(False)
        self.renumber()
        self.list.setUpdatesEnabled(True)
        if self.list.count():
            self.list.setCurrentRow(min(rows[-1], self.list.count() - 1))
