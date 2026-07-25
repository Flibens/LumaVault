from __future__ import annotations

import argparse
import socket
import threading
import time
import webbrowser
from pathlib import Path

from werkzeug.serving import make_server

from lumavault.app import VaultState, create_app


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


class NativeApi:
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
        js_api=NativeApi(),
        width=1500,
        height=920,
        min_size=(980, 640),
        background_color="#08090b",
    )
    try:
        webview.start(debug=args.debug)
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
