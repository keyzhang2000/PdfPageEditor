"""Xuất các trang đã chọn ra file PDF mới."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox

from backend.pdf_io import write_pdf

from ..errors import error_text
from ..i18n import tr


class ExtractMixin:
    def extract_selected(self):
        items = self.sorted_selected()
        if not items:
            return
        path, _ = QFileDialog.getSaveFileName(self, tr("dlg.extract_title"), "", "PDF (*.pdf)")
        if not path:
            return
        try:
            write_pdf(self.docs, [it.data(Qt.UserRole) for it in items], path)
        except Exception as ex:
            QMessageBox.critical(self, tr("dlg.error"), tr("err.extract", err=error_text(ex)))
            return
        self.statusBar().showMessage(tr("msg.extracted", n=len(items)), 4000)
