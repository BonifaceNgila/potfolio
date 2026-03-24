import json
from datetime import datetime, timezone

from db.connection import get_db
from utils.defaults import default_cv_data


def fetch_versions(profile_id: int) -> list[dict]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, version_name, updated_at
            FROM cv_versions
            WHERE profile_id = ?
            ORDER BY datetime(updated_at) DESC, id DESC
            """,
            (profile_id,),
        )
        rows = cur.fetchall()
    return [{"id": r[0], "version_name": r[1], "updated_at": r[2]} for r in rows]


def fetch_version(version_id: int) -> dict:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, version_name, cv_json FROM cv_versions WHERE id = ?", (version_id,))
        row = cur.fetchone()
    if not row:
        return {"id": None, "version_name": "", "cv": default_cv_data()}
    return {
        "id": row[0],
        "version_name": row[1],
        "cv": json.loads(row[2]),
    }


def fetch_default_version() -> dict | None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT v.id, v.version_name, v.cv_json
            FROM cv_versions v
            JOIN profiles p ON p.id = v.profile_id
            WHERE p.is_default = 1
            ORDER BY datetime(v.updated_at) DESC, v.id DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "version_name": row[1],
        "cv": json.loads(row[2]),
    }


def save_version(version_id: int, version_name: str, cv_data: dict) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE cv_versions
            SET version_name = ?, cv_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (version_name.strip(), json.dumps(cv_data), now, version_id),
        )
        conn.commit()


def create_new_version(profile_id: int, version_name: str, cv_data: dict) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO cv_versions(profile_id, version_name, cv_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (profile_id, version_name.strip(), json.dumps(cv_data), now, now),
        )
        conn.commit()


def delete_version(version_id: int) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM cv_versions WHERE id = ?", (version_id,))
        conn.commit()
