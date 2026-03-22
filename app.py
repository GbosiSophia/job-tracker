import sqlite3
from flask import Flask, render_template
from flask import request, redirect, url_for
import json

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        job TEXT,
        status TEXT,
        date_applied TEXT,
        notes TEXT
    )
    """)

    conn.commit()
    conn.close()



@app.route("/")
def home():
    search = request.args.get("search", "")
    status = request.args.get("status", "")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    query = "SELECT * FROM applications WHERE 1=1"
    params = []

    if search:
        query += " AND (company LIKE ? OR job LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
    if status:
        query += " AND status = ?"
        params.append(status)

    cursor.execute(query, params)
    applications = cursor.fetchall()

# Analytics & chart
    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE status='Interview'")
    interviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE status='Offer'")
    offers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]

    labels = ["Applied", "Interview", "Offer", "Rejected"]
    values = []

    for label in labels:
        cursor.execute("SELECT COUNT(*) FROM applications WHERE status=?", (label,))
        values.append(cursor.fetchone()[0])

    chart_data = {
        "labels": labels,
        "values": values
    }

    #To calculate success rate
    if total > 0:
        success_rate = (offers / total) * 100
    else:
        success_rate = 0

    success_rate=round(success_rate, 1)
    conn.close()

    return render_template("index.html",
                           applications=applications,
                           total=total,
                           interviews=interviews,
                           offers=offers,
                           rejected=rejected,
                           success_rate=success_rate,
                           chart_data=json.dumps(chart_data)
                           )

@app.route("/add", methods=["POST"])
def add_application():
    company = request.form["company"]
    job = request.form["job"]
    status = request.form["status"]
    date_applied = request.form["date_applied"]
    notes = request.form["notes"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO applications (company, job, status, date_applied, notes)
    VALUES (?, ?, ?, ?, ?)
    """, (company, job, status, date_applied, notes))
# This VALUES (?, ?, ?, ?, ?) prevents SQL injection
    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route("/delete/<int:id>")
def delete_application(id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM applications WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

#Function to edit
@app.route("/edit/<int:id>")
def edit_application(id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applications WHERE id = ?", (id,))
    application = cursor.fetchone()

    conn.close()

    return render_template("edit.html", app=application)

@app.route("/update/<int:id>", methods=["POST"])
def update_application(id):
    company = request.form["company"]
    job = request.form["job"]
    status = request.form["status"]
    date_applied = request.form["date_applied"]
    notes = request.form["notes"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE applications
    SET company = ?, job = ?, status = ?, date_applied = ?, notes = ?
    WHERE id = ?
    """, (company, job, status, date_applied, notes, id))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db() #database gets created first
    app.run(host="0.0.0.0", port=10000)