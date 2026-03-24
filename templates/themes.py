import re

from utils.pdf_helpers import REPORTLAB_AVAILABLE

if REPORTLAB_AVAILABLE:
    from reportlab.lib import colors
else:
    colors = None


AVAILABLE_TEMPLATES = [
    "One Column - Classic",
    "One Column - Minimal",
    "Two Column - Professional",
    "Two Column - Sidebar",
    "Two Column - Sidebar Skillset",
    "Two Column - Accent Panel",
    "Two Column - Slate Profile",
]

DISPLAY_TEMPLATE_OPTIONS = {
    template.replace(" - ", " \u2022 "): template for template in AVAILABLE_TEMPLATES
}


def _merge_pdf_theme(base: dict, overrides: dict) -> dict:
    merged = base.copy()
    merged.update(overrides)
    return merged


if REPORTLAB_AVAILABLE:
    PDF_BASE_TWO_COLUMN_THEME = {
        "background": colors.HexColor("#e9eef5"),
        "hero_background": colors.HexColor("#1e3a5f"),
        "hero_accent": colors.HexColor("#274c77"),
        "hero_strip": colors.HexColor("#93c5fd"),
        "panel_primary": colors.HexColor("#ffffff"),
        "panel_secondary": colors.HexColor("#f8fbff"),
        "text_color": colors.HexColor("#0f172a"),
        "hero_text": colors.white,
        "panel_border": colors.HexColor("#d6e3f2"),
        "layout": "professional_header",
    }

    PDF_BASE_ONE_COLUMN_THEME = {
        "background": colors.HexColor("#f8fafc"),
        "hero_background": colors.HexColor("#ffffff"),
        "hero_accent": colors.HexColor("#c7d2fe"),
        "hero_strip": colors.HexColor("#1d4ed8"),
        "panel_primary": colors.HexColor("#ffffff"),
        "panel_secondary": colors.HexColor("#f1f5f9"),
        "text_color": colors.HexColor("#0f172a"),
        "hero_text": colors.HexColor("#0f172a"),
    }

    PDF_TEMPLATE_THEMES = {
        "Two Column - Professional": _merge_pdf_theme(
            PDF_BASE_TWO_COLUMN_THEME,
            {
                "layout": "professional_header",
            },
        ),
        "Two Column - Sidebar": _merge_pdf_theme(
            PDF_BASE_TWO_COLUMN_THEME,
            {
                "background": colors.HexColor("#0f172a"),
                "hero_background": colors.HexColor("#111827"),
                "hero_accent": colors.HexColor("#1f2937"),
                "hero_strip": colors.HexColor("#60a5fa"),
                "panel_primary": colors.HexColor("#fefefe"),
                "panel_secondary": colors.HexColor("#f4f6fb"),
                "text_color": colors.HexColor("#0f172a"),
                "hero_text": colors.HexColor("#f8fafc"),
                "panel_border": colors.HexColor("#d6e3f2"),
                "layout": "modern_header",
            },
        ),
        "Two Column - Sidebar Skillset": _merge_pdf_theme(
            PDF_BASE_TWO_COLUMN_THEME,
            {
                "background": colors.HexColor("#f0f2f5"),
                "hero_background": colors.HexColor("#0f172a"),
                "hero_accent": colors.HexColor("#1e293b"),
                "hero_strip": colors.HexColor("#60a5fa"),
                "panel_primary": colors.HexColor("#ffffff"),
                "panel_secondary": colors.HexColor("#f8fafc"),
                "text_color": colors.HexColor("#0f172a"),
                "hero_text": colors.HexColor("#f8fafc"),
                "panel_border": colors.HexColor("#dbe5f0"),
                "layout": "sidebar_skillset",
                "sidebar_text_color": colors.HexColor("#e2e8f0"),
                "sidebar_section_title_color": colors.HexColor("#bfdbfe"),
                "sidebar_section_line_color": colors.HexColor("#334155"),
            },
        ),
        "Two Column - Accent Panel": _merge_pdf_theme(
            PDF_BASE_TWO_COLUMN_THEME,
            {
                "background": colors.HexColor("#f5f7fb"),
                "hero_background": colors.HexColor("#102a43"),
                "hero_accent": colors.HexColor("#1e3a8a"),
                "hero_strip": colors.HexColor("#bae6fd"),
                "panel_primary": colors.HexColor("#ffffff"),
                "panel_secondary": colors.HexColor("#eef2ff"),
                "text_color": colors.HexColor("#0f172a"),
                "hero_text": colors.HexColor("#f8fafc"),
                "panel_border": colors.HexColor("#d6e3f2"),
                "layout": "modern_header",
            },
        ),
        "Two Column - Slate Profile": _merge_pdf_theme(
            PDF_BASE_TWO_COLUMN_THEME,
            {
                "background": colors.HexColor("#eceef1"),
                "hero_background": colors.HexColor("#0f172a"),
                "hero_accent": colors.HexColor("#1e293b"),
                "hero_strip": colors.HexColor("#cbd5f5"),
                "panel_primary": colors.HexColor("#ffffff"),
                "panel_secondary": colors.HexColor("#f1f5f9"),
                "text_color": colors.HexColor("#0f172a"),
                "hero_text": colors.HexColor("#f8fafc"),
                "panel_border": colors.HexColor("#d6e3f2"),
                "layout": "slate_profile",
                "sidebar_background": colors.HexColor("#f1f3f5"),
                "sidebar_border": colors.HexColor("#d6d8dc"),
                "sidebar_text_color": colors.HexColor("#1f2937"),
                "sidebar_section_title_color": colors.HexColor("#0f172a"),
                "sidebar_section_line_color": colors.HexColor("#d6d8dc"),
            },
        ),
        "One Column - Classic": _merge_pdf_theme(
            PDF_BASE_ONE_COLUMN_THEME,
            {
                "background": colors.HexColor("#030712"),
                "hero_background": colors.HexColor("#102a43"),
                "hero_accent": colors.HexColor("#1e3a8a"),
                "hero_strip": colors.HexColor("#2563eb"),
                "panel_primary": colors.HexColor("#0f172a"),
                "panel_secondary": colors.HexColor("#0f172a"),
                "text_color": colors.HexColor("#e2e8f0"),
                "hero_text": colors.HexColor("#f8fafc"),
                "border": colors.HexColor("#1d4ed8"),
                "link_color": colors.HexColor("#38bdf8"),
                "layout": "classic_hero",
            },
        ),
        "One Column - Minimal": _merge_pdf_theme(
            PDF_BASE_ONE_COLUMN_THEME,
            {
                "hero_accent": colors.HexColor("#93c5fd"),
                "hero_text": colors.HexColor("#0f172a"),
                "text_color": colors.HexColor("#0f172a"),
                "layout": "minimal_clean",
            },
        ),
    }
