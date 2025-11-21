import os
from turtle import st
from flask import Flask, render_template, request, redirect, session, url_for, flash, abort
from config import get_db
import mysql.connector
import bcrypt
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "replace-this-in-prod")

DEFAULT_STUDENT = {
    "Sem": 1,
    "s_ph_no": "0000000000",
    "s_gender": "O",
    "Date": 1,
    "Month": 1,
    "Year": 2000
}

DEFAULT_STAFF = {
    "st_Ph_no": "0000000000",
    "DOB": "1970-01-01"
}

def recalculate_scores(quiz_id):
    """Recalculate scores for all students who attempted a quiz."""

    db = get_db()
    cursor = db.cursor(buffered=True)

    # Get all student attempts
    cursor.execute("SELECT student_ID FROM SCORE WHERE Quiz_ID=%s", (quiz_id,))
    students = cursor.fetchall()

    # Load updated questions
    cursor.execute("""
        SELECT Question, Answer, Marks
        FROM QUESTIONS
        WHERE Quiz_ID=%s
    """, (quiz_id,))
    qrows = cursor.fetchall()

    # Recalculate for each student
    for s in students:
        sid = s[0]
        new_score = 0

        for q, ans, marks in qrows:
            cursor.execute("""
                SELECT student_answer
                FROM STUDENT_ANSWERS
                WHERE student_ID=%s AND Quiz_ID=%s AND Question=%s
            """, (sid, quiz_id, q))

            row = cursor.fetchone()
            if row and row[0] == ans:
                new_score += marks

        # Update score table
        cursor.execute("""
            UPDATE SCORE
            SET Score=%s
            WHERE student_ID=%s AND Quiz_ID=%s
        """, (new_score, sid, quiz_id))

    db.commit()
    cursor.close()
    db.close()

@app.context_processor
def inject_user():
    return {
        "logged_in": ("user_id" in session),
        "role": session.get("role"),
        "session": session,
        "current_year": datetime.now().year
    }

# ============================
# HOME
# ============================
@app.route("/")
def home():
    return render_template("index.html")


# ============================
# SIGNUP
# ============================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    msg = ""
    if request.method == "POST":
        role = request.form.get("role")
        db = get_db()
        cursor = db.cursor(buffered=True)

        try:
            # ==========================
            # STUDENT SIGNUP
            # ==========================
            if role == "student":
                student_id = request.form.get("student_id")
                name = request.form.get("student_name")
                email = request.form.get("student_email")
                dept = request.form.get("student_dept")
                password = request.form.get("password")

                pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

                cursor.execute("""
                    INSERT INTO STUDENT
                    (student_ID, s_name, Sem, s_emailid, s_ph_no, s_gender, Date, Month, Year, s_password, Dept_ID)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    student_id, name,
                    DEFAULT_STUDENT["Sem"], email, DEFAULT_STUDENT["s_ph_no"],
                    DEFAULT_STUDENT["s_gender"], DEFAULT_STUDENT["Date"],
                    DEFAULT_STUDENT["Month"], DEFAULT_STUDENT["Year"],
                    pw_hash, dept
                ))

                db.commit()
                flash("Student registered successfully!")
                return redirect(url_for("login"))

            # ==========================
            # STAFF SIGNUP
            # ==========================
            elif role == "staff":
                staff_id = request.form.get("staff_id")
                name = request.form.get("staff_name")
                email = request.form.get("staff_email")
                dept = request.form.get("staff_dept")
                password = request.form.get("password")

                pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

                cursor.execute("""
                    INSERT INTO STAFF
                    (Staff_ID, st_name, st_emailid, Dept_ID, st_Ph_no, DOB, st_password)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    staff_id, name, email, dept,
                    DEFAULT_STAFF["st_Ph_no"], DEFAULT_STAFF["DOB"], pw_hash
                ))

                db.commit()
                flash("Staff registered successfully!")
                return redirect(url_for("login"))

        except mysql.connector.Error as e:
            print("MYSQL ERROR:", e)
            msg = "ERROR: " + str(e)

        finally:
            cursor.close()
            db.close()

    return render_template("signup.html", msg=msg)


