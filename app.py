import html
import hmac
import json
import os
import re
import sqlite3
import tempfile
from datetime import datetime
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfgen import canvas

    REPORTLAB_AVAILABLE = True
except ModuleNotFoundError:
    colors = None
    A4 = None
    pdfmetrics = None
    canvas = None
    REPORTLAB_AVAILABLE = False


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


AVAILABLE_TEMPLATES = [
    "One Column - Classic",
    "One Column - Minimal",
    "Two Column - Professional",
    "Two Column - Sidebar",
    "Two Column - Sidebar Skillset",
    "Two Column - Accent Panel",
    "Two Column - Slate Profile",
]


def default_cv_data() -> dict:
    return {
        "full_name": "BONIFACE MUTISYA NGILA",
        "headline": "IT Officer | IAM | IT Operations | Security",
        "location": "Kilifi, Kenya",
        "phone": "+254792950816",
        "email": "mutisyaboniface@outlook.com",
        "linkedin": "https://www.linkedin.com/in/boniface-ngila",
        "github": "https://github.com/BonifaceNgila",
        "profile_summary": (
            "Highly skilled IT professional with expertise in IT system administration, network "
            "administration, IT security, and Identity & Access Management (IAM). Proven track "
            "record in managing IT infrastructure, optimizing services, and ensuring continuous "
            "operations within global NGO environments. Experienced in user identity lifecycle "
            "management, Active Directory, Azure/Entra ID concepts, and Microsoft 365 "
            "administration. Committed to delivering exceptional IT support and driving "
            "organizational success through secure, innovative technology solutions."
        ),
        "core_competencies": [
            "Identity & Access Management (IAM): User Identity Lifecycle, SSO, MFA, Conditional Access, Global Active Directory, OKTA, OCI IAM Administration",
            "Cloud & Workplace Tech: Azure AD / Entra ID, Microsoft 365, Exchange Online, OneDrive, Oracle Cloud, AWS",
            "IT Operations & Security: ITIL Principles, Incident Management, Endpoint Security, Troubleshooting, PowerShell (and Bash/Python), SOP Documentation",
            "Service Delivery & Operations: ServiceNow, incident management, documentation",
            "Technical Support: Windows & macOS support, hardware/software troubleshooting, Microsoft 365",
            "Active Directory & Azure AD Management: User accounts, groups, and permissions",
            "Network Fundamentals: TCP/IP, DNS, DHCP, VPN",
            "Customer Service & Communication: Strong verbal and written skills, ability to manage user expectations",
        ],
        "experience": [
            {
                "role": "IT OFFICER",
                "organization": "Plan International Kenya, Coastal Hub",
                "period": "March 2024 – December 2025",
                "bullets": [
                    "Managed IT infrastructure, servers, and networks to ensure high availability, security, and performance through continuous monitoring and disaster recovery planning.",
                    "Configured user access, virtualized environments, and server applications, ensuring strict compliance with organizational security standards and IAM governance.",
                    "Provided first- to mid-level helpdesk support, troubleshot complex access issues, and conducted staff training to promote IT best practices and secure authentication.",
                    "Maintained accurate documentation and prepared regular IT performance reports.",
                    "Facilitated service delivery by managing ServiceNow tickets and documentation of incidents and procedures.",
                ],
            },
            {
                "role": "IT ASSISTANT",
                "organization": "Plan International Kenya, Coastal Hub",
                "period": "November 2022 – February 2024",
                "bullets": [
                    "Executed user identity lifecycle activities by configuring user accounts and permissions.",
                    "Collaborated on global directory services and email groups to ensure seamless SSO integrations.",
                    "Delivered Tier 1 support for desktop, network, and infrastructure issues.",
                    "Supported Microsoft 365 applications and VPN connectivity.",
                ],
            },
            {
                "role": "IT SUPPORT INTERN",
                "organization": "Plan International Kenya, Coastal Hub",
                "period": "November 2021 – November 2022",
                "bullets": [
                    "Managed Global Active Directory and OKTA services, troubleshooting authentication errors.",
                    "Supported Exchange Online, SAP, and Office 365 operations to minimize downtime.",
                    "Assisted with Active Directory and Azure AD provisioning and permissions management.",
                ],
            },
        ],
        "education": [
            "Master of Science in Computer Science, UNICAF University (Ongoing)",
            "Coursework includes Cryptography and Networking Security",
            "Bachelor of Business Information Technology, Taita Taveta University (November 2019)",
        ],
        "certifications": [
            "Google IT Support Professional Certification",
            "Oracle Cloud Infrastructure 2025 Certified DevOps Professional",
            "Oracle Cloud Infrastructure 2025 Certified Architect Associate",
            "CIPIT's Data Protection Course, Strathmore University",
        ],
        "languages": ["English (Fluent)", "Swahili (Native)"],
        "referees": [
            {
                "name": "Winfred Mukonza",
                "title": "Country Sponsorship Manager, Plan International Kenya",
                "email": "winfred.mukonza@plan-international.org",
                "phone": "+254713267985",
            },
            {
                "name": "Eston Nyaga",
                "title": "Program Area Manager, Plan International Kenya, Coast Hub",
                "email": "eston.nyaga@plan-international.org",
                "phone": "+254722912493",
            },
            {
                "name": "Cynthia Akoth",
                "title": "IT Coordinator, Plan International Kenya",
                "email": "cynthia.akoth@plan-international.org",
                "phone": "+254707870390",
            },
            {
                "name": "Sharon Meliyio",
                "title": "Country IT Manager, Plan International Kenya",
                "email": "sharon.meliyio@plan-international.org",
                "phone": "+254724917720",
            },
        ],
    }


