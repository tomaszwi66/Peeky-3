"""Keep Tk windows within the Windows work area at the current DPI."""
import ctypes
from ctypes import wintypes


def work_area(window):
    rect = wintypes.RECT()
    if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
        return rect.left, rect.top, rect.right, rect.bottom
    return 0, 0, window.winfo_screenwidth(), window.winfo_screenheight()


def dialog_bounds(window):
    left, top, right, bottom = work_area(window)
    return max(160, right - left - 48), max(160, bottom - top - 84)


def place_dialog(window, width=0, height=0, min_width=None, min_height=None):
    window.update_idletasks()
    max_w, max_h = dialog_bounds(window)
    w = min(max_w, max(width, window.winfo_reqwidth()))
    h = min(max_h, max(height, window.winfo_reqheight()))
    left, top, right, bottom = work_area(window)
    window.minsize(min(w, min_width or window.winfo_reqwidth()),
                   min(h, min_height or window.winfo_reqheight()))
    window.geometry(f"{w}x{h}+{left + (right-left-w)//2}+{top + (bottom-top-h)//2}")