# ============================
# LOGIN
# ============================
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")
        role = request.form.get("role")

        db = get_db()
        cursor = db.cursor(buffered=True)

        try:
            # Fetch correct table based on role
            if role == "student":
                cursor.execute("SELECT student_ID, s_password FROM STUDENT WHERE student_ID=%s", (user_id,))
            else:
                cursor.execute("SELECT Staff_ID, st_password FROM STAFF WHERE Staff_ID=%s", (user_id,))

            row = cursor.fetchone()
            if not row:
                msg = "User not found"
                return render_template("login.html", msg=msg)

            stored = row[1]

            # Try bcrypt verification
            try:
                if bcrypt.checkpw(password.encode(), stored.encode()):
                    session["user_id"] = user_id
                    session["role"] = role

                    # Redirect to correct dashboard
                    if role == "student":
                        return redirect(url_for("student_dashboard"))
                    else:
                        return redirect(url_for("staff_dashboard"))
            except:
                # Plain-text fallback
                if password == stored:
                    session["user_id"] = user_id
                    session["role"] = role

                    if role == "student":
                        return redirect(url_for("student_dashboard"))
                    else:
                        return redirect(url_for("staff_dashboard"))

            msg = "Incorrect password"

        finally:
            cursor.close()
            db.close()

    return render_template("login.html", msg=msg)

# ============================
# LOGOUT
# ============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ============================
# STUDENT DASHBOARD
# ============================
@app.route("/student/dashboard")
def student_dashboard():
    if "role" not in session or session["role"] != "student":
        return redirect(url_for("login"))

    stu = session["user_id"]
    db = get_db()
    cursor = db.cursor(buffered=True)

    try:
        # Basic Student Info
        cursor.execute("SELECT s_name, s_emailid, Dept_ID FROM STUDENT WHERE student_ID=%s", (stu,))
        data = cursor.fetchone()
        name, email, dept_id = data

        # Resolve Dept name using stored function get_department_name
        cursor.execute("SELECT get_department_name(%s)", (dept_id,))
        dept_name_row = cursor.fetchone()
        dept_name = dept_name_row[0] if dept_name_row else dept_id

        # Stats (functions already exist in DB)
        cursor.execute("SELECT get_student_average(%s), get_total_quizzes_taken(%s)", (stu, stu))
        avg, taken = cursor.fetchone()

        # All quizzes available for student dept
        cursor.execute("""
            SELECT q.Quiz_ID, q.Quiz_name, s.st_name
            FROM QUIZ q
            JOIN STAFF s ON q.Staff_ID=s.Staff_ID
            JOIN STUDENT st ON st.Dept_ID=s.Dept_ID
            WHERE st.student_ID=%s
        """, (stu,))
        quizzes = cursor.fetchall()

        # Get student's quiz details (includes score if taken)
        cursor.callproc("get_student_quiz_details", (stu,))
        details = []
        for res in cursor.stored_results():
            details = res.fetchall()
            break

        # ----------------------------------------------------
        #  Build mapping quiz_id → taken(True/False)
        # ----------------------------------------------------
        taken_map = {}

        # Create mapping quiz_name → quiz_id
        name_to_id = {q[1]: q[0] for q in quizzes}

        for row in details:
            quiz_name, score, remark, staff = row
            qid = name_to_id.get(quiz_name)
            if qid:
                taken_map[qid] = (score is not None)

    finally:
        cursor.close()
        db.close()

    return render_template(
        "stu_dashboard.html",
        student_name=name,
        email=email,
        dept_name=dept_name,
        avg_score=avg,
        total_taken=taken,
        quizzes=quizzes,
        quiz_details=details,
        d_taken=taken_map
    )


# ============================
# STUDENT TAKE QUIZ
# ============================
@app.route("/student/quiz/<quiz_id>")
def take_quiz(quiz_id):
    if session.get("role") != "student":
        return redirect(url_for("login"))

    stu = session["user_id"]

    # Check if already taken
    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("""
        SELECT 1 FROM SCORE WHERE student_ID=%s AND Quiz_ID=%s
    """, (stu, quiz_id))

    if cursor.fetchone():
        cursor.close()
        db.close()
        flash("You have already taken this quiz.")
        return redirect(url_for("student_dashboard"))

    cursor.execute("SELECT Quiz_name FROM QUIZ WHERE Quiz_ID=%s", (quiz_id,))
    qrow = cursor.fetchone()
    quiz_name = qrow[0] if qrow else "Quiz"

    cursor.execute("""
        SELECT Question, Option1, Option2, Option3, Option4
        FROM QUESTIONS WHERE Quiz_ID=%s
    """, (quiz_id,))
    questions = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("take_quiz.html",
                           quiz_id=quiz_id,
                           quiz_name=quiz_name,
                           questions=questions)


