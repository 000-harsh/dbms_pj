import os
import sqlite3
from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

# Guarantee SQLite uses the exact directory where app.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")


def get_db_connection():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  """Creates the students table immediately when the module is loaded."""
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            course TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


# ---> CRITICAL FIX FOR GUNICORN / RENDER <---
# Runs at startup so tables exist before any requests hit the server
init_db()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Records DBMS</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #f1f5f9; color: #1e293b; padding: 40px 20px; }
        .wrapper { max-width: 950px; margin: 0 auto; }
        
        .header { background: #0f172a; color: #ffffff; padding: 24px 30px; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.4rem; font-weight: 700; }
        .badge { background: #334155; padding: 6px 14px; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }

        .card { background: #ffffff; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.05); }

        .alert-error { background: #fef2f2; border-left: 4px solid #ef4444; color: #991b1b; padding: 12px 16px; border-radius: 6px; margin-bottom: 24px; font-size: 0.95rem; }

        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 16px; }
        .form-group label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px; color: #475569; }
        .form-group input { width: 100%; padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.95rem; outline: none; transition: border-color 0.2s; }
        .form-group input:focus { border-color: #3b82f6; }

        .submit-btn { width: 100%; background: #2563eb; color: #ffffff; border: none; padding: 12px; font-size: 0.95rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: background 0.2s; margin-bottom: 35px; }
        .submit-btn:hover { background: #1d4ed8; }

        .table-container { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.95rem; }
        th { background: #f8fafc; color: #475569; font-weight: 600; padding: 14px 16px; border-bottom: 1px solid #e2e8f0; }
        td { padding: 14px 16px; border-bottom: 1px solid #f1f5f9; color: #334155; }
        tr:last-child td { border-bottom: none; }
        tr:hover { background: #f8fafc; }

        .btn-delete { background: #fee2e2; color: #dc2626; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; transition: all 0.2s; }
        .btn-delete:hover { background: #dc2626; color: #ffffff; }

        .empty-state { text-align: center; padding: 40px; color: #94a3b8; font-style: italic; }
    </style>
</head>
<body>
<div class="wrapper">
    <div class="header">
        <h1>Student Records Management System</h1>
        <div class="badge">Total Students: {{ students|length }}</div>
    </div>

    <div class="card">
        {% if error %}
            <div class="alert-error">
                <strong>Error:</strong> {{ error }}
            </div>
        {% endif %}

        <form method="POST" action="/add">
            <div class="form-grid">
                <div class="form-group">
                    <label for="name">Full Name</label>
                    <input type="text" id="name" name="name" placeholder="e.g. Aman Sharma" required>
                </div>
                <div class="form-group">
                    <label for="roll_no">Roll Number</label>
                    <input type="text" id="roll_no" name="roll_no" placeholder="e.g. CS101" required>
                </div>
                <div class="form-group">
                    <label for="course">Course</label>
                    <input type="text" id="course" name="course" placeholder="e.g. B.Tech CSE" required>
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" placeholder="e.g. aman@example.com" required>
                </div>
            </div>
            <button type="submit" class="submit-btn">Add Student Record</button>
        </form>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 60px;">ID</th>
                        <th>Name</th>
                        <th>Roll No</th>
                        <th>Course</th>
                        <th>Email</th>
                        <th style="width: 100px; text-align: center;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% if students %}
                        {% for s in students %}
                        <tr>
                            <td><strong>#{{ s['id'] }}</strong></td>
                            <td>{{ s['name'] }}</td>
                            <td><span style="font-family: monospace; font-weight: 600;">{{ s['roll_no'] }}</span></td>
                            <td>{{ s['course'] }}</td>
                            <td>{{ s['email'] }}</td>
                            <td style="text-align: center;">
                                <a class="btn-delete" href="/delete/{{ s['id'] }}" onclick="return confirm('Delete record for {{ s['name'] }}?');">Delete</a>
                            </td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="6" class="empty-state">No student records found in the database. Add one above!</td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
"""


@app.route("/")
def index():
  error = request.args.get("error")
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, name, roll_no, course, email FROM students ORDER BY id DESC"
  )
  students = cursor.fetchall()
  conn.close()
  return render_template_string(HTML_TEMPLATE, students=students, error=error)


@app.route("/add", methods=["POST"])
def add_student():
  name = request.form.get("name", "").strip()
  roll = request.form.get("roll_no", "").strip()
  course = request.form.get("course", "").strip()
  email = request.form.get("email", "").strip()

  if not (name and roll and course and email):
    return redirect(url_for("index", error="All fields are required!"))

  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, roll_no, course, email) VALUES (?, ?, ?,"
        " ?)",
        (name, roll, course, email),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))
  except sqlite3.IntegrityError:
    return redirect(
        url_for(
            "index",
            error=(
                f"Roll Number '{roll}' already exists in the database. Roll"
                " numbers must be unique."
            ),
        )
    )
  except Exception as e:
    return redirect(url_for("index", error=f"Database error: {str(e)}"))


@app.route("/delete/<int:student_id>")
def delete_student(student_id):
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
  conn.commit()
  conn.close()
  return redirect(url_for("index"))


if __name__ == "__main__":
  app.run(debug=True)
