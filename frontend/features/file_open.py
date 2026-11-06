"""Mở file PDF."""
from PySide6.QtWidgets import QFileDialog, QMessageBox

from backend.entries import pdf_entries
from backend.pdf_io import open_pdf

from ..errors import error_text
from ..i18n import tr


class FileOpenMixin:
    def confirm_discard(self, dirty=None):
        if dirty is None:
            dirty = self.dirty
        if not dirty:
            return True
        box = QMessageBox(QMessageBox.Question, tr("dlg.unsaved_title"), tr("dlg.unsaved_text"), parent=self)
        yes = box.addButton(tr("dlg.yes"), QMessageBox.YesRole)
        box.addButton(tr("dlg.no"), QMessageBox.NoRole)
        box.exec()
        return box.clickedButton() is yes

    def open_file(self):
        """Mỗi file được chọn mở trong một tab riêng."""
        paths, _ = QFileDialog.getOpenFileNames(self, tr("dlg.open_pdf"), "", "PDF (*.pdf)")
        for path in paths:
            self.open_pdf_tab(path)

    def go_home(self):
        """Đóng tab hiện tại; chỉ còn 1 tab thì tab đó trở lại Trang chủ (khung gợi ý mở / kéo-thả file)."""
        if self.docs:
            self.close_tab()

    def load_pdf(self, path):
        """Nạp file vào tab hiện tại (thay nội dung); chưa có tab nào thì tạo tab đầu tiên."""
        try:
            doc = open_pdf(path)
        except Exception as ex:
            QMessageBox.critical(self, tr("dlg.error"), tr("err.open", err=error_text(ex)))
            return
        if not self.docs:
            self._add_tab(doc, path)
            return
        for d in self.docs:
            d.close()
        self.docs = [doc]
        self.path = path
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.clear_thumb_cache()
        self.load_snapshot(pdf_entries(0, len(doc)))
        self.dirty = False
        self.update_status()
