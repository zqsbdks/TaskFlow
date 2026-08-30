"use strict";

const API_BASE = "/api/v1";

const state = {
  token: sessionStorage.getItem("taskflow_token") || "",
  user: readStoredUser(),
  tasks: [],
  tags: [],
  taskPage: 1,
  taskPageSize: 10,
  taskTotalPages: 0,
  taskTotal: 0,
  statusFilter: "",
  priorityFilter: "",
  currentView: "dashboard",
  adminTab: "users",
  adminPage: 1,
  adminTotalPages: 0,
};

const statusLabels = {
  pending: "待处理",
  in_progress: "进行中",
  completed: "已完成",
  cancelled: "已取消",
};

const elements = {};

document.addEventListener("DOMContentLoaded", initialize);

function initialize() {
  collectElements();
  bindEvents();
  setTodayLabel();

  if (state.token) {
    showApplication();
    bootstrapApplication();
  } else {
    showAuthentication();
  }
}

function collectElements() {
  const ids = [
    "auth-view", "app-view", "login-form", "register-form", "auth-title",
    "auth-subtitle", "sidebar-username", "sidebar-role", "sidebar-avatar",
    "welcome-name", "profile-name", "profile-email", "profile-role", "profile-avatar",
    "profile-form", "password-form", "logout-button", "new-task-button", "refresh-button",
    "menu-button", "page-title", "today-label", "dashboard-view", "tags-view",
    "profile-view", "admin-view", "admin-nav", "task-list", "task-empty",
    "task-pagination", "status-filter", "priority-filter", "stat-total", "stat-pending",
    "stat-progress", "stat-completed", "completion-rate", "task-modal", "task-modal-title",
    "task-form", "tag-list", "tag-empty", "tag-form", "color-value",
    "tag-binding-form", "binding-task", "binding-tag", "remove-tag-button",
    "admin-table-title", "admin-table-head", "admin-table-body", "admin-pagination",
    "toast-region",
  ];

  ids.forEach((id) => {
    elements[toCamelCase(id)] = document.getElementById(id);
  });
}

function bindEvents() {
  document.querySelectorAll("[data-auth-tab]").forEach((button) => {
    button.addEventListener("click", () => switchAuthTab(button.dataset.authTab));
  });
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });
  document.querySelectorAll("[data-open-task-modal]").forEach((button) => {
    button.addEventListener("click", () => openTaskModal());
  });
  document.querySelectorAll("[data-close-modal]").forEach((button) => {
    button.addEventListener("click", closeTaskModal);
  });
  document.querySelectorAll("[data-admin-tab]").forEach((button) => {
    button.addEventListener("click", () => switchAdminTab(button.dataset.adminTab));
  });

  elements.loginForm.addEventListener("submit", handleLogin);
  elements.registerForm.addEventListener("submit", handleRegister);
  elements.logoutButton.addEventListener("click", logout);
  elements.newTaskButton.addEventListener("click", () => openTaskModal());
  elements.refreshButton.addEventListener("click", refreshCurrentView);
  elements.menuButton.addEventListener("click", toggleSidebar);
  elements.statusFilter.addEventListener("change", handleTaskFilter);
  elements.priorityFilter.addEventListener("change", handleTaskFilter);
  elements.taskForm.addEventListener("submit", handleTaskSubmit);
  elements.taskList.addEventListener("click", handleTaskListClick);
  elements.taskList.addEventListener("change", handleTaskStatusChange);
  elements.tagForm.addEventListener("submit", handleTagCreate);
  elements.tagForm.elements.color.addEventListener("input", handleColorChange);
  elements.tagBindingForm.addEventListener("submit", handleTagBinding);
  elements.removeTagButton.addEventListener("click", handleTagRemoval);
  elements.profileForm.addEventListener("submit", handleProfileUpdate);
  elements.passwordForm.addEventListener("submit", handlePasswordUpdate);
  elements.adminTableBody.addEventListener("click", handleAdminTableClick);
  elements.taskModal.addEventListener("click", (event) => {
    if (event.target === elements.taskModal) closeTaskModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeTaskModal();
  });
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch (error) {
    throw new Error("无法连接服务器，请确认 FastAPI 已启动");
  }

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && state.token) {
      clearSession();
      showAuthentication();
    }
    throw new Error(payload?.message || `请求失败（${response.status}）`);
  }
  return payload;
}

