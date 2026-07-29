from __future__ import annotations

import argparse
import ctypes
import io
import os
import socket
import struct
import threading
import time
import webbrowser
from pathlib import Path

from werkzeug.serving import make_server
from PIL import Image, ImageOps

from lumavault.app import VaultState, create_app


ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
WCA_ACCENT_POLICY = 19
DWMWA_SYSTEMBACKDROP_TYPE = 38
DWMSBT_TRANSIENTWINDOW = 3


def apply_windows_acrylic(window=None) -> bool:
    """Expose the DWM acrylic backdrop through the transparent WebView client."""
    if os.name != "nt":
        return False

    from ctypes import wintypes

    class AccentPolicy(ctypes.Structure):
        _fields_ = [
            ("AccentState", ctypes.c_int),
            ("AccentFlags", ctypes.c_int),
            ("GradientColor", ctypes.c_uint),
            ("AnimationId", ctypes.c_int),
        ]

    class WindowCompositionAttributeData(ctypes.Structure):
        _fields_ = [
            ("Attribute", ctypes.c_int),
            ("Data", ctypes.c_void_p),
            ("SizeOfData", ctypes.c_size_t),
        ]

    class Margins(ctypes.Structure):
        _fields_ = [
            ("cxLeftWidth", ctypes.c_int),
            ("cxRightWidth", ctypes.c_int),
            ("cyTopHeight", ctypes.c_int),
            ("cyBottomHeight", ctypes.c_int),
        ]

    user32 = ctypes.windll.user32
    target_pid = os.getpid()
    hwnd = None
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    @callback_type
    def find_window(candidate, _lparam):
        nonlocal hwnd
        process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(candidate, ctypes.byref(process_id))
        if process_id.value != target_pid:
            return True
        length = user32.GetWindowTextLengthW(candidate)
        if length:
            title = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(candidate, title, length + 1)
            if title.value == "LumaVault":
                hwnd = candidate
                return False
        return True

    for _ in range(100):
        user32.EnumWindows(find_window, 0)
        if hwnd:
            break
        time.sleep(0.05)
    if not hwnd:
        return False

    try:
        # WebView2 is transparent, but WinForms otherwise paints an opaque client
        # surface over DWM. Extend the compositor frame across the whole client and
        # keep both native backing surfaces transparent/black for DWM glass.
        if window is not None and getattr(window, "native", None) is not None:
            from System import Action
            from System.Drawing import Color

            form = window.native

            def prepare_native_surface():
                form.BackColor = Color.Black
                browser = getattr(form, "browser", None)
                webview_control = getattr(browser, "webview", None)
                if webview_control is not None:
                    webview_control.DefaultBackgroundColor = Color.Transparent

            if form.InvokeRequired:
                form.Invoke(Action(prepare_native_surface))
            else:
                prepare_native_surface()

        dwmapi = ctypes.windll.dwmapi
        margins = Margins(-1, -1, -1, -1)
        frame_extended = dwmapi.DwmExtendFrameIntoClientArea(
            hwnd, ctypes.byref(margins),
        ) == 0
        backdrop_type = ctypes.c_int(DWMSBT_TRANSIENTWINDOW)
        system_backdrop = dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(backdrop_type),
            ctypes.sizeof(backdrop_type),
        ) == 0
        dark_mode = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode),
        )

        # Windows 10 fallback where the system-backdrop attribute is unavailable.
        accent_enabled = False
        if not system_backdrop:
            policy = AccentPolicy(ACCENT_ENABLE_ACRYLICBLURBEHIND, 2, 0x241C1C1C, 0)
            data = WindowCompositionAttributeData(
                WCA_ACCENT_POLICY,
                ctypes.cast(ctypes.pointer(policy), ctypes.c_void_p),
                ctypes.sizeof(policy),
            )
            accent_enabled = bool(
                user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
            )
        return frame_extended and (system_backdrop or accent_enabled)
    except (AttributeError, OSError):
        return False


