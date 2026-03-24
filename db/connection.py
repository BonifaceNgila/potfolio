import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone

from utils.defaults import default_cv_data


def resolve_db_path() -> str:
    explicit_path = os.getenv("CV_DB_PATH", "").strip()
    if explicit_path:
        parent_dir = os.path.dirname(explicit_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        return explicit_path

    default_path = os.path.join(os.getcwd(), "cv_portfolio.db")
    try:
        with open(default_path, "a", encoding="utf-8"):
            pass
        return default_path
    except OSError:
        return os.path.join(tempfile.gettempdir(), "cv_portfolio.db")


DB_PATH = resolve_db_path()


def get_conn() -> sqlite3.Connection:
    parent_dir = os.path.dirname(DB_PATH)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    return sqlite3.connect(DB_PATH)


@contextmanager
def get_db():
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()


def _ensure_column(cur: sqlite3.Cursor, table: str, column: str, definition: str) -> None:
    # table/column/definition are always hardcoded internal literals — not user input
    cur.execute(f"PRAGMA table_info({table})")
    existing_columns = {row[1] for row in cur.fetchall()}
    if column not in existing_columns:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db() -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                is_default INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cv_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                version_name TEXT NOT NULL,
                cv_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (profile_id) REFERENCES profiles(id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cover_letter_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                version_name TEXT NOT NULL,
                letter_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (profile_id) REFERENCES profiles(id)
            )
            """
        )

        _ensure_column(cur, "profiles", "is_default", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(cur, "profiles", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(cur, "cv_versions", "version_name", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(cur, "cv_versions", "cv_json", "TEXT NOT NULL DEFAULT '{}' ")
        _ensure_column(cur, "cv_versions", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(cur, "cv_versions", "updated_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(cur, "cover_letter_versions", "version_name", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(cur, "cover_letter_versions", "letter_json", "TEXT NOT NULL DEFAULT '{}' ")
        _ensure_column(cur, "cover_letter_versions", "created_at", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(cur, "cover_letter_versions", "updated_at", "TEXT NOT NULL DEFAULT ''")

        now = datetime.now(timezone.utc).isoformat()
        cur.execute("UPDATE profiles SET created_at = ? WHERE created_at IS NULL OR created_at = ''", (now,))
        cur.execute("UPDATE cv_versions SET created_at = ? WHERE created_at IS NULL OR created_at = ''", (now,))
        cur.execute("UPDATE cv_versions SET updated_at = created_at WHERE updated_at IS NULL OR updated_at = ''")
        cur.execute("UPDATE cover_letter_versions SET created_at = ? WHERE created_at IS NULL OR created_at = ''", (now,))
        cur.execute("UPDATE cover_letter_versions SET updated_at = created_at WHERE updated_at IS NULL OR updated_at = ''")

        cur.execute("SELECT COUNT(*) FROM profiles")
        profile_count = cur.fetchone()[0]
        if profile_count == 0:
            cur.execute(
                "INSERT INTO profiles(name, is_default, created_at) VALUES (?, ?, ?)",
                ("Boniface Main Profile", 1, now),
            )
            profile_id = cur.lastrowid
            cur.execute(
                """
                INSERT INTO cv_versions(profile_id, version_name, cv_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (profile_id, "Default v1", json.dumps(default_cv_data()), now, now),
            )

        conn.commit()
