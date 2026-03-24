import json
from datetime import datetime, timezone

from db.connection import get_db
from utils.defaults import default_cv_data


def fetch_profiles() -> list[dict]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, is_default FROM profiles ORDER BY id")
        rows = cur.fetchall()
    return [{"id": r[0], "name": r[1], "is_default": bool(r[2])} for r in rows]


def set_default_profile(profile_id: int) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE profiles SET is_default = 0")
        cur.execute("UPDATE profiles SET is_default = 1 WHERE id = ?", (profile_id,))
        conn.commit()


def create_profile(profile_name: str, base_cv: dict) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO profiles(name, is_default, created_at) VALUES (?, 0, ?)",
            (profile_name.strip(), now),
        )
        profile_id = cur.lastrowid
        cur.execute(
            """
            INSERT INTO cv_versions(profile_id, version_name, cv_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (profile_id, "Default v1", json.dumps(base_cv), now, now),
        )
        conn.commit()
    return profile_id


def delete_profile(profile_id: int) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM cv_versions WHERE profile_id = ?", (profile_id,))
        cur.execute("DELETE FROM cover_letter_versions WHERE profile_id = ?", (profile_id,))
        cur.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        conn.commit()


def rename_profile(profile_id: int, new_name: str) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE profiles SET name = ? WHERE id = ?",
            (new_name.strip(), profile_id),
        )
        conn.commit()
