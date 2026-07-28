import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "lumavault" / "static" / "styles.css").read_text(encoding="utf-8")
JS = (ROOT / "lumavault" / "static" / "app.js").read_text(encoding="utf-8")
INDEX = (ROOT / "lumavault" / "static" / "index.html").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")


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

    def test_workflow_tab_uses_a_full_size_themed_pan_and_zoom_graph(self):
        self.assertIn("renderWorkflow(data.workflow_graph)", JS)
        self.assertIn("function renderWorkflow(graph)", JS)
        self.assertIn('class="workflow-canvas"', JS)
        self.assertIn('addEventListener("wheel"', JS)
        self.assertIn('addEventListener("pointerdown"', JS)
        self.assertIn("fitWorkflowGraph", JS)
        self.assertIn('classList.toggle("workflow-view", tab === "workflow")', JS)
        self.assertIn(".viewer.workflow-view", CSS)
        self.assertIn(".workflow-canvas", CSS)
        self.assertIn(".workflow-node", CSS)
        self.assertIn(".workflow-link", CSS)

    def test_nodes_tab_restores_the_searchable_node_list_without_replacing_workflow_graph(self):
        self.assertIn('data-tab="nodes">Nodes</button>', INDEX)
        self.assertIn('data-panel="nodes" id="nodesPanel"', INDEX)
        self.assertIn("renderNodeList(data.workflow_nodes || [])", JS)
        self.assertIn("function renderNodeList(nodes)", JS)
        self.assertIn('id="workflowNodeSearch"', JS)
        self.assertIn('id="workflowNodeList"', JS)
        self.assertIn("renderWorkflow(data.workflow_graph)", JS)
        self.assertIn('classList.toggle("workflow-view", tab === "workflow")', JS)

    def test_nodes_panel_is_cleared_during_metadata_loading_and_failure(self):
        self.assertIn('$("#nodesPanel").innerHTML = \'<div class="inspector-loading">Reading workflow nodes</div>\'', JS)
        self.assertIn('$("#nodesPanel").innerHTML = \'<p class="muted-copy">No workflow nodes available.</p>\'', JS)

    def test_readme_download_name_matches_the_release_version(self):
        self.assertIn("LumaVault-1.0.5-Windows.zip", README)
        self.assertNotIn("LumaVault-1.0.4-Windows.zip", README)

    def test_workflow_long_text_values_wrap_and_scroll_without_visual_truncation(self):
        self.assertIn('param.multiline ? "multiline" : ""', JS)
        self.assertIn("workflowParamHeight", JS)
        self.assertIn(".workflow-node-params > div.multiline", CSS)
        self.assertIn("white-space: pre-wrap", CSS)
        self.assertIn("overflow-y: auto", CSS)

    def test_workflow_renders_subgraph_definitions_as_labeled_groups(self):
        self.assertIn("graph?.groups", JS)
        self.assertIn('class="workflow-group', JS)
        self.assertIn(".workflow-group", CSS)
        self.assertNotIn("Math.min(...prepared", JS)
        self.assertNotIn("Math.max(...prepared", JS)
        self.assertIn("remainingWorkflowDomRecords", JS)
        self.assertIn("requiredInputSlots", JS)
        self.assertIn("inputRowBySlot", JS)
        self.assertNotIn("fromSlot >= from.outputs.length", JS)

    def test_workflow_and_nodes_lists_enforce_hard_shared_dom_budgets(self):
        self.assertIn("WORKFLOW_DOM_BUDGET", JS)
        self.assertIn("remainingWorkflowDomRecords", JS)
        self.assertIn("Math.max(0, remainingWorkflowDomRecords", JS)
        self.assertNotIn("requiredRows + Math.max(0, remainingWorkflowRows - requiredRows)", JS)
        self.assertIn("NODE_LIST_DOM_BUDGET", JS)
        self.assertIn("NODE_LIST_MAX_CARDS", JS)
        self.assertIn("visible.slice(0, NODE_LIST_MAX_CARDS)", JS)

    def test_full_workflow_view_keeps_a_visible_close_action(self):
        self.assertIn('id="workflowCloseBtn"', (ROOT / "lumavault" / "static" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('$("#workflowCloseBtn").addEventListener("click", closeViewer)', JS)
        self.assertIn(".viewer.workflow-view #workflowCloseBtn", CSS)

    def test_workflow_keeps_zero_coordinates_from_saved_comfyui_layouts(self):
        self.assertNotIn('x: Number(node.position?.[0]) ||', JS)
        self.assertNotIn('y: Number(node.position?.[1]) ||', JS)
        self.assertIn("Number.isFinite(savedX) ? savedX", JS)

    def test_workflow_fit_and_mobile_layout_use_the_entire_available_viewport(self):
        self.assertNotIn("Math.max(.16", JS)
        self.assertNotIn("Math.max(.12", JS)
        self.assertIn("if (!Number.isFinite(next) || next <= 0) return", JS)
        self.assertIn('if ($("#viewer").classList.contains("workflow-view")) requestAnimationFrame(fitWorkflowGraph)', JS)
        self.assertIn("body.ui-mobile .viewer.workflow-view .inspector", CSS)
        self.assertIn(".viewer.workflow-view .inspector { height: 100%;", CSS)


if __name__ == "__main__":
    unittest.main()
