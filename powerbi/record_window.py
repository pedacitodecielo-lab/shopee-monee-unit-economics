"""Record only the Power BI Desktop window (PrintWindow), so other windows on top never end up in the video.

usage: python record_window.py <seconds> [fps]   -> video/window_raw.mp4
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time
from pathlib import Path

import imageio_ffmpeg
import numpy as np

user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
user32.SetProcessDPIAware()
OUT = Path(__file__).parent / "video" / "window_raw.mp4"


def find_window():
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        n = user32.GetWindowTextLengthW(hwnd)
        if n and user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            if buf.value.startswith("shopee_monee_unit_economics"):
                found.append(hwnd)
        return True
    user32.EnumWindows(cb, 0)
    if not found:
        sys.exit("Power BI window not found")
    return found[0]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG), ("biPlanes", wt.WORD),
                ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD)]


def grab(hwnd, w, h):
    hdc = user32.GetWindowDC(hwnd)
    mdc = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(mdc, bmp)
    user32.PrintWindow(hwnd, mdc, 2)  # PW_RENDERFULLCONTENT: content even when covered by other windows
    bi = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bi), 0)
    gdi32.DeleteObject(bmp); gdi32.DeleteDC(mdc); user32.ReleaseDC(hwnd, hdc)
    return np.frombuffer(buf, np.uint8).reshape(h, w, 4)[:, :, 2::-1]  # BGRA -> RGB


def cursor_overlay(img, hwnd, rect):
    pt = wt.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    x, y = pt.x - rect.left, pt.y - rect.top
    if 0 <= x < img.shape[1] and 0 <= y < img.shape[0]:  # draw a simple arrow-ish dot (PrintWindow has no cursor)
        y0, y1, x0, x1 = max(0, y - 9), min(img.shape[0], y + 9), max(0, x - 9), min(img.shape[1], x + 9)
        yy, xx = np.ogrid[y0:y1, x0:x1]
        d = (yy - y) ** 2 + (xx - x) ** 2
        img[y0:y1, x0:x1][d <= 81] = (34, 34, 34)
        img[y0:y1, x0:x1][d <= 49] = (255, 255, 255)
    return img


def main():
    secs = float(sys.argv[1]); fps = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    hwnd = find_window()
    rect = wt.RECT(); user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = (rect.right - rect.left) // 2 * 2, (rect.bottom - rect.top) // 2 * 2
    writer = imageio_ffmpeg.write_frames(str(OUT), (w, h), fps=fps, codec="libx264", quality=None,
                                         output_params=["-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p"])
    writer.send(None)
    t0 = time.perf_counter(); n = 0
    while (now := time.perf_counter() - t0) < secs:
        frame = cursor_overlay(np.ascontiguousarray(grab(hwnd, w, h)), hwnd, rect).tobytes()
        while n <= (time.perf_counter() - t0) * fps:  # repeat the frame if a grab took longer than one frame slot
            writer.send(frame); n += 1
    writer.close()
    print(n, "frames", w, "x", h)


if __name__ == "__main__":
    main()
