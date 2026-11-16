from pathlib import Path
import sqlite3

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "systeme_chargement.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    with connect() as conn:
        # جدول المستخدمين
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'operator')),
                active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول العربات (Wagons)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wagons (
                wagon_id INTEGER PRIMARY KEY,
                status TEXT NOT NULL CHECK (status IN ('Vide', 'Coulage', 'Emaillage')),
                last_update TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # سجل عمليات الصب (Coulage Logs)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS coulage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wagon_id INTEGER NOT NULL,
                date_coulage TEXT NOT NULL,
                operator_id INTEGER NOT NULL,
                status_start TEXT DEFAULT 'Coulage',
                timestamp_entry TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (wagon_id) REFERENCES wagons (wagon_id),
                FOREIGN KEY (operator_id) REFERENCES users (id)
            )
        """)
        conn.commit()

# --- وظائف المستخدمين (كما هي) ---
def has_admin():
    with connect() as conn:
        row = conn.execute("SELECT 1 FROM users WHERE role = 'admin' LIMIT 1").fetchone()
        return row is not None

def create_user(username, password_hash, role="admin"):
    with connect() as conn:
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                     (username.strip(), password_hash, role))
        conn.commit()

def get_user(username):
    with connect() as conn:
        return conn.execute("SELECT id, username, password_hash, role, active FROM users WHERE username = ? COLLATE NOCASE",
                            (username.strip(),)).fetchone()

def update_password(user_id, password_hash):
    with connect() as conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
        conn.commit()

# --- وظائف العمليات (جديد المرحلة الثانية) ---
def register_coulage(wagon_id, date_coulage, operator_id):
    with connect() as conn:
        # 1. التحقق هل العربة مشغولة فعلاً؟
        wagon = conn.execute("SELECT status FROM wagons WHERE wagon_id = ?", (wagon_id,)).fetchone()
        if wagon and wagon['status'] != 'Vide':
            raise Exception(f"L'wagon {wagon_id} n'est pas Vide (Statut actuel: {wagon['status']})")
        
        # 2. تحديث حالة العربة إلى Coulage
        conn.execute("INSERT OR REPLACE INTO wagons (wagon_id, status, last_update) VALUES (?, 'Coulage', CURRENT_TIMESTAMP)", 
                     (wagon_id,))
        
        # 3. تسجيل العملية في السجل
        conn.execute("INSERT INTO coulage_logs (wagon_id, date_coulage, operator_id) VALUES (?, ?, ?)",
                     (wagon_id, date_coulage, operator_id))
        conn.commit()
