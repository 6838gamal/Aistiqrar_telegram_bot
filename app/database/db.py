import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = "app/data/bot.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    Path("app/data").mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id             INTEGER PRIMARY KEY,
            name                TEXT,
            username            TEXT,
            lang                TEXT DEFAULT 'ar',
            sessions            INTEGER DEFAULT 0,
            referred_by         INTEGER,
            referral_count      INTEGER DEFAULT 0,
            join_type           TEXT DEFAULT 'direct',
            joined_at           TEXT,
            selected_categories TEXT DEFAULT ''
        )
    """)
    try:
        conn.execute("ALTER TABLE users ADD COLUMN selected_categories TEXT DEFAULT ''")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE users ADD COLUMN feed_started_at TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()

def upsert_user(user_id, name, username, lang="ar", referred_by=None):
    conn = get_conn()
    existing = conn.execute(
        "SELECT user_id FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()

    if not existing:
        join_type = "referral" if referred_by else "direct"
        conn.execute("""
            INSERT INTO users (user_id, name, username, lang, referred_by, join_type, joined_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, username, lang, referred_by, join_type, datetime.now().isoformat()))

        if referred_by:
            conn.execute("""
                UPDATE users SET referral_count = referral_count + 1
                WHERE user_id = ?
            """, (referred_by,))

    conn.commit()
    conn.close()

def update_user_lang(user_id, lang):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id)
    )
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"lang": "ar", "sessions": 0, "name": "", "username": ""}

def get_all_users():
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            u.user_id,
            u.name,
            u.username,
            u.lang,
            u.sessions,
            u.join_type,
            u.referral_count,
            u.joined_at,
            r.name AS referred_by_name
        FROM users u
        LEFT JOIN users r ON u.referred_by = r.user_id
        ORDER BY u.joined_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_selected_categories(user_id) -> list:
    conn = get_conn()
    row = conn.execute(
        "SELECT selected_categories FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if row and row["selected_categories"]:
        return [int(x) for x in row["selected_categories"].split(",") if x.strip().isdigit()]
    return []

def update_selected_categories(user_id, selected: list):
    value = ",".join(str(i) for i in sorted(selected))
    conn = get_conn()
    conn.execute("""
        INSERT INTO users (user_id, selected_categories)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET selected_categories = excluded.selected_categories
    """, (user_id, value))
    conn.commit()
    conn.close()

def get_feed_started_at(user_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT feed_started_at FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if row:
        return row["feed_started_at"]
    return None

def set_feed_started_at(user_id):
    conn = get_conn()
    conn.execute("""
        INSERT INTO users (user_id, feed_started_at) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET feed_started_at = excluded.feed_started_at
    """, (user_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def init_favorites_table():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL,
            title     TEXT,
            link      TEXT,
            saved_at  TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_favorite(user_id: int, title: str, link: str) -> bool:
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM favorites WHERE user_id = ? AND link = ?", (user_id, link)
    ).fetchone()
    if existing:
        conn.close()
        return False
    conn.execute(
        "INSERT INTO favorites (user_id, title, link, saved_at) VALUES (?, ?, ?, ?)",
        (user_id, title, link, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return True

def get_favorites(user_id: int) -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT title, link, saved_at FROM favorites WHERE user_id = ? ORDER BY saved_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats():
    conn = get_conn()
    total    = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    direct   = conn.execute("SELECT COUNT(*) FROM users WHERE join_type = 'direct'").fetchone()[0]
    referral = conn.execute("SELECT COUNT(*) FROM users WHERE join_type = 'referral'").fetchone()[0]
    conn.close()
    return {"total": total, "direct": direct, "referral": referral}
