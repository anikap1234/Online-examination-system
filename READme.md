# Online Examination System

A complete SQL-backed Online Exam System built using **Flask**, designed for DBMS coursework.  
This updated README fully reflects:

- the new **QID-based Questions table**
- corrected routes
- final working structure of `manage_quiz.html` & `edit_question.html`
- updated app.py logic
- your current folder layout & behaviour

---

## 📌 Overview

This web application allows administrators, staff, and students to interact in a structured examination environment.

### ✔ Admin  
Manage staff & student accounts.  
View high-level platform statistics.

### ✔ Staff  
Create quizzes, add/edit/delete questions, assign quizzes, view results.

### ✔ Students  
Take assigned quizzes, view results, see leaderboard.

---

## 🚀 Features

### 🔐 Authentication  
- Admin login  
- Staff login  
- Student login  
- Session-based role control  

### 📝 Quiz Management (Staff)
- Create quiz (with Quiz_ID + name)  
- Add questions with 4 options, answer, and marks  
- **Edit questions using QID (AUTO_INCREMENT primary key)**  
- Delete questions safely  
- Update marks & recalculate scores  
- View quiz statistics (avg, highest, lowest, submissions)

### 🧑‍🎓 Student Workflow
- Dashboard showing assigned quizzes  
- Attempt quiz  
- Submission stored in `STUDENT_ANSWERS`  
- Marks calculated based on correct responses  
- Results displayed  
- Leaderboard accessible  

---

## 🧰 Tech Stack

- **Python 3.10+**  
- **Flask**  
- **MySQL / MariaDB**  
- **HTML + CSS + Bootstrap**  
- **Jinja2 templates**

---

## 📦 Requirements

Install all dependencies:

```bash
pip install -r requirements.txt
