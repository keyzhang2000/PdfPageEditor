# PDF Page Editor

App Windows chỉnh sửa trang PDF (xóa, thêm, sắp xếp, xoay) với giao diện thumbnail trực quan.

## Công nghệ
- Python 3.12, PySide6 (giao diện Qt), PyMuPDF (`import pymupdf as fitz`)
- Môi trường ảo: `.venv` (cài từ `requirements.txt`)

## Lệnh thường dùng
- Chạy app: `run.bat` (hoặc `.venv\Scripts\python main.py [file.pdf]`)
- Test (không hiện cửa sổ): `.venv\Scripts\python tests\test_backend.py` và `tests\test_frontend.py`
- Đóng gói .exe: `build_exe.bat` → `dist\PdfPageEditor.exe`

## Cấu trúc (3 thư mục: backend / frontend / tests)
- `main.py`: điểm vào, chỉ tạo `QApplication` + `MainWindow`.
- `backend/` — xử lý PDF thuần, **không import Qt** (test được độc lập):
  - `entries.py`: mô hình trang `{src, page, rot, size}` (`pdf_entries`, `blank_entry`, `page_size`, `displayed_size`, `rotated`, `dest_for_position`).
  - `pdf_builder.py`: `build_pdf` (gộp các trang liên tiếp cùng nguồn thành 1 lần insert).
  - `pdf_io.py`: `open_pdf` (báo lỗi nếu có mật khẩu), `write_pdf`.
  - `naming.py`: `suggest_save_path` → `<tên>_modify_<yyyymmdd>.pdf`.
  - `constants.py`: `BLANK_SIZE`.
- `frontend/` — giao diện PySide6:
  - `main_window.py`: `MainWindow` ghép các mixin chức năng.
  - `page_list.py`: lưới thumbnail + kéo chuột đổi vị trí (tự xử lý sự kiện chuột).
  - `save_worker.py`: luồng nền ghi file.
  - `features/`: **mỗi chức năng một file**, là mixin của `MainWindow`:
    `ui_setup` (menu/toolbar/phím tắt/chuột phải), `page_model`, `history` (undo/redo), `thumbnails`, `preview`,
    `file_open`, `file_save`, `extract`, `file_drop`, `page_delete`, `page_insert`, `page_move`, `page_rotate`,
    `language` (menu Ngôn ngữ, đổi ngay bằng `retranslate()`).
  - `i18n/`: `tr(khóa, **tham_số)`; mỗi ngôn ngữ một file từ điển (`vi.py` gốc/dự phòng, `en.py`, `zh_TW.py`); lựa chọn lưu bằng QSettings.
  - `errors.py`: `error_text(ex)` dịch ngoại lệ backend (vd. PDF có mật khẩu).
- `tests/`: `test_backend.py` (không cần Qt), `test_frontend.py` (luồng chính, kéo chuột, dời trang), `test_i18n.py` (đủ khóa/placeholder, đổi ngôn ngữ trực tiếp; dùng QSettings tạm), `bench.py` (đo tốc độ 500 trang).
- **Chuỗi hiển thị không được viết cứng**: dùng `tr("khóa")` và thêm khóa vào cả 3 file trong `frontend/i18n/` (test_i18n sẽ báo nếu thiếu khóa/placeholder). **Thêm ngôn ngữ mới**: tạo file từ điển mới + thêm vào `LANGUAGES` trong `i18n/__init__.py`.
- Quy tắc: logic PDF/dữ liệu đặt ở `backend/`; `frontend/` chỉ lo giao diện và gọi backend.
- **Thêm chức năng mới**: logic thuần → `backend/`; giao diện → file mixin mới trong `frontend/features/`,
  thêm vào danh sách kế thừa trong `frontend/main_window.py`, thêm action trong `ui_setup.py`.
- Chạy test: `.venv\Scripts\python tests\test_backend.py` và `tests\test_frontend.py` (đặt `PYTHONIOENCODING=utf-8` nếu console báo lỗi mã hóa).

