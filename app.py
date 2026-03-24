import streamlit as st

from db import init_db
from db.cv_versions import fetch_default_version
from templates.themes import DISPLAY_TEMPLATE_OPTIONS, validate_template_mappings
from views.public_view import render_portfolio_landing, render_cv_streamlit, download_section
from views.editor import render_editor_login, render_editor_page
from views.cover_letter_page import render_cover_letter_formatter


st.set_page_config(page_title="CV Portfolio Manager", page_icon="\U0001f4bc", layout="wide")
init_db()

template_mapping_issues = validate_template_mappings()

if "editor_authenticated" not in st.session_state:
    st.session_state["editor_authenticated"] = False

st.sidebar.title("CV Portfolio")
if template_mapping_issues:
    st.sidebar.warning("Template mapping issues detected")
    for issue in template_mapping_issues:
        st.sidebar.caption(f"- {issue}")

page = st.sidebar.radio("Navigation", ["Public View", "Cover Letter", "Editor"], index=0)

if page == "Public View":
    st.sidebar.info("Public view of the default CV profile.")
    default_version = fetch_default_version()
    if not default_version:
        st.error("No default profile found. Create one in Editor.")
        st.stop()

    st.caption(f"Portfolio landing: {default_version['version_name']}")
    render_portfolio_landing(default_version["cv"])
    st.divider()

    template_choice_label = st.selectbox(
        "Template for CV Download", list(DISPLAY_TEMPLATE_OPTIONS.keys()), index=0
    )
    template_choice = DISPLAY_TEMPLATE_OPTIONS[template_choice_label]
    download_section(default_version["cv"], "default_cv", template_choice)

    with st.expander("Preview selected template"):
        render_cv_streamlit(default_version["cv"], template_choice)

elif page == "Cover Letter":
    st.sidebar.info("Format, save versions, and download cover letters.")
    render_cover_letter_formatter()

else:
    if not st.session_state.get("editor_authenticated", False):
        st.sidebar.warning("Login required for editor access.")
        render_editor_login()
        st.stop()

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state["editor_authenticated"] = False
        st.rerun()

    st.sidebar.info("Create, edit, and version multiple CV profiles.")
    render_editor_page()