else:
    PDF_BASE_TWO_COLUMN_THEME = {}
    PDF_BASE_ONE_COLUMN_THEME = {}
    PDF_TEMPLATE_THEMES = {}


DISPLAY_TO_PDF_TEMPLATE_MAP = {template: template for template in DISPLAY_TEMPLATE_OPTIONS.values()}


def validate_template_mappings() -> list[str]:
    issues: list[str] = []
    display_templates = set(DISPLAY_TEMPLATE_OPTIONS.values())
    available_templates = set(AVAILABLE_TEMPLATES)

    missing_in_selector = sorted(available_templates - display_templates)
    if missing_in_selector:
        issues.append(f"Missing selector entries: {', '.join(missing_in_selector)}")

    extra_in_selector = sorted(display_templates - available_templates)
    if extra_in_selector:
        issues.append(f"Unknown selector entries: {', '.join(extra_in_selector)}")

    missing_pdf_themes = sorted(display_templates - set(PDF_TEMPLATE_THEMES.keys()))
    if missing_pdf_themes and REPORTLAB_AVAILABLE:
        issues.append(f"Missing PDF theme mappings: {', '.join(missing_pdf_themes)}")

    missing_pdf_map = sorted(display_templates - set(DISPLAY_TO_PDF_TEMPLATE_MAP.keys()))
    if missing_pdf_map:
        issues.append(f"Missing display-to-PDF mappings: {', '.join(missing_pdf_map)}")

    return issues


def normalize_template_name(template: str) -> str:
    value = str(template or "").strip()
    if not value:
        return value
    if value in DISPLAY_TEMPLATE_OPTIONS:
        return DISPLAY_TEMPLATE_OPTIONS[value]
    if "\u2022" in value:
        value = value.replace(" \u2022 ", " - ").replace("\u2022", "-")
    value = re.sub(r"\s*-\s*", " - ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def get_pdf_theme(template: str) -> dict:
    normalized_template = normalize_template_name(template)
    mapped_template = DISPLAY_TO_PDF_TEMPLATE_MAP.get(normalized_template, normalized_template)
    if mapped_template in PDF_TEMPLATE_THEMES:
        return PDF_TEMPLATE_THEMES[mapped_template]
    if "Two Column" in mapped_template:
        return PDF_TEMPLATE_THEMES.get("Two Column - Professional", {})
    if "One Column" in mapped_template:
        return PDF_TEMPLATE_THEMES.get("One Column - Classic", {})
    return PDF_TEMPLATE_THEMES.get("One Column - Minimal", {})