# ============================
# SUBMIT QUIZ WITH MARKS
# ============================
@app.route("/student/submit_quiz/<quiz_id>", methods=["POST"])
def submit_quiz(quiz_id):
    if "role" not in session or session["role"] != "student":
        return redirect(url_for("login"))

    stu = session["user_id"]
    db = get_db()
    cursor = db.cursor(buffered=True)

    # Load questions
    cursor.execute("SELECT Question, Answer, Marks FROM QUESTIONS WHERE Quiz_ID=%s", (quiz_id,))
    rows = cursor.fetchall()

    score = 0

    for q, a, marks in rows:
        user_ans = request.form.get(q)

        # Store student answer
        cursor.execute("""
            INSERT INTO STUDENT_ANSWERS (student_ID, Quiz_ID, Question, student_answer)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE student_answer=%s
        """, (stu, quiz_id, q, user_ans, user_ans))

        if user_ans == a:
            score += marks

    score_id = str(uuid.uuid4())[:20]

    cursor.execute("SELECT Staff_ID FROM QUIZ WHERE Quiz_ID=%s", (quiz_id,))
    owner = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO SCORE (Score_ID, student_ID, Score, Staff_ID, Quiz_ID)
        VALUES (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE Score=%s
    """, (score_id, stu, score, owner, quiz_id, score))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for("student_result"))


# ============================
# STUDENT RESULT
# ============================
@app.route("/student/result")
def student_result():
    if session.get("role") != "student":
        return redirect(url_for("login"))

    stu = session["user_id"]
    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.callproc("get_student_scores", (stu,))
    results = []
    for res in cursor.stored_results():
        results = res.fetchall()
        break

    cursor.close()
    db.close()
    return render_template("quiz_result.html", scores=results)


# ============================
# LEADERBOARD (filter by subject)
# ============================
@app.route("/leaderboard")
def leaderboard():
    quiz_id = request.args.get("quiz_id")

    db = get_db()
    cursor = db.cursor(buffered=True)

    # Load all quizzes for filter dropdown
    cursor.execute("SELECT Quiz_ID, Quiz_name FROM QUIZ ORDER BY Quiz_name")
    quizzes = cursor.fetchall()

    leaderboard_data = []
    quiz_stats = None
    quiz_avg = None

    try:
        if quiz_id:
            # If filtering by quiz -> show per-student scores (same as before)
            cursor.execute("""
                SELECT sc.Score_ID, sc.student_ID, st.s_name, sc.Score, sc.Remark, 
                       q.Quiz_name
                FROM SCORE sc
                JOIN STUDENT st ON sc.student_ID=st.student_ID
                JOIN QUIZ q ON sc.Quiz_ID=q.Quiz_ID
                WHERE sc.Quiz_ID=%s
                ORDER BY sc.Score DESC
            """, (quiz_id,))
            leaderboard_data = cursor.fetchall()

            # Also call stored procedure get_quiz_statistics to get aggregate stats
            cursor.callproc("get_quiz_statistics", (quiz_id,))
            stats_rows = []
            for res in cursor.stored_results():
                stats_rows = res.fetchall()
                break

            if stats_rows:
                # get_quiz_statistics returns: Quiz_name, COUNT(sc.Score_ID), AVG, MAX, MIN, COUNT(DISTINCT t.student_ID)
                row = stats_rows[0]
                quiz_stats = {
                    "Quiz_name": row[0],
                    "total_submissions": row[1],
                    "avg_score": row[2],
                    "max_score": row[3],
                    "min_score": row[4],
                    "students_attempted": row[5]
                }

            # Also fetch calculate_quiz_average for clearer avg & count
            cursor.callproc("calculate_quiz_average", (quiz_id,))
            avg_rows = []
            for res in cursor.stored_results():
                avg_rows = res.fetchall()
                break
            if avg_rows:
                arow = avg_rows[0]
                # calculate_quiz_average returns: Quiz_name, AVG, COUNT
                quiz_avg = {
                    "Quiz_name": arow[0],
                    "avg_score": arow[1],
                    "submissions": arow[2]
                }

        else:
            # No quiz filter -> call stored procedure get_leaderboard (full leaderboard)
            cursor.callproc("get_leaderboard")
            lb = []
            for res in cursor.stored_results():
                lb = res.fetchall()
                break
            # stored proc returns Score_ID, student_ID, s_name, Score, Remark, Quiz_name
            leaderboard_data = lb

    finally:
        cursor.close()
        db.close()

    return render_template("leaderboard.html",
                           leaderboard=leaderboard_data,
                           quizzes=quizzes,
                           selected_quiz=quiz_id,
                           quiz_stats=quiz_stats,
                           quiz_avg=quiz_avg)


# ============================
# STAFF DASHBOARD
# ============================
@app.route("/staff/dashboard")
def staff_dashboard():
    if session.get("role") != "staff":
        return redirect(url_for("login"))

    staff = session["user_id"]
    db = get_db()
    cursor = db.cursor(buffered=True)

    try:
        cursor.execute("""
            SELECT Quiz_ID, Quiz_name, Date_created
            FROM QUIZ WHERE Staff_ID=%s
        """, (staff,))
        quizzes = cursor.fetchall()

        cursor.execute("SELECT Dept_ID FROM STAFF WHERE Staff_ID=%s", (staff,))
        row = cursor.fetchone()
        dept_id = row[0] if row else None

        # Resolve dept name via stored function
        dept_name = dept_id
        if dept_id:
            cursor.execute("SELECT get_department_name(%s)", (dept_id,))
            r = cursor.fetchone()
            if r:
                dept_name = r[0]

    finally:
        cursor.close()
        db.close()

    return render_template("staff_dashboard.html",
                           quizzes=quizzes,
                           staff=staff,
                           dept_name=dept_name)


# ============================
# MANAGE QUIZ
# ============================
@app.route("/staff/manage/<quiz_id>")
def manage_quiz(quiz_id):
    if session.get("role") != "staff":
        return redirect(url_for("login"))

    staff = session["user_id"]
    db = get_db()
    cursor = db.cursor(buffered=True)

    try:
        cursor.execute("SELECT Staff_ID, Quiz_name FROM QUIZ WHERE Quiz_ID=%s", (quiz_id,))
        row = cursor.fetchone()

        if not row or row[0] != staff:
            flash("Unauthorized")
            return redirect(url_for("staff_dashboard"))

        quiz_name = row[1]

        cursor.execute("""
            SELECT QID, Question, Option1, Option2, Option3, Option4, Answer, Marks
            FROM QUESTIONS
            WHERE Quiz_ID=%s AND Staff_ID=%s
        """, (quiz_id, staff))

        questions = cursor.fetchall()

        # calculate_quiz_average stored procedure (avg & count)
        cursor.callproc("calculate_quiz_average", (quiz_id,))
        avg_rows = []
        for res in cursor.stored_results():
            avg_rows = res.fetchall()
            break
        quiz_avg = None
        if avg_rows:
            arow = avg_rows[0]
            quiz_avg = {
                "Quiz_name": arow[0],
                "avg_score": arow[1],
                "submissions": arow[2]
            }

        # get_quiz_statistics stored procedure (aggregate)
        cursor.callproc("get_quiz_statistics", (quiz_id,))
        stats_rows = []
        for res in cursor.stored_results():
            stats_rows = res.fetchall()
            break
        quiz_stats = None
        if stats_rows:
            srow = stats_rows[0]
            quiz_stats = {
                "Quiz_name": srow[0],
                "total_submissions": srow[1],
                "avg_score": srow[2],
                "max_score": srow[3],
                "min_score": srow[4],
                "students_attempted": srow[5]
            }

    finally:
        cursor.close()
        db.close()

    return render_template("manage_quiz.html",
                           quiz_id=quiz_id,
                           quiz_name=quiz_name,
                           questions=questions,
                           quiz_avg=quiz_avg,
                           quiz_stats=quiz_stats)


# ============================
# ADD QUESTION
# ============================
@app.route("/staff/add_question/<quiz_id>", methods=["GET", "POST"])
def add_question(quiz_id):
    if session.get("role") != "staff":
        return redirect(url_for("login"))

    staff = session["user_id"]

    if request.method == "POST":
        q = request.form.get("q")
        o1 = request.form.get("o1")
        o2 = request.form.get("o2")
        o3 = request.form.get("o3")
        o4 = request.form.get("o4")
        ans = request.form.get("ans")
        marks = request.form.get("marks")

        db = get_db()
        cursor = db.cursor(buffered=True)

        cursor.execute("""
            INSERT INTO QUESTIONS
            (Question, Staff_ID, Option1, Option2, Option3, Option4,
             Answer, Quiz_ID, Marks)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (q, staff, o1, o2, o3, o4, ans, quiz_id, marks))
        db.commit()

        cursor.close()
        db.close()
        return redirect(url_for("manage_quiz", quiz_id=quiz_id))

    return render_template("add_ques.html", quiz_id=quiz_id)


