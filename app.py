import html
import hmac
import json
import os
import re
import sqlite3
import tempfile
from datetime import datetime
from inspect import signature
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

DISPLAY_TEMPLATE_OPTIONS = {
    template.replace(" - ", " • "): template for template in AVAILABLE_TEMPLATES
}


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
                    "Facilitate effective service delivery by managing service tickets on ServiceNow, ensuring timely documentation of incidents, resolutions, and procedures.",
                    "Participate in onboarding and offboarding processes, coordinating account updates and equipment provisioning according to established SOPs.",
                    "Monitor service queues and perform follow-ups on aging tickets to provide users with professional updates on their issues.",
                    "Collaborate with senior specialists and infrastructure teams to escalate complex issues, ensuring clear technical context for efficient resolution.",
                    "Contribute to service improvements by identifying recurring problems and exploring opportunities for operational automation.",
                ],
            },
            {
                "role": "IT ASSISTANT",
                "organization": "Plan International Kenya, Coastal Hub",
                "period": "November 2022 – February 2024",
                "bullets": [
                    "Executed user identity lifecycle activities by configuring user accounts and permissions to secure system access.",
                    "Collaborated with IT management on global directory services and email groups to ensure seamless SSO integrations and quality service delivery.",
                    "Optimized IT infrastructure for efficiency and supported system upgrades, backups, and secure connectivity.",
                    "Adhered to organizational policies on safeguarding, gender equality, and inclusion.",
                    "Delivered Tier 1 support for desktop, network, and infrastructure issues, successfully communicating technical concepts to non-technical users.",
                    "Provided support for Microsoft 365 applications, ensuring proper configuration of email accounts and VPN connectivity.",
                    "Diagnosed and resolved routine hardware and software problems, maintaining accurate records of all interactions in the ticketing system.",
                    "Mentored junior team members, facilitating their technical development and contributing to overall team performance improvements.",
                ],
            },
            {
                "role": "IT SUPPORT INTERN",
                "organization": "Plan International Kenya, Coastal Hub",
                "period": "November 2021 – November 2022",
                "bullets": [
                    "Managed Global Active Directory and OKTA services, troubleshooting authentication errors and supporting access modifications.",
                    "Supported technical operations for systems including Exchange Online, SAP, and Office 365, ensuring secure user access and minimal downtime.",
                    "Enforced IT policies, developed security guidelines, and provided user training on corporate applications.",
                    "Assisted in managing user accounts within Active Directory and Azure AD, ensuring proper access provisioning and permissions management.",
                    "Supported endpoint management and troubleshooting of mobile devices and workstations, including installations and configurations.",
                    "Collaborated with IT teams to analyze incidents.",
                ],
            },
        ],
        "education": [
            {
                "course": "Master of Science in Computer Science",
                "institution": "UNICAF University",
                "timeline": "Ongoing",
            },
            {
                "course": "Coursework in Cryptography and Networking Security",
                "institution": "UNICAF University",
                "timeline": "Ongoing",
            },
            {
                "course": "Bachelor of Business Information Technology",
                "institution": "Taita Taveta University",
                "timeline": "November 2019",
            },
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
                "organization": "Plan International Kenya",
                "title": "Country Sponsorship Manager",
                "email": "winfred.mukonza@plan-international.org",
                "phone": "+254713267985",
            },
            {
                "name": "Eston Nyaga",
                "organization": "Plan International Kenya, Coast Hub",
                "title": "Program Area Manager",
                "email": "eston.nyaga@plan-international.org",
                "phone": "+254722912493",
            },
            {
                "name": "Cynthia Akoth",
                "organization": "Plan International Kenya",
                "title": "IT Coordinator",
                "email": "cynthia.akoth@plan-international.org",
                "phone": "+254707870390",
            },
            {
                "name": "Sharon Meliyio",
                "organization": "Plan International Kenya",
                "title": "Country IT Manager",
                "email": "sharon.meliyio@plan-international.org",
                "phone": "+254724917720",
            },
        ],
    }


TEXT_FORMATTERS = [
    "bold",
    "italic",
    "code",
    "link",
    "ordered_list",
    "unordered_list",
    "quote",
]


TEXT_AREA_SUPPORTS_FORMATTERS = "text_formatters" in signature(st.text_area).parameters


def rich_text_area(label: str, value: str, height: int, **kwargs) -> str:
    params = {"value": value, "height": height}
    params.update(kwargs)
    if TEXT_AREA_SUPPORTS_FORMATTERS:
        params["text_formatters"] = TEXT_FORMATTERS
    return st.text_area(label, **params)


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


def _merge_pdf_theme(base: dict, overrides: dict) -> dict:
    merged = base.copy()
    merged.update(overrides)
    return merged


PDF_BASE_TWO_COLUMN_THEME = {
    "background": colors.HexColor("#e9eef5"),
    "hero_background": colors.HexColor("#1e3a5f"),
    "hero_accent": colors.HexColor("#274c77"),
    "hero_strip": colors.HexColor("#93c5fd"),
    "panel_primary": colors.HexColor("#ffffff"),
    "panel_secondary": colors.HexColor("#f8fbff"),
    "text_color": colors.HexColor("#0f172a"),
    "hero_text": colors.white,
    "panel_border": colors.HexColor("#d6e3f2"),
    "layout": "professional_header",
}


PDF_BASE_ONE_COLUMN_THEME = {
    "background": colors.HexColor("#f8fafc"),
    "hero_background": colors.HexColor("#ffffff"),
    "hero_accent": colors.HexColor("#c7d2fe"),
    "hero_strip": colors.HexColor("#1d4ed8"),
    "panel_primary": colors.HexColor("#ffffff"),
    "panel_secondary": colors.HexColor("#f1f5f9"),
    "text_color": colors.HexColor("#0f172a"),
    "hero_text": colors.HexColor("#0f172a"),
}


