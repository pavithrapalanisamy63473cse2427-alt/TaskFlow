
import sqlite3

DATABASE = "tasks.db"

VALID_CATEGORIES = [
    "Work",
    "Personal",
    "College",
    "Projects",
    "Other"
]


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tasks table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'Medium',
            due_date TEXT,
            status TEXT DEFAULT 'Pending',
            category TEXT DEFAULT 'Other',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check existing task table columns
    columns = conn.execute(
        "PRAGMA table_info(tasks)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    # Add user_id to existing database if missing
    if "user_id" not in column_names:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN user_id INTEGER"
        )

    # Add category to existing database if missing
    if "category" not in column_names:
        conn.execute("""
            ALTER TABLE tasks
            ADD COLUMN category TEXT DEFAULT 'Other'
        """)

    conn.commit()
    conn.close()


# ---------------- USER FUNCTIONS ----------------

def create_user(name, email, password):
    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, password))

        conn.commit()
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None

    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_db_connection()

    user = conn.execute("""
        SELECT * FROM users
        WHERE email = ?
    """, (email,)).fetchone()

    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db_connection()

    user = conn.execute("""
        SELECT id, name, email, created_at
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    conn.close()
    return user


def update_user_profile(user_id, name, email):
    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            UPDATE users
            SET name = ?, email = ?
            WHERE id = ?
        """, (name, email, user_id))

        conn.commit()
        return cursor.rowcount > 0

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def update_user_password(user_id, new_password_hash):
    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            UPDATE users
            SET password = ?
            WHERE id = ?
        """, (new_password_hash, user_id))

        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()


# ---------------- TASK FUNCTIONS ----------------

def get_all_tasks(user_id):
    conn = get_db_connection()

    tasks = conn.execute("""
        SELECT * FROM tasks
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    conn.close()
    return tasks


def add_task(title, description, priority, due_date,
             user_id, category="Other"):

    if category not in VALID_CATEGORIES:
        raise ValueError("Invalid task category")

    conn = get_db_connection()

    cursor = conn.execute("""
        INSERT INTO tasks
        (title, description, priority, due_date, user_id, category)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        description,
        priority,
        due_date,
        user_id,
        category
    ))

    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    return task_id


def update_task(task_id, title, description, priority,
                due_date, status, user_id, category=None):

    conn = get_db_connection()

    if category is None:
        cursor = conn.execute("""
            UPDATE tasks
            SET title = ?,
                description = ?,
                priority = ?,
                due_date = ?,
                status = ?
            WHERE id = ? AND user_id = ?
        """, (
            title,
            description,
            priority,
            due_date,
            status,
            task_id,
            user_id
        ))

    else:
        if category not in VALID_CATEGORIES:
            conn.close()
            raise ValueError("Invalid task category")

        cursor = conn.execute("""
            UPDATE tasks
            SET title = ?,
                description = ?,
                priority = ?,
                due_date = ?,
                status = ?,
                category = ?
            WHERE id = ? AND user_id = ?
        """, (
            title,
            description,
            priority,
            due_date,
            status,
            category,
            task_id,
            user_id
        ))

    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    return updated


def delete_task(task_id, user_id):
    conn = get_db_connection()

    cursor = conn.execute("""
        DELETE FROM tasks
        WHERE id = ? AND user_id = ?
    """, (task_id, user_id))

    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()

    return deleted
