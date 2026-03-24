import html

import streamlit as st
import streamlit.components.v1 as components

from templates.html_builder import build_html
from templates.pdf_builder import build_pdf
from templates.docx_builder import build_docx, DOCX_AVAILABLE
from utils.pdf_helpers import REPORTLAB_AVAILABLE


def render_cv_streamlit(cv: dict, template: str) -> None:
    st.title(cv.get("full_name", ""))
    st.caption(cv.get("headline", ""))
    st.caption(f"Template: {template}")

    html_output = build_html(cv, template)
    components.html(html_output, height=1600, scrolling=True)


def render_portfolio_landing(cv: dict) -> None:
    full_name = html.escape(cv.get("full_name", ""))
    headline = html.escape(cv.get("headline", ""))
    summary = html.escape(cv.get("profile_summary", ""))
    location = html.escape(cv.get("location", ""))
    email_val = html.escape(cv.get("email", ""))
    phone = html.escape(cv.get("phone", ""))
    linkedin = html.escape(cv.get("linkedin", ""))
    github = html.escape(cv.get("github", ""))

    competencies = cv.get("core_competencies", [])[:4]
    experience = cv.get("experience", [])[:2]

    competency_items = "".join(f"<li>{html.escape(item)}</li>" for item in competencies)
    experience_cards = ""
    for item in experience:
        role = html.escape(item.get("role", ""))
        organization = html.escape(item.get("organization", ""))
        period = html.escape(item.get("period", ""))
        experience_cards += f"""
        <div class='pf-job'>
            <h4>{role}</h4>
            <p>{organization}</p>
            <span>{period}</span>
        </div>
        """

    landing_html = f"""
    <style>
        .pf-wrap {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(160deg, #0f172a, #1e3a5f);
            color: #f8fafc;
            border-radius: 16px;
            padding: 28px;
        }}
        .pf-hero {{ display: grid; grid-template-columns: 1.7fr 1fr; gap: 20px; align-items: start; }}
        .pf-name {{ margin: 0; font-size: 42px; letter-spacing: 0.5px; }}
        .pf-headline {{ margin: 10px 0 0; font-size: 24px; color: #dbeafe; }}
        .pf-summary {{ margin-top: 18px; line-height: 1.6; color: #e2e8f0; }}
        .pf-contact {{ background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.24); border-radius: 10px; padding: 14px; }}
        .pf-contact p {{ margin: 0 0 7px 0; }}
        .pf-contact a {{ color: #bfdbfe; text-decoration: none; }}
        .pf-grid {{ margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
        .pf-card {{ background: rgba(255,255,255,0.09); border: 1px solid rgba(148,163,184,0.35); border-radius: 10px; padding: 14px; }}
        .pf-card h3 {{ margin: 0 0 10px 0; color: #bfdbfe; letter-spacing: 0.6px; text-transform: uppercase; font-size: 14px; }}
        .pf-card ul {{ margin: 0; padding-left: 18px; }}
        .pf-card li {{ margin-bottom: 6px; }}
        .pf-job {{ margin-bottom: 10px; }}
        .pf-job h4 {{ margin: 0; color: #ffffff; }}
        .pf-job p {{ margin: 3px 0; color: #dbeafe; }}
        .pf-job span {{ font-size: 12px; color: #93c5fd; }}
        @media (max-width: 900px) {{
            .pf-hero, .pf-grid {{ grid-template-columns: 1fr; }}
            .pf-name {{ font-size: 32px; }}
        }}
    </style>
    <div class='pf-wrap'>
        <div class='pf-hero'>
            <div>
                <h1 class='pf-name'>{full_name}</h1>
                <h2 class='pf-headline'>{headline}</h2>
                <p class='pf-summary'>{summary}</p>
            </div>
            <div class='pf-contact'>
                <p><strong>Location:</strong> {location}</p>
                <p><strong>Phone:</strong> {phone}</p>
                <p><strong>Email:</strong> {email_val}</p>
                <p><a href='{linkedin}' target='_blank'>LinkedIn</a> | <a href='{github}' target='_blank'>GitHub</a></p>
            </div>
        </div>
        <div class='pf-grid'>
            <div class='pf-card'>
                <h3>Core Strengths</h3>
                <ul>{competency_items}</ul>
            </div>
            <div class='pf-card'>
                <h3>Recent Experience</h3>
                {experience_cards}
            </div>
        </div>
    </div>
    """

    st.components.v1.html(landing_html, height=700, scrolling=False)


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