def free_port(preferred: int = 38471) -> int:
    for port in range(preferred, preferred + 30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class ServerThread(threading.Thread):
    def __init__(self, app, port: int):
        super().__init__(name="LumaVaultServer", daemon=True)
        self.server = make_server("127.0.0.1", port, app, threaded=True)

    def run(self) -> None:
        self.server.serve_forever()

    def stop(self) -> None:
        self.server.shutdown()


def _image_clipboard_payloads(path: Path) -> tuple[bytes, bytes]:
    """Build a Windows CF_DIB bitmap and CF_HDROP file-list payload."""
    with Image.open(path) as source:
        source.seek(0)
        frame = ImageOps.exif_transpose(source).convert("RGB")
        output = io.BytesIO()
        frame.save(output, format="BMP")
    bitmap = output.getvalue()
    if len(bitmap) < 15 or not bitmap.startswith(b"BM"):
        raise ValueError("Image could not be converted for the clipboard.")

    # CF_DIB starts with BITMAPINFOHEADER; the 14-byte BMP file header is omitted.
    dib = bitmap[14:]
    absolute_path = str(path.resolve())
    dropfiles = struct.pack("<IiiII", 20, 0, 0, 0, 1)
    file_drop = dropfiles + (absolute_path + "\0\0").encode("utf-16-le")
    return dib, file_drop


def _copy_image_to_windows_clipboard(path: Path) -> list[str]:
    if os.name != "nt":
        raise OSError("Copy image is supported by the Windows desktop application.")

    from ctypes import wintypes

    cf_dib = 8
    cf_hdrop = 15
    gmem_moveable = 0x0002
    dib, file_drop = _image_clipboard_payloads(path)
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]

    for _ in range(20):
        if user32.OpenClipboard(None):
            break
        time.sleep(0.01)
    else:
        raise OSError("The Windows clipboard is busy. Try again.")

    copied_formats: list[str] = []
    try:
        if not user32.EmptyClipboard():
            raise OSError("The Windows clipboard could not be cleared.")
        for clipboard_format, name, payload in (
            (cf_dib, "CF_DIB", dib),
            (cf_hdrop, "CF_HDROP", file_drop),
        ):
            handle = kernel32.GlobalAlloc(gmem_moveable, len(payload))
            if not handle:
                continue
            pointer = kernel32.GlobalLock(handle)
            if not pointer:
                kernel32.GlobalFree(handle)
                continue
            ctypes.memmove(pointer, payload, len(payload))
            kernel32.GlobalUnlock(handle)
            if user32.SetClipboardData(clipboard_format, handle):
                copied_formats.append(name)
            else:
                kernel32.GlobalFree(handle)
        if "CF_DIB" not in copied_formats:
            raise OSError("The image bitmap could not be placed on the clipboard.")
        return copied_formats
    finally:
        user32.CloseClipboard()


class NativeApi:
    def __init__(self, state: VaultState):
        self.state = state

    def choose_folder(self):
        try:
            import webview
            if not webview.windows:
                return None
            result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
            if not result:
                return None
            return result[0] if isinstance(result, (tuple, list)) else result
        except Exception:
            return None

    def copy_image(self, source_id: str, relative_path: str):
        path = self.state.resolve_file(source_id, relative_path)
        if path is None or not path.is_file():
            return {"success": False, "error": "Image not found."}
        try:
            formats = _copy_image_to_windows_clipboard(path)
            return {"success": True, "formats": formats}
        except Exception as error:
            message = str(error).strip() or "Image could not be copied."
            return {"success": False, "error": message}


def main() -> int:
    parser = argparse.ArgumentParser(description="LumaVault standalone ComfyUI media browser")
    parser.add_argument("--browser", action="store_true", help="Run in the default web browser instead of a desktop window")
    parser.add_argument("--no-open", action="store_true", help="Do not open the browser (useful for testing)")
    parser.add_argument("--port", type=int, default=0, help="Local server port")
    parser.add_argument("--data-dir", type=Path, help="Override the persistent data directory")
    parser.add_argument("--debug", action="store_true", help="Enable webview developer tools")
    args = parser.parse_args()

    state = VaultState(data_dir=args.data_dir)
    app = create_app(state)
    port = args.port or free_port()
    server = ServerThread(app, port)
    server.start()
    url = f"http://127.0.0.1:{port}"

    if args.browser:
        print(f"LumaVault is running at {url}")
        print(f"Data directory: {state.data_dir}")
        if not args.no_open:
            webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
            return 0

    try:
        import webview
    except ImportError:
        print("pywebview is not installed; opening browser mode instead.")
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
            return 0

    window = webview.create_window(
        "LumaVault",
        url,
        js_api=NativeApi(state),
        width=1500,
        height=920,
        min_size=(980, 640),
        background_color="#08090b",
        transparent=True,
    )
    try:
        webview.start(func=apply_windows_acrylic, args=(window,), debug=args.debug)
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
