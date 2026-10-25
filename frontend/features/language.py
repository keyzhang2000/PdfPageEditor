"""Đổi ngôn ngữ giao diện (đổi ngay, không cần khởi động lại)."""
from PySide6.QtGui import QAction, QActionGroup

from ..i18n import LANGUAGES, current_language, set_language, tr


class LanguageMixin:
    def build_language_menu(self, menubar):
        menu = self.add_menu(menubar, "menu.language")
        group = QActionGroup(self)
        self._lang_actions = {}
        for code, (name, _) in LANGUAGES.items():
            a = QAction(name, self)
            a.setCheckable(True)
            a.setChecked(code == current_language())
            a.triggered.connect(lambda _checked=False, c=code: self.change_language(c))
            group.addAction(a)
            self._lang_actions[code] = a
            menu.addAction(a)

    def change_language(self, code):
        if code == current_language():
            return
        set_language(code)
        self.retranslate()

    def retranslate(self):
        """Đổi chữ đang hiển thị theo ngôn ngữ hiện tại (sửa tại chỗ, không dựng lại giao diện)."""
        self.retranslate_ui()
        self._lang_actions[current_language()].setChecked(True)
        self.list.empty_text = tr("list.empty")
        self.list.viewport().update()
        if not self.docs:
            self.preview.setText(tr("preview.empty"))
        self.update_status()
