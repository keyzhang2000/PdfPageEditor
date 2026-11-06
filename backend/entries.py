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
    """Vị trí chèn (trước khi gỡ các trang) để trang chọn đầu tiên nằm ở vị trí `pos` (1..count).

    O(count + len(rows)) bằng con trỏ quét dần trên `rows` đã sắp xếp,
    thay vì quét lại toàn bộ `rows` cho mỗi `d` (O(count * len(rows)))."""
    final = pos - 1
    rows = sorted(rows)
    removed, r = 0, 0
    for d in range(count + 1):
        while r < len(rows) and rows[r] < d:
            r += 1
            removed += 1
        if d - removed == final:
            return d
    raise ValueError("vị trí không hợp lệ")
