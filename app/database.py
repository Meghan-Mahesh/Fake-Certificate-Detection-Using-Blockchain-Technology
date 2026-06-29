import sqlite3
from werkzeug.security import generate_password_hash
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "..", "database", "certchain.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # ---------------------------
    # ADMIN TABLE (Single Admin)
    # ---------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        email TEXT PRIMARY KEY,
        passwordHash TEXT NOT NULL
    )
    """)

    #  Check if admin already exists
    cursor.execute("SELECT * FROM admin WHERE email = ?", ("admin@gmail.com",))
    admin = cursor.fetchone()

    if not admin:
        email = "admin@gmail.com"
        password = generate_password_hash("admin123")

        cursor.execute("""
        INSERT INTO admin (email, passwordHash)
        VALUES (?, ?)
        """, (email, password))

    # ---------------------------
    # ISSUER TABLE
    # ---------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issuer (
        issuerId TEXT PRIMARY KEY,
        organizationName TEXT NOT NULL,
        organizationType TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        passwordHash TEXT NOT NULL,
        blockchainAddress TEXT,
        approvalStatus TEXT NOT NULL DEFAULT 'PENDING'
            CHECK (approvalStatus IN ('PENDING', 'APPROVED', 'REJECTED')),
        registrationDate DATE NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn