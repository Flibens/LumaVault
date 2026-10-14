"""Real headless comparison regression with isolated temporary fixtures and state."""
import os
import tempfile
import threading
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from lumavault.app import VaultState, create_app


class CompareBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scratch = Path(tempfile.gettempdir())
        scratch.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="lumavault-compare-", dir=scratch)
        root = Path(cls.temp.name)
        media = root / "media"
        media.mkdir()
        for name, size, color in [("A.png", (800, 600), "#347fa3"), ("B.png", (1200, 900), "#a37c34")]:
            image = Image.new("RGB", size, color)
            draw = ImageDraw.Draw(image)
            for x in range(0, size[0], size[0] // 10):
                draw.line((x, 0, x, size[1]), fill="white", width=2)
            for y in range(0, size[1], size[1] // 10):
                draw.line((0, y, size[0], y), fill="white", width=2)
            image.save(media / name)
        import json
        from unittest.mock import patch
        data = root / "data"
        data.mkdir()
        (data / "state.json").write_text(json.dumps({"sources": [{"id": "default", "name": "Fixtures", "path": str(media), "recursive": False}], "favorites": []}))
        with patch.dict(os.environ, {"LUMAVAULT_SHARED_BROWSER_STATE_FILE": str(data / "shared.json")}):
            state = VaultState(data, migrate_legacy=False)
        cls.app = create_app(state)
        cls.server = make_server("127.0.0.1", 0, cls.app, threaded=True)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True, channel=os.environ.get("LUMAVAULT_TEST_BROWSER_CHANNEL"))
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.package_process = None
        if os.environ.get('LUMAVAULT_QA_PACKAGED_EXE'):
            import socket
            import subprocess
            import time
            import urllib.request
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            cls.url = f'http://127.0.0.1:{port}'
            env = dict(os.environ, LUMAVAULT_SHARED_BROWSER_STATE_FILE=str(data / 'shared.json'))
            cls.package_process = subprocess.Popen([os.environ['LUMAVAULT_QA_PACKAGED_EXE'], '--browser', '--no-open', '--port', str(port), '--data-dir', str(data)], env=env)
            for _ in range(100):
                try:
                    with urllib.request.urlopen(cls.url + '/api/health', timeout=1) as response:
                        assert response.status == 200
                    break
                except OSError:
                    time.sleep(.1)
            else:
                cls.package_process.terminate()
                raise RuntimeError('Packaged server did not become healthy')
            import hashlib
            source = Path(__file__).resolve().parents[1] / 'lumavault/static'
            for name in ('index.html', 'app.js', 'styles.css'):
                with urllib.request.urlopen(cls.url + ('/' if name == 'index.html' else '/static/' + name)) as response:
                    actual = response.read()
                assert actual == (source / name).read_bytes(), f'Packaged HTTP asset mismatch: {name}'
                print(f'Packaged HTTP SHA256 {name}: {hashlib.sha256(actual).hexdigest()}')

    @classmethod
    def tearDownClass(cls):
        if cls.package_process:
            cls.package_process.terminate()
            cls.package_process.wait(timeout=10)
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.thread.join()
        cls.temp.cleanup()

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(self.url)
        self.page.locator(".media-card").first.wait_for()
        self.page.locator("#compareModeBtn").click()
        self.page.locator(".media-card").nth(0).click()
        self.page.locator(".media-card").nth(1).click()
        self.page.locator("#openCompareBtn").click()
        self.page.wait_for_function("document.querySelector('#compareFront').naturalWidth > 0 && document.querySelector('#compareBack').naturalWidth > 0")

    def tearDown(self):
        self.page.close()

    def geometry(self):
        return self.page.evaluate("""() => {
          const rect = id => { const e = document.querySelector(id), r = e.getBoundingClientRect();
            return {x:r.x,y:r.y,width:r.width,height:r.height,w:e.clientWidth,h:e.clientHeight}; };
          const a = document.querySelector('#compareFront'), b = document.querySelector('#compareBack');
          const m = new DOMMatrix(getComputedStyle(a).transform);
          return {a:rect('#compareFrontWrap'),b:rect('#compareBackWrap'),stage:rect('#compareStage'),
            transformA:a.style.transform,transformB:b.style.transform,z:m.a,px:m.e,py:m.f,
            imageWidth:parseFloat(a.style.width),imageHeight:parseFloat(a.style.height)};
        }""")

    def assert_linked(self, g):
        self.assertEqual(g["transformA"], g["transformB"])
        self.assertAlmostEqual(g["a"]["width"], g["b"]["width"], delta=1)
        self.assertAlmostEqual(g["a"]["x"] + g["a"]["width"], g["b"]["x"], delta=1)
        self.assertAlmostEqual(g["imageWidth"], g["stage"]["w"] / 2, delta=.01)

    def test_side_by_side_pointer_zoom_is_pane_local_and_pan_is_linked(self):
        button = self.page.locator('[data-compare-view="side-by-side"]')
        self.assertEqual(button.count(), 1, "Comparison must offer Side by side")
        button.click()
        for pane in ("a", "b"):
            self.page.locator("#compareZoomResetBtn").click()
            before = self.geometry()
            self.assert_linked(before)
            r = before[pane]
            x, y = r["x"] + r["width"] * .73, r["y"] + r["height"] * .37
            self.page.mouse.move(x, y)
            self.page.mouse.wheel(0, -120)
            self.page.wait_for_function("document.querySelector('#compareZoomResetBtn').textContent === '120%'")
            after = self.geometry()
            self.assert_linked(after)
            self.assertAlmostEqual(after["px"], -.23 * before["imageWidth"] * .2, delta=.6)
            self.assertAlmostEqual(after["py"], .13 * before["imageHeight"] * .2, delta=.6)
            self.page.mouse.down()
            self.page.mouse.move(x + 30, y + 20, steps=5)
            self.page.mouse.up()
            panned = self.geometry()
            self.assert_linked(panned)
            self.assertGreater(panned["px"], after["px"])
            self.page.locator("#compareZoomResetBtn").click()
            reset = self.geometry()
            self.assertEqual((reset["z"], reset["px"], reset["py"]), (1, 0, 0))
        self.assertEqual(self.errors, [])

    def test_normalized_view_survives_mode_switch_and_resize(self):
        self.page.locator('[data-compare-view="side-by-side"]').click()
        g = self.geometry()
        self.page.mouse.move(g['a']['x'] + g['a']['width'] * .7, g['a']['y'] + g['a']['height'] * .4)
        self.page.mouse.wheel(0, -120)
        self.page.wait_for_function("document.querySelector('#compareZoomResetBtn').textContent === '120%'")
        before = self.geometry()
        for mode in ('wipe', 'difference', 'overlay'):
            self.page.locator(f'[data-compare-view="{mode}"]').click()
            after = self.geometry()
            self.assertAlmostEqual(after['px'] / after['imageWidth'], before['px'] / before['imageWidth'], delta=.001)
            self.assertEqual(after['transformA'], after['transformB'])
            self.assertEqual(self.page.locator('#compareDivider').is_visible(), mode == 'wipe')
            self.assertEqual(self.page.locator('#compareOverlayControl').is_visible(), mode == 'overlay')
        self.page.locator('[data-compare-view="side-by-side"]').click()
        self.page.set_viewport_size({'width': 1100, 'height': 800})
        self.page.wait_for_timeout(100)
        after = self.geometry()
        self.assert_linked(after)
        self.assertAlmostEqual(after['px'] / after['imageWidth'], before['px'] / before['imageWidth'], delta=.001)
        self.assertAlmostEqual(after['py'] / after['imageHeight'], before['py'] / before['imageHeight'], delta=.001)
        self.assertEqual(self.errors, [])


    def test_themes_and_ui_scale_keep_precise_pointer_anchor_and_clipped_pan(self):
        for theme, scale in [('original', '1'), ('gloss', '1.25'), ('nier', '1.5')]:
            with self.subTest(theme=theme, scale=scale):
                self.page.locator('#closeCompareOverlay').click()
                self.page.locator('#manageSourcesBtn').click()
                self.page.locator(f'[data-theme-choice="{theme}"]').click()
                self.page.locator(f'[data-ui-scale="{scale}"]').click()
                self.page.locator('#closeSourcesBtn').click()
                self.page.locator('#openCompareBtn').click()
                self.page.locator('[data-compare-view="side-by-side"]').click()
                self.page.locator('#compareZoomResetBtn').click()
                self.page.wait_for_timeout(50)
                for pane in ('a', 'b'):
                    before = self.geometry()
                    r = before[pane]
                    x, y = r['x'] + r['width'] * .73, r['y'] + r['height'] * .37
                    self.page.evaluate("document.querySelector('#compareStage').addEventListener('wheel', e => window.lastCompareWheel = {x:e.clientX,y:e.clientY}, {once:true})")
                    self.page.mouse.move(x, y)
                    self.page.mouse.wheel(0, -120)
                    self.page.wait_for_function("document.querySelector('#compareZoomResetBtn').textContent === '120%'")
                    after = self.geometry()
                    self.assert_linked(after)
                    self.assertEqual(self.page.locator('#compareStage').evaluate('(e) => getComputedStyle(e).cursor'), 'grab')
                    # Chromium rounds physical wheel coordinates; assert the actual event anchor.
                    wheel = self.page.evaluate('window.lastCompareWheel')
                    point_x = (wheel['x'] - r['x']) * before['imageWidth'] / r['width'] - before['imageWidth'] / 2
                    point_y = (wheel['y'] - r['y']) * before['imageHeight'] / r['height'] - before['imageHeight'] / 2
                    self.assertAlmostEqual(after['px'], -point_x * .2, delta=.1)
                    self.assertAlmostEqual(after['py'], -point_y * .2, delta=.1)
                    self.page.mouse.down()
                    self.page.mouse.move(x + 350, y + 200, steps=5)
                    self.page.mouse.up()
                    panned = self.geometry()
                    self.assert_linked(panned)
                    self.assertLessEqual(abs(panned['px']), panned['imageWidth'] * (panned['z'] - 1) / 2 + .01)
                    self.assertEqual(self.page.locator('#compareBackWrap').evaluate('(e) => getComputedStyle(e).overflow'), 'hidden')
                    if pane == 'b':
                        screenshot = Path(self.temp.name) / f'lumavault-side-by-side-{theme}.png'
                        self.page.screenshot(path=str(screenshot))
                    self.page.locator('#compareZoomResetBtn').click()
                self.assertEqual(self.page.locator('[data-compare-view="side-by-side"]').get_attribute('aria-pressed'), 'true')
                self.assertEqual(self.errors, [])