## Nhật ký làm việc
### 2026-10-25
- [x] Chọn stack Python + PySide6 + PyMuPDF, tạo venv và cài thư viện.
- [x] Viết `app.py`: lưới thumbnail (render dần bằng timer), khung xem trước, thanh trượt thu phóng.
- [x] Xóa trang (Delete), chọn nhiều trang, không cho xóa hết trang.
- [x] Chèn trang từ PDF khác (trước/sau vị trí chọn) và chèn trang trống; kéo-thả file PDF vào cửa sổ.
- [x] Kéo-thả thumbnail để đổi thứ tự; nhân đôi, xoay trái/phải, xuất trang đã chọn.
- [x] Hoàn tác/làm lại, menu chuột phải, Lưu/Lưu thành, cảnh báo khi đóng chưa lưu.
- [x] `test_smoke.py` chạy qua (offscreen); đổi `fitz` sang `pymupdf` để hết cảnh báo.
- [x] Thêm `requirements.txt`, `run.bat`, `build_exe.bat`.
- [x] Tối ưu tốc độ (người dùng báo xóa/lưu chậm, treo giao diện):
  - Lưu chạy ở luồng nền (`SaveWorker`), khóa giao diện + con trỏ chờ trong lúc lưu.
  - `build_pdf` gộp các trang liên tiếp cùng nguồn thành 1 lần `insert_pdf` (trước đây insert từng trang); `garbage=1` thay `garbage=3`.
  - Sau khi lưu không nạp lại/render lại thumbnail, chỉ đánh lại chỉ số trang.
  - Xóa trang tắt repaint/signal trong lúc xóa hàng loạt.
  - `bench.py` (500 trang): xóa ~0.04s, lưu ~0.09s.
- [x] Viết lại kéo-thả đổi vị trí trang (`PageList`): vạch xanh chỉ vị trí thả, tự cuộn khi kéo gần mép, kéo nhiều trang cùng lúc, thả tại chỗ cũ thì bỏ qua, hoàn tác được; file PDF kéo từ ngoài vào vẫn do cửa sổ chính xử lý. Thêm `test_drag.py` (logic `drop_row_at`/`move_rows`).
- [x] Thêm cách đổi vị trí khác: Alt+←/→ dời trang đã chọn 1 vị trí, Ctrl+G "Chuyển đến vị trí..." (nhập số trang đích); có trên toolbar, menu Trang và chuột phải.
- [x] Viết lại kéo chuột trong `PageList` bằng sự kiện chuột tự xử lý (không dùng QDrag của Qt, vì không ổn với lưới thumbnail): nhấn giữ + kéo, ảnh mờ bám con trỏ, vạch xanh chỉ vị trí thả, tự cuộn gần mép, Esc để hủy. `test_drag.py` giả lập chuột bằng QTest.
- [x] Thêm nút "Lưu thành..." lên thanh công cụ (đã có sẵn ở menu Tệp, Ctrl+Shift+S). Lưu thành file mới thì app chuyển sang làm việc trên file mới đó.
- [x] "Lưu thành..." gợi ý tên `<tên gốc>_modify_<yyyymmdd>.pdf` (`suggest_save_path`, bỏ đuôi modify cũ để không nối chồng). Dùng `_` thay `*` vì `*` không hợp lệ trong tên file Windows. Test: `test_name.py`.
- [x] Tái cấu trúc: tách `app.py` thành `main.py` + package `pdfeditor/` (mỗi chức năng một file mixin), giữ nguyên hành vi; test và bench vẫn qua, pyflakes sạch. Sửa `build_exe.bat` (dòng `activate` bị hỏng) và đổi `run.bat`/`build_exe.bat` sang `main.py`.
- [x] Tách 3 thư mục: `backend/` (logic PDF thuần, không Qt), `frontend/` (giao diện, `pdfeditor/` cũ được đổi tên), `tests/`. Chuyển logic khỏi các mixin sang backend (`entries`, `pdf_io`, `naming`). Ba file test cũ ở thư mục gốc không còn trên đĩa, nên viết lại gọn thành `test_backend.py` + `test_frontend.py`; tất cả qua, pyflakes sạch, bench 500 trang vẫn xóa ~0.04s / lưu ~0.09s.
- [x] Đa ngôn ngữ: Tiếng Việt / English / 繁體中文, menu "Ngôn ngữ" đổi ngay không cần khởi động lại, nhớ lựa chọn lần sau (QSettings). Đưa toàn bộ chuỗi giao diện/hộp thoại/lỗi sang `tr()`; backend ném `PasswordProtectedError` thay vì chuỗi tiếng Việt. Hộp thoại xác nhận chưa lưu dùng nút Có/Không theo ngôn ngữ đã chọn. `test_i18n.py` qua.

### Chưa làm / ý tưởng
- Chưa thử giao diện thật bằng tay (kéo-thả thumbnail chỉ mới viết, chưa kiểm tra trực quan).
- Chưa build thử .exe; chưa hỗ trợ PDF có mật khẩu.
- Hộp thoại chọn file (QFileDialog) là của Windows nên theo ngôn ngữ hệ thống, chưa theo ngôn ngữ app.
- Ý tưởng: gộp nhiều PDF, tách theo khoảng trang, chèn ảnh thành trang, giao diện tối, icon app.
