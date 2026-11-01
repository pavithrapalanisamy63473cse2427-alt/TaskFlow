
const API_URL = "/api/tasks";

let tasks = [];
let editingTaskId = null;

// HTML elements
const taskForm = document.getElementById("task-form");
const titleInput = document.getElementById("task-title");
const descriptionInput = document.getElementById("task-description");
const priorityInput = document.getElementById("task-priority");
const dateInput = document.getElementById("task-date");

const taskList = document.getElementById("task-list");

const totalTasks = document.getElementById("total-tasks");
const pendingTasks = document.getElementById("pending-tasks");
const completedTasks = document.getElementById("completed-tasks");

const searchInput = document.getElementById("search-task");
const statusFilter = document.getElementById("status-filter");
const priorityFilter = document.getElementById("priority-filter");

const submitButton = document.getElementById("submit-button");
const cancelButton = document.getElementById("cancel-button");


// API request function
async function apiRequest(url, method = "GET", data = null) {
    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (data !== null) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || "Something went wrong");
    }

    return result;
}


// Load tasks from database
async function loadTasks() {
    try {
        tasks = await apiRequest(API_URL);

        updateDashboard();
        displayTasks();

    } catch (error) {
        alert("Unable to load tasks: " + error.message);
    }
}


// Create or update a task
taskForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const title = titleInput.value.trim();

    if (!title) {
        alert("Please enter a task title.");
        return;
    }

    const taskData = {
        title: title,
        description: descriptionInput.value.trim(),
        priority: priorityInput.value,
        due_date: dateInput.value
    };

    try {
        submitButton.disabled = true;

        submitButton.textContent =
            editingTaskId !== null ? "Updating..." : "Creating...";

        if (editingTaskId !== null) {

            const currentTask = tasks.find(
                task => task.id === editingTaskId
            );

            if (!currentTask) {
                throw new Error("Task not found.");
            }

            taskData.status = currentTask.status;

            await apiRequest(
                `${API_URL}/${editingTaskId}`,
                "PUT",
                taskData
            );

            alert("Task updated successfully!");

        } else {

            await apiRequest(
                API_URL,
                "POST",
                taskData
            );

            alert("Task created successfully!");
        }

        resetForm();
        await loadTasks();

    } catch (error) {

        alert(error.message);

    } finally {

        submitButton.disabled = false;

        submitButton.textContent =
            editingTaskId !== null ? "Update Task" : "+ Create Task";
    }
});


// Reset form and cancel editing
function resetForm() {

    taskForm.reset();

    editingTaskId = null;

    submitButton.textContent = "+ Create Task";

    cancelButton.hidden = true;

    document.querySelector(".add-task-section")
        .querySelector("h2").textContent = "Add a New Task";
}


// Display tasks with search and filters
function displayTasks() {

    const searchValue = searchInput.value.toLowerCase();

    const selectedStatus = statusFilter.value;

    const selectedPriority = priorityFilter.value;

    const filteredTasks = tasks.filter(task => {

        const matchesSearch =
            task.title.toLowerCase().includes(searchValue) ||
            task.description.toLowerCase().includes(searchValue);

        const matchesStatus =
            selectedStatus === "All" ||
            task.status === selectedStatus;

        const matchesPriority =
            selectedPriority === "All" ||
            task.priority === selectedPriority;

        return matchesSearch && matchesStatus && matchesPriority;
    });


    taskList.innerHTML = "";


    if (filteredTasks.length === 0) {

        taskList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">☷</div>
                <h3>No tasks found</h3>
                <p>Try adding a task or changing your filters.</p>
            </div>
        `;

        return;
    }


    filteredTasks.forEach(task => {

        const card = document.createElement("div");

        card.className = "task-card";

        if (task.status === "Completed") {
            card.classList.add("completed");
        }


        const priorityClass = {
            "High": "priority-high",
            "Medium": "priority-medium",
            "Low": "priority-low"
        }[task.priority];


        const statusClass =
            task.status === "Completed"
                ? "status-completed"
                : "status-pending";


        const dateText = task.due_date
            ? `Due: ${task.due_date}`
            : "No due date";


        const title = escapeHTML(task.title);

        const description = escapeHTML(task.description);


        card.innerHTML = `
            <div class="task-info">

                <h3 class="task-title">${title}</h3>

                <p class="task-description">
                    ${description || "No description provided"}
                </p>

                <div class="task-meta">

                    <span class="priority-badge ${priorityClass}">
                        ${task.priority} Priority
                    </span>

                    <span class="status-badge ${statusClass}">
                        ${task.status}
                    </span>

                    <span class="due-date">
                        ${dateText}
                    </span>

                </div>

            </div>

            <div class="task-actions">

                <button
                    class="complete-btn"
                    data-action="toggle"
                    data-id="${task.id}">
                    ${task.status === "Completed" ? "Undo" : "Complete"}
                </button>

                <button
                    class="edit-btn"
                    data-action="edit"
                    data-id="${task.id}">
                    Edit
                </button>

                <button
                    class="delete-btn"
                    data-action="delete"
                    data-id="${task.id}">
                    Delete
                </button>

            </div>
        `;


        taskList.appendChild(card);

    });
}


// Prevent HTML injection
function escapeHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, character => {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];

    });
}


// Handle task actions
taskList.addEventListener("click", async function(event) {

    const button = event.target.closest("button[data-action]");

    if (!button) return;


    const taskId = Number(button.dataset.id);

    const action = button.dataset.action;


    const task = tasks.find(item => item.id === taskId);

    if (!task) return;


    try {

        // Complete or undo task
        if (action === "toggle") {

            const updatedTask = {

                title: task.title,

                description: task.description,

                priority: task.priority,

                due_date: task.due_date,

                status: task.status === "Completed"
                    ? "Pending"
                    : "Completed"

            };


            await apiRequest(
                `${API_URL}/${taskId}`,
                "PUT",
                updatedTask
            );

            await loadTasks();

        }


        // Edit task
        else if (action === "edit") {

            editingTaskId = taskId;

            titleInput.value = task.title;

            descriptionInput.value = task.description;

            priorityInput.value = task.priority;

            dateInput.value = task.due_date || "";


            submitButton.textContent = "Update Task";

            cancelButton.hidden = false;


            document.querySelector(".add-task-section")
                .querySelector("h2").textContent = "Edit Task";


            document.getElementById("add-task-section")
                .scrollIntoView({
                    behavior: "smooth"
                });

        }


        // Delete task
        else if (action === "delete") {

            const confirmed = confirm(
                "Are you sure you want to delete this task?"
            );

            if (!confirmed) return;


            await apiRequest(
                `${API_URL}/${taskId}`,
                "DELETE"
            );


            if (editingTaskId === taskId) {
                resetForm();
            }


            await loadTasks();

        }

    } catch (error) {

        alert(error.message);

    }

});


// Update dashboard statistics
function updateDashboard() {

    const total = tasks.length;

    const completed = tasks.filter(
        task => task.status === "Completed"
    ).length;

    const pending = tasks.filter(
        task => task.status === "Pending"
    ).length;


    totalTasks.textContent = total;

    pendingTasks.textContent = pending;

    completedTasks.textContent = completed;

}


// Search and filter events
searchInput.addEventListener("input", displayTasks);

statusFilter.addEventListener("change", displayTasks);

priorityFilter.addEventListener("change", displayTasks);


// Cancel editing
cancelButton.addEventListener("click", resetForm);


// Load tasks when page opens
document.addEventListener("DOMContentLoaded", function() {

    loadTasks();

});
