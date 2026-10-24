"""Mô hình trang: mỗi trang là dict {src, page, rot, size}.

src  : chỉ số PDF nguồn trong danh sách docs, hoặc -1 nếu là trang trống
page : số trang (từ 0) trong PDF nguồn
rot  : góc xoay thêm (0/90/180/270)
size : (rộng, cao) cho trang trống, None với trang từ PDF
"""
import copy

from .constants import BLANK_SIZE


def pdf_entries(src, count):
    """Các trang 0..count-1 của PDF nguồn số `src`."""
    return [{"src": src, "page": i, "rot": 0, "size": None} for i in range(count)]


def blank_entry(size=BLANK_SIZE):
    return {"src": -1, "page": 0, "rot": 0, "size": tuple(size)}


def page_size(docs, entry):
    """Kích thước gốc (rộng, cao) của trang, chưa tính xoay."""
    if entry["src"] < 0:
        return entry["size"]
    r = docs[entry["src"]][entry["page"]].rect
    return (r.width, r.height)


def displayed_size(docs, entry):
    """Kích thước trang sau khi xoay."""
    w, h = page_size(docs, entry)
    return (h, w) if entry["rot"] % 180 else (w, h)


def rotated(entry, deg):
    e = copy.deepcopy(entry)
    e["rot"] = (e["rot"] + deg) % 360
    return e


def dest_for_position(rows, count, pos):
    """Vị trí chèn (trước khi gỡ các trang) để trang chọn đầu tiên nằm ở vị trí `pos` (1..count)."""
    final = pos - 1
    return next(d for d in range(count + 1) if d - sum(1 for r in rows if r < d) == final)
