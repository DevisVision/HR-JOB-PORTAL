"""
=========================================================
VisionBoard Career Portal
Professional Search & Filters
=========================================================
"""

import streamlit as st


def show_filters():

    st.markdown("## 🔎 Search Jobs")

    search, location = st.columns([4, 2])

    with search:
        keyword = st.text_input(
            "Search",
            placeholder="Python, Azure, Databricks, Spark, GenAI...",
            label_visibility="collapsed",
        )

    with location:
        job_location = st.selectbox(
            "Location",
            [
                "All Jobs",
                "India",
                "Rest of World",
                "Remote",
            ],
            label_visibility="collapsed",
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        employment = st.selectbox(
            "Employment",
            [
                "All",
                "Full Time",
                "Part Time",
                "Contract",
                "Internship",
            ],
        )

    with c2:
        source = st.selectbox(
            "Source",
            [
                "All",
                "Adzuna",
                "ArbeitNow",
            ],
        )

    with c3:
        sort_by = st.selectbox(
            "Sort By",
            [
                "Latest",
                "Relevance",
                "Company",
            ],
        )

    with st.expander("⚙ Advanced Filters", expanded=False):

        a1, a2 = st.columns(2)

        with a1:

            experience = st.selectbox(
                "Experience",
                [
                    "All",
                    "Fresher",
                    "1-3 Years",
                    "3-5 Years",
                    "5+ Years",
                ],
            )

            salary = st.selectbox(
                "Salary",
                [
                    "Any",
                    "5 LPA+",
                    "10 LPA+",
                    "20 LPA+",
                    "30 LPA+",
                ],
            )

        with a2:

            work_mode = st.selectbox(
                "Work Mode",
                [
                    "All",
                    "Remote",
                    "Hybrid",
                    "Onsite",
                ],
            )

            posted = st.selectbox(
                "Posted Within",
                [
                    "Any Time",
                    "24 Hours",
                    "3 Days",
                    "7 Days",
                    "30 Days",
                ],
            )

    st.divider()

    return (
        job_location,
        keyword,
        employment,
        posted,
        source,
        sort_by,
    )