"""Dựng PDF mới từ danh sách trang (nguồn, số trang, góc xoay)."""
import pymupdf as fitz


def build_pdf(docs, entries):
    """Dựng PDF mới; gộp các trang liên tiếp cùng nguồn thành một lần insert_pdf (nhanh hơn nhiều)."""
    out = fitz.open()
    i, n = 0, len(entries)
    while i < n:
        e = entries[i]
        if e["src"] < 0:
            out.new_page(width=e["size"][0], height=e["size"][1])
            j = i + 1
        else:
            j = i + 1
            while (j < n and entries[j]["src"] == e["src"]
                   and entries[j]["page"] == entries[j - 1]["page"] + 1):
                j += 1
            out.insert_pdf(docs[e["src"]], from_page=e["page"],
                           to_page=entries[j - 1]["page"])
        for k in range(i, j):
            if entries[k]["rot"]:
                p = out[len(out) - (j - k)]
                p.set_rotation((p.rotation + entries[k]["rot"]) % 360)
        i = j
    return out
