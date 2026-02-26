import html
import json
import re
import sqlite3
from datetime import datetime

import streamlit as st

DB_PATH = "cv_portfolio.db"


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
    return sqlite3.connect(DB_PATH)


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

    cur.execute("SELECT COUNT(*) FROM profiles")
    profile_count = cur.fetchone()[0]
    if profile_count == 0:
        now = datetime.utcnow().isoformat()
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


def render_cv_streamlit(cv: dict, layout: str) -> None:
    st.title(cv.get("full_name", ""))
    st.caption(cv.get("headline", ""))

    if layout == "Two Column":
        left, right = st.columns([2, 1])
        with left:
            st.header("Profile")
            st.write(cv.get("profile_summary", ""))

            st.header("Professional Experience")
            for item in cv.get("experience", []):
                title = f"{item.get('role', '')} — {item.get('organization', '')} | {item.get('period', '')}"
                with st.expander(title, expanded=False):
                    for bullet in item.get("bullets", []):
                        st.markdown(f"- {bullet}")

            st.header("Education")
            for item in cv.get("education", []):
                st.markdown(f"- {item}")
        with right:
            st.subheader("Contact")
            st.markdown(f"**Location:** {cv.get('location', '')}")
            st.markdown(f"**Phone:** {cv.get('phone', '')}")
            st.markdown(f"**Email:** {cv.get('email', '')}")

            linkedin = cv.get("linkedin", "").strip()
            github = cv.get("github", "").strip()
            if linkedin:
                st.link_button("LinkedIn", linkedin)
            if github:
                st.link_button("GitHub", github)

            st.subheader("Core Competencies")
            for item in cv.get("core_competencies", []):
                st.markdown(f"- {item}")

            st.subheader("Certifications")
            for item in cv.get("certifications", []):
                st.markdown(f"- {item}")

            st.subheader("Languages")
            for item in cv.get("languages", []):
                st.markdown(f"- {item}")
    else:
        st.markdown(
            f"**Location:** {cv.get('location', '')}  \n"
            f"**Phone:** {cv.get('phone', '')}  \n"
            f"**Email:** {cv.get('email', '')}"
        )
        col1, col2 = st.columns(2)
        with col1:
            if cv.get("linkedin", "").strip():
                st.link_button("LinkedIn", cv.get("linkedin", "").strip())
        with col2:
            if cv.get("github", "").strip():
                st.link_button("GitHub", cv.get("github", "").strip())

        st.header("Profile")
        st.write(cv.get("profile_summary", ""))

        st.header("Core Competencies")
        for item in cv.get("core_competencies", []):
            st.markdown(f"- {item}")

        st.header("Professional Experience")
        for item in cv.get("experience", []):
            title = f"{item.get('role', '')} — {item.get('organization', '')} | {item.get('period', '')}"
            with st.expander(title, expanded=False):
                for bullet in item.get("bullets", []):
                    st.markdown(f"- {bullet}")

        st.header("Education")
        for item in cv.get("education", []):
            st.markdown(f"- {item}")

        st.header("Certifications")
        for item in cv.get("certifications", []):
            st.markdown(f"- {item}")

        st.header("Languages")
        for item in cv.get("languages", []):
            st.markdown(f"- {item}")

    st.header("Referees")
    for index, ref in enumerate(cv.get("referees", []), start=1):
        st.markdown(
            f"{index}. **{ref.get('name', '')}** — {ref.get('title', '')}  \n"
            f"Email: {ref.get('email', '')} | Phone: {ref.get('phone', '')}"
        )


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
    links = (
        f"<p><a href='{html.escape(cv.get('linkedin', ''))}'>LinkedIn</a> | "
        f"<a href='{html.escape(cv.get('github', ''))}'>GitHub</a></p>"
    )

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

    one_column_css = """
    body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 0; padding: 24px; }
    .cv { max-width: 900px; margin: auto; background: white; padding: 28px; border-radius: 8px; }
    h1 { margin-bottom: 4px; }
    h2 { border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-top: 24px; }
    .meta { color: #555; margin-top: -6px; }
    .job { margin-bottom: 16px; }
    """

    one_column_minimal_css = """
    body { font-family: 'Segoe UI', sans-serif; background: #ffffff; margin: 0; padding: 20px; }
    .cv { max-width: 820px; margin: auto; }
    h1 { letter-spacing: 1px; }
    h2 { margin-top: 20px; color: #1f4e79; }
    .meta { color: #6b7280; margin-top: -6px; }
    .job { margin-bottom: 14px; }
    ul { margin-top: 8px; }
    """

    two_column_css = """
    body { font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 24px; }
    .cv { max-width: 1100px; margin: auto; background: white; border-radius: 8px; overflow: hidden; }
    .header { padding: 24px; border-bottom: 1px solid #ddd; }
    .grid { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; padding: 24px; }
    h2 { margin-top: 0; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
    .meta { color: #555; margin-top: -6px; }
    .job { margin-bottom: 14px; }
    """

    two_column_sidebar_css = """
    body { font-family: 'Calibri', sans-serif; margin: 0; background: #eef2f7; padding: 24px; }
    .cv { max-width: 1100px; margin: auto; display: grid; grid-template-columns: 1fr 2fr; background: white; }
    .sidebar { background: #1f2937; color: #f9fafb; padding: 24px; }
    .content { padding: 24px; }
    .sidebar h2 { color: #f9fafb; border-bottom: 1px solid #4b5563; }
    h2 { border-bottom: 1px solid #ddd; padding-bottom: 4px; }
    .meta { color: #555; margin-top: -6px; }
    .job { margin-bottom: 14px; }
    a { color: inherit; }
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
                <div class='header'><h1>{name}</h1><p>{headline}</p>{contact}{links}</div>
                <div class='grid'>
                    <div>{section_main}</div>
                    <div>{section_side}</div>
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

    return f"""
    <html><head><meta charset='UTF-8'><style>{one_column_css}</style></head>
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
        [
            "One Column - Classic",
            "One Column - Minimal",
            "Two Column - Professional",
            "Two Column - Sidebar",
        ],
    )
    html_output = build_html(cv, template)
    filename = f"{suggested_name}_{template.lower().replace(' ', '_')}.html"
    st.download_button(
        "Download as HTML",
        data=html_output,
        file_name=filename,
        mime="text/html",
        use_container_width=True,
    )


st.set_page_config(page_title="CV Portfolio Manager", page_icon="💼", layout="wide")
init_db()

st.sidebar.title("CV Portfolio")
page = st.sidebar.radio("Navigation", ["Visitor Page", "Editor"], index=0)

if page == "Visitor Page":
    st.sidebar.info("Public view of the default CV profile.")
    default_version = fetch_default_version()
    if not default_version:
        st.error("No default profile found. Create one in Editor.")
        st.stop()

    layout_choice = st.selectbox("Display Layout", ["One Column", "Two Column"], index=0)
    st.caption(f"Showing default CV: {default_version['version_name']}")
    render_cv_streamlit(default_version["cv"], layout_choice)
    st.divider()
    download_section(default_version["cv"], "default_cv")

else:
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

    preview_layout = st.selectbox("Preview Layout", ["One Column", "Two Column"], index=0)
    st.subheader("Preview")
    render_cv_streamlit(selected_version["cv"], preview_layout)
    st.divider()
    download_section(selected_version["cv"], selected_profile["name"].replace(" ", "_"))
    st.divider()
    cv_editor(selected_profile["id"], selected_version)
