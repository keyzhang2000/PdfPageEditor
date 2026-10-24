"""Hoàn tác / làm lại (Ctrl+Z / Ctrl+Y)."""
import copy


class HistoryMixin:
    def push_undo(self):
        self.undo_stack.append(copy.deepcopy(self.snapshot()))
        self.redo_stack.clear()
        self.dirty = True

    def _list_event(self, what):
        if what == "before_drop":
            self.push_undo()
        else:
            self.renumber()

    def load_snapshot(self, entries, select_rows=()):
        self.list.blockSignals(True)
        self.list.clear()
        for e in entries:
            self.list.addItem(self.make_item(copy.deepcopy(e)))
        for r in select_rows:
            if 0 <= r < self.list.count():
                self.list.item(r).setSelected(True)
        self.list.blockSignals(False)
        self.renumber()
        self.start_rendering()
        self.update_preview()

    def _restore(self, entries):
        self.load_snapshot(entries)
        self.update_status()

    def undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(copy.deepcopy(self.snapshot()))
        self._restore(self.undo_stack.pop())

    def redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(copy.deepcopy(self.snapshot()))
        self._restore(self.redo_stack.pop())
