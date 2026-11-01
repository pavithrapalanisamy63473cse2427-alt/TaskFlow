from flask import (
    Flask, render_template, request,
    jsonify, redirect, url_for, session, flash
)
from datetime import date
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from database import (
    initialize_database,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_profile,
    update_user_password,
    get_all_tasks,
    add_task,
    update_task,
    delete_task
)
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY", "change-this-development-secret"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

VALID_PRIORITIES = ["Low", "Medium", "High"]
VALID_STATUSES = ["Pending", "Completed"]

VALID_CATEGORIES = [
    "Work",
    "Personal",
    "College",
    "Projects",
    "Other"
]

initialize_database()


# ---------------- LOGIN REQUIRED ----------------

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Please log in"}), 401

            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# ---------------- HOME ----------------

@app.route("/")
@login_required
def home():
    return render_template("home.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if len(name) > 100 or len(email) > 254:
            flash("Name or email is too long.", "error")
            return redirect(url_for("register"))

        if "@" not in email or "." not in email.split("@")[-1]:
            flash("Enter a valid email address.", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user_id = create_user(name, email, hashed_password)

        if user_id is None:
            flash("This email is already registered.", "error")
            return redirect(url_for("register"))

        session.clear()
        session["user_id"] = user_id
        session["user_name"] = name

        return redirect(url_for("home"))

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_user_by_email(email)

        if user and check_password_hash(user["password"], password):

            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("home"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
@login_required
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- PROFILE PAGE ----------------

@app.route("/profile")
@login_required
def profile_page():

    user = get_user_by_id(session["user_id"])

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)


# ---------------- UPDATE PROFILE ----------------

@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()

    if not name or not email:
        flash("Name and email are required.", "error")
        return redirect(url_for("profile_page"))

    if len(name) > 100 or len(email) > 254:
        flash("Name or email is too long.", "error")
        return redirect(url_for("profile_page"))

    if "@" not in email or "." not in email.split("@")[-1]:
        flash("Enter a valid email address.", "error")
        return redirect(url_for("profile_page"))

    updated = update_user_profile(
        session["user_id"],
        name,
        email
    )

    if not updated:
        flash("This email is already registered.", "error")
        return redirect(url_for("profile_page"))

    session["user_name"] = name

    flash("Profile updated successfully!", "success")

    return redirect(url_for("profile_page"))


# ---------------- CHANGE PASSWORD ----------------

@app.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    profile = get_user_by_id(session["user_id"])

    if profile is None:
        session.clear()
        return redirect(url_for("login"))

    user = get_user_by_email(profile["email"])

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    if not check_password_hash(user["password"], current_password):
        flash("Current password is incorrect.", "error")
        return redirect(url_for("profile_page"))

    if len(new_password) < 8:
        flash("New password must contain at least 8 characters.", "error")
        return redirect(url_for("profile_page"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for("profile_page"))

    if current_password == new_password:
        flash("New password must be different from the current password.", "error")
        return redirect(url_for("profile_page"))

    password_hash = generate_password_hash(new_password)

    updated = update_user_password(
        session["user_id"],
        password_hash
    )

    if not updated:
        flash("Unable to update password. Please try again.", "error")
        return redirect(url_for("profile_page"))

    flash("Password changed successfully!", "success")

    return redirect(url_for("profile_page"))


# ---------------- CREATE TASK PAGE ----------------

@app.route("/create-task")
@login_required
def create_task_page():

    return render_template("create_task.html")


# ---------------- VIEW TASKS PAGE ----------------

@app.route("/tasks")
@login_required
def view_tasks_page():

    return render_template("view_tasks.html")


# ---------------- GET ALL TASKS API ----------------

@app.route("/api/tasks", methods=["GET"])
@login_required
def get_tasks():

    user_id = session["user_id"]

    tasks = get_all_tasks(user_id)

    return jsonify([dict(task) for task in tasks]), 200


# ---------------- CREATE TASK API ----------------

@app.route("/api/tasks", methods=["POST"])
@login_required
def create_task():

    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    priority = data.get("priority", "Medium")
    due_date = data.get("due_date", "")
    category = data.get("category", "Other")

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    if len(title) > 100 or len(description) > 500:
        return jsonify({"error": "Task details are too long"}), 400

    if priority not in VALID_PRIORITIES:
        return jsonify({"error": "Invalid priority"}), 400

    if category not in VALID_CATEGORIES:
        return jsonify({"error": "Invalid task category"}), 400

    if due_date:
        try:
            date.fromisoformat(due_date)
        except ValueError:
            return jsonify({"error": "Invalid due date"}), 400

    task_id = add_task(
        title,
        description,
        priority,
        due_date,
        session["user_id"],
        category
    )

    return jsonify({
        "message": "Task created successfully",
        "id": task_id
    }), 201


# ---------------- UPDATE TASK API ----------------

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def edit_task(task_id):

    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    priority = data.get("priority")
    due_date = data.get("due_date", "")
    status = data.get("status")
    category = data.get("category", "Other")

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    if len(title) > 100 or len(description) > 500:
        return jsonify({"error": "Task details are too long"}), 400

    if priority not in VALID_PRIORITIES:
        return jsonify({"error": "Invalid priority"}), 400

    if status not in VALID_STATUSES:
        return jsonify({"error": "Invalid status"}), 400

    if category not in VALID_CATEGORIES:
        return jsonify({"error": "Invalid task category"}), 400

    if due_date:
        try:
            date.fromisoformat(due_date)
        except ValueError:
            return jsonify({"error": "Invalid due date"}), 400

    updated = update_task(
        task_id,
        title,
        description,
        priority,
        due_date,
        status,
        session["user_id"],
        category
    )

    if not updated:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "message": "Task updated successfully"
    }), 200


# ---------------- DELETE TASK API ----------------

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def remove_task(task_id):

    deleted = delete_task(
        task_id,
        session["user_id"]
    )

    if not deleted:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "message": "Task deleted successfully"
    }), 200


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)