def get_conn() -> sqlite3.Connection:
    parent_dir = os.path.dirname(DB_PATH)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def ensure_column(cur: sqlite3.Cursor, table: str, column: str, definition: str) -> None:
    cur.execute(f"PRAGMA table_info({table})")
    existing_columns = {row[1] for row in cur.fetchall()}
    if column not in existing_columns:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db() -> None:
    conn = get_conn()
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

    ensure_column(cur, "profiles", "is_default", "INTEGER NOT NULL DEFAULT 0")
    ensure_column(cur, "profiles", "created_at", "TEXT NOT NULL DEFAULT ''")

    ensure_column(cur, "cv_versions", "version_name", "TEXT NOT NULL DEFAULT ''")
    ensure_column(cur, "cv_versions", "cv_json", "TEXT NOT NULL DEFAULT '{}' ")
    ensure_column(cur, "cv_versions", "created_at", "TEXT NOT NULL DEFAULT ''")
    ensure_column(cur, "cv_versions", "updated_at", "TEXT NOT NULL DEFAULT ''")

    now = datetime.utcnow().isoformat()
    cur.execute("UPDATE profiles SET created_at = ? WHERE created_at IS NULL OR created_at = ''", (now,))
    cur.execute("UPDATE cv_versions SET created_at = ? WHERE created_at IS NULL OR created_at = ''", (now,))
    cur.execute("UPDATE cv_versions SET updated_at = created_at WHERE updated_at IS NULL OR updated_at = ''")

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
    conn.close()


def fetch_profiles() -> list[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, is_default FROM profiles ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "is_default": bool(r[2])} for r in rows]


def set_default_profile(profile_id: int) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE profiles SET is_default = 0")
    cur.execute("UPDATE profiles SET is_default = 1 WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()


def create_profile(profile_name: str, base_cv: dict) -> int:
    now = datetime.utcnow().isoformat()
    conn = get_conn()
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
    conn.close()
    return profile_id


def fetch_versions(profile_id: int) -> list[dict]:
    conn = get_conn()
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
    conn.close()
    return [{"id": r[0], "version_name": r[1], "updated_at": r[2]} for r in rows]


def fetch_version(version_id: int) -> dict:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, version_name, cv_json FROM cv_versions WHERE id = ?", (version_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"id": None, "version_name": "", "cv": default_cv_data()}
    return {
        "id": row[0],
        "version_name": row[1],
        "cv": json.loads(row[2]),
    }


def fetch_default_version() -> dict | None:
    conn = get_conn()
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
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "version_name": row[1],
        "cv": json.loads(row[2]),
    }


def save_version(version_id: int, version_name: str, cv_data: dict) -> None:
    now = datetime.utcnow().isoformat()
    conn = get_conn()
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
    conn.close()


def create_new_version(profile_id: int, version_name: str, cv_data: dict) -> None:
    now = datetime.utcnow().isoformat()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO cv_versions(profile_id, version_name, cv_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (profile_id, version_name.strip(), json.dumps(cv_data), now, now),
    )
    conn.commit()
    conn.close()


