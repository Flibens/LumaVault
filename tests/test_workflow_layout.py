import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYOUT_MODULE = ROOT / "lumavault" / "static" / "workflow-layout.js"


def run_layout(nodes, links=None, groups=None):
    payload = json.dumps({"nodes": nodes, "links": links or [], "groups": groups or []})
    script = f"""
const layout = require({json.dumps(str(LAYOUT_MODULE))});
const input = {payload};
process.stdout.write(JSON.stringify(layout.compactWorkflowLayout(input.nodes, input.links, input.groups)));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def rectangles_overlap(left, right):
    return not (
        left["x"] + left["width"] <= right["x"]
        or right["x"] + right["width"] <= left["x"]
        or left["y"] + left["height"] <= right["y"]
        or right["y"] + right["height"] <= left["y"]
    )


class CompactWorkflowLayoutTests(unittest.TestCase):
    def test_node_height_includes_rendered_body_padding_and_borders(self):
        result = run_layout([{
            "id": "note",
            "position": [0, 0],
            "inputs": [],
            "outputs": [],
            "params": [{"multiline": True}],
        }])

        self.assertGreaterEqual(result["nodes"][0]["height"], 146)

    def test_ignores_oversized_saved_dimensions_and_prevents_node_overlap(self):
        nodes = [
            {"id": "loader", "position": [0, 0], "size": [900, 1200], "inputs": [], "outputs": [{}], "params": [{"multiline": False}]},
            {"id": "prompt", "position": [100, 20], "size": [700, 980], "inputs": [{}], "outputs": [{}], "params": [{"multiline": True}]},
            {"id": "settings", "position": [110, 35], "size": [640, 760], "inputs": [{}], "outputs": [], "params": [{"multiline": False}, {"multiline": False}]},
            {"id": "sampler", "position": [180, 50], "size": [800, 1100], "inputs": [{}, {}], "outputs": [{}], "params": [{"multiline": False}]},
        ]
        links = [
            {"from_node": "loader", "to_node": "prompt"},
            {"from_node": "loader", "to_node": "settings"},
            {"from_node": "prompt", "to_node": "sampler"},
            {"from_node": "settings", "to_node": "sampler"},
        ]

        result = run_layout(nodes, links)
        laid_out = result["nodes"]

        self.assertTrue(all(node["width"] <= 280 for node in laid_out))
        self.assertTrue(all(node["height"] < 300 for node in laid_out))
        for index, left in enumerate(laid_out):
            for right in laid_out[index + 1:]:
                self.assertFalse(rectangles_overlap(left, right), f"{left['id']} overlaps {right['id']}")

        by_id = {node["id"]: node for node in laid_out}
        self.assertLess(by_id["loader"]["x"], by_id["prompt"]["x"])
        self.assertLess(by_id["prompt"]["x"], by_id["sampler"]["x"])

    def test_splits_a_tall_layer_into_balanced_columns_for_wide_viewports(self):
        nodes = [
            {"id": str(index), "position": [0, index * 100], "size": [500, 500], "inputs": [], "outputs": [], "params": [{"multiline": False}]}
            for index in range(10)
        ]

        result = run_layout(nodes)
        laid_out = result["nodes"]

        self.assertGreater(len({node["x"] for node in laid_out}), 1)
        self.assertLessEqual(max(node["y"] + node["height"] for node in laid_out) - min(node["y"] for node in laid_out), 1100)
        for index, left in enumerate(laid_out):
            for right in laid_out[index + 1:]:
                self.assertFalse(rectangles_overlap(left, right), f"{left['id']} overlaps {right['id']}")

    def test_top_level_and_subgraph_layout_avoid_an_excessively_wide_strip(self):
        top_nodes = [
            {"id": f"top-{index}", "position": [index * 300, 0], "inputs": [], "outputs": [], "params": [{"multiline": False}]}
            for index in range(5)
        ]
        subgraph_nodes = [
            {"id": f"nested-{index}", "subgraph": "Nested", "position": [0, index * 100], "inputs": [], "outputs": [], "params": [{"multiline": False}]}
            for index in range(24)
        ]
        links = [
            {"from_node": top_nodes[index]["id"], "to_node": top_nodes[index + 1]["id"]}
            for index in range(len(top_nodes) - 1)
        ]

        result = run_layout(top_nodes + subgraph_nodes, links, [{"title": "Nested"}])

        self.assertLess(result["width"] / result["height"], 3.5)


if __name__ == "__main__":
    unittest.main()
