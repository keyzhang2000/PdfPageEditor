"""Cửa sổ chính: chỉ ghép các chức năng (frontend/features/) lại với nhau."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QMainWindow, QScrollArea, QSplitter

from .features.language import LanguageMixin
from .features.extract import ExtractMixin
from .features.file_drop import FileDropMixin
from .features.file_open import FileOpenMixin
from .features.file_save import FileSaveMixin
from .features.history import HistoryMixin
from .features.page_delete import PageDeleteMixin
from .features.page_insert import PageInsertMixin
from .features.page_model import PageModelMixin
from .features.page_move import PageMoveMixin
from .features.page_rotate import PageRotateMixin
from .features.preview import PreviewMixin
from .features.thumbnails import ThumbnailMixin
from .features.ui_setup import UiSetupMixin
from .i18n import load_saved_language, tr
from .page_list import PageList


class MainWindow(
    UiSetupMixin, LanguageMixin, PageModelMixin, HistoryMixin, ThumbnailMixin, PreviewMixin,
    FileOpenMixin, FileSaveMixin, ExtractMixin, FileDropMixin,
    PageDeleteMixin, PageInsertMixin, PageMoveMixin, PageRotateMixin,
    QMainWindow,
):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Page Editor")
        self.resize(1200, 760)
        self.setAcceptDrops(True)

        self.docs = []          # danh sách fitz.Document nguồn
        self.path = None        # file đang mở
        self.dirty = False
        self.thumb_scale = 0.25
        self.undo_stack = []
        self.redo_stack = []
        self.thumb_cache = {}
        self.pending = []       # item chờ render thumbnail
        self.saver = None
        self._actions = []      # QAction đang dùng (dọn lại khi đổi ngôn ngữ)
        load_saved_language()

        self.list = PageList(self._list_event)
        self.list.itemSelectionChanged.connect(self.update_preview)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.context_menu)

        self.preview = QLabel(tr("preview.empty"))
        self.preview.setAlignment(Qt.AlignCenter)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.preview)

        split = QSplitter()
        split.addWidget(self.list)
        split.addWidget(scroll)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        self.setCentralWidget(split)

        self.render_timer = QTimer(self)
        self.render_timer.setInterval(5)
        self.render_timer.timeout.connect(self.render_next)

        self.build_actions()
        self.update_status()
