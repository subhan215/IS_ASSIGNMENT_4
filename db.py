# db.py
import sqlite3
from contextlib import contextmanager

DB_PATH = "hospital.db"

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

# Users
def fetch_users():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, password_hash, role FROM users")
        return [dict(r) for r in cur.fetchall()]

def get_user_by_username(username):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, password_hash, role FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return dict(row) if row else None

# Patients
def add_patient(name, contact, diagnosis, date_added):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO patients (name, contact, diagnosis, date_added)
            VALUES (?, ?, ?, ?)
        """, (name, contact, diagnosis, date_added))
        return cur.lastrowid

def update_patient(patient_id, **fields):
    if not fields:
        return
    with get_conn() as conn:
        cur = conn.cursor()
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        params = list(fields.values()) + [patient_id]
        cur.execute(f"UPDATE patients SET {set_clause} WHERE patient_id = ?", params)

def fetch_patients(raw=False):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients ORDER BY patient_id")
        rows = [dict(r) for r in cur.fetchall()]
        return rows

# Logs
def add_log(user_id, username, role, action, details=""):
    from datetime import datetime
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO logs (user_id, username, role, action, timestamp, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, role, action, datetime.utcnow().isoformat(), details))

def fetch_logs(limit=500):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM logs ORDER BY log_id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]

# Consent Management
def check_consent(user_id):
    """Check if user has already given GDPR consent."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT consent_given FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return bool(row['consent_given']) if row else False

def set_consent(user_id, username, role, consent=True):
    """Set GDPR consent status for user and log the action."""
    from datetime import datetime
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET consent_given = ?, consent_date = ? WHERE user_id = ?",
            (1 if consent else 0, datetime.utcnow().isoformat() if consent else None, user_id)
        )
    # Log the action
    add_log(user_id, username, role, "consent_given" if consent else "consent_declined", 
            f"User {'accepted' if consent else 'declined'} GDPR consent")
