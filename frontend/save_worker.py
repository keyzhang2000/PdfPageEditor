"""Luồng nền ghi file PDF để giao diện không bị treo."""
from PySide6.QtCore import QThread, Signal

from backend.pdf_io import write_pdf

from .errors import error_text


class SaveWorker(QThread):
    done = Signal(str)  # chuỗi lỗi, rỗng nếu thành công

    def __init__(self, docs, entries, tmp):
        super().__init__()
        self.docs, self.entries, self.tmp = list(docs), entries, tmp

    def run(self):
        try:
            write_pdf(self.docs, self.entries, self.tmp)
            self.done.emit("")
        except Exception as ex:
            self.done.emit(error_text(ex))
