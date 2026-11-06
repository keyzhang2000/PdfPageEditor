"""Cửa sổ chính: chỉ ghép các chức năng (frontend/features/) lại với nhau."""
from collections import deque

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QSplitter, QToolButton, QVBoxLayout, QWidget

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
from .features.tabs import TabsMixin
from .features.thumbnails import ThumbnailMixin
from .features.ui_setup import UiSetupMixin
from .i18n import load_saved_language, tr
from .icons import icon
from .tab_bar import TabBar
from .page_list import PageList
from .preview_view import PreviewScroll


class MainWindow(
    UiSetupMixin, LanguageMixin, PageModelMixin, HistoryMixin, ThumbnailMixin, PreviewMixin,
    TabsMixin, FileOpenMixin, FileSaveMixin, ExtractMixin, FileDropMixin,
    PageDeleteMixin, PageInsertMixin, PageClipboardMixin, PageMoveMixin, PageRotateMixin,
    QMainWindow,
):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Page Editor")
        self.resize(1200, 760)
        self.setAcceptDrops(True)

        self._tab_states = {}   # id tab -> trạng thái đã cất của tab (tab đang mở thì trạng thái nằm ở các thuộc tính dưới)
        self._tab_id = None
        self._next_tab_id = 0
        self._switching = False
        self.docs = []          # danh sách fitz.Document nguồn
        self.path = None        # file đang mở
        self.dirty = False
        self.thumb_scale = 0.25
        self.preview_zoom = 1.0   # 1.0 = vừa khung
        self.undo_stack = []
        self.redo_stack = []
        self.thumb_cache = {}
        self.thumb_cache_bytes = 0
        self.pending = deque()  # item chờ render thumbnail
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
        self.preview_scroll = PreviewScroll()
        self.preview_scroll.zoom_requested.connect(self.zoom_preview)
        self.preview_scroll.zoom_reset.connect(self.reset_preview_zoom)
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setWidget(self.preview)

        split = QSplitter()
        split.addWidget(self.list)
        split.addWidget(self.preview_scroll)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        self.tabbar = TabBar()
        self.tabbar.currentChanged.connect(self.on_tab_changed)
        self.tabbar.close_requested.connect(self.close_tab)
        self.tab_plus = QToolButton()        # "+" cạnh tab cuối: mở tab Trang chủ mới
        self.tab_plus.setObjectName("tabplus")
        self.tab_plus.setIcon(icon("plus"))
        self.tab_plus.setIconSize(QSize(14, 14))
        self.tab_plus.clicked.connect(self.new_tab)
        self.tab_strip = QWidget()
        self.tab_strip.setObjectName("tabstrip")
        strip = QHBoxLayout(self.tab_strip)
        strip.setContentsMargins(8, 0, 8, 0)
        strip.setSpacing(2)
        strip.addWidget(self.tabbar)
        strip.addWidget(self.tab_plus)
        strip.addStretch(1)
        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.tab_strip)
        lay.addWidget(split, 1)
        self.setCentralWidget(central)
        split.splitterMoved.connect(lambda *_: self.preview_timer.start())   # kéo thanh chia → vẽ lại vừa khung

        self.zoom_timer = QTimer(self)       # gộp nhiều nấc lăn chuột thành một lần vẽ lại
        self.zoom_timer.setSingleShot(True)
        self.zoom_timer.setInterval(30)
        self.zoom_timer.timeout.connect(self._apply_zoom)
        self._zoom_anchor = None

        self.preview_timer = QTimer(self)    # gộp nhiều lần đổi kích thước thành một lần vẽ lại
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(60)
        self.preview_timer.timeout.connect(self.update_preview)

        self.render_timer = QTimer(self)
        self.render_timer.setInterval(5)
        self.render_timer.timeout.connect(self.render_next)

        self.build_actions()
        self._init_home_tab()
        self.update_status()