def text_to_list(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def list_to_text(items: list[str]) -> str:
    return "\n".join(items)


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


def referees_to_text(referees: list[dict]) -> str:
    lines = []
    for ref in referees:
        lines.append(
            " || ".join(
                [
                    ref.get("name", ""),
                    ref.get("title", ""),
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
                "title": parts[1] if len(parts) > 1 else "",
                "email": parts[2] if len(parts) > 2 else "",
                "phone": parts[3] if len(parts) > 3 else "",
            }
        )
    return refs


def render_cv_streamlit(cv: dict, template: str) -> None:
    st.title(cv.get("full_name", ""))
    st.caption(cv.get("headline", ""))
    st.caption(f"Template: {template}")

    html_output = build_html(cv, template)
    components.html(html_output, height=1200, scrolling=True)


def html_list(items: list[str]) -> str:
    escaped = [f"<li>{html.escape(item)}</li>" for item in items if str(item).strip()]
    return f"<ul>{''.join(escaped)}</ul>" if escaped else ""


def html_experience(experience: list[dict]) -> str:
    chunks = []
    for item in experience:
        bullets = html_list(item.get("bullets", []))
        chunks.append(
            """
            <div class="job">
                <h4>{role}</h4>
                <p class="meta">{org} | {period}</p>
                {bullets}
            </div>
            """.format(
                role=html.escape(item.get("role", "")),
                org=html.escape(item.get("organization", "")),
                period=html.escape(item.get("period", "")),
                bullets=bullets,
            )
        )
    return "".join(chunks)


def html_referees(referees: list[dict]) -> str:
    blocks = []
    for ref in referees:
        blocks.append(
            """
            <li><strong>{name}</strong> — {title}<br>Email: {email} | Phone: {phone}</li>
            """.format(
                name=html.escape(ref.get("name", "")),
                title=html.escape(ref.get("title", "")),
                email=html.escape(ref.get("email", "")),
                phone=html.escape(ref.get("phone", "")),
            )
        )
    return f"<ul>{''.join(blocks)}</ul>"


def build_html(cv: dict, template: str) -> str:
    name = html.escape(cv.get("full_name", ""))
    headline = html.escape(cv.get("headline", ""))
    profile = html.escape(cv.get("profile_summary", ""))
    contact = (
        f"<p><strong>Location:</strong> {html.escape(cv.get('location', ''))}<br>"
        f"<strong>Phone:</strong> {html.escape(cv.get('phone', ''))}<br>"
        f"<strong>Email:</strong> {html.escape(cv.get('email', ''))}</p>"
    )
    linkedin_url = cv.get('linkedin', '').strip()
    github_url = cv.get('github', '').strip()
    link_items = []
    if linkedin_url:
        link_items.append(f"<a href='{html.escape(linkedin_url)}'>LinkedIn</a>")
    if github_url:
        link_items.append(f"<a href='{html.escape(github_url)}'>GitHub</a>")
    links = f"<p>{' | '.join(link_items)}</p>" if link_items else ""

    section_main = f"""
    <h2>Profile</h2><p>{profile}</p>
    <h2>Professional Experience</h2>{html_experience(cv.get('experience', []))}
    <h2>Education</h2>{html_list(cv.get('education', []))}
    """

    section_side = f"""
    <h2>Core Competencies</h2>{html_list(cv.get('core_competencies', []))}
    <h2>Certifications</h2>{html_list(cv.get('certifications', []))}
    <h2>Languages</h2>{html_list(cv.get('languages', []))}
    <h2>Referees</h2>{html_referees(cv.get('referees', []))}
    """

    sidebar_skills = html_list(cv.get('core_competencies', []))
    sidebar_languages = html_list(cv.get('languages', []))
    certifications_html = html_list(cv.get('certifications', []))
    referees_html = html_referees(cv.get('referees', []))

    one_column_css = """
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #eaf0f7; margin: 0; padding: 26px; color: #1f2937; }
    .cv { max-width: 940px; margin: auto; background: #ffffff; border-radius: 12px; box-shadow: 0 10px 24px rgba(30,58,95,0.14); overflow: hidden; }
    .hero { background: linear-gradient(135deg, #1e3a5f, #274c77); color: #f8fafc; padding: 26px 30px; }
    .hero h1 { margin: 0; color: #ffffff; font-size: 34px; line-height: 1.05; letter-spacing: 0.6px; }
    .hero .headline { margin: 8px 0 12px; color: #dbeafe; font-size: 15px; }
    .hero-meta { font-size: 13px; line-height: 1.5; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); border-radius: 8px; padding: 10px 12px; }
    .hero a { color: #ffffff; }
    .content { padding: 22px 24px 26px; }
    .section-block { background: #ffffff; border: 1px solid #dbe5f0; border-radius: 8px; padding: 14px 16px; margin-bottom: 14px; }
    p { line-height: 1.5; }
    h2 { color: #1e3a5f; border-bottom: 2px solid #bfdbfe; padding-bottom: 4px; margin-top: 14px; }
    .meta { color: #475569; margin-top: -4px; }
    .job { margin-bottom: 16px; }
    ul { margin-top: 8px; padding-left: 18px; }
    li { margin-bottom: 6px; }
    a { color: #1d4ed8; text-decoration: none; }
    a:hover { text-decoration: underline; }
    """

    one_column_minimal_css = """
    body { font-family: 'Segoe UI', sans-serif; background: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }
    .cv { max-width: 840px; margin: auto; background: #ffffff; border-left: 6px solid #1e3a5f; padding: 24px 28px; }
    h1 { letter-spacing: 0.8px; margin-bottom: 4px; color: #0f172a; }
    h2 { margin-top: 20px; color: #1e40af; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; }
    .meta { color: #64748b; margin-top: -6px; }
    .job { margin-bottom: 14px; }
    ul { margin-top: 8px; }
    a { color: #1d4ed8; }
    """

    two_column_css = """
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #e9eef5; margin: 0; padding: 24px; color: #1f2937; }
    .cv { max-width: 1100px; margin: auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 8px 20px rgba(30,58,95,0.14); }
    .header { padding: 28px 32px; border-bottom: 1px solid #cbd5e1; background: linear-gradient(135deg, #1e3a5f, #274c77); color: #f8fafc; }
    .header-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; align-items: end; }
    .header-main h1 { margin: 0; font-size: 34px; line-height: 1.05; letter-spacing: 0.6px; color: #ffffff; }
    .headline { margin: 8px 0 0 0; font-size: 15px; color: #dbeafe; font-weight: 500; }
    .header-contact { background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.24); border-radius: 8px; padding: 10px 12px; font-size: 13px; }
    .header-contact p { margin: 0 0 6px 0; line-height: 1.4; color: #f8fafc; }
    .header-contact strong, .header-contact a { color: #ffffff; }
    .grid { display: grid; grid-template-columns: 1.85fr 1fr; gap: 20px; padding: 24px; }
    .main-panel { background: #ffffff; border: 1px solid #dbe5f0; border-radius: 8px; padding: 16px 18px; }
    .side-panel { background: #f8fbff; border: 1px solid #d6e3f2; border-radius: 8px; padding: 16px 16px; }
    h2 { margin: 0 0 10px 0; color: #1e3a5f; border-bottom: 2px solid #bfdbfe; padding-bottom: 4px; font-size: 22px; }
    h4 { margin: 0 0 4px 0; color: #0f172a; }
    p { line-height: 1.45; }
    ul { margin: 8px 0 12px 18px; padding: 0; }
    li { margin-bottom: 6px; }
    .meta { color: #475569; margin-top: -4px; }
    .job { margin-bottom: 14px; }
    a { color: #93c5fd; }
    .grid a { color: #1d4ed8; }
    """

    two_column_sidebar_css = """
    body { font-family: 'Calibri', 'Segoe UI', sans-serif; margin: 0; background: #e6edf5; padding: 24px; color: #1f2937; }
    .cv { max-width: 1100px; margin: auto; display: grid; grid-template-columns: 1fr 2fr; background: #ffffff; box-shadow: 0 8px 20px rgba(15,23,42,0.15); }
    .sidebar { background: linear-gradient(180deg, #1e293b, #0f172a); color: #f8fafc; padding: 24px; }
    .content { padding: 24px; }
    .sidebar h1 { color: #ffffff; }
    .sidebar h2 { color: #bfdbfe; border-bottom: 1px solid #475569; }
    h2 { color: #1e3a5f; border-bottom: 2px solid #bfdbfe; padding-bottom: 4px; }
    .meta { color: #64748b; margin-top: -6px; }
    .job { margin-bottom: 14px; }
    .sidebar a { color: #93c5fd; }
    .content a { color: #1d4ed8; }
    """

    two_column_sidebar_skillset_css = """
    body { font-family: 'Inter', 'Segoe UI', sans-serif; margin: 0; background: #f0f2f5; padding: 32px; color: #0f172a; }
    .cv { max-width: 1120px; margin: auto; background: #ffffff; display: grid; grid-template-columns: 0.95fr 1.7fr; border-radius: 18px; box-shadow: 0 18px 40px rgba(15,23,42,0.18); overflow: hidden; }
    .sidebar { background: linear-gradient(180deg, #0f172a, #1f2937); color: #f8fafc; padding: 36px 32px; display: flex; flex-direction: column; gap: 14px; min-height: 420px; }
    .sidebar h1 { margin: 0; font-size: 34px; letter-spacing: 0.5px; }
    .sidebar .headline { color: #cbd5ff; font-weight: 500; margin-top: 6px; margin-bottom: 12px; }
    .contact-block { font-size: 13px; line-height: 1.6; }
    .contact-block strong { display: block; color: #94a3b8; font-size: 10px; letter-spacing: 0.4px; text-transform: uppercase; margin-top: 12px; }
    .contact-block span { color: #f0f4ff; }
    .sidebar-section { margin-top: 18px; }
    .sidebar-section h2 { font-size: 12px; letter-spacing: 0.6px; text-transform: uppercase; color: #94a3b8; margin-bottom: 6px; }
    .sidebar-section ul { margin: 0; padding-left: 16px; }
    .sidebar-section li { margin-bottom: 6px; line-height: 1.4; color: #f1f5f9; }
    .links { margin-top: auto; font-size: 14px; line-height: 1.7; }
    .links a { color: #60a5fa; text-decoration: none; margin-right: 12px; }
    .links a:last-child { margin-right: 0; }
    .content { padding: 36px; display: flex; flex-direction: column; gap: 24px; }
    .section-block { border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }
    .section-block h2 { margin-bottom: 10px; font-size: 22px; color: #0f172a; }
    .job { margin-bottom: 12px; }
    .job h4 { margin: 0; }
    .meta { color: #475569; margin-bottom: 8px; }
    .referees-list { margin: 0; padding-left: 18px; }
    .referees-list li { margin-bottom: 8px; }
    """

    two_column_accent_css = """
    body { font-family: 'Inter', 'Segoe UI', sans-serif; margin: 0; background: #f5f7fb; padding: 32px; }
    .cv { max-width: 960px; margin: auto; background: #ffffff; border-radius: 22px; box-shadow: 0 20px 45px rgba(15,23,42,0.25); overflow: hidden; }
    .hero { background: linear-gradient(135deg, #102a43, #1e3a8a); color: #f8fafc; padding: 36px 40px; display: grid; grid-template-columns: 2fr 1fr; gap: 24px; align-items: end; }
    .hero h1 { margin: 0; font-size: 36px; letter-spacing: 0.6px; }
    .hero .headline { margin: 6px 0 0; font-size: 16px; color: #cbd5f5; }
    .hero-meta { font-size: 14px; line-height: 1.6; }
    .hero-meta strong { display: block; color: #cbd5f5; text-transform: uppercase; letter-spacing: 0.5px; font-size: 10px; margin-top: 10px; }
    .hero-links { margin-top: 12px; }
    .hero-links a { color: #bae6fd; margin-right: 12px; font-weight: 600; text-decoration: none; }
    .main { padding: 36px; display: grid; grid-template-columns: 1.7fr 0.9fr; gap: 24px; }
    .main-panel { border-right: 1px solid #e5e7eb; padding-right: 24px; }
    .aside-panel { padding-left: 24px; }
    .main-panel h2, .aside-panel h2 { margin-top: 0; color: #0f172a; font-size: 22px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 14px; }
    .main-panel .job { margin-bottom: 12px; }
    .main-panel .meta { color: #475569; margin-bottom: 8px; }
    .aside-panel ul { margin: 0; padding-left: 18px; line-height: 1.6; }
    .aside-panel li { margin-bottom: 6px; }
    """

    two_column_slate_css = """
    body { font-family: 'Source Sans Pro', 'Segoe UI', sans-serif; margin: 0; background: #eceef1; color: #111827; }
    .cv { max-width: 1100px; margin: 32px auto; background: #ffffff; border: 1px solid #d1d5da; box-shadow: 0 25px 50px rgba(15,23,42,0.2); }
    .name-banner { padding: 24px 38px; border-bottom: 1px solid #d6d8dc; display: flex; justify-content: center; }
    .name-banner h1 { margin: 0; font-size: 34px; letter-spacing: 6px; text-transform: uppercase; color: #111827; }
    .layout { display: grid; grid-template-columns: 0.95fr 1.55fr; }
    .sidebar { background: #f1f3f5; padding: 32px 30px; border-right: 1px solid #d6d8dc; display: flex; flex-direction: column; gap: 28px; }
    .sidebar h3 { margin: 0 0 14px 0; font-size: 12px; letter-spacing: 2px; text-transform: uppercase; color: #4b5563; }
    .detail-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 14px; }
    .detail-label { font-weight: 600; color: #4b5563; }
    .detail-value { text-align: right; }
    .sidebar ul { margin: 0; padding-left: 18px; }
    .sidebar li { margin-bottom: 6px; line-height: 1.5; color: #1f2937; }
    .sidebar-section { border-top: 1px solid #d6d8dc; padding-top: 18px; }
    .main-area { padding: 36px 42px; }
    .main-area h2 { margin-top: 0; font-size: 20px; letter-spacing: 2px; text-transform: uppercase; color: #111827; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }
    .summary { font-size: 15px; line-height: 1.7; color: #1f2937; margin-bottom: 24px; }
    .section-body { margin-top: 18px; }
    .section-body .job { margin-bottom: 18px; }
    .section-body h4 { margin: 0; font-size: 16px; color: #111827; }
    .section-body .meta { font-size: 13px; color: #64748b; margin-top: 4px; }
    .main-area ul { padding-left: 20px; }
    .links-row { margin-top: 14px; font-size: 13px; color: #111827; letter-spacing: 0.4px; }
    .divider { height: 1px; background: #e2e8f0; margin: 32px 0 18px; }
    """

    if template == "One Column - Minimal":
        return f"""
        <html><head><meta charset='UTF-8'><style>{one_column_minimal_css}</style></head>
        <body>
            <div class='cv'>
                <h1>{name}</h1>
                <p>{headline}</p>
                {contact}
                {links}
                {section_main}
                {section_side}
            </div>
        </body></html>
        """

    if template == "Two Column - Professional":
        return f"""
        <html><head><meta charset='UTF-8'><style>{two_column_css}</style></head>
        <body>
            <div class='cv'>
                <div class='header'>
                    <div class='header-grid'>
                        <div class='header-main'>
                            <h1>{name}</h1>
                            <p class='headline'>{headline}</p>
                        </div>
                        <div class='header-contact'>
                            {contact}
                            {links}
                        </div>
                    </div>
                </div>
                <div class='grid'>
                    <div class='main-panel'>{section_main}</div>
                    <div class='side-panel'>{section_side}</div>
                </div>
            </div>
        </body></html>
        """

    if template == "Two Column - Sidebar":
        return f"""
        <html><head><meta charset='UTF-8'><style>{two_column_sidebar_css}</style></head>
        <body>
            <div class='cv'>
                <aside class='sidebar'>
                    <h1>{name}</h1>
                    <p>{headline}</p>
                    {contact}
                    {links}
                    {section_side}
                </aside>
                <main class='content'>
                    {section_main}
                </main>
            </div>
        </body></html>
        """

    if template == "Two Column - Sidebar Skillset":
        sidebar_contact = f"""
        <div class='contact-block'>
            <strong>Location</strong><span>{html.escape(cv.get('location', ''))}</span>
            <strong>Phone</strong><span>{html.escape(cv.get('phone', ''))}</span>
            <strong>Email</strong><span>{html.escape(cv.get('email', ''))}</span>
        </div>
        """
        return f"""
        <html><head><meta charset='UTF-8'><style>{two_column_sidebar_skillset_css}</style></head>
        <body>
            <div class='cv'>
                <aside class='sidebar'>
                    <h1>{name}</h1>
                    <p class='headline'>{headline}</p>
                    {sidebar_contact}
                    <div class='sidebar-section'>
                        <h2>Skills</h2>
                        {sidebar_skills}
                    </div>
                    <div class='sidebar-section'>
                        <h2>Languages</h2>
                        {sidebar_languages}
                    </div>
                    <div class='links'>
                        {links}
                    </div>
                </aside>
                <main class='content'>
                    <div class='section-block'>
                        {section_main}
                    </div>
                    <div class='section-block'>
                        <h2>Certifications</h2>
                        {certifications_html}
                    </div>
                    <div class='section-block'>
                        <h2>Referees</h2>
                        {referees_html}
                    </div>
                </main>
            </div>
        </body></html>
        """

    if template == "Two Column - Accent Panel":
        return f"""
        <html><head><meta charset='UTF-8'><style>{two_column_accent_css}</style></head>
        <body>
            <div class='cv'>
                <div class='hero'>
                    <div>
                        <h1>{name}</h1>
                        <p class='headline'>{headline}</p>
                    </div>
                    <div class='hero-meta'>
                        {contact}
                        <div class='hero-links'>
                            {links}
                        </div>
                    </div>
                </div>
                <div class='main'>
                    <div class='main-panel'>
                        {section_main}
                    </div>
                    <aside class='aside-panel'>
                        {section_side}
                    </aside>
                </div>
            </div>
        </body></html>
        """

    if template == "Two Column - Slate Profile":
        contact_fields = [
            ("Name", cv.get("full_name", "")),
            ("Address", cv.get("location", "")),
            ("Phone", cv.get("phone", "")),
            ("Email", cv.get("email", "")),
        ]
        contact_rows = []
        for label, raw_value in contact_fields:
            if str(raw_value).strip():
                contact_rows.append(
                    """
                    <div class='detail-row'>
                        <span class='detail-label'>{label}</span>
                        <span class='detail-value'>{value}</span>
                    </div>
                    """.format(label=label, value=html.escape(str(raw_value)))
                )
        personal_details_html = "".join(contact_rows)

        competencies = cv.get("core_competencies", [])
        skills_entries = competencies[:6] if competencies else []
        if not skills_entries:
            skills_entries = cv.get("languages", [])
        skills_html = html_list(skills_entries)
        technical_entries = competencies[6:]
        tech_html = html_list(technical_entries)
        education_html = html_list(cv.get("education", []))
        languages_html = html_list(cv.get("languages", []))
        links_row = f"<div class='links-row'>{' | '.join(link_items)}</div>" if link_items else ""

        education_section = (
            f"""
            <div class='sidebar-section'>
                <h3>Education</h3>
                {education_html}
            </div>
            """ if education_html else ""
        )
        skills_section = (
            f"""
            <div class='sidebar-section'>
                <h3>Skills</h3>
                {skills_html}
            </div>
            """ if skills_html else ""
        )
        tech_section = (
            f"""
            <div class='sidebar-section'>
                <h3>Technical Proficiencies</h3>
                {tech_html}
            </div>
            """ if tech_html else ""
        )
        languages_section = (
            f"""
            <div class='sidebar-section'>
                <h3>Languages</h3>
                {languages_html}
            </div>
            """ if languages_html else ""
        )

        return f"""
        <html><head><meta charset='UTF-8'><style>{two_column_slate_css}</style></head>
        <body>
            <div class='cv'>
                <div class='name-banner'>
                    <h1>{name}</h1>
                </div>
                <div class='layout'>
                    <aside class='sidebar'>
                        <div class='sidebar-section'>
                            <h3>Personal Details</h3>
                            {personal_details_html}
                            {links_row}
                        </div>
                        {education_section}
                        {skills_section}
                        {tech_section}
                        {languages_section}
                    </aside>
                    <div class='main-area'>
                        <div class='summary'>
                            <p>{profile}</p>
                        </div>
                        <div class='section-body'>
                            <h2>Work Experience</h2>
                            {html_experience(cv.get('experience', []))}
                        </div>
                        <div class='divider'></div>
                        <div class='section-body'>
                            <h2>Courses and Certificates</h2>
                            {html_list(cv.get('certifications', []))}
                        </div>
                    </div>
                </div>
            </div>
        </body></html>
        """

    return f"""
    <html><head><meta charset='UTF-8'><style>{one_column_css}</style></head>
    <body>
        <div class='cv'>
            <div class='hero'>
                <h1>{name}</h1>
                <p class='headline'>{headline}</p>
                <div class='hero-meta'>
                    {contact}
                    {links}
                </div>
            </div>
            <div class='content'>
                <div class='section-block'>{section_main}</div>
                <div class='section-block'>{section_side}</div>
            </div>
        </div>
    </body></html>
    """


def pdf_safe_text(value: str) -> str:
    return str(value).replace("\n", " ").encode("latin-1", "replace").decode("latin-1")


def wrap_pdf_text(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    if not REPORTLAB_AVAILABLE:
        return [pdf_safe_text(text)]
    words = pdf_safe_text(text).split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_pdf_wrapped_text(
    pdf,
    text: str,
    x: float,
    y: float,
    max_width: float,
    bottom_margin: float,
    top_reset: float,
    font_name: str = "Helvetica",
    font_size: int = 10,
    leading: int = 13,
) -> float:
    pdf.setFont(font_name, font_size)
    for line in wrap_pdf_text(text, font_name, font_size, max_width):
        if y < bottom_margin:
            pdf.showPage()
            y = top_reset
            pdf.setFont(font_name, font_size)
        pdf.drawString(x, y, line)
        y -= leading
    return y


def draw_pdf_title(pdf, title: str, x: float, y: float, font_size: int = 12) -> float:
    pdf.setFillColor(colors.HexColor("#1E3A5F"))
    pdf.setFont("Helvetica-Bold", font_size)
    pdf.drawString(x, y, pdf_safe_text(title))
    pdf.setStrokeColor(colors.HexColor("#BFD7ED"))
    pdf.setLineWidth(1)
    pdf.line(x, y - 3, x + 120, y - 3)
    pdf.setFillColor(colors.black)
    return y - 16


def ensure_pdf_space(pdf, y: float, needed_height: float, bottom_margin: float, top_reset: float) -> float:
    if y - needed_height < bottom_margin:
        pdf.showPage()
        return top_reset
    return y


def build_pdf_one_column(cv: dict) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 40
    right = width - 40
    content_width = right - left
    top = height - 50
    bottom = 45
    y = top

    header_height = 72
    header_bottom = y - 52
    pdf.setFillColor(colors.HexColor("#1E3A5F"))
    pdf.rect(left, header_bottom, content_width, header_height, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(left + 12, y - 6, pdf_safe_text(cv.get("full_name", "")))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left + 12, y - 23, pdf_safe_text(cv.get("headline", "")))
    y = header_bottom - 14

    pdf.setFillColor(colors.HexColor("#334155"))
    y = draw_pdf_wrapped_text(
        pdf,
        f"Location: {cv.get('location', '')} | Phone: {cv.get('phone', '')} | Email: {cv.get('email', '')}",
        left,
        y,
        content_width,
        bottom,
        top,
        font_name="Helvetica",
        font_size=10,
        leading=13,
    )
    pdf.setFillColor(colors.HexColor("#1D4ED8"))
    links_line = f"LinkedIn: {cv.get('linkedin', '')} | GitHub: {cv.get('github', '')}"
    y = draw_pdf_wrapped_text(pdf, links_line, left, y, content_width, bottom, top)
    pdf.setFillColor(colors.black)
    y -= 6

    y = ensure_pdf_space(pdf, y, 40, bottom, top)
    y = draw_pdf_title(pdf, "Profile", left, y)
    y = draw_pdf_wrapped_text(pdf, cv.get("profile_summary", ""), left, y, content_width, bottom, top)
    y -= 6

    y = ensure_pdf_space(pdf, y, 40, bottom, top)
    y = draw_pdf_title(pdf, "Core Competencies", left, y)
    for item in cv.get("core_competencies", []):
        y = draw_pdf_wrapped_text(pdf, f"- {item}", left, y, content_width, bottom, top)
    y -= 6

    y = ensure_pdf_space(pdf, y, 40, bottom, top)
    y = draw_pdf_title(pdf, "Professional Experience", left, y)
    for exp in cv.get("experience", []):
        y = ensure_pdf_space(pdf, y, 28, bottom, top)
        y = draw_pdf_wrapped_text(
            pdf,
            f"{exp.get('role', '')} - {exp.get('organization', '')} | {exp.get('period', '')}",
            left,
            y,
            content_width,
            bottom,
            top,
            font_name="Helvetica-Bold",
            font_size=10,
            leading=13,
        )
        for bullet in exp.get("bullets", []):
            y = draw_pdf_wrapped_text(pdf, f"  - {bullet}", left, y, content_width, bottom, top)
        y -= 3

    y = ensure_pdf_space(pdf, y, 36, bottom, top)
    y = draw_pdf_title(pdf, "Education", left, y)
    for item in cv.get("education", []):
        y = draw_pdf_wrapped_text(pdf, f"- {item}", left, y, content_width, bottom, top)

    y = ensure_pdf_space(pdf, y, 36, bottom, top)
    y = draw_pdf_title(pdf, "Certifications", left, y)
    for item in cv.get("certifications", []):
        y = draw_pdf_wrapped_text(pdf, f"- {item}", left, y, content_width, bottom, top)

    y = ensure_pdf_space(pdf, y, 36, bottom, top)
    y = draw_pdf_title(pdf, "Languages", left, y)
    for item in cv.get("languages", []):
        y = draw_pdf_wrapped_text(pdf, f"- {item}", left, y, content_width, bottom, top)

    y = ensure_pdf_space(pdf, y, 42, bottom, top)
    y = draw_pdf_title(pdf, "Referees", left, y)
    for idx, ref in enumerate(cv.get("referees", []), start=1):
        ref_line = (
            f"{idx}. {ref.get('name', '')} - {ref.get('title', '')} | "
            f"Email: {ref.get('email', '')} | Phone: {ref.get('phone', '')}"
        )
        y = draw_pdf_wrapped_text(pdf, ref_line, left, y, content_width, bottom, top)

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def build_pdf_two_column(cv: dict) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin = 32
    gap = 16
    top = height - 28
    bottom = 45
    left_x = margin
    left_width = (width - (2 * margin) - gap) * 0.62
    right_x = left_x + left_width + gap
    right_width = width - right_x - margin

    header_height = 64
    header_bottom = top - header_height
    pdf.setFillColor(colors.HexColor("#1E3A5F"))
    pdf.rect(left_x, header_bottom, width - (2 * margin), header_height, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(left_x + 12, top - 24, pdf_safe_text(cv.get("full_name", "")))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left_x + 12, top - 42, pdf_safe_text(cv.get("headline", "")))

    contact_y = top - 20
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(
        width - margin - 12,
        contact_y,
        pdf_safe_text(f"{cv.get('location', '')} | {cv.get('phone', '')}"),
    )
    pdf.drawRightString(
        width - margin - 12,
        contact_y - 11,
        pdf_safe_text(f"{cv.get('email', '')}"),
    )
    pdf.drawRightString(
        width - margin - 12,
        contact_y - 22,
        pdf_safe_text("LinkedIn | GitHub"),
    )
    pdf.setFillColor(colors.black)

    y_left = header_bottom - 16
    y_right = header_bottom - 16

    pdf.setFillColor(colors.HexColor("#F8FBFF"))
    pdf.rect(left_x - 2, bottom - 4, left_width + 6, y_left - (bottom - 4), fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#F1F5F9"))
    pdf.rect(right_x - 8, bottom - 4, right_width + 12, y_right - (bottom - 4), fill=1, stroke=0)
    pdf.setFillColor(colors.black)

    y_left = draw_pdf_title(pdf, "Profile", left_x, y_left)
    y_left = draw_pdf_wrapped_text(
        pdf, cv.get("profile_summary", ""), left_x, y_left, left_width, bottom, top
    )
    y_left -= 6

    y_left = draw_pdf_title(pdf, "Professional Experience", left_x, y_left)
    for exp in cv.get("experience", []):
        y_left = draw_pdf_wrapped_text(
            pdf,
            f"{exp.get('role', '')} - {exp.get('organization', '')} | {exp.get('period', '')}",
            left_x,
            y_left,
            left_width,
            bottom,
            top,
            font_name="Helvetica-Bold",
            font_size=9,
            leading=12,
        )
        for bullet in exp.get("bullets", []):
            y_left = draw_pdf_wrapped_text(
                pdf,
                f"- {bullet}",
                left_x,
                y_left,
                left_width,
                bottom,
                top,
                font_name="Helvetica",
                font_size=9,
                leading=12,
            )
        y_left -= 3

    y_left = draw_pdf_title(pdf, "Education", left_x, y_left)
    for item in cv.get("education", []):
        y_left = draw_pdf_wrapped_text(pdf, f"- {item}", left_x, y_left, left_width, bottom, top)

    y_right = draw_pdf_title(pdf, "Contact", right_x, y_right)
    y_right = draw_pdf_wrapped_text(
        pdf,
        f"Location: {cv.get('location', '')}",
        right_x,
        y_right,
        right_width,
        bottom,
        top,
        font_size=9,
        leading=12,
    )
    y_right = draw_pdf_wrapped_text(
        pdf,
        f"Phone: {cv.get('phone', '')}",
        right_x,
        y_right,
        right_width,
        bottom,
        top,
        font_size=9,
        leading=12,
    )
    y_right = draw_pdf_wrapped_text(
        pdf,
        f"Email: {cv.get('email', '')}",
        right_x,
        y_right,
        right_width,
        bottom,
        top,
        font_size=9,
        leading=12,
    )
    y_right = draw_pdf_wrapped_text(
        pdf,
        f"LinkedIn: {cv.get('linkedin', '')}",
        right_x,
        y_right,
        right_width,
        bottom,
        top,
        font_size=9,
        leading=12,
    )
    y_right = draw_pdf_wrapped_text(
        pdf,
        f"GitHub: {cv.get('github', '')}",
        right_x,
        y_right,
        right_width,
        bottom,
        top,
        font_size=9,
        leading=12,
    )
    y_right -= 6

    y_right = draw_pdf_title(pdf, "Core Competencies", right_x, y_right)
    for item in cv.get("core_competencies", []):
        y_right = draw_pdf_wrapped_text(
            pdf, f"- {item}", right_x, y_right, right_width, bottom, top, font_size=9, leading=12
        )

    y_right -= 4
    y_right = draw_pdf_title(pdf, "Certifications", right_x, y_right)
    for item in cv.get("certifications", []):
        y_right = draw_pdf_wrapped_text(
            pdf, f"- {item}", right_x, y_right, right_width, bottom, top, font_size=9, leading=12
        )

    y_right -= 4
    y_right = draw_pdf_title(pdf, "Languages", right_x, y_right)
    for item in cv.get("languages", []):
        y_right = draw_pdf_wrapped_text(
            pdf, f"- {item}", right_x, y_right, right_width, bottom, top, font_size=9, leading=12
        )

    y_right -= 4
    y_right = draw_pdf_title(pdf, "Referees", right_x, y_right)
    for ref in cv.get("referees", []):
        text = f"- {ref.get('name', '')}: {ref.get('title', '')}, {ref.get('phone', '')}"
        y_right = draw_pdf_wrapped_text(
            pdf, text, right_x, y_right, right_width, bottom, top, font_size=9, leading=12
        )

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def build_pdf(cv: dict, template: str) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    if "Two Column" in template:
        return build_pdf_two_column(cv)
    return build_pdf_one_column(cv)


def cv_editor(profile_id: int, selected_version: dict) -> None:
    cv = selected_version["cv"]
    st.subheader("Edit CV")

    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", value=cv.get("full_name", ""))
        headline = st.text_input("Headline", value=cv.get("headline", ""))
        location = st.text_input("Location", value=cv.get("location", ""))
        phone = st.text_input("Phone", value=cv.get("phone", ""))
        email = st.text_input("Email", value=cv.get("email", ""))
    with col2:
        linkedin = st.text_input("LinkedIn URL", value=cv.get("linkedin", ""))
        github = st.text_input("GitHub URL", value=cv.get("github", ""))
        version_name = st.text_input("Version Name", value=selected_version["version_name"])

    profile_summary = st.text_area("Profile Summary", value=cv.get("profile_summary", ""), height=140)
    competencies_text = st.text_area(
        "Core Competencies (one per line)",
        value=list_to_text(cv.get("core_competencies", [])),
        height=160,
    )

    st.caption("Experience format per block: Role || Organization || Period, then bullet lines starting with '-'.")
    experience_text = st.text_area(
        "Professional Experience",
        value=experience_to_text(cv.get("experience", [])),
        height=260,
    )

    education_text = st.text_area(
        "Education (one per line)",
        value=list_to_text(cv.get("education", [])),
        height=120,
    )
    certifications_text = st.text_area(
        "Certifications (one per line)",
        value=list_to_text(cv.get("certifications", [])),
        height=120,
    )
    languages_text = st.text_area(
        "Languages (one per line)",
        value=list_to_text(cv.get("languages", [])),
        height=90,
    )

    st.caption("Referees format: Name || Title || Email || Phone")
    referees_text = st.text_area(
        "Referees",
        value=referees_to_text(cv.get("referees", [])),
        height=150,
    )

    new_cv = {
        "full_name": full_name,
        "headline": headline,
        "location": location,
        "phone": phone,
        "email": email,
        "linkedin": linkedin,
        "github": github,
        "profile_summary": profile_summary,
        "core_competencies": text_to_list(competencies_text),
        "experience": text_to_experience(experience_text),
        "education": text_to_list(education_text),
        "certifications": text_to_list(certifications_text),
        "languages": text_to_list(languages_text),
        "referees": text_to_referees(referees_text),
    }

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save Changes", type="primary", use_container_width=True):
            save_version(selected_version["id"], version_name, new_cv)
            st.success("Version updated successfully.")
            st.rerun()
    with c2:
        new_version_name = st.text_input("New Version Name", value="", placeholder="e.g., Recruiter v2")
        if st.button("Save as New Version", use_container_width=True):
            if not new_version_name.strip():
                st.error("Enter a name for the new version.")
            else:
                create_new_version(profile_id, new_version_name, new_cv)
                st.success("New version created.")
                st.rerun()


def download_section(cv: dict, suggested_name: str) -> None:
    st.subheader("Download CV")
    template = st.selectbox(
        "Select template",
        AVAILABLE_TEMPLATES,
    )
    html_output = build_html(cv, template)
    pdf_output = build_pdf(cv, template) if REPORTLAB_AVAILABLE else b""
    slug = template.lower().replace(" ", "_").replace("-", "")
    html_filename = f"{suggested_name}_{slug}.html"
    pdf_filename = f"{suggested_name}_{slug}.pdf"

    col_html, col_pdf = st.columns(2)
    with col_html:
        st.download_button(
            "Download as HTML",
            data=html_output,
            file_name=html_filename,
            mime="text/html",
            use_container_width=True,
        )
    with col_pdf:
        if REPORTLAB_AVAILABLE:
            st.download_button(
                "Download as PDF",
                data=pdf_output,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.button("Download as PDF", disabled=True, use_container_width=True)
            st.caption("PDF export unavailable: install `reportlab` from requirements.")


def get_editor_password() -> str:
    secret_password = st.secrets.get("editor_password", "")
    if secret_password:
        return str(secret_password)
    return os.getenv("CV_EDITOR_PASSWORD", "")


def render_editor_login() -> None:
    st.subheader("Editor Login")
    configured_password = get_editor_password()

    if not configured_password:
        st.warning("Editor password is not configured.")
        st.info(
            "Set `editor_password` in Streamlit secrets or set environment variable "
            "`CV_EDITOR_PASSWORD`, then reload the app."
        )
        return

    with st.form("editor_login_form"):
        password = st.text_input("Password", type="password", placeholder="Enter editor password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if hmac.compare_digest(password, configured_password):
            st.session_state["editor_authenticated"] = True
            st.success("Login successful.")
            st.rerun()
        else:
            st.error("Invalid password.")


st.set_page_config(page_title="CV Portfolio Manager", page_icon="💼", layout="wide")
init_db()

if "editor_authenticated" not in st.session_state:
    st.session_state["editor_authenticated"] = False

st.sidebar.title("CV Portfolio")
page = st.sidebar.radio("Navigation", ["Public View", "Editor"], index=0)

if page == "Public View":
    st.sidebar.info("Public view of the default CV profile.")
    default_version = fetch_default_version()
    if not default_version:
        st.error("No default profile found. Create one in Editor.")
        st.stop()

    template_choice = st.selectbox("Display Template", AVAILABLE_TEMPLATES, index=0)
    st.caption(f"Showing default CV: {default_version['version_name']}")
    render_cv_streamlit(default_version["cv"], template_choice)
    st.divider()
    download_section(default_version["cv"], "default_cv")

else:
    if not st.session_state.get("editor_authenticated", False):
        st.sidebar.warning("Login required for editor access.")
        render_editor_login()
        st.stop()

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state["editor_authenticated"] = False
        st.rerun()

    st.sidebar.info("Create, edit, and version multiple CV profiles.")
    profiles = fetch_profiles()

    if not profiles:
        st.error("No profiles available.")
        st.stop()

    profile_options = {f"{p['name']}{' (Default)' if p['is_default'] else ''}": p for p in profiles}
    selected_profile_label = st.selectbox("Select Profile", list(profile_options.keys()))
    selected_profile = profile_options[selected_profile_label]

    with st.expander("Profile Management"):
        new_profile_name = st.text_input("Create New Profile", value="", placeholder="e.g., DevOps CV")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Create Profile", use_container_width=True):
                if not new_profile_name.strip():
                    st.error("Profile name is required.")
                else:
                    create_profile(new_profile_name, default_cv_data())
                    st.success("Profile created.")
                    st.rerun()
        with col_b:
            if st.button("Set As Default", use_container_width=True):
                set_default_profile(selected_profile["id"])
                st.success("Default profile updated.")
                st.rerun()

    versions = fetch_versions(selected_profile["id"])
    if not versions:
        st.error("No CV versions found for this profile.")
        st.stop()

    version_options = {f"{v['version_name']} ({v['updated_at'][:19]})": v for v in versions}
    selected_version_label = st.selectbox("Select Version", list(version_options.keys()))
    selected_version_meta = version_options[selected_version_label]
    selected_version = fetch_version(selected_version_meta["id"])

    preview_template = st.selectbox("Preview Template", AVAILABLE_TEMPLATES, index=0)
    st.subheader("Preview")
    render_cv_streamlit(selected_version["cv"], preview_template)
    st.divider()
    download_section(selected_version["cv"], selected_profile["name"].replace(" ", "_"))
    st.divider()
    cv_editor(selected_profile["id"], selected_version)
