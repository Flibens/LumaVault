(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.LumaVaultWorkflowMedia = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const IMAGE_EXTENSIONS = new Set(["png", "jpg", "jpeg", "webp", "gif", "bmp", "tif", "tiff", "avif"]);
  const VIDEO_EXTENSIONS = new Set(["mp4", "webm", "mov", "mkv", "avi", "m4v"]);
  const INPUT_NODE = /(?:^|\b)(?:load|input).*image|image.*(?:loader|input)/i;
  const OUTPUT_NODE = /(?:save|preview|output).*(?:image|video)|(?:image|video).*(?:save|preview|output)/i;
  const INPUT_PARAM = /^(?:image|first_frame|start_image|reference_image|image_path|file|filename|path|upload|widget_\d+)$/i;

  function safeRelativeImagePath(value) {
    if (typeof value !== "string" || !value || value.length > 4096 || value.includes("\0")) return null;
    const path = value.trim().replaceAll("\\", "/");
    if (!path || path.startsWith("/") || path.startsWith("//") || /^[a-z][a-z0-9+.-]*:/i.test(path)) return null;
    const parts = path.split("/");
    if (parts.some(part => !part || part === "." || part === "..")) return null;
    const extension = parts[parts.length - 1].split(".").pop().toLowerCase();
    return IMAGE_EXTENSIONS.has(extension) ? parts.join("/") : null;
  }

  function inputLabel(name, index) {
    const value = String(name || "");
    if (/^(?:image|file|filename|path|upload)$/i.test(value)) return "Input image";
    if (/^widget_\d+$/i.test(value)) return `Input image ${index + 1}`;
    return value.replaceAll("_", " ").replace(/^\w/, character => character.toUpperCase()) || `Input image ${index + 1}`;
  }

  function workflowMediaPreviews(node, item) {
    if (!node || !item || !item.source_id) return [];
    const type = String(node.type || node.title || "");
    const params = Array.isArray(node.params) ? node.params : [];
    const previews = [];
    const seen = new Set();

    if (INPUT_NODE.test(type) || params.some(param => INPUT_PARAM.test(String(param?.name || "")))) {
      for (const param of params) {
        if (!param || !INPUT_PARAM.test(String(param.name || ""))) continue;
        const path = safeRelativeImagePath(param.value);
        if (!path || seen.has(path)) continue;
        seen.add(path);
        previews.push({ role: "input", label: inputLabel(param.name, previews.length), path, current: false });
      }
    }

    if (OUTPUT_NODE.test(type) && (item.kind === "image" || item.kind === "video")) {
      const path = String(item.path || "").trim().replaceAll("\\", "/");
      const extension = path.split(".").pop().toLowerCase();
      if (safeRelativeImagePath(path) || (VIDEO_EXTENSIONS.has(extension) && !path.startsWith("/") && !path.includes(".."))) {
        previews.push({ role: "output", label: item.kind === "video" ? "Output video" : "Output image", path, current: true });
      }
    }
    return previews;
  }

  function workflowMediaPreview(node, item) {
    return workflowMediaPreviews(node, item)[0] || null;
  }

  return { safeRelativeImagePath, workflowMediaPreviews, workflowMediaPreview };
});
