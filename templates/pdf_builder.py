from io import BytesIO

from utils.pdf_helpers import (
    REPORTLAB_AVAILABLE, colors, A4, pdfmetrics, canvas,
    pdf_safe_text, wrap_pdf_text, draw_pdf_wrapped_text,
    draw_pdf_section_title, safe_round_rect, ensure_pdf_space,
    SECTION_ICON_SHAPES,
)
from utils.converters import normalize_education_record, normalize_project_record
from templates.themes import normalize_template_name, get_pdf_theme


def _measure_wrapped_text_height(
    text: str,
    font_name: str,
    font_size: int,
    max_width: float,
    leading: int,
) -> int:
    if not str(text).strip():
        return 0
    return len(wrap_pdf_text(text, font_name, font_size, max_width)) * leading


def _draw_wrapped_lines(
    pdf,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font_name: str,
    font_size: int,
    leading: int,
    fill_color=None,
    align: str = "left",
) -> float:
    lines = wrap_pdf_text(text, font_name, font_size, max_width)
    if not lines:
        return y

    pdf.setFont(font_name, font_size)
    if fill_color is not None:
        pdf.setFillColor(fill_color)

    for line in lines:
        if align == "center":
            pdf.drawCentredString(x, y, line)
        elif align == "right":
            pdf.drawRightString(x, y, line)
        else:
            pdf.drawString(x, y, line)
        y -= leading
    return y


def _build_contact_fields(cv: dict) -> list[tuple[str, str]]:
    fields = [
        ("Location", cv.get("location", "")),
        ("Phone", cv.get("phone", "")),
        ("Email", cv.get("email", "")),
        ("LinkedIn", cv.get("linkedin", "")),
        ("GitHub", cv.get("github", "")),
    ]
    return [(label, str(value).strip()) for label, value in fields if str(value).strip()]


def _measure_contact_blocks_height(
    contact_fields: list[tuple[str, str]],
    max_width: float,
    label_font_size: int,
    value_font_size: int,
    value_leading: int,
    block_gap: int = 6,
) -> int:
    total_height = 0
    for index, (_, value) in enumerate(contact_fields):
        total_height += label_font_size + 4
        total_height += max(
            value_leading,
            _measure_wrapped_text_height(
                value,
                "Helvetica",
                value_font_size,
                max_width,
                value_leading,
            ),
        )
        if index < len(contact_fields) - 1:
            total_height += block_gap
    return total_height


def _draw_contact_blocks(
    pdf,
    contact_fields: list[tuple[str, str]],
    x: float,
    y: float,
    max_width: float,
    label_font_size: int,
    value_font_size: int,
    value_leading: int,
    label_color,
    value_color,
    block_gap: int = 6,
) -> float:
    for index, (label, value) in enumerate(contact_fields):
        pdf.setFillColor(label_color)
        pdf.setFont("Helvetica-Bold", label_font_size)
        pdf.drawString(x, y, pdf_safe_text(label.upper()))
        y -= label_font_size + 4
        y = _draw_wrapped_lines(
            pdf,
            value,
            x,
            y,
            max_width,
            "Helvetica",
            value_font_size,
            value_leading,
            fill_color=value_color,
        )
        if index < len(contact_fields) - 1:
            y -= block_gap
    return y


def build_pdf(cv: dict, template: str) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    normalized_template = normalize_template_name(template)
    theme = get_pdf_theme(normalized_template)
    if "Two Column" in normalized_template:
        return build_pdf_two_column(cv, theme)
    return build_pdf_one_column(cv, theme)


