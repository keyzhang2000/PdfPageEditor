"""Nhiều file PDF mở cùng lúc, mỗi file một tab (trạng thái đang làm việc nằm ở MainWindow; đổi tab thì cất/nạp)."""
import os

from PySide6.QtWidgets import QMessageBox

from backend.entries import pdf_entries
from backend.pdf_io import open_pdf

from ..errors import error_text
from ..i18n import tr
from ..icons import icon


def _same_file(a, b):
    return bool(a) and bool(b) and os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def _home_state():
    """Trạng thái tab Trang chủ: chưa có file nào, chỉ hiện khung gợi ý mở/kéo-thả."""
    return dict(docs=[], path=None, dirty=False, undo=[], redo=[], entries=[], sel=[])


class TabsMixin:
    # ----- tra cứu -----
    def _tab_index(self, tid):
        for i in range(self.tabbar.count()):
            if self.tabbar.tabData(i) == tid:
                return i
        return -1

    def _all_dirty(self):
        others = (st["dirty"] for tid, st in self._tab_states.items() if tid != self._tab_id)
        return self.dirty or any(others)

    # ----- cất / nạp trạng thái của tab -----
    def _stash(self):
        st = self._tab_states.get(self._tab_id)
        if st is None:
            return
        st.update(docs=self.docs, path=self.path, dirty=self.dirty, undo=self.undo_stack, redo=self.redo_stack,
                  entries=self.snapshot(), sel=[self.list.row(i) for i in self.list.selectedItems()])

    def _activate(self, st):
        self.render_timer.stop()
        self.pending.clear()
        self.docs, self.path, self.dirty = st["docs"], st["path"], st["dirty"]
        self.undo_stack, self.redo_stack = st["undo"], st["redo"]
        self.clear_thumb_cache()          # chỉ số nguồn (src) chỉ có nghĩa trong từng tab
        self.load_snapshot(st["entries"], st["sel"])
        if not self.docs:                 # tab Trang chủ: hiện lại khung gợi ý mở/kéo-thả
            self.preview.clear()
            self.preview.setText(tr("preview.empty"))
        self.update_status()

    # ----- thao tác với tab -----
    def _init_home_tab(self):
        """Gọi một lần lúc khởi động: luôn có sẵn 1 tab Trang chủ."""
        tid = self._next_tab_id
        self._next_tab_id += 1
        self._tab_states[tid] = _home_state()
        idx = self.tabbar.add_document(tr("tab.home"), "home")
        self.tabbar.setTabData(idx, tid)
        self._tab_id = tid

    def new_tab(self):
        """Nút "+": mở tab Trang chủ mới, chưa gắn file nào."""
        self._stash()
        tid = self._next_tab_id
        self._next_tab_id += 1
        st = _home_state()
        self._tab_states[tid] = st
        self._switching = True
        idx = self.tabbar.add_document(tr("tab.home"), "home")
        self.tabbar.setTabData(idx, tid)
        self.tabbar.setCurrentIndex(idx)
        self._switching = False
        self._tab_id = tid
        self._activate(st)

    def _add_tab(self, doc, path):
        st = dict(docs=[doc], path=path, dirty=False, undo=[], redo=[],
                  entries=pdf_entries(0, len(doc)), sel=[])
        if self._tab_id is not None and not self.docs:    # tab hiện tại là Trang chủ: nạp file vào đây luôn
            idx = self._tab_index(self._tab_id)
            self._tab_states[self._tab_id] = st
            self.tabbar.setTabIcon(idx, icon("pdffile"))
            self.tabbar.setTabText(idx, os.path.basename(path))
            self.tabbar.setTabToolTip(idx, path)
            self._activate(st)
            return
        self._stash()
        tid = self._next_tab_id
        self._next_tab_id += 1
        self._tab_states[tid] = st
        self._switching = True
        idx = self.tabbar.add_document(os.path.basename(path))
        self.tabbar.setTabData(idx, tid)
        self.tabbar.setCurrentIndex(idx)
        self._switching = False
        self._tab_id = tid
        self._activate(st)

    def open_pdf_tab(self, path):
        """Mở file trong tab mới (file đã mở sẵn thì chuyển sang tab đó)."""
        for tid, st in self._tab_states.items():
            if _same_file(self.path if tid == self._tab_id else st["path"], path):
                self.tabbar.setCurrentIndex(self._tab_index(tid))
                return
        try:
            doc = open_pdf(path)
        except Exception as ex:
            QMessageBox.critical(self, tr("dlg.error"), tr("err.open", err=error_text(ex)))
            return
        self._add_tab(doc, path)

    def on_tab_changed(self, idx):
        if self._switching or idx < 0:
            return
        tid = self.tabbar.tabData(idx)
        if tid == self._tab_id:        # kéo đổi thứ tự tab cũng phát tín hiệu này
            return
        self._stash()
        self._tab_id = tid
        self._activate(self._tab_states[tid])

    def close_tab(self, idx=None):
        if idx is None:
            idx = self.tabbar.currentIndex()
        if idx < 0:
            return
        tid = self.tabbar.tabData(idx)
        is_cur = tid == self._tab_id
        if is_cur:
            self._stash()
        st = self._tab_states[tid]
        if not st["docs"] and self.tabbar.count() == 1:
            return                          # chỉ còn tab Trang chủ: không có gì để đóng
        if not self.confirm_discard(st["dirty"]):
            return
        for d in st["docs"]:
            d.close()
        if self.tabbar.count() == 1:        # tab cuối cùng: biến thành Trang chủ, luôn giữ ít nhất 1 tab
            home = _home_state()
            self._tab_states[tid] = home
            self.tabbar.setTabIcon(idx, icon("home"))
            self.tabbar.setTabText(idx, tr("tab.home"))
            self.tabbar.setTabToolTip(idx, "")
            self._activate(home)
            return
        del self._tab_states[tid]
        self._switching = True
        self.tabbar.removeTab(idx)
        self._switching = False
        if not is_cur:
            return
        self._tab_id = None
        cur = self.tabbar.currentIndex()
        self._tab_id = self.tabbar.tabData(cur)
        self._activate(self._tab_states[self._tab_id])

    def step_tab(self, delta):
        n = self.tabbar.count()
        if n > 1:
            self.tabbar.setCurrentIndex((self.tabbar.currentIndex() + delta) % n)

    def update_tab_title(self):
        idx = self._tab_index(self._tab_id)
        if idx < 0 or not self.path:
            return
        self.tabbar.setTabText(idx, ("*" if self.dirty else "") + os.path.basename(self.path))
        self.tabbar.setTabToolTip(idx, self.path)
