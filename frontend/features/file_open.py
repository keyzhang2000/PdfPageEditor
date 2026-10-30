"""Mở file PDF."""
from PySide6.QtWidgets import QFileDialog, QMessageBox

from backend.entries import pdf_entries
from backend.pdf_io import open_pdf

from ..errors import error_text
from ..i18n import tr


class FileOpenMixin:
    def confirm_discard(self):
        if not self.dirty:
            return True
        box = QMessageBox(QMessageBox.Question, tr("dlg.unsaved_title"), tr("dlg.unsaved_text"), parent=self)
        yes = box.addButton(tr("dlg.yes"), QMessageBox.YesRole)
        box.addButton(tr("dlg.no"), QMessageBox.NoRole)
        box.exec()
        return box.clickedButton() is yes

    def open_file(self):
        if not self.confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, tr("dlg.open_pdf"), "", "PDF (*.pdf)")
        if path:
            self.load_pdf(path)

    def go_home(self):
        """Đóng file hiện tại, quay về màn hình chính (khung gợi ý mở / kéo-thả file)."""
        if not self.docs or not self.confirm_discard():
            return
        self.render_timer.stop()
        self.pending.clear()
        for d in self.docs:
            d.close()
        self.docs = []
        self.path = None
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.clear_thumb_cache()
        self.clear_page_clipboard()
        self.load_snapshot([])
        self.preview.clear()
        self.preview.setText(tr("preview.empty"))
        self.dirty = False
        self.update_status()

    def load_pdf(self, path):
        try:
            doc = open_pdf(path)
        except Exception as ex:
            QMessageBox.critical(self, tr("dlg.error"), tr("err.open", err=error_text(ex)))
            return
        for d in self.docs:
            d.close()
        self.docs = [doc]
        self.path = path
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.clear_thumb_cache()
        self.clear_page_clipboard()
        self.load_snapshot(pdf_entries(0, len(doc)))
        self.dirty = False
        self.update_status()
