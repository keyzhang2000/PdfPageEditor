"""Đổi ngôn ngữ giao diện (đổi ngay, không cần khởi động lại)."""
from PySide6.QtGui import QAction, QActionGroup, QKeySequence
from PySide6.QtWidgets import QToolBar

from ..i18n import LANGUAGES, current_language, set_language, tr


class LanguageMixin:
    def build_language_menu(self, menubar):
        menu = menubar.addMenu(tr("menu.language"))
        group = QActionGroup(self)
        for code, (name, _) in LANGUAGES.items():
            a = QAction(name, self)
            a.setCheckable(True)
            a.setChecked(code == current_language())
            a.triggered.connect(lambda _checked=False, c=code: self.change_language(c))
            group.addAction(a)
            menu.addAction(a)
            self._actions.append(a)

    def change_language(self, code):
        if code == current_language():
            return
        set_language(code)
        self.retranslate()

    def retranslate(self):
        """Dựng lại menu / thanh công cụ và các chữ đang hiển thị theo ngôn ngữ hiện tại."""
        for a in self._actions:
            a.setShortcut(QKeySequence())  # tránh trùng phím tắt với bộ action mới
            a.deleteLater()
        self._actions = []
        self.menuBar().clear()
        for tb in self.findChildren(QToolBar):
            self.removeToolBar(tb)
            tb.setParent(None)  # gỡ khỏi cửa sổ ngay, đối tượng được xóa sau
            tb.deleteLater()
        self.build_actions()
        if not self.docs:
            self.preview.setText(tr("preview.empty"))
        self.update_status()
