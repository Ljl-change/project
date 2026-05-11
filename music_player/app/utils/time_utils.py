from __future__ import annotations

from PyQt6.QtCore import QTime


def format_milliseconds(milliseconds: int) -> str:
    time_value = QTime(0, 0).addMSecs(max(milliseconds, 0))
    if milliseconds >= 3600 * 1000:
        return time_value.toString("hh:mm:ss")
    return time_value.toString("mm:ss")