# ============================
# CREATE QUIZ  (IMPORTANT: MUST EXIST)
# ============================
@app.route("/staff/create_quiz", methods=["GET", "POST"])
def create_quiz():
    if "role" not in session or session["role"] != "staff":
        return redirect(url_for("login"))

    staff_id = session["user_id"]

    if request.method == "POST":
        quiz_id = request.form.get("quiz_id")
        quiz_name = request.form.get("quiz_name")

        if not quiz_id or not quiz_name:
            flash("Please fill all fields")
            return render_template("create_quiz.html")

        db = get_db()
        cursor = db.cursor(buffered=True)

        try:
            cursor.execute("""
                INSERT INTO QUIZ (Quiz_ID, Quiz_name, Date_created, Staff_ID)
                VALUES (%s, %s, NOW(), %s)
            """, (quiz_id, quiz_name, staff_id))
            db.commit()
        except mysql.connector.Error as e:
            flash("Error: " + str(e))
            return render_template("create_quiz.html")
        finally:
            cursor.close()
            db.close()

        flash("Quiz created successfully!")
        return redirect(url_for("staff_dashboard"))

    return render_template("create_quiz.html")


# ============================
# EDIT QUESTION
# ============================
@app.route("/staff/edit_question/<quiz_id>/<int:qid>")
def edit_question_form(quiz_id, qid):
    print("DEBUG ROUTE HIT:", quiz_id, qid)  # <-- Add this temporarily
    if session.get("role") != "staff":
        return redirect(url_for("login"))

    staff = session["user_id"]

    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("""
        SELECT QID, Question, Option1, Option2, Option3, Option4, Answer, Marks
        FROM QUESTIONS
        WHERE QID=%s AND Quiz_ID=%s AND Staff_ID=%s
    """, (qid, quiz_id, staff))

    q = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template("edit_question.html", quiz_id=quiz_id, q=q)

