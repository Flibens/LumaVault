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

    def test_grid_size_is_restored_and_persisted(self):
        self.assertIn('id="cardSize"', HTML)
        self.assertIn("function applyCardSize(size", JS)
        self.assertIn("data.settings?.card_size", JS)
        self.assertIn('$("#cardSize").addEventListener("input"', JS)
        self.assertIn("card_size: size", JS)

    def test_search_field_selector_supports_generation_metadata(self):
        self.assertIn('id="searchFieldSelect"', HTML)
        for value in ("filename", "prompt", "lora", "model", "all"):
            self.assertIn(f'value="{value}"', HTML)
        self.assertIn("searchField", JS)
        self.assertIn("search_field: state.searchField", JS)
        self.assertIn('$("#searchFieldSelect").addEventListener("change"', JS)

    def test_metadata_searches_are_coalesced_instead_of_running_for_every_keystroke(self):
        self.assertIn("reloadQueued: false", JS)
        self.assertIn("if (state.loading) {", JS)
        self.assertIn("state.reloadQueued = true", JS)
        self.assertIn("if (state.reloadQueued)", JS)

    def test_original_theme_has_an_opaque_window_surface(self):
        self.assertIn("background: var(--bg)", CSS[CSS.index(".app-shell {"):CSS.index(".main {")])

    def test_theme_switch_restores_original_or_glossy_glass(self):
        self.assertIn('data-theme-choice="original"', HTML)
        self.assertIn('data-theme-choice="gloss"', HTML)
        self.assertIn("function applyTheme(theme", JS)
        self.assertIn("data.settings?.theme", JS)
        self.assertIn('body.classList.toggle("theme-gloss"', JS)
        self.assertIn('document.documentElement.classList.toggle("native-window"', JS)
        self.assertIn("body: JSON.stringify({ theme: next })", JS)
        self.assertIn("data-theme-choice", JS)
        self.assertIn('html[data-theme="gloss"].native-window', CSS)
        self.assertIn("body.theme-gloss .app-shell", CSS)
        self.assertIn("backdrop-filter: blur(", CSS)


if __name__ == "__main__":
    unittest.main()
