"""
=========================================================
VisionBoard Career Portal
Home Page
=========================================================
Professional Home Page
=========================================================
"""

import math
import streamlit as st

from database.db_service import (
    search_jobs,
    get_jobs_paginated,
    get_total_job_count,
)

from services.ranking import rank_jobs

from components.job_card import show_job_card


# =========================================================
# HOME PAGE
# =========================================================

def show_home(
    category,
    keyword,
    employment_type,
    posted,
    source,
    sort_by,
):

    # -----------------------------------------------------
    # Session State
    # -----------------------------------------------------

    if "page" not in st.session_state:

        st.session_state.page = 1

    PAGE_SIZE = 10

    # -----------------------------------------------------
    # Reset Page when Search Changes
    # -----------------------------------------------------

    current_filter = (
        category,
        keyword,
        employment_type,
        posted,
        source,
        sort_by,
    )

    if (
        "last_filter" not in st.session_state
        or st.session_state.last_filter != current_filter
    ):

        st.session_state.page = 1

        st.session_state.last_filter = current_filter

    page = st.session_state.page

    offset = (page - 1) * PAGE_SIZE

    # -----------------------------------------------------
    # Load Jobs
    # -----------------------------------------------------

    with st.spinner("Loading latest opportunities..."):

        if keyword.strip():

            jobs = search_jobs(

                keyword=keyword,

                category=category,

                employment_type=employment_type,

                source=source,

                limit=1000,

                offset=0,

            )

        else:

            jobs = get_jobs_paginated(

                page=1,

                page_size=1000,

            )

    # -----------------------------------------------------
    # Ranking Engine
    # -----------------------------------------------------

    jobs = rank_jobs(jobs)

    # -----------------------------------------------------
    # Posted Filter
    # -----------------------------------------------------

    if posted != "Any Time":

        if posted == "Today":

            jobs = jobs[:50]

        elif posted == "Last 7 Days":

            jobs = jobs[:200]

    # -----------------------------------------------------
    # Sort
    # -----------------------------------------------------

    if sort_by == "Company":

        jobs = sorted(

            jobs,

            key=lambda x: str(
                x.get("company", "")
            ).lower(),

        )

    elif sort_by == "Latest":

        jobs = sorted(

            jobs,

            key=lambda x: str(
                x.get("posted_date", "")
            ),

            reverse=True,

        )

    elif sort_by == "Location":

        jobs = sorted(

            jobs,

            key=lambda x: str(
                x.get("location", "")
            ).lower(),

        )

    # -----------------------------------------------------
    # Total Jobs
    # -----------------------------------------------------

    total_jobs = len(jobs)

    total_pages = max(

        1,

        math.ceil(total_jobs / PAGE_SIZE)

    )

    if page > total_pages:

        page = total_pages

        st.session_state.page = page

    start = (page - 1) * PAGE_SIZE

    end = start + PAGE_SIZE

    jobs_to_show = jobs[start:end]
    # -----------------------------------------------------
    # Categorize Jobs
    # -----------------------------------------------------

    INDIA_KEYWORDS = [
        "india",
        "bangalore",
        "bengaluru",
        "hyderabad",
        "pune",
        "mumbai",
        "chennai",
        "gurgaon",
        "gurugram",
        "noida",
        "kochi",
        "cochin",
        "kolkata",
        "ahmedabad",
        "mysore",
        "trivandrum",
        "thiruvananthapuram",
    ]

    REMOTE_KEYWORDS = [
        "remote",
        "work from home",
        "wfh",
        "anywhere",
    ]

    FORTUNE_COMPANIES = [
        "IBM",
        "ACCENTURE",
        "COGNIZANT",
        "CAPGEMINI",
        "EY",
        "KPMG",
        "DELOITTE",
        "PWC",
        "UST",
        "MICROSOFT",
        "GOOGLE",
        "AMAZON",
        "ORACLE",
        "CISCO",
        "ALLIANZ",
        "WIPRO",
        "INFOSYS",
        "TCS",
        "HCL",
        "TECH MAHINDRA",
    ]

    india_jobs = []
    fortune_jobs = []
    remote_jobs = []
    abroad_jobs = []

    for job in jobs:

        company = str(job.get("company", "")).upper()

        location = (
            str(job.get("country", "")) +
            " " +
            str(job.get("location", ""))
        ).lower()

        description = str(job.get("description", "")).lower()

        # Fortune Companies
        if any(c in company for c in FORTUNE_COMPANIES):

            fortune_jobs.append(job)

            continue

        # India Jobs
        if any(city in location for city in INDIA_KEYWORDS):

            india_jobs.append(job)

            continue

        # Remote Jobs
        if any(word in location for word in REMOTE_KEYWORDS):

            remote_jobs.append(job)

            continue

        if any(word in description for word in REMOTE_KEYWORDS):

            remote_jobs.append(job)

            continue

        # Abroad
        abroad_jobs.append(job)

    # -----------------------------------------------------
    # Final Ordering
    # -----------------------------------------------------

    jobs = (
        india_jobs +
        fortune_jobs +
        remote_jobs +
        abroad_jobs
    )

    total_jobs = len(jobs)

    total_pages = max(
        1,
        math.ceil(total_jobs / PAGE_SIZE)
    )

    start = (page - 1) * PAGE_SIZE

    end = start + PAGE_SIZE

    jobs_to_show = jobs[start:end]

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    left, right = st.columns([4, 1])

    with left:

        st.markdown(
            """
## 💼 Latest Career Opportunities
"""
        )

        st.caption(
            f"""
Showing **{len(jobs)}** verified opportunities from
multiple trusted job portals.
"""
        )

    with right:

        st.metric(
            "Jobs Found",
            len(jobs)
        )

    st.divider()

    # -----------------------------------------------------
    # Statistics Row
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🇮🇳 India",
        len(india_jobs)
    )

    c2.metric(
        "🏢 Fortune",
        len(fortune_jobs)
    )

    c3.metric(
        "🌍 Remote",
        len(remote_jobs)
    )

    c4.metric(
        "✈ Abroad",
        len(abroad_jobs)
    )

    st.write("")

    # -----------------------------------------------------
    # No Results
    # -----------------------------------------------------

    if total_jobs == 0:

        st.warning(
            """
No jobs found matching your search.

Try:

• Different keyword

• Remove filters

• Search another technology
"""
        )

        return
    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

    st.divider()

    PAGE_WINDOW = 5

    start_page = max(
        1,
        page - (PAGE_WINDOW // 2)
    )

    end_page = min(
        total_pages,
        start_page + PAGE_WINDOW - 1
    )

    if end_page - start_page < PAGE_WINDOW:

        start_page = max(
            1,
            end_page - PAGE_WINDOW + 1
        )

    col_prev, col_pages, col_next = st.columns([2, 6, 2])

    # -----------------------------------------------------
    # Previous Button
    # -----------------------------------------------------

    with col_prev:

        if st.button(
            "⬅ Previous",
            disabled=(page == 1),
            use_container_width=True,
        ):

            st.session_state.page -= 1
            st.rerun()

    # -----------------------------------------------------
    # Page Numbers
    # -----------------------------------------------------

    with col_pages:

        page_cols = st.columns(end_page - start_page + 1)

        index = 0

        for page_no in range(start_page, end_page + 1):

            with page_cols[index]:

                label = f"[{page_no}]" if page_no == page else str(page_no)

                if st.button(
                    label,
                    key=f"page_{page_no}",
                    use_container_width=True,
                ):

                    st.session_state.page = page_no
                    st.rerun()

            index += 1

    # -----------------------------------------------------
    # Next Button
    # -----------------------------------------------------

    with col_next:

        if st.button(
            "Next ➜",
            disabled=(page == total_pages),
            use_container_width=True,
        ):

            st.session_state.page += 1
            st.rerun()

    # -----------------------------------------------------
    # Results Summary
    # -----------------------------------------------------

    st.info(

        f"Showing **{start + 1}** to **{min(end, total_jobs)}** "
        f"of **{total_jobs}** live opportunities."

    )

    st.write("")

    # -----------------------------------------------------
    # Job Cards
    # -----------------------------------------------------

    for job in jobs_to_show:

        show_job_card(job)

        st.markdown("<br>", unsafe_allow_html=True)
    # -----------------------------------------------------
    # Bottom Pagination
    # -----------------------------------------------------

    st.divider()

    bottom_left, bottom_center, bottom_right = st.columns([2, 4, 2])

    with bottom_left:

        if st.button(
            "⬅ Previous Page",
            key="bottom_prev",
            disabled=(page == 1),
            use_container_width=True,
        ):

            st.session_state.page -= 1
            st.rerun()

    with bottom_center:

        st.markdown(
            f"""
<div style="text-align:center;
font-size:16px;
font-weight:600;
padding-top:8px;">

Page {page} of {total_pages}

</div>
""",
            unsafe_allow_html=True,
        )

    with bottom_right:

        if st.button(
            "Next Page ➜",
            key="bottom_next",
            disabled=(page == total_pages),
            use_container_width=True,
        ):

            st.session_state.page += 1
            st.rerun()

    # -----------------------------------------------------
    # Footer Statistics
    # -----------------------------------------------------

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Jobs",
        total_jobs
    )

    col2.metric(
        "Current Page",
        page
    )

    col3.metric(
        "Total Pages",
        total_pages
    )

    col4.metric(
        "Showing",
        len(jobs_to_show)
    )

    st.write("")

    # -----------------------------------------------------
    # Portal Information
    # -----------------------------------------------------

    st.markdown(
        """
<div style="
background:#F8FAFC;
padding:18px;
border-radius:12px;
border:1px solid #E5E7EB;
">

<h4 style="margin-bottom:10px;color:#0F4C81;">
About VisionBoard Career Portal
</h4>

<p style="color:#475569;line-height:1.8;">

✔ Latest jobs aggregated from multiple trusted job portals.

<br>

✔ Priority given to Indian opportunities, Fortune 500 companies,
remote roles and global careers.

<br>

✔ AI-powered ranking engine removes duplicates and promotes
high-quality opportunities.

</p>

</div>
""",
        unsafe_allow_html=True,
    )

    st.write("")

    # -----------------------------------------------------
    # Last Updated
    # -----------------------------------------------------

    st.caption(
        "🔄 Jobs are automatically synchronized every 6 hours."
    )

    st.caption(
        f"Showing {len(jobs_to_show)} jobs on this page."
    )

    st.write("")

    # -----------------------------------------------------
    # Back To Top
    # -----------------------------------------------------

    if st.button(
        "⬆ Back to Top",
        use_container_width=True,
    ):

        st.rerun() 