@app.route("/staff/edit_question/<quiz_id>/<int:qid>", methods=["POST"])
def edit_question(quiz_id, qid):
    if session.get("role") != "staff":
        return redirect(url_for("login"))

    staff = session["user_id"]

    q = request.form.get("q")
    o1 = request.form.get("o1")
    o2 = request.form.get("o2")
    o3 = request.form.get("o3")
    o4 = request.form.get("o4")
    ans = request.form.get("ans")
    marks = request.form.get("marks")

    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("""
        UPDATE QUESTIONS
        SET Question=%s, Option1=%s, Option2=%s, Option3=%s, Option4=%s,
            Answer=%s, Marks=%s
        WHERE QID=%s AND Quiz_ID=%s AND Staff_ID=%s
    """, (q, o1, o2, o3, o4, ans, marks, qid, quiz_id, staff))

    db.commit()
    cursor.close()
    db.close()

    flash("Question updated!", "success")
    return redirect(url_for("manage_quiz", quiz_id=quiz_id))

# ============================
# DELETE QUESTION
# ============================
@app.route("/staff/delete_question/<quiz_id>/<int:qid>", methods=["POST"])
def delete_question(quiz_id, qid):
    if session.get("role") != "staff":
        return redirect(url_for("login"))

    st = session["user_id"]
    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("""
        DELETE FROM QUESTIONS
        WHERE Question_ID=%s AND Quiz_ID=%s AND Staff_ID=%s
    """, (qid, quiz_id, st))

    db.commit()
    cursor.close()
    db.close()

    flash("Question deleted!", "success")
    return redirect(url_for("manage_quiz", quiz_id=quiz_id))

