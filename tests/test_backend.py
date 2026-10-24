"""Test backend (không cần Qt): dựng PDF, ghi file, xoay, đặt tên, tính vị trí."""
import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymupdf as fitz

from backend.entries import blank_entry, dest_for_position, pdf_entries, rotated
from backend.naming import suggest_save_path
from backend.pdf_io import open_pdf, write_pdf


def make(path, n, tag):
    doc = fitz.open()
    for i in range(n):
        doc.new_page().insert_text((72, 72), f"{tag}{i + 1}", fontsize=40)
    doc.save(path)
    doc.close()


d = tempfile.mkdtemp()
a, b, out = (os.path.join(d, x) for x in ("a.pdf", "b.pdf", "out.pdf"))
make(a, 5, "A")
make(b, 2, "B")
docs = [open_pdf(a), open_pdf(b)]

# A1 A3 A4 [B1 B2] [trống] A5(xoay 90) — gồm cả trang liên tiếp và không liên tiếp
A, B = pdf_entries(0, 5), pdf_entries(1, 2)
entries = [A[0], A[2], A[3], *B, blank_entry(), rotated(A[4], 90)]
write_pdf(docs, entries, out)
r = fitz.open(out)
texts = [p.get_text().strip() for p in r]
assert texts == ["A1", "A3", "A4", "B1", "B2", "", "A5"], texts
assert [p.rotation for p in r] == [0, 0, 0, 0, 0, 0, 90]

# đặt tên
today = date(2026, 10, 25)
assert suggest_save_path(r"C:\x\bao cao.pdf", today) == r"C:\x\bao cao_modify_20261025.pdf"
assert suggest_save_path(r"C:\x\bao cao_modify_20200101.pdf", today) == r"C:\x\bao cao_modify_20261025.pdf"
assert suggest_save_path(None) == ""

# chuyển đến vị trí: chọn trang 0,1 của 6 trang, đưa tới vị trí 5 -> chỉ số cuối cùng 4
assert dest_for_position([0, 1], 6, 5) == 6
print("backend OK")