PDF_TEMPLATE_THEMES = {
    "Two Column - Professional": _merge_pdf_theme(
        PDF_BASE_TWO_COLUMN_THEME,
        {
            "layout": "professional_header",
        },
    ),
    "Two Column - Sidebar": _merge_pdf_theme(
        PDF_BASE_TWO_COLUMN_THEME,
        {
            "background": colors.HexColor("#0f172a"),
            "hero_background": colors.HexColor("#111827"),
            "hero_accent": colors.HexColor("#1f2937"),
            "hero_strip": colors.HexColor("#60a5fa"),
            "panel_primary": colors.HexColor("#fefefe"),
            "panel_secondary": colors.HexColor("#f4f6fb"),
            "text_color": colors.HexColor("#0f172a"),
            "hero_text": colors.HexColor("#f8fafc"),
            "panel_border": colors.HexColor("#d6e3f2"),
            "layout": "modern_header",
        },
    ),
    "Two Column - Sidebar Skillset": _merge_pdf_theme(
        PDF_BASE_TWO_COLUMN_THEME,
        {
            "background": colors.HexColor("#f0f2f5"),
            "hero_background": colors.HexColor("#0f172a"),
            "hero_accent": colors.HexColor("#1e293b"),
            "hero_strip": colors.HexColor("#60a5fa"),
            "panel_primary": colors.HexColor("#ffffff"),
            "panel_secondary": colors.HexColor("#f8fafc"),
            "text_color": colors.HexColor("#0f172a"),
            "hero_text": colors.HexColor("#f8fafc"),
            "panel_border": colors.HexColor("#dbe5f0"),
            "layout": "modern_header",
        },
    ),
    "Two Column - Accent Panel": _merge_pdf_theme(
        PDF_BASE_TWO_COLUMN_THEME,
        {
            "background": colors.HexColor("#f5f7fb"),
            "hero_background": colors.HexColor("#102a43"),
            "hero_accent": colors.HexColor("#1e3a8a"),
            "hero_strip": colors.HexColor("#bae6fd"),
            "panel_primary": colors.HexColor("#ffffff"),
            "panel_secondary": colors.HexColor("#eef2ff"),
            "text_color": colors.HexColor("#0f172a"),
            "hero_text": colors.HexColor("#f8fafc"),
            "panel_border": colors.HexColor("#d6e3f2"),
            "layout": "modern_header",
        },
    ),
    "Two Column - Slate Profile": _merge_pdf_theme(
        PDF_BASE_TWO_COLUMN_THEME,
        {
            "background": colors.HexColor("#eceef1"),
            "hero_background": colors.HexColor("#0f172a"),
            "hero_accent": colors.HexColor("#1e293b"),
            "hero_strip": colors.HexColor("#cbd5f5"),
            "panel_primary": colors.HexColor("#ffffff"),
            "panel_secondary": colors.HexColor("#f1f5f9"),
            "text_color": colors.HexColor("#0f172a"),
            "hero_text": colors.HexColor("#f8fafc"),
            "panel_border": colors.HexColor("#d6e3f2"),
            "layout": "modern_header",
        },
    ),
    "One Column - Classic": _merge_pdf_theme(
        PDF_BASE_ONE_COLUMN_THEME,
        {
            "background": colors.HexColor("#030712"),
            "hero_background": colors.HexColor("#102a43"),
            "hero_accent": colors.HexColor("#1e3a8a"),
            "hero_strip": colors.HexColor("#2563eb"),
            "panel_primary": colors.HexColor("#0f172a"),
            "panel_secondary": colors.HexColor("#0f172a"),
            "text_color": colors.HexColor("#e2e8f0"),
            "hero_text": colors.HexColor("#f8fafc"),
            "border": colors.HexColor("#1d4ed8"),
            "link_color": colors.HexColor("#38bdf8"),
            "layout": "classic_hero",
        },
    ),
    "One Column - Minimal": _merge_pdf_theme(
        PDF_BASE_ONE_COLUMN_THEME,
        {
            "hero_accent": colors.HexColor("#93c5fd"),
            "hero_text": colors.HexColor("#0f172a"),
            "text_color": colors.HexColor("#0f172a"),
            "layout": "minimal_clean",
        },
    ),
}


DISPLAY_TO_PDF_TEMPLATE_MAP = {template: template for template in DISPLAY_TEMPLATE_OPTIONS.values()}


def validate_template_mappings() -> list[str]:
    issues: list[str] = []
    display_templates = set(DISPLAY_TEMPLATE_OPTIONS.values())
    available_templates = set(AVAILABLE_TEMPLATES)

    missing_in_selector = sorted(available_templates - display_templates)
    if missing_in_selector:
        issues.append(f"Missing selector entries: {', '.join(missing_in_selector)}")

    extra_in_selector = sorted(display_templates - available_templates)
    if extra_in_selector:
        issues.append(f"Unknown selector entries: {', '.join(extra_in_selector)}")

    missing_pdf_themes = sorted(display_templates - set(PDF_TEMPLATE_THEMES.keys()))
    if missing_pdf_themes:
        issues.append(f"Missing PDF theme mappings: {', '.join(missing_pdf_themes)}")

    missing_pdf_map = sorted(display_templates - set(DISPLAY_TO_PDF_TEMPLATE_MAP.keys()))
    if missing_pdf_map:
        issues.append(f"Missing display-to-PDF mappings: {', '.join(missing_pdf_map)}")

    return issues


def get_pdf_theme(template: str) -> dict:
    mapped_template = DISPLAY_TO_PDF_TEMPLATE_MAP.get(template, template)
    if mapped_template in PDF_TEMPLATE_THEMES:
        return PDF_TEMPLATE_THEMES[mapped_template]
    if "Two Column" in mapped_template:
        return PDF_TEMPLATE_THEMES["Two Column - Professional"]
    if "One Column" in mapped_template:
        return PDF_TEMPLATE_THEMES["One Column - Classic"]
    return PDF_TEMPLATE_THEMES["One Column - Minimal"]


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


