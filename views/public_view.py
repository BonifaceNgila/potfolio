import base64
import html
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from templates.html_builder import build_html
from templates.pdf_builder import build_pdf
from templates.docx_builder import build_docx, DOCX_AVAILABLE
from utils.pdf_helpers import REPORTLAB_AVAILABLE


def _clean_text(value: object) -> str:
    text = str(value or "")
    replacements = {
        "â€“": "-",
        "â€”": "-",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def _e(value: object) -> str:
    return html.escape(_clean_text(value))


def _asset_data_uri(filename: str) -> str:
    path = Path(__file__).resolve().parents[1] / "assets" / filename
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_cv_streamlit(cv: dict, template: str) -> None:
    st.title(cv.get("full_name", ""))
    st.caption(cv.get("headline", ""))
    st.caption(f"Template: {template}")

    html_output = build_html(cv, template)
    components.html(html_output, height=1600, scrolling=True)


def render_portfolio_landing(cv: dict) -> None:
    full_name = _e(cv.get("full_name", ""))
    headline = _e(cv.get("headline", ""))
    summary = _e(cv.get("profile_summary", ""))
    location = _e(cv.get("location", ""))
    email_val = _e(cv.get("email", ""))
    phone = _e(cv.get("phone", ""))
    linkedin = _e(cv.get("linkedin", ""))
    github = _e(cv.get("github", ""))
    hero_uri = _asset_data_uri("portfolio-hero.png")

    competencies = [_clean_text(item) for item in cv.get("core_competencies", [])]
    experience = cv.get("experience", [])
    education = cv.get("education", [])
    certifications = cv.get("certifications", [])
    projects = cv.get("projects", [])
    languages = cv.get("languages", [])

    role_cards = [
        (
            "IAM & Access Governance",
            "Identity lifecycle, SSO, MFA, Active Directory, Entra ID concepts, OKTA, OCI IAM, access troubleshooting.",
        ),
        (
            "IT Operations Leadership",
            "Infrastructure availability, endpoint support, incident queues, documentation, onboarding, and user enablement.",
        ),
        (
            "Cloud & DevOps Support",
            "Microsoft 365, Oracle Cloud, AWS exposure, PowerShell/Bash/Python automation, reporting, and operational improvement.",
        ),
        (
            "Security & Compliance",
            "Endpoint security, secure authentication, policy adherence, disaster recovery awareness, and data protection training.",
        ),
    ]
    role_cards_html = "".join(
        f"""
        <article class='role-card'>
            <h3>{_e(title)}</h3>
            <p>{_e(body)}</p>
        </article>
        """
        for title, body in role_cards
    )

    stats = [
        ("4+ years", "IT service delivery across NGO operations"),
        ("3 roles", "progressive growth at Plan International Kenya"),
        (str(len(certifications)), "professional certifications and courses"),
        (str(len(projects)), "portfolio projects and operational tools"),
    ]
    stats_html = "".join(
        f"<div class='stat'><strong>{_e(value)}</strong><span>{_e(label)}</span></div>"
        for value, label in stats
    )

    skills_html = "".join(f"<li>{_e(item)}</li>" for item in competencies[:8])

    experience_html = ""
    for item in experience[:3]:
        bullets = "".join(f"<li>{_e(bullet)}</li>" for bullet in item.get("bullets", [])[:4])
        experience_html += f"""
        <article class='timeline-item'>
            <div>
                <span>{_e(item.get("period", ""))}</span>
                <h3>{_e(item.get("role", ""))}</h3>
                <p>{_e(item.get("organization", ""))}</p>
            </div>
            <ul>{bullets}</ul>
        </article>
        """

    project_html = ""
    for item in projects[:4]:
        tech = _e(item.get("technologies", ""))
        project_html += f"""
        <article class='project-card'>
            <h3>{_e(item.get("name", ""))}</h3>
            <p>{_e(item.get("description", ""))}</p>
            <span>{tech}</span>
        </article>
        """

    education_html = "".join(
        f"""
        <article class='proof-item'>
            <h3>{_e(item.get("course", ""))}</h3>
            <p>{_e(item.get("institution", ""))}</p>
            <span>{_e(item.get("timeline", ""))}</span>
        </article>
        """
        for item in education
    )
    certification_html = "".join(f"<li>{_e(item)}</li>" for item in certifications)
    language_html = " | ".join(_e(item) for item in languages)
    link_html = ""
    if linkedin:
        link_html += f"<a href='{linkedin}' target='_blank' rel='noreferrer'>LinkedIn</a>"
    if github:
        link_html += f"<a href='{github}' target='_blank' rel='noreferrer'>GitHub</a>"

    landing_html = f"""
    <style>
        :root {{
            color-scheme: light;
        }}
        .pf-wrap, .pf-wrap * {{
            box-sizing: border-box;
        }}
        .pf-wrap {{
            font-family: Inter, 'Segoe UI', Arial, sans-serif;
            background: #f7f8fb;
            color: #17202a;
            line-height: 1.55;
        }}
        .pf-wrap a {{
            color: inherit;
            text-decoration: none;
        }}
        .pf-hero {{
            min-height: 660px;
            padding: 44px;
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(340px, 0.85fr);
            gap: 36px;
            align-items: end;
            color: #ffffff;
            background:
                linear-gradient(90deg, rgba(9, 16, 25, 0.96) 0%, rgba(9, 16, 25, 0.82) 48%, rgba(9, 16, 25, 0.36) 100%),
                url('{hero_uri}');
            background-size: cover;
            background-position: center;
            border-radius: 8px;
            overflow: hidden;
        }}
        .eyebrow {{
            margin: 0 0 14px;
            color: #f4b35d;
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 0;
            text-transform: uppercase;
        }}
        .pf-name {{
            margin: 0;
            max-width: 780px;
            font-size: 58px;
            line-height: 1.02;
            letter-spacing: 0;
        }}
        .pf-headline {{
            margin: 18px 0 0;
            max-width: 740px;
            font-size: 22px;
            color: #d7f6f1;
            font-weight: 650;
        }}
        .pf-summary {{
            margin: 20px 0 0;
            max-width: 760px;
            color: #e8eef4;
            font-size: 16px;
        }}
        .pf-actions {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 28px;
        }}
        .pf-button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 44px;
            padding: 0 16px;
            border-radius: 6px;
            border: 1px solid rgba(255,255,255,0.34);
            background: rgba(255,255,255,0.1);
            color: #ffffff;
            font-weight: 800;
        }}
        .pf-button.primary {{
            background: #22b8a0;
            border-color: #22b8a0;
            color: #07141a;
        }}
        .contact-panel {{
            align-self: stretch;
            display: flex;
            flex-direction: column;
            justify-content: end;
            gap: 16px;
        }}
        .contact-box {{
            padding: 18px;
            border: 1px solid rgba(255,255,255,0.22);
            border-radius: 8px;
            background: rgba(7, 20, 26, 0.74);
            backdrop-filter: blur(14px);
        }}
        .contact-box span {{
            display: block;
            color: #9fb3c8;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .contact-box p {{
            margin: 0 0 12px;
            overflow-wrap: anywhere;
        }}
        .contact-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            color: #bff4ea;
            font-weight: 800;
        }}
        .stats-band {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background: #dbe3ea;
            border-radius: 8px;
            overflow: hidden;
            margin-top: 18px;
        }}
        .stat {{
            min-height: 112px;
            padding: 20px;
            background: #ffffff;
        }}
        .stat strong {{
            display: block;
            color: #0b5964;
            font-size: 30px;
            line-height: 1;
            margin-bottom: 8px;
        }}
        .stat span {{
            color: #536271;
            font-size: 14px;
        }}
        .section {{
            padding: 44px 36px;
        }}
        .section.alt {{
            background: #ffffff;
        }}
        .section-head {{
            display: flex;
            justify-content: space-between;
            gap: 20px;
            align-items: end;
            margin-bottom: 22px;
        }}
        .section-head h2 {{
            margin: 0;
            font-size: 30px;
            color: #111827;
            letter-spacing: 0;
        }}
        .section-head p {{
            margin: 0;
            max-width: 540px;
            color: #5d6a78;
        }}
        .roles-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
        }}
        .role-card, .project-card, .proof-item {{
            border: 1px solid #dce4eb;
            border-radius: 8px;
            background: #ffffff;
            padding: 18px;
        }}
        .role-card h3, .project-card h3, .proof-item h3 {{
            margin: 0 0 10px;
            font-size: 18px;
            color: #101820;
        }}
        .role-card p, .project-card p, .proof-item p {{
            margin: 0;
            color: #536271;
        }}
        .evidence-grid {{
            display: grid;
            grid-template-columns: minmax(0, 1.25fr) minmax(300px, 0.75fr);
            gap: 18px;
            align-items: start;
        }}
        .timeline {{
            display: grid;
            gap: 14px;
        }}
        .timeline-item {{
            display: grid;
            grid-template-columns: 0.42fr 1fr;
            gap: 18px;
            padding: 20px;
            background: #ffffff;
            border: 1px solid #dce4eb;
            border-left: 5px solid #22b8a0;
            border-radius: 8px;
        }}
        .timeline-item span, .project-card span, .proof-item span {{
            color: #b36b18;
            font-size: 13px;
            font-weight: 800;
        }}
        .timeline-item h3 {{
            margin: 6px 0 4px;
            color: #111827;
        }}
        .timeline-item p {{
            margin: 0;
            color: #536271;
        }}
        .timeline-item ul, .skills-panel ul, .cert-list {{
            margin: 0;
            padding-left: 20px;
        }}
        .timeline-item li, .skills-panel li, .cert-list li {{
            margin-bottom: 8px;
            color: #374151;
        }}
        .skills-panel {{
            padding: 22px;
            border-radius: 8px;
            background: #101820;
            color: #ffffff;
        }}
        .skills-panel h3 {{
            margin: 0 0 14px;
            color: #f4b35d;
            font-size: 18px;
        }}
        .skills-panel li {{
            color: #e5edf4;
        }}
        .projects-grid, .proof-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
        }}
        .project-card {{
            background: #f7f8fb;
        }}
        .proof-wrap {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(280px, 0.72fr);
            gap: 18px;
        }}
        .proof-grid {{
            grid-template-columns: 1fr;
        }}
        .cert-panel {{
            padding: 22px;
            border-radius: 8px;
            background: #fff7ed;
            border: 1px solid #fed7aa;
        }}
        .cert-panel h3 {{
            margin: 0 0 14px;
            color: #7c3f10;
        }}
        .closing-band {{
            padding: 32px 36px;
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 18px;
            align-items: center;
            color: #ffffff;
            background: #0f2f35;
            border-radius: 8px;
        }}
        .closing-band h2 {{
            margin: 0 0 6px;
            font-size: 26px;
        }}
        .closing-band p {{
            margin: 0;
            color: #d6ebe7;
        }}
        .language-line {{
            margin-top: 16px;
            color: #42505f;
            font-weight: 700;
        }}
        @media (max-width: 900px) {{
            .pf-hero,
            .evidence-grid,
            .proof-wrap,
            .closing-band {{
                grid-template-columns: 1fr;
            }}
            .stats-band,
            .roles-grid,
            .projects-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .section-head {{
                display: block;
            }}
            .pf-name {{
                font-size: 42px;
            }}
            .timeline-item {{
                grid-template-columns: 1fr;
            }}
        }}
        @media (max-width: 560px) {{
            .pf-hero,
            .section,
            .closing-band {{
                padding: 24px;
            }}
            .pf-name {{
                font-size: 34px;
            }}
            .stats-band,
            .roles-grid,
            .projects-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
    <div class='pf-wrap'>
        <div class='pf-hero'>
            <div>
                <p class='eyebrow'>Portfolio for IT, IAM, Cloud, Security, and Service Delivery Roles</p>
                <h1 class='pf-name'>{full_name}</h1>
                <h2 class='pf-headline'>{headline}</h2>
                <p class='pf-summary'>{summary}</p>
                <div class='pf-actions'>
                    <a class='pf-button primary' href='mailto:{email_val}'>Contact Me</a>
                    <a class='pf-button' href='{linkedin}' target='_blank' rel='noreferrer'>View LinkedIn</a>
                    <a class='pf-button' href='{github}' target='_blank' rel='noreferrer'>View GitHub</a>
                </div>
            </div>
            <div class='contact-panel'>
                <div class='contact-box'>
                    <span>Location</span>
                    <p>{location}</p>
                    <span>Phone</span>
                    <p>{phone}</p>
                    <span>Email</span>
                    <p>{email_val}</p>
                    <div class='contact-links'>{link_html}</div>
                </div>
            </div>
        </div>

        <div class='stats-band'>{stats_html}</div>

        <section class='section'>
            <div class='section-head'>
                <h2>Role Fit</h2>
                <p>Positioning drawn from your CV, academic path, certifications, projects, and progressive IT support experience.</p>
            </div>
            <div class='roles-grid'>{role_cards_html}</div>
        </section>

        <section class='section alt'>
            <div class='section-head'>
                <h2>Experience Evidence</h2>
                <p>Recent roles show delivery across infrastructure operations, access management, user support, governance, and service improvement.</p>
            </div>
            <div class='evidence-grid'>
                <div class='timeline'>{experience_html}</div>
                <aside class='skills-panel'>
                    <h3>Core Capability Stack</h3>
                    <ul>{skills_html}</ul>
                </aside>
            </div>
        </section>

        <section class='section'>
            <div class='section-head'>
                <h2>Projects</h2>
                <p>Practical builds and operational tools that show capacity to automate, report, document, and deliver usable systems.</p>
            </div>
            <div class='projects-grid'>{project_html}</div>
        </section>

        <section class='section alt'>
            <div class='section-head'>
                <h2>Academic & Professional Proof</h2>
                <p>Formal education and certifications supporting technical breadth, security awareness, cloud capability, and ongoing growth.</p>
            </div>
            <div class='proof-wrap'>
                <div class='proof-grid'>{education_html}</div>
                <aside class='cert-panel'>
                    <h3>Certifications & Courses</h3>
                    <ul class='cert-list'>{certification_html}</ul>
                    <p class='language-line'>Languages: {language_html}</p>
                </aside>
            </div>
        </section>

        <section class='closing-band'>
            <div>
                <h2>Available for roles where secure, reliable IT delivery matters.</h2>
                <p>Best matched to IAM, IT operations, cloud support, service desk coordination, systems administration, and security-focused technology roles.</p>
            </div>
            <a class='pf-button primary' href='mailto:{email_val}'>Start a Conversation</a>
        </section>
    </div>
    """

    st.components.v1.html(landing_html, height=3100, scrolling=True)


def download_section(cv: dict, suggested_name: str, template: str) -> None:
    st.subheader("Download CV")
    st.caption(f"Download template: {template}")
    st.caption("Note: PDF export uses a print-safe renderer; complex HTML/CSS glyph icons are converted to fallback markers.")
    html_output = build_html(cv, template)
    pdf_output = build_pdf(cv, template) if REPORTLAB_AVAILABLE else b""
    docx_output = build_docx(cv, template) if DOCX_AVAILABLE else b""
    slug = template.lower().replace(" ", "_").replace("-", "")
    html_filename = f"{suggested_name}_{slug}.html"
    pdf_filename = f"{suggested_name}_{slug}.pdf"
    docx_filename = f"{suggested_name}_{slug}.docx"

    col_html, col_pdf, col_docx = st.columns(3)
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
    with col_docx:
        if DOCX_AVAILABLE:
            st.download_button(
                "Download as Word",
                data=docx_output,
                file_name=docx_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        else:
            st.button("Download as Word", disabled=True, use_container_width=True)
            st.caption("Word export unavailable: install `python-docx` from requirements.")
