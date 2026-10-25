"""Lưu thành tệp mới (không ghi đè file gốc; ghi ở luồng nền, tên gợi ý có đuôi _modify_<ngày>)."""
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMessageBox, QToolBar,
)

from backend.entries import pdf_entries
from backend.naming import suggest_save_path
from backend.pdf_io import open_pdf

from ..errors import error_text
from ..i18n import tr
from ..save_worker import SaveWorker


class FileSaveMixin:
    def save_as(self):
        if not self.docs:
            return
        path, _ = QFileDialog.getSaveFileName(self, tr("dlg.save_pdf"), self.suggest_save_path(), "PDF (*.pdf)")
        if path:
            self._write(path)

    def suggest_save_path(self):
        return suggest_save_path(self.path)

    def _write(self, path):
        if self.list.count() == 0:
            QMessageBox.warning(self, tr("dlg.error"), tr("err.no_pages"))
            return
        # Ghi file ở luồng nền để giao diện không bị treo.
        self.render_timer.stop()
        self.set_busy(True, tr("msg.saving"))
        self.saver = SaveWorker(self.docs, self.snapshot(), path + ".tmp")
        self.saver.done.connect(lambda err, p=path: self._save_finished(p, err))
        self.saver.start()

    def set_busy(self, busy, msg=""):
        self.centralWidget().setEnabled(not busy)
        for tb in self.findChildren(QToolBar):
            tb.setEnabled(not busy)
        self.menuBar().setEnabled(not busy)
        if busy:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.statusBar().showMessage(msg)
        else:
            QApplication.restoreOverrideCursor()

    def _save_finished(self, path, err):
        self.saver = None
        tmp = path + ".tmp"
        try:
            if err:
                raise RuntimeError(err)
            for d in self.docs:
                d.close()
            self.docs = []
            os.replace(tmp, path)
            doc = open_pdf(path)
        except Exception as ex:
            self.set_busy(False)
            if os.path.exists(tmp):
                os.remove(tmp)
            QMessageBox.critical(self, tr("dlg.error"), tr("err.save", err=error_text(ex)))
            return
        # File đã lưu thành nguồn mới; giữ nguyên thumbnail, chỉ đánh lại chỉ số trang.
        self.docs = [doc]
        self.path = path
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.thumb_cache.clear()
        self.clear_page_clipboard()
        for i, e in enumerate(pdf_entries(0, self.list.count())):
            self.list.item(i).setData(Qt.UserRole, e)
        self.dirty = False
        self.set_busy(False)
        self.update_status()
        self.statusBar().showMessage(tr("msg.saved", path=path), 4000)
