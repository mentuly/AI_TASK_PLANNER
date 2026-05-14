function getProfile() {
    return {
        name: localStorage.getItem("profileName") || "Користувач",
        avatar: localStorage.getItem("avatarURL") || ""
    };
}

function renderProfile() {
    const profile = getProfile();
    const nameNode = document.getElementById("profileName");
    const avatarNode = document.getElementById("profileAvatar");

    if (nameNode) {
        nameNode.textContent = profile.name;
    }

    if (avatarNode) {
        if (profile.avatar) {
            avatarNode.style.backgroundImage = `url('${profile.avatar}')`;
            avatarNode.textContent = "";
            avatarNode.style.backgroundSize = "cover";
            avatarNode.style.backgroundPosition = "center";
        } else {
            avatarNode.style.backgroundImage = "";
            const initials = profile.name
                .split(" ")
                .filter(Boolean)
                .map(word => word[0])
                .slice(0, 2)
                .join("");
            avatarNode.textContent = initials || "TB";
        }
    }
}

async function fetchTasks() {
    const response = await fetch("/tasks");
    if (response.status === 401) {
        window.location.href = "/login";
        return null;
    }
    return await response.json();
}

let currentFilter = "all";
let dashboardTasks = [];
let selectedTaskId = null;

async function loadTasks() {
    const tasks = await fetchTasks();
    if (!tasks) return;

    dashboardTasks = tasks;
    renderTaskList();
}

function setTaskDetails(task) {
    const details = document.getElementById("taskDetails");
    if (!details || !task) return;

    const progress = task.is_done ? 100 : Math.min(100, Math.round((task.steps.filter(step => step.is_done).length / Math.max(task.steps.length, 1)) * 100));
    const stepMarkup = task.steps.length
        ? task.steps.map(step => `
                <div class="details-step">
                    <strong>${step.title}</strong>
                    <span>${step.minutes} хв</span>
                </div>
            `).join("")
        : `<div class="details-step">Немає кроків для цієї задачі.</div>`;

    details.innerHTML = `
        <div class="details-card">
            <div>
                <h3>${task.title}</h3>
                <div class="task-status">${task.is_done ? "✅ Завершено" : "⏳ В роботі"}</div>
            </div>
            <div class="details-summary">
                <span>⏱ Час: ${task.total_minutes} хв</span>
                <span>🧩 Кроків: ${task.steps.length}</span>
                <span>📈 Прогрес: ${progress}%</span>
            </div>
            <div class="task-progress">
                <div class="progress-bar-wrap">
                    <div class="progress-bar" style="width: ${progress}%"></div>
                </div>
            </div>
            <div class="details-steps">
                ${stepMarkup}
            </div>
            <div class="details-actions">
                ${task.is_done ? "" : `<button class='button button-primary' onclick='markDone(${task.id})'>Відмітити як виконане</button>`}
                <button class='button button-secondary' onclick='deleteTask(${task.id})'>🗑 Видалити</button>
                <button class='button button-secondary' onclick='refreshDashboard()'>Оновити</button>
            </div>
        </div>
    `;
}

