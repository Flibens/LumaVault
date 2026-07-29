import json
import math
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image
from PIL.PngImagePlugin import PngInfo

import lumavault.metadata as metadata_module
from lumavault.app import VaultState, create_app
from lumavault.metadata import (
    _scan_bytes_for_workflow,
    build_workflow_graph,
    extract_workflow_from_file,
    extract_workflow_nodes,
    parse_comfy_metadata,
)


class LumaVaultAppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.media = root / "media"
        self.media.mkdir()
        self.data = root / "data"

        prompt = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "aurora.safetensors"}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "a glass city at blue hour"}, "_meta": {"title": "Positive Prompt"}},
            "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "low quality"}, "_meta": {"title": "Negative Prompt"}},
            "4": {"class_type": "KSampler", "inputs": {"seed": 4242, "steps": 28, "cfg": 6.5, "sampler_name": "euler", "scheduler": "normal", "positive": ["2", 0], "negative": ["3", 0], "model": ["1", 0]}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 768, "height": 1024}},
            "6": {"class_type": "LoraLoader", "inputs": {"lora_name": "cinematic.safetensors", "strength_model": 0.8, "strength_clip": 0.7}},
        }
        workflow = {
            "nodes": [
                {
                    "id": 1,
                    "type": "CheckpointLoaderSimple",
                    "pos": [40, 80],
                    "size": [230, 92],
                    "mode": 0,
                    "outputs": [{"name": "MODEL", "type": "MODEL", "links": [10]}],
                    "widgets_values": ["aurora.safetensors"],
                },
                {
                    "id": 4,
                    "type": "KSampler",
                    "pos": [410, 80],
                    "size": [260, 250],
                    "mode": 0,
                    "inputs": [{"name": "model", "type": "MODEL", "link": 10}],
                    "widgets_values": [4242, 28, 6.5, "euler", "normal"],
                },
            ],
            "links": [[10, 1, 0, 4, 0, "MODEL"]],
            "definitions": {"subgraphs": [{
                "id": "sg1",
                "name": "Detail Pass",
                "nodes": [
                    {
                        "id": 22,
                        "type": "ImageScale",
                        "pos": [0, 0],
                        "size": [240, 150],
                        "mode": 0,
                        "inputs": [{"name": "image", "type": "IMAGE", "link": 21}],
                        "outputs": [{"name": "IMAGE", "type": "IMAGE", "links": [20]}],
                        "widgets_values": ["lanczos", 1536, 2048],
                    },
                    {
                        "id": 23,
                        "type": "PreviewImage",
                        "pos": [340, 0],
                        "size": [240, 150],
                        "mode": 0,
                        "inputs": [{"name": "images", "type": "IMAGE", "link": 20}],
                        "outputs": [{"name": "IMAGE", "type": "IMAGE", "links": [22]}],
                    },
                ],
                "inputs": [{"name": "image", "type": "IMAGE"}],
                "outputs": [{"name": "result", "type": "IMAGE"}],
                "inputNode": {"id": -10, "bounding": [-180, 0, 120, 120]},
                "outputNode": {"id": -20, "bounding": [640, 0, 120, 120]},
                "links": [
                    {"id": 20, "origin_id": 22, "origin_slot": 0, "target_id": 23, "target_slot": 0, "type": "IMAGE"},
                    {"id": 21, "origin_id": -10, "origin_slot": 0, "target_id": 22, "target_slot": 0, "type": "IMAGE"},
                    {"id": 22, "origin_id": 23, "origin_slot": 0, "target_id": -20, "target_slot": 0, "type": "IMAGE"},
                ],
            }]},
        }
        info = PngInfo()
        info.add_text("prompt", json.dumps(prompt))
        info.add_text("workflow", json.dumps(workflow))
        Image.new("RGB", (768, 1024), (60, 80, 120)).save(self.media / "sample.png", pnginfo=info)

        self.state = VaultState(self.data, migrate_legacy=False)
        self.state.data["sources"] = [{"id": "test", "name": "Test Media", "path": str(self.media), "recursive": True}]
        self.state.data["favorites"] = []
        self.state.save()
        self.client = create_app(self.state).test_client()

    def tearDown(self):
        self.temp.cleanup()

    def test_health_and_gallery(self):
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        listing = self.client.get("/api/media?source=test&page=0&per_page=20")
        payload = listing.get_json()
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["items"][0]["name"], "sample.png")
        self.assertEqual(payload["items"][0]["kind"], "image")

    def test_gallery_can_filter_by_prompt_lora_model_and_all_metadata(self):
        cases = [
            ("prompt", "glass city", 1),
            ("prompt", "LOW QUALITY", 1),
            ("lora", "cinematic", 1),
            ("model", "AURORA", 1),
            ("all", "blue hour", 1),
            ("all", "sample.png", 1),
            ("filename", "glass city", 0),
            ("prompt", "not present", 0),
        ]
        for search_field, search, expected in cases:
            with self.subTest(search_field=search_field, search=search):
                response = self.client.get("/api/media", query_string={
                    "source": "test",
                    "search_field": search_field,
                    "search": search,
                    "page": 0,
                    "per_page": 20,
                })
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json()["total"], expected)

        invalid = self.client.get("/api/media?source=test&search_field=raw&search=glass")
        self.assertEqual(invalid.status_code, 400)

    def test_metadata_search_index_is_persistent_and_reused(self):
        first = self.client.get("/api/media?source=test&search_field=prompt&search=glass")
        self.assertEqual(first.get_json()["total"], 1)
        self.assertTrue((self.data / "metadata-index.json").is_file())

        reloaded = VaultState(self.data, migrate_legacy=False)
        reloaded_client = create_app(reloaded).test_client()
        with mock.patch("lumavault.app.extract_metadata", side_effect=AssertionError("cache was not reused")):
            second = reloaded_client.get("/api/media?source=test&search_field=model&search=aurora")
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.get_json()["total"], 1)

    def test_cached_metadata_search_does_not_touch_every_media_file_again(self):
        rows = self.state.scan("test")
        first = self.state.filter_media(rows, "glass", "prompt")
        self.assertEqual(len(first), 1)

        with mock.patch.object(
            self.state,
            "resolve_file",
            side_effect=AssertionError("cached search resolved a media path"),
        ):
            second = self.state.filter_media(rows, "glass", "prompt")

        self.assertEqual(len(second), 1)

    def test_metadata_search_index_refreshes_when_a_file_changes(self):
        first = self.client.get("/api/media?source=test&search_field=prompt&search=glass")
        self.assertEqual(first.get_json()["total"], 1)

        path = self.media / "sample.png"
        previous_mtime_ns = path.stat().st_mtime_ns
        replacement = PngInfo()
        replacement.add_text("prompt", json.dumps({
            "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "a copper forest at dawn"}},
        }))
        Image.new("RGB", (768, 1024), (120, 80, 60)).save(path, pnginfo=replacement)
        os.utime(path, ns=(previous_mtime_ns + 1_000_000, previous_mtime_ns + 1_000_000))
        self.state.clear_scan_cache()

        old = self.client.get("/api/media?source=test&search_field=prompt&search=glass").get_json()
        new = self.client.get("/api/media?source=test&search_field=prompt&search=copper").get_json()
        self.assertEqual(old["total"], 0)
        self.assertEqual(new["total"], 1)

    def test_metadata_and_subgraph_workflow(self):
        response = self.client.get("/api/metadata?source=test&path=sample.png")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        parsed = payload["parsed"]
        self.assertEqual(parsed["prompt"], "a glass city at blue hour")
        self.assertEqual(parsed["negative_prompt"], "low quality")
        self.assertEqual(parsed["seed"], 4242)
        self.assertEqual(parsed["steps"], 28)
        self.assertEqual(parsed["model"], "aurora.safetensors")
        self.assertEqual(parsed["loras"][0]["name"], "cinematic.safetensors")
        self.assertTrue(any(node["id"] == "sg1:22" for node in payload["workflow_nodes"]))
        self.assertEqual(payload["raw"]["prompt"]["2"]["inputs"]["text"], "a glass city at blue hour")
        self.assertEqual(payload["raw"]["workflow"]["nodes"][0]["id"], 1)

    def test_sampler_custom_resolves_seed_from_linked_random_noise(self):
        for value, expected in [(918273645, 918273645), ("4815162342", 4815162342), (0, 0)]:
            with self.subTest(value=value):
                prompt = {
                    "noise": {"class_type": "RandomNoise", "inputs": {"noise_seed": value}},
                    "sampler": {
                        "class_type": "SamplerCustomAdvanced",
                        "inputs": {"noise": ["noise", 0]},
                    },
                }

                parsed = parse_comfy_metadata({"prompt": prompt})

                self.assertEqual(parsed["seed"], expected)

        missing = parse_comfy_metadata({
            "prompt": {"sampler": {"class_type": "SamplerCustomAdvanced", "inputs": {}}},
        })
        self.assertIsNone(missing["seed"])

    def test_raw_display_prioritizes_prompt_and_workflow_after_generic_metadata(self):
        metadata = {f"generic-{index}": "value" for index in range(256)}
        metadata["prompt"] = {"1": {"class_type": "Text", "inputs": {"text": "kept"}}}
        metadata["workflow"] = {"nodes": [{"id": 1, "type": "Text"}]}

        raw = metadata_module.raw_metadata_for_display(metadata)

        self.assertEqual(raw["prompt"]["1"]["inputs"]["text"], "kept")
        self.assertEqual(raw["workflow"]["nodes"][0]["id"], 1)
        self.assertLessEqual(len(raw), 256)

    def test_metadata_returns_visual_workflow_graph_with_saved_layout_and_links(self):
        response = self.client.get("/api/metadata?source=test&path=sample.png")
        self.assertEqual(response.status_code, 200)
        graph = response.get_json()["workflow_graph"]

        self.assertEqual(graph["kind"], "ui")
        self.assertEqual(graph["nodes"][0]["position"], [40.0, 80.0])
        self.assertEqual(graph["nodes"][0]["size"], [230.0, 92.0])
        self.assertEqual(graph["nodes"][0]["outputs"][0]["name"], "MODEL")
        self.assertEqual(graph["nodes"][1]["inputs"][0]["name"], "model")
        self.assertEqual(graph["links"][0], {
            "id": "10",
            "from_node": "1",
            "from_slot": 0,
            "to_node": "4",
            "to_slot": 0,
            "type": "MODEL",
        })
        self.assertEqual({node["id"] for node in graph["nodes"]}, {"1", "4", "sg1:-10", "sg1:22", "sg1:23", "sg1:-20"})
        self.assertEqual(next(node for node in graph["nodes"] if node["id"] == "sg1:22")["subgraph"], "Detail Pass")
        self.assertIn({
            "id": "sg1:20",
            "from_node": "sg1:22",
            "from_slot": 0,
            "to_node": "sg1:23",
            "to_slot": 0,
            "type": "IMAGE",
        }, graph["links"])
        self.assertEqual({link["id"] for link in graph["links"]}, {"10", "sg1:20", "sg1:21", "sg1:22"})
        group = next(group for group in graph["groups"] if group["id"] == "subgraph:sg1")
        self.assertEqual(group["title"], "Detail Pass")
        grouped_nodes = [node for node in graph["nodes"] if node.get("subgraph") == "Detail Pass"]
        for node in grouped_nodes:
            rendered_width = max(210, min(420, node["size"][0]))
            content_height = 48 + max(len(node["inputs"]), len(node["outputs"])) * 22
            if node["params"]:
                content_height += 14 + min(7, len(node["params"])) * 22
            rendered_height = max(92, min(480, max(node["size"][1], content_height)))
            self.assertLessEqual(node["position"][0] + rendered_width, group["position"][0] + group["size"][0])
            self.assertLessEqual(node["position"][1] + rendered_height, group["position"][1] + group["size"][1])

    def test_api_prompt_graph_is_auto_arranged_with_inferred_connections(self):
        long_prompt = "A detailed cinematic prompt. " * 300
        prompt = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "aurora.safetensors"}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": long_prompt, "clip": ["1", 1]}},
            "3": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "seed": 42}},
        }

        graph = build_workflow_graph(prompt, "api")

        self.assertEqual(graph["kind"], "api")
        self.assertEqual([node["id"] for node in graph["nodes"]], ["1", "2", "3"])
        self.assertLess(graph["nodes"][0]["position"][0], graph["nodes"][1]["position"][0])
        self.assertLess(graph["nodes"][1]["position"][0], graph["nodes"][2]["position"][0])
        self.assertEqual(
            {(link["from_node"], link["to_node"], link["to_slot"]) for link in graph["links"]},
            {("1", "2", 1), ("1", "3", 0), ("2", "3", 1)},
        )
        self.assertTrue(any(param["name"] == "seed" and param["value"] == "42" for param in graph["nodes"][2]["params"]))
        text_param = next(param for param in graph["nodes"][1]["params"] if param["name"] == "text")
        self.assertEqual(text_param["value"], long_prompt)
        self.assertTrue(text_param["multiline"])

    def test_workflow_graph_sanitizes_nonfinite_coordinates_and_invalid_slots(self):
        ui_graph = build_workflow_graph({
            "nodes": [
                {"id": 1, "type": "Source", "pos": [float("nan"), float("inf")], "size": [float("inf"), -20], "outputs": []},
                {"id": 2, "type": "Target", "pos": [200, 0], "inputs": []},
            ],
            "links": [
                [1, 1, "not-a-slot", 2, 0, "IMAGE"],
                [2, 1, 0, 2, 1_000_000, "IMAGE"],
            ],
        }, "ui")
        json.dumps(ui_graph, allow_nan=False)
        self.assertEqual(ui_graph["nodes"][0]["position"], [0.0, 0.0])
        self.assertEqual(ui_graph["nodes"][0]["size"], [240.0, 150.0])
        self.assertEqual(ui_graph["links"], [])
        self.assertEqual(build_workflow_graph({"nodes": [], "links": 1}, "ui")["links"], [])

        strict_ui_graph = build_workflow_graph({
            "nodes": [
                {"id": 1, "type": "Source", "outputs": ["malformed", {"name": "real", "type": "IMAGE"}]},
                {"id": 2, "type": "Target", "inputs": [{"name": "image", "type": "IMAGE"}]},
            ],
            "links": [
                [1, 1, True, 2, 0, "IMAGE"],
                [2, 1, 1.5, 2, 0, "IMAGE"],
                [3, 1, 511, 2, 0, "IMAGE"],
                [4, 999, 0, 2, 0, "IMAGE"],
                [5, 1, 1, 2, 0, "IMAGE"],
            ],
        }, "ui")
        self.assertEqual(len(strict_ui_graph["links"]), 1)
        self.assertEqual(strict_ui_graph["links"][0]["id"], "5")
        self.assertEqual(len(strict_ui_graph["nodes"][0]["outputs"]), 2)
        self.assertEqual(strict_ui_graph["nodes"][0]["outputs"][1]["name"], "real")

        api_graph = build_workflow_graph({
            "1": {"class_type": "Source", "inputs": {}},
            "2": {"class_type": "Target", "inputs": {
                "image": ["1", 1_000_000],
                "literal_choices": ["1", "not-a-slot"],
                "three_item_literal": ["1", 0, "literal-tail"],
                "fractional_literal": ["1", 1.5],
                "boolean_literal": ["1", True],
            }},
        }, "api")
        self.assertEqual(api_graph["links"], [])
        self.assertLessEqual(len(api_graph["nodes"][0]["outputs"]), 512)
        self.assertTrue(any(
            param["name"] == "literal_choices" and "not-a-slot" in param["value"]
            for param in api_graph["nodes"][1]["params"]
        ))
        param_names = {param["name"] for param in api_graph["nodes"][1]["params"]}
        self.assertTrue({"three_item_literal", "fractional_literal", "boolean_literal"} <= param_names)

    def test_api_graph_layout_handles_long_reverse_dependency_chains_iteratively(self):
        count = 1500
        prompt = {
            str(node_id): {
                "class_type": "Node",
                "inputs": ({"input": [str(node_id + 1), 0]} if node_id + 1 < count else {}),
            }
            for node_id in range(count - 1, -1, -1)
        }
        graph = build_workflow_graph(prompt, "api")
        self.assertEqual(len(graph["nodes"]), count)
        self.assertEqual(len(graph["links"]), count - 1)

        cycle = build_workflow_graph({
            "1": {"class_type": "A", "inputs": {"input": ["2", 0]}},
            "2": {"class_type": "B", "inputs": {"input": ["1", 0]}},
        }, "api")
        self.assertEqual(cycle["nodes"][0]["position"][0], cycle["nodes"][1]["position"][0])

    def test_workflow_graph_bounds_untrusted_graph_complexity(self):
        nodes = [
            {
                "id": index,
                "type": "Node",
                "title": "x" * 10_000,
                "inputs": [{"name": "input", "type": "IMAGE"}],
                "outputs": [{"name": "output", "type": "IMAGE"}],
            }
            for index in range(5_001)
        ]
        nodes[0]["widgets_values"] = list(range(100))
        links = [[index, 0, 0, 1, 0, "IMAGE"] for index in range(20_001)]
        graph = build_workflow_graph({"nodes": nodes, "links": links}, "ui")
        self.assertLessEqual(len(graph["nodes"]), 5_000)
        self.assertLessEqual(len(graph["links"]), 20_000)
        self.assertLessEqual(len(graph["nodes"][0]["title"]), 2_048)

        subgraphs = [{
            "id": f"subgraph-{index}",
            "name": f"Subgraph {index}",
            "nodes": [{"id": 1, "type": "Node"}],
            "links": [],
        } for index in range(129)]
        nested = build_workflow_graph({"nodes": [], "definitions": {"subgraphs": subgraphs}}, "ui")
        self.assertLessEqual(len(nested["groups"]), 128)

        inspector = extract_workflow_nodes({"workflow": {"nodes": nodes}})
        self.assertLessEqual(len(inspector), 5_000)
        self.assertTrue(all(len(node["params"]) <= 64 for node in inspector))

    def test_workflow_graph_enforces_a_global_port_budget(self):
        slot = {"name": "value", "type": "*"}
        workflow = {
            "nodes": [
                {"id": index, "type": "LargeCustomNode", "inputs": [slot] * 512, "outputs": [slot] * 512}
                for index in range(80)
            ],
            "links": [],
        }

        graph = build_workflow_graph(workflow, "ui")
        total_ports = sum(len(node["inputs"]) + len(node["outputs"]) for node in graph["nodes"])

        self.assertLessEqual(total_ports, metadata_module.WORKFLOW_MAX_TOTAL_PORTS)

    def test_duplicate_workflow_ids_are_deduplicated_in_linear_time(self):
        duplicate_id = "duplicate" * 100
        workflow = {"nodes": [{"id": duplicate_id, "type": "Custom"} for _ in range(5000)], "links": []}

        started = time.perf_counter()
        graph = build_workflow_graph(workflow, "ui")
        elapsed = time.perf_counter() - started

        ids = [node["id"] for node in graph["nodes"]]
        self.assertEqual(len(ids), 5000)
        self.assertEqual(len(set(ids)), 5000)
        self.assertLess(elapsed, 0.75)

    def test_composite_workflow_identifiers_remain_globally_bounded(self):
        long_id = "identifier" * 100
        metadata = {
            "workflow": {
                "nodes": [],
                "definitions": {"subgraphs": [{
                    "id": long_id,
                    "name": "Long identifiers",
                    "nodes": [{"id": long_id, "type": "Custom"}],
                    "links": [],
                }]},
            }
        }

        inspector = extract_workflow_nodes(metadata)
        graph = build_workflow_graph(metadata["workflow"], "ui")

        self.assertTrue(inspector)
        self.assertTrue(graph["groups"])
        self.assertTrue(all(len(node["id"]) <= 512 for node in inspector))
        self.assertTrue(all(len(node["id"]) <= 512 for node in graph["nodes"]))
        self.assertTrue(all(len(group["id"]) <= 512 for group in graph["groups"]))

    def test_workflow_graph_sanitizes_mode_and_duplicate_subgraph_ids(self):
        duplicate = {
            "nodes": [],
            "definitions": {"subgraphs": [
                {"id": "duplicate", "name": "First", "nodes": [{"id": 1, "type": "Node", "mode": float("nan")}]},
                {"id": "duplicate", "name": "Second", "nodes": [{"id": 1, "type": "Node", "mode": float("inf")}]},
            ]},
        }
        graph = build_workflow_graph(duplicate, "ui")
        self.assertEqual(len({node["id"] for node in graph["nodes"]}), len(graph["nodes"]))
        self.assertEqual(len({group["id"] for group in graph["groups"]}), len(graph["groups"]))
        self.assertTrue(all(node["mode"] == 0 for node in graph["nodes"]))
        json.dumps(graph, allow_nan=False)

    def test_workflow_graph_limits_raw_api_inspection_and_deduplicates_all_ids(self):
        api = {f"junk-{index}": None for index in range(10_000)}
        api["late"] = {"class_type": "TooLate", "inputs": {}}
        self.assertEqual(build_workflow_graph(api, "api")["nodes"], [])
        api_collision = {
            1: {"class_type": "Numeric", "inputs": {}},
            "1": {"class_type": "String", "inputs": {}},
        }
        api_collision_ids = [node["id"] for node in build_workflow_graph(api_collision, "api")["nodes"]]
        self.assertEqual(len(api_collision_ids), 2)
        self.assertEqual(len(api_collision_ids), len(set(api_collision_ids)))

        ui = {
            "nodes": [
                {"id": "sg:1", "type": "Top", "inputs": [{"name": "a"}, {"name": "b"}], "outputs": [{"name": "a"}, {"name": "b"}]},
                {"id": "sg:1", "type": "TopDuplicate", "inputs": [{"name": "a"}, {"name": "b"}], "outputs": [{"name": "a"}, {"name": "b"}]},
            ],
            "links": [[5, "sg:1", 0, "sg:1", 0, ""], [5, "sg:1", 1, "sg:1", 1, ""]],
            "definitions": {"subgraphs": [{
                "id": "sg",
                "name": "Collision",
                "nodes": [{"id": 1, "type": "Inside", "inputs": [{"name": "in"}], "outputs": [{"name": "out"}]}],
                "inputNode": {"id": 1, "bounding": [-100, 0, 80, 80]},
                "links": [[5, 1, 0, 1, 0, ""]],
            }]},
        }
        graph = build_workflow_graph(ui, "ui")
        node_ids = [node["id"] for node in graph["nodes"]]
        link_ids = [link["id"] for link in graph["links"]]
        self.assertEqual(len(node_ids), len(set(node_ids)))
        self.assertEqual(len(link_ids), len(set(link_ids)))

    def test_metadata_is_strict_json_finite_and_loras_are_globally_bounded(self):
        prompt = {"1": {"class_type": "KSampler", "inputs": {
            "seed": float("nan"), "steps": float("inf"), "cfg": float("-inf"),
        }}}
        workflow = {"nodes": [{
            "id": index,
            "type": "LoraManager",
            "widgets_values": [[
                {"name": f"lora-{index}-{item}", "active": True, "strength": 1.0}
                for item in range(64)
            ]],
        } for index in range(100)]}
        info = PngInfo()
        info.add_text("prompt", json.dumps(prompt))
        info.add_text("workflow", json.dumps(workflow))
        Image.new("RGB", (8, 8)).save(self.media / "hostile.png", pnginfo=info)
        response = self.client.get("/api/metadata?source=test&path=hostile.png")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        json.dumps(payload, allow_nan=False)
        self.assertLessEqual(len(payload["parsed"]["loras"]), 128)
        self.assertFalse(any(isinstance(value, float) and not math.isfinite(value) for value in payload["parsed"].values()))

        lora_hashes = ",".join(f"hash-lora-{index}:deadbeef" for index in range(6_400))
        hashed = parse_comfy_metadata({"parameters": f'ordinary prompt\nLora hashes: "{lora_hashes}"'})
        self.assertEqual(len(hashed["loras"]), 128)

    def test_api_prompt_preserves_bounded_meta_title_for_negative_classification(self):
        parsed = parse_comfy_metadata({"prompt": {
            "negative": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "low quality"},
                "_meta": {"title": "Negative Prompt", "ignored": "x" * 100_000},
            },
            "positive": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "sunlit forest"},
                "_meta": {"title": "Positive Prompt"},
            },
        }})
        self.assertEqual(parsed["prompt"], "sunlit forest")
        self.assertEqual(parsed["negative_prompt"], "low quality")

    def test_raw_workflow_fallback_is_quote_aware_and_never_reads_the_whole_file(self):
        embedded = json.dumps({
            "workflow": {
                "nodes": [{"id": 1, "type": "Note", "title": "literal } brace"}],
                "links": [],
            }
        }).encode("utf-8")
        candidates = list(_scan_bytes_for_workflow(b"{ malformed-prefix " + embedded + b"binary-suffix"))
        self.assertTrue(any("literal } brace" in candidate for candidate in candidates))

        media = self.media / "large-fallback.bin"
        with media.open("wb") as handle:
            handle.write(b"header")
            handle.seek(24 * 1024 * 1024)
            handle.write(embedded)

        original_open = open

        class GuardedReader:
            def __init__(self, handle):
                self.handle = handle

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return self.handle.__exit__(*args)

            def __getattr__(self, name):
                return getattr(self.handle, name)

            def read(self, size=-1):
                if size is None or size < 0:
                    raise AssertionError("fallback attempted an unbounded read")
                return self.handle.read(size)

        def guarded_open(path, mode="r", *args, **kwargs):
            handle = original_open(path, mode, *args, **kwargs)
            if Path(path) == media and "b" in mode:
                return GuardedReader(handle)
            return handle

        with mock.patch("builtins.open", side_effect=guarded_open):
            workflow, workflow_type = extract_workflow_from_file(media)
        self.assertEqual(workflow_type, "ui")
        self.assertEqual(workflow["nodes"][0]["title"], "literal } brace")

    def test_api_prompt_resolution_handles_deep_linear_chains(self):
        prompt = {"0": {"class_type": "Text", "inputs": {"text": "deep prompt"}}}
        for index in range(1, 1_200):
            prompt[str(index)] = {"class_type": "Reroute", "inputs": {"text": [str(index - 1), 0]}}
        prompt["sampler"] = {"class_type": "KSampler", "inputs": {"seed": 42, "positive": ["1199", 0]}}
        parsed = parse_comfy_metadata({"prompt": prompt})
        self.assertEqual(parsed["seed"], 42)
        self.assertEqual(parsed["prompt"], "deep prompt")

        linked = {
            "source": {"class_type": "Text", "inputs": {"text": "shared"}},
            **{
                f"encode-{index}": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {"text": ["source", 0]},
                }
                for index in range(2_000)
            },
        }
        with mock.patch.object(
            metadata_module,
            "_build_showtext_snapshots",
            wraps=metadata_module._build_showtext_snapshots,
        ) as snapshot_builder:
            parse_comfy_metadata({"prompt": linked})
        self.assertEqual(snapshot_builder.call_count, 1)

    def test_string_concatenate_resolution_is_iterative_memoized_and_output_bounded(self):
        chain = {"0": {"class_type": "Text", "inputs": {"text": "x"}}}
        for index in range(1, 1_200):
            chain[str(index)] = {
                "class_type": "StringConcatenate",
                "inputs": {"string_1": [str(index - 1), 0]},
            }
        chain["sampler"] = {
            "class_type": "KSampler",
            "inputs": {"positive": ["1199", 0]},
        }
        self.assertEqual(parse_comfy_metadata({"prompt": chain})["prompt"], "x")

        amplified = {"0": {"class_type": "Text", "inputs": {"text": "seed"}}}
        for index in range(1, 23):
            amplified[str(index)] = {
                "class_type": "StringConcatenate",
                "inputs": {
                    "string_1": [str(index - 1), 0],
                    "string_2": [str(index - 1), 0],
                },
            }
        amplified["sampler"] = {
            "class_type": "KSampler",
            "inputs": {"positive": ["22", 0]},
        }
        amplified_prompt = parse_comfy_metadata({"prompt": amplified})["prompt"]
        self.assertIsInstance(amplified_prompt, str)
        self.assertLessEqual(len(amplified_prompt), 20_000)

        wide = {
            "source": {"class_type": "Text", "inputs": {"text": "z" * 100_000}},
            "concat": {
                "class_type": "StringConcatenate",
                "inputs": {f"string_{index}": ["source", 0] for index in range(512)},
            },
            "sampler": {"class_type": "KSampler", "inputs": {"positive": ["concat", 0]}},
        }
        self.assertLessEqual(len(parse_comfy_metadata({"prompt": wide})["prompt"]), 20_000)

    def test_favorite_and_thumbnail(self):
        favorite = self.client.post("/api/favorite", json={"source_id": "test", "path": "sample.png"})
        self.assertTrue(favorite.get_json()["is_favorite"])
        listing = self.client.get("/api/media?source=test&favorites=true&page=0&per_page=20").get_json()
        self.assertEqual(listing["total"], 1)
        thumb = self.client.get("/api/thumb?source=test&path=sample.png&width=300")
        self.assertEqual(thumb.status_code, 200)
        self.assertEqual(thumb.mimetype, "image/jpeg")
        thumb.close()

    def test_path_traversal_is_rejected(self):
        response = self.client.get("/api/file?source=test&path=../state/state.json")
        self.assertEqual(response.status_code, 404)

    def test_ui_scale_setting_is_saved_to_application_state(self):
        response = self.client.patch("/api/settings", json={"ui_scale": 1.75})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["settings"]["ui_scale"], 1.75)
        self.assertEqual(self.client.get("/api/sources").get_json()["settings"]["ui_scale"], 1.75)
        reloaded = VaultState(self.data, migrate_legacy=False)
        self.assertEqual(reloaded.data["settings"]["ui_scale"], 1.75)
        self.assertEqual(self.client.patch("/api/settings", json={"ui_scale": "huge"}).status_code, 400)

    def test_grid_size_setting_is_saved_to_application_state(self):
        response = self.client.patch("/api/settings", json={"card_size": 315})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["settings"]["card_size"], 315)
        self.assertEqual(self.client.get("/api/sources").get_json()["settings"]["card_size"], 315)

        reloaded = VaultState(self.data, migrate_legacy=False)
        self.assertEqual(reloaded.data["settings"]["card_size"], 315)
        self.assertEqual(self.client.patch("/api/settings", json={"card_size": "huge"}).status_code, 400)
        self.assertEqual(self.client.patch("/api/settings", json={"card_size": float("inf")}).status_code, 400)

    def test_grid_size_setting_is_clamped_to_slider_bounds(self):
        small = self.client.patch("/api/settings", json={"card_size": 1}).get_json()
        large = self.client.patch("/api/settings", json={"card_size": 10_000}).get_json()
        self.assertEqual(small["settings"]["card_size"], 190)
        self.assertEqual(large["settings"]["card_size"], 380)

    def test_theme_setting_is_saved_to_application_state(self):
        self.assertEqual(self.client.get("/api/sources").get_json()["settings"]["theme"], "original")
        response = self.client.patch("/api/settings", json={"theme": "gloss"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["settings"]["theme"], "gloss")
        reloaded = VaultState(self.data, migrate_legacy=False)
        self.assertEqual(reloaded.data["settings"]["theme"], "gloss")

    def test_theme_setting_rejects_unknown_theme(self):
        response = self.client.patch("/api/settings", json={"theme": "neon"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.state.settings()["theme"], "original")

    def test_lora_manager_structured_widget_excludes_inactive_inventory(self):
        metadata = {
            "workflow": {
                "nodes": [{
                    "id": 61,
                    "type": "Lora Stacker (LoraManager)",
                    "mode": 0,
                    "widgets_values": [
                        "<lora:active_style:0.80> <lora:unused_style:1.00>",
                        [],
                        [
                            {"name": "active_style", "strength": 0.8, "clipStrength": 0.6, "active": True},
                            {"name": "unused_style", "strength": 1.0, "clipStrength": 1.0, "active": False},
                        ],
                    ],
                }],
            },
        }
        parsed = parse_comfy_metadata(metadata)
        self.assertEqual(parsed["loras"], [{
            "name": "active_style",
            "strength_model": 0.8,
            "strength_clip": 0.6,
        }])

    def test_standard_lora_loader_ignores_unrelated_empty_widget(self):
        metadata = {
            "workflow": {
                "nodes": [{
                    "id": 8,
                    "type": "LoraLoader",
                    "mode": 0,
                    "inputs": [],
                    "widgets_values": ["style.safetensors", 0.8, 0.6, []],
                }],
            },
        }
        parsed = parse_comfy_metadata(metadata)
        self.assertEqual(parsed["loras"], [{
            "name": "style.safetensors",
            "strength_model": 0.8,
            "strength_clip": 0.6,
        }])

    def test_split_sampler_nodes_and_generation_model_priority(self):
        graph = {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "pixel-dit.safetensors"}},
            "2": {"class_type": "SamplerCustom", "inputs": {"noise_seed": 3, "cfg": 1.0, "positive": ["6", 0], "negative": ["7", 0]}},
            "3": {"class_type": "BasicScheduler", "inputs": {"scheduler": "simple", "steps": 4}},
            "4": {"class_type": "AILab_QwenVL", "inputs": {"model_name": "Qwen3-VL-2B-Instruct", "seed": 99}},
            "5": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "lcm"}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": ["4", 0]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "low quality"}, "_meta": {"title": "Negative Prompt"}},
            "8": {"class_type": "ShowText|pysssss", "inputs": {"text_0": "a luminous mushroom forest", "text": ["4", 0]}},
        }
        parsed = parse_comfy_metadata({"prompt": graph})
        self.assertEqual(parsed["prompt"], "a luminous mushroom forest")
        self.assertEqual(parsed["negative_prompt"], "low quality")
        self.assertEqual(parsed["model"], "pixel-dit.safetensors")
        self.assertEqual(parsed["seed"], 3)
        self.assertEqual(parsed["steps"], 4)
        self.assertEqual(parsed["cfg"], 1.0)
        self.assertEqual(parsed["sampler"], "lcm")
        self.assertEqual(parsed["scheduler"], "simple")


if __name__ == "__main__":
    unittest.main()
