import re

import streamlit as st
import streamlit.components.v1 as components

from db.profiles import fetch_profiles
from db.cv_versions import fetch_versions, fetch_version
from db.cover_letters import (
    fetch_cover_letter_versions, fetch_cover_letter_version,
    save_cover_letter_version, create_cover_letter_version,
    delete_cover_letter_version,
)
from templates.cover_letter_builder import (
    build_cover_letter_html, build_cover_letter_text, build_cover_letter_docx,
    default_cover_letter_data,
)
from templates.docx_builder import DOCX_AVAILABLE
from utils.widgets import rich_text_area


def cover_letter_download_section(letter_data: dict, suggested_name: str) -> None:
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", suggested_name.strip()) or "cover_letter"
    html_output = build_cover_letter_html(letter_data)
    text_output = build_cover_letter_text(letter_data)
    docx_output = build_cover_letter_docx(letter_data) if DOCX_AVAILABLE else b""

    col_html, col_txt, col_docx = st.columns(3)
    with col_html:
        st.download_button(
            "Download as HTML",
            data=html_output,
            file_name=f"{safe_name}.html",
            mime="text/html",
            use_container_width=True,
        )
    with col_txt:
        st.download_button(
            "Download as TXT",
            data=text_output,
            file_name=f"{safe_name}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with col_docx:
        if DOCX_AVAILABLE:
            st.download_button(
                "Download as Word",
                data=docx_output,
                file_name=f"{safe_name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        else:
            st.button("Download as Word", disabled=True, use_container_width=True)
            st.caption("Word export unavailable: install `python-docx` from requirements.")


def render_cover_letter_formatter() -> None:
    st.title("Cover Letter Formatter")
    st.caption("Create, save, and download versioned cover letters per profile.")

    profiles = fetch_profiles()
    if not profiles:
        st.error("No profiles available. Create one in the Editor first.")
        return

    profile_options = {f"{p['name']}{' (Default)' if p['is_default'] else ''}": p for p in profiles}
    selected_profile_label = st.selectbox("Profile", list(profile_options.keys()), key="cover_profile_select")
    selected_profile = profile_options[selected_profile_label]

    cv_versions = fetch_versions(selected_profile["id"])
    if not cv_versions:
        st.error("No CV versions found for this profile.")
        return

    cv_version_options = {
        f"{v['version_name']} ({v['updated_at'][:19]})": v for v in cv_versions
    }
    selected_cv_label = st.selectbox(
        "Fetch Sender's Address from CV Version",
        list(cv_version_options.keys()),
        key="cover_cv_version_select",
    )
    selected_cv_version = cv_version_options[selected_cv_label]
    selected_cv = fetch_version(selected_cv_version["id"])["cv"]
    cv_default_letter = default_cover_letter_data(selected_cv)

    cover_versions = fetch_cover_letter_versions(selected_profile["id"])
    cover_option_labels = ["New Draft (from CV)"] + [
        f"{v['version_name']} ({v['updated_at'][:19]})" for v in cover_versions
    ]
    selected_cover_label = st.selectbox(
        "Cover Letter Version",
        cover_option_labels,
        key="cover_version_select",
    )

    selected_cover_version_id = None
    selected_cover_version_name = ""
    if selected_cover_label != "New Draft (from CV)":
        selected_cover_version = next(
            (v for v in cover_versions if f"{v['version_name']} ({v['updated_at'][:19]})" == selected_cover_label),
            None,
        )
        if selected_cover_version:
            selected_cover_version_id = selected_cover_version["id"]
            selected_cover_version_name = selected_cover_version["version_name"]

    if selected_cover_version_id:
        saved_letter = fetch_cover_letter_version(selected_cover_version_id)
        base_letter = cv_default_letter.copy()
        if saved_letter and isinstance(saved_letter.get("letter"), dict):
            base_letter.update(saved_letter["letter"])
    else:
        base_letter = cv_default_letter

    editor_state_key = f"cover_editor::{selected_profile['id']}::{selected_cover_version_id or 'new'}::{selected_cv_version['id']}"
    if st.session_state.get("cover_editor_source") != editor_state_key:
        st.session_state["cover_editor_source"] = editor_state_key
        st.session_state["cover_version_name"] = selected_cover_version_name or "Draft v1"
        st.session_state["cover_name"] = base_letter.get("name", "")
        st.session_state["cover_title"] = base_letter.get("title", "")
        st.session_state["cover_sender_address"] = base_letter.get("sender_address", "")
        st.session_state["cover_recipient_address"] = base_letter.get("recipient_address", "")
        st.session_state["cover_subject"] = base_letter.get("subject", "")
        st.session_state["cover_body"] = base_letter.get("body", "")
        st.session_state["cover_signatory"] = base_letter.get("signatory", "")

    st.info("Sender details are auto-fetched from the selected CV version. Use 'Refresh From CV' to re-apply them.")
    if st.button("Refresh From CV", use_container_width=False):
        st.session_state["cover_name"] = cv_default_letter.get("name", "")
        st.session_state["cover_title"] = cv_default_letter.get("title", "")
        st.session_state["cover_sender_address"] = cv_default_letter.get("sender_address", "")
        if not str(st.session_state.get("cover_signatory", "")).strip():
            st.session_state["cover_signatory"] = cv_default_letter.get("signatory", "")

    version_name = st.text_input("Version Name", key="cover_version_name", placeholder="e.g., Data Analyst - Company X")

    col_left, col_right = st.columns(2)
    with col_left:
        st.text_input("Name", key="cover_name", placeholder="Your full name")
        st.text_input("Title", key="cover_title", placeholder="e.g., Software Engineer")
        st.text_area(
            "Sender's Address",
            key="cover_sender_address",
            placeholder="Street\nCity, State\nCountry",
            height=110,
        )
    with col_right:
        st.text_area(
            "Recipient's Address",
            key="cover_recipient_address",
            placeholder="Hiring Manager\nCompany\nStreet\nCity, State",
            height=110,
        )
        st.text_input("Subject", key="cover_subject", placeholder="Application for ...")
        st.text_input("Signatory", key="cover_signatory", placeholder="Your Name")

    rich_text_area(
        "Body",
        value=st.session_state.get("cover_body", ""),
        height=260,
        key="cover_body",
        placeholder=(
            "Write your cover letter body here. Use a blank line between paragraphs for best formatting."
        ),
    )

    current_letter_data = {
        "name": st.session_state.get("cover_name", ""),
        "title": st.session_state.get("cover_title", ""),
        "sender_address": st.session_state.get("cover_sender_address", ""),
        "recipient_address": st.session_state.get("cover_recipient_address", ""),
        "subject": st.session_state.get("cover_subject", ""),
        "body": st.session_state.get("cover_body", ""),
        "signatory": st.session_state.get("cover_signatory", ""),
    }

    col_save, col_new = st.columns(2)
    with col_save:
        save_label = "Update Version" if selected_cover_version_id else "Save Draft"
        if st.button(save_label, use_container_width=True):
            if not str(version_name).strip():
                st.error("Version name is required.")
            elif selected_cover_version_id:
                save_cover_letter_version(selected_cover_version_id, version_name, current_letter_data)
                st.success("Cover letter version updated.")
                st.rerun()
            else:
                create_cover_letter_version(selected_profile["id"], version_name, current_letter_data)
                st.success("Cover letter draft saved.")
                st.rerun()
    with col_new:
        if st.button("Save As New Version", use_container_width=True):
            if not str(version_name).strip():
                st.error("Version name is required.")
            else:
                create_cover_letter_version(selected_profile["id"], version_name, current_letter_data)
                st.success("New cover letter version created.")
                st.rerun()

    # Delete cover letter version
    if selected_cover_version_id:
        with st.expander("Danger Zone"):
            if st.checkbox(
                f"Delete cover letter version '{selected_cover_version_name}'",
                key="confirm_delete_cover_letter",
            ):
                if st.button("Delete This Cover Letter Version", use_container_width=True):
                    delete_cover_letter_version(selected_cover_version_id)
                    st.success("Cover letter version deleted.")
                    st.rerun()

    st.subheader("Download")
    cover_letter_download_section(
        current_letter_data,
        f"{selected_profile['name'].replace(' ', '_')}_{str(version_name).strip() or 'cover_letter'}",
    )

    st.subheader("Preview")
    components.html(build_cover_letter_html(current_letter_data), height=760, scrolling=True)
