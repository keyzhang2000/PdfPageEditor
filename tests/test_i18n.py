"""Test đa ngôn ngữ: đủ khóa, đủ placeholder, đổi ngôn ngữ trực tiếp, lưu lựa chọn."""
import os
import re
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile

from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QToolBar

# Cài đặt của test ghi vào thư mục tạm, không đụng cài đặt thật của người dùng.
QSettings.setDefaultFormat(QSettings.IniFormat)
QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, tempfile.mkdtemp())

from frontend import i18n
from frontend.main_window import MainWindow

# 1) mọi ngôn ngữ có đúng các khóa của tiếng Việt, và cùng tập placeholder {..}
base = i18n.LANGUAGES["vi"][1]
ph = lambda s: sorted(re.findall(r"\{(\w+)\}", s))
for code, (_, strings) in i18n.LANGUAGES.items():
    assert set(strings) == set(base), (code, set(strings) ^ set(base))
    for k, v in strings.items():
        assert ph(v) == ph(base[k]), (code, k)
print("từ điển OK:", list(i18n.LANGUAGES))

# 2) tr() và dự phòng
i18n.set_language("en", save=False)
assert i18n.tr("act.open") == "Open"
assert i18n.tr("status.counts", n=3, sel=1) == "3 pages | 1 selected"
assert i18n.tr("khong.ton.tai") == "khong.ton.tai"

# 3) đổi ngôn ngữ trực tiếp trên cửa sổ
qa = QApplication([])
i18n.set_language("vi", save=False)
w = MainWindow()
assert w.menuBar().actions()[0].text() == "Tệp"
before = len(w._actions)

for code, file_menu, open_text in (("en", "File", "Open"), ("zh_TW", "檔案", "開啟"), ("vi", "Tệp", "Mở")):
    w.change_language(code)
    qa.processEvents()
    assert w.menuBar().actions()[0].text() == file_menu, code
    assert w.a_open.text() == open_text
    assert len(w._actions) == before          # không tích tụ action cũ
    assert len(w.findChildren(QToolBar)) == 1  # chỉ một thanh công cụ
    assert w.preview.text() == i18n.tr("preview.empty")
    # không có hai action cùng phím tắt đang hoạt động (sẽ gây "ambiguous shortcut")
    keys = [a.shortcut().toString() for a in w.findChildren(QAction)
            if a.shortcut().toString() and not a.parent() is None and a in w._actions]
    assert len(keys) == len(set(keys)), keys
    checked = [a.text() for a in w.menuBar().actions()[-1].menu().actions() if a.isChecked()]
    assert checked == [i18n.LANGUAGES[code][0]], checked

# 4) lựa chọn được lưu và nạp lại
i18n.set_language("zh_TW")
i18n.set_language("vi", save=False)
i18n.load_saved_language()
assert i18n.current_language() == "zh_TW"
i18n.set_language("vi")  # trả về mặc định
print("đổi ngôn ngữ OK")
