import os
import sys

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from db import init_db
from db.cv_versions import fetch_default_version
from templates.themes import DISPLAY_TEMPLATE_OPTIONS, validate_template_mappings
from views.public_view import render_portfolio_landing, render_cv_streamlit, download_section
from views.editor import render_editor_login, render_editor_page
from views.cover_letter_page import render_cover_letter_formatter


def _run_with_streamlit_if_needed() -> None:
    if get_script_run_ctx(suppress_warning=True) is not None:
        return

    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", os.path.abspath(__file__), *sys.argv[1:]]
    sys.exit(stcli.main())


if __name__ == "__main__":
    _run_with_streamlit_if_needed()


st.set_page_config(
    page_title="Boniface Ngila | Technology Portfolio",
    page_icon="\U0001f4bc",
    layout="wide",
    initial_sidebar_state="collapsed",
)
init_db()

template_mapping_issues = validate_template_mappings()

if "editor_authenticated" not in st.session_state:
    st.session_state["editor_authenticated"] = False

st.markdown(
    """
    <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"],
        [data-testid="stToolbar"], #MainMenu, footer:not(.portfolio-footer) {
            display: none;
        }
        .block-container {
            max-width: 100%;
            padding: 0;
        }
        header[data-testid="stHeader"] {
            background: transparent;
        }
        div[data-testid="stDecoration"] {
            display: none;
        }
        .admin-shell {
            max-width: 1180px;
            margin: 0 auto;
            padding: 34px 24px 60px;
        }
        .admin-shell h1 {
            margin-bottom: 4px;
        }
        .portfolio-footer {
            border-top: 1px solid #1d3440;
            background: #081116;
            color: #9fb3bd;
            display: flex;
            justify-content: space-between;
            gap: 18px;
            padding: 18px 28px;
            font: 13px Inter, "Segoe UI", Arial, sans-serif;
        }
        .portfolio-footer a {
            color: #55e6d0;
            text-decoration: none;
            font-weight: 700;
        }
        @media (max-width: 700px) {
            .portfolio-footer {
                display: block;
            }
            .portfolio-footer span {
                display: block;
                margin-bottom: 8px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

admin_mode = st.query_params.get("admin", "0") == "1"
default_version = fetch_default_version()
if not default_version:
    st.error("No default profile found. Open admin and create one in the editor.")
    st.stop()

if not admin_mode:
    render_portfolio_landing(default_version["cv"])
    st.markdown(
        """
        <footer class="portfolio-footer">
            <span>Boniface Mutisya Ngila | Technology Portfolio</span>
            <a href="?admin=1" target="_self">Admin</a>
        </footer>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown('<div class="admin-shell">', unsafe_allow_html=True)
st.title("Portfolio Admin")
st.caption("Management tools are hidden from the public portfolio and available here only.")

if template_mapping_issues:
    with st.expander("Template mapping issues", expanded=True):
        for issue in template_mapping_issues:
            st.warning(issue)

st.link_button("Back to Portfolio", "/", use_container_width=False)

downloads_tab, cover_letter_tab, editor_tab = st.tabs(["CV Downloads", "Cover Letter", "Editor"])

with downloads_tab:
    st.subheader("Download Default CV")
    template_choice_label = st.selectbox(
        "Template for CV Download", list(DISPLAY_TEMPLATE_OPTIONS.keys()), index=0
    )
    template_choice = DISPLAY_TEMPLATE_OPTIONS[template_choice_label]
    download_section(default_version["cv"], "default_cv", template_choice)

    with st.expander("Preview selected template"):
        render_cv_streamlit(default_version["cv"], template_choice)

with cover_letter_tab:
    render_cover_letter_formatter()

with editor_tab:
    if not st.session_state.get("editor_authenticated", False):
        render_editor_login()
    else:
        if st.button("Logout", use_container_width=True):
            st.session_state["editor_authenticated"] = False
            st.rerun()
        render_editor_page()

st.markdown("</div>", unsafe_allow_html=True)
