"""Kéo-thả file PDF từ Explorer vào cửa sổ và xác nhận khi đóng."""
from ..page_list import PageList


class FileDropMixin:
    def dragEnterEvent(self, ev):
        if ev.mimeData().hasUrls() and PageList.pdf_paths(ev.mimeData()):
            ev.acceptProposedAction()

    def dropEvent(self, ev):
        """Thả ngoài lưới thumbnail (vd. khung xem trước, thanh công cụ): chèn vào cuối."""
        self.drop_pdfs(PageList.pdf_paths(ev.mimeData()), None)

    def drop_pdfs(self, paths, row):
        """Chưa mở file nào thì mỗi file mở một tab; còn lại chèn tại `row` (None = cuối danh sách)."""
        if not paths:
            return
        if not self.docs:
            for p in paths:
                self.open_pdf_tab(p)
        else:
            self.insert_pdf(paths=paths, row=self.list.count() if row is None else row)

    def closeEvent(self, ev):
        if self.confirm_discard(self._all_dirty()):
            ev.accept()
        else:
            ev.ignore()
