"""Sao chép / dán trang (Ctrl+C / Ctrl+V): dán được cả sang tab khác.

Clipboard không giữ entry {src, ...} thô vì `src` chỉ là chỉ số trong self.docs của
tab đang mở — vô nghĩa ở tab khác. Thay vào đó giữ đường dẫn file nguồn (fitz.Document.name);
lúc dán, mở file đó trong tab đích nếu tab đích chưa có (hoặc dùng lại nếu đã mở).
"""
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from backend.pdf_io import open_pdf

from ..errors import error_text
from ..i18n import tr


def _norm(path):
    return os.path.normcase(os.path.abspath(path))


class PageClipboardMixin:
    def copy_pages(self):
        sel = self.sorted_selected()
        if not sel:
            return
        items = []
        for it in sel:
            e = it.data(Qt.UserRole)
            if e["src"] < 0:
                items.append({"path": None, "page": 0, "rot": e["rot"], "size": e["size"]})
            else:
                items.append({"path": _norm(self.docs[e["src"]].name), "page": e["page"],
                              "rot": e["rot"], "size": None})
        self.page_clipboard = items

    def paste_pages(self):
        """Dán sau trang đang chọn (không chọn gì thì dán cuối); mở lại file nguồn nếu cần."""
        if not self.docs or not self.page_clipboard:
            return
        path_to_src = {_norm(d.name): i for i, d in enumerate(self.docs)}
        entries, failed = [], []
        for item in self.page_clipboard:
            if item["path"] is None:
                entries.append({"src": -1, "page": 0, "rot": item["rot"], "size": item["size"]})
                continue
            src = path_to_src.get(item["path"])
            if src is None:
                try:
                    d = open_pdf(item["path"])
                except Exception as ex:
                    failed.append((item["path"], ex))
                    continue
                self.docs.append(d)
                src = len(self.docs) - 1
                path_to_src[item["path"]] = src
            entries.append({"src": src, "page": item["page"], "rot": item["rot"], "size": None})
        if failed:
            names = ", ".join(os.path.basename(p) for p, _ in failed)
            QMessageBox.warning(self, tr("dlg.error"), tr("err.paste", err=error_text(failed[0][1]), name=names))
        if entries:
            self._insert_entries(entries, self.insertion_row(after=True))

    def clear_page_clipboard(self):
        self.page_clipboard = []

    def invalidate_clipboard_path(self, path):
        """Nội dung file tại `path` sắp bị ghi đè (Lưu): bỏ các mục clipboard trỏ tới trang trong file đó."""
        if not self.page_clipboard:
            return
        p = _norm(path)
        self.page_clipboard = [c for c in self.page_clipboard if c["path"] != p]
