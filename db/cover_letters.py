import json
from datetime import datetime, timezone

from db.connection import get_db


def fetch_cover_letter_versions(profile_id: int) -> list[dict]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, version_name, updated_at
            FROM cover_letter_versions
            WHERE profile_id = ?
            ORDER BY datetime(updated_at) DESC, id DESC
            """,
            (profile_id,),
        )
        rows = cur.fetchall()
    return [{"id": r[0], "version_name": r[1], "updated_at": r[2]} for r in rows]


def fetch_cover_letter_version(version_id: int) -> dict | None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, version_name, letter_json FROM cover_letter_versions WHERE id = ?",
            (version_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "version_name": row[1],
        "letter": json.loads(row[2]),
    }


def save_cover_letter_version(version_id: int, version_name: str, letter_data: dict) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE cover_letter_versions
            SET version_name = ?, letter_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (version_name.strip(), json.dumps(letter_data), now, version_id),
        )
        conn.commit()


def create_cover_letter_version(profile_id: int, version_name: str, letter_data: dict) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO cover_letter_versions(profile_id, version_name, letter_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (profile_id, version_name.strip(), json.dumps(letter_data), now, now),
        )
        conn.commit()


def delete_cover_letter_version(version_id: int) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM cover_letter_versions WHERE id = ?", (version_id,))
        conn.commit()
