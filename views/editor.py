import hmac
import json
import os
import time

import streamlit as st

from db.profiles import fetch_profiles, set_default_profile, create_profile, delete_profile, rename_profile
from db.cv_versions import fetch_versions, fetch_version, save_version, create_new_version, delete_version
from utils.defaults import default_cv_data
from utils.converters import (
    list_to_text, text_to_list, experience_to_text, text_to_experience,
    education_to_text, text_to_education, referees_to_text, text_to_referees,
    projects_to_text, text_to_projects,
)
from utils.widgets import rich_text_area
from templates.themes import DISPLAY_TEMPLATE_OPTIONS
from views.public_view import render_cv_streamlit, download_section

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300


def get_editor_password() -> str:
    try:
        secret_password = st.secrets.get("editor_password", "")
        if secret_password:
            return str(secret_password)
    except Exception:
        pass
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

    attempts = st.session_state.get("login_attempts", 0)
    lockout_until = st.session_state.get("login_lockout_until", 0)

    if time.time() < lockout_until:
        remaining = int(lockout_until - time.time())
        st.error(f"Too many failed attempts. Try again in {remaining} seconds.")
        return

    if lockout_until and time.time() >= lockout_until:
        st.session_state["login_attempts"] = 0
        st.session_state["login_lockout_until"] = 0
        attempts = 0

    with st.form("editor_login_form"):
        password = st.text_input("Password", type="password", placeholder="Enter editor password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if hmac.compare_digest(password, configured_password):
            st.session_state["editor_authenticated"] = True
            st.session_state["login_attempts"] = 0
            st.session_state["login_lockout_until"] = 0
            st.success("Login successful.")
            st.rerun()
        else:
            attempts += 1
            st.session_state["login_attempts"] = attempts
            if attempts >= MAX_LOGIN_ATTEMPTS:
                st.session_state["login_lockout_until"] = time.time() + LOCKOUT_SECONDS
                st.error(f"Too many failed attempts. Locked out for {LOCKOUT_SECONDS // 60} minutes.")
            else:
                st.error(f"Invalid password. ({MAX_LOGIN_ATTEMPTS - attempts} attempts remaining)")


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
    st.caption("Projects format: Name || Description || Technologies || Link")
    projects_text = rich_text_area(
        "Projects",
        value=projects_to_text(cv.get("projects", [])),
        height=140,
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
        "projects": text_to_projects(projects_text),
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

    # JSON Export / Import
    with st.expander("Import / Export"):
        st.download_button(
            "Export CV as JSON",
            data=json.dumps(new_cv, indent=2, ensure_ascii=False),
            file_name=f"{version_name.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
        )
        uploaded = st.file_uploader("Import CV from JSON", type=["json"], key="cv_json_import")
        if uploaded is not None:
            try:
                imported = json.loads(uploaded.getvalue().decode("utf-8"))
                if not isinstance(imported, dict):
                    st.error("Invalid JSON: expected a JSON object.")
                else:
                    import_name = st.text_input(
                        "Name for imported version",
                        value=f"Imported - {uploaded.name}",
                        key="import_version_name",
                    )
                    if st.button("Import as New Version", use_container_width=True):
                        create_new_version(profile_id, import_name, imported)
                        st.success("Imported as new version.")
                        st.rerun()
            except (json.JSONDecodeError, UnicodeDecodeError):
                st.error("Could not parse the uploaded file as JSON.")

    # Delete version
    with st.expander("Danger Zone"):
        st.warning("These actions are irreversible.")
        if st.checkbox(f"I want to delete version '{selected_version['version_name']}'", key="confirm_delete_version"):
            if st.button("Delete This Version", type="primary", use_container_width=True):
                versions_list = fetch_versions(profile_id)
                if len(versions_list) <= 1:
                    st.error("Cannot delete the last remaining version.")
                else:
                    delete_version(selected_version["id"])
                    st.success("Version deleted.")
                    st.rerun()


def render_editor_page() -> None:
    """Full editor page: profile management, version selection, preview, download, editor."""
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

        st.divider()
        rename_val = st.text_input("Rename Profile", value=selected_profile["name"], key="rename_profile_name")
        if st.button("Rename Profile", use_container_width=True):
            if rename_val.strip() and rename_val.strip() != selected_profile["name"]:
                rename_profile(selected_profile["id"], rename_val.strip())
                st.success("Profile renamed.")
                st.rerun()

        st.divider()
        if len(profiles) > 1:
            if st.checkbox(f"I want to delete profile '{selected_profile['name']}'", key="confirm_delete_profile"):
                if st.button("Delete Profile", use_container_width=True):
                    delete_profile(selected_profile["id"])
                    st.success("Profile deleted.")
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
