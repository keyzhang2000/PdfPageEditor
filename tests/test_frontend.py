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

from frontend import i18n
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

# ---- sao chép / dán trang ----
w = MainWindow()
w.load_pdf(b)                                          # B1, B2
w.list.item(0).setSelected(True)
w.copy_pages()
w.list.clearSelection(); w.list.item(1).setSelected(True)
w.paste_pages()                                        # dán sau B2
assert w.list.count() == 3 and w.docs[0].page_count == 2
w.paste_pages()                                        # dán tiếp sau bản vừa dán (đang được chọn)
assert w.list.count() == 4
w._write(os.path.join(d, "pasted.pdf")); wait_saved(w)
assert [p.get_text().strip() for p in fitz.open(os.path.join(d, "pasted.pdf"))] == ["B1", "B2", "B1", "B1"]
assert w.page_clipboard == []                          # lưu xong thì chỉ số nguồn đổi → xóa clipboard
print("sao chép/dán OK")

# ---- màn hình chính: đóng file, quay về trạng thái ban đầu ----
w = MainWindow()
w.load_pdf(a)
w.go_home()
assert w.docs == [] and w.path is None and w.list.count() == 0 and not w.dirty
assert w.preview.text() == i18n.tr("preview.empty")
w.go_home()                                            # đã ở màn hình chính: không lỗi
w.load_pdf(a)
assert w.list.count() == 7                             # mở lại bình thường
print("màn hình chính OK")

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

# ----- kéo file PDF từ Explorer: thả vào đúng vị trí dưới con trỏ -----
from PySide6.QtCore import QMimeData, QPoint, QPointF, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent

mime = QMimeData()
mime.setUrls([QUrl.fromLocalFile(b), QUrl.fromLocalFile(os.path.join(d, "x.txt"))])
n0 = L.count()
L.scrollToTop(); qa.processEvents()
pos = L.visualItemRect(L.item(1)).center() - QPoint(10, 0)    # nửa trái trang 2 → chèn tại hàng 1
vp = L.viewport()
en = QDragEnterEvent(pos, Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier)
qa.sendEvent(vp, en)
assert en.isAccepted() and L._file_drag and L._drop_row == 1
qa.sendEvent(vp, QDropEvent(QPointF(pos), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier))
assert L.count() == n0 + 2 and not L._file_drag, L.count()
assert [L.item(r).data(Qt.UserRole)["src"] for r in (1, 2)] == [len(w.docs) - 1] * 2

txt = QMimeData(); txt.setUrls([QUrl.fromLocalFile(os.path.join(d, "x.txt"))])   # không phải PDF → từ chối
en = QDragEnterEvent(pos, Qt.CopyAction, txt, Qt.LeftButton, Qt.NoModifier)
qa.sendEvent(vp, en)
assert not en.isAccepted()
print("kéo file từ Explorer OK")

# ----- khung xem trước vừa khít theo kích thước khung -----
w.show(); qa.processEvents()
L.setCurrentRow(0); L.item(0).setSelected(True); w.update_preview()
vpw = w.preview_scroll.viewport()
pm = w.preview.pixmap()
assert pm.width() <= vpw.width() and pm.height() <= vpw.height(), (pm.size(), vpw.size())
w.resize(500, 400); qa.processEvents(); time.sleep(0.2); qa.processEvents()
pm2 = w.preview.pixmap()
assert pm2.height() <= vpw.height() and pm2.width() < pm.width(), (pm2.size(), vpw.size())
print("xem trước theo kích thước OK")

# ----- thanh công cụ: cửa sổ hẹp thì chỉ còn biểu tượng, không mất nút -----
w.resize(2200, 700); qa.processEvents()
assert w.toolbar.toolButtonStyle() == Qt.ToolButtonTextBesideIcon
w.resize(620, 700); qa.processEvents()
assert w.toolbar.toolButtonStyle() == Qt.ToolButtonIconOnly
w.change_language("en"); w.resize(2200, 700); qa.processEvents()      # đổi ngôn ngữ → tính lại bề rộng
assert w.toolbar.toolButtonStyle() == Qt.ToolButtonTextBesideIcon
w.change_language("vi")
print("thanh công cụ co giãn OK")

# ----- thu phóng khu xem trước -----
qa.processEvents(); time.sleep(0.2); qa.processEvents()
w.reset_preview_zoom(); w.update_preview()
base = w.preview.pixmap().width()
w.zoom_preview(1)
assert w.preview_zoom > 1 and w.preview.pixmap().width() > base, "phóng to xem trước"
w.zoom_preview(-1); w.zoom_preview(-1)
assert w.preview_zoom == 1.0, "không thu nhỏ hơn mức vừa khung"
for _ in range(30):
    w.zoom_preview(1)
assert w.preview_zoom <= 8.0
w.reset_preview_zoom()
assert w.preview.pixmap().width() == base
print("thu phóng xem trước OK")

# ----- nhấn giữ con lăn + kéo để chỉnh vị trí xem -----
from PySide6.QtCore import QEvent, QPoint, QPointF
from PySide6.QtGui import QMouseEvent
w.zoom_preview(1); w.zoom_preview(1); qa.processEvents()
sv = w.preview_scroll.verticalScrollBar(); sv.setValue(0)
vp = w.preview_scroll.viewport()
QTest.mousePress(vp, Qt.MiddleButton, Qt.NoModifier, QPoint(100, 200))
qa.sendEvent(vp, QMouseEvent(QEvent.MouseMove, QPointF(100, 100), QPointF(100, 100), Qt.NoButton, Qt.MiddleButton, Qt.NoModifier))
QTest.mouseRelease(vp, Qt.MiddleButton, Qt.NoModifier, QPoint(100, 100))
assert sv.value() > 0, "kéo con lăn phải cuộn khung xem"
w.reset_preview_zoom()
print("kéo con lăn OK")

# ----- Ctrl+lăn: cộng dồn nấc nhỏ (touchpad), gộp lần vẽ, giữ điểm dưới con trỏ -----
from PySide6.QtGui import QWheelEvent
def wheel(dy, pos):
    qa.sendEvent(w.preview_scroll.viewport(), QWheelEvent(QPointF(pos), QPointF(pos), QPoint(0, 0), QPoint(0, dy),
                                                          Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False))
w.reset_preview_zoom(); qa.processEvents()
for _ in range(4):
    wheel(30, QPoint(50, 50))            # 4 x 30 = một nấc 120
time.sleep(0.1); qa.processEvents()
assert abs(w.preview_zoom - 1.25) < 1e-6, w.preview_zoom
wheel(120, QPoint(50, 50)); wheel(120, QPoint(50, 50))   # hai nấc liền → một lần vẽ
time.sleep(0.1); qa.processEvents()
assert abs(w.preview_zoom - 1.25 ** 3) < 1e-3, w.preview_zoom
lab, sc = w.preview, w.preview_scroll
under = (50 - lab.x()) / lab.width()      # điểm dưới con trỏ vẫn gần (50, 50) của khung nhìn
assert under < 0.25, under
w.reset_preview_zoom()
print("lăn chuột thu phóng OK")
