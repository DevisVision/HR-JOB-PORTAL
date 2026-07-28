"""
components/filters.py
"""

import streamlit as st


def show_filters():

    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

    with c1:
        keyword = st.text_input(
            "Search",
            placeholder="Python, Azure, Databricks, Spark...",
            label_visibility="collapsed",
        )

    with c2:
        category = st.selectbox(
            "Category",
            [
                "All Jobs",
                "India",
                "Rest of World",
                "Remote",
            ],
            label_visibility="collapsed",
        )

    with c3:
        employment = st.selectbox(
            "Employment",
            [
                "All",
                "Full Time",
                "Contract",
                "Internship",
                "Hybrid",
            ],
            label_visibility="collapsed",
        )

    with c4:
        search_clicked = st.button(
            "🔍 Search",
            use_container_width=True,
        )

    return (
        keyword,
        category,
        employment,
        search_clicked,
    )