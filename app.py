import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lifeos.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        deadline TEXT,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Active',
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        deadline TEXT,
        status TEXT DEFAULT 'Active',
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        project_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        priority TEXT DEFAULT 'Medium',
        deadline TEXT,
        status TEXT DEFAULT 'Pending',
        depends_on INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(depends_on) REFERENCES tasks(id)
    );

    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        content TEXT,
        uploaded_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    conn.commit()
    conn.close()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def current_user():
    if "user_id" not in session:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    conn.close()
    return user


def seed_demo_data(user_id):
    conn = get_db()
    now = datetime.utcnow().isoformat()
    if conn.execute("SELECT COUNT(*) FROM projects WHERE user_id=?", (user_id,)).fetchone()[0] == 0:
        cur = conn.execute(
            "INSERT INTO projects(user_id,name,description,deadline,status,created_at) VALUES(?,?,?,?,?,?)",
            (user_id, "LifeOS AI", "Personal intelligence command center", "2026-10-15", "Active", now)
        )
        project_id = cur.lastrowid
        conn.execute(
            "INSERT INTO goals(user_id,title,description,deadline,priority,status,created_at) VALUES(?,?,?,?,?,?,?)",
            (user_id, "Build a connected personal knowledge system",
             "Connect goals, projects, tasks and documents.", "2026-10-31", "High", "Active", now)
        )
        conn.execute(
            "INSERT INTO tasks(user_id,project_id,title,description,priority,deadline,status,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (user_id, project_id, "Create the LifeOS dashboard",
             "Finish the first working dashboard.", "High", "2026-10-05", "Pending", now)
        )
        conn.execute(
            "INSERT INTO tasks(user_id,project_id,title,description,priority,deadline,status,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (user_id, project_id, "Test the application",
             "Verify authentication and core workflows.", "Medium", "2026-10-07", "Pending", now)
        )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if not name or not email or not password:
            flash("Please complete all fields.", "error")
            return render_template("register.html")
        conn = get_db()
        try:
            cur = conn.execute(
                "INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
                (name, email, generate_password_hash(password), datetime.utcnow().isoformat())
            )
            user_id = cur.lastrowid
            conn.commit()
            conn.close()
            seed_demo_data(user_id)
            session["user_id"] = user_id
            session["name"] = name
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            conn.close()
            flash("An account with that email already exists.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    conn = get_db()
    goals = conn.execute("SELECT * FROM goals WHERE user_id=? ORDER BY deadline IS NULL, deadline LIMIT 5", (uid,)).fetchall()
    projects = conn.execute("SELECT * FROM projects WHERE user_id=? ORDER BY id DESC LIMIT 6", (uid,)).fetchall()
    tasks = conn.execute("""
        SELECT tasks.*, projects.name AS project_name
        FROM tasks LEFT JOIN projects ON tasks.project_id=projects.id
        WHERE tasks.user_id=? ORDER BY
        CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
        tasks.deadline IS NULL, tasks.deadline
        LIMIT 8
    """, (uid,)).fetchall()
    counts = {
        "goals": conn.execute("SELECT COUNT(*) FROM goals WHERE user_id=?", (uid,)).fetchone()[0],
        "projects": conn.execute("SELECT COUNT(*) FROM projects WHERE user_id=?", (uid,)).fetchone()[0],
        "pending": conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND status!='Completed'", (uid,)).fetchone()[0],
        "documents": conn.execute("SELECT COUNT(*) FROM documents WHERE user_id=?", (uid,)).fetchone()[0],
    }
    conn.close()
    return render_template("dashboard.html", user=current_user(), goals=goals, projects=projects, tasks=tasks, counts=counts)


@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    uid = session["user_id"]
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO goals(user_id,title,description,deadline,priority,status,created_at) VALUES(?,?,?,?,?,?,?)",
            (uid, request.form["title"], request.form.get("description",""),
             request.form.get("deadline") or None, request.form.get("priority","Medium"),
             request.form.get("status","Active"), datetime.utcnow().isoformat())
        )
        conn.commit()
        flash("Goal created.", "success")
        return redirect(url_for("goals"))
    rows = conn.execute("SELECT * FROM goals WHERE user_id=? ORDER BY deadline IS NULL, deadline", (uid,)).fetchall()
    conn.close()
    return render_template("goals.html", goals=rows)


