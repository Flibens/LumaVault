import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "lumavault" / "static" / "workflow-media.js"
INDEX = (ROOT / "lumavault" / "static" / "index.html").read_text(encoding="utf-8")


def preview_for(node, item):
    script = f"""
const media = require({json.dumps(str(MODULE))});
const result = media.workflowMediaPreview({json.dumps(node)}, {json.dumps(item)});
process.stdout.write(JSON.stringify(result));
"""
    completed = subprocess.run(
        ["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return json.loads(completed.stdout)


def previews_for(node, item):
    script = f"""
const media = require({json.dumps(str(MODULE))});
const result = media.workflowMediaPreviews({json.dumps(node)}, {json.dumps(item)});
process.stdout.write(JSON.stringify(result));
"""
    completed = subprocess.run(
        ["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return json.loads(completed.stdout)


class WorkflowMediaPreviewTests(unittest.TestCase):
    def test_load_image_uses_a_safe_relative_image_parameter(self):
        result = preview_for(
            {"type": "LoadImage", "params": [{"name": "image", "value": "inputs/portrait.png"}]},
            {"kind": "image", "source_id": "source", "path": "outputs/result.png"},
        )

        self.assertEqual(result, {
            "role": "input",
            "label": "Input image",
            "path": "inputs/portrait.png",
            "current": False,
        })

    def test_input_preview_rejects_paths_that_could_escape_or_fetch_remotely(self):
        unsafe = [
            "../secret.png", "/absolute.png", r"C:\\secret.png",
            "https://example.test/tracker.png", "//server/share.png", "bad\x00.png",
        ]
        for value in unsafe:
            with self.subTest(value=value):
                result = preview_for(
                    {"type": "LoadImage", "params": [{"name": "image", "value": value}]},
                    {"kind": "image", "source_id": "source", "path": "result.png"},
                )
                self.assertIsNone(result)

    def test_input_preview_ignores_non_media_values_and_unrelated_nodes(self):
        item = {"kind": "image", "source_id": "source", "path": "result.png"}
        self.assertIsNone(preview_for(
            {"type": "LoadImage", "params": [{"name": "image", "value": "notes.txt"}]}, item
        ))
        self.assertIsNone(preview_for(
            {"type": "CLIPTextEncode", "params": [{"name": "text", "value": "portrait.png"}]}, item
        ))

    def test_image_output_nodes_preview_the_current_gallery_item(self):
        result = preview_for(
            {"type": "SaveImage", "params": [{"name": "filename_prefix", "value": "LumaVault"}]},
            {"kind": "image", "source_id": "source", "path": "outputs/result.png"},
        )

        self.assertEqual(result, {
            "role": "output",
            "label": "Output image",
            "path": "outputs/result.png",
            "current": True,
        })

    def test_video_output_nodes_preview_the_current_video_frame(self):
        result = preview_for(
            {"type": "SaveVideo", "params": []},
            {"kind": "video", "source_id": "source", "path": "outputs/result.mp4"},
        )
        self.assertEqual(result, {
            "role": "output", "label": "Output video",
            "path": "outputs/result.mp4", "current": True,
        })

    def test_subgraph_first_frame_parameter_can_preview_an_input_image(self):
        result = preview_for(
            {"type": "future-subgraph", "title": "Image to Video", "params": [{"name": "first_frame", "value": "pasted/start.png"}]},
            {"kind": "video", "source_id": "source", "path": "outputs/result.mp4"},
        )
        self.assertEqual(result["role"], "input")
        self.assertEqual(result["path"], "pasted/start.png")

    def test_every_unique_image_input_is_returned_in_parameter_order(self):
        result = previews_for(
            {
                "type": "Multi-reference video",
                "params": [
                    {"name": "first_frame", "value": "pasted/start.png"},
                    {"name": "reference_image", "value": "pasted/style.webp"},
                    {"name": "start_image", "value": "pasted/start.png"},
                    {"name": "widget_4", "value": "pasted/end.jpg"},
                ],
            },
            {"kind": "video", "source_id": "source", "path": "outputs/result.mp4"},
        )

        self.assertEqual([preview["path"] for preview in result], [
            "pasted/start.png", "pasted/style.webp", "pasted/end.jpg",
        ])
        self.assertTrue(all(preview["role"] == "input" for preview in result))
        self.assertEqual([preview["label"] for preview in result], [
            "First frame", "Reference image", "Input image 3",
        ])

    def test_output_preview_is_not_attached_to_non_visual_current_media(self):
        result = preview_for(
            {"type": "SaveImage", "params": []},
            {"kind": "audio", "source_id": "source", "path": "song.mp3"},
        )
        self.assertIsNone(result)

    def test_media_helper_loads_before_the_application(self):
        helper = INDEX.index('<script src="/static/workflow-media.js"></script>')
        app = INDEX.index('<script src="/static/app.js"></script>')
        self.assertLess(helper, app)


if __name__ == "__main__":
    unittest.main()
