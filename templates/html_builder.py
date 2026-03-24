import html

from utils.html_helpers import html_list, html_experience, html_education, html_projects, html_referees, section_header
from utils.converters import normalize_education_record


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

    profile_section = section_header("Profile") + f"<p>{profile}</p>"
    experience_section = section_header("Professional Experience") + html_experience(cv.get("experience", []))
    education_section = section_header("Education") + html_education(cv.get("education", []))
    competencies_section = section_header("Core Competencies") + html_list(cv.get("core_competencies", []))
    certifications_section = section_header("Certifications") + html_list(cv.get("certifications", []))
    projects_section = section_header("Projects") + html_projects(cv.get("projects", []))
    languages_section = section_header("Languages") + html_list(cv.get("languages", []))
    referees_section = section_header("Referees") + html_referees(cv.get("referees", []))

    section_main = f"""
    {profile_section}
    {experience_section}
    {projects_section}
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
    .project-entry { margin-bottom: 10px; padding: 8px 12px; border-left: 3px solid #2563eb; background: rgba(37,99,235,0.04); border-radius: 4px; }
    .project-entry h4 { margin: 0 0 4px 0; font-size: 14px; }
    .project-entry p { margin: 2px 0; font-size: 13px; color: #334155; }
    .project-tech { font-size: 12px; color: #64748b; font-style: italic; margin-top: 4px; }
    .project-entry a { font-size: 12px; color: #2563eb; }
    .job p, .job li, .section-block p, .section-block li, .main-panel p, .main-panel li,
    .side-panel p, .side-panel li, .content p, .content li, .main-area p, .main-area li,
    .summary { text-align: justify; text-justify: inter-word; }
    """

    one_column_css = _one_column_classic_css() + shared_section_styles
    one_column_minimal_css = _one_column_minimal_css() + shared_section_styles
    two_column_css = _two_column_professional_css() + shared_section_styles
    two_column_sidebar_css = _two_column_sidebar_css() + shared_section_styles
    two_column_sidebar_skillset_css = _two_column_sidebar_skillset_css() + shared_section_styles
    two_column_accent_css = _two_column_accent_css() + shared_section_styles
    two_column_slate_css = _two_column_slate_css() + shared_section_styles

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
        education_html_content = html_education(cv.get("education", []))
        languages_html = html_list(cv.get("languages", []))
        referees_html_content = html_referees(cv.get("referees", []))
        projects_html = html_projects(cv.get("projects", []))
        links_row = f"<div class='links-row'>{' | '.join(link_items)}</div>" if link_items else ""

        education_sec = (
            f"<div class='sidebar-section'><h3>Education</h3>{education_html_content}</div>"
            if education_html_content else ""
        )
        skills_sec = (
            f"<div class='sidebar-section'><h3>Skills</h3>{skills_html}</div>"
            if skills_html else ""
        )
        tech_sec = (
            f"<div class='sidebar-section'><h3>Technical Proficiencies</h3>{tech_html}</div>"
            if tech_html else ""
        )
        languages_sec = (
            f"<div class='sidebar-section'><h3>Languages</h3>{languages_html}</div>"
            if languages_html else ""
        )
        referees_sec = (
            f"<div class='section-body'><h2>Referees</h2>{referees_html_content}</div>"
            if referees_html_content else ""
        )
        projects_sec = (
            f"<div class='section-body'><h2>Projects</h2>{projects_html}</div>"
            if projects_html else ""
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
                        {education_sec}
                        {skills_sec}
                        {tech_sec}
                        {languages_sec}
                    </aside>
                    <div class='main-area'>
                        <div class='summary'>
                            <p>{profile}</p>
                        </div>
                        <div class='section-body'>
                            <h2>Work Experience</h2>
                            {html_experience(cv.get('experience', []))}
                        </div>
                        {projects_sec}
                        <div class='divider'></div>
                        <div class='section-body'>
                            <h2>Courses and Certificates</h2>
                            {html_list(cv.get('certifications', []))}
                        </div>
                        {referees_sec}
                    </div>
                </div>
            </div>
        </body></html>
        """

    # Default: One Column - Classic
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


# ---------------------------------------------------------------------------
# CSS template functions
# ---------------------------------------------------------------------------

def _one_column_classic_css() -> str:
    return """
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


def _one_column_minimal_css() -> str:
    return """
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


def _two_column_professional_css() -> str:
    return """
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


def _two_column_sidebar_css() -> str:
    return """
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


def _two_column_sidebar_skillset_css() -> str:
    return """
    body { font-family: 'Inter', 'Segoe UI', sans-serif; margin: 0; background: #f0f2f5; padding: 32px; color: #0f172a; }
    .cv { max-width: 1120px; margin: auto; background: #ffffff; display: grid; grid-template-columns: 0.95fr 1.7fr; border-radius: 18px; box-shadow: 0 18px 40px rgba(15,23,42,0.18); overflow: hidden; }
    .sidebar { background: linear-gradient(180deg, #0f172a, #1f2937); color: #f8fafc; padding: 36px 32px; display: flex; flex-direction: column; gap: 14px; min-height: 420px; }
    .sidebar h1 {
        margin: 0;
        font-size: clamp(28px, 3vw, 34px);
        line-height: 1.15;
        letter-spacing: 0.5px;
        overflow-wrap: anywhere;
        word-break: break-word;
    }
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


def _two_column_accent_css() -> str:
    return """
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


def _two_column_slate_css() -> str:
    return """
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