async function handleLogin(event) {
  event.preventDefault();
  const submitButton = event.submitter;
  setButtonBusy(submitButton, true, "正在登录…");
  const form = new FormData(event.currentTarget);

  try {
    const response = await api("/users/login", {
      method: "POST",
      body: JSON.stringify({ email: form.get("email"), password: form.get("password") }),
    });
    state.token = response.data.token;
    state.user = response.data.userinfo;
    sessionStorage.setItem("taskflow_token", state.token);
    storeUser();
    showApplication();
    await bootstrapApplication();
    showToast("登录成功，欢迎回来");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(submitButton, false);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const submitButton = event.submitter;
  setButtonBusy(submitButton, true, "正在创建…");
  const form = new FormData(event.currentTarget);

  try {
    await api("/users/register", {
      method: "POST",
      body: JSON.stringify({
        username: form.get("username"),
        email: form.get("email"),
        password: form.get("password"),
      }),
    });
    event.currentTarget.reset();
    switchAuthTab("login");
    elements.loginForm.elements.email.value = form.get("email");
    showToast("账户创建成功，请登录");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(submitButton, false);
  }
}

async function bootstrapApplication() {
  try {
    const userResponse = await api("/users/info");
    state.user = userResponse.data;
    storeUser();
    renderUser();
    await Promise.all([loadTasks(), loadTags()]);
  } catch (error) {
    if (state.token) showToast(error.message, "error");
  }
}

function switchAuthTab(tab) {
  const isLogin = tab === "login";
  document.querySelectorAll("[data-auth-tab]").forEach((button) => {
    button.classList.toggle("active", button.dataset.authTab === tab);
  });
  elements.loginForm.classList.toggle("hidden", !isLogin);
  elements.registerForm.classList.toggle("hidden", isLogin);
  elements.authTitle.textContent = isLogin ? "登录你的工作台" : "创建一个新账户";
  elements.authSubtitle.textContent = isLogin
    ? "继续推进那些真正重要的事情。"
    : "从一个清晰的计划开始。";
}

function showAuthentication() {
  elements.authView.classList.remove("hidden");
  elements.appView.classList.add("hidden");
}

function showApplication() {
  elements.authView.classList.add("hidden");
  elements.appView.classList.remove("hidden");
  renderUser();
}

function renderUser() {
  if (!state.user) return;
  const initial = (state.user.username || "U").trim().charAt(0).toUpperCase();
  const roleName = state.user.role === "admin" ? "管理员" : "普通用户";
  elements.sidebarUsername.textContent = state.user.username;
  elements.sidebarRole.textContent = roleName;
  elements.sidebarAvatar.textContent = initial;
  elements.welcomeName.textContent = state.user.username;
  elements.profileName.textContent = state.user.username;
  elements.profileEmail.textContent = state.user.email;
  elements.profileRole.textContent = roleName;
  elements.profileAvatar.textContent = initial;
  elements.profileForm.elements.username.value = state.user.username || "";
  elements.profileForm.elements.email.value = state.user.email || "";
  elements.adminNav.classList.toggle("hidden", state.user.role !== "admin");
}

function logout() {
  clearSession();
  state.tasks = [];
  state.tags = [];
  switchView("dashboard");
  showAuthentication();
  showToast("已安全退出");
}

function clearSession() {
  state.token = "";
  state.user = null;
  sessionStorage.removeItem("taskflow_token");
  sessionStorage.removeItem("taskflow_user");
}

async function loadTasks(page = state.taskPage) {
  const params = new URLSearchParams({ page: String(page), page_size: String(state.taskPageSize) });
  if (state.statusFilter) params.set("status", state.statusFilter);
  if (state.priorityFilter) params.set("priority", state.priorityFilter);

  try {
    const response = await api(`/tasks/list?${params}`);
    state.tasks = response.data.items;
    state.taskPage = response.data.page;
    state.taskTotal = response.data.total;
    state.taskTotalPages = response.data.total_pages;
    renderTasks();
    renderTaskPagination();
    renderStats();
    populateBindingOptions();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function renderTasks() {
  elements.taskList.innerHTML = state.tasks.map(taskTemplate).join("");
  elements.taskList.classList.toggle("hidden", state.tasks.length === 0);
  elements.taskEmpty.classList.toggle("hidden", state.tasks.length !== 0);
}

function taskTemplate(task) {
  const completed = task.status === "completed";
  const dueDate = task.due_date ? formatDate(task.due_date) : "无截止时间";
  const description = task.description ? escapeHtml(task.description) : "暂无描述";
  return `
    <article class="task-item" data-task-id="${task.id}">
      <button class="status-toggle ${completed ? "completed" : ""}" data-action="toggle-complete" type="button" title="${completed ? "重新打开" : "标记完成"}">✓</button>
      <div class="task-copy">
        <h4 class="${completed ? "completed" : ""}" title="${description}">${escapeHtml(task.title)}</h4>
        <div class="task-meta">
          <select class="inline-status status-${task.status}" data-action="change-status" aria-label="修改任务状态">
            ${Object.entries(statusLabels).map(([value, label]) => `<option value="${value}" ${value === task.status ? "selected" : ""}>${label}</option>`).join("")}
          </select>
          <span class="priority-badge ${task.priority >= 4 ? "high" : ""}">P${task.priority}</span>
          <span>${description}</span>
        </div>
      </div>
      <time class="task-date">${dueDate}</time>
      <div class="task-actions">
        <button class="task-action" data-action="edit" type="button" title="编辑任务">✎</button>
        <button class="task-action danger" data-action="delete" type="button" title="删除任务">×</button>
      </div>
    </article>`;
}

function renderStats() {
  const counts = { pending: 0, in_progress: 0, completed: 0 };
  state.tasks.forEach((task) => {
    if (Object.hasOwn(counts, task.status)) counts[task.status] += 1;
  });
  const rate = state.tasks.length ? Math.round((counts.completed / state.tasks.length) * 100) : 0;
  elements.statTotal.textContent = state.taskTotal;
  elements.statPending.textContent = counts.pending;
  elements.statProgress.textContent = counts.in_progress;
  elements.statCompleted.textContent = counts.completed;
  elements.completionRate.textContent = `${rate}%`;
}

function renderTaskPagination() {
  renderPagination(elements.taskPagination, state.taskPage, state.taskTotalPages, (page) => {
    state.taskPage = page;
    loadTasks(page);
  });
}

function handleTaskFilter() {
  state.statusFilter = elements.statusFilter.value;
  state.priorityFilter = elements.priorityFilter.value;
  state.taskPage = 1;
  loadTasks(1);
}

function handleTaskListClick(event) {
  const button = event.target.closest("[data-action]");
  if (!button || button.dataset.action === "change-status") return;
  const item = button.closest("[data-task-id]");
  const task = state.tasks.find((candidate) => candidate.id === Number(item.dataset.taskId));
  if (!task) return;

  if (button.dataset.action === "edit") openTaskModal(task);
  if (button.dataset.action === "delete") deleteTask(task);
  if (button.dataset.action === "toggle-complete") {
    updateTaskStatus(task, task.status === "completed" ? "pending" : "completed");
  }
}

function handleTaskStatusChange(event) {
  const select = event.target.closest('[data-action="change-status"]');
  if (!select) return;
  const item = select.closest("[data-task-id]");
  const task = state.tasks.find((candidate) => candidate.id === Number(item.dataset.taskId));
  if (task && select.value !== task.status) updateTaskStatus(task, select.value);
}

async function updateTaskStatus(task, nextStatus) {
  try {
    await api(`/tasks/status/${task.id}`, {
      method: "PUT",
      body: JSON.stringify({ status: nextStatus }),
    });
    showToast("任务状态已更新");
    await loadTasks();
  } catch (error) {
    showToast(error.message, "error");
    renderTasks();
  }
}

async function deleteTask(task) {
  if (!window.confirm(`确定删除“${task.title}”吗？此操作无法撤销。`)) return;
  try {
    await api(`/tasks/delete/${task.id}`, { method: "DELETE" });
    showToast("任务已删除");
    const nextPage = state.tasks.length === 1 && state.taskPage > 1 ? state.taskPage - 1 : state.taskPage;
    await loadTasks(nextPage);
  } catch (error) {
    showToast(error.message, "error");
  }
}

function openTaskModal(task = null) {
  elements.taskForm.reset();
  elements.taskForm.elements.priority.value = "3";
  elements.taskForm.elements.task_id.value = task?.id || "";
  elements.taskModalTitle.textContent = task ? "编辑任务" : "新建任务";
  if (task) {
    elements.taskForm.elements.title.value = task.title || "";
    elements.taskForm.elements.description.value = task.description || "";
    elements.taskForm.elements.priority.value = String(task.priority);
    elements.taskForm.elements.due_date.value = toLocalDateTimeInput(task.due_date);
  }
  elements.taskModal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
  elements.taskForm.elements.title.focus();
}

function closeTaskModal() {
  elements.taskModal.classList.add("hidden");
  document.body.style.overflow = "";
}

async function handleTaskSubmit(event) {
  event.preventDefault();
  const submitButton = event.submitter;
  const form = new FormData(event.currentTarget);
  const taskId = form.get("task_id");
  const payload = {
    title: form.get("title").trim(),
    description: form.get("description").trim() || null,
    priority: Number(form.get("priority")),
    due_date: form.get("due_date") || null,
  };

  setButtonBusy(submitButton, true, "保存中…");
  try {
    if (taskId) {
      await api(`/tasks/update/${taskId}`, { method: "PUT", body: JSON.stringify(payload) });
      showToast("任务已更新");
    } else {
      await api("/tasks/create", {
        method: "POST",
        body: JSON.stringify({ ...payload, status: "pending" }),
      });
      showToast("任务已创建");
    }
    closeTaskModal();
    state.taskPage = 1;
    await loadTasks(1);
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(submitButton, false);
  }
}

async function loadTags() {
  try {
    const response = await api("/tags/list");
    state.tags = response.data || [];
    renderTags();
    populateBindingOptions();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function renderTags() {
  elements.tagList.innerHTML = state.tags.map((tag) => `
    <article class="tag-card" style="--tag-color: ${safeColor(tag.color)}">
      <strong><span class="tag-dot"></span>${escapeHtml(tag.name)}</strong>
      <small>${tag.color || "未设置颜色"}</small>
    </article>`).join("");
  elements.tagList.classList.toggle("hidden", state.tags.length === 0);
  elements.tagEmpty.classList.toggle("hidden", state.tags.length !== 0);
}

async function handleTagCreate(event) {
  event.preventDefault();
  const submitButton = event.submitter;
  const form = new FormData(event.currentTarget);
  setButtonBusy(submitButton, true, "创建中…");
  try {
    await api("/tags/create", {
      method: "POST",
      body: JSON.stringify({ name: form.get("name").trim(), color: form.get("color").toUpperCase() }),
    });
    event.currentTarget.reset();
    event.currentTarget.elements.color.value = "#3b82f6";
    handleColorChange({ target: event.currentTarget.elements.color });
    showToast("标签已创建");
    await loadTags();
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(submitButton, false);
  }
}

function handleColorChange(event) {
  elements.colorValue.textContent = event.target.value.toUpperCase();
}

function populateBindingOptions() {
  const selectedTask = elements.bindingTask.value;
  const selectedTag = elements.bindingTag.value;
  elements.bindingTask.innerHTML = state.tasks.length
    ? state.tasks.map((task) => `<option value="${task.id}">${escapeHtml(task.title)}</option>`).join("")
    : '<option value="">当前页没有任务</option>';
  elements.bindingTag.innerHTML = state.tags.length
    ? state.tags.map((tag) => `<option value="${tag.id}">${escapeHtml(tag.name)}</option>`).join("")
    : '<option value="">还没有标签</option>';
  if ([...elements.bindingTask.options].some((option) => option.value === selectedTask)) {
    elements.bindingTask.value = selectedTask;
  }
  if ([...elements.bindingTag.options].some((option) => option.value === selectedTag)) {
    elements.bindingTag.value = selectedTag;
  }
}

async function handleTagBinding(event) {
  event.preventDefault();
  const taskId = elements.bindingTask.value;
  const tagId = elements.bindingTag.value;
  if (!taskId || !tagId) return showToast("请先选择任务和标签", "error");
  setButtonBusy(event.submitter, true, "添加中…");
  try {
    await api(`/tags/task/${taskId}/tag/${tagId}`, { method: "POST" });
    showToast("标签已添加到任务");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(event.submitter, false);
  }
}

async function handleTagRemoval() {
  const taskId = elements.bindingTask.value;
  const tagId = elements.bindingTag.value;
  if (!taskId || !tagId) return showToast("请先选择任务和标签", "error");
  setButtonBusy(elements.removeTagButton, true, "移除中…");
  try {
    await api(`/tags/task/${taskId}/tag/${tagId}`, { method: "DELETE" });
    showToast("已从任务移除标签");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(elements.removeTagButton, false);
  }
}

async function handleProfileUpdate(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const payload = {
    username: form.get("username").trim(),
    email: form.get("email").trim(),
  };
  setButtonBusy(event.submitter, true, "保存中…");
  try {
    const response = await api("/users/update", { method: "PUT", body: JSON.stringify(payload) });
    state.user = { ...state.user, ...response.data };
    storeUser();
    renderUser();
    showToast("个人资料已更新");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(event.submitter, false);
  }
}

async function handlePasswordUpdate(event) {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  setButtonBusy(event.submitter, true, "更新中…");
  try {
    await api("/users/password", {
      method: "PUT",
      body: JSON.stringify({ old_password: form.get("old_password"), new_password: form.get("new_password") }),
    });
    event.currentTarget.reset();
    showToast("密码已更新");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setButtonBusy(event.submitter, false);
  }
}

function switchView(view) {
  if (view === "admin" && state.user?.role !== "admin") return;
  state.currentView = view;
  const titles = { dashboard: "任务概览", tags: "标签管理", profile: "账户设置", admin: "管理中心" };
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  ["dashboard", "tags", "profile", "admin"].forEach((name) => {
    elements[`${name}View`].classList.toggle("hidden", name !== view);
  });
  elements.pageTitle.textContent = titles[view];
  elements.newTaskButton.classList.toggle("hidden", view !== "dashboard");
  document.querySelector(".sidebar").classList.remove("open");
  if (view === "tags") loadTags();
  if (view === "admin") loadAdminData();
}

function refreshCurrentView() {
  if (state.currentView === "dashboard") loadTasks();
  if (state.currentView === "tags") loadTags();
  if (state.currentView === "profile") bootstrapApplication();
  if (state.currentView === "admin") loadAdminData();
}

function switchAdminTab(tab) {
  state.adminTab = tab;
  state.adminPage = 1;
  document.querySelectorAll("[data-admin-tab]").forEach((button) => {
    button.classList.toggle("active", button.dataset.adminTab === tab);
  });
  loadAdminData();
}

async function loadAdminData(page = state.adminPage) {
  if (state.user?.role !== "admin") return;
  const endpoint = state.adminTab === "users" ? "/admin/user/list" : "/admin/user/task/list";
  try {
    const response = await api(`${endpoint}?page=${page}&page_size=10`);
    state.adminPage = response.data.page;
    state.adminTotalPages = response.data.total_pages;
    renderAdminTable(response.data.items);
    renderPagination(elements.adminPagination, state.adminPage, state.adminTotalPages, (nextPage) => {
      state.adminPage = nextPage;
      loadAdminData(nextPage);
    });
  } catch (error) {
    showToast(error.message, "error");
  }
}

function renderAdminTable(items) {
  if (state.adminTab === "users") {
    elements.adminTableTitle.textContent = "用户列表";
    elements.adminTableHead.innerHTML = "<tr><th>ID</th><th>用户名</th><th>邮箱</th><th>角色</th><th>状态</th><th>操作</th></tr>";
    elements.adminTableBody.innerHTML = items.map((user) => `
      <tr data-user-id="${user.id}" data-user-active="${user.is_active}">
        <td>${user.id}</td><td>${escapeHtml(user.username)}</td><td>${escapeHtml(user.email)}</td>
        <td>${escapeHtml(user.role)}</td><td>${user.is_active ? "已启用" : "已禁用"}</td>
        <td><button class="table-action" data-admin-action="toggle-user" type="button">${user.is_active ? "禁用" : "启用"}</button> <button class="table-action danger" data-admin-action="delete-user" type="button">删除</button></td>
      </tr>`).join("");
  } else {
    elements.adminTableTitle.textContent = "全站任务";
    elements.adminTableHead.innerHTML = "<tr><th>ID</th><th>用户 ID</th><th>标题</th><th>状态</th><th>优先级</th><th>创建时间</th></tr>";
    elements.adminTableBody.innerHTML = items.map((task) => `
      <tr><td>${task.id}</td><td>${task.user_id}</td><td>${escapeHtml(task.title)}</td><td>${statusLabels[task.status] || task.status}</td><td>P${task.priority}</td><td>${formatDate(task.created_at)}</td></tr>`).join("");
  }
  if (!items.length) {
    elements.adminTableBody.innerHTML = '<tr><td colspan="6">暂无数据</td></tr>';
  }
}

async function handleAdminTableClick(event) {
  const button = event.target.closest("[data-admin-action]");
  if (!button) return;
  const row = button.closest("[data-user-id]");
  const userId = Number(row.dataset.userId);
  try {
    if (button.dataset.adminAction === "toggle-user") {
      const nextActive = row.dataset.userActive !== "true";
      await api(`/admin/user/status/${userId}`, {
        method: "PUT",
        body: JSON.stringify({ is_active: nextActive }),
      });
      showToast(nextActive ? "用户已启用" : "用户已禁用");
    }
    if (button.dataset.adminAction === "delete-user") {
      if (!window.confirm(`确定删除用户 #${userId} 吗？`)) return;
      await api(`/admin/user/delete/${userId}`, { method: "DELETE" });
      showToast("用户已删除");
    }
    await loadAdminData();
  } catch (error) {
    showToast(error.message, "error");
  }
}

function renderPagination(container, current, total, onChange) {
  container.innerHTML = "";
  if (total <= 1) return;
  const pages = paginationRange(current, total);
  const previous = pageButton("上一页", current - 1, current === 1, false, onChange);
  container.appendChild(previous);
  pages.forEach((page) => {
    if (page === "…") {
      const span = document.createElement("span");
      span.textContent = page;
      container.appendChild(span);
    } else {
      container.appendChild(pageButton(String(page), page, false, page === current, onChange));
    }
  });
  container.appendChild(pageButton("下一页", current + 1, current === total, false, onChange));
}

function pageButton(label, page, disabled, active, onChange) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `page-button${active ? " active" : ""}`;
  button.textContent = label;
  button.disabled = disabled;
  button.addEventListener("click", () => onChange(page));
  return button;
}

function paginationRange(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, index) => index + 1);
  if (current <= 4) return [1, 2, 3, 4, 5, "…", total];
  if (current >= total - 3) return [1, "…", total - 4, total - 3, total - 2, total - 1, total];
  return [1, "…", current - 1, current, current + 1, "…", total];
}

function toggleSidebar() {
  document.querySelector(".sidebar").classList.toggle("open");
}

function setTodayLabel() {
  elements.todayLabel.textContent = new Intl.DateTimeFormat("zh-CN", {
    month: "long", day: "numeric", weekday: "long",
  }).format(new Date());
}

function setButtonBusy(button, busy, busyText = "处理中…") {
  if (!button) return;
  if (busy) {
    button.dataset.originalText = button.innerHTML;
    button.textContent = busyText;
    button.disabled = true;
  } else {
    button.innerHTML = button.dataset.originalText || button.innerHTML;
    button.disabled = false;
  }
}

function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  elements.toastRegion.appendChild(toast);
  window.setTimeout(() => toast.remove(), 3200);
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit",
  }).format(date);
}

function toLocalDateTimeInput(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

function safeColor(value) {
  return /^#[0-9a-f]{6}$/i.test(value || "") ? value : "#8aa399";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function toCamelCase(value) {
  return value.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
}

function readStoredUser() {
  try {
    return JSON.parse(sessionStorage.getItem("taskflow_user")) || null;
  } catch {
    return null;
  }
}

function storeUser() {
  sessionStorage.setItem("taskflow_user", JSON.stringify(state.user));
}