def build_pdf_one_column(cv: dict, theme: dict | None = None) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    theme = theme or get_pdf_theme("One Column - Minimal")
    background = theme.get("background", colors.HexColor("#030712"))
    hero_background = theme.get("hero_background", colors.HexColor("#102a43"))
    hero_accent = theme.get("hero_accent", colors.HexColor("#1e3a8a"))
    hero_strip = theme.get("hero_strip", colors.HexColor("#2563eb"))
    hero_text_color = theme.get("hero_text", colors.white)
    text_color = theme.get("text_color", colors.HexColor("#e2e8f0"))
    link_color = theme.get("link_color", hero_strip)
    panel_primary = theme.get("panel_primary", colors.HexColor("#0f172a"))
    panel_secondary = theme.get("panel_secondary", colors.HexColor("#0f172a"))
    border_color = theme.get("border", colors.HexColor("#1d4ed8"))
    layout_style = theme.get("layout", "classic_hero")
    section_title_color = theme.get(
        "section_title_color",
        colors.HexColor("#1E3A5F") if layout_style == "minimal_clean" else theme.get("hero_strip", colors.HexColor("#2563eb")),
    )
    section_line_color = theme.get(
        "section_line_color",
        colors.HexColor("#BFD7ED") if layout_style == "minimal_clean" else border_color,
    )
    header_min_height = theme.get("header_min_height", 126)
    header_name_font_size = theme.get("header_name_font_size", 22)
    header_headline_font_size = theme.get("header_headline_font_size", 12)
    header_contact_label_font_size = theme.get("header_contact_label_font_size", 8)
    header_contact_font_size = theme.get("header_contact_font_size", 9)
    header_contact_leading = theme.get("header_contact_leading", header_contact_font_size + 2)
    header_meta_ratio = min(max(theme.get("header_meta_ratio", 0.34), 0.26), 0.4)
    contact_fields = _build_contact_fields(cv)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 28
    right = width - 28
    content_width = right - left
    top = height - 34
    bottom = 28
    y = top
    on_new_page_callback = None

    if layout_style == "minimal_clean":
        def draw_minimal_frame() -> None:
            pdf.setFillColor(background)
            pdf.rect(0, 0, width, height, fill=1, stroke=0)
            pdf.setFillColor(theme.get("hero_strip", colors.HexColor("#1e3a5f")))
            pdf.rect(left - 18, 0, 4, height, fill=1, stroke=0)

        def on_minimal_new_page() -> float:
            draw_minimal_frame()
            pdf.setFillColor(text_color)
            return top - 6

        draw_minimal_frame()
        header_width = content_width - 8
        y = _draw_wrapped_lines(
            pdf,
            cv.get("full_name", ""),
            left,
            y,
            header_width,
            "Helvetica-Bold",
            header_name_font_size,
            header_name_font_size + 4,
            fill_color=hero_text_color,
        )
        y -= 4
        y = _draw_wrapped_lines(
            pdf,
            cv.get("headline", ""),
            left,
            y,
            header_width,
            "Helvetica",
            header_headline_font_size,
            header_headline_font_size + 4,
            fill_color=hero_text_color,
        )
        if contact_fields:
            y -= 10
            y = _draw_contact_blocks(
                pdf,
                contact_fields,
                left,
                y,
                header_width,
                header_contact_label_font_size,
                header_contact_font_size,
                header_contact_leading,
                theme.get("hero_strip", colors.HexColor("#1e3a5f")),
                text_color,
            )
            y -= 6
        pdf.setFillColor(text_color)
        on_new_page_callback = on_minimal_new_page
    else:
        def on_classic_new_page() -> float:
            pdf.setFillColor(background)
            pdf.rect(0, 0, width, height, fill=1, stroke=0)

            ribbon_height = 26
            ribbon_bottom = top - ribbon_height
            pdf.setFillColor(hero_background)
            safe_round_rect(pdf, left - 12, ribbon_bottom, content_width + 24, ribbon_height, 10, fill=1, stroke=0)
            pdf.setFillColor(hero_accent)
            pdf.rect(left, ribbon_bottom + 5, content_width * 0.56, ribbon_height - 10, fill=1, stroke=0)

            y_start = ribbon_bottom - 16
            pdf.setFillColor(panel_primary)
            pdf.rect(left - 12, bottom - 6, content_width + 24, y_start - bottom + 24, fill=1, stroke=0)
            pdf.setStrokeColor(border_color)
            pdf.setLineWidth(1)
            pdf.rect(left - 12, bottom - 6, content_width + 24, y_start - bottom + 24, fill=0, stroke=1)
            pdf.setFillColor(text_color)
            return y_start - 8

        pdf.setFillColor(background)
        pdf.rect(0, 0, width, height, fill=1, stroke=0)
        meta_width = min(max(content_width * header_meta_ratio, 150), content_width * 0.42)
        left_header_width = content_width - meta_width - 24
        name_leading = header_name_font_size + 4
        headline_leading = header_headline_font_size + 4
        left_header_height = _measure_wrapped_text_height(
            cv.get("full_name", ""),
            "Helvetica-Bold",
            header_name_font_size,
            left_header_width,
            name_leading,
        )
        if str(cv.get("headline", "")).strip():
            left_header_height += 6 + _measure_wrapped_text_height(
                cv.get("headline", ""),
                "Helvetica",
                header_headline_font_size,
                left_header_width,
                headline_leading,
            )
        meta_header_height = _measure_contact_blocks_height(
            contact_fields,
            meta_width,
            header_contact_label_font_size,
            header_contact_font_size,
            header_contact_leading,
        )
        hero_height = max(header_min_height, max(left_header_height, meta_header_height) + 36)
        hero_bottom = y - hero_height
        pdf.setFillColor(hero_background)
        safe_round_rect(pdf, left - 16, hero_bottom - 8, content_width + 32, hero_height + 16, 20, fill=1, stroke=0)
        pdf.setFillColor(hero_accent)
        accent_height = min(max(left_header_height + 18, 42), hero_height * 0.6)
        accent_y = hero_bottom + ((hero_height - accent_height) / 2)
        pdf.rect(left, accent_y, min(content_width * 0.68, left_header_width + 22), accent_height, fill=1, stroke=0)
        text_y = hero_bottom + hero_height - 24
        text_y = _draw_wrapped_lines(
            pdf,
            cv.get("full_name", ""),
            left + 8,
            text_y,
            left_header_width,
            "Helvetica-Bold",
            header_name_font_size,
            name_leading,
            fill_color=hero_text_color,
        )
        text_y -= 6
        _draw_wrapped_lines(
            pdf,
            cv.get("headline", ""),
            left + 8,
            text_y,
            left_header_width,
            "Helvetica",
            header_headline_font_size,
            headline_leading,
            fill_color=hero_text_color,
        )
        _draw_contact_blocks(
            pdf,
            contact_fields,
            right - meta_width,
            hero_bottom + hero_height - 18,
            meta_width,
            header_contact_label_font_size,
            header_contact_font_size,
            header_contact_leading,
            link_color,
            hero_text_color,
        )
        y = hero_bottom - 18
        pdf.setFillColor(panel_primary)
        pdf.rect(left - 12, bottom - 6, content_width + 24, y - bottom + 24, fill=1, stroke=0)
        pdf.setStrokeColor(border_color)
        pdf.setLineWidth(1)
        pdf.rect(left - 12, bottom - 6, content_width + 24, y - bottom + 24, fill=0, stroke=1)
        y -= 12
        pdf.setFillColor(text_color)
        on_new_page_callback = on_classic_new_page

    def _draw_section(title, items_fn):
        nonlocal y
        y = ensure_pdf_space(pdf, y, 40, bottom, top, on_new_page=on_new_page_callback)
        y = draw_pdf_section_title(pdf, title, left, y, title_color=section_title_color, line_color=section_line_color)
        pdf.setFillColor(text_color)
        items_fn()

    def _profile():
        nonlocal y
        y = draw_pdf_wrapped_text(pdf, cv.get("profile_summary", ""), left, y, content_width, bottom, top, on_new_page=on_new_page_callback)
        y -= 6

    def _competencies():
        nonlocal y
        for item in cv.get("core_competencies") or []:
            y = draw_pdf_wrapped_text(pdf, f"- {item}", left, y, content_width, bottom, top, on_new_page=on_new_page_callback)
        y -= 6

    def _experience():
        nonlocal y
        for exp in cv.get("experience") or []:
            y = ensure_pdf_space(pdf, y, 28, bottom, top, on_new_page=on_new_page_callback)
            y = draw_pdf_wrapped_text(
                pdf,
                f"{exp.get('role', '')} - {exp.get('organization', '')} | {exp.get('period', '')}",
                left, y, content_width, bottom, top,
                font_name="Helvetica-Bold", font_size=10, leading=13,
                on_new_page=on_new_page_callback,
            )
            for bullet in exp.get("bullets") or []:
                y = draw_pdf_wrapped_text(pdf, f"  - {bullet}", left, y, content_width, bottom, top, on_new_page=on_new_page_callback)
            y -= 3

    def _projects():
        nonlocal y
        for item in cv.get("projects") or []:
            record = normalize_project_record(item)
            name = record.get("name", "")
            description = record.get("description", "")
            technologies = record.get("technologies", "")
            link = record.get("link", "")
            if name:
                y = draw_pdf_wrapped_text(pdf, name, left, y, content_width, bottom, top, font_name="Helvetica-Bold", font_size=10, leading=13, on_new_page=on_new_page_callback)
            if description:
                y = draw_pdf_wrapped_text(pdf, f"  {description}", left, y, content_width, bottom, top, on_new_page=on_new_page_callback)
            if technologies:
                y = draw_pdf_wrapped_text(pdf, f"  Technologies: {technologies}", left, y, content_width, bottom, top, font_name="Helvetica-Oblique", font_size=9, leading=12, on_new_page=on_new_page_callback)
            if link:
                y = draw_pdf_wrapped_text(pdf, f"  {link}", left, y, content_width, bottom, top, font_name="Helvetica-Oblique", font_size=9, leading=12, on_new_page=on_new_page_callback)
            y -= 3

    def _education():
        nonlocal y
        for idx, item in enumerate(cv.get("education") or [], start=1):
            record = normalize_education_record(item)
            course = record.get("course", "")
            institution = record.get("institution", "")
            timeline = record.get("timeline", "")
            line_parts = [part for part in [course, institution] if part]
            if timeline:
                line_parts.append(f"({timeline})")
            entry_line = " - ".join(line_parts) if line_parts else ""
            if entry_line:
                entry_line = f"{idx}. {entry_line}"
            y = draw_pdf_wrapped_text(pdf, entry_line, left, y, content_width, bottom, top, on_new_page=on_new_page_callback)

    def _certifications():
        nonlocal y
        for item in cv.get("certifications") or []:
            y = draw_pdf_wrapped_text(pdf, f"- {item}", left, y, content_width, bottom, top, on_new_page=on_new_page_callback)

    def _languages():
        nonlocal y
        for item in cv.get("languages") or []:
            y = draw_pdf_wrapped_text(pdf, f"- {item}", left, y, content_width, bottom, top, on_new_page=on_new_page_callback)

    def _referees():
        nonlocal y
        for idx, ref in enumerate(cv.get("referees") or [], start=1):
            full_line = _format_referee_line(ref, idx)
            y = draw_pdf_wrapped_text(pdf, full_line, left, y, content_width, bottom, top, on_new_page=on_new_page_callback)

    _draw_section("Profile", _profile)
    _draw_section("Core Competencies", _competencies)
    _draw_section("Professional Experience", _experience)
    y = ensure_pdf_space(pdf, y, 36, bottom, top, on_new_page=on_new_page_callback)
    y = draw_pdf_section_title(pdf, "Projects", left, y, title_color=section_title_color, line_color=section_line_color)
    pdf.setFillColor(text_color)
    _projects()
    _draw_section("Education", _education)
    _draw_section("Certifications", _certifications)
    _draw_section("Languages", _languages)
    y = ensure_pdf_space(pdf, y, 42, bottom, top, on_new_page=on_new_page_callback)
    y = draw_pdf_section_title(pdf, "Referees", left, y, title_color=section_title_color, line_color=section_line_color)
    pdf.setFillColor(text_color)
    _referees()

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def _format_referee_line(ref: dict, idx: int) -> str:
    name = ref.get("name", "")
    position = ref.get("position") or ref.get("title", "")
    organization = ref.get("organization", "")
    email = ref.get("email", "")
    phone = ref.get("phone", "")
    parts = [part for part in [name, position, organization] if part]
    ref_summary = " | ".join(parts)
    contact = []
    if email:
        contact.append(f"Email: {email}")
    if phone:
        contact.append(f"Phone: {phone}")
    contact_line = " | ".join(contact)
    full_line = f"{idx}. {ref_summary}" if ref_summary else f"{idx}."
    if contact_line:
        full_line = f"{full_line} | {contact_line}"
    return full_line


