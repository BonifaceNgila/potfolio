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


def pdf_safe_text(value: str) -> str:
    return str(value).replace("\n", " ").encode("latin-1", "replace").decode("latin-1")


def wrap_pdf_text(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    if not REPORTLAB_AVAILABLE:
        return [pdf_safe_text(text)]
    words = pdf_safe_text(text).split()
    if not words:
        return [""]

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
    title_x = x
    pdf.setFillColor(title_color or colors.HexColor("#1E3A5F"))
    pdf.setFont("Helvetica-Bold", font_size)
    pdf.drawString(title_x, y, pdf_safe_text(title))
    pdf.setStrokeColor(line_color or colors.HexColor("#BFD7ED"))
    pdf.setLineWidth(1)
    pdf.line(title_x, y - 3, title_x + 130, y - 3)
    return y - 16


def safe_round_rect(pdf, x: float, y: float, width: float, height: float, radius: float, fill: int = 0, stroke: int = 1) -> None:
    safe_radius = min(radius, abs(width) / 2, abs(height) / 2)
    pdf.roundRect(x, y, width, height, safe_radius, fill=fill, stroke=stroke)


def draw_section_card(pdf, x: float, y: float, width: float, height: float, fill, border) -> float:
    pdf.setFillColor(fill)
    pdf.setStrokeColor(border)
    pdf.setLineWidth(1)
    safe_round_rect(pdf, x, y - height, width, height, 12, fill=1, stroke=0)
    pdf.setStrokeColor(border)
    safe_round_rect(pdf, x, y - height, width, height, 12, fill=0, stroke=1)
    return y - height - 14


def ensure_pdf_space(pdf, y: float, needed_height: float, bottom_margin: float, top_reset: float, on_new_page=None) -> float:
    if y - needed_height < bottom_margin:
        pdf.showPage()
        return on_new_page() if callable(on_new_page) else top_reset
    return y
