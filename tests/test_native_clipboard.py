import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from main import NativeApi, _image_clipboard_payloads


class NativeClipboardTests(unittest.TestCase):
    def test_image_payload_contains_windows_dib_and_original_file_drop(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.png"
            Image.new("RGB", (3, 2), (24, 96, 180)).save(path)

            dib, file_drop = _image_clipboard_payloads(path)

            self.assertFalse(dib.startswith(b"BM"))
            self.assertEqual(struct.unpack_from("<I", dib)[0], 40)
            file_list_offset = struct.unpack_from("<I", file_drop)[0]
            dropped_path = file_drop[file_list_offset:].decode("utf-16-le").rstrip("\0")
            self.assertEqual(dropped_path, str(path.resolve()))

    def test_native_api_resolves_source_path_before_copying_image(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.jpg"
            Image.new("RGB", (2, 2), (200, 100, 25)).save(path)

            class State:
                def resolve_file(self, source_id, relative_path):
                    self.arguments = (source_id, relative_path)
                    return path

            state = State()
            with patch("main._copy_image_to_windows_clipboard", return_value=["CF_DIB", "CF_HDROP"]) as copy:
                result = NativeApi(state).copy_image("source-one", "nested/sample.jpg")

            self.assertEqual(state.arguments, ("source-one", "nested/sample.jpg"))
            copy.assert_called_once_with(path)
            self.assertEqual(result, {"success": True, "formats": ["CF_DIB", "CF_HDROP"]})

    def test_native_api_rejects_missing_files_without_touching_clipboard(self):
        class State:
            def resolve_file(self, source_id, relative_path):
                return None

        with patch("main._copy_image_to_windows_clipboard") as copy:
            result = NativeApi(State()).copy_image("missing", "image.png")

        copy.assert_not_called()
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Image not found.")


if __name__ == "__main__":
    unittest.main()
