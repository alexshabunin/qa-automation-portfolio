// TaskFlow — a fixture SPA used by the test suite.
//
// Talks to a REST backend at /api/tasks. The repo doesn't ship a backend —
// the tests intercept these calls via Playwright route mocks. When running
// the UI in a browser without test mocks, you'll see an empty board.
//
// Kept dependency-free on purpose: no framework, no build step. The thing
// under test in this repo is the test framework, not the app.

const API = "/api/tasks";
const SEARCH_DEBOUNCE_MS = 300;
const TAGS = ["frontend", "backend", "infra", "bug", "research"];

const $ = (selector, root = document) => root.querySelector(selector);

const els = {
  list: $('[data-test="task-list"]'),
  counter: $('[data-test="task-counter"]'),
  loading: $('[data-test="loading-indicator"]'),
  empty: $('[data-test="empty-state"]'),
  search: $('[data-test="search-input"]'),
  createBtn: $('[data-test="create-task-button"]'),
  drawer: $('[data-test="task-drawer"]'),
  drawerTitle: $('[data-test="drawer-title"]'),
  drawerClose: $('[data-test="drawer-close"]'),
  drawerCancel: $('[data-test="drawer-cancel"]'),
  drawerSave: $('[data-test="drawer-save"]'),
  drawerForm: $('[data-test="task-drawer-form"]'),
  drawerError: $('[data-test="drawer-error"]'),
  titleInput: $('[data-test="task-title-input"]'),
  titleError: $('[data-test="task-title-error"]'),
  descInput: $('[data-test="task-description-input"]'),
  statusSelect: $('[data-test="task-status-select"]'),
  tagsPicker: $('[data-test="tags-picker"]'),
  toast: $('[data-test="toast"]'),
};

const state = {
  tasks: [],
  query: "",
  editing: null, // null = creating new, object = editing existing
  selectedTags: new Set(),
};

renderTagPicker();
attachEventHandlers();
loadTasks();

function renderTagPicker() {
  els.tagsPicker.replaceChildren(
    ...TAGS.map((tag) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "tag-chip";
      chip.dataset.test = `tag-chip-${tag}`;
      chip.setAttribute("aria-pressed", "false");
      chip.textContent = tag;
      chip.addEventListener("click", () => toggleTag(tag));
      return chip;
    }),
  );
}

function toggleTag(tag) {
  if (state.selectedTags.has(tag)) {
    state.selectedTags.delete(tag);
  } else {
    state.selectedTags.add(tag);
  }
  const chip = els.tagsPicker.querySelector(`[data-test="tag-chip-${tag}"]`);
  if (chip) chip.setAttribute("aria-pressed", String(state.selectedTags.has(tag)));
}

function attachEventHandlers() {
  els.search.addEventListener("input", debounce((event) => {
    state.query = event.target.value.trim();
    loadTasks();
  }, SEARCH_DEBOUNCE_MS));

  els.createBtn.addEventListener("click", () => openDrawer(null));
  els.drawerClose.addEventListener("click", closeDrawer);
  els.drawerCancel.addEventListener("click", closeDrawer);
  els.drawerForm.addEventListener("submit", onSubmit);
  els.titleInput.addEventListener("input", () => clearFieldError(els.titleError));
}

