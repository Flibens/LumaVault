import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "lumavault" / "static" / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "lumavault" / "static" / "styles.css").read_text(encoding="utf-8")
JS = (ROOT / "lumavault" / "static" / "app.js").read_text(encoding="utf-8")


class UiScaleContractTests(unittest.TestCase):
    def test_ui_scale_is_adjustable_persistent_and_viewport_safe(self):
        self.assertIn('id="uiScale"', HTML)
        self.assertIn('id="uiScaleValue"', HTML)
        self.assertIn("--ui-scale: 1", CSS)
        self.assertIn("zoom: var(--ui-scale)", CSS)
        self.assertIn("height: calc(100vh / var(--ui-scale))", CSS)
        self.assertIn("const UI_SCALE_KEY", JS)
        self.assertIn("function applyUiScale(scale", JS)
        self.assertIn("localStorage.setItem(UI_SCALE_KEY", JS)
        self.assertIn('api("/api/settings"', JS)
        self.assertIn("data.settings?.ui_scale", JS)
        self.assertIn('$("#uiScale").addEventListener("input"', JS)
        self.assertIn("function syncUiScaleBreakpoints()", JS)
        self.assertIn("event.clientX / state.uiScale", JS)
        self.assertIn("body.ui-mobile", CSS)


if __name__ == "__main__":
    unittest.main()