@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    uid = session["user_id"]
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO projects(user_id,name,description,deadline,status,created_at) VALUES(?,?,?,?,?,?)",
            (uid, request.form["name"], request.form.get("description",""),
             request.form.get("deadline") or None, request.form.get("status","Active"),
             datetime.utcnow().isoformat())
        )
        conn.commit()
        flash("Project created.", "success")
        return redirect(url_for("projects"))
    rows = conn.execute("SELECT * FROM projects WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
    conn.close()
    return render_template("projects.html", projects=rows)


@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    uid = session["user_id"]
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            """INSERT INTO tasks(user_id,project_id,title,description,priority,deadline,status,depends_on,created_at)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (uid, request.form.get("project_id") or None, request.form["title"],
             request.form.get("description",""), request.form.get("priority","Medium"),
             request.form.get("deadline") or None, request.form.get("status","Pending"),
             request.form.get("depends_on") or None, datetime.utcnow().isoformat())
        )
        conn.commit()
        flash("Task created.", "success")
        return redirect(url_for("tasks"))
    task_rows = conn.execute("""
        SELECT tasks.*, projects.name AS project_name
        FROM tasks LEFT JOIN projects ON tasks.project_id=projects.id
        WHERE tasks.user_id=? ORDER BY tasks.deadline IS NULL, tasks.deadline
    """, (uid,)).fetchall()
    project_rows = conn.execute("SELECT * FROM projects WHERE user_id=? ORDER BY name", (uid,)).fetchall()
    conn.close()
    return render_template("tasks.html", tasks=task_rows, projects=project_rows)


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
@login_required
def complete_task(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET status='Completed' WHERE id=? AND user_id=?", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("tasks"))


@app.route("/documents", methods=["GET", "POST"])
@login_required
def documents():
    uid = session["user_id"]
    if request.method == "POST":
        uploaded = request.files.get("file")
        if not uploaded or not uploaded.filename:
            flash("Choose a file first.", "error")
            return redirect(url_for("documents"))
        filename = os.path.basename(uploaded.filename)
        save_path = os.path.join(UPLOAD_DIR, f"{uid}_{filename}")
        uploaded.save(save_path)
        content = ""
        if filename.lower().endswith((".txt", ".md", ".csv")):
            try:
                with open(save_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()[:50000]
            except OSError:
                pass
        conn = get_db()
        conn.execute(
            "INSERT INTO documents(user_id,filename,content,uploaded_at) VALUES(?,?,?,?)",
            (uid, filename, content, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        flash("Document uploaded.", "success")
        return redirect(url_for("documents"))
    conn = get_db()
    rows = conn.execute("SELECT * FROM documents WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
    conn.close()
    return render_template("documents.html", documents=rows)


@app.route("/graph")
@login_required
def graph():
    uid = session["user_id"]
    conn = get_db()
    goals = conn.execute("SELECT id,title FROM goals WHERE user_id=?", (uid,)).fetchall()
    projects = conn.execute("SELECT id,name FROM projects WHERE user_id=?", (uid,)).fetchall()
    tasks = conn.execute("SELECT id,title,project_id,depends_on FROM tasks WHERE user_id=?", (uid,)).fetchall()
    conn.close()
    nodes, links = [], []
    for g in goals:
        nodes.append({"id": f"goal-{g['id']}", "label": g["title"], "type": "goal"})
    for p in projects:
        nodes.append({"id": f"project-{p['id']}", "label": p["name"], "type": "project"})
    for t in tasks:
        nodes.append({"id": f"task-{t['id']}", "label": t["title"], "type": "task"})
        if t["project_id"]:
            links.append({"source": f"task-{t['id']}", "target": f"project-{t['project_id']}", "label": "belongs to"})
        if t["depends_on"]:
            links.append({"source": f"task-{t['id']}", "target": f"task-{t['depends_on']}", "label": "depends on"})
    return render_template("graph.html", nodes=nodes, links=links)


@app.route("/assistant", methods=["GET", "POST"])
@login_required
def assistant():
    answer = None
    if request.method == "POST":
        question = request.form.get("question","").strip()
        answer = generate_contextual_answer(session["user_id"], question)
    return render_template("assistant.html", answer=answer)


def generate_contextual_answer(uid, question):
    q = question.lower()
    conn = get_db()
    tasks = conn.execute("""
        SELECT tasks.*, projects.name AS project_name
        FROM tasks LEFT JOIN projects ON tasks.project_id=projects.id
        WHERE tasks.user_id=? AND tasks.status!='Completed'
    """, (uid,)).fetchall()
    goals = conn.execute("SELECT * FROM goals WHERE user_id=? AND status='Active'", (uid,)).fetchall()
    conn.close()

    if not tasks:
        return "You have no pending tasks. Consider creating a goal or project to give LifeOS more context."

    if "today" in q or "priorit" in q or "work on" in q:
        ranked = sorted(tasks, key=lambda t: (
            0 if t["priority"] == "High" else 1 if t["priority"] == "Medium" else 2,
            t["deadline"] or "9999-99-99"
        ))
        lines = []
        for i, t in enumerate(ranked[:3], 1):
            reason = []
            if t["priority"] == "High": reason.append("high priority")
            if t["deadline"]: reason.append(f"deadline {t['deadline']}")
            if t["project_name"]: reason.append(f"part of {t['project_name']}")
            lines.append(f"{i}. <strong>{t['title']}</strong> — {', '.join(reason) or 'currently pending'}")
        return "Based on your current tasks and context, consider:<br><br>" + "<br>".join(lines)

    if "postpone" in q or "delay" in q:
        return ("A reliable scenario requires a specific task and delay period. "
                "LifeOS can trace explicit task dependencies and show which downstream tasks may be affected. "
                "Try: <strong>What happens if I postpone my database task?</strong>")

    if "goal" in q:
        return f"You currently have <strong>{len(goals)}</strong> active goal(s). Connect each goal to projects and tasks so LifeOS can reason about dependencies."

    return ("I can reason over the goals, projects, tasks, deadlines and relationships currently stored in LifeOS. "
            "Try asking what to work on today, which tasks are high priority, or what could be affected by postponing a task.")


@app.route("/scenario", methods=["GET", "POST"])
@login_required
def scenario():
    result = None
    if request.method == "POST":
        task_id = request.form.get("task_id")
        days = int(request.form.get("days", 1))
        conn = get_db()
        task = conn.execute("SELECT * FROM tasks WHERE id=? AND user_id=?", (task_id, session["user_id"])).fetchone()
        affected = []
        if task:
            queue = [task["id"]]
            seen = set(queue)
            while queue:
                current = queue.pop(0)
                children = conn.execute(
                    "SELECT * FROM tasks WHERE user_id=? AND depends_on=?", (session["user_id"], current)
                ).fetchall()
                for child in children:
                    if child["id"] not in seen:
                        seen.add(child["id"])
                        affected.append(child)
                        queue.append(child["id"])
            result = {"task": task, "days": days, "affected": affected}
        conn.close()
    conn = get_db()
    task_rows = conn.execute(
        "SELECT id,title FROM tasks WHERE user_id=? AND status!='Completed' ORDER BY title", (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("scenario.html", tasks=task_rows, result=result)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "LifeOS AI"})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
