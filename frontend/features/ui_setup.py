"""Menu, thanh công cụ, phím tắt và menu chuột phải."""
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QLabel, QMenu, QSlider, QToolBar

from ..i18n import tr
from ..icons import icon


class UiSetupMixin:
    def act(self, text, slot, shortcut=None, tip=None, icon_name=None):
        a = QAction(text, self)
        if icon_name:
            a.setIcon(icon(icon_name))
        a.triggered.connect(slot)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        if not tip:
            tip = text
        if shortcut:   # khi thanh công cụ chỉ còn biểu tượng, tooltip cho biết tên + phím tắt
            tip = f"{tip} ({QKeySequence(shortcut).toString(QKeySequence.NativeText)})"
        a.setToolTip(tip)
        self._actions.append(a)  # để retranslate() dọn lại khi đổi ngôn ngữ
        return a

    def build_actions(self):
        self.a_open = self.act(tr("act.open"), self.open_file, "Ctrl+O", icon_name="open")
        self.a_save = self.act(tr("act.save"), self.save, "Ctrl+S", icon_name="save")
        self.a_saveas = self.act(tr("act.saveas"), self.save_as, "Ctrl+Shift+S", icon_name="saveas")
        self.a_delete = self.act(tr("act.delete"), self.delete_selected, "Delete", icon_name="delete")
        self.a_ins_pdf = self.act(tr("act.ins_pdf_after"), lambda: self.insert_pdf(after=True), "Ctrl+I",
                                  tr("tip.ins_pdf"), icon_name="ins_pdf")
        self.a_ins_pdf_b = self.act(tr("act.ins_pdf_before"), lambda: self.insert_pdf(after=False), icon_name="ins_pdf")
        self.a_ins_blank = self.act(tr("act.ins_blank_after"), lambda: self.insert_blank(after=True), "Ctrl+B", icon_name="ins_blank")
        self.a_ins_blank_b = self.act(tr("act.ins_blank_before"), lambda: self.insert_blank(after=False), icon_name="ins_blank")
        self.a_rot_r = self.act(tr("act.rot_r"), lambda: self.rotate(90), "Ctrl+R", icon_name="rot_r")
        self.a_rot_l = self.act(tr("act.rot_l"), lambda: self.rotate(-90), "Ctrl+L", icon_name="rot_l")
        self.a_move_l = self.act(tr("act.move_l"), lambda: self.shift_selected(-1), "Alt+Left",
                                 tr("tip.move_l"), icon_name="move_l")
        self.a_move_r = self.act(tr("act.move_r"), lambda: self.shift_selected(1), "Alt+Right",
                                 tr("tip.move_r"), icon_name="move_r")
        self.a_move_to = self.act(tr("act.move_to"), self.move_to, "Ctrl+G", icon_name="move_to")
        self.a_dup = self.act(tr("act.dup"), self.duplicate, "Ctrl+D", icon_name="dup")
        self.a_extract = self.act(tr("act.extract"), self.extract_selected, icon_name="extract")
        self.a_undo = self.act(tr("act.undo"), self.undo, "Ctrl+Z", icon_name="undo")
        self.a_redo = self.act(tr("act.redo"), self.redo, "Ctrl+Y", icon_name="redo")
        self.a_all = self.act(tr("act.select_all"), self.list.selectAll, "Ctrl+A", icon_name="select_all")

        m = self.menuBar()
        f = m.addMenu(tr("menu.file"))
        f.addActions([self.a_open, self.a_save, self.a_saveas])
        f.addSeparator()
        f.addAction(self.act(tr("act.quit"), self.close, "Ctrl+Q", icon_name="quit"))
        e = m.addMenu(tr("menu.edit"))
        e.addActions([self.a_undo, self.a_redo, self.a_all])
        p = m.addMenu(tr("menu.page"))
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
        tb.addActions([self.a_open, self.a_save, self.a_saveas])
        tb.addSeparator()
        # Thanh công cụ chỉ giữ thao tác hay dùng; còn lại có trong menu, chuột phải và phím tắt.
        tb.addActions([self.a_delete, self.a_ins_pdf, self.a_rot_l, self.a_rot_r])
        tb.addSeparator()
        tb.addActions([self.a_undo, self.a_redo])
        tb.addSeparator()
        tb.addWidget(QLabel(tr("label.zoom")))
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
        menu.addActions([self.a_delete, self.a_dup, self.a_rot_l, self.a_rot_r])
        menu.addSeparator()
        menu.addActions([self.a_move_l, self.a_move_r, self.a_move_to])
        menu.addSeparator()
        menu.addActions([self.a_ins_pdf_b, self.a_ins_pdf, self.a_ins_blank_b, self.a_ins_blank])
        menu.exec(self.list.mapToGlobal(pos))