function renderTaskList() {
    const tasks = dashboardTasks;
    const tableBody = document.getElementById("taskTableBody");
    const summaryTotal = document.getElementById("summaryTotal");
    const summaryPending = document.getElementById("summaryPending");
    const summaryDone = document.getElementById("summaryDone");
    const detailsPanel = document.getElementById("taskDetails");

    if (!tableBody) return;

    if (!tasks.length) {
        tableBody.innerHTML = `
            <tr class="table-fallback">
                <td colspan="4">У вас ще немає задач. Створіть їх у Telegram-боті за допомогою команди <strong>/plan</strong>.</td>
            </tr>
        `;
        if (summaryTotal) summaryTotal.textContent = "0";
        if (summaryPending) summaryPending.textContent = "0";
        if (summaryDone) summaryDone.textContent = "0";
        if (detailsPanel) {
            detailsPanel.innerHTML = `
                <div class="details-placeholder">
                    <h3>Немає задач</h3>
                    <p>Додайте першу задачу через Telegram-бота, щоб побачити її деталі тут.</p>
                </div>
            `;
        }
        return;
    }

    const visibleTasks = tasks.filter(task => {
        if (currentFilter === "all") return true;
        return currentFilter === "done" ? task.is_done : !task.is_done;
    });

    if (summaryTotal) summaryTotal.textContent = String(tasks.length);
    if (summaryDone) summaryDone.textContent = String(tasks.filter(task => task.is_done).length);
    if (summaryPending) summaryPending.textContent = String(tasks.filter(task => !task.is_done).length);

    tableBody.innerHTML = "";

    visibleTasks.forEach((task, index) => {
        const row = document.createElement("tr");
        row.className = "task-row";
        row.dataset.taskId = task.id;
        row.style.setProperty('--delay', `${index * 40}ms`);

        row.innerHTML = `
            <td>${task.title}</td>
            <td><span class="task-status">${task.is_done ? "Завершено" : "В роботі"}</span></td>
            <td>${task.total_minutes} хв</td>
            <td>${task.steps.length}</td>
        `;

        row.addEventListener("mouseenter", () => setTaskDetails(task));
        row.addEventListener("click", () => selectTask(task.id, task));

        tableBody.appendChild(row);
    });

    if (!selectedTaskId || !visibleTasks.some(task => task.id === selectedTaskId)) {
        selectedTaskId = visibleTasks[0].id;
    }

    const selectedTask = visibleTasks.find(task => task.id === selectedTaskId);
    if (selectedTask) {
        setTaskDetails(selectedTask);
        document.querySelectorAll('.task-row').forEach(row => {
            row.classList.toggle('active', row.dataset.taskId === String(selectedTaskId));
        });
    }
}

function selectTask(taskId, task) {
    selectedTaskId = taskId;
    document.querySelectorAll('.task-row').forEach(row => {
        row.classList.toggle('active', row.dataset.taskId === String(taskId));
    });
    if (task) {
        setTaskDetails(task);
    } else {
        const selected = dashboardTasks.find(item => item.id === taskId);
        if (selected) setTaskDetails(selected);
    }
}

function setActiveFilter(filter) {
    currentFilter = filter;
    document.querySelectorAll('.filter-pill').forEach(button => {
        button.classList.toggle('active', button.dataset.filter === filter);
    });
    renderTaskList();
}

function refreshDashboard() {
    loadTasks();
}

async function markDone(id) {
    await fetch(`/done/${id}`, { method: "POST" });
    await loadTasks();
}

function saveProfile() {
    const nameInput = document.getElementById("profileNameInput");
    const avatarInput = document.getElementById("avatarUrlInput");
    if (!nameInput || !avatarInput) return;

    localStorage.setItem("profileName", nameInput.value.trim() || "Користувач");
    localStorage.setItem("avatarURL", avatarInput.value.trim());

    renderProfile();
    const notification = document.getElementById("saveNotification");
    if (notification) {
        notification.textContent = "Збережено!";
        setTimeout(() => {
            notification.textContent = "";
        }, 2200);
    }
}

function loadSettings() {
    const profile = getProfile();
    const nameInput = document.getElementById("profileNameInput");
    const avatarInput = document.getElementById("avatarUrlInput");

    if (nameInput) nameInput.value = profile.name;
    if (avatarInput) avatarInput.value = profile.avatar;
    renderProfile();
}

function initPage() {
    renderProfile();

    const page = document.body.dataset.page;
    if (page === "dashboard") {
        document.querySelectorAll('.filter-pill').forEach(button => {
            button.addEventListener('click', () => setActiveFilter(button.dataset.filter));
        });
        loadTasks();
    }
    if (page === "settings") {
        loadSettings();
    }
}

async function deleteTask(taskId) {
    if (!confirm("❌ Ви впевнені, що хочете видалити цю задачу?")) {
        return;
    }
    
    const response = await fetch(`/delete/${taskId}`, { method: "DELETE" });
    
    if (response.ok) {
        alert("✅ Задача видалена!");
        await loadTasks();
    } else {
        const error = await response.json();
        alert(`❌ Помилка: ${error.detail}`);
    }
}

window.addEventListener("DOMContentLoaded", initPage);