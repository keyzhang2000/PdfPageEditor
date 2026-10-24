"""Mở và ghi file PDF."""
import pymupdf as fitz

from .pdf_builder import build_pdf


class PasswordProtectedError(ValueError):
    """File PDF có mật khẩu."""


def open_pdf(path):
    """Mở PDF; ném PasswordProtectedError nếu file có mật khẩu."""
    doc = fitz.open(path)
    if doc.needs_pass:
        doc.close()
        raise PasswordProtectedError(path)
    return doc


def write_pdf(docs, entries, path):
    """Dựng PDF từ danh sách trang rồi ghi ra `path`."""
    out = build_pdf(docs, entries)
    try:
        out.save(path, garbage=1, deflate=True)
    finally:
        out.close()