function debounce(fn, delay) {
  let timer;
  return function debounced(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

async function loadTasks() {
  setLoading(true);
  try {
    const url = state.query ? `${API}?q=${encodeURIComponent(state.query)}` : API;
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    state.tasks = Array.isArray(payload?.data) ? payload.data : [];
    renderTasks();
  } catch (error) {
    state.tasks = [];
    renderTasks();
    showToast(`Couldn't load tasks: ${error.message}`, "error");
  } finally {
    setLoading(false);
  }
}

function setLoading(on) {
  els.loading.hidden = !on;
}

function renderTasks() {
  els.counter.textContent = `${state.tasks.length} task${state.tasks.length === 1 ? "" : "s"}`;
  els.empty.hidden = state.tasks.length !== 0;
  els.list.replaceChildren(
    ...state.tasks.map((task) => {
      const li = document.createElement("li");
      li.className = "task-card";
      li.dataset.test = `task-${task.id}`;
      li.addEventListener("click", () => openDrawer(task));

      const title = document.createElement("span");
      title.className = "task-title";
      title.dataset.test = "task-title";
      title.textContent = task.title;

      const status = document.createElement("span");
      status.className = `task-status status-${task.status}`;
      status.dataset.test = "task-status";
      status.textContent = task.status.replace("_", " ");

      const meta = document.createElement("span");
      meta.className = "task-meta";
      const tags = document.createElement("span");
      tags.className = "task-tags";
      tags.dataset.test = "task-tags";
      for (const tag of task.tags ?? []) {
        const t = document.createElement("span");
        t.className = "task-tag";
        t.dataset.test = `task-tag-${tag}`;
        t.textContent = tag;
        tags.append(t);
      }
      meta.append(tags);

      li.append(title, status, meta);
      return li;
    }),
  );
}

function openDrawer(task) {
  state.editing = task;
  state.selectedTags = new Set(task?.tags ?? []);

  els.drawerTitle.textContent = task ? "Edit task" : "New task";
  els.titleInput.value = task?.title ?? "";
  els.descInput.value = task?.description ?? "";
  els.statusSelect.value = task?.status ?? "todo";
  for (const tag of TAGS) {
    const chip = els.tagsPicker.querySelector(`[data-test="tag-chip-${tag}"]`);
    if (chip) chip.setAttribute("aria-pressed", String(state.selectedTags.has(tag)));
  }

  clearFieldError(els.titleError);
  els.drawerError.hidden = true;
  els.drawer.hidden = false;
  els.drawer.setAttribute("aria-hidden", "false");
  els.titleInput.focus();
}

function closeDrawer() {
  els.drawer.hidden = true;
  els.drawer.setAttribute("aria-hidden", "true");
  state.editing = null;
  state.selectedTags = new Set();
}

async function onSubmit(event) {
  event.preventDefault();
  const title = els.titleInput.value.trim();

  if (!title) {
    showFieldError(els.titleError, "Title is required.");
    els.titleInput.focus();
    return;
  }
  if (title.length < 3) {
    showFieldError(els.titleError, "Title must be at least 3 characters.");
    els.titleInput.focus();
    return;
  }

  const body = {
    title,
    description: els.descInput.value.trim(),
    status: els.statusSelect.value,
    tags: [...state.selectedTags].sort(),
  };

  const isEditing = state.editing !== null;
  const url = isEditing ? `${API}/${state.editing.id}` : API;
  const method = isEditing ? "PATCH" : "POST";

  setSaving(true);
  els.drawerError.hidden = true;
  try {
    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      let detail = `Server responded with ${response.status}.`;
      try {
        const errPayload = await response.json();
        if (errPayload?.message) detail = errPayload.message;
      } catch (_) { /* keep default */ }
      throw new Error(detail);
    }
    const saved = await response.json();
    upsertTask(saved);
    renderTasks();
    showToast(isEditing ? "Task updated" : "Task created");
    closeDrawer();
  } catch (error) {
    showDrawerError(error.message);
  } finally {
    setSaving(false);
  }
}

function upsertTask(task) {
  const i = state.tasks.findIndex((t) => t.id === task.id);
  if (i === -1) state.tasks.unshift(task);
  else state.tasks[i] = task;
}

function setSaving(saving) {
  els.drawerSave.disabled = saving;
  els.drawerSave.textContent = saving ? "Saving…" : "Save";
}

function showFieldError(node, message) {
  node.textContent = message;
  node.hidden = false;
}

function clearFieldError(node) {
  node.textContent = "";
  node.hidden = true;
}

function showDrawerError(message) {
  els.drawerError.textContent = message;
  els.drawerError.hidden = false;
}

function showToast(message, variant = "ok") {
  els.toast.textContent = message;
  els.toast.className = `toast toast-${variant}`;
  els.toast.hidden = false;
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => { els.toast.hidden = true; }, 2500);
}
