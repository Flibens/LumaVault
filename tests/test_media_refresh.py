"""Real browser regressions for recycled and regenerated media (optional Playwright)."""
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image
from werkzeug.serving import make_server
from lumavault.app import VaultState, create_app

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


class ScanRefreshTests(unittest.TestCase):
    def test_scan_started_before_refresh_cannot_repopulate_stale_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            media = root / "media"
            media.mkdir()
            Image.new("RGB", (8, 8), "red").save(media / "old.png")
            state = VaultState(root / "data", migrate_legacy=False)
            state.data["sources"] = [{"id": "test", "name": "Test", "path": str(media), "recursive": False}]
            state.save()
            captured = threading.Event()
            release = threading.Event()
            original = Path.iterdir

            def paused_iterdir(path):
                yield from original(path)
                if path == media:
                    captured.set()
                    release.wait(5)

            with mock.patch.object(Path, "iterdir", paused_iterdir):
                worker = threading.Thread(target=lambda: state.scan("test"))
                worker.start()
                try:
                    self.assertTrue(captured.wait(5))
                    Image.new("RGB", (8, 8), "blue").save(media / "new.png")
                    create_app(state).test_client().post("/api/refresh")
                finally:
                    release.set()
                    worker.join(5)
            self.assertEqual({row["name"] for row in state.scan("test")}, {"old.png", "new.png"})


@unittest.skipUnless(sync_playwright, "Requires Playwright")
class MediaRefreshBrowserTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.media = root / "media"
        self.media.mkdir()
        self.path = self.media / "generated.png"
        Image.new("RGB", (64, 64), "red").save(self.path)
        self.state = VaultState(root / "data", migrate_legacy=False)
        self.state.data["sources"] = [{"id": "test", "name": "Test", "path": str(self.media), "recursive": False}]
        self.state.save()
        self.server = make_server("127.0.0.1", 0, create_app(self.state), threaded=True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(executable_path=os.environ.get("LUMAVAULT_TEST_CHROME"), channel=os.environ.get("LUMAVAULT_TEST_BROWSER_CHANNEL"), headless=True)
        self.page = self.browser.new_page()
        self.page.goto(f"http://127.0.0.1:{self.server.server_port}")
        self.page.wait_for_selector(".media-card img:not(.loading)")

    def tearDown(self):
        self.browser.close()
        self.pw.stop()
        self.server.shutdown()
        self.thread.join()
        self.temp.cleanup()

    def pixel(self, selector):
        self.page.wait_for_function("s => {const i=document.querySelector(s);return i && i.complete && i.naturalWidth>0}", arg=selector)
        return self.page.eval_on_selector(selector, "i => {const c=document.createElement('canvas');c.width=c.height=1;c.getContext('2d').drawImage(i,0,0,1,1);return [...c.getContext('2d').getImageData(0,0,1,1).data].slice(0,3)}")

    def test_deleting_an_earlier_item_preserves_the_open_viewer_target(self):
        Image.new("RGB", (64, 64), "blue").save(self.media / "survivor.png")
        self.page.request.post(f"http://127.0.0.1:{self.server.server_port}/api/refresh")
        self.page.locator("#sortSelect").select_option("name_asc")
        self.page.wait_for_function("document.querySelectorAll('.media-card').length === 2")
        entered = threading.Event()
        release = threading.Event()

        def recycle(path):
            entered.set()
            release.wait(10)
            Path(path).unlink()

        with mock.patch("lumavault.app.send2trash", side_effect=recycle):
            self.page.locator(".media-card").filter(has_text="generated.png").locator(".card-menu").click()
            self.page.locator('#contextMenu [data-action="delete"]').click()
            self.assertTrue(entered.wait(5))
            try:
                self.page.locator(".media-card").filter(has_text="survivor.png").click()
                self.assertEqual(self.pixel("#viewerImage"), [0, 0, 255])
            finally:
                release.set()
            self.page.wait_for_function("document.querySelectorAll('.media-card').length === 1")
        self.page.locator("#viewerFavoriteBtn").click()
        self.page.wait_for_function("document.querySelector('#viewerFavoriteBtn').textContent.includes('Favorited')", timeout=3000)
        self.assertTrue(self.state.is_favorite("test", "survivor.png"))

    def test_recycled_filename_reloads_thumbnail_and_viewer_bytes(self):
        self.assertGreater(self.pixel(".media-card img")[0], 240)
        self.page.locator(".media-card").click()
        self.assertEqual(self.pixel("#viewerImage"), [255, 0, 0])
        self.page.keyboard.press("Escape")
        # Only test fixtures are removed; the OS Recycle Bin is never touched.
        with mock.patch("lumavault.app.send2trash", side_effect=lambda p: Path(p).unlink()):
            self.page.locator(".card-menu").click()
            self.page.locator('#contextMenu [data-action="delete"]').click()
            self.page.wait_for_function("document.querySelectorAll('.media-card').length === 0")
        Image.new("RGB", (64, 64), "blue").save(self.path)
        self.page.locator("#refreshBtn").click()
        self.page.wait_for_selector(".media-card img:not(.loading)")
        self.assertEqual(self.page.locator(".card-name").inner_text(), "generated.png")
        pixel = self.pixel(".media-card img")
        self.assertGreater(pixel[2], 240, f"Regenerated blue image shows cached pixels: {pixel}")
        self.page.locator(".media-card").click()
        self.assertEqual(self.pixel("#viewerImage"), [0, 0, 255])
