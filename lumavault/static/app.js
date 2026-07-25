(() => {
  "use strict";

  const icons = {
    grid: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
    "grid-small": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/></svg>',
    star: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg>',
    settings: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.6v-.2h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/></svg>',
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 5v14M5 12h14"/></svg>',
    minus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 12h14"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>',
    refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7"/></svg>',
    compare: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M12 5v14M8 9l-2 3 2 3M16 9l2 3-2 3"/></svg>',
    menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    image: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 20"/></svg>',
    video: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="5" width="14" height="14" rx="2"/><path d="m17 10 4-2v8l-4-2"/></svg>',
    audio: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M9 18V5l10-2v13M9 9l10-2"/><circle cx="6" cy="18" r="3"/><circle cx="16" cy="16" r="3"/></svg>',
    more: '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m6 6 12 12M18 6 6 18"/></svg>',
    "chevron-left": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m15 18-6-6 6-6"/></svg>',
    "chevron-right": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m9 18 6-6-6-6"/></svg>',
    "folder-open": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 19V6a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v2"/><path d="m3 19 3-9h16l-3 9H3Z"/></svg>',
    external: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M14 4h6v6M20 4l-9 9"/><path d="M19 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h6"/></svg>',
    trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v5M14 11v5"/></svg>',
    copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/></svg>',
    play: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="m10 8 6 4-6 4V8Z"/></svg>'
  };

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[ch]);
  const icon = (name) => icons[name] || "";
  const UI_SCALE_KEY = "lumavault-ui-scale";
  let uiScaleSaveTimer = null;

  $$('[data-icon]').forEach(el => { el.innerHTML = icon(el.dataset.icon); });

  const state = {
    sources: [], source: "all", page: 0, hasMore: false, loading: false,
    search: "", sort: "date_desc", kind: "all", favorites: false,
    items: [], total: 0, compareMode: false, compareItems: [], selectedKeys: new Set(),
    viewerIndex: -1, metadata: null, dataDir: "", zoom: 1, panX: 0, panY: 0,
    panning: false, panStart: null, requestToken: 0, uiScale: 1
  };

  const gallery = $("#gallery");
  const content = $(".content");
  const emptyState = $("#emptyState");
  const loadMore = $("#loadMore");

  function applyUiScale(scale, persist = true) {
    const numeric = Number(scale);
    const next = Number.isFinite(numeric) ? Math.min(2, Math.max(.8, Math.round(numeric * 20) / 20)) : 1;
    state.uiScale = next;
    document.documentElement.style.setProperty("--ui-scale", String(next));
    const percent = Math.round(next * 100);
    const slider = $("#uiScale");
    const output = $("#uiScaleValue");
    if (slider) slider.value = String(percent);
    if (output) output.textContent = `${percent}%`;
    $$("[data-ui-scale]").forEach(button => button.classList.toggle("active", Number(button.dataset.uiScale) === next));
    syncUiScaleBreakpoints();
    if (persist) {
      try { localStorage.setItem(UI_SCALE_KEY, String(next)); } catch (_) { /* local storage can be unavailable */ }
      scheduleUiScaleSave(next);
    }
    requestAnimationFrame(syncCompareGeometry);
  }

  function scheduleUiScaleSave(scale) {
    clearTimeout(uiScaleSaveTimer);
    uiScaleSaveTimer = setTimeout(() => {
      api("/api/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ui_scale: scale })
      }).catch(error => toast(`Interface size could not be saved: ${error.message}`, "error"));
    }, 250);
  }

  function syncUiScaleBreakpoints() {
    const layoutWidth = window.innerWidth / state.uiScale;
    document.body.classList.toggle("ui-compact", layoutWidth <= 1050);
    document.body.classList.toggle("ui-mobile", layoutWidth <= 780);
  }

  function storedUiScale() {
    try { return Number(localStorage.getItem(UI_SCALE_KEY) || 1); }
    catch (_) { return 1; }
  }

  async function api(url, options = {}) {
    const response = await fetch(url, options);
    let data = {};
    try { data = await response.json(); } catch (_) { data = {}; }
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
    return data;
  }

  function queryUrl(base, values) {
    const params = new URLSearchParams();
    Object.entries(values).forEach(([key, value]) => params.set(key, String(value)));
    return `${base}?${params}`;
  }

  function mediaUrl(item, thumbnail = false) {
    return queryUrl(thumbnail ? "/api/thumb" : "/api/file", {
      source: item.source_id, path: item.path, ...(thumbnail ? { width: 720 } : {})
    });
  }

  function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) return "0 B";
    const units = ["B", "KB", "MB", "GB", "TB"];
    const index = Math.min(units.length - 1, Math.floor(Math.log(bytes) / Math.log(1024)));
    return `${(bytes / Math.pow(1024, index)).toFixed(index ? 1 : 0)} ${units[index]}`;
  }

  function formatDate(timestamp) {
    const date = new Date(Number(timestamp) * 1000);
    return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(date);
  }

  function toast(message, type = "success") {
    const el = document.createElement("div");
    el.className = `toast ${type}`;
    el.textContent = message;
    $("#toastStack").append(el);
    setTimeout(() => el.remove(), 3300);
  }

  async function loadSources() {
    const data = await api("/api/sources");
    state.sources = data.sources || [];
    state.dataDir = data.data_dir || "";
    const savedScale = Number(data.settings?.ui_scale);
    if (Number.isFinite(savedScale)) {
      applyUiScale(savedScale, false);
      try { localStorage.setItem(UI_SCALE_KEY, String(state.uiScale)); } catch (_) { /* local storage can be unavailable */ }
    }
    if (state.source !== "all" && !state.sources.some(source => source.id === state.source)) state.source = "all";
    renderSources();
    renderSourcesManager();
    $("#dataLocation").textContent = state.dataDir ? `Settings: ${state.dataDir}` : "";
  }

  function renderSources() {
    const root = $("#sourceList");
    const all = [{ id: "all", name: "All sources", available: true }, ...state.sources];
    root.innerHTML = all.map(source => `
      <button class="source-item ${state.source === source.id ? "active" : ""}" data-source="${escapeHtml(source.id)}" title="${escapeHtml(source.path || source.name)}">
        <span class="source-glyph"></span><span>${escapeHtml(source.name)}</span>${source.available === false ? "<i title='Folder unavailable'></i>" : ""}
      </button>`).join("");
    $$(".source-item", root).forEach(button => button.addEventListener("click", () => {
      state.source = button.dataset.source;
      state.favorites = false;
      syncViewButtons();
      renderSources();
      loadMedia(true);
      $("#sidebar").classList.remove("open");
    }));
  }

  function renderSourcesManager() {
    const root = $("#sourcesManagerList");
    root.innerHTML = state.sources.map(source => `
      <div class="source-manager-row" data-source-row="${escapeHtml(source.id)}">
        <div class="source-manager-copy"><strong>${escapeHtml(source.name)}</strong><span title="${escapeHtml(source.path)}">${escapeHtml(source.path)}</span></div>
        <label class="toggle-label"><input type="checkbox" data-recursive="${escapeHtml(source.id)}" ${source.recursive ? "checked" : ""}>Include subfolders</label>
        <button class="icon-button danger" data-remove-source="${escapeHtml(source.id)}" title="Remove source">${icon("trash")}</button>
      </div>`).join("");
    $$('[data-recursive]', root).forEach(input => input.addEventListener("change", async () => {
      try {
        await api(`/api/sources/${encodeURIComponent(input.dataset.recursive)}`, {
          method: "PATCH", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ recursive: input.checked })
        });
        await loadSources();
        loadMedia(true);
      } catch (error) { toast(error.message, "error"); }
    }));
    $$('[data-remove-source]', root).forEach(button => button.addEventListener("click", async () => {
      const source = state.sources.find(item => item.id === button.dataset.removeSource);
      if (!source || !confirm(`Remove “${source.name}” from LumaVault?\n\nNo files will be deleted.`)) return;
      try {
        await api(`/api/sources/${encodeURIComponent(source.id)}`, { method: "DELETE" });
        await loadSources();
        await updateFavoriteCount();
        loadMedia(true);
      } catch (error) { toast(error.message, "error"); }
    }));
  }

  async function chooseFolder() {
    let path = null;
    try {
      if (window.pywebview?.api?.choose_folder) path = await window.pywebview.api.choose_folder();
    } catch (_) { path = null; }
    if (!path) path = prompt("Paste the full path of the folder you want to add:", "C:\\Comfy\\ComfyUI\\output");
    if (!path) return;
    const pieces = path.replace(/[\\/]+$/, "").split(/[\\/]/);
    const name = pieces[pieces.length - 1] || "Media Folder";
    try {
      await api("/api/sources", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path, name, recursive: true })
      });
      await loadSources();
      state.source = state.sources.find(source => source.path.toLowerCase() === path.toLowerCase())?.id || "all";
      renderSources();
      $("#sourcesModal").classList.add("hidden");
      loadMedia(true);
      toast(`Added ${name}`);
    } catch (error) { toast(error.message, "error"); }
  }

  async function loadMedia(reset = false) {
    if (state.loading) return;
    if (!reset && !state.hasMore) return;
    if (reset) {
      state.page = 0;
      state.items = [];
      state.hasMore = false;
      state.selectedKeys.clear();
      gallery.innerHTML = "";
    }
    state.loading = true;
    const token = ++state.requestToken;
    loadMore.classList.remove("hidden");
    emptyState.classList.add("hidden");
    try {
      const url = queryUrl("/api/media", {
        source: state.source, search: state.search, favorites: state.favorites,
        kind: state.kind, sort: state.sort, page: state.page, per_page: 80
      });
      const data = await api(url);
      if (token !== state.requestToken) return;
      const startIndex = state.items.length;
      state.items.push(...(data.items || []));
      state.total = data.total || 0;
      state.hasMore = !!data.has_more;
      state.page += 1;
      renderMedia(data.items || [], startIndex, reset);
      updateSummary();
      emptyState.classList.toggle("hidden", state.total !== 0);
    } catch (error) {
      if (token === state.requestToken) {
        gallery.innerHTML = `<div class="muted-copy">Could not load the library: ${escapeHtml(error.message)}</div>`;
        toast(error.message, "error");
      }
    } finally {
      if (token === state.requestToken) {
        state.loading = false;
        loadMore.classList.toggle("hidden", !state.hasMore);
      }
    }
  }

  function audioBars() {
    return `<div class="audio-bars">${[18,34,48,28,42,54,24,44,32].map((height, i) => `<i style="--h:${height}px;--d:-${i * .13}s"></i>`).join("")}</div>`;
  }

  function renderMedia(items, startIndex, reset) {
    if (reset) gallery.innerHTML = "";
    const fragment = document.createDocumentFragment();
    items.forEach((item, offset) => {
      const index = startIndex + offset;
      const card = document.createElement("article");
      card.className = "media-card";
      card.dataset.index = String(index);
      card.dataset.key = `${item.source_id}:${item.path}`;
      const visual = item.kind === "audio"
        ? `<div class="media-placeholder audio">${audioBars()}</div>`
        : `<div class="media-placeholder">${icon(item.kind === "video" ? "video" : "image")}</div><img class="loading" src="${escapeHtml(mediaUrl(item, true))}" alt="" loading="lazy">`;
      card.innerHTML = `
        <div class="card-media">
          ${visual}
          ${item.kind !== "image" ? `<span class="kind-badge">${escapeHtml(item.kind.toUpperCase())}</span>` : ""}
          <button class="card-favorite ${item.is_favorite ? "active" : ""}" title="Favorite">${icon("star")}</button>
          <div class="compare-marker"><span></span></div>
        </div>
        <div class="card-info"><div class="card-copy"><span class="card-name" title="${escapeHtml(item.name)}">${escapeHtml(item.name)}</span><span class="card-meta">${escapeHtml(item.source_name)} · ${formatBytes(item.size)}</span></div><button class="card-menu" title="More">${icon("more")}</button></div>`;
      const image = $("img", card);
      if (image) {
        image.addEventListener("load", () => image.classList.remove("loading"));
        image.addEventListener("error", () => { image.classList.remove("loading"); image.classList.add("failed"); });
      }
      $(".card-favorite", card).addEventListener("click", event => { event.stopPropagation(); toggleFavorite(item, card); });
      $(".card-menu", card).addEventListener("click", event => { event.stopPropagation(); showContextMenu(event, item, card); });
      card.addEventListener("contextmenu", event => { event.preventDefault(); showContextMenu(event, item, card); });
      card.addEventListener("click", event => {
        if (state.compareMode) toggleCompare(item, card);
        else if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          toggleMultiSelection(item, card);
        } else if (state.selectedKeys.has(card.dataset.key)) {
          event.stopPropagation();
          showContextMenu(event, item, card);
        } else openViewer(Number(card.dataset.index));
      });
      fragment.append(card);
    });
    gallery.append(fragment);
    syncMultiSelectionCards();
  }

  function toggleMultiSelection(item, card) {
    const key = `${item.source_id}:${item.path}`;
    if (state.selectedKeys.has(key)) state.selectedKeys.delete(key);
    else state.selectedKeys.add(key);
    card.classList.toggle("multi-selected", state.selectedKeys.has(key));
  }

  function syncMultiSelectionCards() {
    $$(".media-card").forEach(card => card.classList.toggle("multi-selected", state.selectedKeys.has(card.dataset.key)));
  }

  function clearMultiSelection() {
    state.selectedKeys.clear();
    syncMultiSelectionCards();
  }

  function selectedItemsFor(item) {
    const key = `${item.source_id}:${item.path}`;
    return state.selectedKeys.has(key)
      ? state.items.filter(row => state.selectedKeys.has(`${row.source_id}:${row.path}`))
      : [item];
  }

  function updateSummary() {
    $("#resultCount").textContent = `${state.total.toLocaleString()} ${state.total === 1 ? "item" : "items"}`;
    const source = state.source === "all" ? null : state.sources.find(item => item.id === state.source);
    $("#activeSourceLabel").textContent = source?.name || "All sources";
    $("#viewTitle").textContent = state.favorites ? "Favorites" : (source?.name || "Library");
    $("#viewSubtitle").textContent = state.favorites ? "The work you want close at hand." : "Your generated work, in one place.";
  }

  async function updateFavoriteCount() {
    try {
      const data = await api(queryUrl("/api/media", { source: "all", favorites: true, kind: "all", sort: "date_desc", page: 0, per_page: 20 }));
      $("#favoriteCount").textContent = Number(data.total || 0).toLocaleString();
    } catch (_) { /* non-critical */ }
  }

  async function toggleFavorite(item, card = null) {
    try {
      const data = await api("/api/favorite", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_id: item.source_id, path: item.path })
      });
      item.is_favorite = data.is_favorite;
      if (card) $(".card-favorite", card)?.classList.toggle("active", data.is_favorite);
      const viewerButton = $("#viewerFavoriteBtn");
      if (state.viewerIndex >= 0 && state.items[state.viewerIndex] === item) {
        viewerButton.classList.toggle("favorite", data.is_favorite);
        viewerButton.innerHTML = `${icon("star")}<span>${data.is_favorite ? "Favorited" : "Favorite"}</span>`;
      }
      await updateFavoriteCount();
      if (state.favorites && !data.is_favorite) loadMedia(true);
    } catch (error) { toast(error.message, "error"); }
  }

  function syncViewButtons() {
    $("#libraryViewBtn").classList.toggle("active", !state.favorites);
    $("#favoritesViewBtn").classList.toggle("active", state.favorites);
  }

  function setCompareMode(enabled) {
    state.compareMode = enabled;
    $("#compareModeBtn").classList.toggle("active", enabled);
    $("#compareModeBtn").classList.toggle("primary", enabled);
    if (!enabled) clearCompare();
    else $("#selectionDock").classList.remove("hidden");
    syncCompareDock();
  }

  function toggleCompare(item, card) {
    if (item.kind !== "image") { toast("Comparison is available for images.", "error"); return; }
    const key = `${item.source_id}:${item.path}`;
    const existing = state.compareItems.findIndex(row => `${row.source_id}:${row.path}` === key);
    if (existing >= 0) state.compareItems.splice(existing, 1);
    else if (state.compareItems.length < 2) state.compareItems.push(item);
    else { toast("Choose only two images.", "error"); return; }
    syncCompareCards();
    syncCompareDock();
  }

  function syncCompareCards() {
    $$(".media-card").forEach(card => {
      card.classList.remove("selected-a", "selected-b");
      const marker = $(".compare-marker span", card);
      if (marker) marker.textContent = "";
      const index = state.compareItems.findIndex(item => `${item.source_id}:${item.path}` === card.dataset.key);
      if (index >= 0) {
        card.classList.add(index === 0 ? "selected-a" : "selected-b");
        if (marker) marker.textContent = index === 0 ? "A" : "B";
      }
    });
  }

  function syncCompareDock() {
    $("#selectionCount").textContent = String(state.compareItems.length);
    $("#openCompareBtn").disabled = state.compareItems.length !== 2;
    $("#selectionDock").classList.toggle("hidden", !state.compareMode);
  }

  function clearCompare() {
    state.compareItems = [];
    syncCompareCards();
    syncCompareDock();
  }

  function openCompare() {
    if (state.compareItems.length !== 2) return;
    const [a, b] = state.compareItems;
    $("#compareFront").src = mediaUrl(a);
    $("#compareBack").src = mediaUrl(b);
    $("#compareLabelA").textContent = `A · ${a.name}`;
    $("#compareLabelB").textContent = `B · ${b.name}`;
    $("#compareTitle").textContent = `${a.name}  /  ${b.name}`;
    $("#compareOverlay").classList.remove("hidden");
    updateCompareSlider(50);
    requestAnimationFrame(syncCompareGeometry);
  }

  function syncCompareGeometry() {
    const stage = $("#compareStage");
    const front = $("#compareFront");
    const back = $("#compareBack");
    if (!stage || !front || !back) return;
    [front, back].forEach(image => {
      image.style.width = `${stage.clientWidth}px`;
      image.style.height = `${stage.clientHeight}px`;
      image.style.maxWidth = "none";
      image.style.maxHeight = "none";
      image.style.left = "0";
      image.style.top = "0";
      image.style.transform = "none";
      image.style.objectFit = "contain";
    });
  }

  function updateCompareSlider(percent) {
    const value = Math.max(0, Math.min(100, percent));
    $("#compareFrontWrap").style.width = `${value}%`;
    $("#compareDivider").style.left = `${value}%`;
  }

  function currentViewerItem() { return state.items[state.viewerIndex]; }

  async function openViewer(index) {
    if (index < 0 || index >= state.items.length) return;
    state.viewerIndex = index;
    state.metadata = null;
    resetZoom();
    const item = currentViewerItem();
    $("#viewer").classList.remove("hidden");
    document.body.style.overflow = "hidden";
    $("#viewerName").textContent = item.name;
    $("#viewerKindBadge").textContent = item.kind.toUpperCase();
    $("#viewerPrev").style.visibility = index > 0 ? "visible" : "hidden";
    $("#viewerNext").style.visibility = (index < state.items.length - 1 || state.hasMore) ? "visible" : "hidden";
    const favorite = $("#viewerFavoriteBtn");
    favorite.classList.toggle("favorite", item.is_favorite);
    favorite.innerHTML = `${icon("star")}<span>${item.is_favorite ? "Favorited" : "Favorite"}</span>`;
    renderViewerMedia(item);
    $("#detailsPanel").innerHTML = '<div class="inspector-loading"><div><div class="spinner"></div><p>Reading metadata</p></div></div>';
    $("#workflowPanel").innerHTML = '<div class="inspector-loading">Reading workflow</div>';
    $("#rawPanel").innerHTML = '<div class="inspector-loading">Reading embedded data</div>';
    setInspectorTab("details");
    try {
      const data = await api(queryUrl("/api/metadata", { source: item.source_id, path: item.path }));
      if (currentViewerItem() !== item) return;
      state.metadata = data;
      renderMetadata(data, item);
    } catch (error) {
      $("#detailsPanel").innerHTML = `<p class="muted-copy">Metadata could not be read: ${escapeHtml(error.message)}</p>`;
      $("#workflowPanel").innerHTML = '<p class="muted-copy">No workflow data available.</p>';
      $("#rawPanel").innerHTML = '<p class="muted-copy">No raw metadata available.</p>';
    }
  }

  function renderViewerMedia(item) {
    const canvas = $("#mediaCanvas");
    if (item.kind === "video") canvas.innerHTML = `<video src="${escapeHtml(mediaUrl(item))}" controls autoplay loop></video>`;
    else if (item.kind === "audio") canvas.innerHTML = `<div class="audio-player"><div class="audio-art">${audioBars()}</div><audio src="${escapeHtml(mediaUrl(item))}" controls autoplay></audio></div>`;
    else {
      canvas.innerHTML = `<img id="viewerImage" class="zoomable" src="${escapeHtml(mediaUrl(item))}" alt="${escapeHtml(item.name)}">`;
      bindImagePan();
    }
    $("#zoomOutBtn").style.visibility = item.kind === "image" ? "visible" : "hidden";
    $("#zoomInBtn").style.visibility = item.kind === "image" ? "visible" : "hidden";
    $("#zoomResetBtn").style.visibility = item.kind === "image" ? "visible" : "hidden";
  }

  function settingCell(label, value, wide = false) {
    if (value === null || value === undefined || value === "") return "";
    return `<div class="meta-cell ${wide ? "wide" : ""}"><label>${escapeHtml(label)}</label><span>${escapeHtml(value)}</span></div>`;
  }

  function renderMetadata(data, item) {
    const parsed = data.parsed || {};
    const dimensions = data.dimensions || {};
    const file = data.file_info || {};
    const promptSection = parsed.prompt || parsed.negative_prompt ? `
      <section class="meta-section">
        <div class="meta-section-title"><span>Prompts</span>${parsed.prompt ? '<button data-copy-prompt="positive">Copy positive</button>' : ""}</div>
        ${parsed.prompt ? `<div class="prompt-box">${escapeHtml(parsed.prompt)}</div>` : ""}
        ${parsed.negative_prompt ? `<div class="meta-section-title"><span>Negative</span><button data-copy-prompt="negative">Copy negative</button></div><div class="prompt-box negative">${escapeHtml(parsed.negative_prompt)}</div>` : ""}
      </section>` : '<section class="meta-section"><div class="meta-section-title"><span>Prompts</span></div><p class="muted-copy">No prompt text was found in this file.</p></section>';
    const loras = Array.isArray(parsed.loras) && parsed.loras.length
      ? parsed.loras.map(lora => `<div class="lora-chip"><strong>${escapeHtml(lora.name)}</strong><span>MODEL ${escapeHtml(lora.strength_model)} · CLIP ${escapeHtml(lora.strength_clip)}</span></div>`).join("")
      : '<p class="muted-copy">No LoRAs detected.</p>';
    const size = dimensions.width && dimensions.height ? `${dimensions.width} × ${dimensions.height}` : (parsed.width && parsed.height ? `${parsed.width} × ${parsed.height}` : null);
    $("#detailsPanel").innerHTML = `
      ${promptSection}
      <section class="meta-section"><div class="meta-section-title"><span>Generation</span></div><div class="meta-grid">
        ${settingCell("Model", parsed.model, true)}${settingCell("Seed", parsed.seed)}${settingCell("Steps", parsed.steps)}${settingCell("CFG", parsed.cfg)}${settingCell("Sampler", parsed.sampler)}${settingCell("Scheduler", parsed.scheduler)}${settingCell("Canvas", size)}
      </div></section>
      <section class="meta-section"><div class="meta-section-title"><span>LoRAs</span></div>${loras}</section>
      <section class="meta-section"><div class="meta-section-title"><span>File</span><button data-copy-path>Copy path</button></div><div class="meta-grid">
        ${settingCell("Name", item.name, true)}${settingCell("Type", item.kind)}${settingCell("Size", formatBytes(file.size || item.size))}${settingCell("Modified", formatDate(file.modified || item.modified), true)}${settingCell("Location", file.path, true)}
      </div></section>`;
    $$('[data-copy-prompt]', $("#detailsPanel")).forEach(button => button.addEventListener("click", () => copyText(button.dataset.copyPrompt === "negative" ? parsed.negative_prompt : parsed.prompt, "Prompt copied")));
    $('[data-copy-path]', $("#detailsPanel"))?.addEventListener("click", () => copyText(file.path, "Path copied"));
    renderWorkflow(data.workflow_nodes || []);
    $("#rawPanel").innerHTML = `<section class="meta-section"><div class="meta-section-title"><span>Embedded metadata</span><button id="copyRawBtn">Copy JSON</button></div><pre class="raw-box">${escapeHtml(JSON.stringify(data.raw || {}, null, 2))}</pre></section>`;
    $("#copyRawBtn")?.addEventListener("click", () => copyText(JSON.stringify(data.raw || {}, null, 2), "Raw metadata copied"));
  }

  function renderWorkflow(nodes) {
    const panel = $("#workflowPanel");
    if (!Array.isArray(nodes) || !nodes.length) {
      panel.innerHTML = '<p class="muted-copy">No ComfyUI workflow nodes were found in this file.</p>';
      return;
    }
    panel.innerHTML = `<div class="workflow-search"><input id="workflowSearch" placeholder="Filter ${nodes.length} workflow nodes"></div><div id="workflowNodes"></div>`;
    const render = (filter = "") => {
      const term = filter.trim().toLowerCase();
      const visible = nodes.filter(node => !term || `${node.type} ${node.id} ${JSON.stringify(node.params)}`.toLowerCase().includes(term));
      $("#workflowNodes").innerHTML = visible.map((node, index) => `
        <article class="node-card"><button class="node-head"><span class="node-index">${index + 1}</span><span class="node-head-copy"><strong>${escapeHtml(node.type || "Unknown")}</strong><small>NODE ${escapeHtml(node.id || "N/A")} · ${(node.params || []).length} PARAMS</small></span>${icon("chevron-right")}</button>
          <ul class="node-params">${(node.params || []).map(param => `<li><b>${escapeHtml(param.name)}</b><span>${escapeHtml(param.value)}</span></li>`).join("") || "<li><span>No parameters</span></li>"}</ul></article>`).join("") || '<p class="muted-copy">No nodes match that filter.</p>';
      $$(".node-head", $("#workflowNodes")).forEach(button => button.addEventListener("click", () => button.closest(".node-card").classList.toggle("open")));
    };
    render();
    $("#workflowSearch").addEventListener("input", event => render(event.target.value));
  }

  function setInspectorTab(tab) {
    $$(".tabs button").forEach(button => button.classList.toggle("active", button.dataset.tab === tab));
    $$(".tab-panel").forEach(panel => panel.classList.toggle("active", panel.dataset.panel === tab));
    const inspectorBody = $(".inspector-body");
    if (inspectorBody) inspectorBody.scrollTop = 0;
  }

  async function navigateViewer(direction) {
    let index = state.viewerIndex + direction;
    if (index >= state.items.length && state.hasMore && !state.loading) {
      await loadMedia(false);
      index = state.viewerIndex + direction;
    }
    if (index >= 0 && index < state.items.length) openViewer(index);
  }

  function closeViewer() {
    $("#viewer").classList.add("hidden");
    $("#mediaCanvas").innerHTML = "";
    state.viewerIndex = -1;
    state.metadata = null;
    document.body.style.overflow = "";
    resetZoom();
  }

  function isPointOnRenderedMedia(event) {
    if (event.target.closest(".viewer-top, .viewer-nav, .audio-player")) return true;
    const video = event.target.closest("#mediaCanvas video");
    if (video) return true;
    const image = $("#viewerImage");
    if (!image || event.target !== image || !image.naturalWidth || !image.naturalHeight) return false;
    const rect = image.getBoundingClientRect();
    const scale = Math.min(rect.width / image.naturalWidth, rect.height / image.naturalHeight);
    const renderedWidth = image.naturalWidth * scale;
    const renderedHeight = image.naturalHeight * scale;
    const left = rect.left + (rect.width - renderedWidth) / 2;
    const top = rect.top + (rect.height - renderedHeight) / 2;
    return event.clientX >= left && event.clientX <= left + renderedWidth
      && event.clientY >= top && event.clientY <= top + renderedHeight;
  }

  function applyZoom() {
    const image = $("#viewerImage");
    if (!image) return;
    image.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.zoom})`;
    image.classList.toggle("panning", state.panning);
    $("#zoomResetBtn").textContent = `${Math.round(state.zoom * 100)}%`;
  }

  function setZoom(value) {
    state.zoom = Math.max(.2, Math.min(8, value));
    if (state.zoom <= 1) { state.panX = 0; state.panY = 0; }
    applyZoom();
  }

  function resetZoom() { state.zoom = 1; state.panX = 0; state.panY = 0; state.panning = false; applyZoom(); }

  function bindImagePan() {
    const image = $("#viewerImage");
    if (!image) return;
    image.addEventListener("mousedown", event => {
      if (event.button !== 0 || state.zoom <= 1) return;
      state.panning = true;
      state.panStart = { x: event.clientX, y: event.clientY, panX: state.panX, panY: state.panY };
      applyZoom();
      event.preventDefault();
    });
  }

  function removeDeletedItems(items) {
    const keys = new Set(items.map(item => `${item.source_id}:${item.path}`));
    const viewerItem = currentViewerItem();
    const removedCount = state.items.filter(item => keys.has(`${item.source_id}:${item.path}`)).length;
    if (viewerItem && keys.has(`${viewerItem.source_id}:${viewerItem.path}`)) closeViewer();
    state.items = state.items.filter(item => !keys.has(`${item.source_id}:${item.path}`));
    state.compareItems = state.compareItems.filter(item => !keys.has(`${item.source_id}:${item.path}`));
    keys.forEach(key => state.selectedKeys.delete(key));
    state.total = Math.max(0, state.total - removedCount);
    $$(".media-card").forEach(card => {
      if (keys.has(card.dataset.key)) card.remove();
      else card.dataset.index = String(state.items.findIndex(item => `${item.source_id}:${item.path}` === card.dataset.key));
    });
    syncCompareCards();
    syncCompareDock();
    syncMultiSelectionCards();
    updateSummary();
    emptyState.classList.toggle("hidden", state.total !== 0);
  }

  async function performAction(action, itemOrItems = currentViewerItem()) {
    const items = (Array.isArray(itemOrItems) ? itemOrItems : [itemOrItems]).filter(Boolean);
    if (!items.length) return;
    const results = await Promise.allSettled(items.map(item => api(`/api/action/${action}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_id: item.source_id, path: item.path })
    }).then(() => item)));
    const completed = results.filter(result => result.status === "fulfilled").map(result => result.value);
    const failed = results.filter(result => result.status === "rejected");
    if (action === "delete" && completed.length) {
      removeDeletedItems(completed);
      updateFavoriteCount();
      toast(completed.length === 1 ? "Moved to Recycle Bin" : `Moved ${completed.length} items to Recycle Bin`);
    } else if (action === "reveal" && completed.length) toast("Shown in Explorer");
    if (failed.length) toast(failed[0].reason?.message || `${failed.length} actions failed`, "error");
  }

  function showContextMenu(event, item, card) {
    const menu = $("#contextMenu");
    const targets = selectedItemsFor(item);
    const multiple = targets.length > 1;
    menu.innerHTML = `
      <button data-action="open-viewer">${icon("image")}Open viewer</button>
      <button data-action="open">${icon("external")}Open externally</button>
      <button data-action="reveal">${icon("folder-open")}Show in Explorer</button>
      <button data-action="copy">${icon("copy")}${multiple ? `Copy ${targets.length} paths` : "Copy path"}</button><hr>
      <button data-action="favorite">${icon("star")}${item.is_favorite ? "Remove favorite" : "Add favorite"}</button><hr>
      <button class="danger" data-action="delete">${icon("trash")}${multiple ? `Move ${targets.length} items to Recycle Bin` : "Move to Recycle Bin"}</button>`;
    const pointerX = event.clientX / state.uiScale;
    const pointerY = event.clientY / state.uiScale;
    const layoutWidth = window.innerWidth / state.uiScale;
    const layoutHeight = window.innerHeight / state.uiScale;
    menu.style.left = `${Math.max(6, Math.min(pointerX, layoutWidth - 202))}px`;
    menu.style.top = `${Math.max(6, Math.min(pointerY, layoutHeight - 250))}px`;
    menu.classList.remove("hidden");
    $$('[data-action]', menu).forEach(button => button.addEventListener("click", async () => {
      const action = button.dataset.action;
      menu.classList.add("hidden");
      if (action === "open-viewer") openViewer(Number(card.dataset.index));
      else if (action === "favorite") toggleFavorite(item, card);
      else if (action === "copy") copyText(targets.map(row => {
        const root = state.sources.find(source => source.id === row.source_id)?.path || "";
        return root ? `${root}\\${row.path.replaceAll("/", "\\")}` : row.path;
      }).join("\n"), multiple ? `${targets.length} paths copied` : "Path copied");
      else if (action === "delete") performAction("delete", targets);
      else performAction(action, item);
    }));
  }

  async function copyText(text, success = "Copied") {
    if (!text) return;
    try { await navigator.clipboard.writeText(String(text)); toast(success); }
    catch (_) {
      const area = document.createElement("textarea"); area.value = String(text); document.body.append(area); area.select(); document.execCommand("copy"); area.remove(); toast(success);
    }
  }

  let searchTimer = null;
  $("#searchInput").addEventListener("input", event => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { state.search = event.target.value.trim(); loadMedia(true); }, 220);
  });
  $("#sortSelect").addEventListener("change", event => { state.sort = event.target.value; loadMedia(true); });
  $("#cardSize").addEventListener("input", event => document.documentElement.style.setProperty("--card-size", `${event.target.value}px`));
  $$("#kindFilter button").forEach(button => button.addEventListener("click", () => {
    state.kind = button.dataset.kind;
    $$("#kindFilter button").forEach(row => row.classList.toggle("active", row === button));
    loadMedia(true);
  }));
  $("#libraryViewBtn").addEventListener("click", () => { state.favorites = false; syncViewButtons(); loadMedia(true); });
  $("#favoritesViewBtn").addEventListener("click", () => { state.favorites = true; syncViewButtons(); loadMedia(true); });
  $("#refreshBtn").addEventListener("click", async () => {
    try { await api("/api/refresh", { method: "POST" }); } catch (_) { /* refresh still reloads UI */ }
    await loadSources();
    loadMedia(true);
    toast("Library refreshed");
  });
  $("#compareModeBtn").addEventListener("click", () => setCompareMode(!state.compareMode));
  $("#clearCompareBtn").addEventListener("click", clearCompare);
  $("#openCompareBtn").addEventListener("click", openCompare);
  $("#closeCompareOverlay").addEventListener("click", () => $("#compareOverlay").classList.add("hidden"));
  $("#compareStage").addEventListener("pointerdown", event => {
    const stage = event.currentTarget;
    const move = ev => updateCompareSlider((ev.clientX - stage.getBoundingClientRect().left) / stage.clientWidth * 100);
    move(event); stage.setPointerCapture(event.pointerId); stage.addEventListener("pointermove", move);
    stage.addEventListener("pointerup", () => stage.removeEventListener("pointermove", move), { once: true });
  });
  $("#compareFront").addEventListener("load", syncCompareGeometry);
  $("#compareBack").addEventListener("load", syncCompareGeometry);
  window.addEventListener("resize", syncCompareGeometry);

  $("#addSourceBtn").addEventListener("click", chooseFolder);
  $("#emptyAddBtn").addEventListener("click", chooseFolder);
  $("#modalAddSourceBtn").addEventListener("click", chooseFolder);
  $("#manageSourcesBtn").addEventListener("click", () => $("#sourcesModal").classList.remove("hidden"));
  $("#closeSourcesBtn").addEventListener("click", () => $("#sourcesModal").classList.add("hidden"));
  $("#sourcesModal").addEventListener("click", event => { if (event.target.id === "sourcesModal") event.currentTarget.classList.add("hidden"); });
  $("#mobileMenuBtn").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
  $("#uiScale").addEventListener("input", event => applyUiScale(Number(event.target.value) / 100));
  $$("[data-ui-scale]").forEach(button => button.addEventListener("click", () => applyUiScale(Number(button.dataset.uiScale))));
  window.addEventListener("resize", syncUiScaleBreakpoints);

  $("#closeViewerBtn").addEventListener("click", closeViewer);
  $("#viewerStage").addEventListener("click", event => { if (!isPointOnRenderedMedia(event)) closeViewer(); });
  $("#viewerPrev").addEventListener("click", () => navigateViewer(-1));
  $("#viewerNext").addEventListener("click", () => navigateViewer(1));
  $("#viewerFavoriteBtn").addEventListener("click", () => toggleFavorite(currentViewerItem()));
  $("#revealBtn").addEventListener("click", () => performAction("reveal"));
  $("#openExternalBtn").addEventListener("click", () => performAction("open"));
  $("#deleteBtn").addEventListener("click", () => performAction("delete"));
  $("#zoomInBtn").addEventListener("click", () => setZoom(state.zoom + .2));
  $("#zoomOutBtn").addEventListener("click", () => setZoom(state.zoom - .2));
  $("#zoomResetBtn").addEventListener("click", resetZoom);
  $("#viewerStage").addEventListener("wheel", event => { if (!$("#viewerImage")) return; event.preventDefault(); setZoom(state.zoom + (event.deltaY < 0 ? .15 : -.15)); }, { passive: false });
  $$(".tabs button").forEach(button => button.addEventListener("click", () => setInspectorTab(button.dataset.tab)));

  document.addEventListener("mousemove", event => {
    if (!state.panning || !state.panStart) return;
    state.panX = state.panStart.panX + event.clientX - state.panStart.x;
    state.panY = state.panStart.panY + event.clientY - state.panStart.y;
    applyZoom();
  });
  document.addEventListener("mouseup", () => { if (state.panning) { state.panning = false; applyZoom(); } });
  document.addEventListener("click", event => { if (!event.target.closest("#contextMenu") && !event.target.closest(".card-menu")) $("#contextMenu").classList.add("hidden"); });
  content.addEventListener("scroll", () => { if (!state.loading && state.hasMore && content.scrollTop + content.clientHeight > content.scrollHeight - 700) loadMedia(false); });
  document.addEventListener("keydown", event => {
    const typing = ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName);
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") { event.preventDefault(); $("#searchInput").focus(); }
    if (event.key === "Escape") {
      $("#contextMenu").classList.add("hidden");
      if (!$("#sourcesModal").classList.contains("hidden")) $("#sourcesModal").classList.add("hidden");
      else if (!$("#compareOverlay").classList.contains("hidden")) $("#compareOverlay").classList.add("hidden");
      else if (!$("#viewer").classList.contains("hidden")) closeViewer();
      else if (state.selectedKeys.size) clearMultiSelection();
    }
    if (!typing && !$("#viewer").classList.contains("hidden")) {
      if (event.key === "ArrowLeft") navigateViewer(-1);
      if (event.key === "ArrowRight") navigateViewer(1);
      if (event.key.toLowerCase() === "f") toggleFavorite(currentViewerItem());
    }
  });

  async function initialize() {
    try {
      await loadSources();
      await Promise.all([loadMedia(true), updateFavoriteCount()]);
    } catch (error) {
      gallery.innerHTML = `<p class="muted-copy">LumaVault could not start: ${escapeHtml(error.message)}</p>`;
      toast(error.message, "error");
    }
  }

  applyUiScale(storedUiScale(), false);
  initialize();
})();
