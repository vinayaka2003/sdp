import os
import sqlite3
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify, g
)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "mevi-workshop-development-key"
)

# Database configuration
os.makedirs(app.instance_path, exist_ok=True)

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(app.instance_path, "management.db")
)


# Database connection
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row

    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


# Create database table
def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


# Dashboard
@app.route("/")
def dashboard():
    db = get_db()

    total_students = db.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_courses = db.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    recent_students = db.execute(
        "SELECT * FROM students ORDER BY id DESC LIMIT 5"
    ).fetchall()

    return render_template(
        "index.html",
        total_students=total_students,
        total_courses=total_courses,
        recent_students=recent_students
    )


# Student management page
@app.route("/students")
def students():
    db = get_db()

    all_students = db.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    return render_template(
        "students.html",
        students=all_students
    )


# Add student
@app.route("/students/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    course = request.form.get("course", "").strip()

    if not name or not email or not course:
        flash("Please fill in all fields.", "error")
        return redirect(url_for("students"))

    if "@" not in email:
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("students"))

    db = get_db()

    try:
        db.execute(
            """
            INSERT INTO students (name, email, course)
            VALUES (?, ?, ?)
            """,
            (name, email, course)
        )
        db.commit()

        flash("Student added successfully!", "success")

    except sqlite3.IntegrityError:
        flash("This email address is already registered.", "error")

    return redirect(url_for("students"))


# Delete student
@app.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):
    db = get_db()

    db.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )
    db.commit()

    flash("Student record deleted.", "success")

    return redirect(url_for("students"))


# JSON API
@app.route("/api/students")
def students_api():
    db = get_db()

    records = db.execute(
        "SELECT id, name, email, course FROM students ORDER BY id DESC"
    ).fetchall()

    return jsonify([
        dict(record) for record in records
    ])


# Health check
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "TRAFFIC GODS"
    })


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "5001"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )