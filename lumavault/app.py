from __future__ import annotations

import hashlib
import json
import math
import mimetypes
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_file, send_from_directory
from PIL import Image, ImageOps
from send2trash import send2trash

from . import __version__
from .metadata import (
    build_workflow_graph,
    extract_metadata,
    extract_workflow_from_file,
    extract_workflow_nodes,
    parse_comfy_metadata,
    raw_metadata_for_display,
)

APP_NAME = "LumaVault"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".avif"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".mkv", ".avi"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | AUDIO_EXTENSIONS


def resource_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "lumavault"
    return Path(__file__).resolve().parent


def default_data_dir() -> Path:
    override = os.environ.get("LUMAVAULT_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / APP_NAME
    return Path.home() / f".{APP_NAME.lower()}"


def json_read(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)


def media_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    if suffix in AUDIO_EXTENSIONS:
        return "audio"
    return "image"


def safe_relative(path: Path, root: Path) -> str | None:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return None


class VaultState:
    def __init__(self, data_dir: Path | None = None, migrate_legacy: bool = True):
        self.data_dir = (data_dir or default_data_dir()).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "state.json"
        self.thumb_dir = self.data_dir / "thumbnails"
        self.thumb_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self._scan_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
        self.data = self._load_or_initialize(migrate_legacy)

    def _default_source_path(self) -> Path:
        candidates = [
            Path(r"C:\Comfy\ComfyUI\output"),
            Path.home() / "ComfyUI" / "output",
            Path.home() / "Pictures",
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate.resolve()
        return (Path.home() / "Pictures").resolve()

    def _load_or_initialize(self, migrate_legacy: bool) -> dict[str, Any]:
        existing = json_read(self.state_file, None)
        if isinstance(existing, dict) and isinstance(existing.get("sources"), list):
            existing.setdefault("favorites", [])
            settings = existing.setdefault("settings", {})
            if not isinstance(settings, dict):
                settings = {}
                existing["settings"] = settings
            settings.setdefault("card_size", 260)
            settings.setdefault("ui_scale", 1.0)
            return existing

        default_path = self._default_source_path()
        data: dict[str, Any] = {
            "version": 1,
            "sources": [{
                "id": "default",
                "name": "ComfyUI Output" if "ComfyUI" in str(default_path) else default_path.name,
                "path": str(default_path),
                "recursive": False,
            }],
            "favorites": [],
            "settings": {"card_size": 260, "ui_scale": 1.0},
            "legacy_migrated": False,
        }

        if migrate_legacy:
            legacy = Path(r"C:\Comfy\ComfyUI\user\comfyui-image-browser")
            folders = json_read(legacy / "folders.json", [])
            favorites = json_read(legacy / "favorites.json", [])
            if isinstance(folders, list):
                known = {"default"}
                for folder in folders:
                    if not isinstance(folder, dict):
                        continue
                    folder_id = str(folder.get("id") or f"source_{uuid.uuid4().hex[:8]}")
                    path_text = str(folder.get("path") or "").strip()
                    if not path_text or folder_id in known:
                        continue
                    path_obj = Path(path_text).expanduser()
                    data["sources"].append({
                        "id": folder_id,
                        "name": str(folder.get("name") or path_obj.name or "Media Folder"),
                        "path": str(path_obj),
                        "recursive": False,
                    })
                    known.add(folder_id)
            if isinstance(favorites, list):
                data["favorites"] = [str(item) for item in favorites if isinstance(item, str)]
            data["legacy_migrated"] = bool(folders or favorites)

        json_write(self.state_file, data)
        return data

    def save(self) -> None:
        with self.lock:
            json_write(self.state_file, self.data)

    def settings(self) -> dict[str, Any]:
        with self.lock:
            return dict(self.data.setdefault("settings", {"card_size": 260, "ui_scale": 1.0}))

    def update_settings(self, values: dict[str, Any]) -> dict[str, Any]:
        if "ui_scale" not in values:
            raise ValueError("No supported setting was provided.")
        try:
            ui_scale = float(values["ui_scale"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Interface size must be a number.") from exc
        if not math.isfinite(ui_scale):
            raise ValueError("Interface size must be a finite number.")
        ui_scale = min(2.0, max(0.8, round(ui_scale * 20) / 20))
        with self.lock:
            settings = self.data.setdefault("settings", {})
            settings["ui_scale"] = ui_scale
            settings.setdefault("card_size", 260)
            self.save()
            return dict(settings)

    def clear_scan_cache(self) -> None:
        with self.lock:
            self._scan_cache.clear()

    def sources(self) -> list[dict[str, Any]]:
        with self.lock:
            sources = []
            for source in self.data.get("sources", []):
                row = dict(source)
                path = Path(row.get("path", ""))
                row["available"] = path.exists() and path.is_dir()
                sources.append(row)
            return sources

    def source(self, source_id: str) -> dict[str, Any] | None:
        for source in self.data.get("sources", []):
            if source.get("id") == source_id:
                return source
        return None

    def resolve_file(self, source_id: str, relative_path: str) -> Path | None:
        source = self.source(source_id)
        if not source or not isinstance(relative_path, str) or not relative_path.strip():
            return None
        root = Path(source["path"]).expanduser().resolve()
        candidate = (root / Path(relative_path.replace("/", os.sep))).resolve()
        if safe_relative(candidate, root) is None:
            return None
        return candidate

    def favorite_key(self, source_id: str, relative_path: str) -> str:
        return f"{source_id}:{relative_path}"

    def is_favorite(self, source_id: str, relative_path: str) -> bool:
        return self.favorite_key(source_id, relative_path) in self.data.get("favorites", [])

    def toggle_favorite(self, source_id: str, relative_path: str) -> bool:
        key = self.favorite_key(source_id, relative_path)
        with self.lock:
            favorites = self.data.setdefault("favorites", [])
            if key in favorites:
                favorites.remove(key)
                value = False
            else:
                favorites.append(key)
                value = True
            self.save()
            return value

    def add_source(self, path_text: str, name: str | None = None, recursive: bool = True) -> dict[str, Any]:
        path = Path(path_text).expanduser().resolve()
        if not path.exists() or not path.is_dir():
            raise ValueError("That folder does not exist.")
        for source in self.data.get("sources", []):
            try:
                if Path(source["path"]).expanduser().resolve() == path:
                    return source
            except Exception:
                continue
        source = {
            "id": f"source_{uuid.uuid4().hex[:10]}",
            "name": (name or path.name or "Media Folder").strip(),
            "path": str(path),
            "recursive": bool(recursive),
        }
        with self.lock:
            self.data.setdefault("sources", []).append(source)
            self.clear_scan_cache()
            self.save()
        return source

    def update_source(self, source_id: str, values: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            source = self.source(source_id)
            if not source:
                raise KeyError("Source not found")
            if "name" in values and str(values["name"]).strip():
                source["name"] = str(values["name"]).strip()
            if "recursive" in values:
                source["recursive"] = bool(values["recursive"])
            self.clear_scan_cache()
            self.save()
            return source

    def remove_source(self, source_id: str) -> None:
        with self.lock:
            sources = self.data.get("sources", [])
            if len(sources) <= 1:
                raise ValueError("LumaVault needs at least one source folder.")
            if not any(source.get("id") == source_id for source in sources):
                raise KeyError("Source not found")
            self.data["sources"] = [source for source in sources if source.get("id") != source_id]
            prefix = f"{source_id}:"
            self.data["favorites"] = [fav for fav in self.data.get("favorites", []) if not fav.startswith(prefix)]
            self.clear_scan_cache()
            self.save()

    def scan(self, source_filter: str = "all") -> list[dict[str, Any]]:
        favorites = set(self.data.get("favorites", []))
        cached = self._scan_cache.get(source_filter)
        if cached and time.monotonic() - cached[0] < 30:
            return [dict(row, is_favorite=self.favorite_key(row["source_id"], row["path"]) in favorites) for row in cached[1]]

        targets = self.data.get("sources", []) if source_filter == "all" else [self.source(source_filter)]
        rows: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for source in targets:
            if not source:
                continue
            root = Path(source.get("path", "")).expanduser()
            if not root.exists() or not root.is_dir():
                continue
            iterator = root.rglob("*") if source.get("recursive", False) else root.iterdir()
            try:
                for path in iterator:
                    if not path.is_file() or path.suffix.lower() not in MEDIA_EXTENSIONS:
                        continue
                    relative = safe_relative(path, root)
                    if relative is None:
                        continue
                    key_tuple = (str(source.get("id")), relative)
                    if key_tuple in seen:
                        continue
                    seen.add(key_tuple)
                    try:
                        stat = path.stat()
                    except OSError:
                        continue
                    rows.append({
                        "name": path.name,
                        "path": relative,
                        "source_id": source.get("id"),
                        "source_name": source.get("name"),
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "kind": media_kind(path),
                        "is_favorite": False,
                    })
            except OSError:
                continue
        self._scan_cache[source_filter] = (time.monotonic(), rows)
        return [dict(row, is_favorite=self.favorite_key(row["source_id"], row["path"]) in favorites) for row in rows]

    def thumbnail_path(self, file_path: Path, width: int = 640) -> Path | None:
        try:
            stat = file_path.stat()
        except OSError:
            return None
        cache_key = f"{file_path.resolve()}|{stat.st_mtime_ns}|{stat.st_size}|{width}"
        digest = hashlib.sha1(cache_key.encode("utf-8", errors="ignore")).hexdigest()
        target = self.thumb_dir / f"{digest}.jpg"
        if target.exists():
            return target

        kind = media_kind(file_path)
        if kind == "image":
            try:
                with Image.open(file_path) as image:
                    image.seek(0)
                    image = ImageOps.exif_transpose(image)
                    image.thumbnail((width, width), Image.Resampling.LANCZOS)
                    if image.mode in ("RGBA", "LA"):
                        background = Image.new("RGB", image.size, (13, 14, 18))
                        alpha = image.getchannel("A")
                        background.paste(image.convert("RGB"), mask=alpha)
                        image = background
                    elif image.mode != "RGB":
                        image = image.convert("RGB")
                    image.save(target, "JPEG", quality=84, optimize=True)
                return target
            except Exception:
                return None

        if kind == "video":
            ffmpeg = os.environ.get("FFMPEG_PATH") or shutil.which("ffmpeg")
            if not ffmpeg:
                return None
            command = [
                ffmpeg, "-y", "-ss", "0.15", "-i", str(file_path), "-frames:v", "1",
                "-vf", f"scale='min({width},iw)':-2", "-q:v", "3", str(target),
            ]
            try:
                kwargs: dict[str, Any] = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "timeout": 20}
                if os.name == "nt":
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                subprocess.run(command, check=True, **kwargs)
                return target if target.exists() else None
            except Exception:
                return None
        return None


def create_app(state: VaultState | None = None) -> Flask:
    state = state or VaultState()
    static_dir = resource_dir() / "static"
    app = Flask(__name__, static_folder=None)
    app.config["VAULT_STATE"] = state

    @app.after_request
    def no_cache_for_api(response):
        if request.path.startswith("/api/") and request.path not in {"/api/file", "/api/thumb"}:
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def index():
        return send_from_directory(static_dir, "index.html")

    @app.get("/static/<path:filename>")
    def static_file(filename: str):
        return send_from_directory(static_dir, filename)

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "app": APP_NAME, "version": __version__})

    @app.post("/api/refresh")
    def refresh():
        state.clear_scan_cache()
        return jsonify({"success": True})

    @app.get("/api/sources")
    def sources():
        return jsonify({
            "sources": state.sources(),
            "settings": state.settings(),
            "data_dir": str(state.data_dir),
            "legacy_migrated": bool(state.data.get("legacy_migrated")),
        })

    @app.patch("/api/settings")
    def update_settings():
        try:
            settings = state.update_settings(request.get_json(silent=True) or {})
            return jsonify({"success": True, "settings": settings})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/sources")
    def add_source():
        payload = request.get_json(silent=True) or {}
        try:
            source = state.add_source(str(payload.get("path", "")), payload.get("name"), payload.get("recursive", True))
            return jsonify({"success": True, "source": source})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.patch("/api/sources/<source_id>")
    def update_source(source_id: str):
        try:
            source = state.update_source(source_id, request.get_json(silent=True) or {})
            return jsonify({"success": True, "source": source})
        except KeyError as exc:
            return jsonify({"error": str(exc)}), 404

    @app.delete("/api/sources/<source_id>")
    def remove_source(source_id: str):
        try:
            state.remove_source(source_id)
            return jsonify({"success": True})
        except KeyError as exc:
            return jsonify({"error": str(exc)}), 404
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.get("/api/media")
    def list_media():
        source_filter = request.args.get("source", "all")
        search = request.args.get("search", "").strip().lower()
        favorites_only = request.args.get("favorites", "false").lower() == "true"
        kind_filter = request.args.get("kind", "all")
        sort = request.args.get("sort", "date_desc")
        try:
            page = max(0, int(request.args.get("page", "0")))
            per_page = min(200, max(20, int(request.args.get("per_page", "80"))))
        except ValueError:
            return jsonify({"error": "Invalid pagination"}), 400

        rows = state.scan(source_filter)
        if search:
            rows = [row for row in rows if search in row["name"].lower() or search in row["path"].lower()]
        if favorites_only:
            rows = [row for row in rows if row["is_favorite"]]
        if kind_filter in {"image", "video", "audio"}:
            rows = [row for row in rows if row["kind"] == kind_filter]

        sorters = {
            "date_desc": (lambda row: row["modified"], True),
            "date_asc": (lambda row: row["modified"], False),
            "name_asc": (lambda row: row["name"].lower(), False),
            "name_desc": (lambda row: row["name"].lower(), True),
            "size_desc": (lambda row: row["size"], True),
        }
        key, reverse = sorters.get(sort, sorters["date_desc"])
        rows.sort(key=key, reverse=reverse)
        start = page * per_page
        chunk = rows[start:start + per_page]
        return jsonify({
            "items": chunk,
            "total": len(rows),
            "page": page,
            "has_more": start + per_page < len(rows),
        })

    def requested_file() -> tuple[Path | None, str, str]:
        source_id = request.args.get("source", "")
        relative_path = request.args.get("path", "")
        return state.resolve_file(source_id, relative_path), source_id, relative_path

    @app.get("/api/file")
    def serve_media():
        path, _, _ = requested_file()
        if not path or not path.exists() or not path.is_file():
            return jsonify({"error": "File not found"}), 404
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return send_file(path, mimetype=mime, conditional=True, max_age=3600)

    @app.get("/api/thumb")
    def thumbnail():
        path, _, _ = requested_file()
        if not path or not path.exists() or not path.is_file():
            return "", 404
        try:
            width = min(1200, max(240, int(request.args.get("width", "640"))))
        except ValueError:
            width = 640
        thumb = state.thumbnail_path(path, width)
        if not thumb:
            return "", 404
        return send_file(thumb, mimetype="image/jpeg", conditional=True, max_age=86400)

    @app.get("/api/metadata")
    def metadata():
        path, source_id, relative_path = requested_file()
        if not path or not path.exists() or not path.is_file():
            return jsonify({"error": "File not found"}), 404
        kind = media_kind(path)
        raw: dict[str, Any] = {}
        if kind == "image":
            raw = extract_metadata(path)
        workflow_obj, workflow_type = extract_workflow_from_file(path)
        if workflow_obj:
            raw["workflow" if workflow_type == "ui" else "prompt"] = workflow_obj
        parsed = parse_comfy_metadata(raw)
        nodes = extract_workflow_nodes(raw)
        dimensions: dict[str, Any] = {"width": None, "height": None}
        if kind == "image":
            try:
                with Image.open(path) as image:
                    dimensions = {"width": image.width, "height": image.height}
                    parsed["width"] = parsed.get("width") or image.width
                    parsed["height"] = parsed.get("height") or image.height
            except Exception:
                pass
        stat = path.stat()
        raw_display = raw_metadata_for_display(raw)
        return jsonify({
            "parsed": parsed,
            "workflow_nodes": nodes,
            "workflow_graph": build_workflow_graph(workflow_obj, workflow_type),
            "raw": raw_display,
            "dimensions": dimensions,
            "file_info": {
                "name": path.name,
                "path": str(path),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "kind": kind,
            },
            "is_favorite": state.is_favorite(source_id, relative_path),
        })

    @app.post("/api/favorite")
    def favorite():
        payload = request.get_json(silent=True) or {}
        source_id = str(payload.get("source_id", ""))
        relative_path = str(payload.get("path", ""))
        path = state.resolve_file(source_id, relative_path)
        if not path or not path.exists():
            return jsonify({"error": "File not found"}), 404
        return jsonify({"success": True, "is_favorite": state.toggle_favorite(source_id, relative_path)})

    @app.post("/api/action/<action>")
    def file_action(action: str):
        payload = request.get_json(silent=True) or {}
        source_id = str(payload.get("source_id", ""))
        relative_path = str(payload.get("path", ""))
        path = state.resolve_file(source_id, relative_path)
        if not path or not path.exists() or not path.is_file():
            return jsonify({"error": "File not found"}), 404
        try:
            if action == "reveal":
                if os.name != "nt":
                    return jsonify({"error": "Reveal is currently implemented for Windows."}), 400
                subprocess.Popen(["explorer.exe", "/select,", str(path)])
            elif action == "open":
                if os.name == "nt":
                    os.startfile(path)  # type: ignore[attr-defined]
                else:
                    subprocess.Popen(["xdg-open", str(path)])
            elif action == "delete":
                send2trash(str(path))
                state.clear_scan_cache()
                key = state.favorite_key(source_id, relative_path)
                with state.lock:
                    if key in state.data.get("favorites", []):
                        state.data["favorites"].remove(key)
                        state.save()
            else:
                return jsonify({"error": "Unknown action"}), 404
            return jsonify({"success": True})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return app
