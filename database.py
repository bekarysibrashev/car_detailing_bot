import sqlite3
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id       INTEGER UNIQUE NOT NULL,
                username    TEXT,
                name        TEXT,
                created_at  TEXT DEFAULT (datetime('now')),
                last_seen   TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS requests (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id       INTEGER NOT NULL,
                color       TEXT,
                coating     TEXT,
                input_path  TEXT,
                output_url  TEXT,
                status      TEXT DEFAULT 'pending',
                created_at  TEXT DEFAULT (datetime('now'))
            );
        """)
    logger.info("DB ready")

def upsert_user(tg_id, username, name):
    with conn() as c:
        c.execute("""
            INSERT INTO users (tg_id, username, name)
            VALUES (?,?,?)
            ON CONFLICT(tg_id) DO UPDATE SET
                username=excluded.username,
                name=excluded.name,
                last_seen=datetime('now')
        """, (tg_id, username, name))

def save_request(tg_id, color, coating, input_path) -> int:
    with conn() as c:
        cur = c.execute(
            "INSERT INTO requests (tg_id,color,coating,input_path,status) VALUES (?,?,?,?,'processing')",
            (tg_id, color, coating, input_path)
        )
        return cur.lastrowid

def finish_request(req_id, output_url, status='done'):
    with conn() as c:
        c.execute(
            "UPDATE requests SET output_url=?, status=? WHERE id=?",
            (output_url, status, req_id)
        )

def get_stats():
    with conn() as c:
        users    = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        requests = c.execute("SELECT COUNT(*) FROM requests WHERE status='done'").fetchone()[0]
        top_colors = c.execute("""
            SELECT color, COUNT(*) n FROM requests
            WHERE status='done' GROUP BY color ORDER BY n DESC LIMIT 5
        """).fetchall()
        top_coatings = c.execute("""
            SELECT coating, COUNT(*) n FROM requests
            WHERE status='done' GROUP BY coating ORDER BY n DESC LIMIT 3
        """).fetchall()
    return {
        "users": users, "requests": requests,
        "top_colors":   [(r["color"],   r["n"]) for r in top_colors],
        "top_coatings": [(r["coating"], r["n"]) for r in top_coatings],
    }