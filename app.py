import sqlite3
from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            course TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Student DBMS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f6f9; }
        .container { max-width: 900px; margin: auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; }
        form { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 25px; }
        input { padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { grid-column: span 2; padding: 10px; background: #27ae60; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #2c3e50; color: white; }
        .del-btn { background: #c0392b; color: white; text-decoration: none; padding: 5px 10px; border-radius: 3px; }
        .error { color: #c0392b; font-weight: bold; }
    </style>
</head>
<body>
<div class="container">
    <h2>Student Management System (DBMS)</h2>
    
    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}

    <form method="POST" action="/add">
        <input type="text" name="name" placeholder="Full Name" required>
        <input type="text" name="roll_no" placeholder="Roll Number" required>
        <input type="text" name="course" placeholder="Course" required>
        <input type="email" name="email" placeholder="Email Address" required>
        <button type="submit">Add Student Record</button>
    </form>

    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Roll No</th>
            <th>Course</th>
            <th>Email</th>
            <th>Action</th>
        </tr>
        {% for s in students %}
        <tr>
            <td>{{ s[0] }}</td>
            <td>{{ s[1] }}</td>
            <td>{{ s[2] }}</td>
            <td>{{ s[3] }}</td>
            <td>{{ s[4] }}</td>
            <td><a class="del-btn" href="/delete/{{ s[0] }}">Delete</a></td>
        </tr>
        {% endfor %}
    </table>
</div>
</body>
</html>
"""


@app.route("/")
def index():
    error = request.args.get("error")
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, students=students, error=error)


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"].strip()
    roll = request.form["roll_no"].strip()
    course = request.form["course"].strip()
    email = request.form["email"].strip()

    try:
        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, roll_no, course, email) VALUES (?, ?, ?, ?)",
            (name, roll, course, email),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    except sqlite3.IntegrityError:
        return redirect(
            url_for("index", error="Roll Number already exists! Must be unique.")
        )


@app.route("/delete/<int:student_id>")
def delete_student(student_id):
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
