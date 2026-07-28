from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent


def load_css():

    css_folder = BASE_DIR / "styles"

    css_files = [
        "theme.css",
        "layout.css",
        "header.css",
        "sidebar.css",
        "search.css",
        "jobcard.css",
        "footer.css",
        "responsive.css",
    ]

    css = ""

    for file in css_files:

        path = css_folder / file

        if path.exists():

            with open(path, encoding="utf-8") as f:

                css += f.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )