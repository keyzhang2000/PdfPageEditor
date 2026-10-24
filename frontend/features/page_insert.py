"""Chèn trang (từ PDF khác, trang trống) và nhân đôi trang."""
import copy
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox

from backend.constants import BLANK_SIZE
from backend.entries import blank_entry, pdf_entries
from backend.pdf_io import open_pdf

from ..errors import error_text
from ..i18n import tr


class PageInsertMixin:
    def insertion_row(self, after):
        sel = [self.list.row(i) for i in self.list.selectedItems()]
        if not sel:
            return self.list.count() if after else 0
        return max(sel) + 1 if after else min(sel)

    def _insert_entries(self, entries, row):
        self.push_undo()
        self.list.clearSelection()
        for k, e in enumerate(entries):
            it = self.make_item(e)
            self.list.insertItem(row + k, it)
            it.setSelected(True)
        self.renumber()
        self.pending = [self.list.item(row + k) for k in range(len(entries))]
        self.render_timer.start()
        self.list.scrollToItem(self.list.item(row))

    def insert_pdf(self, after=True, paths=None, row=None):
        if not self.docs:
            return self.open_file()
        if paths is None:
            paths, _ = QFileDialog.getOpenFileNames(self, tr("dlg.pick_insert"), "", "PDF (*.pdf)")
        if row is None:
            row = self.insertion_row(after)
        entries = []
        for p in paths:
            try:
                d = open_pdf(p)
            except Exception as ex:
                QMessageBox.warning(self, tr("dlg.error"),
                                    tr("err.insert", name=os.path.basename(p), err=error_text(ex)))
                continue
            self.docs.append(d)
            idx = len(self.docs) - 1
            entries += pdf_entries(idx, len(d))
        if entries:
            self._insert_entries(entries, row)

    def insert_blank(self, after=True):
        if not self.docs:
            return
        size = BLANK_SIZE
        sel = self.sorted_selected()
        if sel:  # dùng cùng kích thước với trang đang chọn
            size = self.page_size(sel[-1 if after else 0].data(Qt.UserRole))
        self._insert_entries([blank_entry(size)], self.insertion_row(after))

    def duplicate(self):
        sel = self.sorted_selected()
        if not sel:
            return
        row = self.list.row(sel[-1]) + 1
        self._insert_entries([copy.deepcopy(i.data(Qt.UserRole)) for i in sel], row)
