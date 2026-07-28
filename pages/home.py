"""
=========================================================
VisionBoard Career Portal
Home Page
=========================================================
"""

import math
import streamlit as st

from database.db_service import (
    get_jobs_by_category,
    search_jobs,
)

from components.job_card import show_job_card


# ==========================================================
# Home Page
# ==========================================================

def show_home(
    category,
    keyword,
    employment_type,
    posted,
    source,
    sort_by,
):

    # ------------------------------------------------------
    # Load Jobs
    # ------------------------------------------------------

    with st.spinner("Loading latest opportunities..."):

        if keyword.strip():

            jobs = search_jobs(
                keyword=keyword,
                category=category,
            )

        else:

            jobs = get_jobs_by_category(
                category=category,
                limit=500,
            )

    # ------------------------------------------------------
    # India / Rest of World Filter
    # ------------------------------------------------------

    if category == "India":

        jobs = [
            j for j in jobs
            if "india" in str(j.get("country", "")).lower()
            or "india" in str(j.get("location", "")).lower()
        ]

    elif category == "Rest of World":

        jobs = [
            j for j in jobs
            if "india" not in str(j.get("country", "")).lower()
            and "india" not in str(j.get("location", "")).lower()
        ]

    # ------------------------------------------------------
    # Employment Filter
    # ------------------------------------------------------

    if employment_type != "All":

        jobs = [
            j for j in jobs
            if employment_type.lower()
            in str(j.get("employment_type", "")).lower()
        ]

    # ------------------------------------------------------
    # Source Filter
    # ------------------------------------------------------

    if source != "All":

        jobs = [
            j for j in jobs
            if source.lower()
            == str(j.get("source", "")).lower()
        ]

    # ------------------------------------------------------
    # Sort by Company / Latest
    # ------------------------------------------------------

    if sort_by == "Company":

        jobs = sorted(
            jobs,
            key=lambda x: str(x.get("company", "")).lower()
        )

    elif sort_by == "Latest":

        jobs = sorted(
            jobs,
            key=lambda x: str(x.get("posted_date", "")),
            reverse=True,
        )

    # ------------------------------------------------------
    # India First Priority
    # ------------------------------------------------------

    INDIA_CITIES = [
        "bangalore",
        "bengaluru",
        "hyderabad",
        "pune",
        "mumbai",
        "delhi",
        "new delhi",
        "gurgaon",
        "gurugram",
        "noida",
        "chennai",
        "kolkata",
        "ahmedabad",
        "kochi",
        "cochin",
        "trivandrum",
        "thiruvananthapuram",
        "coimbatore",
        "mysore",
        "india",
    ]

    india_jobs = []
    world_jobs = []

    for job in jobs:

        text = (
            str(job.get("country", "")) + " " +
            str(job.get("location", ""))
        ).lower()

        if any(city in text for city in INDIA_CITIES):
            india_jobs.append(job)
        else:
            world_jobs.append(job)

    jobs = india_jobs + world_jobs

    # ------------------------------------------------------
    # Header
    # ------------------------------------------------------

    col1, col2 = st.columns([4, 1])

    with col1:

        st.markdown("## 💼 Latest Opportunities")

        st.caption(
            f"{len(jobs)} verified jobs from trusted job portals"
        )

    with col2:

        show_all = st.checkbox(
            "Show All",
            value=False,
        )

    st.divider()

    # ------------------------------------------------------
    # No Jobs
    # ------------------------------------------------------

    if len(jobs) == 0:

        st.warning("No matching jobs found.")

        return

    # ------------------------------------------------------
    # Pagination
    # ------------------------------------------------------

    if show_all:

        jobs_to_show = jobs

        st.success(f"Showing all {len(jobs)} jobs")

    else:

        PAGE_SIZE = 10

        total_pages = max(
            1,
            math.ceil(len(jobs) / PAGE_SIZE)
        )

        if "page" not in st.session_state:
            st.session_state.page = 1

        page = st.session_state.page

        if page > total_pages:
            page = total_pages
            st.session_state.page = page

        start = (page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE

        jobs_to_show = jobs[start:end]

        left, middle, right = st.columns([2, 4, 2])

        with left:

            if st.button(
                "⬅ Previous",
                disabled=(page == 1),
            ):

                st.session_state.page -= 1
                st.rerun()

        with middle:

            st.markdown(
                f"""
                <div style="
                text-align:center;
                font-weight:600;
                padding-top:8px;
                ">
                Page {page} of {total_pages}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:

            if st.button(
                "Next ➜",
                disabled=(page == total_pages),
            ):

                st.session_state.page += 1
                st.rerun()

        st.info(
            f"Showing {start+1}-{min(end,len(jobs))} of {len(jobs)} jobs"
        )

    # ------------------------------------------------------
    # Job Cards
    # ------------------------------------------------------

    for job in jobs_to_show:

        show_job_card(job)

        st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------
    # Footer Summary
    # ------------------------------------------------------

    st.divider()

    st.caption(
        f"VisionBoard Career Portal • {len(jobs)} Live Opportunities"
    )