# db_setup.py
import sqlite3
from datetime import datetime
import os
import hashlib

DB_PATH = "hospital.db"

def hash_password(password: str, salt: str = "static_salt_for_demo") -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()

def ensure_db():
    need_seed = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        consent_given INTEGER DEFAULT 0,
        consent_date TEXT DEFAULT NULL
    );
    """)

    # patients table
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        diagnosis TEXT,
        anonymized_name TEXT,
        anonymized_contact TEXT,
        encrypted_name TEXT,
        encrypted_contact TEXT,
        date_added TEXT
    );
    """)

    # logs table
    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        role TEXT,
        action TEXT,
        timestamp TEXT,
        details TEXT
    );
    """)

    conn.commit()

    # Migration: Add consent columns if they don't exist
    try:
        c.execute("ALTER TABLE users ADD COLUMN consent_given INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN consent_date TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()

    # seed default users only if fresh DB
    if need_seed:
        users = [
            ("admin", "admin123", "admin"),
            ("drbob", "doc123", "doctor"),
            ("alice_recep", "rec123", "receptionist"),
        ]
        for uname, pwd, role in users:
            try:
                c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                          (uname, hash_password(pwd) , role))
            except sqlite3.IntegrityError:
                pass

        # seed patients
        patients = [
            ("John Doe", "0300-555-1234", "Flu", "", "", "", "", datetime.utcnow().isoformat()),
            ("Jane Smith", "0300-999-4592", "Fracture", "", "", "", "", datetime.utcnow().isoformat()),
        ]
        for p in patients:
            c.execute("""
            INSERT INTO patients (name, contact, diagnosis, anonymized_name, anonymized_contact, encrypted_name, encrypted_contact, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, p)

        conn.commit()
        print("Seeded database with sample users and patients.")

    conn.close()
    print(f"Database file: {DB_PATH} created/updated.")

if __name__ == "__main__":
    ensure_db()
