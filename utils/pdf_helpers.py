try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfgen import canvas

    REPORTLAB_AVAILABLE = True
except ModuleNotFoundError:
    colors = None
    A4 = None
    pdfmetrics = None
    canvas = None
    REPORTLAB_AVAILABLE = False


# Section icon shapes drawn natively via ReportLab canvas (no font needed).
# Each value is a callable: draw_fn(pdf, x, center_y, size, color)
def _draw_icon_circle(pdf, x, cy, size, color):
    pdf.setFillColor(color)
    pdf.circle(x + size / 2, cy, size / 2, fill=1, stroke=0)

def _draw_icon_diamond(pdf, x, cy, size, color):
    pdf.setFillColor(color)
    hs = size / 2
    p = pdf.beginPath()
    p.moveTo(x + hs, cy + hs)
    p.lineTo(x + size, cy)
    p.lineTo(x + hs, cy - hs)
    p.lineTo(x, cy)
    p.close()
    pdf.drawPath(p, fill=1, stroke=0)

def _draw_icon_square(pdf, x, cy, size, color):
    pdf.setFillColor(color)
    pdf.rect(x, cy - size / 2, size, size, fill=1, stroke=0)

def _draw_icon_bar(pdf, x, cy, size, color):
    pdf.setFillColor(color)
    pdf.rect(x, cy - size * 0.35, size * 0.35, size * 0.7, fill=1, stroke=0)

def _draw_icon_triangle(pdf, x, cy, size, color):
    pdf.setFillColor(color)
    hs = size / 2
    p = pdf.beginPath()
    p.moveTo(x + hs, cy + hs)
    p.lineTo(x + size, cy - hs)
    p.lineTo(x, cy - hs)
    p.close()
    pdf.drawPath(p, fill=1, stroke=0)

def _draw_icon_star(pdf, x, cy, size, color):
    """Simple 4-point star using two overlapping squares."""
    pdf.setFillColor(color)
    hs = size / 2
    # rotated square
    p = pdf.beginPath()
    p.moveTo(x + hs, cy + hs)
    p.lineTo(x + size, cy)
    p.lineTo(x + hs, cy - hs)
    p.lineTo(x, cy)
    p.close()
    pdf.drawPath(p, fill=1, stroke=0)
    # small inner square
    q = size * 0.25
    pdf.rect(x + hs - q, cy - q, q * 2, q * 2, fill=1, stroke=0)


SECTION_ICON_SHAPES: dict[str, callable] = {
    "Profile": _draw_icon_circle,
    "Core Competencies": _draw_icon_diamond,
    "Professional Experience": _draw_icon_bar,
    "Projects": _draw_icon_square,
    "Education": _draw_icon_triangle,
    "Certifications": _draw_icon_star,
    "Languages": _draw_icon_circle,
    "Referees": _draw_icon_diamond,
    "Contact": _draw_icon_circle,
    "Personal Details": _draw_icon_circle,
    "Skills": _draw_icon_diamond,
    "Technical Proficiencies": _draw_icon_square,
}

# Unicode emoji icons for HTML section headers (rendered by the browser).
SECTION_ICONS_HTML: dict[str, str] = {
    "Profile": "\U0001F464",           # bust in silhouette
    "Core Competencies": "\U0001F4A1", # light bulb
    "Professional Experience": "\U0001F4BC",  # briefcase
    "Projects": "\U0001F680",          # rocket
    "Education": "\U0001F393",         # graduation cap
    "Certifications": "\U0001F3C6",    # trophy
    "Languages": "\U0001F310",         # globe
    "Referees": "\U0001F465",          # busts in silhouette
}


def pdf_safe_text(value: str) -> str:
    text = str(value).replace("\n", " ")
    # Normalize Unicode dashes/hyphens to ASCII hyphen-minus so they
    # survive the latin-1 encoding instead of becoming '?'
    text = (
        text
        .replace("\u2010", "-")   # hyphen
        .replace("\u2011", "-")   # non-breaking hyphen
        .replace("\u2012", "-")   # figure dash
        .replace("\u2013", "-")   # en-dash
        .replace("\u2014", "-")   # em-dash
        .replace("\u2015", "-")   # horizontal bar
        .replace("\u2212", "-")   # minus sign
        .replace("\u00ad", "-")   # soft hyphen
        .replace("\u2018", "'")   # left single quote
        .replace("\u2019", "'")   # right single quote
        .replace("\u201c", '"')   # left double quote
        .replace("\u201d", '"')   # right double quote
        .replace("\u2026", "...") # ellipsis
        .replace("\u2022", "-")   # bullet
    )
    return text.encode("latin-1", "replace").decode("latin-1")


def wrap_pdf_text(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    if not REPORTLAB_AVAILABLE:
        return [pdf_safe_text(text)]
    words = pdf_safe_text(text).split()
    if not words:
        return []

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_pdf_wrapped_text(
    pdf,
    text: str,
    x: float,
    y: float,
    max_width: float,
    bottom_margin: float,
    top_reset: float,
    font_name: str = "Helvetica",
    font_size: int = 10,
    leading: int = 13,
    on_new_page=None,
) -> float:
    pdf.setFont(font_name, font_size)
    for line in wrap_pdf_text(text, font_name, font_size, max_width):
        if y < bottom_margin:
            pdf.showPage()
            y = on_new_page() if callable(on_new_page) else top_reset
            pdf.setFont(font_name, font_size)
        pdf.drawString(x, y, line)
        y -= leading
    return y


def draw_pdf_section_title(
    pdf,
    title: str,
    x: float,
    y: float,
    font_size: int = 12,
    title_color=None,
    line_color=None,
) -> float:
    if not REPORTLAB_AVAILABLE:
        return y
    resolved_title_color = title_color or colors.HexColor("#1E3A5F")
    icon_fn = SECTION_ICON_SHAPES.get(title)
    icon_advance = 0
    if icon_fn:
        icon_size = font_size * 0.7
        icon_fn(pdf, x, y + font_size * 0.2, icon_size, resolved_title_color)
        icon_advance = icon_size + 5
    title_x = x + icon_advance
    title_text = pdf_safe_text(title)
    pdf.setFillColor(resolved_title_color)
    pdf.setFont("Helvetica-Bold", font_size)
    pdf.drawString(title_x, y, title_text)
    title_width = pdfmetrics.stringWidth(title_text, "Helvetica-Bold", font_size)
    pdf.setStrokeColor(line_color or colors.HexColor("#BFD7ED"))
    pdf.setLineWidth(1)
    pdf.line(x, y - 3, title_x + title_width + 4, y - 3)
    return y - 16


def safe_round_rect(pdf, x: float, y: float, width: float, height: float, radius: float, fill: int = 0, stroke: int = 1) -> None:
    safe_radius = min(radius, abs(width) / 2, abs(height) / 2)
    pdf.roundRect(x, y, width, height, safe_radius, fill=fill, stroke=stroke)


def ensure_pdf_space(pdf, y: float, needed_height: float, bottom_margin: float, top_reset: float, on_new_page=None) -> float:
    if y - needed_height < bottom_margin:
        pdf.showPage()
        return on_new_page() if callable(on_new_page) else top_reset
    return y
