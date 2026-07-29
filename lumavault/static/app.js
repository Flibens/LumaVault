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
  const WORKFLOW_DOM_BUDGET = 20000;
  const NODE_LIST_DOM_BUDGET = 20000;
  const NODE_LIST_MAX_CARDS = 2000;
  let uiScaleSaveTimer = null;
  let cardSizeSaveTimer = null;

  $$('[data-icon]').forEach(el => { el.innerHTML = icon(el.dataset.icon); });

  const state = {
    sources: [], source: "all", page: 0, hasMore: false, loading: false, reloadQueued: false,
    search: "", searchField: "filename", sort: "date_desc", kind: "all", favorites: false,
    items: [], total: 0, compareMode: false, compareItems: [], selectedKeys: new Set(),
    compareZoom: 1, comparePanX: 0, comparePanY: 0, comparePanning: false, comparePanStart: null,
    viewerIndex: -1, metadata: null, dataDir: "", zoom: 1, panX: 0, panY: 0,
    panning: false, panStart: null, requestToken: 0, uiScale: 1, cardSize: 260, theme: "original", workflowView: null
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

  function applyCardSize(size, persist = true) {
    const numeric = Number(size);
    const next = Number.isFinite(numeric) ? Math.min(380, Math.max(190, Math.round(numeric))) : 260;
    state.cardSize = next;
    document.documentElement.style.setProperty("--card-size", `${next}px`);
    const slider = $("#cardSize");
    if (slider) slider.value = String(next);
    if (persist) {
      clearTimeout(cardSizeSaveTimer);
      cardSizeSaveTimer = setTimeout(() => {
        api("/api/settings", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ card_size: size })
        }).catch(error => toast(`Grid size could not be saved: ${error.message}`, "error"));
      }, 250);
    }
  }

  function syncNativeWindowClass() {
    document.documentElement.classList.toggle("native-window", Boolean(window.pywebview?.api));
  }

  function applyTheme(theme, persist = true) {
    const next = theme === "gloss" ? "gloss" : "original";
    state.theme = next;
    document.documentElement.dataset.theme = next;
    document.body.classList.toggle("theme-gloss", next === "gloss");
    $$('[data-theme-choice]').forEach(button => {
      const active = button.dataset.themeChoice === next;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    if (persist) {
      api("/api/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme: next })
      }).catch(error => toast(`Theme could not be saved: ${error.message}`, "error"));
    }
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
    const savedCardSize = Number(data.settings?.card_size);
    if (Number.isFinite(savedCardSize)) applyCardSize(savedCardSize, false);
    applyTheme(data.settings?.theme, false);
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
    if (state.loading) {
      if (reset) state.reloadQueued = true;
      return;
    }
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
    if (reset && state.search && state.searchField !== "filename") {
      const labels = { prompt: "prompts", lora: "LoRAs", model: "models", all: "metadata" };
      $("#resultCount").textContent = `Searching ${labels[state.searchField] || "metadata"}…`;
    }
    try {
      const url = queryUrl("/api/media", {
        source: state.source, search: state.search, search_field: state.searchField, favorites: state.favorites,
        kind: state.kind, sort: state.sort, page: state.page, per_page: 80
      });
      const data = await api(url);
      if (token !== state.requestToken || state.reloadQueued) return;
      const startIndex = state.items.length;
      state.items.push(...(data.items || []));
      state.total = data.total || 0;
      state.hasMore = !!data.has_more;
      state.page += 1;
      renderMedia(data.items || [], startIndex, reset);
      updateSummary();
      emptyState.classList.toggle("hidden", state.total !== 0);
    } catch (error) {
      if (token === state.requestToken && !state.reloadQueued) {
        gallery.innerHTML = `<div class="muted-copy">Could not load the library: ${escapeHtml(error.message)}</div>`;
        toast(error.message, "error");
      }
    } finally {
      if (token === state.requestToken) {
        state.loading = false;
        loadMore.classList.toggle("hidden", !state.hasMore);
        if (state.reloadQueued) {
          state.reloadQueued = false;
          loadMedia(true);
        }
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
    resetCompareView();
    updateCompareSlider(50);
    requestAnimationFrame(syncCompareGeometry);
  }

  function clampComparePan() {
    const stage = $("#compareStage");
    if (!stage || state.compareZoom <= 1) {
      state.comparePanX = 0;
      state.comparePanY = 0;
      return;
    }
    const maxX = stage.clientWidth * (state.compareZoom - 1) / 2;
    const maxY = stage.clientHeight * (state.compareZoom - 1) / 2;
    state.comparePanX = Math.max(-maxX, Math.min(maxX, state.comparePanX));
    state.comparePanY = Math.max(-maxY, Math.min(maxY, state.comparePanY));
  }

  function applyCompareTransform() {
    const front = $("#compareFront");
    const back = $("#compareBack");
    if (!front || !back) return;
    clampComparePan();
    [front, back].forEach(image => {
      image.style.transform = `translate(${state.comparePanX}px, ${state.comparePanY}px) scale(${state.compareZoom})`;
    });
    $("#compareZoomResetBtn").textContent = `${Math.round(state.compareZoom * 100)}%`;
    const stage = $("#compareStage");
    stage.classList.toggle("zoomed", state.compareZoom > 1);
    stage.classList.toggle("panning", state.comparePanning);
  }

  function comparePointerPosition(clientX, clientY) {
    const stage = $("#compareStage");
    const rect = stage.getBoundingClientRect();
    const scaleX = rect.width ? stage.clientWidth / rect.width : 1;
    const scaleY = rect.height ? stage.clientHeight / rect.height : 1;
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY,
      scaleX, scaleY
    };
  }

  function setCompareZoom(value, clientX = null, clientY = null) {
    const previous = state.compareZoom;
    const next = Math.max(1, Math.min(8, value));
    const stage = $("#compareStage");
    if (stage && next > 1 && clientX !== null && clientY !== null) {
      const position = comparePointerPosition(clientX, clientY);
      const pointX = position.x - stage.clientWidth / 2;
      const pointY = position.y - stage.clientHeight / 2;
      const worldX = (pointX - state.comparePanX) / previous;
      const worldY = (pointY - state.comparePanY) / previous;
      state.comparePanX = pointX - worldX * next;
      state.comparePanY = pointY - worldY * next;
    }
    state.compareZoom = next;
    applyCompareTransform();
  }

  function resetCompareView() {
    state.compareZoom = 1;
    state.comparePanX = 0;
    state.comparePanY = 0;
    state.comparePanning = false;
    state.comparePanStart = null;
    applyCompareTransform();
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
      image.style.objectFit = "contain";
    });
    applyCompareTransform();
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
    document.body.classList.add("viewer-open");
    document.body.style.overflow = "hidden";
    $("#viewerName").textContent = item.name;
    $("#viewerKindBadge").textContent = item.kind.toUpperCase();
    $("#viewerPrev").style.visibility = index > 0 ? "visible" : "hidden";
    $("#viewerNext").style.visibility = (index < state.items.length - 1 || state.hasMore) ? "visible" : "hidden";
    const favorite = $("#viewerFavoriteBtn");
    favorite.classList.toggle("favorite", item.is_favorite);
    favorite.innerHTML = `${icon("star")}<span>${item.is_favorite ? "Favorited" : "Favorite"}</span>`;
    $("#copyImageBtn").classList.toggle("hidden", item.kind !== "image");
    renderViewerMedia(item);
    $("#detailsPanel").innerHTML = '<div class="inspector-loading"><div><div class="spinner"></div><p>Reading metadata</p></div></div>';
    $("#nodesPanel").innerHTML = '<div class="inspector-loading">Reading workflow nodes</div>';
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
      $("#nodesPanel").innerHTML = '<p class="muted-copy">No workflow nodes available.</p>';
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

  function settingCell(label, value, wide = false, copyValue = null, copySuccess = "Copied") {
    if (value === null || value === undefined || value === "") return "";
    const copyButton = copyValue === null || copyValue === undefined
      ? ""
      : `<button class="meta-copy-button" data-copy-cell="${escapeHtml(copyValue)}" data-copy-success="${escapeHtml(copySuccess)}" title="Copy ${escapeHtml(label)}" aria-label="Copy ${escapeHtml(label)}">${icon("copy")}</button>`;
    return `<div class="meta-cell ${wide ? "wide" : ""}"><label>${escapeHtml(label)}</label>${copyButton}<span>${escapeHtml(value)}</span></div>`;
  }

  function renderMetadata(data, item) {
    const parsed = data.parsed || {};
    const dimensions = data.dimensions || {};
    const file = data.file_info || {};
    const promptSection = parsed.prompt || parsed.negative_prompt ? `
      <section class="meta-section">
        <div class="meta-section-title"><span>Prompts</span>${parsed.prompt ? `<button class="meta-copy-button" data-copy-prompt="positive" title="Copy positive prompt" aria-label="Copy positive prompt">${icon("copy")}</button>` : ""}</div>
        ${parsed.prompt ? `<div class="prompt-box">${escapeHtml(parsed.prompt)}</div>` : ""}
        ${parsed.negative_prompt ? `<div class="meta-section-title"><span>Negative</span><button class="meta-copy-button" data-copy-prompt="negative" title="Copy negative prompt" aria-label="Copy negative prompt">${icon("copy")}</button></div><div class="prompt-box negative">${escapeHtml(parsed.negative_prompt)}</div>` : ""}
      </section>` : '<section class="meta-section"><div class="meta-section-title"><span>Prompts</span></div><p class="muted-copy">No prompt text was found in this file.</p></section>';
    const loras = Array.isArray(parsed.loras) && parsed.loras.length
      ? parsed.loras.slice(0, 128).map((lora, index) => `<div class="lora-chip"><strong>${escapeHtml(lora.name)}</strong><button class="meta-copy-button" data-copy-lora="${index}" title="Copy LoRA name" aria-label="Copy LoRA name">${icon("copy")}</button><span>MODEL ${escapeHtml(lora.strength_model)} · CLIP ${escapeHtml(lora.strength_clip)}</span></div>`).join("")
      : '<p class="muted-copy">No LoRAs detected.</p>';
    const size = dimensions.width && dimensions.height ? `${dimensions.width} × ${dimensions.height}` : (parsed.width && parsed.height ? `${parsed.width} × ${parsed.height}` : null);
    $("#detailsPanel").innerHTML = `
      ${promptSection}
      <section class="meta-section"><div class="meta-section-title"><span>Generation</span></div><div class="meta-grid">
        ${settingCell("Model", parsed.model, true)}${settingCell("Seed", parsed.seed, false, parsed.seed, "Seed copied")}${settingCell("Steps", parsed.steps)}${settingCell("CFG", parsed.cfg)}${settingCell("Sampler", parsed.sampler)}${settingCell("Scheduler", parsed.scheduler)}${settingCell("Canvas", size)}
      </div></section>
      <section class="meta-section"><div class="meta-section-title"><span>LoRAs</span></div>${loras}</section>
      <section class="meta-section"><div class="meta-section-title"><span>File</span><button data-copy-path>Copy path</button></div><div class="meta-grid">
        ${settingCell("Name", item.name, true)}${settingCell("Type", item.kind)}${settingCell("Size", formatBytes(file.size || item.size))}${settingCell("Modified", formatDate(file.modified || item.modified), true)}${settingCell("Location", file.path, true)}
      </div></section>`;
    $$('[data-copy-prompt]', $("#detailsPanel")).forEach(button => button.addEventListener("click", () => copyText(button.dataset.copyPrompt === "negative" ? parsed.negative_prompt : parsed.prompt, "Prompt copied")));
    $$('[data-copy-cell]', $("#detailsPanel")).forEach(button => button.addEventListener("click", () => copyText(button.dataset.copyCell, button.dataset.copySuccess)));
    $$('[data-copy-lora]', $("#detailsPanel")).forEach(button => button.addEventListener("click", () => copyText(parsed.loras[Number(button.dataset.copyLora)]?.name, "LoRA name copied")));
    $('[data-copy-path]', $("#detailsPanel"))?.addEventListener("click", () => copyText(file.path, "Path copied"));
    renderNodeList(data.workflow_nodes || []);
    renderWorkflow(data.workflow_graph);
    $("#rawPanel").innerHTML = `<section class="meta-section"><div class="meta-section-title"><span>Embedded metadata</span><button id="copyRawBtn">Copy JSON</button></div><pre class="raw-box">${escapeHtml(JSON.stringify(data.raw || {}, null, 2))}</pre></section>`;
    $("#copyRawBtn")?.addEventListener("click", () => copyText(JSON.stringify(data.raw || {}, null, 2), "Raw metadata copied"));
  }

  function renderNodeList(nodes) {
    const panel = $("#nodesPanel");
    if (!Array.isArray(nodes) || !nodes.length) {
      panel.innerHTML = '<p class="muted-copy">No ComfyUI workflow nodes were found in this file.</p>';
      return;
    }
    panel.innerHTML = `<div class="workflow-search"><input id="workflowNodeSearch" placeholder="Filter ${nodes.length} workflow nodes"></div><div id="workflowNodeList"></div>`;
    const render = (filter = "") => {
      const term = filter.trim().toLowerCase();
      const visible = nodes.filter(node => !term || `${node.type} ${node.id} ${JSON.stringify(node.params)}`.toLowerCase().includes(term));
      const renderedNodes = visible.slice(0, NODE_LIST_MAX_CARDS);
      let remainingNodeListRecords = Math.max(0, NODE_LIST_DOM_BUDGET - renderedNodes.length);
      const cards = renderedNodes.map((node, index) => {
        const sourceParams = Array.isArray(node.params) ? node.params : [];
        const params = sourceParams.slice(0, remainingNodeListRecords);
        remainingNodeListRecords = Math.max(0, remainingNodeListRecords - params.length);
        let paramMarkup = params.map(param => `<li><b>${escapeHtml(param.name)}</b><span>${escapeHtml(param.value)}</span></li>`).join("");
        if (!sourceParams.length && remainingNodeListRecords > 0) {
          paramMarkup = "<li><span>No parameters</span></li>";
          remainingNodeListRecords -= 1;
        }
        return `<article class="node-card"><button class="node-head"><span class="node-index">${index + 1}</span><span class="node-head-copy"><strong>${escapeHtml(node.type || "Unknown")}</strong><small>NODE ${escapeHtml(node.id || "N/A")} · ${sourceParams.length} PARAMS</small></span>${icon("chevron-right")}</button>
          <ul class="node-params">${paramMarkup}</ul></article>`;
      }).join("");
      const limited = visible.length > renderedNodes.length ? `<p class="muted-copy">Showing ${renderedNodes.length} of ${visible.length} matching nodes. Refine the filter to see others.</p>` : "";
      $("#workflowNodeList").innerHTML = cards ? `${limited}${cards}` : '<p class="muted-copy">No nodes match that filter.</p>';
      $$(".node-head", $("#workflowNodeList")).forEach(button => button.addEventListener("click", () => button.closest(".node-card").classList.toggle("open")));
    };
    render();
    $("#workflowNodeSearch").addEventListener("input", event => render(event.target.value));
  }

  function workflowPortColor(type) {
    const value = String(type || "").toUpperCase();
    if (value.includes("MODEL")) return "#b985ff";
    if (value.includes("CLIP")) return "#f1c75b";
    if (value.includes("CONDITION")) return "#f28b68";
    if (value.includes("LATENT")) return "#ff78b7";
    if (value.includes("IMAGE")) return "#61d5e8";
    if (value.includes("MASK")) return "#79d69f";
    if (value.includes("VAE")) return "#ef8fbd";
    return "#8d89ff";
  }

  function workflowNodeAccent(type) {
    const value = String(type || "").toLowerCase();
    if (value.includes("sampler")) return "#7772ff";
    if (value.includes("loader") || value.includes("checkpoint")) return "#b985ff";
    if (value.includes("text") || value.includes("prompt") || value.includes("clip")) return "#e69a65";
    if (value.includes("image") || value.includes("latent") || value.includes("vae")) return "#48bfd3";
    return "#7772ff";
  }

  function workflowParamHeight(params) {
    if (!params.length) return 0;
    return 14 + params.reduce((height, param) => height + (param.multiline ? 104 : 22), 0);
  }

  function applyWorkflowTransform() {
    const view = state.workflowView;
    if (!view?.scene) return;
    view.scene.style.transform = `translate(${view.x}px, ${view.y}px) scale(${view.scale})`;
    const label = $("#workflowZoomValue");
    if (label) label.textContent = `${Math.round(view.scale * 100)}%`;
  }

  function fitWorkflowGraph() {
    const view = state.workflowView;
    if (!view?.canvas?.clientWidth || !view.canvas.clientHeight) return;
    const padding = 54;
    const availableWidth = Math.max(1, view.canvas.clientWidth - padding * 2);
    const availableHeight = Math.max(1, view.canvas.clientHeight - padding * 2);
    const fittedScale = Math.min(1.2, availableWidth / view.width, availableHeight / view.height);
    view.scale = Number.isFinite(fittedScale) && fittedScale > 0 ? fittedScale : 1;
    view.x = (view.canvas.clientWidth - view.width * view.scale) / 2;
    view.y = (view.canvas.clientHeight - view.height * view.scale) / 2;
    applyWorkflowTransform();
  }

  function zoomWorkflow(factor, clientX = null, clientY = null) {
    const view = state.workflowView;
    if (!view?.canvas) return;
    const rect = view.canvas.getBoundingClientRect();
    const pointX = clientX === null ? rect.width / 2 : clientX - rect.left;
    const pointY = clientY === null ? rect.height / 2 : clientY - rect.top;
    const worldX = (pointX - view.x) / view.scale;
    const worldY = (pointY - view.y) / view.scale;
    const next = Math.min(2.5, view.scale * factor);
    if (!Number.isFinite(next) || next <= 0) return;
    view.x = pointX - worldX * next;
    view.y = pointY - worldY * next;
    view.scale = next;
    applyWorkflowTransform();
  }

  function renderWorkflow(graph) {
    const panel = $("#workflowPanel");
    const sourceNodes = Array.isArray(graph?.nodes) ? graph.nodes.slice(0, 5000) : [];
    if (!sourceNodes.length) {
      state.workflowView = null;
      panel.innerHTML = '<div class="workflow-empty"><div class="workflow-empty-mark">◇</div><strong>No visual workflow found</strong><span>This file does not contain a ComfyUI workflow graph.</span></div>';
      return;
    }

    const sourceLinks = Array.isArray(graph?.links) ? graph.links.slice(0, 20000) : [];
    const requiredInputSlots = new Map();
    const requiredOutputSlots = new Map();
    const requireSlot = (mapping, nodeId, slot) => {
      if (!Number.isInteger(slot) || slot < 0 || slot >= 512) return;
      const key = String(nodeId);
      if (!mapping.has(key)) mapping.set(key, new Set());
      mapping.get(key).add(slot);
    };
    sourceLinks.forEach(link => {
      requireSlot(requiredOutputSlots, link.from_node, Number(link.from_slot || 0));
      requireSlot(requiredInputSlots, link.to_node, Number(link.to_slot || 0));
    });

    let remainingWorkflowDomRecords = Math.max(0, WORKFLOW_DOM_BUDGET - sourceNodes.length);
    const prepared = sourceNodes.map((node, index) => {
      const params = Array.isArray(node.params) ? node.params.slice(0, Math.min(7, remainingWorkflowDomRecords)) : [];
      remainingWorkflowDomRecords = Math.max(0, remainingWorkflowDomRecords - params.length);
      const parameterHeight = workflowParamHeight(params);
      const rawInputs = Array.isArray(node.inputs) ? node.inputs.slice(0, 512) : [];
      const rawOutputs = Array.isArray(node.outputs) ? node.outputs.slice(0, 512) : [];
      const inputRequired = [...(requiredInputSlots.get(String(node.id)) || [])].filter(slot => slot < rawInputs.length).sort((a, b) => a - b);
      const outputRequired = [...(requiredOutputSlots.get(String(node.id)) || [])].filter(slot => slot < rawOutputs.length).sort((a, b) => a - b);
      const targetRows = Math.max(0, remainingWorkflowDomRecords);
      const compactPorts = (ports, required) => {
        const indices = required.slice(0, targetRows);
        const chosen = new Set(indices);
        for (let slot = 0; slot < ports.length && indices.length < targetRows; slot += 1) {
          if (!chosen.has(slot)) indices.push(slot);
        }
        return indices.map(slot => ({ ...ports[slot], originalSlot: slot }));
      };
      const inputs = compactPorts(rawInputs, inputRequired);
      const outputs = compactPorts(rawOutputs, outputRequired);
      remainingWorkflowDomRecords = Math.max(0, remainingWorkflowDomRecords - Math.max(inputs.length, outputs.length));
      const savedWidth = Number(node.size?.[0]) || 240;
      const savedHeight = Number(node.size?.[1]) || 140;
      const savedX = Number(node.position?.[0]);
      const savedY = Number(node.position?.[1]);
      const contentHeight = 48 + Math.max(inputs.length, outputs.length) * 22 + parameterHeight;
      return {
        ...node,
        x: Number.isFinite(savedX) ? savedX : index % 4 * 320,
        y: Number.isFinite(savedY) ? savedY : Math.floor(index / 4) * 240,
        width: Math.max(210, Math.min(420, savedWidth)),
        height: Math.max(92, Math.min(12000, Math.max(savedHeight, contentHeight))),
        inputs, outputs, params,
        inputRowBySlot: new Map(inputs.map((port, row) => [port.originalSlot, row])),
        outputRowBySlot: new Map(outputs.map((port, row) => [port.originalSlot, row]))
      };
    });
    const preparedGroups = (Array.isArray(graph?.groups) ? graph.groups.slice(0, 128) : []).map(group => {
      const x = Number(group.position?.[0]);
      const y = Number(group.position?.[1]);
      const width = Number(group.size?.[0]);
      const height = Number(group.size?.[1]);
      return {
        ...group,
        x: Number.isFinite(x) ? x : 0,
        y: Number.isFinite(y) ? y : 0,
        width: Number.isFinite(width) && width > 0 ? width : 320,
        height: Number.isFinite(height) && height > 0 ? height : 220
      };
    });
    let minX = Infinity;
    let minY = Infinity;
    for (const item of [...prepared, ...preparedGroups]) {
      minX = Math.min(minX, item.x);
      minY = Math.min(minY, item.y);
    }
    prepared.forEach(node => { node.x = node.x - minX + 74; node.y = node.y - minY + 74; });
    preparedGroups.forEach(group => { group.x = group.x - minX + 74; group.y = group.y - minY + 74; });
    let contentWidth = 0;
    let contentHeight = 0;
    for (const node of prepared) {
      contentWidth = Math.max(contentWidth, node.x + node.width);
      contentHeight = Math.max(contentHeight, node.y + node.height);
    }
    for (const group of preparedGroups) {
      contentWidth = Math.max(contentWidth, group.x + group.width);
      contentHeight = Math.max(contentHeight, group.y + group.height);
    }
    const width = contentWidth + 74;
    const height = contentHeight + 74;
    const nodeMap = new Map(prepared.map(node => [String(node.id), node]));

    const renderedLinks = [];
    for (const link of sourceLinks) {
      if (remainingWorkflowDomRecords <= 0) break;
      const from = nodeMap.get(String(link.from_node));
      const to = nodeMap.get(String(link.to_node));
      if (!from || !to) continue;
      const fromSlot = Number(link.from_slot || 0);
      const toSlot = Number(link.to_slot || 0);
      const fromRow = from.outputRowBySlot.get(fromSlot);
      const toRow = to.inputRowBySlot.get(toSlot);
      if (fromRow === undefined || toRow === undefined) continue;
      const x1 = from.x + from.width;
      const y1 = from.y + 48 + fromRow * 22;
      const x2 = to.x;
      const y2 = to.y + 48 + toRow * 22;
      const curve = Math.max(64, Math.abs(x2 - x1) * .48);
      const color = workflowPortColor(link.type);
      renderedLinks.push(`<path class="workflow-link" d="M ${x1} ${y1} C ${x1 + curve} ${y1}, ${x2 - curve} ${y2}, ${x2} ${y2}" style="--link-color:${color}"></path>`);
      remainingWorkflowDomRecords -= 1;
    }
    const links = renderedLinks.join("");

    const groupMarkup = preparedGroups.map(group => `<section class="workflow-group" style="left:${group.x}px;top:${group.y}px;width:${group.width}px;height:${group.height}px">
      <strong>${escapeHtml(group.title || "Subgraph")}</strong><span>SUBGRAPH · ${escapeHtml(group.id || "")}</span>
    </section>`).join("");

    const nodes = prepared.map(node => {
      const rowCount = Math.max(node.inputs.length, node.outputs.length);
      const rows = Array.from({ length: rowCount }, (_, index) => {
        const input = node.inputs[index];
        const output = node.outputs[index];
        return `<div class="workflow-node-row">
          <span class="workflow-slot input ${input ? "" : "empty"}">${input ? `<i style="--port-color:${workflowPortColor(input.type)}"></i><b title="${escapeHtml(input.name)}">${escapeHtml(input.name)}</b>` : ""}</span>
          <span class="workflow-slot output ${output ? "" : "empty"}">${output ? `<b title="${escapeHtml(output.name)}">${escapeHtml(output.name)}</b><i style="--port-color:${workflowPortColor(output.type)}"></i>` : ""}</span>
        </div>`;
      }).join("");
      const params = node.params.length ? `<div class="workflow-node-params">${node.params.map(param => `<div class="${param.multiline ? "multiline" : ""}"><b title="${escapeHtml(param.name)}">${escapeHtml(param.name)}</b><span ${param.multiline ? "" : `title="${escapeHtml(param.value)}"`}>${escapeHtml(param.value)}</span></div>`).join("")}</div>` : "";
      return `<article class="workflow-node ${Number(node.mode) !== 0 ? "muted" : ""}" data-workflow-node="${escapeHtml(node.id)}" style="left:${node.x}px;top:${node.y}px;width:${node.width}px;min-height:${node.height}px;--node-accent:${workflowNodeAccent(node.type)}">
        <header><span></span><strong title="${escapeHtml(node.title || node.type)}">${escapeHtml(node.title || node.type || "Unknown")}</strong><small>#${escapeHtml(node.id)}</small></header>
        <div class="workflow-node-body">${rows}${params}</div>
      </article>`;
    }).join("");

    const graphLabel = graph.kind === "api" ? "AUTO-ARRANGED API GRAPH" : "SAVED COMFYUI LAYOUT";
    panel.innerHTML = `<div class="workflow-graph">
      <div class="workflow-toolbar">
        <div class="workflow-summary"><span>${graphLabel}</span><strong>${prepared.length} NODES · ${renderedLinks.length} LINKS</strong></div>
        <div class="workflow-controls">
          <button data-workflow-action="zoom-out" title="Zoom out">${icon("minus")}</button>
          <output id="workflowZoomValue">100%</output>
          <button data-workflow-action="zoom-in" title="Zoom in">${icon("plus")}</button>
          <button class="fit" data-workflow-action="fit">Fit workflow</button>
        </div>
      </div>
      <div class="workflow-canvas" tabindex="0" aria-label="Read-only ComfyUI workflow. Scroll to zoom and drag the background to pan.">
        <div class="workflow-scene" style="width:${width}px;height:${height}px">
          <div class="workflow-groups">${groupMarkup}</div>
          <svg class="workflow-links" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" aria-hidden="true">${links}</svg>
          <div class="workflow-nodes">${nodes}</div>
        </div>
        <div class="workflow-help">Scroll to zoom · drag to pan · double-click to fit</div>
      </div>
    </div>`;

    const canvas = $(".workflow-canvas", panel);
    const scene = $(".workflow-scene", panel);
    state.workflowView = { canvas, scene, width, height, scale: 1, x: 0, y: 0, drag: null };
    $$('[data-workflow-action]', panel).forEach(button => button.addEventListener("click", () => {
      if (button.dataset.workflowAction === "fit") fitWorkflowGraph();
      else zoomWorkflow(button.dataset.workflowAction === "zoom-in" ? 1.2 : 1 / 1.2);
    }));
    canvas.addEventListener("wheel", event => {
      event.preventDefault();
      zoomWorkflow(event.deltaY < 0 ? 1.12 : 1 / 1.12, event.clientX, event.clientY);
    }, { passive: false });
    canvas.addEventListener("pointerdown", event => {
      if (event.button !== 0 || event.target.closest("button, .workflow-node")) return;
      const view = state.workflowView;
      view.drag = { pointerId: event.pointerId, startX: event.clientX, startY: event.clientY, x: view.x, y: view.y };
      canvas.setPointerCapture(event.pointerId);
      canvas.classList.add("panning");
    });
    canvas.addEventListener("pointermove", event => {
      const view = state.workflowView;
      if (!view?.drag || view.drag.pointerId !== event.pointerId) return;
      view.x = view.drag.x + event.clientX - view.drag.startX;
      view.y = view.drag.y + event.clientY - view.drag.startY;
      applyWorkflowTransform();
    });
    const endPan = event => {
      const view = state.workflowView;
      if (!view?.drag || view.drag.pointerId !== event.pointerId) return;
      view.drag = null;
      canvas.classList.remove("panning");
    };
    canvas.addEventListener("pointerup", endPan);
    canvas.addEventListener("pointercancel", endPan);
    canvas.addEventListener("dblclick", event => { if (!event.target.closest(".workflow-node")) fitWorkflowGraph(); });
    $$(".workflow-node", panel).forEach(node => node.addEventListener("click", () => {
      $$(".workflow-node", panel).forEach(row => row.classList.toggle("selected", row === node));
    }));
    if ($("#viewer").classList.contains("workflow-view")) requestAnimationFrame(fitWorkflowGraph);
  }

  function setInspectorTab(tab) {
    $$(".tabs button").forEach(button => button.classList.toggle("active", button.dataset.tab === tab));
    $$(".tab-panel").forEach(panel => panel.classList.toggle("active", panel.dataset.panel === tab));
    const inspectorBody = $(".inspector-body");
    if (inspectorBody) inspectorBody.scrollTop = 0;
    $("#viewer").classList.toggle("workflow-view", tab === "workflow");
    if (tab === "workflow") requestAnimationFrame(fitWorkflowGraph);
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
    $("#viewer").classList.remove("workflow-view");
    document.body.classList.remove("viewer-open");
    $("#mediaCanvas").innerHTML = "";
    state.viewerIndex = -1;
    state.metadata = null;
    state.workflowView = null;
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
      ${item.kind === "image" && !multiple ? `<button data-action="copy-image">${icon("copy")}Copy image</button>` : ""}
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
      else if (action === "copy-image") copyImage(item);
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

  async function browserClipboardImage(item) {
    if (!navigator.clipboard?.write || typeof ClipboardItem === "undefined") throw new Error("Image clipboard access is unavailable");
    const response = await fetch(mediaUrl(item));
    if (!response.ok) throw new Error("Image could not be loaded");
    const sourceBlob = await response.blob();
    let pngBlob = sourceBlob;
    if (sourceBlob.type !== "image/png") {
      const bitmap = await createImageBitmap(sourceBlob);
      const canvas = document.createElement("canvas");
      canvas.width = bitmap.width;
      canvas.height = bitmap.height;
      canvas.getContext("2d").drawImage(bitmap, 0, 0);
      bitmap.close();
      pngBlob = await new Promise((resolve, reject) => canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error("Image could not be converted")), "image/png"));
    }
    await navigator.clipboard.write([new ClipboardItem({ "image/png": pngBlob })]);
  }

  async function copyImage(item) {
    if (!item || item.kind !== "image") return;
    try {
      if (window.pywebview?.api?.copy_image) {
        const result = await window.pywebview.api.copy_image(item.source_id, item.path);
        if (!result?.success) throw new Error(result?.error || "Image could not be copied");
      } else await browserClipboardImage(item);
      toast("Image copied");
    } catch (error) { toast(error.message || "Image could not be copied", "error"); }
  }

  let searchTimer = null;
  $("#searchInput").addEventListener("input", event => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { state.search = event.target.value.trim(); loadMedia(true); }, 220);
  });
  $("#searchFieldSelect").addEventListener("change", event => {
    state.searchField = event.target.value;
    const labels = { filename: "file names", prompt: "prompts", lora: "LoRAs", model: "models", all: "all fields" };
    $("#searchInput").placeholder = `Search ${labels[state.searchField] || "files"}`;
    if (state.search) loadMedia(true);
  });
  $("#sortSelect").addEventListener("change", event => { state.sort = event.target.value; loadMedia(true); });
  $("#cardSize").addEventListener("input", event => applyCardSize(event.target.value));
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
  $("#compareZoomOutBtn").addEventListener("click", () => setCompareZoom(state.compareZoom - .25));
  $("#compareZoomInBtn").addEventListener("click", () => setCompareZoom(state.compareZoom + .25));
  $("#compareZoomResetBtn").addEventListener("click", resetCompareView);
  $("#compareStage").addEventListener("wheel", event => {
    event.preventDefault();
    setCompareZoom(state.compareZoom + (event.deltaY < 0 ? .2 : -.2), event.clientX, event.clientY);
  }, { passive: false });
  $("#compareStage").addEventListener("pointerdown", event => {
    if (event.button !== 0) return;
    const stage = event.currentTarget;
    const dividerDrag = !!event.target.closest("#compareDivider");
    let move;
    if (state.compareZoom > 1 && !dividerDrag) {
      state.comparePanning = true;
      state.comparePanStart = {
        pointerId: event.pointerId, x: event.clientX, y: event.clientY,
        panX: state.comparePanX, panY: state.comparePanY
      };
      move = ev => {
        if (!state.comparePanStart || ev.pointerId !== state.comparePanStart.pointerId) return;
        const position = comparePointerPosition(ev.clientX, ev.clientY);
        state.comparePanX = state.comparePanStart.panX + (ev.clientX - state.comparePanStart.x) * position.scaleX;
        state.comparePanY = state.comparePanStart.panY + (ev.clientY - state.comparePanStart.y) * position.scaleY;
        applyCompareTransform();
      };
      applyCompareTransform();
    } else {
      move = ev => {
        const position = comparePointerPosition(ev.clientX, ev.clientY);
        updateCompareSlider(position.x / stage.clientWidth * 100);
      };
      move(event);
    }
    const end = ev => {
      if (ev.pointerId !== event.pointerId) return;
      state.comparePanning = false;
      state.comparePanStart = null;
      stage.removeEventListener("pointermove", move);
      stage.removeEventListener("pointerup", end);
      stage.removeEventListener("pointercancel", end);
      applyCompareTransform();
    };
    stage.setPointerCapture(event.pointerId);
    stage.addEventListener("pointermove", move);
    stage.addEventListener("pointerup", end);
    stage.addEventListener("pointercancel", end);
    event.preventDefault();
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
  $$('[data-theme-choice]').forEach(button => button.addEventListener("click", () => applyTheme(button.dataset.themeChoice)));
  window.addEventListener("resize", syncUiScaleBreakpoints);
  window.addEventListener("pywebviewready", syncNativeWindowClass);

  $("#closeViewerBtn").addEventListener("click", closeViewer);
  $("#workflowCloseBtn").addEventListener("click", closeViewer);
  $("#viewerStage").addEventListener("click", event => { if (!isPointOnRenderedMedia(event)) closeViewer(); });
  $("#viewerPrev").addEventListener("click", () => navigateViewer(-1));
  $("#viewerNext").addEventListener("click", () => navigateViewer(1));
  $("#viewerFavoriteBtn").addEventListener("click", () => toggleFavorite(currentViewerItem()));
  $("#copyImageBtn").addEventListener("click", () => copyImage(currentViewerItem()));
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

  syncNativeWindowClass();
  applyUiScale(storedUiScale(), false);
  initialize();
})();
