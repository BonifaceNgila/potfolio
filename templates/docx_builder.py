from io import BytesIO

from utils.converters import normalize_education_record, normalize_project_record

try:
    import docx
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ModuleNotFoundError:
    docx = None
    Pt = None
    RGBColor = None
    Inches = None
    WD_ALIGN_PARAGRAPH = None
    DOCX_AVAILABLE = False


def build_docx(cv: dict, template: str) -> bytes:
    if not DOCX_AVAILABLE:
        return b""

    doc = docx.Document()

    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    name_para = doc.add_paragraph()
    name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_run = name_para.add_run(cv.get("full_name", ""))
    name_run.bold = True
    name_run.font.size = Pt(24)

    headline_para = doc.add_paragraph()
    headline_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    headline_run = headline_para.add_run(cv.get("headline", ""))
    headline_run.font.size = Pt(14)
    headline_run.font.color.rgb = RGBColor(100, 100, 100)

    contact_parts = []
    if cv.get("location"):
        contact_parts.append(cv.get("location"))
    if cv.get("phone"):
        contact_parts.append(cv.get("phone"))
    if cv.get("email"):
        contact_parts.append(cv.get("email"))
    if cv.get("linkedin"):
        contact_parts.append(cv.get("linkedin"))
    if cv.get("github"):
        contact_parts.append(cv.get("github"))

    contact_para = doc.add_paragraph()
    contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_run = contact_para.add_run(" | ".join(contact_parts))
    contact_run.font.size = Pt(10)

    doc.add_paragraph()

    def add_heading(text):
        p = doc.add_paragraph()
        r = p.add_run(text.upper())
        r.bold = True
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(30, 58, 95)
        p.paragraph_format.space_after = Pt(6)

    if cv.get("profile_summary"):
        add_heading("Profile")
        p = doc.add_paragraph(cv.get("profile_summary"))
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    if cv.get("core_competencies"):
        add_heading("Core Competencies")
        for item in cv.get("core_competencies"):
            if str(item).strip():
                doc.add_paragraph(item, style='List Bullet')

    if cv.get("experience"):
        add_heading("Professional Experience")
        for exp in cv.get("experience"):
            p = doc.add_paragraph()
            r1 = p.add_run(exp.get("role", ""))
            r1.bold = True
            p.add_run(f" - {exp.get('organization', '')} | {exp.get('period', '')}")

            for bullet in exp.get("bullets", []):
                if str(bullet).strip():
                    bp = doc.add_paragraph(bullet, style='List Bullet')
                    bp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            doc.add_paragraph()

    if cv.get("education"):
        add_heading("Education")
        for item in cv.get("education"):
            record = normalize_education_record(item)
            course = record.get("course", "")
            institution = record.get("institution", "")
            timeline = record.get("timeline", "")

            parts = [p for p in [course, institution] if p]
            if timeline:
                parts.append(f"({timeline})")

            if parts:
                doc.add_paragraph(" - ".join(parts), style='List Bullet')

    if cv.get("projects"):
        add_heading("Projects")
        for item in cv.get("projects"):
            record = normalize_project_record(item)
            name = record.get("name", "")
            description = record.get("description", "")
            technologies = record.get("technologies", "")
            link = record.get("link", "")
            if not name.strip() and not description.strip():
                continue
            if name:
                p = doc.add_paragraph(name, style='List Bullet')
                for run in p.runs:
                    run.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            if description:
                p = doc.add_paragraph(description)
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            if technologies:
                p = doc.add_paragraph(f"Technologies: {technologies}")
                for run in p.runs:
                    run.italic = True
            if link:
                doc.add_paragraph(link)

    if cv.get("certifications"):
        add_heading("Certifications")
        for item in cv.get("certifications"):
            if str(item).strip():
                doc.add_paragraph(item, style='List Bullet')

    if cv.get("languages"):
        add_heading("Languages")
        for item in cv.get("languages"):
            if str(item).strip():
                doc.add_paragraph(item, style='List Bullet')

    if cv.get("referees"):
        add_heading("Referees")
        for ref in cv.get("referees"):
            name = ref.get("name", "")
            position = ref.get("position") or ref.get("title", "")
            organization = ref.get("organization", "")
            email = ref.get("email", "")
            phone = ref.get("phone", "")

            parts = [p for p in [name, position, organization] if p]
            summary = " | ".join(parts)

            contacts = []
            if email:
                contacts.append(f"Email: {email}")
            if phone:
                contacts.append(f"Phone: {phone}")
            contact_line = " | ".join(contacts)

            text = summary
            if contact_line:
                text = f"{text} | {contact_line}" if text else contact_line

            if text:
                doc.add_paragraph(text, style='List Bullet')

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
