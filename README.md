# TaskFlow – Smart Task Management System

**Live Demo:** https://pavithra151.pythonanywhere.com

TaskFlow is a web-based task management application designed to help users organize, track, and manage their daily activities efficiently. It provides a simple interface for managing tasks, monitoring deadlines, and tracking productivity.

## Features

- **User Authentication:** User registration, login, and logout.
- **Dashboard:** Overview of tasks and productivity statistics.
- **Task Management:** Create, view, edit, and delete tasks.
- **Task Categories:** Organize tasks into Work, Personal, College, Projects, and Other.
- **Priority Management:** Assign priorities to tasks.
- **Search and Filters:** Find tasks using search and filtering options.
- **Task Status:** Track task completion and progress.
- **Deadline Tracking:** Identify overdue, due-today, and upcoming tasks.
- **Profile Management:** Update profile information and change passwords.
- **Browser Notifications:** Receive task reminders through browser notifications.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML | Page structure |
| CSS | Styling and layout |
| JavaScript | Frontend interactivity |
| Git & GitHub | Version control |
| PythonAnywhere | Deployment and hosting |

## Project Structure

```text
TaskFlow/
│
├── app.py
├── database.py
├── requirements.txt
│
├── static/
│   ├── css/
│   │   ├── auth.css
│   │   └── pages.css
│   ├── script.js
│   └── style.css
│
├── templates/
│   ├── create_task.html
│   ├── home.html
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   ├── register.html
│   └── view_tasks.html
│
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/pavithrapalanisamy63473cse2427-alt/TaskFlow.git
```

### 2. Navigate to the project folder

```bash
cd TaskFlow
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## Database

TaskFlow uses SQLite to store user information and task details. The database is initialized by the application when it starts.

## Deployment

The application is deployed using **PythonAnywhere**.

**Live Application:** https://pavithra151.pythonanywhere.com

## Future Enhancements

- Calendar-based task visualization.
- Advanced productivity analytics.
- Additional reminder options.

## Author

**Pavithra P.**

- GitHub: [pavithralanisamy63473cse2427-alt](https://github.com/pavithrapalanisamy63473cse2427-alt)

---

*TaskFlow – Organize your work. Manage your time. Stay productive.*
