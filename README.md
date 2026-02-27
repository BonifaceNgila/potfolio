# Python CV Portfolio Manager

This project is a database-driven Streamlit CV portfolio with:

- Editable CV content
- Multiple profiles (e.g., IAM CV, DevOps CV, General CV)
- Multiple versions per profile
- Public Visitor Page that shows the default CV
- Downloadable CV templates in one-column and two-column layouts
- Downloadable CV templates in HTML and PDF
- A Cover Letter formatter page with justified body text
- Database-driven cover letter drafts and version history per profile
- Sender details auto-fetched from selected CV versions
- Cover letter downloads in HTML, TXT, and Word formats

## Run locally

1. Open a terminal in this folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

The app will open in your browser.

## How it works

- **Public View:** Displays the current default profile CV and lets visitors preview it with every downloadable template.
- **Editor:** Create and manage profiles, set default profile, edit CV fields, and save multiple versions.
- **Database:** Uses SQLite (`cv_portfolio.db`) created automatically on first run.

## Editor login

Editor access requires a password. Configure one of the following:

- Streamlit secrets: set `editor_password`
- Environment variable: set `CV_EDITOR_PASSWORD`

Example for Streamlit Cloud `secrets.toml`:

```toml
editor_password = "your-strong-password"
```

## Downloads

You can download CVs as both HTML and PDF in these templates:

- One Column - Classic
- One Column - Minimal
- Two Column - Professional
- Two Column - Sidebar
- Two Column - Sidebar Skillset
- Two Column - Accent Panel
- Two Column - Slate Profile

## Editing format notes

- **Experience:** Each job block starts with `Role || Organization || Period`, then bullet lines starting with `-`.
- **Referees:** One line per referee in this format: `Name || Title || Email || Phone`.
