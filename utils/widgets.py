from inspect import signature

import streamlit as st


TEXT_FORMATTERS = [
    "bold",
    "italic",
    "code",
    "link",
    "ordered_list",
    "unordered_list",
    "quote",
]

TEXT_AREA_SUPPORTS_FORMATTERS = "text_formatters" in signature(st.text_area).parameters


def rich_text_area(label: str, value: str, height: int, **kwargs) -> str:
    params = {"value": value, "height": height}
    params.update(kwargs)
    if TEXT_AREA_SUPPORTS_FORMATTERS:
        params["text_formatters"] = TEXT_FORMATTERS
    return st.text_area(label, **params)