def render_cv_streamlit(cv: dict, template: str) -> None:
    st.title(cv.get("full_name", ""))
    st.caption(cv.get("headline", ""))
    st.caption(f"Template: {template}")

    html_output = build_html(cv, template)
    components.html(html_output, height=1600, scrolling=True)


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
            <div class=\"job\">
                <div class=\"experience-header\">
                    <h4>{role}</h4>
                    <span class=\"experience-period\">🕒 {period}</span>
                </div>
                <div class=\"experience-org\">🏢 {org}</div>
                {bullets}
            </div>
            """
        )
    return "".join(chunks)


def normalize_education_record(item) -> dict:
    if isinstance(item, dict):
        return item
    if isinstance(item, str):
        return {"course": item, "institution": "", "timeline": ""}
    return {"course": "", "institution": "", "timeline": ""}


def html_education(education: list[dict]) -> str:
    entries = []
    for item in education:
        record = normalize_education_record(item)
        course = html.escape(record.get("course", ""))
        institution = html.escape(record.get("institution", ""))
        timeline = html.escape(record.get("timeline", ""))
        if not any([course, institution, timeline]):
            continue
        entries.append(
            f"""
            <div class=\"education-entry\">
                <div class=\"education-top\">
                    <span class=\"education-course\">📚 {course}</span>
                    <span class=\"education-timeline\">{timeline}</span>
                </div>
                <div class=\"education-institution\">
                    🎓 {institution}
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
            meta_parts.append(f"<span class='referee-field'>🎯 {position}</span>")
        if email:
            meta_parts.append(f"<span class='referee-field'>✉️ {email}</span>")
        if phone:
            meta_parts.append(f"<span class='referee-field'>📞 {phone}</span>")
        meta_html = "".join(meta_parts)
        entries.append(
            f"""
            <li class='referee'>
                <div class='referee-head'>
                    <span class='referee-name'>🧑‍💼 {name}</span>
                    <span class='referee-org'>🏢 {organization}</span>
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


def section_header(title: str, icon: str) -> str:
    if not title:
        return ""
    return (
        "<div class='section-heading'>"
        f"<span class='section-icon'>{html.escape(icon)}</span>"
        f"<h2>{html.escape(title)}</h2>"
        "</div>"
    )


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

    profile_section = (
        section_header("Profile", "🧭") + f"<p>{profile}</p>"
    )
    experience_section = (
        section_header("Professional Experience", "💼")
        + html_experience(cv.get("experience", []))
    )
    education_section = (
        section_header("Education", "🎓")
        + html_education(cv.get("education", []))
    )
    competencies_section = (
        section_header("Core Competencies", "🧠")
        + html_list(cv.get("core_competencies", []))
    )
    certifications_section = (
        section_header("Certifications", "📜")
        + html_list(cv.get("certifications", []))
    )
    languages_section = (
        section_header("Languages", "🗣️")
        + html_list(cv.get("languages", []))
    )
    referees_section = (
        section_header("Referees", "🧑‍💼")
        + html_referees(cv.get("referees", []))
    )

    section_main = f"""
    {profile_section}
    {experience_section}
    {education_section}
    """

    section_side = f"""
    {competencies_section}
    {certifications_section}
    {languages_section}
    {referees_section}
    """

    sidebar_skills = html_list(cv.get('core_competencies', []))
    sidebar_languages = html_list(cv.get('languages', []))
    certifications_html = html_list(cv.get('certifications', []))
    referees_html = html_referees(cv.get('referees', []))

    one_column_css = """
    body {
        font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
        margin: 0;
        background: radial-gradient(circle at 10% 10%, rgba(56,189,248,0.15), transparent 30%),
            radial-gradient(circle at 85% 0%, rgba(236,72,153,0.18), transparent 28%),
            #030712;
        color: #e2e8f0;
        min-height: 100vh;
    }
    body::before {
        content: '';
        position: fixed;
        inset: 0;
        background: linear-gradient(120deg, rgba(15,23,42,0.9), rgba(2,6,23,0.8));
        pointer-events: none;
        z-index: -1;
    }
    .cv {
        max-width: 1040px;
        margin: 32px auto 48px;
        background: rgba(6,11,30,0.85);
        border-radius: 28px;
        padding: 32px;
        box-shadow: 0 30px 60px rgba(2,6,23,0.65), 0 12px 20px rgba(59,130,246,0.25);
        border: 1px solid rgba(59,130,246,0.35);
    }
    .hero {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 32px;
        align-items: center;
        padding: 36px;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(14,165,233,0.25), rgba(79,70,229,0.3));
        border: 1px solid rgba(255,255,255,0.4);
        position: relative;
        overflow: hidden;
    }
    .hero::after {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 30% 20%, rgba(236,72,153,0.4), transparent 45%),
            radial-gradient(circle at 80% 20%, rgba(14,165,233,0.4), transparent 50%),
            radial-gradient(circle at 50% 120%, rgba(59,130,246,0.2), transparent 60%);
        opacity: 0.8;
        pointer-events: none;
    }
    .hero > * {
        position: relative;
        z-index: 1;
    }
    .hero h1 {
        margin: 0;
        font-size: clamp(38px, 4vw, 48px);
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    .hero .headline {
        margin: 14px 0 2px;
        font-size: 17px;
        color: #e0e7ff;
    }
    .hero-meta {
        margin-top: 18px;
        font-size: 14px;
        line-height: 1.6;
        background: rgba(15,23,42,0.65);
        border-radius: 12px;
        padding: 12px 16px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .hero-meta strong {
        color: #bfdbfe;
    }
    .hero-meta a {
        color: #7dd3fc;
        text-decoration: none;
        font-weight: 600;
    }
    .content {
        margin-top: 28px;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 22px;
    }
    .section-block {
        background: rgba(15,23,42,0.7);
        border-radius: 18px;
        padding: 24px;
        border: 1px solid rgba(59,130,246,0.25);
        min-height: 200px;
    }
    .section-block:nth-child(odd) {
        border-color: rgba(236,72,153,0.35);
    }
    p { line-height: 1.7; color: #e2e8f0; }
    .section-heading h2 { color: #f8fafc; }
    ul {
        margin-top: 12px;
        padding-left: 22px;
        color: #e2e8f0;
    }
    li { margin-bottom: 6px; }
    a { color: #38bdf8; }
    @media (max-width: 640px) {
        .cv { padding: 18px; }
        .hero { padding: 24px; grid-template-columns: 1fr; text-align: center; }
    }
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
    .referees-list { margin-top: 10px; padding-left: 0; }
    .referees-list li { margin-bottom: 8px; list-style: none; }
    .referee-contact, .referee-title { display: block; font-size: 12px; color: #475569; }
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
    .referees-list { margin-top: 8px; padding-left: 0; }
    .referees-list li { margin-bottom: 6px; list-style: none; }
    .referee strong { display: block; font-size: 15px; }
    .referee-contact, .referee-title { display: block; font-size: 13px; color: #475569; }
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
    .referees-list { margin-top: 12px; padding-left: 0; }
    .referees-list li { margin-bottom: 10px; list-style: none; }
    .referee strong { display: block; font-size: 15px; }
    .referee-contact, .referee-title { display: block; font-size: 12px; color: #dbeafe; }
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
    .referees-list { margin: 0 0 8px 0; padding-left: 0; }
    .referee { list-style: none; margin-bottom: 10px; }
    .referee strong { display: block; font-size: 15px; }
    .referee-contact, .referee-title { display: block; font-size: 13px; color: #f1f5f9; }
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
    .referees-list { margin-top: 12px; padding-left: 0; }
    .referees-list li { margin-bottom: 10px; list-style: none; }
    .referee strong { display: block; font-size: 15px; }
    .referee-contact, .referee-title { display: block; font-size: 13px; color: #475569; }
    .links-row { margin-top: 14px; font-size: 13px; color: #111827; letter-spacing: 0.4px; }
    .referees-list { margin-top: 18px; padding-left: 0; }
    .referee { list-style: none; margin-bottom: 10px; }
    .referee strong { display: block; font-size: 16px; letter-spacing: 1px; }
    .referee-contact, .referee-title { display: block; font-size: 13px; color: #4b5563; margin-top: 4px; }
    .divider { height: 1px; background: #e2e8f0; margin: 32px 0 18px; }
    """

    shared_section_styles = """
    .section-heading { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
    .section-heading h2 { margin: 0; font-size: 20px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 600; }
    .section-icon { font-size: 20px; }
    .experience-header { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }
    .experience-period { font-size: 13px; color: #475569; }
    .experience-org { font-size: 14px; color: #1f2937; margin-bottom: 6px; }
    .education-entry { padding: 10px 12px; border-left: 3px solid #1d4ed8; margin-bottom: 10px; background: rgba(29,78,216,0.06); border-radius: 4px; }
    .education-top { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; }
    .education-course { display: inline-flex; gap: 6px; }
    .education-timeline { font-size: 12px; color: #475569; }
    .education-institution { font-size: 13px; color: #0f172a; margin-top: 4px; }
    .referee { margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px dashed rgba(15,23,42,0.1); }
    .referee-head { display: flex; flex-direction: column; gap: 2px; }
    .referee-name { font-weight: 600; }
    .referee-org { font-size: 13px; color: #475569; }
    .referee-meta { margin-top: 4px; display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: #1f2937; }
    .referee-field { display: inline-flex; align-items: center; gap: 4px; padding-right: 8px; }
    """

    one_column_css += shared_section_styles
    one_column_minimal_css += shared_section_styles
    two_column_css += shared_section_styles
    two_column_sidebar_css += shared_section_styles
    two_column_sidebar_skillset_css += shared_section_styles
    two_column_accent_css += shared_section_styles
    two_column_slate_css += shared_section_styles

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
        education_html = html_education(cv.get("education", []))
        languages_html = html_list(cv.get("languages", []))
        referees_html = html_referees(cv.get("referees", []))
        links_row = f"<div class='links-row'>{' | '.join(link_items)}</div>" if link_items else ""

        education_section = (
            f"""
            <div class='sidebar-section'>
                <h3>🎓 Education</h3>
                {education_html}
            </div>
            """ if education_html else ""
        )
        skills_section = (
            f"""
            <div class='sidebar-section'>
                <h3>🧠 Skills</h3>
                {skills_html}
            </div>
            """ if skills_html else ""
        )
        tech_section = (
            f"""
            <div class='sidebar-section'>
                <h3>⚙️ Technical Proficiencies</h3>
                {tech_html}
            </div>
            """ if tech_html else ""
        )
        languages_section = (
            f"""
            <div class='sidebar-section'>
                <h3>🗣️ Languages</h3>
                {languages_html}
            </div>
            """ if languages_html else ""
        )
        referees_section = (
            f"""
            <div class='section-body'>
                <h2>Referees</h2>
                {referees_html}
            </div>
            """ if referees_html else ""
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
                        {referees_section}
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
    on_new_page=None,
) -> float:
    pdf.setFont(font_name, font_size)
    for line in wrap_pdf_text(text, font_name, font_size, max_width):
        if y < bottom_margin:
            pdf.showPage()
            y = on_new_page() if callable(on_new_page) else top_reset
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


PDF_SECTION_ICON_FALLBACKS = {
    "Profile": "P",
    "Core Competencies": "C",
    "Professional Experience": "E",
    "Education": "Ed",
    "Certifications": "Cf",
    "Languages": "Lg",
    "Referees": "Rf",
    "Contact": "Ct",
}


def draw_pdf_section_title(
    pdf,
    title: str,
    x: float,
    y: float,
    font_size: int = 12,
    title_color=None,
    line_color=None,
    icon_badge_color=None,
    icon_text_color=None,
) -> float:
    icon = PDF_SECTION_ICON_FALLBACKS.get(title, "")
    title_x = x
    if icon:
        badge_color = icon_badge_color or line_color or colors.HexColor("#BFD7ED")
        text_color = icon_text_color or colors.white
        badge_x = x + 6
        badge_y = y - 2
        pdf.setFillColor(badge_color)
        pdf.circle(badge_x, badge_y, 6, fill=1, stroke=0)
        pdf.setFillColor(text_color)
        pdf.setFont("Helvetica-Bold", 5)
        pdf.drawCentredString(badge_x, badge_y - 2, pdf_safe_text(icon))
        title_x = x + 20

    pdf.setFillColor(title_color or colors.HexColor("#1E3A5F"))
    pdf.setFont("Helvetica-Bold", font_size)
    pdf.drawString(title_x, y, pdf_safe_text(title))
    pdf.setStrokeColor(line_color or colors.HexColor("#BFD7ED"))
    pdf.setLineWidth(1)
    pdf.line(title_x, y - 3, title_x + 130, y - 3)
    return y - 16


def draw_section_card(pdf, x: float, y: float, width: float, height: float, fill: colors.Color, border: colors.Color) -> float:
    pdf.setFillColor(fill)
    pdf.setStrokeColor(border)
    pdf.setLineWidth(1)
    pdf.roundRect(x, y - height, width, height, 12, fill=1, stroke=0)
    pdf.setStrokeColor(border)
    pdf.roundRect(x, y - height, width, height, 12, fill=0, stroke=1)
    return y - height - 14


def ensure_pdf_space(pdf, y: float, needed_height: float, bottom_margin: float, top_reset: float, on_new_page=None) -> float:
    if y - needed_height < bottom_margin:
        pdf.showPage()
        return on_new_page() if callable(on_new_page) else top_reset
    return y


def build_pdf_one_column(cv: dict, theme: dict | None = None) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    theme = theme or get_pdf_theme("One Column - Minimal")
    background = theme.get("background", colors.HexColor("#030712"))
    hero_background = theme.get("hero_background", colors.HexColor("#102a43"))
    hero_accent = theme.get("hero_accent", colors.HexColor("#1e3a8a"))
    hero_strip = theme.get("hero_strip", colors.HexColor("#2563eb"))
    hero_text_color = theme.get("hero_text", colors.white)
    text_color = theme.get("text_color", colors.HexColor("#e2e8f0"))
    link_color = theme.get("link_color", hero_strip)
    panel_primary = theme.get("panel_primary", colors.HexColor("#0f172a"))
    panel_secondary = theme.get("panel_secondary", colors.HexColor("#0f172a"))
    border_color = theme.get("border", colors.HexColor("#1d4ed8"))
    layout_style = theme.get("layout", "classic_hero")
    section_title_color = theme.get(
        "section_title_color",
        colors.HexColor("#1E3A5F") if layout_style == "minimal_clean" else theme.get("hero_strip", colors.HexColor("#2563eb")),
    )
    section_line_color = theme.get(
        "section_line_color",
        colors.HexColor("#BFD7ED") if layout_style == "minimal_clean" else border_color,
    )
    section_icon_badge_color = theme.get("section_icon_badge_color", section_line_color)
    section_icon_text_color = theme.get("section_icon_text_color", colors.white)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 28
    right = width - 28
    content_width = right - left
    top = height - 34
    bottom = 28
    y = top
    on_new_page_callback = None

    if layout_style == "minimal_clean":
        def draw_minimal_frame() -> None:
            pdf.setFillColor(background)
            pdf.rect(0, 0, width, height, fill=1, stroke=0)
            pdf.setFillColor(theme.get("hero_strip", colors.HexColor("#1e3a5f")))
            pdf.rect(left - 18, 0, 4, height, fill=1, stroke=0)

        def on_minimal_new_page() -> float:
            draw_minimal_frame()
            pdf.setFillColor(text_color)
            return top - 6

        draw_minimal_frame()
        pdf.setFillColor(hero_text_color)
        pdf.setFont("Helvetica-Bold", 30)
        pdf.drawString(left, y, pdf_safe_text(cv.get("full_name", "")))
        y -= 34
        pdf.setFont("Helvetica", 17)
        pdf.drawString(left, y, pdf_safe_text(cv.get("headline", "")))
        y -= 28
        pdf.setFillColor(text_color)
        pdf.setFont("Helvetica", 14)
        pdf.drawString(left, y, pdf_safe_text(f"Location: {cv.get('location', '')}"))
        y -= 24
        pdf.drawString(left, y, pdf_safe_text(f"Phone: {cv.get('phone', '')}"))
        y -= 24
        pdf.drawString(left, y, pdf_safe_text(f"Email: {cv.get('email', '')}"))
        y -= 28
        pdf.setFillColor(link_color)
        pdf.setFont("Helvetica", 13)
        pdf.drawString(left, y, pdf_safe_text(f"LinkedIn | GitHub"))
        y -= 24
        pdf.setFillColor(text_color)
        on_new_page_callback = on_minimal_new_page
    else:
        pdf.setFillColor(background)
        pdf.rect(0, 0, width, height, fill=1, stroke=0)
        hero_height = 120
        hero_bottom = y - hero_height
        pdf.setFillColor(hero_background)
        pdf.roundRect(left - 16, hero_bottom - 8, content_width + 32, hero_height + 16, 20, fill=1, stroke=0)
        pdf.setFillColor(hero_accent)
        pdf.rect(left, hero_bottom + hero_height * 0.4, content_width * 0.68, hero_height * 0.5, fill=1, stroke=0)
        pdf.setFillColor(hero_text_color)
        pdf.setFont("Helvetica-Bold", 22)
        pdf.drawString(left + 8, hero_bottom + hero_height - 28, pdf_safe_text(cv.get("full_name", "")))
        pdf.setFont("Helvetica", 12)
        pdf.drawString(left + 8, hero_bottom + hero_height - 48, pdf_safe_text(cv.get("headline", "")))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(right - 160, hero_bottom + hero_height - 28, pdf_safe_text(f"Location: {cv.get('location', '')}"))
        pdf.drawString(right - 160, hero_bottom + hero_height - 44, pdf_safe_text(f"Phone: {cv.get('phone', '')}"))
        pdf.drawString(right - 160, hero_bottom + hero_height - 60, pdf_safe_text(f"Email: {cv.get('email', '')}"))
        y = hero_bottom - 28
        pdf.setFillColor(link_color)
        pdf.drawString(left, y + 8, pdf_safe_text(f"LinkedIn: {cv.get('linkedin', '')} | GitHub: {cv.get('github', '')}"))
        pdf.setFillColor(text_color)
        y -= 16
        pdf.setFillColor(panel_primary)
        pdf.rect(left - 12, bottom - 6, content_width + 24, y - bottom + 24, fill=1, stroke=0)
        pdf.setStrokeColor(border_color)
        pdf.setLineWidth(1)
        pdf.rect(left - 12, bottom - 6, content_width + 24, y - bottom + 24, fill=0, stroke=1)
        y -= 12
        pdf.setFillColor(text_color)

    y = ensure_pdf_space(pdf, y, 40, bottom, top, on_new_page=on_new_page_callback)
    y = draw_pdf_section_title(
        pdf,
        "Profile",
        left,
        y,
        title_color=section_title_color,
        line_color=section_line_color,
        icon_badge_color=section_icon_badge_color,
        icon_text_color=section_icon_text_color,
    )
    pdf.setFillColor(text_color)
    y = draw_pdf_wrapped_text(
        pdf,
        cv.get("profile_summary", ""),
        left,
        y,
        content_width,
        bottom,
        top,
        on_new_page=on_new_page_callback,
    )
    y -= 6

    y = ensure_pdf_space(pdf, y, 40, bottom, top, on_new_page=on_new_page_callback)
    y = draw_pdf_section_title(
        pdf,
        "Core Competencies",
        left,
        y,
        title_color=section_title_color,
        line_color=section_line_color,
        icon_badge_color=section_icon_badge_color,
        icon_text_color=section_icon_text_color,
    )
    pdf.setFillColor(text_color)
    for item in cv.get("core_competencies", []):
        y = draw_pdf_wrapped_text(
            pdf, f"- {item}", left, y, content_width, bottom, top, on_new_page=on_new_page_callback
        )
    y -= 6

    y = ensure_pdf_space(pdf, y, 40, bottom, top, on_new_page=on_new_page_callback)
    y = draw_pdf_section_title(
        pdf,
        "Professional Experience",
        left,
        y,
        title_color=section_title_color,
        line_color=section_line_color,
        icon_badge_color=section_icon_badge_color,
        icon_text_color=section_icon_text_color,
    )
    pdf.setFillColor(text_color)
    for exp in cv.get("experience", []):
        y = ensure_pdf_space(pdf, y, 28, bottom, top, on_new_page=on_new_page_callback)
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
            on_new_page=on_new_page_callback,
        )
        for bullet in exp.get("bullets", []):
            y = draw_pdf_wrapped_text(
                pdf, f"  - {bullet}", left, y, content_width, bottom, top, on_new_page=on_new_page_callback
            )
        y -= 3

    y = ensure_pdf_space(pdf, y, 36, bottom, top, on_new_page=on_new_page_callback)
    y = draw_pdf_section_title(
        pdf,
        "Education",
        left,
        y,
        title_color=section_title_color,
        line_color=section_line_color,
        icon_badge_color=section_icon_badge_color,
        icon_text_color=section_icon_text_color,
    )
    pdf.setFillColor(text_color)
    for item in cv.get("education", []):
        record = normalize_education_record(item)
        course = record.get("course", "")
        institution = record.get("institution", "")
        timeline = record.get("timeline", "")
        line_parts = [part for part in [course, institution] if part]
        if timeline:
            line_parts.append(f"({timeline})")
        entry_line = " - ".join(line_parts) if line_parts else ""
        if entry_line:
            entry_line = f"• {entry_line}"
        y = draw_pdf_wrapped_text(
            pdf, entry_line, left, y, content_width, bottom, top, on_new_page=on_new_page_callback
        )

    y = ensure_pdf_space(pdf, y, 36, bottom, top, on_new_page=on_new_page_callback)
    y = draw_pdf_section_title(
        pdf,
        "Certifications",
        left,
        y,
        title_color=section_title_color,
        line_color=section_line_color,
        icon_badge_color=section_icon_badge_color,
        icon_text_color=section_icon_text_color,
    )
    pdf.setFillColor(text_color)
    for item in cv.get("certifications", []):
        y = draw_pdf_wrapped_text(
            pdf, f"- {item}", left, y, content_width, bottom, top, on_new_page=on_new_page_callback
        )

    y = ensure_pdf_space(pdf, y, 36, bottom, top, on_new_page=on_new_page_callback)
    y = draw_pdf_section_title(
        pdf,
        "Languages",
        left,
        y,
        title_color=section_title_color,
        line_color=section_line_color,
        icon_badge_color=section_icon_badge_color,
        icon_text_color=section_icon_text_color,
    )
    pdf.setFillColor(text_color)
    for item in cv.get("languages", []):
        y = draw_pdf_wrapped_text(
            pdf, f"- {item}", left, y, content_width, bottom, top, on_new_page=on_new_page_callback
        )

    y = ensure_pdf_space(pdf, y, 42, bottom, top, on_new_page=on_new_page_callback)
    y = draw_pdf_section_title(
        pdf,
        "Referees",
        left,
        y,
        title_color=section_title_color,
        line_color=section_line_color,
        icon_badge_color=section_icon_badge_color,
        icon_text_color=section_icon_text_color,
    )
    pdf.setFillColor(text_color)
    for idx, ref in enumerate(cv.get("referees", []), start=1):
        name = ref.get("name", "")
        position = ref.get("position") or ref.get("title", "")
        organization = ref.get("organization", "")
        email = ref.get("email", "")
        phone = ref.get("phone", "")
        parts = [part for part in [name, position, organization] if part]
        ref_summary = " | ".join(parts)
        contact = []
        if email:
            contact.append(f"Email: {email}")
        if phone:
            contact.append(f"Phone: {phone}")
        contact_line = " | ".join(contact)
        full_line = f"{idx}. {ref_summary}" if ref_summary else f"{idx}."
        if contact_line:
            full_line = f"{full_line} | {contact_line}"
        y = draw_pdf_wrapped_text(
            pdf, full_line, left, y, content_width, bottom, top, on_new_page=on_new_page_callback
        )

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def build_pdf_two_column(cv: dict, theme: dict | None = None) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    theme = theme or get_pdf_theme("Two Column - Professional")
    background = theme.get("background", colors.HexColor("#030712"))
    hero_background = theme.get("hero_background", colors.HexColor("#0f172a"))
    hero_accent = theme.get("hero_accent", colors.HexColor("#1e3a8a"))
    hero_strip = theme.get("hero_strip", colors.HexColor("#2563eb"))
    panel_primary = theme.get("panel_primary", colors.HexColor("#f8fafc"))
    panel_secondary = theme.get("panel_secondary", colors.HexColor("#eef2ff"))
    panel_border = theme.get("panel_border", colors.HexColor("#d6e3f2"))
    hero_text_color = theme.get("hero_text", colors.white)
    text_color = theme.get("text_color", colors.black)
    layout_style = theme.get("layout", "modern_header")
    section_title_color = theme.get("section_title_color", colors.HexColor("#1E3A5F"))
    section_line_color = theme.get("section_line_color", colors.HexColor("#BFD7ED"))
    section_icon_badge_color = theme.get("section_icon_badge_color", section_line_color)
    section_icon_text_color = theme.get("section_icon_text_color", colors.white)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFillColor(background)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    margin = 22
    gap = 14
    top = height - 22
    bottom = 28
    total_width = width - (2 * margin)
    left_width = total_width * 0.62
    right_width = total_width - left_width - gap
    left_x = margin
    right_x = left_x + left_width + gap

    def draw_columns(panel_top: float) -> None:
        column_height = panel_top - bottom + 12
        pdf.setFillColor(panel_primary)
        pdf.setStrokeColor(panel_border)
        pdf.setLineWidth(1)
        pdf.roundRect(left_x - 4, bottom - 4, left_width + 8, column_height, 8, fill=1, stroke=1)
        pdf.setFillColor(panel_secondary)
        pdf.roundRect(right_x - 4, bottom - 4, right_width + 8, column_height, 8, fill=1, stroke=1)

    def draw_page_layout(first_page: bool) -> tuple[float, float]:
        pdf.setFillColor(background)
        pdf.rect(0, 0, width, height, fill=1, stroke=0)

        if first_page:
            if layout_style == "professional_header":
                header_height = 112
                header_bottom = top - header_height
                pdf.setFillColor(hero_background)
                pdf.roundRect(left_x - 2, header_bottom, total_width + 4, header_height, 6, fill=1, stroke=0)
                contact_box_height = 76
                contact_box_width = right_width + 10
                contact_box_x = right_x - 2
                contact_box_y = header_bottom + 18
                pdf.setFillColor(hero_accent)
                pdf.roundRect(contact_box_x, contact_box_y, contact_box_width, contact_box_height, 6, fill=1, stroke=0)
                pdf.setStrokeColor(colors.HexColor("#7da0c4"))
                pdf.setLineWidth(0.8)
                pdf.roundRect(contact_box_x, contact_box_y, contact_box_width, contact_box_height, 6, fill=0, stroke=1)

                pdf.setFillColor(hero_text_color)
                pdf.setFont("Helvetica-Bold", 24)
                pdf.drawString(left_x + 10, header_bottom + header_height - 36, pdf_safe_text(cv.get("full_name", "")))
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(left_x + 10, header_bottom + header_height - 58, pdf_safe_text(cv.get("headline", "")))

                pdf.setFont("Helvetica-Bold", 11)
                pdf.drawString(contact_box_x + 8, contact_box_y + contact_box_height - 18, pdf_safe_text("Location:"))
                pdf.setFont("Helvetica", 11)
                pdf.drawString(contact_box_x + 56, contact_box_y + contact_box_height - 18, pdf_safe_text(cv.get("location", "")))
                pdf.setFont("Helvetica-Bold", 11)
                pdf.drawString(contact_box_x + 8, contact_box_y + contact_box_height - 34, pdf_safe_text("Phone:"))
                pdf.setFont("Helvetica", 11)
                pdf.drawString(contact_box_x + 48, contact_box_y + contact_box_height - 34, pdf_safe_text(cv.get("phone", "")))
                pdf.setFont("Helvetica-Bold", 11)
                pdf.drawString(contact_box_x + 8, contact_box_y + contact_box_height - 50, pdf_safe_text("Email:"))
                pdf.setFont("Helvetica", 11)
                pdf.drawString(contact_box_x + 46, contact_box_y + contact_box_height - 50, pdf_safe_text(cv.get("email", "")))

                draw_columns(header_bottom - 10)
                pdf.setFillColor(text_color)
                start_y = header_bottom - 26
                return start_y, start_y

            hero_height = 120
            hero_top = top
            hero_bottom = hero_top - hero_height
            pdf.setFillColor(hero_background)
            pdf.roundRect(left_x - 12, hero_bottom - 10, total_width + 24, hero_height + 20, 20, fill=1, stroke=0)
            pdf.setFillColor(hero_accent)
            pdf.roundRect(left_x + 6, hero_bottom + hero_height * 0.32, total_width * 0.58, hero_height * 0.48, 18, fill=1, stroke=0)
            pdf.setFillColor(hero_strip)
            pdf.roundRect(right_x - 8, hero_bottom + hero_height * 0.58, right_width + 16, hero_height * 0.22, 14, fill=1, stroke=0)
            pdf.setFillColor(hero_text_color)
            pdf.setFont("Helvetica-Bold", 24)
            pdf.drawString(left_x + 12, hero_bottom + hero_height - 28, pdf_safe_text(cv.get("full_name", "")))
            pdf.setFont("Helvetica", 11)
            pdf.drawString(left_x + 12, hero_bottom + hero_height - 50, pdf_safe_text(cv.get("headline", "")))
            pdf.setFont("Helvetica", 8)
            pdf.drawString(right_x + 6, hero_bottom + hero_height - 26, pdf_safe_text(f"Location: {cv.get('location', '')}"))
            pdf.drawString(right_x + 6, hero_bottom + hero_height - 38, pdf_safe_text(f"Phone: {cv.get('phone', '')}"))
            pdf.drawString(right_x + 6, hero_bottom + hero_height - 50, pdf_safe_text(f"Email: {cv.get('email', '')}"))
            pdf.drawString(right_x + 6, hero_bottom + hero_height - 62, pdf_safe_text(f"LinkedIn: {cv.get('linkedin', '')}"))
            pdf.drawString(right_x + 6, hero_bottom + hero_height - 74, pdf_safe_text(f"GitHub: {cv.get('github', '')}"))
            draw_columns(hero_bottom)
            pdf.setFillColor(text_color)
            return hero_bottom - 16, hero_bottom - 24

        ribbon_height = 24
        ribbon_bottom = top - ribbon_height
        pdf.setFillColor(hero_background)
        if layout_style == "professional_header":
            pdf.roundRect(left_x - 2, ribbon_bottom, total_width + 4, ribbon_height, 5, fill=1, stroke=0)
        else:
            pdf.roundRect(left_x - 10, ribbon_bottom, total_width + 20, ribbon_height, 10, fill=1, stroke=0)
        pdf.setFillColor(hero_strip)
        pdf.roundRect(right_x - 4, ribbon_bottom + 5, right_width + 8, ribbon_height - 10, 8, fill=1, stroke=0)
        panel_top = top - 8
        draw_columns(panel_top)
        pdf.setFillColor(text_color)
        start_y = panel_top - 16
        return start_y, start_y

    def add_title_op(ops: list[dict], title: str) -> None:
        ops.append({"kind": "title", "title": title, "height": 16})

    def add_gap_op(ops: list[dict], gap_size: int) -> None:
        if gap_size > 0:
            ops.append({"kind": "gap", "height": gap_size})

    def add_text_ops(
        ops: list[dict],
        text: str,
        max_width: float,
        font_name: str = "Helvetica",
        font_size: int = 10,
        leading: int = 13,
    ) -> None:
        safe_text = pdf_safe_text(text)
        for line in wrap_pdf_text(safe_text, font_name, font_size, max_width):
            ops.append(
                {
                    "kind": "line",
                    "text": line,
                    "font_name": font_name,
                    "font_size": font_size,
                    "leading": leading,
                    "height": leading,
                }
            )

    left_ops: list[dict] = []
    add_title_op(left_ops, "Profile")
    add_text_ops(left_ops, cv.get("profile_summary", ""), left_width, font_name="Helvetica", font_size=10, leading=13)
    add_gap_op(left_ops, 6)

    add_title_op(left_ops, "Professional Experience")
    for exp in cv.get("experience", []):
        add_text_ops(
            left_ops,
            f"{exp.get('role', '')} - {exp.get('organization', '')} | {exp.get('period', '')}",
            left_width,
            font_name="Helvetica-Bold",
            font_size=9,
            leading=12,
        )
        for bullet in exp.get("bullets", []):
            add_text_ops(left_ops, f"- {bullet}", left_width, font_name="Helvetica", font_size=9, leading=12)
        add_gap_op(left_ops, 3)

    add_title_op(left_ops, "Education")
    for item in cv.get("education", []):
        record = normalize_education_record(item)
        course = record.get("course", "")
        institution = record.get("institution", "")
        timeline = record.get("timeline", "")
        parts = [part for part in [course, institution] if part]
        if timeline:
            parts.append(f"({timeline})")
        entry_line = " - ".join(parts) if parts else ""
        if entry_line:
            add_text_ops(left_ops, f"• {entry_line}", left_width, font_name="Helvetica", font_size=10, leading=13)

    right_ops: list[dict] = []
    add_title_op(right_ops, "Contact")
    contact_lines = [
        f"Location: {cv.get('location', '')}",
        f"Phone: {cv.get('phone', '')}",
        f"Email: {cv.get('email', '')}",
        f"LinkedIn: {cv.get('linkedin', '')}",
        f"GitHub: {cv.get('github', '')}",
    ]
    for line in contact_lines:
        add_text_ops(right_ops, line, right_width, font_name="Helvetica", font_size=9, leading=12)
    add_gap_op(right_ops, 6)

    add_title_op(right_ops, "Core Competencies")
    for item in cv.get("core_competencies", []):
        add_text_ops(right_ops, f"- {item}", right_width, font_name="Helvetica", font_size=9, leading=12)
    add_gap_op(right_ops, 4)

    add_title_op(right_ops, "Certifications")
    for item in cv.get("certifications", []):
        add_text_ops(right_ops, f"- {item}", right_width, font_name="Helvetica", font_size=9, leading=12)
    add_gap_op(right_ops, 4)

    add_title_op(right_ops, "Languages")
    for item in cv.get("languages", []):
        add_text_ops(right_ops, f"- {item}", right_width, font_name="Helvetica", font_size=9, leading=12)
    add_gap_op(right_ops, 4)

    add_title_op(right_ops, "Referees")
    for ref in cv.get("referees", []):
        name = ref.get("name", "")
        position = ref.get("position") or ref.get("title", "")
        organization = ref.get("organization", "")
        email = ref.get("email", "")
        phone = ref.get("phone", "")
        parts = [part for part in [name, position, organization] if part]
        summary = " | ".join(parts)
        contacts = []
        if email:
            contacts.append(f"Email: {email}")
        if phone:
            contacts.append(f"Phone: {phone}")
        contact_line = " | ".join(contacts)
        text = f"{summary}" if summary else ""
        if contact_line:
            text = f"{text} | {contact_line}" if text else contact_line
        if text:
            add_text_ops(right_ops, f"- {text}", right_width, font_name="Helvetica", font_size=9, leading=12)

    def render_op(op: dict, x: float, y: float) -> float:
        if op["kind"] == "title":
            return draw_pdf_section_title(
                pdf,
                op["title"],
                x,
                y,
                title_color=section_title_color,
                line_color=section_line_color,
                icon_badge_color=section_icon_badge_color,
                icon_text_color=section_icon_text_color,
            )
        if op["kind"] == "line":
            pdf.setFillColor(text_color)
            pdf.setFont(op["font_name"], op["font_size"])
            pdf.drawString(x, y, op["text"])
            return y - op["leading"]
        return y - op["height"]

    left_index = 0
    right_index = 0
    y_left, y_right = draw_page_layout(first_page=True)

    while left_index < len(left_ops) or right_index < len(right_ops):
        while left_index < len(left_ops):
            op = left_ops[left_index]
            if y_left - op["height"] < bottom:
                break
            y_left = render_op(op, left_x, y_left)
            left_index += 1

        while right_index < len(right_ops):
            op = right_ops[right_index]
            if y_right - op["height"] < bottom:
                break
            y_right = render_op(op, right_x, y_right)
            right_index += 1

        if left_index >= len(left_ops) and right_index >= len(right_ops):
            break

        pdf.showPage()
        y_left, y_right = draw_page_layout(first_page=False)

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def build_pdf(cv: dict, template: str) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    theme = get_pdf_theme(template)
    if "Two Column" in template:
        return build_pdf_two_column(cv, theme)
    return build_pdf_one_column(cv, theme)


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

    profile_summary = rich_text_area(
        "Profile Summary",
        value=cv.get("profile_summary", ""),
        height=140,
    )
    competencies_text = rich_text_area(
        "Core Competencies (one per line)",
        value=list_to_text(cv.get("core_competencies", [])),
        height=160,
    )

    st.caption("Experience format per block: Role || Organization || Period, then bullet lines starting with '-'.")
    experience_text = rich_text_area(
        "Professional Experience",
        value=experience_to_text(cv.get("experience", [])),
        height=260,
    )

    st.caption("Education format: Course || Institution || Timeline")
    education_text = rich_text_area(
        "Education",
        value=education_to_text(cv.get("education", [])),
        height=140,
    )
    certifications_text = rich_text_area(
        "Certifications (one per line)",
        value=list_to_text(cv.get("certifications", [])),
        height=120,
    )
    languages_text = rich_text_area(
        "Languages (one per line)",
        value=list_to_text(cv.get("languages", [])),
        height=90,
    )

    st.caption("Referees format: Name || Organization || Position || Email || Phone")
    referees_text = rich_text_area(
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
        "education": text_to_education(education_text),
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


def download_section(cv: dict, suggested_name: str, template: str) -> None:
    st.subheader("Download CV")
    st.caption(f"Download template: {template}")
    st.caption("Note: PDF export uses a print-safe renderer; complex HTML/CSS glyph icons are converted to fallback markers.")
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

template_mapping_issues = validate_template_mappings()

if "editor_authenticated" not in st.session_state:
    st.session_state["editor_authenticated"] = False

st.sidebar.title("CV Portfolio")
if template_mapping_issues:
    st.sidebar.warning("Template mapping issues detected")
    for issue in template_mapping_issues:
        st.sidebar.caption(f"- {issue}")
page = st.sidebar.radio("Navigation", ["Public View", "Editor"], index=0)

if page == "Public View":
    st.sidebar.info("Public view of the default CV profile.")
    default_version = fetch_default_version()
    if not default_version:
        st.error("No default profile found. Create one in Editor.")
        st.stop()

    template_choice_label = st.selectbox("Display Template", list(DISPLAY_TEMPLATE_OPTIONS.keys()), index=0)
    template_choice = DISPLAY_TEMPLATE_OPTIONS[template_choice_label]
    st.caption(f"Showing default CV: {default_version['version_name']}")
    render_cv_streamlit(default_version["cv"], template_choice)
    st.divider()
    download_section(default_version["cv"], "default_cv", template_choice)

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

    preview_template_label = st.selectbox("Preview Template", list(DISPLAY_TEMPLATE_OPTIONS.keys()), index=0)
    preview_template = DISPLAY_TEMPLATE_OPTIONS[preview_template_label]
    st.subheader("Preview")
    render_cv_streamlit(selected_version["cv"], preview_template)
    st.divider()
    download_section(selected_version["cv"], selected_profile["name"].replace(" ", "_"), preview_template)
    st.divider()
    cv_editor(selected_profile["id"], selected_version)
