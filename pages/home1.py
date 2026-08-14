"""
VisionBoard Career Portal
pages/home.py

Responsibilities:
- Load jobs from database
- Apply VisionBoard relevance rules
- Primary search
- Location filtering
- Verified filtering
- Expired-job filtering
- DevOps/Airflow exclusion
- Job ranking
- India-first ordering
- Preferred-company prioritization
- Remote / Abroad classification
- Pagination
- Job card display

IMPORTANT:
- This file does NOT control job synchronization.
- This file does NOT modify the database.
- Sync continues to be handled by sync_service.py / GitHub Actions.
"""

import math
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from database.db_service import (
    search_jobs,
    get_jobs_paginated,
)

from services.ranking import rank_jobs
from components.job_card import show_job_card

from config.company_priority import FORTUNE_PRIORITY


# =========================================================
# CONFIGURATION
# =========================================================

PAGE_SIZE = 10
MAX_JOBS_TO_LOAD = 5000
PAGE_WINDOW = 5

# Jobs older than this are hidden from the portal.
JOB_ACTIVE_DAYS = 30


# =========================================================
# VISIONBOARD RELEVANCE KEYWORDS
# =========================================================
#
# These keywords define the type of jobs VisionBoard
# should display.
#
# IMPORTANT:
# Airflow is intentionally NOT included here as a primary
# technology because dedicated Airflow roles are excluded.
#
# Airflow mentioned inside a Data Engineering job is still
# allowed.
# =========================================================

RELEVANT_JOB_KEYWORDS = [

    # -----------------------------------------------------
    # Data Engineering
    # -----------------------------------------------------

    "data engineer",
    "senior data engineer",
    "lead data engineer",
    "big data engineer",
    "data engineering",
    "data architect",
    "data platform engineer",
    "data pipeline",
    "etl",
    "etl developer",
    "data warehouse",
    "data warehouse engineer",
    "data integration",

    # -----------------------------------------------------
    # Azure
    # -----------------------------------------------------

    "azure",
    "azure data engineer",
    "azure data factory",
    "adf",
    "azure synapse",
    "synapse",
    "azure databricks",
    "microsoft fabric",
    "fabric data",
    "data lake",
    "adls",
    "adls gen2",

    # -----------------------------------------------------
    # AWS
    # -----------------------------------------------------

    "aws",
    "aws data engineer",
    "aws glue",
    "redshift",
    "athena",
    "s3",
    "emr",

    # -----------------------------------------------------
    # GCP
    # -----------------------------------------------------

    "gcp",
    "google cloud",
    "bigquery",
    "dataflow",

    # -----------------------------------------------------
    # Spark / PySpark
    # -----------------------------------------------------

    "pyspark",
    "spark",
    "apache spark",

    # -----------------------------------------------------
    # Databricks
    # -----------------------------------------------------

    "databricks",
    "delta lake",
    "unity catalog",

    # -----------------------------------------------------
    # Snowflake
    # -----------------------------------------------------

    "snowflake",

    # -----------------------------------------------------
    # SQL
    # -----------------------------------------------------

    "sql",
    "sql developer",
    "sql server",
    "postgresql",
    "mysql",

    # -----------------------------------------------------
    # Python
    # -----------------------------------------------------

    "python",
    "python developer",
    "backend python",
    "fastapi",
    "django",
    "flask",

    # -----------------------------------------------------
    # Kafka / Streaming
    # -----------------------------------------------------

    "kafka",
    "apache kafka",
    "event hub",
    "eventhub",
    "streaming",

    # -----------------------------------------------------
    # Analytics / BI
    # -----------------------------------------------------

    "data analyst",
    "business intelligence",
    "bi developer",
    "power bi",

    # -----------------------------------------------------
    # AI / ML / GenAI
    # -----------------------------------------------------

    "ai engineer",
    "machine learning engineer",
    "machine learning",
    "artificial intelligence",
    "generative ai",
    "genai",
    "llm",
    "rag",
    "langchain",
    "openai",
    "prompt engineer",
    "prompt engineering",
    "vector database",

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
# EXCLUDED JOB TITLE KEYWORDS
# =========================================================
#
# IMPORTANT:
#
# "Data Engineer requiring Airflow"
#       -> ALLOWED
#
# "Data Engineer requiring DevOps knowledge"
#       -> ALLOWED
#
# "Airflow Engineer"
#       -> EXCLUDED
#
# "DevOps Engineer"
#       -> EXCLUDED
#
# =========================================================

EXCLUDED_JOB_TITLE_KEYWORDS = [

    "devops engineer",
    "devops developer",
    "devops architect",
    "devops specialist",
    "devops lead",
    "devops manager",
    "devops consultant",

    "airflow engineer",
    "airflow developer",
    "airflow specialist",
    "airflow architect",
    "airflow consultant",

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
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):
    """
    Normalize text for reliable keyword matching.
    """

    text = safe_text(value).lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# =========================================================
# JOB SEARCHABLE TEXT
# =========================================================

def get_job_search_text(job):
    """
    Build searchable text from the important job fields.
    """

    return " ".join(
        [
            normalize_text(job.get("title")),
            normalize_text(job.get("company")),
            normalize_text(job.get("skills")),
            normalize_text(job.get("location")),
            normalize_text(job.get("country")),
            normalize_text(job.get("description")),
            normalize_text(job.get("employment_type")),
        ]
    )


# =========================================================
# DATE PARSING
# =========================================================

def parse_posted_datetime(value):
    """
    Convert common posted-date formats into datetime.

    Returns:
        datetime | None
    """

    raw = safe_text(value)

    if not raw:
        return None

    raw_lower = raw.lower()

    now = datetime.now()

    # -----------------------------------------------------
    # Relative dates
    # -----------------------------------------------------

    if "today" in raw_lower:
        return now

    if "yesterday" in raw_lower:

        return now - timedelta(days=1)

    match = re.search(
        r"(\d+)\s*day",
        raw_lower,
    )

    if match:

        days_ago = int(
            match.group(1)
        )

        return (
            now
            - timedelta(days=days_ago)
        )

    # -----------------------------------------------------
    # ISO date
    # -----------------------------------------------------

    normalized = raw.replace(
        "Z",
        "+00:00",
    )

    try:

        return datetime.fromisoformat(
            normalized
        )

    except ValueError:
        pass

    # -----------------------------------------------------
    # Common formats
    # -----------------------------------------------------

    formats = [

        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",

    ]

    for fmt in formats:

        try:

            return datetime.strptime(
                raw,
                fmt,
            )

        except ValueError:

            continue

    return None


# =========================================================
# CONVERT DATETIME TO IST-NAIVE
# =========================================================

def normalize_datetime(value):
    """
    Convert timezone-aware datetime to IST and remove
    timezone information so comparisons are safe.
    """

    if value is None:
        return None

    if value.tzinfo is not None:

        value = (
            value
            .astimezone(
                ZoneInfo("Asia/Kolkata")
            )
            .replace(
                tzinfo=None
            )
        )

    return value


# =========================================================
# JOB EXPIRY
# =========================================================

def is_expired_job(job):
    """
    Hide jobs older than JOB_ACTIVE_DAYS.

    Jobs with missing or unrecognized dates are retained
    rather than incorrectly removed.
    """

    posted_date = safe_text(
        job.get("posted_date")
    )

    if not posted_date:
        return False

    posted_dt = parse_posted_datetime(
        posted_date
    )

    if posted_dt is None:
        return False

    posted_dt = normalize_datetime(
        posted_dt
    )

    now = datetime.now()

    age_days = (
        now - posted_dt
    ).total_seconds() / 86400

    return age_days > JOB_ACTIVE_DAYS


# =========================================================
# EXCLUDED JOB CHECK
# =========================================================

def is_excluded_job(job):
    """
    Exclude dedicated DevOps/Airflow job roles.

    Only the job title is checked.
    """

    title = normalize_text(
        job.get("title")
    )

    if not title:
        return False

    return any(
        keyword in title
        for keyword in EXCLUDED_JOB_TITLE_KEYWORDS
    )


# =========================================================
# VISIONBOARD RELEVANCE CHECK
# =========================================================

def is_relevant_job(job):
    """
    Determines whether a job belongs to the technology
    areas supported by VisionBoard.

    This is the IMPORTANT protection against the portal
    displaying every unrelated job in the database.

    A job must contain at least one VisionBoard technology
    keyword in its title, company, skills, description,
    location or country.

    Dedicated DevOps/Airflow roles are rejected separately.
    """

    if is_excluded_job(job):
        return False

    searchable_text = get_job_search_text(
        job
    )

    if not searchable_text:
        return False

    for keyword in RELEVANT_JOB_KEYWORDS:

        if keyword in searchable_text:
            return True

    return False


# =========================================================
# VALID JOB CHECK
# =========================================================

def is_valid_job(job):
    """
    Final VisionBoard validation.

    Rules:

    1. Expired jobs -> hidden
    2. Dedicated DevOps/Airflow -> hidden
    3. Irrelevant jobs -> hidden
    """

    if is_expired_job(job):
        return False

    if is_excluded_job(job):
        return False

    if not is_relevant_job(job):
        return False

    return True


# =========================================================
# FILTER VALID JOBS
# =========================================================

def filter_valid_jobs(jobs):
    """
    Remove invalid/unrelated jobs before ranking,
    location classification and pagination.
    """

    valid_jobs = []

    for job in jobs:

        if is_valid_job(job):

            valid_jobs.append(job)

    return valid_jobs


# =========================================================
# INDIA JOB
# =========================================================

def is_india_job(job):
    """
    Identify India jobs using country and location.
    """

    country = normalize_text(
        job.get("country")
    )

    location = normalize_text(
        job.get("location")
    )

    combined = (
        f"{country} {location}"
    )

    return any(
        keyword in combined
        for keyword in INDIA_KEYWORDS
    )


# =========================================================
# REMOTE JOB
# =========================================================

def is_remote_job(job):
    """
    Identify remote jobs using location, country and
    description.

    India + Remote is classified as India first when
    prioritizing jobs.
    """

    location = normalize_text(
        job.get("location")
    )

    country = normalize_text(
        job.get("country")
    )

    description = normalize_text(
        job.get("description")
    )

    combined = (
        f"{location} "
        f"{country} "
        f"{description}"
    )

    return any(
        keyword in combined
        for keyword in REMOTE_KEYWORDS
    )


# =========================================================
# PREFERRED COMPANY PRIORITY
# =========================================================

def get_company_priority(job):
    """
    Return the priority configured in:

        config/company_prioroty.py

    Higher number = higher priority.
    """

    company = safe_text(
        job.get("company")
    ).upper()

    if not company:
        return 0

    best_priority = 0

    for company_name, priority in FORTUNE_PRIORITY.items():

        company_name = safe_text(
            company_name
        ).upper()

        if not company_name:
            continue

        # Exact company match
        if company == company_name:

            best_priority = max(
                best_priority,
                int(priority),
            )

        # Safe substring match for names such as
        # "Tata Consultancy Services - TCS"
        elif company_name in company:

            best_priority = max(
                best_priority,
                int(priority),
            )

    return best_priority


# =========================================================
# PREFERRED COMPANY CHECK
# =========================================================

def is_preferred_company(job):
    """
    Determine whether the job belongs to one of the
    preferred companies.
    """

    return (
        get_company_priority(job) > 0
    )


# =========================================================
# VERIFIED JOB
# =========================================================

def is_verified_job(job):
    """
    Current verification rule.

    A job is considered verified when:

    - company exists
    - apply URL exists
    - source exists

    If a real verified column is added to the database
    later, this function can be updated.
    """

    company = safe_text(
        job.get("company")
    )

    apply_url = safe_text(
        job.get("apply_url")
    )

    source = safe_text(
        job.get("source")
    )

    return bool(
        company
        and apply_url
        and source
    )


# =========================================================
# ABROAD JOB
# =========================================================

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
    Return sortable posted date.
    """

    parsed = parse_posted_datetime(
        job.get("posted_date")
    )

    if parsed is None:
        return datetime.min

    parsed = normalize_datetime(
        parsed
    )

    return parsed


# =========================================================
# LOAD JOBS
# =========================================================

def load_jobs(search_text):
    """
    Load current jobs from the existing database.

    IMPORTANT:
    This function does NOT run synchronization.

    It only reads the database and applies the
    VisionBoard display rules.
    """

    search_text = safe_text(
        search_text
    )

    # -----------------------------------------------------
    # EXPLICIT EXCLUDED SEARCH
    # -----------------------------------------------------
    #
    # If someone searches only for DevOps or Airflow,
    # VisionBoard should return no results.
    #
    # -----------------------------------------------------

    search_lower = (
        search_text.lower().strip()
    )

    if (
        search_lower == "devops"
        or search_lower == "airflow"
        or search_lower == "devops engineer"
        or search_lower == "airflow engineer"
    ):

        return []

    # -----------------------------------------------------
    # DATABASE LOAD
    # -----------------------------------------------------

    with st.spinner(
        "Loading latest opportunities..."
    ):

        try:

            if search_text:

                jobs = search_jobs(
                    keyword=search_text,
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
                f"Database error: {error}"
            )

            return []

    # -----------------------------------------------------
    # SAFETY
    # -----------------------------------------------------

    if jobs is None:
        return []

    try:

        jobs = list(jobs)

    except TypeError:

        return []

    # -----------------------------------------------------
    # VISIONBOARD VALIDATION
    # -----------------------------------------------------

    jobs = filter_valid_jobs(
        jobs
    )

    return jobs


# =========================================================
# APPLY LOCATION FILTER
# =========================================================

def apply_location_filter(
    jobs,
    filter_value,
):
    """
    Apply the main radio-button filter.

    Supported:

        All Jobs
        India
        Remote
        Abroad
        Verified Jobs
    """

    filter_value = safe_text(
        filter_value
    )

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

    Within each group:

    - Preferred-company priority
    - Latest posted jobs
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

    # -----------------------------------------------------
    # Preferred company groups
    # -----------------------------------------------------

    preferred_groups = [
        india_preferred,
        remote_preferred,
        abroad_preferred,
    ]

    for group in preferred_groups:

        group.sort(
            key=lambda job: (
                get_company_priority(job),
                posted_date_key(job),
            ),
            reverse=True,
        )

    # -----------------------------------------------------
    # Normal groups
    # -----------------------------------------------------

    normal_groups = [
        india_other,
        remote_other,
        abroad_other,
    ]

    for group in normal_groups:

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
            disabled=page == 1,
            key="top_previous",
            use_container_width=True,
        ):

            st.session_state.page = (
                page - 1
            )

            st.rerun()

    # -----------------------------------------------------
    # Page numbers
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
            disabled=page == total_pages,
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

    # -----------------------------------------------------
    # Previous
    # -----------------------------------------------------

    with left:

        if st.button(
            "← Previous",
            disabled=page == 1,
            key="bottom_previous",
            use_container_width=True,
        ):

            st.session_state.page = (
                page - 1
            )

            st.rerun()

    # -----------------------------------------------------
    # Page indicator
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Next
    # -----------------------------------------------------

    with right:

        if st.button(
            "Next →",
            disabled=page == total_pages,
            key="bottom_next",
            use_container_width=True,
        ):

            st.session_state.page = (
                page + 1
            )

            st.rerun()


# =========================================================
# BACK TO TOP
# =========================================================

def show_back_to_top():
    """
    Display Back to Top on the right side.
    """

    st.markdown(
        """
        <div style="
            width:100%;
            text-align:right;
            margin-top:10px;
            margin-bottom:14px;
        ">
            <a
                href="#visionboard-top"
                style="
                    text-decoration:none;
                    font-size:13px;
                    font-weight:600;
                    color:#0F4C81;
                "
            >
                ↑ Back to Top
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    """

    # =====================================================
    # TOP ANCHOR
    # =====================================================

    st.header(
        "VisionBoard Career Portal",
        anchor="visionboard-top",
    )

    # =====================================================
    # SESSION STATE
    # =====================================================

    if "page" not in st.session_state:

        st.session_state.page = 1

    # =====================================================
    # NORMALIZE
    # =====================================================

    search = safe_text(
        search
    )

    filter_value = safe_text(
        filter_value
    )

    # =====================================================
    # EFFECTIVE FILTER
    # =====================================================

    effective_filter = (
        filter_value
        or "All Jobs"
    )

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
        bool(india_only),
        bool(remote_only),
        bool(abroad_only),
        bool(verified_only),
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

            # Ranking must never break
            # the portal.
            pass

    # =====================================================
    # LOCATION FILTER
    # =====================================================

    jobs = apply_location_filter(
        jobs,
        effective_filter,
    )

    # =====================================================
    # PRIORITIZATION
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
    # PAGINATION
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

        st.session_state.page = (
            page
        )

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
    # STATISTICS ROW
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
            f'Showing relevant results for "{search}"'
        )

    elif effective_filter == "India":

        status_text = (
            "Showing relevant India opportunities."
        )

    elif effective_filter == "Remote":

        status_text = (
            "Showing relevant remote opportunities."
        )

    elif effective_filter == "Abroad":

        status_text = (
            "Showing relevant global opportunities."
        )

    elif effective_filter == "Verified Jobs":

        status_text = (
            "Showing verified VisionBoard opportunities."
        )

    else:

        status_text = (
            "Showing the latest relevant "
            "VisionBoard opportunities."
        )

    st.info(
        status_text
    )

    # =====================================================
    # RESULTS HEADER
    # =====================================================

    header_col, pagination_col = st.columns(
        [5, 5],
        vertical_alignment="center",
    )

    with header_col:

        st.markdown(
            """
            ### 💼 Latest Career Opportunities

            Latest relevant opportunities from
            leading companies across India
            and worldwide.
            """
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

        if search:

            st.warning(
                f'No relevant jobs found matching "{search}".'
            )

        elif effective_filter == "India":

            st.info(
                "No relevant India opportunities "
                "are currently available."
            )

        elif effective_filter == "Remote":

            st.info(
                "No relevant remote opportunities "
                "are currently available."
            )

        elif effective_filter == "Abroad":

            st.info(
                "No relevant international opportunities "
                "are currently available."
            )

        else:

            st.info(
                "No relevant jobs are currently "
                "available for the selected filter."
            )

        st.caption(
            "Try another technology, company, "
            "location or job title."
        )

        show_back_to_top()

        return

    # =====================================================
    # RESULT RANGE
    # =====================================================

    st.caption(
        f"Showing {start + 1}–"
        f"{min(end, total_jobs)} "
        f"of {total_jobs} relevant opportunities."
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
    # BACK TO TOP
    # =====================================================

    show_back_to_top()

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
            "Latest relevant jobs aggregated from "
            "multiple trusted job portals."
        )

        st.caption(
            "Priority is given to Indian opportunities, "
            "remote roles, preferred companies and "
            "relevant global careers."
        )

        st.caption(
            "Jobs are filtered and ranked to help "
            "candidates find relevant opportunities faster."
        )