def _build_referee_ops(cv: dict, target_ops: list[dict], column_width: float) -> None:
    """Shared referee ops builder to eliminate duplication between layouts."""
    for ref in cv.get("referees") or []:
        name = ref.get("name", "")
        position = ref.get("position") or ref.get("title", "")
        organization = ref.get("organization", "")
        email = ref.get("email", "")
        phone = ref.get("phone", "")
        parts = [part for part in [name, position, organization] if part]
        summary = " | ".join(parts)
        contacts = []
        if email:
            contacts.append(f"Email: {email}")
        if phone:
            contacts.append(f"Phone: {phone}")
        contact_line = " | ".join(contacts)
        text = summary or ""
        if contact_line:
            text = f"{text} | {contact_line}" if text else contact_line
        if text:
            _add_text_ops(target_ops, f"- {text}", column_width, font_name="Helvetica", font_size=9, leading=12)


def build_pdf_two_column(cv: dict, theme: dict | None = None) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    theme = theme or get_pdf_theme("Two Column - Professional")
    background = theme.get("background", colors.HexColor("#030712"))
    hero_background = theme.get("hero_background", colors.HexColor("#0f172a"))
    hero_accent = theme.get("hero_accent", colors.HexColor("#1e3a8a"))
    hero_strip = theme.get("hero_strip", colors.HexColor("#2563eb"))
    panel_primary = theme.get("panel_primary", colors.HexColor("#f8fafc"))
    panel_secondary = theme.get("panel_secondary", colors.HexColor("#eef2ff"))
    panel_border = theme.get("panel_border", colors.HexColor("#d6e3f2"))
    hero_text_color = theme.get("hero_text", colors.white)
    text_color = theme.get("text_color", colors.black)
    layout_style = theme.get("layout", "modern_header")
    section_title_color = theme.get("section_title_color", colors.HexColor("#1E3A5F"))
    section_line_color = theme.get("section_line_color", colors.HexColor("#BFD7ED"))
    sidebar_text_color = theme.get("sidebar_text_color", text_color)
    sidebar_section_title_color = theme.get("sidebar_section_title_color", section_title_color)
    sidebar_section_line_color = theme.get("sidebar_section_line_color", section_line_color)
    sidebar_background = theme.get("sidebar_background", panel_secondary)
    sidebar_border = theme.get("sidebar_border", panel_border)
    header_min_height = theme.get("header_min_height", 132)
    header_name_font_size = theme.get("header_name_font_size", 24)
    header_headline_font_size = theme.get("header_headline_font_size", 12)
    header_contact_label_font_size = theme.get("header_contact_label_font_size", 8)
    header_contact_font_size = theme.get("header_contact_font_size", 9)
    header_contact_leading = theme.get("header_contact_leading", header_contact_font_size + 2)
    main_ratio = min(max(theme.get("main_ratio", 0.62), 0.55), 0.72)
    contact_fields = _build_contact_fields(cv)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFillColor(background)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    margin = 22
    gap = 14
    top = height - 22
    bottom = 28
    total_width = width - (2 * margin)
    if layout_style == "sidebar_skillset":
        sidebar_ratio = min(max(theme.get("sidebar_ratio", 0.36), 0.3), 0.42)
        sidebar_width = total_width * sidebar_ratio
        main_width = total_width - sidebar_width - gap
        left_width = main_width
        right_width = sidebar_width
        right_x = margin
        left_x = right_x + right_width + gap
    elif layout_style == "slate_profile":
        sidebar_ratio = min(max(theme.get("sidebar_ratio", 0.37), 0.3), 0.44)
        sidebar_width = total_width * sidebar_ratio
        main_width = total_width - sidebar_width - gap
        right_width = sidebar_width
        right_x = margin
        left_width = main_width
        left_x = right_x + right_width + gap
    else:
        left_width = total_width * main_ratio
        right_width = total_width - left_width - gap
        left_x = margin
        right_x = left_x + left_width + gap

    def draw_columns(panel_top: float) -> None:
        column_height = panel_top - bottom + 12
        pdf.setStrokeColor(panel_border)
        pdf.setLineWidth(1)
        if layout_style == "sidebar_skillset":
            pdf.setFillColor(panel_primary)
            safe_round_rect(pdf, left_x - 4, bottom - 4, left_width + 8, column_height, 10, fill=1, stroke=1)
            pdf.setFillColor(hero_background)
            safe_round_rect(pdf, right_x - 4, bottom - 4, right_width + 8, column_height, 10, fill=1, stroke=0)
            pdf.setStrokeColor(hero_accent)
            safe_round_rect(pdf, right_x - 4, bottom - 4, right_width + 8, column_height, 10, fill=0, stroke=1)
            return
        if layout_style == "slate_profile":
            pdf.setFillColor(panel_primary)
            safe_round_rect(pdf, left_x - 4, bottom - 4, left_width + 8, column_height, 10, fill=1, stroke=1)
            pdf.setStrokeColor(panel_border)
            safe_round_rect(pdf, left_x - 4, bottom - 4, left_width + 8, column_height, 10, fill=0, stroke=1)
            pdf.setFillColor(sidebar_background)
            safe_round_rect(pdf, right_x - 4, bottom - 4, right_width + 8, column_height, 10, fill=1, stroke=0)
            pdf.setStrokeColor(sidebar_border)
            safe_round_rect(pdf, right_x - 4, bottom - 4, right_width + 8, column_height, 10, fill=0, stroke=1)
            return
        pdf.setFillColor(panel_primary)
        safe_round_rect(pdf, left_x - 4, bottom - 4, left_width + 8, column_height, 8, fill=1, stroke=1)
        pdf.setFillColor(panel_secondary)
        safe_round_rect(pdf, right_x - 4, bottom - 4, right_width + 8, column_height, 8, fill=1, stroke=1)

    def draw_page_layout(first_page: bool) -> tuple[float, float]:
        pdf.setFillColor(background)
        pdf.rect(0, 0, width, height, fill=1, stroke=0)

        if first_page:
            if layout_style == "slate_profile":
                banner_width = total_width - 72
                compact_name_leading = header_name_font_size + 4
                compact_headline_leading = header_headline_font_size + 4
                name_banner_height = max(
                    78,
                    _measure_wrapped_text_height(
                        cv.get("full_name", ""),
                        "Helvetica-Bold",
                        header_name_font_size,
                        banner_width,
                        compact_name_leading,
                    )
                    + _measure_wrapped_text_height(
                        cv.get("headline", ""),
                        "Helvetica",
                        header_headline_font_size,
                        banner_width,
                        compact_headline_leading,
                    )
                    + 32,
                )
                banner_bottom = top - name_banner_height
                pdf.setFillColor(panel_primary)
                safe_round_rect(pdf, margin - 6, banner_bottom - 10, total_width + 12, name_banner_height + 18, 8, fill=1, stroke=0)
                pdf.setStrokeColor(panel_border)
                pdf.setLineWidth(1)
                safe_round_rect(pdf, margin - 6, banner_bottom - 10, total_width + 12, name_banner_height + 18, 8, fill=0, stroke=1)
                text_y = banner_bottom + name_banner_height - 24
                text_y = _draw_wrapped_lines(
                    pdf,
                    cv.get("full_name", ""),
                    width / 2,
                    text_y,
                    banner_width,
                    "Helvetica-Bold",
                    header_name_font_size,
                    compact_name_leading,
                    fill_color=text_color,
                    align="center",
                )
                _draw_wrapped_lines(
                    pdf,
                    cv.get("headline", ""),
                    width / 2,
                    text_y - 4,
                    banner_width,
                    "Helvetica",
                    header_headline_font_size,
                    compact_headline_leading,
                    fill_color=text_color,
                    align="center",
                )
                draw_columns(banner_bottom - 14)
                start_y = banner_bottom - 30
                return start_y, start_y

            if layout_style == "sidebar_skillset":
                draw_columns(top)
                compact_name_font_size = max(16, header_name_font_size - 7)
                compact_headline_font_size = max(10, header_headline_font_size - 1)
                compact_name_leading = compact_name_font_size + 3
                compact_headline_leading = compact_headline_font_size + 3
                box_inner_width = right_width - 40
                box_content_height = _measure_wrapped_text_height(
                    cv.get("full_name", ""),
                    "Helvetica-Bold",
                    compact_name_font_size,
                    box_inner_width,
                    compact_name_leading,
                )
                if str(cv.get("headline", "")).strip():
                    box_content_height += 4 + _measure_wrapped_text_height(
                        cv.get("headline", ""),
                        "Helvetica",
                        compact_headline_font_size,
                        box_inner_width,
                        compact_headline_leading,
                    )
                name_box_height = max(44, box_content_height + 18)
                box_top = top - 12
                box_bottom = box_top - name_box_height
                pdf.setFillColor(hero_accent)
                safe_round_rect(pdf, right_x + 8, box_bottom, right_width - 16, name_box_height, 8, fill=1, stroke=0)
                text_y = box_top - 10
                text_y = _draw_wrapped_lines(
                    pdf,
                    cv.get("full_name", ""),
                    right_x + 12,
                    text_y,
                    box_inner_width,
                    "Helvetica-Bold",
                    compact_name_font_size,
                    compact_name_leading,
                    fill_color=hero_text_color,
                )
                _draw_wrapped_lines(
                    pdf,
                    cv.get("headline", ""),
                    right_x + 12,
                    text_y - 4,
                    box_inner_width,
                    "Helvetica",
                    compact_headline_font_size,
                    compact_headline_leading,
                    fill_color=hero_text_color,
                )
                sidebar_y = box_bottom - 14
                sidebar_y = _draw_contact_blocks(
                    pdf,
                    contact_fields,
                    right_x + 12,
                    sidebar_y,
                    right_width - 24,
                    header_contact_label_font_size,
                    header_contact_font_size,
                    header_contact_leading,
                    sidebar_section_title_color,
                    hero_text_color,
                )
                return top - 22, sidebar_y - 6

            if layout_style == "professional_header":
                contact_box_width = right_width + 10
                contact_box_x = right_x - 2
                contact_inner_width = contact_box_width - 16
                left_header_width = right_x - left_x - 22
                name_leading = header_name_font_size + 4
                headline_leading = header_headline_font_size + 4
                left_content_height = _measure_wrapped_text_height(
                    cv.get("full_name", ""),
                    "Helvetica-Bold",
                    header_name_font_size,
                    left_header_width,
                    name_leading,
                )
                if str(cv.get("headline", "")).strip():
                    left_content_height += 6 + _measure_wrapped_text_height(
                        cv.get("headline", ""),
                        "Helvetica",
                        header_headline_font_size,
                        left_header_width,
                        headline_leading,
                    )
                contact_box_height = max(
                    96,
                    _measure_contact_blocks_height(
                        contact_fields,
                        contact_inner_width,
                        header_contact_label_font_size,
                        header_contact_font_size,
                        header_contact_leading,
                    ) + 16,
                )
                header_height = max(header_min_height, max(left_content_height + 34, contact_box_height + 28))
                header_bottom = top - header_height
                contact_box_y = header_bottom + 14
                pdf.setFillColor(hero_background)
                safe_round_rect(pdf, left_x - 2, header_bottom, total_width + 4, header_height, 6, fill=1, stroke=0)
                pdf.setFillColor(hero_accent)
                safe_round_rect(pdf, contact_box_x, contact_box_y, contact_box_width, contact_box_height, 6, fill=1, stroke=0)
                pdf.setStrokeColor(colors.HexColor("#7da0c4"))
                pdf.setLineWidth(0.8)
                safe_round_rect(pdf, contact_box_x, contact_box_y, contact_box_width, contact_box_height, 6, fill=0, stroke=1)
                text_y = header_bottom + header_height - 22
                text_y = _draw_wrapped_lines(
                    pdf,
                    cv.get("full_name", ""),
                    left_x + 10,
                    text_y,
                    left_header_width,
                    "Helvetica-Bold",
                    header_name_font_size,
                    name_leading,
                    fill_color=hero_text_color,
                )
                _draw_wrapped_lines(
                    pdf,
                    cv.get("headline", ""),
                    left_x + 10,
                    text_y - 4,
                    left_header_width,
                    "Helvetica-Bold",
                    header_headline_font_size,
                    headline_leading,
                    fill_color=hero_text_color,
                )
                _draw_contact_blocks(
                    pdf,
                    contact_fields,
                    contact_box_x + 8,
                    contact_box_y + contact_box_height - 12,
                    contact_inner_width,
                    header_contact_label_font_size,
                    header_contact_font_size,
                    header_contact_leading,
                    hero_strip,
                    hero_text_color,
                )
                draw_columns(header_bottom - 10)
                pdf.setFillColor(text_color)
                start_y = header_bottom - 26
                return start_y, start_y

            # modern_header (default)
            title_width = right_x - left_x - 22
            name_leading = header_name_font_size + 4
            headline_leading = header_headline_font_size + 4
            title_content_height = _measure_wrapped_text_height(
                cv.get("full_name", ""),
                "Helvetica-Bold",
                header_name_font_size,
                title_width,
                name_leading,
            )
            if str(cv.get("headline", "")).strip():
                title_content_height += 6 + _measure_wrapped_text_height(
                    cv.get("headline", ""),
                    "Helvetica",
                    header_headline_font_size,
                    title_width,
                    headline_leading,
                )
            contact_content_height = _measure_contact_blocks_height(
                contact_fields,
                right_width - 10,
                header_contact_label_font_size,
                header_contact_font_size,
                header_contact_leading,
            )
            hero_height = max(header_min_height, max(title_content_height + 34, contact_content_height + 28))
            hero_top = top
            hero_bottom = hero_top - hero_height
            pdf.setFillColor(hero_background)
            safe_round_rect(pdf, left_x - 12, hero_bottom - 10, total_width + 24, hero_height + 20, 20, fill=1, stroke=0)
            pdf.setFillColor(hero_accent)
            accent_height = min(max(title_content_height + 18, 42), hero_height * 0.52)
            accent_y = hero_bottom + ((hero_height - accent_height) / 2)
            safe_round_rect(pdf, left_x + 6, accent_y, min(total_width * 0.58, title_width + 20), accent_height, 18, fill=1, stroke=0)
            text_y = hero_bottom + hero_height - 22
            text_y = _draw_wrapped_lines(
                pdf,
                cv.get("full_name", ""),
                left_x + 12,
                text_y,
                title_width,
                "Helvetica-Bold",
                header_name_font_size,
                name_leading,
                fill_color=hero_text_color,
            )
            _draw_wrapped_lines(
                pdf,
                cv.get("headline", ""),
                left_x + 12,
                text_y - 4,
                title_width,
                "Helvetica",
                header_headline_font_size,
                headline_leading,
                fill_color=hero_text_color,
            )
            _draw_contact_blocks(
                pdf,
                contact_fields,
                right_x + 6,
                hero_bottom + hero_height - 18,
                right_width - 10,
                header_contact_label_font_size,
                header_contact_font_size,
                header_contact_leading,
                hero_strip,
                hero_text_color,
            )
            draw_columns(hero_bottom)
            pdf.setFillColor(text_color)
            return hero_bottom - 16, hero_bottom - 24

        # Continuation pages
        ribbon_height = 24
        ribbon_bottom = top - ribbon_height
        if layout_style == "sidebar_skillset":
            draw_columns(top)
            compact_y = top - 18
            compact_y = _draw_wrapped_lines(
                pdf,
                cv.get("full_name", ""),
                right_x + 12,
                compact_y,
                right_width - 24,
                "Helvetica-Bold",
                10,
                12,
                fill_color=hero_text_color,
            )
            compact_y = _draw_wrapped_lines(
                pdf,
                cv.get("headline", ""),
                right_x + 12,
                compact_y,
                right_width - 24,
                "Helvetica",
                8,
                10,
                fill_color=hero_text_color,
            )
            return top - 18, compact_y - 8

        if layout_style == "slate_profile":
            draw_columns(top - 8)
            pdf.setFillColor(text_color)
            start_y = top - 26
            return start_y, start_y

        pdf.setFillColor(hero_background)
        if layout_style == "professional_header":
            safe_round_rect(pdf, left_x - 2, ribbon_bottom, total_width + 4, ribbon_height, 5, fill=1, stroke=0)
        else:
            safe_round_rect(pdf, left_x - 10, ribbon_bottom, total_width + 20, ribbon_height, 10, fill=1, stroke=0)
        pdf.setFillColor(hero_strip)
        safe_round_rect(pdf, right_x - 4, ribbon_bottom + 5, right_width + 8, ribbon_height - 10, 8, fill=1, stroke=0)
        panel_top = top - 8
        draw_columns(panel_top)
        pdf.setFillColor(text_color)
        start_y = panel_top - 16
        return start_y, start_y

    # Build operations for left/right columns
    left_ops: list[dict] = []
    _add_title_op(left_ops, "Profile")
    _add_text_ops(left_ops, cv.get("profile_summary", ""), left_width, font_name="Helvetica", font_size=10, leading=13)
    _add_gap_op(left_ops, 6)

    _add_title_op(left_ops, "Professional Experience")
    for exp in cv.get("experience") or []:
        _add_text_ops(
            left_ops,
            f"{exp.get('role', '')} - {exp.get('organization', '')} | {exp.get('period', '')}",
            left_width, font_name="Helvetica-Bold", font_size=9, leading=12,
        )
        for bullet in exp.get("bullets") or []:
            _add_text_ops(left_ops, f"- {bullet}", left_width, font_name="Helvetica", font_size=9, leading=12)
        _add_gap_op(left_ops, 3)

    projects = [item for item in (cv.get("projects") or []) if (isinstance(item, dict) and item.get("name", "").strip()) or (isinstance(item, str) and item.strip())]
    if projects:
        _add_title_op(left_ops, "Projects")
        for item in projects:
            record = normalize_project_record(item)
            name = record.get("name", "")
            description = record.get("description", "")
            technologies = record.get("technologies", "")
            link = record.get("link", "")
            if name:
                _add_text_ops(left_ops, name, left_width, font_name="Helvetica-Bold", font_size=9, leading=12)
            if description:
                _add_text_ops(left_ops, f"  {description}", left_width, font_name="Helvetica", font_size=9, leading=12)
            if technologies:
                _add_text_ops(left_ops, f"  Technologies: {technologies}", left_width, font_name="Helvetica-Oblique", font_size=8, leading=11)
            if link:
                _add_text_ops(left_ops, f"  {link}", left_width, font_name="Helvetica-Oblique", font_size=8, leading=11)
        _add_gap_op(left_ops, 4)

    education_records: list[dict] = []
    for item in cv.get("education") or []:
        record = normalize_education_record(item)
        if any(str(record.get(field, "")).strip() for field in ("course", "institution", "timeline")):
            education_records.append(record)

    def append_education_ops(target_ops: list[dict], column_width: float) -> None:
        if not education_records:
            return
        _add_title_op(target_ops, "Education")
        for idx, record in enumerate(education_records, start=1):
            course = record.get("course", "")
            institution = record.get("institution", "")
            timeline = record.get("timeline", "")
            parts = [part for part in [course, institution] if part]
            if timeline:
                parts.append(f"({timeline})")
            entry_line = " - ".join(parts) if parts else ""
            if entry_line:
                _add_text_ops(target_ops, f"{idx}. {entry_line}", column_width, font_name="Helvetica", font_size=10, leading=13)

    if layout_style != "slate_profile":
        append_education_ops(left_ops, left_width)

    right_ops: list[dict] = []

    def add_contact_line(label: str, value: str) -> None:
        if str(value).strip():
            _add_text_ops(right_ops, f"{label}: {value}", right_width, font_name="Helvetica", font_size=9, leading=12)

    if layout_style == "slate_profile":
        # Banner only shows name — need full Personal Details in sidebar
        _add_title_op(right_ops, "Personal Details")
        add_contact_line("Name", cv.get("full_name", ""))
        add_contact_line("Address", cv.get("location", ""))
        add_contact_line("Phone", cv.get("phone", ""))
        add_contact_line("Email", cv.get("email", ""))
        add_contact_line("LinkedIn", cv.get("linkedin", ""))
        add_contact_line("GitHub", cv.get("github", ""))
        _add_gap_op(right_ops, 6)
    elif layout_style in ("professional_header", "sidebar_skillset"):
        # Hero/sidebar header shows Location/Phone/Email; LinkedIn/GitHub now
        # shown there too — no contact section needed in ops
        pass
    else:
        # modern_header — hero shows all contact info; skip duplicate section
        pass

    if layout_style == "slate_profile":
        append_education_ops(right_ops, right_width)
        if education_records:
            _add_gap_op(right_ops, 4)

    competencies = [item for item in (cv.get("core_competencies") or []) if str(item).strip()]
    if layout_style == "slate_profile":
        skills = competencies[:6] if competencies else []
        technical = competencies[6:] if len(competencies) > 6 else []
        if not skills and competencies:
            skills = competencies
            technical = []
        if skills:
            _add_title_op(right_ops, "Skills")
            for item in skills:
                _add_text_ops(right_ops, f"- {item}", right_width, font_name="Helvetica", font_size=9, leading=12)
            _add_gap_op(right_ops, 4 if technical else 6)
        if technical:
            _add_title_op(right_ops, "Technical Proficiencies")
            for item in technical:
                _add_text_ops(right_ops, f"- {item}", right_width, font_name="Helvetica", font_size=9, leading=12)
            _add_gap_op(right_ops, 4)
    else:
        _add_title_op(right_ops, "Core Competencies")
        for item in competencies:
            _add_text_ops(right_ops, f"- {item}", right_width, font_name="Helvetica", font_size=9, leading=12)
        _add_gap_op(right_ops, 4)

    _add_title_op(right_ops, "Languages")
    for item in cv.get("languages") or []:
        _add_text_ops(right_ops, f"- {item}", right_width, font_name="Helvetica", font_size=9, leading=12)
    _add_gap_op(right_ops, 4)

    if layout_style in ("sidebar_skillset", "slate_profile"):
        _add_title_op(left_ops, "Certifications")
        for item in cv.get("certifications") or []:
            _add_text_ops(left_ops, f"- {item}", left_width, font_name="Helvetica", font_size=9, leading=12)
        _add_gap_op(left_ops, 4)
        _add_title_op(left_ops, "Referees")
        _build_referee_ops(cv, left_ops, left_width)
    else:
        _add_title_op(right_ops, "Certifications")
        for item in cv.get("certifications") or []:
            _add_text_ops(right_ops, f"- {item}", right_width, font_name="Helvetica", font_size=9, leading=12)
        _add_gap_op(right_ops, 4)
        _add_title_op(right_ops, "Referees")
        _build_referee_ops(cv, right_ops, right_width)

    def render_op(op: dict, x: float, y: float, column: str) -> float:
        is_sidebar_column = layout_style in {"sidebar_skillset", "slate_profile"} and column == "sidebar"
        if op["kind"] == "title":
            return draw_pdf_section_title(
                pdf, op["title"], x, y,
                title_color=sidebar_section_title_color if is_sidebar_column else section_title_color,
                line_color=sidebar_section_line_color if is_sidebar_column else section_line_color,
            )
        if op["kind"] == "line":
            pdf.setFillColor(sidebar_text_color if is_sidebar_column else text_color)
            pdf.setFont(op["font_name"], op["font_size"])
            pdf.drawString(x, y, op["text"])
            return y - op["leading"]
        return y - op["height"]

    left_index = 0
    right_index = 0
    y_left, y_right = draw_page_layout(first_page=True)

    prev_left = -1
    prev_right = -1
    while left_index < len(left_ops) or right_index < len(right_ops):
        while left_index < len(left_ops):
            op = left_ops[left_index]
            if y_left - op["height"] < bottom:
                break
            y_left = render_op(op, left_x, y_left, "main")
            left_index += 1

        while right_index < len(right_ops):
            op = right_ops[right_index]
            if y_right - op["height"] < bottom:
                break
            y_right = render_op(op, right_x, y_right, "sidebar")
            right_index += 1

        if left_index >= len(left_ops) and right_index >= len(right_ops):
            break

        # Safety guard: if no progress was made, force-render the blocking op
        # to prevent an infinite loop when a single op exceeds page height.
        if left_index == prev_left and right_index == prev_right:
            if left_index < len(left_ops):
                y_left = render_op(left_ops[left_index], left_x, y_left, "main")
                left_index += 1
            if right_index < len(right_ops):
                y_right = render_op(right_ops[right_index], right_x, y_right, "sidebar")
                right_index += 1
            continue

        prev_left = left_index
        prev_right = right_index
        pdf.showPage()
        y_left, y_right = draw_page_layout(first_page=False)

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Op helpers (used by two-column builder)
# ---------------------------------------------------------------------------

def _add_title_op(ops: list[dict], title: str) -> None:
    ops.append({"kind": "title", "title": title, "height": 32})


def _add_gap_op(ops: list[dict], gap_size: int) -> None:
    if gap_size > 0:
        ops.append({"kind": "gap", "height": gap_size})


def _add_text_ops(
    ops: list[dict],
    text: str,
    max_width: float,
    font_name: str = "Helvetica",
    font_size: int = 10,
    leading: int = 13,
) -> None:
    for line in wrap_pdf_text(text, font_name, font_size, max_width):
        ops.append(
            {
                "kind": "line",
                "text": line,
                "font_name": font_name,
                "font_size": font_size,
                "leading": leading,
                "height": leading,
            }
        )
