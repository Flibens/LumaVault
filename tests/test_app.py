import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from lumavault.app import VaultState, create_app
from lumavault.metadata import parse_comfy_metadata


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
            "nodes": [{"id": 4, "type": "KSampler", "mode": 0, "widgets_values": [4242, 28, 6.5, "euler", "normal"]}],
            "definitions": {"subgraphs": [{"id": "sg1", "name": "Detail Pass", "nodes": [{"id": 22, "type": "ImageScale", "mode": 0, "widgets_values": ["lanczos", 1536, 2048]}]}]},
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
