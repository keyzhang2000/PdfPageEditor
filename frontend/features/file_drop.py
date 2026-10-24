"""Kéo-thả file PDF vào cửa sổ và xác nhận khi đóng."""



class FileDropMixin:
    def dragEnterEvent(self, ev):
        if ev.mimeData().hasUrls():
            ev.acceptProposedAction()

    def dropEvent(self, ev):
        paths = [u.toLocalFile() for u in ev.mimeData().urls()
                 if u.toLocalFile().lower().endswith(".pdf")]
        if not paths:
            return
        if not self.docs:
            if self.confirm_discard():
                self.load_pdf(paths[0])
                paths = paths[1:]
        if paths:
            self.insert_pdf(after=True, paths=paths)

    def closeEvent(self, ev):
        if self.confirm_discard():
            ev.accept()
        else:
            ev.ignore()
