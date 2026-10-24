"""Chuyển ngoại lệ thành thông báo đã dịch."""
from backend.pdf_io import PasswordProtectedError

from .i18n import tr


def error_text(ex):
    if isinstance(ex, PasswordProtectedError):
        return tr("err.password")
    return str(ex) or tr("err.unknown")
