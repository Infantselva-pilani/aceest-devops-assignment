"""
ACEest Fitness & Gym - Flask Web Application
DevOps Assignment - CI/CD Pipeline Implementation
Student Roll No: 2024TM93572
Course: Introduction to DevOps (CSIZG514/SEZG514/SEUSZG514)
"""

from flask import Flask, jsonify, request
import sqlite3
import os
from datetime import date

app = Flask(__name__)
DB_NAME = os.environ.get("DB_NAME", "aceest_fitness.db")


# ---------- DATABASE INITIALIZATION ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        age INTEGER,
        weight REAL,
        program TEXT,
        membership_status TEXT DEFAULT 'Active'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        date TEXT NOT NULL,
        workout_type TEXT,
        duration_min INTEGER,
        notes TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        week TEXT,
        adherence INTEGER
    )
    """)

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- HEALTH CHECK ----------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "ACEest Fitness API"}), 200


# ---------- CLIENTS ----------
@app.route("/clients", methods=["GET"])
def get_clients():
    conn = get_db()
    clients = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(c) for c in clients]), 200


@app.route("/clients", methods=["POST"])
def add_client():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Client name is required"}), 400

    name = data["name"].strip()
    if not name:
        return jsonify({"error": "Client name cannot be empty"}), 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO clients (name, age, weight, program, membership_status) VALUES (?, ?, ?, ?, ?)",
            (name, data.get("age"), data.get("weight"), data.get("program"), data.get("membership_status", "Active"))
        )
        conn.commit()
        client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
        conn.close()
        return jsonify(dict(client)), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": f"Client '{name}' already exists"}), 409


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(client)), 200


@app.route("/clients/<name>", methods=["PUT"])
def update_client(name):
    data = request.get_json()
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404

    conn.execute(
        "UPDATE clients SET age=?, weight=?, program=?, membership_status=? WHERE name=?",
        (
            data.get("age", client["age"]),
            data.get("weight", client["weight"]),
            data.get("program", client["program"]),
            data.get("membership_status", client["membership_status"]),
            name
        )
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    return jsonify(dict(updated)), 200


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    conn.execute("DELETE FROM clients WHERE name=?", (name,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Client '{name}' deleted"}), 200


# ---------- WORKOUTS ----------
@app.route("/workouts/<client_name>", methods=["GET"])
def get_workouts(client_name):
    conn = get_db()
    workouts = conn.execute(
        "SELECT * FROM workouts WHERE client_name=? ORDER BY date DESC", (client_name,)
    ).fetchall()
    conn.close()
    return jsonify([dict(w) for w in workouts]), 200


@app.route("/workouts", methods=["POST"])
def add_workout():
    data = request.get_json()
    if not data or not data.get("client_name"):
        return jsonify({"error": "client_name is required"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)",
        (
            data["client_name"],
            data.get("date", date.today().isoformat()),
            data.get("workout_type"),
            data.get("duration_min"),
            data.get("notes", "")
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Workout added"}), 201


# ---------- PROGRESS ----------
@app.route("/progress/<client_name>", methods=["GET"])
def get_progress(client_name):
    conn = get_db()
    progress = conn.execute(
        "SELECT * FROM progress WHERE client_name=? ORDER BY id", (client_name,)
    ).fetchall()
    conn.close()
    return jsonify([dict(p) for p in progress]), 200


@app.route("/progress", methods=["POST"])
def add_progress():
    data = request.get_json()
    if not data or not data.get("client_name"):
        return jsonify({"error": "client_name is required"}), 400

    adherence = data.get("adherence", 0)
    if not (0 <= adherence <= 100):
        return jsonify({"error": "Adherence must be between 0 and 100"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
        (data["client_name"], data.get("week"), adherence)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Progress logged"}), 201


# ---------- MEMBERSHIP ----------
@app.route("/membership/<client_name>", methods=["GET"])
def check_membership(client_name):
    conn = get_db()
    client = conn.execute(
        "SELECT name, membership_status FROM clients WHERE name=?", (client_name,)
    ).fetchone()
    conn.close()
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(client)), 200


# ---------- PROGRAM GENERATOR ----------
PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"]
}


@app.route("/generate-program", methods=["POST"])
def generate_program():
    data = request.get_json()
    goal = data.get("goal", "Beginner") if data else "Beginner"
    if goal not in PROGRAM_TEMPLATES:
        return jsonify({"error": f"Unknown goal. Choose from: {list(PROGRAM_TEMPLATES.keys())}"}), 400

    programs = PROGRAM_TEMPLATES[goal]
    return jsonify({
        "goal": goal,
        "recommended_programs": programs,
        "primary_recommendation": programs[0]
    }), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
