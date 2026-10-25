"""Menu, thanh công cụ, phím tắt và menu chuột phải."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QLabel, QMenu, QSlider, QToolBar

from ..i18n import tr


class UiSetupMixin:
    def act(self, text, slot, shortcut=None, tip=None):
        a = QAction(text, self)
        a.triggered.connect(slot)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        if tip:
            a.setToolTip(tip)
        self._actions.append(a)  # để retranslate() dọn lại khi đổi ngôn ngữ
        return a

    def build_actions(self):
        self.a_open = self.act(tr("act.open"), self.open_file, "Ctrl+O")
        self.a_save = self.act(tr("act.save"), self.save, "Ctrl+S")
        self.a_saveas = self.act(tr("act.saveas"), self.save_as, "Ctrl+Shift+S")
        self.a_delete = self.act(tr("act.delete"), self.delete_selected, "Delete")
        self.a_ins_pdf = self.act(tr("act.ins_pdf_after"), lambda: self.insert_pdf(after=True), "Ctrl+I",
                                  tr("tip.ins_pdf"))
        self.a_ins_pdf_b = self.act(tr("act.ins_pdf_before"), lambda: self.insert_pdf(after=False))
        self.a_ins_blank = self.act(tr("act.ins_blank_after"), lambda: self.insert_blank(after=True), "Ctrl+B")
        self.a_ins_blank_b = self.act(tr("act.ins_blank_before"), lambda: self.insert_blank(after=False))
        self.a_rot_r = self.act(tr("act.rot_r"), lambda: self.rotate(90), "Ctrl+R")
        self.a_rot_l = self.act(tr("act.rot_l"), lambda: self.rotate(-90), "Ctrl+L")
        self.a_move_l = self.act(tr("act.move_l"), lambda: self.shift_selected(-1), "Alt+Left",
                                 tr("tip.move_l"))
        self.a_move_r = self.act(tr("act.move_r"), lambda: self.shift_selected(1), "Alt+Right",
                                 tr("tip.move_r"))
        self.a_move_to = self.act(tr("act.move_to"), self.move_to, "Ctrl+G")
        self.a_dup = self.act(tr("act.dup"), self.duplicate, "Ctrl+D")
        self.a_extract = self.act(tr("act.extract"), self.extract_selected)
        self.a_undo = self.act(tr("act.undo"), self.undo, "Ctrl+Z")
        self.a_redo = self.act(tr("act.redo"), self.redo, "Ctrl+Y")
        self.a_all = self.act(tr("act.select_all"), self.list.selectAll, "Ctrl+A")

        m = self.menuBar()
        f = m.addMenu(tr("menu.file"))
        f.addActions([self.a_open, self.a_save, self.a_saveas])
        f.addSeparator()
        f.addAction(self.act(tr("act.quit"), self.close, "Ctrl+Q"))
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
        tb.setToolButtonStyle(Qt.ToolButtonTextOnly)
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

    def context_menu(self, pos):
        menu = QMenu(self)
        menu.addActions([self.a_delete, self.a_dup, self.a_rot_l, self.a_rot_r])
        menu.addSeparator()
        menu.addActions([self.a_move_l, self.a_move_r, self.a_move_to])
        menu.addSeparator()
        menu.addActions([self.a_ins_pdf_b, self.a_ins_pdf, self.a_ins_blank_b, self.a_ins_blank])
        menu.exec(self.list.mapToGlobal(pos))
