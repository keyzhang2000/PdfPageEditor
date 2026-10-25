"""Menu, thanh công cụ, phím tắt và menu chuột phải."""
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QLabel, QMenu, QSlider, QToolBar

from ..i18n import tr
from ..icons import icon


class UiSetupMixin:
    def act(self, key, slot, shortcut=None, tip_key=None, icon_name=None):
        a = QAction(self)
        if icon_name:
            a.setIcon(icon(icon_name))
        a.triggered.connect(slot)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        self._actions.append((a, key, tip_key, shortcut))  # để retranslate() đổi chữ tại chỗ
        self.retranslate_action(a, key, tip_key, shortcut)
        return a

    @staticmethod
    def retranslate_action(a, key, tip_key, shortcut):
        text = tr(key)
        tip = tr(tip_key) if tip_key else text
        if shortcut:   # khi thanh công cụ chỉ còn biểu tượng, tooltip cho biết tên + phím tắt
            tip = f"{tip} ({QKeySequence(shortcut).toString(QKeySequence.NativeText)})"
        a.setText(text)
        a.setToolTip(tip)

    def retranslate_ui(self):
        """Đổi chữ menu / thanh công cụ tại chỗ (không dựng lại, không vẽ lại biểu tượng)."""
        for a, key, tip_key, shortcut in self._actions:
            self.retranslate_action(a, key, tip_key, shortcut)
        for menu, key in self._menus:
            menu.setTitle(tr(key))
        self.toolbar.setWindowTitle(tr("toolbar.main"))
        self.zoom_label.setText(tr("label.zoom"))
        self._toolbar_full_width = None   # chữ đổi thì bề rộng đầy đủ của thanh công cụ cũng đổi
        self.fit_toolbar()

    def add_menu(self, menubar, key):
        menu = menubar.addMenu(tr(key))
        self._menus.append((menu, key))
        return menu

    def build_actions(self):
        """Dựng menu + thanh công cụ một lần; đổi ngôn ngữ dùng retranslate_ui()."""
        self.a_home = self.act("act.home", self.go_home, "Alt+Home", icon_name="home")
        self.a_open = self.act("act.open", self.open_file, "Ctrl+O", icon_name="open")
        self.a_saveas = self.act("act.saveas", self.save_as, "Ctrl+S", icon_name="saveas")
        self.a_delete = self.act("act.delete", self.delete_selected, "Delete", icon_name="delete")
        self.a_ins_pdf = self.act("act.ins_pdf_after", lambda: self.insert_pdf(after=True), "Ctrl+I",
                                  "tip.ins_pdf", icon_name="ins_pdf")
        self.a_ins_pdf_b = self.act("act.ins_pdf_before", lambda: self.insert_pdf(after=False), icon_name="ins_pdf")
        self.a_ins_blank = self.act("act.ins_blank_after", lambda: self.insert_blank(after=True), "Ctrl+B", icon_name="ins_blank")
        self.a_ins_blank_b = self.act("act.ins_blank_before", lambda: self.insert_blank(after=False), icon_name="ins_blank")
        self.a_rot_r = self.act("act.rot_r", lambda: self.rotate(90), "Ctrl+R", icon_name="rot_r")
        self.a_rot_l = self.act("act.rot_l", lambda: self.rotate(-90), "Ctrl+L", icon_name="rot_l")
        self.a_move_l = self.act("act.move_l", lambda: self.shift_selected(-1), "Alt+Left",
                                 "tip.move_l", icon_name="move_l")
        self.a_move_r = self.act("act.move_r", lambda: self.shift_selected(1), "Alt+Right",
                                 "tip.move_r", icon_name="move_r")
        self.a_move_to = self.act("act.move_to", self.move_to, "Ctrl+G", icon_name="move_to")
        self.a_dup = self.act("act.dup", self.duplicate, "Ctrl+D", icon_name="dup")
        self.a_extract = self.act("act.extract", self.extract_selected, icon_name="extract")
        self.a_undo = self.act("act.undo", self.undo, "Ctrl+Z", icon_name="undo")
        self.a_redo = self.act("act.redo", self.redo, "Ctrl+Y", icon_name="redo")
        self.a_copy = self.act("act.copy", self.copy_pages, "Ctrl+C", icon_name="dup")
        self.a_paste = self.act("act.paste", self.paste_pages, "Ctrl+V", icon_name="paste")
        self.a_all = self.act("act.select_all", self.list.selectAll, "Ctrl+A", icon_name="select_all")

        m = self.menuBar()
        f = self.add_menu(m, "menu.file")
        f.addActions([self.a_home, self.a_open, self.a_saveas])
        f.addSeparator()
        f.addAction(self.act("act.quit", self.close, "Ctrl+Q", icon_name="quit"))
        e = self.add_menu(m, "menu.edit")
        e.addActions([self.a_undo, self.a_redo])
        e.addSeparator()
        e.addActions([self.a_copy, self.a_paste, self.a_all])
        p = self.add_menu(m, "menu.page")
        p.addAction(self.a_delete)
        p.addSeparator()
        p.addActions([self.a_ins_pdf_b, self.a_ins_pdf, self.a_ins_blank_b, self.a_ins_blank, self.a_dup])
        p.addSeparator()
        p.addActions([self.a_move_l, self.a_move_r, self.a_move_to])
        p.addSeparator()
        p.addActions([self.a_rot_l, self.a_rot_r, self.a_extract])
        self.build_language_menu(m)

        tb = QToolBar(tr("toolbar.main"))
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        tb.setIconSize(QSize(20, 20))
        self.addToolBar(tb)
        tb.addActions([self.a_home, self.a_open, self.a_saveas])
        tb.addSeparator()
        # Thanh công cụ chỉ giữ thao tác hay dùng; còn lại có trong menu, chuột phải và phím tắt.
        tb.addActions([self.a_delete, self.a_ins_pdf, self.a_rot_l, self.a_rot_r])
        tb.addSeparator()
        tb.addActions([self.a_undo, self.a_redo])
        tb.addSeparator()
        self.zoom_label = QLabel(tr("label.zoom"))
        tb.addWidget(self.zoom_label)
        s = QSlider(Qt.Horizontal)
        s.setRange(10, 60)
        s.setValue(int(self.thumb_scale * 100))
        s.setFixedWidth(140)
        s.valueChanged.connect(self.set_zoom)
        tb.addWidget(s)
        self.toolbar = tb
        self._toolbar_full_width = None   # bề rộng khi có đủ chữ; tính lại sau mỗi lần dựng
        self.fit_toolbar()

    def fit_toolbar(self):
        """Cửa sổ hẹp thì bỏ chữ, chỉ giữ biểu tượng để các nút không bị gom vào mục » ."""
        tb = self.toolbar
        if self._toolbar_full_width is None:
            tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self._toolbar_full_width = tb.sizeHint().width()
        wide = self.width() >= self._toolbar_full_width
        tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon if wide else Qt.ToolButtonIconOnly)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if getattr(self, "toolbar", None) is not None:
            self.fit_toolbar()

    def context_menu(self, pos):
        menu = QMenu(self)
        menu.addActions([self.a_copy, self.a_paste, self.a_delete, self.a_dup, self.a_rot_l, self.a_rot_r])
        menu.addSeparator()
        menu.addActions([self.a_move_l, self.a_move_r, self.a_move_to])
        menu.addSeparator()
        menu.addActions([self.a_ins_pdf_b, self.a_ins_pdf, self.a_ins_blank_b, self.a_ins_blank])
        menu.exec(self.list.mapToGlobal(pos))
