"""Test giao diện (chạy không hiện cửa sổ): luồng chỉnh sửa chính, kéo chuột, dời trang."""
import os
import sys
import tempfile
import time

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymupdf as fitz
import PySide6.QtWidgets as W
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from frontend.main_window import MainWindow


def make(path, n, tag):
    doc = fitz.open()
    for i in range(n):
        doc.new_page().insert_text((72, 72), f"{tag}{i + 1}", fontsize=40)
    doc.save(path)
    doc.close()


def wait_saved(w):
    for _ in range(100):
        qa.processEvents()
        if w.saver is None:
            return
        time.sleep(0.02)
    raise AssertionError("lưu quá lâu")


d = tempfile.mkdtemp()
a, b = os.path.join(d, "a.pdf"), os.path.join(d, "b.pdf")
make(a, 5, "A")
make(b, 2, "B")
qa = QApplication([])

# ---- luồng chính: xóa, chèn PDF, chèn trang trống, xoay, undo/redo, lưu ----
w = MainWindow()
w.load_pdf(a)
assert w.list.count() == 5
w.list.item(1).setSelected(True)
w.delete_selected()                                    # xóa A2
w.list.clearSelection(); w.list.item(2).setSelected(True)
w.insert_pdf(after=True, paths=[b])                    # sau A4
w.list.clearSelection(); w.list.item(0).setSelected(True)
w.insert_blank(after=False)
w.list.clearSelection(); w.list.item(1).setSelected(True)
w.rotate(90)
w.undo(); w.redo()
w._write(a)
wait_saved(w)
assert not w.dirty and w.docs[0].page_count == 7
r = fitz.open(a)
assert [p.get_text().strip() for p in r] == ["", "A1", "A3", "A4", "B1", "B2", "A5"]
assert r[1].rotation == 90
print("luồng chính OK")

# ---- kéo / dời trang ----
w = MainWindow(); w.resize(900, 600); w.show()
c6 = os.path.join(d, "six.pdf")
make(c6, 6, "P")
w.load_pdf(c6); qa.processEvents()
L = w.list


def order():
    return [L.item(i).data(Qt.UserRole)["page"] + 1 for i in range(L.count())]


def select(*rows):
    L.clearSelection()
    for r in rows:
        L.item(r).setSelected(True)


select(0, 1)
dest = L.drop_row_at(L.visualItemRect(L.item(4)).center() + __import__("PySide6.QtCore").QtCore.QPoint(5, 0))
assert dest == 5, dest
L.move_rows([0, 1], dest)
assert order() == [3, 4, 5, 1, 2, 6], order()
assert not L.move_rows([3, 4], 4)                      # thả tại chỗ cũ
w.undo(); assert order() == [1, 2, 3, 4, 5, 6]

select(2); w.shift_selected(-1); assert order() == [1, 3, 2, 4, 5, 6]
w.shift_selected(1); w.shift_selected(1); assert order() == [1, 2, 4, 3, 5, 6]
select(0, 1)
W.QInputDialog.getInt = staticmethod(lambda *a, **k: (5, True))
w.move_to(); assert order() == [4, 3, 5, 6, 1, 2], order()

# kéo bằng chuột giả lập
vp = L.viewport()
L.clearSelection()
c = lambda r: L.visualItemRect(L.item(r)).center()
src = c(0)
tgt = L.visualItemRect(L.item(3)); dst = tgt.center(); dst.setX(tgt.right() - 3)
before = order()
QTest.mousePress(vp, Qt.LeftButton, Qt.NoModifier, src)
for k in range(1, 11):
    QTest.mouseMove(vp, src + (dst - src) * k / 10)
    qa.processEvents()
assert L._dragging and L._drop_row == 4
QTest.mouseRelease(vp, Qt.LeftButton, Qt.NoModifier, dst)
assert order() == [before[1], before[2], before[3], before[0]] + before[4:], order()
assert not L._dragging

b2 = order()                                           # Esc hủy kéo
QTest.mousePress(vp, Qt.LeftButton, Qt.NoModifier, c(0))
QTest.mouseMove(vp, c(4)); QTest.mouseMove(vp, c(5)); qa.processEvents()
assert L._dragging
QTest.keyClick(L, Qt.Key_Escape)
QTest.mouseRelease(vp, Qt.LeftButton, Qt.NoModifier, c(5))
assert order() == b2 and not L._dragging
QTest.mouseClick(vp, Qt.LeftButton, Qt.NoModifier, c(2))   # click thường không di chuyển
assert order() == b2
print("kéo/dời trang OK")
