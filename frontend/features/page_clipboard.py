"""Sao chép / dán trang trong app (Ctrl+C / Ctrl+V)."""
import copy

from PySide6.QtCore import Qt


class PageClipboardMixin:
    def copy_pages(self):
        sel = self.sorted_selected()
        if sel:
            self.page_clipboard = [copy.deepcopy(i.data(Qt.UserRole)) for i in sel]

    def paste_pages(self):
        """Dán sau trang đang chọn (không chọn gì thì dán cuối)."""
        if not self.docs or not self.page_clipboard:
            return
        self._insert_entries(copy.deepcopy(self.page_clipboard), self.insertion_row(after=True))

    def clear_page_clipboard(self):
        """Chỉ số nguồn trong clipboard hết hiệu lực khi danh sách tài liệu bị thay."""
        self.page_clipboard = []
