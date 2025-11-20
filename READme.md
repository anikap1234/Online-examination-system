# Online Exam System

A simple web-based Online Examination System built with Flask. This project provides a lightweight platform for administrators, staff, and students to create quizzes, assign quizzes, take exams, and view results and leaderboards.

**Repository**: `Online-exam-system`

**Status:** Prototype / Student project (third-year DBMS coursework)

**Table of contents**
- Project Overview
- Features
- Tech Stack
- Requirements
- Installation (Windows PowerShell)
- Configuration
- Database
- Running the app
- Usage (roles & flows)
- Project structure
- Troubleshooting
- Contributing
- License & Contact

**Project Overview**

This application implements a basic online exam workflow:
- Admins can add and manage staff and student accounts, and view overall stats.
- Staff can create quizzes and questions, assign quizzes to students, and review submissions.
- Students can sign up, take quizzes, view results and leaderboard.

**Features**
- User authentication: signup & login for students and staff/admin.
- Quiz creation, question management, and assignment to students.
- Timed quizzes and submission handling.
- Result calculation and leaderboard view.
- Template-driven UI using Flask templates in `templates/`.

**Tech Stack**
- Python 3.8+ (tested with 3.8-3.11)
- Flask (micro web framework)
- MySQL / MariaDB (SQL script included) or any SQL RDBMS supported by the connector/library used in `config.py`.
- HTML + Bootstrap for templates (project supplies template files under `templates/`).

**Requirements**
- `requirements.txt` — install Python dependencies from this file.
- MySQL or MariaDB server (or adapt the SQL/script to your DB server).
- `config.py` — project expects configuration (DB credentials, secret key) in this file. A `config_example.py` is provided.

Installation (Windows PowerShell)

1. Open PowerShell and change to repository folder:

```powershell
cd 'C:/Anika/btechcse/3rd year/DBMS/Online-exam-system'
```

2. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Create the database schema (MySQL example):

```powershell
# Adjust user/host and database name as necessary
mysql -u <db_user> -p < combined_schema_and_routines.sql
```

5. Copy and update the configuration file:

```powershell
copy .\config_example.py .\config.py
# Edit config.py to set your DB credentials and any secret keys
notepad .\config.py
```

Notes: If you prefer a different RDBMS (SQLite, PostgreSQL), adapt the schema and connection settings accordingly.

**Configuration**
- The repository includes `config_example.py` which contains example settings. Copy it to `config.py` and update:
  - Database host, name, user, password
  - Secret key for Flask sessions
  - Any other environment-specific flags

If the project uses environment variables, set them in PowerShell before running:

```powershell
$env:FLASK_ENV = 'development'
$env:FLASK_APP = 'app.py'
# or set DB creds as environment variables if config.py reads from them
```

**Database**
- A file `combined_schema_and_routines.sql` is included with table schemas, stored procedures or routines used by the app.
- Typical steps:
  1. Create a database (example: `online_exam`).
  2. Import the SQL file into the DB server.
  3. Ensure the user in `config.py` has appropriate permissions.

**Run the application**

From PowerShell with the virtualenv active:

```powershell
# Option A: Run directly
python app.py

# Option B: Use Flask CLI (if supported)
$env:FLASK_APP = 'app.py'; $env:FLASK_ENV = 'development'
flask run
```

Access the app in your browser at `http://127.0.0.1:5000/`.

**Usage (roles & flows)**
- Admin: manage users, view stats, manage quizzes at admin dashboard routes.
- Staff: create quizzes and questions via `create_quiz.html` / `add_ques.html` templates; assign quizzes using `assign_quiz.html`.
- Student: signup/login, view assigned quizzes in `stu_quiz.html`, take quiz under `take_quiz.html`, view results in `quiz_result.html` and see leaderboard.

Look at the templates list in the project for route names and UI pages.

**Project structure**
- `app.py` - main Flask application entrypoint.
- `config.py` / `config_example.py` - configuration.
- `combined_schema_and_routines.sql` - DB schema & routines.
- `requirements.txt` - Python package dependencies.
- `templates/` - HTML templates used by the app (list included in the workspace).

Key template files:
- `index.html`, `login.html`, `signup.html`
- `create_quiz.html`, `add_ques.html`, `assign_quiz.html`
- `take_quiz.html`, `quiz_result.html`, `leaderboard.html`
- `admin_staff.html`, `admin_students.html`, `staff_dashboard.html`, `stu_dashboard.html`

**Troubleshooting / Tips**
- Database connection issues: verify `config.py` credentials and that the DB server is reachable.
- Missing packages: ensure you installed from `requirements.txt` inside the virtual environment.
- If the app fails to start, run `python app.py` from PowerShell — errors will appear in the terminal and are the fastest way to debug.

**Testing**
- This repository does not include an automated test suite by default. To add tests, consider using `pytest` and adding tests under a `tests/` directory.

**Contributing**
- Fork the repository and create a feature branch for changes.
- Keep changes focused and open a pull request with a clear description of what you changed and why.
- Add tests for any new functionality where applicable.

**License**
- This project is a student coursework example. Add a `LICENSE` file if you want to open-source it (MIT/Apache recommended for permissive licensing).

**Contact / Support**
- For questions about the project structure or running the app, open an issue in your repo or contact the project author.

---

If you want, I can:
- update `config.py` with comments and examples,
- add a short `run_local.ps1` PowerShell script to automate setup,
- or create a minimal `README.md` screenshot and route map for easier onboarding.
Tell me which you'd like next.
