"""
=========================================================
VisionBoard Career Portal
Home Page
=========================================================
Professional Job Results Page

Responsibilities:
    - Load jobs from database
    - Primary search
    - Location filtering
    - Verified filtering
    - Job ranking
    - India-first ordering
    - Preferred-company prioritization
    - Remote / Abroad classification
    - Pagination
    - Job card display

NOTE:
    Footer is intentionally NOT included here.
    app.py should call show_footer() once.
=========================================================
"""

import math
import streamlit as st

from database.db_service import (
    search_jobs,
    get_jobs_paginated,
)

from services.ranking import rank_jobs
from components.job_card import show_job_card


# =========================================================
# CONFIGURATION
# =========================================================

PAGE_SIZE = 10

MAX_JOBS_TO_LOAD = 5000

PAGE_WINDOW = 5


# =========================================================
# PREFERRED COMPANIES
# =========================================================

PREFERRED_COMPANIES = [
    "IBM",
    "UST",
    "EY",
    "ERNST & YOUNG",
    "ALLIANZ",
    "CAPGEMINI",
    "CISCO",
    "KPMG",
    "DELOITTE",
    "PWC",
    "PRICEWATERHOUSECOOPERS",
    "WIPRO",
    "COGNIZANT",
    "ACCENTURE",
    "TECH MAHINDRA",
    "MICROSOFT",
    "GOOGLE",
    "AMAZON",
    "ORACLE",
    "INFOSYS",
    "TCS",
    "TATA CONSULTANCY SERVICES",
    "HCL",
    "HCLTECH",
]


# =========================================================
# INDIA KEYWORDS
# =========================================================

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
    "mysuru",
    "trivandrum",
    "thiruvananthapuram",
    "delhi",
    "new delhi",
    "jaipur",
    "indore",
    "chandigarh",
    "coimbatore",
    "vadodara",
    "surat",
    "bhubaneswar",
]


# =========================================================
# REMOTE KEYWORDS
# =========================================================

REMOTE_KEYWORDS = [
    "remote",
    "work from home",
    "wfh",
    "work-from-home",
    "anywhere",
    "worldwide",
    "distributed",
]


# =========================================================
# SAFE TEXT
# =========================================================

def safe_text(value):
    """
    Safely convert a database value to text.
    """

    if value is None:
        return ""

    return str(value).strip()


# =========================================================
# JOB CLASSIFICATION
# =========================================================

def is_india_job(job):
    """
    Identify India jobs using country and location.
    """

    country = safe_text(
        job.get("country", "")
    ).lower()

    location = safe_text(
        job.get("location", "")
    ).lower()

    combined = f"{country} {location}"

    return any(
        keyword in combined
        for keyword in INDIA_KEYWORDS
    )


def is_remote_job(job):
    """
    Identify remote jobs from location,
    country and description.
    """

    location = safe_text(
        job.get("location", "")
    ).lower()

    country = safe_text(
        job.get("country", "")
    ).lower()

    description = safe_text(
        job.get("description", "")
    ).lower()

    combined = (
        f"{location} "
        f"{country} "
        f"{description}"
    )

    return any(
        keyword in combined
        for keyword in REMOTE_KEYWORDS
    )


def is_preferred_company(job):
    """
    Identify jobs from the organization's
    preferred company list.
    """

    company = safe_text(
        job.get("company", "")
    ).upper()

    if not company:
        return False

    return any(
        company_name in company
        for company_name in PREFERRED_COMPANIES
    )


def is_verified_job(job):
    """
    Current verification rule.

    A job is considered verified when:
        - company exists
        - apply URL exists
        - source exists

    If a real verified column is added to the DB later,
    this function can be updated without changing the UI.
    """

    company = safe_text(
        job.get("company", "")
    )

    apply_url = safe_text(
        job.get("apply_url", "")
    )

    source = safe_text(
        job.get("source", "")
    )

    return bool(
        company
        and apply_url
        and source
    )


def is_abroad_job(job):
    """
    Identify jobs that are neither India nor remote.
    """

    return (
        not is_india_job(job)
        and not is_remote_job(job)
    )


# =========================================================
# POSTED DATE SORTING
# =========================================================

def posted_date_key(job):
    """
    Return posted date safely for sorting.
    """

    return safe_text(
        job.get("posted_date", "")
    )


# =========================================================
# LOAD JOBS
# =========================================================

def load_jobs(search_text):
    """
    Load jobs from the existing database layer.

    IMPORTANT:
    The existing database logic is preserved.
    """

    with st.spinner(
        "Loading latest opportunities..."
    ):

        try:

            if search_text.strip():

                jobs = search_jobs(
                    keyword=search_text.strip(),
                    limit=MAX_JOBS_TO_LOAD,
                    offset=0,
                )

            else:

                jobs = get_jobs_paginated(
                    page=1,
                    page_size=MAX_JOBS_TO_LOAD,
                )

        except Exception as error:

            st.error(
                "Unable to load jobs from the database."
            )

            st.caption(
                str(error)
            )

            return []

    if jobs is None:
        return []

    return list(jobs)


# =========================================================
# APPLY LOCATION FILTER
# =========================================================

def apply_location_filter(
    jobs,
    filter_value,
):
    """
    Apply the main radio-button filter.

    Supported values:
        All Jobs
        India
        Remote
        Abroad
        Verified Jobs
    """

    if filter_value == "India":

        return [
            job
            for job in jobs
            if is_india_job(job)
        ]

    if filter_value == "Remote":

        return [
            job
            for job in jobs
            if is_remote_job(job)
        ]

    if filter_value == "Abroad":

        return [
            job
            for job in jobs
            if is_abroad_job(job)
        ]

    if filter_value == "Verified Jobs":

        return [
            job
            for job in jobs
            if is_verified_job(job)
        ]

    return jobs


# =========================================================
# PRIORITIZE JOBS
# =========================================================

def prioritize_jobs(jobs):
    """
    VisionBoard ordering:

        1. India + Preferred Company
        2. India
        3. Remote + Preferred Company
        4. Remote
        5. Abroad + Preferred Company
        6. Abroad

    Latest jobs are shown first inside each group.
    """

    india_preferred = []
    india_other = []

    remote_preferred = []
    remote_other = []

    abroad_preferred = []
    abroad_other = []

    for job in jobs:

        india = is_india_job(job)

        remote = is_remote_job(job)

        preferred = is_preferred_company(job)

        if india:

            if preferred:
                india_preferred.append(job)

            else:
                india_other.append(job)

        elif remote:

            if preferred:
                remote_preferred.append(job)

            else:
                remote_other.append(job)

        else:

            if preferred:
                abroad_preferred.append(job)

            else:
                abroad_other.append(job)

    groups = [
        india_preferred,
        india_other,
        remote_preferred,
        remote_other,
        abroad_preferred,
        abroad_other,
    ]

    for group in groups:

        group.sort(
            key=posted_date_key,
            reverse=True,
        )

    return (
        india_preferred
        + india_other
        + remote_preferred
        + remote_other
        + abroad_preferred
        + abroad_other
    )


# =========================================================
# TOP PAGINATION
# =========================================================

def show_top_pagination(
    page,
    total_pages,
):
    """
    Compact pagination displayed beside
    Latest Career Opportunities.
    """

    if total_pages <= 1:
        return

    start_page = max(
        1,
        page - 2,
    )

    end_page = min(
        total_pages,
        start_page + PAGE_WINDOW - 1,
    )

    if (
        end_page - start_page
        < PAGE_WINDOW - 1
    ):

        start_page = max(
            1,
            end_page - PAGE_WINDOW + 1,
        )

    page_count = (
        end_page - start_page + 1
    )

    columns = st.columns(
        page_count + 2
    )

    # -----------------------------------------------------
    # Previous
    # -----------------------------------------------------

    with columns[0]:

        if st.button(
            "‹",
            disabled=(
                page == 1
            ),
            key="top_previous",
            use_container_width=True,
        ):

            st.session_state.page = (
                page - 1
            )

            st.rerun()

    # -----------------------------------------------------
    # Page Numbers
    # -----------------------------------------------------

    for index, page_number in enumerate(
        range(
            start_page,
            end_page + 1,
        ),
        start=1,
    ):

        with columns[index]:

            if st.button(
                str(page_number),
                key=f"top_page_{page_number}",
                type=(
                    "primary"
                    if page_number == page
                    else "secondary"
                ),
                use_container_width=True,
            ):

                st.session_state.page = (
                    page_number
                )

                st.rerun()

    # -----------------------------------------------------
    # Next
    # -----------------------------------------------------

    with columns[-1]:

        if st.button(
            "›",
            disabled=(
                page == total_pages
            ),
            key="top_next",
            use_container_width=True,
        ):

            st.session_state.page = (
                page + 1
            )

            st.rerun()


# =========================================================
# BOTTOM PAGINATION
# =========================================================

def show_bottom_pagination(
    page,
    total_pages,
):
    """
    Simple pagination at the bottom.
    """

    if total_pages <= 1:
        return

    st.divider()

    left, center, right = st.columns(
        [2, 4, 2]
    )

    with left:

        if st.button(
            "← Previous",
            disabled=(
                page == 1
            ),
            key="bottom_previous",
            use_container_width=True,
        ):

            st.session_state.page = (
                page - 1
            )

            st.rerun()

    with center:

        st.markdown(
            f"""
            <div style="
                text-align:center;
                padding-top:8px;
                color:#64748B;
                font-size:13px;
            ">
                Page <strong>{page}</strong>
                of
                <strong>{total_pages}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        if st.button(
            "Next →",
            disabled=(
                page == total_pages
            ),
            key="bottom_next",
            use_container_width=True,
        ):

            st.session_state.page = (
                page + 1
            )

            st.rerun()


# =========================================================
# SHOW HOME
# =========================================================

def show_home(
    search,
    filter_value,
    india_only,
    remote_only,
    abroad_only,
    verified_only,
):
    """
    Main VisionBoard job-results page.

    The six parameters correspond to filters.py.
    """

    # =====================================================
    # SESSION STATE
    # =====================================================

    if "page" not in st.session_state:

        st.session_state.page = 1

    # =====================================================
    # NORMALIZE VALUES
    # =====================================================

    search = safe_text(search)

    filter_value = safe_text(
        filter_value
    )

    # =====================================================
    # HANDLE QUICK FILTERS
    # =====================================================

    # The radio-button location filter remains the
    # primary location filter.

    # These quick-filter flags are also respected
    # independently when selected.

    effective_filter = filter_value

    if india_only:

        effective_filter = "India"

    elif remote_only:

        effective_filter = "Remote"

    elif abroad_only:

        effective_filter = "Abroad"

    elif verified_only:

        effective_filter = "Verified Jobs"

    # =====================================================
    # FILTER STATE
    # =====================================================

    current_filter = (
        search,
        effective_filter,
        india_only,
        remote_only,
        abroad_only,
        verified_only,
    )

    if (
        "last_home_filter"
        not in st.session_state
    ):

        st.session_state.last_home_filter = (
            current_filter
        )

    elif (
        st.session_state.last_home_filter
        != current_filter
    ):

        st.session_state.page = 1

        st.session_state.last_home_filter = (
            current_filter
        )

    # =====================================================
    # LOAD JOBS
    # =====================================================

    jobs = load_jobs(
        search
    )

    # =====================================================
    # RANK JOBS
    # =====================================================

    if jobs:

        try:

            jobs = rank_jobs(
                jobs
            )

        except Exception:

            # Ranking should never stop
            # the job portal.
            pass

    # =====================================================
    # LOCATION FILTER
    # =====================================================

    jobs = apply_location_filter(
        jobs,
        effective_filter,
    )

    # =====================================================
    # PRIORITIZE
    # =====================================================

    jobs = prioritize_jobs(
        jobs
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    india_jobs = [
        job
        for job in jobs
        if is_india_job(job)
    ]

    remote_jobs = [
        job
        for job in jobs
        if is_remote_job(job)
    ]

    abroad_jobs = [
        job
        for job in jobs
        if is_abroad_job(job)
    ]

    preferred_jobs = [
        job
        for job in jobs
        if is_preferred_company(job)
    ]

    verified_jobs = [
        job
        for job in jobs
        if is_verified_job(job)
    ]

    total_jobs = len(
        jobs
    )

    # =====================================================
    # PAGINATION CALCULATION
    # =====================================================

    total_pages = max(
        1,
        math.ceil(
            total_jobs
            / PAGE_SIZE
        ),
    )

    page = st.session_state.page

    if page > total_pages:

        page = total_pages

        st.session_state.page = page

    start = (
        page - 1
    ) * PAGE_SIZE

    end = (
        start
        + PAGE_SIZE
    )

    jobs_to_show = jobs[
        start:end
    ]

    # =====================================================
    # TOP INFORMATION
    # =====================================================

    info1, info2, info3, info4 = st.columns(
        4
    )

    with info1:

        st.caption(
            f"🇮🇳 India  **{len(india_jobs)}**"
        )

    with info2:

        st.caption(
            f"⭐ Preferred  **{len(preferred_jobs)}**"
        )

    with info3:

        st.caption(
            f"🌍 Remote  **{len(remote_jobs)}**"
        )

    with info4:

        st.caption(
            f"✈ Abroad  **{len(abroad_jobs)}**"
        )

    # =====================================================
    # RESULT STATUS
    # =====================================================

    if search:

        status_text = (
            f'Showing results for "{search}"'
        )

    elif effective_filter == "India":

        status_text = (
            "Showing India opportunities."
        )

    elif effective_filter == "Remote":

        status_text = (
            "Showing remote opportunities."
        )

    elif effective_filter == "Abroad":

        status_text = (
            "Showing global opportunities."
        )

    elif effective_filter == "Verified Jobs":

        status_text = (
            "Showing verified opportunities."
        )

    else:

        status_text = (
            "Showing the latest opportunities."
        )

    st.markdown(
        f"""
        <div style="
            display:inline-block;
            margin:4px 0 14px 0;
            padding:6px 14px;
            border-radius:20px;
            background:#F1F7FC;
            border:1px solid #D7E8F5;
            color:#0F4C81;
            font-size:12px;
            font-weight:600;
        ">
            ● &nbsp; {status_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # RESULTS HEADER + PAGINATION
    # =====================================================

    st.write("")

    header_col, pagination_col = st.columns(
        [5, 5],
        vertical_alignment="center",
    )

    with header_col:

        st.markdown(
            """
            <div style="
                color:#0F4C81;
                font-size:24px;
                font-weight:800;
                margin-bottom:2px;
            ">
                💼 Latest Career Opportunities
            </div>

            <div style="
                color:#64748B;
                font-size:13px;
                margin-bottom:8px;
            ">
                Latest opportunities from leading companies
                across India and worldwide.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with pagination_col:

        show_top_pagination(
            page,
            total_pages,
        )

    # =====================================================
    # NO RESULTS
    # =====================================================

    if total_jobs == 0:

        st.info(
            """
            No jobs found matching your search.

            Try a different keyword or select
            "All Jobs".
            """
        )

        return

    # =====================================================
    # RESULT RANGE
    # =====================================================

    st.caption(
        f"Showing {start + 1}–"
        f"{min(end, total_jobs)} "
        f"of {total_jobs} opportunities."
    )

    st.write("")

    # =====================================================
    # JOB CARDS
    # =====================================================

    for job in jobs_to_show:

        show_job_card(
            job
        )

        st.markdown(
            "<div style='height:8px'></div>",
            unsafe_allow_html=True,
        )

    # =====================================================
    # BOTTOM PAGINATION
    # =====================================================

    show_bottom_pagination(
        page,
        total_pages,
    )

    # =====================================================
    # ABOUT VISIONBOARD
    # =====================================================

    st.write("")

    with st.container(
        border=True
    ):

        st.markdown(
            "### About VisionBoard Career Portal"
        )

        st.caption(
            "Latest jobs aggregated from multiple "
            "trusted job portals."
        )

        st.caption(
            "Priority is given to Indian opportunities, "
            "remote roles, preferred companies and "
            "global careers."
        )

        st.caption(
            "Jobs are automatically synchronized and "
            "ranked to help candidates find relevant "
            "opportunities faster."
        )

    # =====================================================
    # SYNC INFORMATION
    # =====================================================

    st.caption(
        "🔄 Jobs are automatically synchronized "
        "every 6 hours."
    )