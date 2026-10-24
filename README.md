# PDF Page Editor

Ứng dụng Windows để chỉnh sửa trang PDF (xóa, thêm, sắp xếp, xoay) với giao diện thumbnail trực quan.

Viết bằng Python 3.12, [PySide6](https://doc.qt.io/qtforpython-6/) (giao diện Qt) và [PyMuPDF](https://pymupdf.readthedocs.io/) (xử lý PDF).

## Tính năng

- Xem lưới thumbnail các trang và khung xem trước, có thanh trượt thu phóng.
- Chọn nhiều trang; **xóa** (không cho xóa hết trang).
- **Chèn** trang từ PDF khác (trước/sau vị trí chọn) hoặc chèn trang trống; **nhân đôi** trang.
- **Đổi thứ tự**: kéo chuột thumbnail (có vạch xanh chỉ chỗ thả, tự cuộn gần mép, Esc để hủy), `Alt+←/→` dời 1 vị trí, `Ctrl+G` chuyển đến vị trí chỉ định.
- **Xoay** trái/phải; **xuất** các trang đã chọn ra file mới.
- **Kéo-thả file PDF từ File Explorer** vào cửa sổ: thả lên lưới thì chèn đúng vị trí dưới con trỏ, thả chỗ khác thì chèn cuối; chưa mở file nào thì mở file đầu tiên.
- Hoàn tác / làm lại, menu chuột phải, Lưu / Lưu thành (gợi ý tên `<tên>_modify_<yyyymmdd>.pdf`), cảnh báo khi đóng mà chưa lưu.
- Lưu chạy ở luồng nền nên giao diện không bị treo; 500 trang xóa ~0.04s, lưu ~0.09s.
- Đa ngôn ngữ: Tiếng Việt, English, 繁體中文 (đổi ngay từ menu, nhớ lựa chọn lần sau).

Chưa hỗ trợ PDF có mật khẩu (app sẽ báo lỗi khi mở).

## Cài đặt và chạy

Yêu cầu: Windows, Python 3.12.

```bat
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
run.bat
```

Hoặc chạy trực tiếp, có thể kèm file PDF cần mở:

```bat
.venv\Scripts\python main.py [file.pdf]
```

## Đóng gói thành .exe

```bat
build_exe.bat
```

Kết quả: `dist\PdfPageEditor.exe` (một file duy nhất, không hiện cửa sổ console). Script dùng PyInstaller và loại `pymupdf.layout`, `pymupdf4llm`, `onnxruntime` khỏi bản build, vì app không dùng và nếu gói thiếu dữ liệu của chúng thì `.exe` sẽ lỗi khi khởi động.

## Kiểm thử

```bat
.venv\Scripts\python tests\test_backend.py
.venv\Scripts\python tests\test_frontend.py
.venv\Scripts\python tests\test_i18n.py
```

Các test chạy không hiện cửa sổ. Nếu console báo lỗi mã hóa, đặt `PYTHONIOENCODING=utf-8`. `tests\bench.py` đo tốc độ với 500 trang.

## Cấu trúc mã nguồn

```
main.py                 điểm vào: tạo QApplication + MainWindow
backend/                xử lý PDF thuần, không import Qt (test độc lập được)
  entries.py            mô hình trang {src, page, rot, size}
  pdf_builder.py        build_pdf: gộp các trang liên tiếp cùng nguồn thành 1 lần insert
  pdf_io.py             open_pdf (báo lỗi nếu có mật khẩu), write_pdf
  naming.py             suggest_save_path
  constants.py          BLANK_SIZE
frontend/               giao diện PySide6
  main_window.py        MainWindow, ghép các mixin chức năng
  page_list.py          lưới thumbnail, kéo chuột đổi vị trí, nhận file kéo từ Explorer
  save_worker.py        luồng nền ghi file
  errors.py             dịch ngoại lệ backend thành thông báo
  features/             mỗi chức năng một file mixin của MainWindow
  i18n/                 tr(khóa, **tham_số) và từ điển từng ngôn ngữ (vi, en, zh_TW)
tests/                  test_backend, test_frontend, test_i18n, bench
```

Nguyên tắc: logic PDF/dữ liệu nằm ở `backend/`, `frontend/` chỉ lo giao diện và gọi backend. Trang được biểu diễn bằng danh sách entry; file PDF chỉ được dựng lại khi lưu (`build_pdf`).

## Mở rộng

- **Thêm chức năng:** logic thuần vào `backend/`; giao diện là một file mixin mới trong `frontend/features/`, thêm vào danh sách kế thừa của `MainWindow` và thêm action trong `features/ui_setup.py`.
- **Chuỗi hiển thị:** không viết cứng, dùng `tr("khóa")` và thêm khóa vào cả 3 file trong `frontend/i18n/` (`test_i18n.py` sẽ báo nếu thiếu khóa hoặc placeholder).
- **Thêm ngôn ngữ:** tạo file từ điển mới trong `frontend/i18n/` và thêm vào `LANGUAGES` trong `i18n/__init__.py`.

## Hạn chế đã biết

- Hộp thoại chọn file (QFileDialog) theo ngôn ngữ hệ thống, chưa theo ngôn ngữ của app.
- Ý tưởng chưa làm: gộp nhiều PDF, tách theo khoảng trang, chèn ảnh thành trang, giao diện tối, icon app.
