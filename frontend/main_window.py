"""Cửa sổ chính: chỉ ghép các chức năng (frontend/features/) lại với nhau."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QMainWindow, QScrollArea, QSplitter

from .features.language import LanguageMixin
from .features.extract import ExtractMixin
from .features.file_drop import FileDropMixin
from .features.file_open import FileOpenMixin
from .features.file_save import FileSaveMixin
from .features.history import HistoryMixin
from .features.page_clipboard import PageClipboardMixin
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
    PageDeleteMixin, PageInsertMixin, PageClipboardMixin, PageMoveMixin, PageRotateMixin,
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
        self._actions = []      # (QAction, khóa, khóa tooltip, phím tắt) để đổi chữ tại chỗ
        self.page_clipboard = []   # entry đã sao chép (Ctrl+C)
        self._menus = []        # (QMenu, khóa tiêu đề)
        load_saved_language()

        self.list = PageList(self._list_event)
        self.list.empty_text = tr("list.empty")
        self.list.files_dropped.connect(self.drop_pdfs)
        self.list.itemSelectionChanged.connect(self.update_preview)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.context_menu)

        self.preview = QLabel(tr("preview.empty"))
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("color: palette(mid); font-size: 14px;")
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setWidget(self.preview)

        split = QSplitter()
        split.addWidget(self.list)
        split.addWidget(self.preview_scroll)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        self.setCentralWidget(split)
        split.splitterMoved.connect(lambda *_: self.preview_timer.start())   # kéo thanh chia → vẽ lại vừa khung

        self.preview_timer = QTimer(self)    # gộp nhiều lần đổi kích thước thành một lần vẽ lại
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(60)
        self.preview_timer.timeout.connect(self.update_preview)

        self.render_timer = QTimer(self)
        self.render_timer.setInterval(5)
        self.render_timer.timeout.connect(self.render_next)

        self.build_actions()
        self.update_status()
