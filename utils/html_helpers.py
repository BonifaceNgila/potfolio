import html

from utils.converters import normalize_education_record, normalize_project_record


def html_list(items: list[str]) -> str:
    escaped = [f"<li>{html.escape(item)}</li>" for item in items if str(item).strip()]
    return f"<ul>{''.join(escaped)}</ul>" if escaped else ""


def html_experience(experience: list[dict]) -> str:
    chunks = []
    for item in experience:
        role = html.escape(item.get("role", ""))
        org = html.escape(item.get("organization", ""))
        period = html.escape(item.get("period", ""))
        bullets = html_list(item.get("bullets", []))
        chunks.append(
            f"""
            <div class="job">
                <div class="experience-header">
                    <h4>{role}</h4>
                    <span class="experience-period">{period}</span>
                </div>
                <div class="experience-org">{org}</div>
                {bullets}
            </div>
            """
        )
    return "".join(chunks)


def html_education(education: list[dict]) -> str:
    entries = []
    for idx, item in enumerate(education, start=1):
        record = normalize_education_record(item)
        course = html.escape(record.get("course", ""))
        institution = html.escape(record.get("institution", ""))
        timeline = html.escape(record.get("timeline", ""))
        if not any([course, institution, timeline]):
            continue
        entries.append(
            f"""
            <div class="education-entry">
                <div class="education-top">
                    <span class="education-course">{idx}. {course}</span>
                    <span class="education-timeline">{timeline}</span>
                </div>
                <div class="education-institution">
                    {institution}
                </div>
            </div>
            """
        )
    return "".join(entries)


def html_referees(referees: list[dict]) -> str:
    entries = []
    for ref in referees:
        name = html.escape(ref.get("name", ""))
        organization = html.escape(ref.get("organization", "") or "")
        position = html.escape(ref.get("position", "") or ref.get("title", ""))
        email = html.escape(ref.get("email", ""))
        phone = html.escape(ref.get("phone", ""))
        meta_parts = []
        if position:
            meta_parts.append(f"<span class='referee-field'>{position}</span>")
        if email:
            meta_parts.append(f"<span class='referee-field'>{email}</span>")
        if phone:
            meta_parts.append(f"<span class='referee-field'>{phone}</span>")
        meta_html = "".join(meta_parts)
        entries.append(
            f"""
            <li class='referee'>
                <div class='referee-head'>
                    <span class='referee-name'>{name}</span>
                    <span class='referee-org'>{organization}</span>
                </div>
                <div class='referee-meta'>
                    {meta_html}
                </div>
            </li>
            """
        )
    if not entries:
        return ""
    return f"<ul class='referees-list'>{''.join(entries)}</ul>"


def html_projects(projects: list) -> str:
    entries = []
    for item in projects:
        record = normalize_project_record(item)
        name = html.escape(record.get("name", ""))
        description = html.escape(record.get("description", ""))
        technologies = html.escape(record.get("technologies", ""))
        link = record.get("link", "").strip()
        if not any([name, description]):
            continue
        link_html = (
            f"<a href='{html.escape(link)}' target='_blank'>{html.escape(link)}</a>"
            if link else ""
        )
        tech_html = f"<div class='project-tech'>{technologies}</div>" if technologies else ""
        entries.append(
            f"""<div class='project-entry'>
                <h4>{name}</h4>
                <p>{description}</p>
                {tech_html}
                {link_html}
            </div>"""
        )
    return "".join(entries)


def section_header(title: str) -> str:
    if not title:
        return ""
    return (
        "<div class='section-heading'>"
        f"<h2>{html.escape(title)}</h2>"
        "</div>"
    )