# ============================
# DELETE QUIZ
# ============================
@app.route("/staff/delete_quiz/<quiz_id>", methods=["POST"])
def delete_quiz(quiz_id):
    if "role" not in session or session["role"] != "staff":
        return redirect(url_for("login"))

    st = session["user_id"]
    db = get_db()
    cursor = db.cursor(buffered=True)

    try:
        # Manually delete dependent rows first (CASCADE fix)
        cursor.execute("DELETE FROM QUESTIONS WHERE Quiz_ID=%s", (quiz_id,))
        cursor.execute("DELETE FROM SCORE WHERE Quiz_ID=%s", (quiz_id,))
        cursor.execute("DELETE FROM TAKE WHERE Quiz_ID=%s", (quiz_id,))

        # Now delete the quiz
        cursor.execute("DELETE FROM QUIZ WHERE Quiz_ID=%s AND Staff_ID=%s",
                       (quiz_id, st))
        db.commit()

        flash("Quiz deleted successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"Error deleting quiz: {err.msg}", "danger")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for("staff_dashboard"))


# ============================
# EDIT QUIZ TITLE
# ============================
@app.route("/staff/edit_quiz_title/<quiz_id>", methods=["POST"])
def edit_quiz_title(quiz_id):
    if session.get("role") != "staff":
        return redirect(url_for("login"))

    staff = session["user_id"]
    new_title = request.form.get("quiz_name")

    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("""
        UPDATE QUIZ SET Quiz_name=%s
        WHERE Quiz_ID=%s AND Staff_ID=%s
    """, (new_title, quiz_id, staff))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for("manage_quiz", quiz_id=quiz_id))


# ============================
# SCORE VIEW
# ============================
@app.route("/staff/scores/<quiz_id>")
def staff_scores(quiz_id):
    if session.get("role") != "staff":
        return redirect(url_for("login"))

    staff = session["user_id"]

    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT Staff_ID FROM QUIZ WHERE Quiz_ID=%s", (quiz_id,))
    owner = cursor.fetchone()[0]

    if owner != staff:
        flash("Unauthorized")
        return redirect(url_for("staff_dashboard"))

    cursor.execute("""
        SELECT sc.Score_ID, sc.student_ID, st.s_name, sc.Score, sc.Remark
        FROM SCORE sc
        JOIN STUDENT st ON sc.student_ID=st.student_ID
        WHERE sc.Quiz_ID=%s
    """, (quiz_id,))
    scores = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("quiz_result.html", scores=scores)


# ============================
# ASSIGN QUIZ TO STUDENT (uses stored procedure)
# ============================
@app.route("/staff/assign_quiz", methods=["GET", "POST"])
def staff_assign_quiz():
    if session.get("role") != "staff":
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor(buffered=True)

    # Load students & quizzes to build form
    cursor.execute("SELECT student_ID, s_name FROM STUDENT ORDER BY s_name")
    students = cursor.fetchall()

    cursor.execute("SELECT Quiz_ID, Quiz_name FROM QUIZ WHERE Staff_ID=%s ORDER BY Quiz_name", (session["user_id"],))
    quizzes = cursor.fetchall()

    message = None

    if request.method == "POST":
        student = request.form.get("student_id")
        quiz = request.form.get("quiz_id")

        try:
            cursor.callproc("assign_quiz_to_student", (student, quiz))
            # Get any result set returned by procedure
            proc_result = []
            for r in cursor.stored_results():
                proc_result = r.fetchall()
                break
            if proc_result and isinstance(proc_result[0], tuple):
                # procedure SELECT CONCAT(...) returns a single column message
                message = proc_result[0][0]
            else:
                message = "Quiz assigned."
            db.commit()
            flash(message, "success")
        except mysql.connector.Error as e:
            db.rollback()
            flash(f"Error assigning quiz: {e.msg}", "danger")

    cursor.close()
    db.close()

    return render_template("assign_quiz.html", students=students, quizzes=quizzes, message=message)


# ============================
# STATIC PAGE FALLBACK
# ============================
@app.route("/<path:page>")
def render_page(page):
    if page in {"stu_dashboard.html", "student_dashboard.html", "staff_dashboard.html"}:
        return redirect(url_for("home"))

    if not page.endswith(".html"):
        page += ".html"

    try:
        return render_template(page)
    except:
        abort(404)


if __name__ == "__main__":
    app.run(debug=True)
