"""
pages/home.py
"""

import math
import streamlit as st

from database.db_service import (
    search_jobs,
    get_latest_india_jobs,
    get_latest_global_jobs,
)

from components.job_card import show_job_card


def show_home(
    keyword,
    category,
    employment,
    source,
    posted,
):

    # =====================================================
    # Load Jobs
    # =====================================================

    if keyword.strip():

        jobs = search_jobs(
            keyword=keyword,
            category=category,
        )

    else:

        if category == "India":

            jobs = get_latest_india_jobs(limit=200)

        elif category == "Rest of World":

            jobs = get_latest_global_jobs(limit=200)

        else:

            jobs = (
                get_latest_india_jobs(limit=200)
                + get_latest_global_jobs(limit=200)
            )

    # =====================================================
    # Employment Filter
    # =====================================================

    if employment != "All":

        jobs = [
            j
            for j in jobs
            if employment.lower()
            in str(
                j.get(
                    "employment_type",
                    "",
                )
            ).lower()
        ]

    # =====================================================
    # Source Filter
    # =====================================================

    if source != "All":

        jobs = [
            j
            for j in jobs
            if source.lower()
            == str(
                j.get(
                    "source",
                    "",
                )
            ).lower()
        ]

    # =====================================================
    # Posted Filter
    # =====================================================

    if posted == "24 Hours":

        jobs = jobs[:25]

    elif posted == "3 Days":

        jobs = jobs[:75]

    elif posted == "7 Days":

        jobs = jobs[:150]

    # =====================================================
    # Header
    # =====================================================

    st.markdown(
        f"""
        <h3 style="margin-bottom:0;">
            {len(jobs)} Live Jobs
        </h3>

        <p style="color:#64748B;">
            Updated automatically every 6 hours
        </p>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # Toolbar
    # =====================================================

    left, right = st.columns([3, 1])

    with left:

        sort = st.selectbox(
            "Sort",
            [
                "Latest",
                "Company",
                "Location",
            ],
        )

    with right:

        page_size = st.selectbox(
            "Jobs / Page",
            [
                10,
                20,
                50,
            ],
            index=0,
        )

    # =====================================================
    # Sorting
    # =====================================================

    if sort == "Company":

        jobs = sorted(
            jobs,
            key=lambda x: x.get("company", ""),
        )

    elif sort == "Location":

        jobs = sorted(
            jobs,
            key=lambda x: x.get("location", ""),
        )

    # =====================================================
    # Pagination
    # =====================================================

    total_pages = max(
        1,
        math.ceil(len(jobs) / page_size),
    )

    if "page" not in st.session_state:

        st.session_state.page = 1

    p1, p2, p3 = st.columns([1, 6, 1])

    with p1:

        if st.button("⬅ Previous"):

            if st.session_state.page > 1:

                st.session_state.page -= 1

    with p3:

        if st.button("Next ➜"):

            if st.session_state.page < total_pages:

                st.session_state.page += 1

    page = st.session_state.page

    start = (page - 1) * page_size
    end = start + page_size

    # =====================================================
    # Job Cards
    # =====================================================

    for job in jobs[start:end]:

        show_job_card(job)

        st.write("")

    # =====================================================
    # Footer
    # =====================================================

    st.divider()

    st.caption(
        f"Showing {start+1}-{min(end,len(jobs))} of {len(jobs)} jobs | Page {page} of {total_pages}"
    )