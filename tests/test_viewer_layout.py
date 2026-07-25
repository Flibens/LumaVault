import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "lumavault" / "static" / "styles.css").read_text(encoding="utf-8")
JS = (ROOT / "lumavault" / "static" / "app.js").read_text(encoding="utf-8")


class ViewerLayoutContractTests(unittest.TestCase):
    def test_viewer_grid_is_hard_constrained_to_viewport(self):
        self.assertIn("grid-template-rows: minmax(0,1fr)", CSS)
        self.assertIn("height: calc(100vh / var(--ui-scale)); max-height: calc(100vh / var(--ui-scale)); overflow: hidden", CSS)
        self.assertIn("min-width: 0; min-height: 0; height: 100%; overflow: hidden", CSS)

    def test_inspector_has_an_independent_scroll_area(self):
        self.assertIn(".inspector { min-width: 0; min-height: 0; height: 100%; overflow: hidden", CSS)
        self.assertIn(".inspector-body { flex: 1; min-height: 0; overflow-y: auto", CSS)

    def test_viewer_image_uses_a_fixed_fit_box(self):
        self.assertIn(".media-canvas img { position: absolute", CSS)
        self.assertIn("height: calc(100% - var(--media-pad-top) - var(--media-pad-bottom))", CSS)
        self.assertIn("object-fit: contain", CSS)

    def test_viewer_video_uses_the_same_fixed_fit_box(self):
        self.assertIn(".media-canvas video { position: absolute", CSS)
        self.assertIn("max-width: none; max-height: none; object-fit: contain", CSS)

    def test_switching_inspector_tabs_starts_at_top(self):
        self.assertIn("if (inspectorBody) inspectorBody.scrollTop = 0", JS)

    def test_clicking_outside_rendered_media_closes_the_viewer(self):
        self.assertIn("function isPointOnRenderedMedia(event)", JS)
        self.assertIn('$("#viewerStage").addEventListener("click"', JS)
        self.assertIn("if (!isPointOnRenderedMedia(event)) closeViewer()", JS)

    def test_delete_is_one_click_and_keeps_gallery_position(self):
        action_section = JS[JS.index("async function performAction"):JS.index("function showContextMenu")]
        self.assertIn("function removeDeletedItems(items)", JS)
        self.assertNotIn("loadMedia(true)", action_section)
        self.assertNotIn("confirm(`Move “${item.name}” to the Recycle Bin?`)", JS)
        self.assertIn('$("#deleteBtn").addEventListener("click", () => performAction("delete"))', JS)

    def test_add_folder_uses_only_the_native_folder_picker(self):
        choose_folder = JS[JS.index("async function chooseFolder()"):JS.index("async function loadMedia")]
        self.assertIn("await window.pywebview.api.choose_folder()", choose_folder)
        self.assertNotIn("prompt(", choose_folder)

    def test_ctrl_click_selects_multiple_cards_for_group_actions(self):
        self.assertIn("selectedKeys: new Set()", JS)
        self.assertIn("if (event.ctrlKey || event.metaKey)", JS)
        self.assertIn("toggleMultiSelection(item, card)", JS)
        self.assertIn("function selectedItemsFor(item)", JS)
        self.assertIn("performAction(\"delete\", targets)", JS)
        self.assertIn(".media-card.multi-selected", CSS)


if __name__ == "__main__":
    unittest.main()
