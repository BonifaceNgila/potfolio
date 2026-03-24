import re


def normalize_project_record(item) -> dict:
    if isinstance(item, dict):
        return item
    if isinstance(item, str):
        return {"name": item, "description": "", "technologies": "", "link": ""}
    return {"name": "", "description": "", "technologies": "", "link": ""}


def normalize_education_record(item) -> dict:
    if isinstance(item, dict):
        return item
    if isinstance(item, str):
        return {"course": item, "institution": "", "timeline": ""}
    return {"course": "", "institution": "", "timeline": ""}


def text_to_list(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def list_to_text(items: list[str]) -> str:
    return "\n".join(items)


def projects_to_text(projects: list) -> str:
    lines = []
    for item in projects:
        record = normalize_project_record(item)
        parts = [
            record.get("name", ""),
            record.get("description", ""),
            record.get("technologies", ""),
            record.get("link", ""),
        ]
        lines.append(" || ".join(parts))
    return "\n".join(lines)


def text_to_projects(raw: str) -> list[dict]:
    records: list[dict] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("||")]
        records.append(
            {
                "name": parts[0] if len(parts) > 0 else "",
                "description": parts[1] if len(parts) > 1 else "",
                "technologies": parts[2] if len(parts) > 2 else "",
                "link": parts[3] if len(parts) > 3 else "",
            }
        )
    return records


def experience_to_text(experience: list[dict]) -> str:
    blocks = []
    for item in experience:
        header = f"{item.get('role', '')} || {item.get('organization', '')} || {item.get('period', '')}".strip()
        bullets = [f"- {bullet}" for bullet in item.get("bullets", []) if str(bullet).strip()]
        blocks.append("\n".join([header] + bullets))
    return "\n\n".join(blocks)


def text_to_experience(raw: str) -> list[dict]:
    entries: list[dict] = []
    blocks = [block.strip() for block in re.split(r"\n\s*\n", raw.strip()) if block.strip()]
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        header_parts = [p.strip() for p in lines[0].split("||")]
        role = header_parts[0] if len(header_parts) > 0 else ""
        organization = header_parts[1] if len(header_parts) > 1 else ""
        period = header_parts[2] if len(header_parts) > 2 else ""
        bullets = [line.lstrip("- ").strip() for line in lines[1:] if line.lstrip("- ").strip()]
        entries.append(
            {
                "role": role,
                "organization": organization,
                "period": period,
                "bullets": bullets,
            }
        )
    return entries


def education_to_text(education: list[dict]) -> str:
    lines = []
    for item in education:
        record = normalize_education_record(item)
        parts = [
            record.get("course", ""),
            record.get("institution", ""),
            record.get("timeline", ""),
        ]
        lines.append(" || ".join(parts))
    return "\n".join(lines)


def text_to_education(raw: str) -> list[dict]:
    records: list[dict] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("||")]
        records.append(
            {
                "course": parts[0] if len(parts) > 0 else "",
                "institution": parts[1] if len(parts) > 1 else "",
                "timeline": parts[2] if len(parts) > 2 else "",
            }
        )
    return records


def referees_to_text(referees: list[dict]) -> str:
    lines = []
    for ref in referees:
        lines.append(
            " || ".join(
                [
                    ref.get("name", ""),
                    ref.get("organization", ""),
                    ref.get("position", ""),
                    ref.get("email", ""),
                    ref.get("phone", ""),
                ]
            )
        )
    return "\n".join(lines)


def text_to_referees(raw: str) -> list[dict]:
    refs: list[dict] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("||")]
        refs.append(
            {
                "name": parts[0] if len(parts) > 0 else "",
                "organization": parts[1] if len(parts) > 1 else "",
                "position": parts[2] if len(parts) > 2 else "",
                "email": parts[3] if len(parts) > 3 else "",
                "phone": parts[4] if len(parts) > 4 else "",
            }
        )
    return refs
