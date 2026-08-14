"""
=========================================================
VisionBoard Career Portal
Home / Job Results Page
=========================================================

Responsibilities:
    - Load jobs from database
    - Primary search
    - India / Remote / Abroad filtering
    - Verified jobs
    - Data Engineering / Cloud relevance filtering
    - Exclude DevOps / Airflow-specific roles
    - Exclude expired jobs
    - Preferred-company prioritization
    - India-first ordering
    - Pagination
    - Job card display

IMPORTANT:
    This page only READS the jobs database.

    It does NOT run the 6-hour scheduler.

    Job synchronization is handled by the
    aggregator / scheduler layer.
=========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import math
import re
from datetime import datetime

import streamlit as st

from database.db_service import (
    search_jobs,
    get_jobs_paginated,
)

from services.ranking import rank_jobs
from components.job_card import show_job_card


# =========================================================
# COMPANY PRIORITY
# =========================================================

# Correct module spelling:
# company_priority
#
# We keep a safe fallback so the portal does not crash
# if the configuration file is temporarily unavailable.

try:
    from config.company_priority import FORTUNE_PRIORITY
except Exception:

    FORTUNE_PRIORITY = {
        "IBM": 100,
        "MICROSOFT": 100,
        "GOOGLE": 100,
        "AMAZON": 100,
        "ORACLE": 95,
        "ACCENTURE": 95,
        "COGNIZANT": 95,
        "CAPGEMINI": 95,
        "EY": 95,
        "KPMG": 95,
        "DELOITTE": 95,
        "UST": 95,
        "ALLIANZ": 90,
        "CISCO": 90,
        "WIPRO": 90,
        "TECH MAHINDRA": 90,
        "INFOSYS": 90,
        "TCS": 90,
        "HCL": 90,
        "IBS": 85,
    }


# =========================================================
# CONFIGURATION
# =========================================================

PAGE_SIZE = 10

MAX_JOBS_TO_LOAD = 5000

MAX_PAGES = 500

JOB_ACTIVE_DAYS = 30


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
    "lucknow",
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
    "work-from-home",
    "wfh",
    "anywhere",
    "worldwide",
    "distributed",
]


# =========================================================
# EXCLUDED JOB TITLE KEYWORDS
# =========================================================
#
# IMPORTANT:
# We check ONLY the title.
#
# Therefore:
#
# Data Engineer + Airflow in description
#       -> ALLOWED
#
# Data Engineer + DevOps in description
#       -> ALLOWED
#
# DevOps Engineer
#       -> BLOCKED
#
# Airflow Engineer
#       -> BLOCKED
# =========================================================

EXCLUDED_JOB_TITLE_KEYWORDS = [
    "devops engineer",
    "devops developer",
    "devops architect",
    "devops specialist",
    "devops lead",
    "devops manager",
    "devops consultant",
    "devops administrator",
    "devops admin",
    "airflow engineer",
    "airflow developer",
    "airflow specialist",
    "airflow administrator",
]


# =========================================================
# DATA ENGINEERING / CLOUD KEYWORDS
# =========================================================
#
# Used especially for the Abroad filter.
#
# Abroad should NOT become:
# "show every non-India job".
#
# It should focus on VisionBoard's target technology
# areas.
# =========================================================

DATA_ENGINEERING_KEYWORDS = [

    # Core Data Engineering
    "data engineer",
    "senior data engineer",
    "lead data engineer",
    "staff data engineer",
    "principal data engineer",
    "big data engineer",
    "data engineering",
    "data pipeline",
    "data pipelines",
    "etl",
    "etl developer",
    "data warehouse",
    "data platform",
    "data architect",
    "data integration",

    # Azure
    "azure data engineer",
    "azure data factory",
    "azure synapse",
    "adf",
    "synapse",
    "azure databricks",
    "microsoft fabric",
    "fabric data",

    # Databricks
    "databricks",
    "delta lake",
    "unity catalog",

    # Spark
    "pyspark",
    "apache spark",
    "spark",

    # AWS
    "aws data engineer",
    "aws glue",
    "aws redshift",
    "aws emr",
    "amazon emr",
    "kinesis",
    "athena",

    # Snowflake
    "snowflake",

    # SQL / Warehouse
    "sql developer",
    "sql",
    "data warehouse",
    "data lake",
    "data lakehouse",

    # Streaming
    "kafka",
    "apache kafka",

    # Cloud
    "cloud data engineer",
    "cloud engineer",
    "cloud data",

    # Engineering
    "analytics engineer",
    "big data",
]


# =========================================================
# SAFE TEXT
# =========================================================

def safe_text(value):
    """
    Safely convert any database value to lowercase text.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):
    """
    Normalize text for reliable comparisons.

    Example:

        Full-Time
        full time
        full_time

    all become comparable.
    """

    return (
        safe_text(value)
        .replace("-", " ")
        .replace("_", " ")
        .replace("/", " ")
    )


# =========================================================
# JOB SEARCH TEXT
# =========================================================

def job_search_text(job):
    """
    Build a single searchable text string.
    """

    fields = [
        job.get("title"),
        job.get("company"),
        job.get("location"),
        job.get("country"),
        job.get("employment_type"),
        job.get("experience"),
        job.get("work_mode"),
        job.get("skills"),
        job.get("description"),
        job.get("source"),
    ]

    return " ".join(
        safe_text(value)
        for value in fields
        if value is not None
    )


# =========================================================
# LOCAL KEYWORD SEARCH
# =========================================================

def local_keyword_search(jobs, keyword):
    """
    Reliable fallback search.

    Every meaningful word entered by the user must
    exist somewhere in the job record.

    Example:

        Azure Data Engineer

    must match jobs containing:
        Azure
        AND
        Data
        AND
        Engineer
    """

    keyword = safe_text(keyword)

    if not keyword:
        return jobs

    terms = [
        term
        for term in re.split(r"\s+", keyword)
        if term
    ]

    results = []

    for job in jobs:

        text = job_search_text(job)

        if all(term in text for term in terms):
            results.append(job)

    return results


# =========================================================
# INDIA JOB
# =========================================================

def is_india_job(job):
    """
    Identify India jobs from country or location.
    """

    country = safe_text(
        job.get("country")
    )

    location = safe_text(
        job.get("location")
    )

    combined = f"{country} {location}"

    return any(
        keyword in combined
        for keyword in INDIA_KEYWORDS
    )


# =========================================================
# REMOTE JOB
# =========================================================

def is_remote_job(job):
    """
    Identify remote jobs.

    Checks:
        country
        location
        description
        work_mode
    """

    country = safe_text(
        job.get("country")
    )

    location = safe_text(
        job.get("location")
    )

    description = safe_text(
        job.get("description")
    )

    work_mode = safe_text(
        job.get("work_mode")
    )

    combined = (
        f"{country} "
        f"{location} "
        f"{description} "
        f"{work_mode}"
    )

    return any(
        keyword in combined
        for keyword in REMOTE_KEYWORDS
    )


# =========================================================
# ABROAD JOB
# =========================================================

def is_abroad_job(job):
    """
    Abroad means:

        NOT India
        AND
        NOT Remote

    The technology relevance filter is applied
    separately.
    """

    return (
        not is_india_job(job)
        and not is_remote_job(job)
    )


# =========================================================
# DATA ENGINEERING JOB
# =========================================================

def is_data_engineering_job(job):
    """
    Determine whether a job belongs to the
    VisionBoard Data Engineering / Cloud technology
    target area.

    Searches title, skills and description.
    """

    title = safe_text(
        job.get("title")
    )

    skills = safe_text(
        job.get("skills")
    )

    description = safe_text(
        job.get("description")
    )

    combined = (
        f"{title} "
        f"{skills} "
        f"{description}"
    )

    return any(
        keyword in combined
        for keyword in DATA_ENGINEERING_KEYWORDS
    )


# =========================================================
# PREFERRED COMPANY
# =========================================================

def get_company_priority(job):
    """
    Return company priority.

    Higher number = higher priority.
    """

    company = safe_text(
        job.get("company")
    ).upper()

    if not company:
        return 0

    best_priority = 0

    for company_name, priority in FORTUNE_PRIORITY.items():

        if company_name.upper() in company:

            best_priority = max(
                best_priority,
                int(priority),
            )

    return best_priority


# =========================================================
# PREFERRED COMPANY CHECK
# =========================================================

def is_preferred_company(job):
    return get_company_priority(job) > 0


# =========================================================
# VERIFIED JOB
# =========================================================

def is_verified_job(job):
    """
    A job is considered verified when:

        company exists
        apply_url exists
        source exists
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
# DATE PARSER
# =========================================================

def parse_posted_datetime(value):
    """
    Parse common job posting date formats.
    """

    raw = safe_text(value)

    if not raw:
        return None

    raw_lower = raw.lower()

    # -----------------------------------------------------
    # Today
    # -----------------------------------------------------

    if "today" in raw_lower:

        return datetime.now()

    # -----------------------------------------------------
    # Yesterday
    # -----------------------------------------------------

    if "yesterday" in raw_lower:

        from datetime import timedelta

        return datetime.now() - timedelta(
            days=1
        )

    # -----------------------------------------------------
    # Relative days
    # -----------------------------------------------------

    match = re.search(
        r"(\d+)\s*day",
        raw_lower,
    )

    if match:

        from datetime import timedelta

        days_ago = int(
            match.group(1)
        )

        return (
            datetime.now()
            - timedelta(days=days_ago)
        )

    # -----------------------------------------------------
    # ISO
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
# EXPIRED JOB
# =========================================================

def is_expired_job(job):
    """
    Hide jobs older than JOB_ACTIVE_DAYS.

    Unknown dates are retained.
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

    # Timezone-aware date
    if posted_dt.tzinfo is not None:

        posted_dt = posted_dt.replace(
            tzinfo=None
        )

    age_days = (
        datetime.now()
        - posted_dt
    ).total_seconds() / 86400

    return age_days > JOB_ACTIVE_DAYS


# =========================================================
# EXCLUDED JOB
# =========================================================

def is_excluded_job(job):
    """
    Exclude DevOps/Airflow-specific TITLE roles.

    IMPORTANT:
    We only inspect the title.

    Therefore a Data Engineer mentioning
    Airflow or DevOps in the description remains
    valid.
    """

    title = safe_text(
        job.get("title")
    )

    return any(
        keyword in title
        for keyword in EXCLUDED_JOB_TITLE_KEYWORDS
    )


# =========================================================
# VALID JOB
# =========================================================

def is_valid_job(job):
    """
    Final UAT validation.
    """

    if is_expired_job(job):
        return False

    if is_excluded_job(job):
        return False

    return True


# =========================================================
# FILTER VALID JOBS
# =========================================================

def filter_valid_jobs(jobs):

    return [
        job
        for job in jobs
        if is_valid_job(job)
    ]


# =========================================================
# LOAD SEARCH RESULTS
# =========================================================

def load_search_results(search):
    """
    Load current jobs from database.

    IMPORTANT:
        No scheduler is executed here.
    """

    search = str(
        search or ""
    ).strip()

    # -----------------------------------------------------
    # Explicitly block excluded searches
    # -----------------------------------------------------

    search_lower = search.lower()

    if (
        search_lower == "devops"
        or search_lower == "airflow"
        or "devops engineer" in search_lower
        or "airflow engineer" in search_lower
    ):

        return []

    # -----------------------------------------------------
    # No search
    # -----------------------------------------------------

    if not search:

        try:

            jobs = get_jobs_paginated(
                page=1,
                page_size=MAX_JOBS_TO_LOAD,
            )

            return filter_valid_jobs(
                jobs or []
            )

        except Exception as error:

            st.error(
                f"Unable to load jobs: {error}"
            )

            return []

    # -----------------------------------------------------
    # Database search
    # -----------------------------------------------------

    try:

        jobs = search_jobs(
            keyword=search,
            category="All Jobs",
            company="",
            country="",
            employment_type="",
            source="",
            limit=MAX_JOBS_TO_LOAD,
            offset=0,
        )

        jobs = list(
            jobs or []
        )

        # -------------------------------------------------
        # IMPORTANT:
        # DB search can return broad results.
        #
        # Apply our local AND-word search to ensure:
        #
        # Azure Data Engineer
        #
        # does not return unrelated jobs.
        # -------------------------------------------------

        jobs = local_keyword_search(
            jobs,
            search,
        )

        return filter_valid_jobs(
            jobs
        )

    except TypeError:

        # Compatibility with older db_service.py
        try:

            jobs = search_jobs(
                keyword=search,
                category="All Jobs",
            )

            jobs = list(
                jobs or []
            )

            jobs = local_keyword_search(
                jobs,
                search,
            )

            return filter_valid_jobs(
                jobs
            )

        except Exception:
            pass

    except Exception:
        pass

    # -----------------------------------------------------
    # FINAL FALLBACK
    # -----------------------------------------------------

    try:

        all_jobs = get_jobs_paginated(
            page=1,
            page_size=MAX_JOBS_TO_LOAD,
        )

        jobs = local_keyword_search(
            all_jobs or [],
            search,
        )

        return filter_valid_jobs(
            jobs
        )

    except Exception as error:

        st.error(
            f"Unable to search jobs: {error}"
        )

        return []


# =========================================================
# APPLY MAIN FILTER
# =========================================================

def apply_location_filter(
    jobs,
    filter_value,
):
    """
    Main radio filter.

    Supported:

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

        # -------------------------------------------------
        # IMPORTANT:
        #
        # Abroad is NOT "all foreign jobs".
        #
        # Only VisionBoard target technology jobs.
        # -------------------------------------------------

        return [
            job
            for job in jobs
            if (
                is_abroad_job(job)
                and is_data_engineering_job(job)
            )
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

    Higher company priority first.
    Latest jobs next.
    """

    def sort_key(job):

        india = is_india_job(job)

        remote = is_remote_job(job)

        if india:
            location_group = 1

        elif remote:
            location_group = 2

        else:
            location_group = 3

        company_priority = (
            get_company_priority(job)
        )

        posted = safe_text(
            job.get("posted_date")
        )

        return (
            location_group,
            -company_priority,
            posted,
        )

    return sorted(
        jobs,
        key=sort_key,
        reverse=False,
    )


# =========================================================
# BETTER PRIORITY SORT
# =========================================================

def sort_recommended_jobs(jobs):
    """
    Explicit VisionBoard recommendation ordering.

    India:
        preferred companies first

    Remote:
        preferred companies first

    Abroad:
        preferred companies first
    """

    def group(job):

        if is_india_job(job):
            return 1

        if is_remote_job(job):
            return 2

        return 3

    def priority(job):

        return get_company_priority(job)

    return sorted(
        jobs,
        key=lambda job: (
            group(job),
            -priority(job),
            safe_text(
                job.get("posted_date")
            ),
        ),
    )


# =========================================================
# SORT JOBS
# =========================================================

def sort_jobs(
    jobs,
    sort,
):

    if sort == "Latest Jobs":

        return sorted(
            jobs,
            key=lambda job: safe_text(
                job.get("posted_date")
            ),
            reverse=True,
        )

    if sort == "Company A-Z":

        return sorted(
            jobs,
            key=lambda job: safe_text(
                job.get("company")
            ),
        )

    if sort == "India First":

        return sorted(
            jobs,
            key=lambda job: (
                not is_india_job(job),
                -get_company_priority(job),
            ),
        )

    if sort == "Remote First":

        return sorted(
            jobs,
            key=lambda job: (
                not is_remote_job(job),
                not is_india_job(job),
                -get_company_priority(job),
            ),
        )

    return jobs


# =========================================================
# SHOW PAGINATION
# =========================================================

def show_pagination(
    page,
    total_pages,
    prefix,
):
    """
    Reusable pagination component.
    """

    page_window = 5

    start_page = max(
        1,
        page - 2,
    )

    end_page = min(
        total_pages,
        start_page + page_window - 1,
    )

    if (
        end_page - start_page
        < page_window - 1
    ):

        start_page = max(
            1,
            end_page - page_window + 1,
        )

    left, center, right = st.columns(
        [2, 6, 2]
    )

    with left:

        if st.button(
            "⬅ Previous",
            key=f"{prefix}_previous",
            disabled=(page <= 1),
            use_container_width=True,
        ):

            st.session_state.page = max(
                1,
                page - 1,
            )

            st.rerun()

    with center:

        page_columns = st.columns(
            end_page - start_page + 1
        )

        for index, page_no in enumerate(
            range(
                start_page,
                end_page + 1,
            )
        ):

            with page_columns[index]:

                if st.button(
                    (
                        f"● {page_no}"
                        if page_no == page
                        else str(page_no)
                    ),
                    key=f"{prefix}_page_{page_no}",
                    use_container_width=True,
                    type=(
                        "primary"
                        if page_no == page
                        else "secondary"
                    ),
                ):

                    st.session_state.page = (
                        page_no
                    )

                    st.rerun()

    with right:

        if st.button(
            "Next ➜",
            key=f"{prefix}_next",
            disabled=(page >= total_pages),
            use_container_width=True,
        ):

            st.session_state.page = min(
                total_pages,
                page + 1,
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
    Main VisionBoard home page.

    IMPORTANT:
    This signature matches your current filters.py:

        return (
            search,
            filter_value,
            india_only,
            remote_only,
            abroad_only,
            verified_only,
        )

    app.py should call:

        filters = show_filters()
        show_home(*filters)
    """

    # =====================================================
    # SESSION STATE
    # =====================================================

    if "page" not in st.session_state:
        st.session_state.page = 1

    # =====================================================
    # NORMALIZE FILTER
    # =====================================================

    filter_value = (
        str(filter_value or "All Jobs")
        .strip()
    )

    search = (
        str(search or "")
        .strip()
    )

    # =====================================================
    # EFFECTIVE FILTER
    # =====================================================

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
    # RESET PAGE WHEN FILTER CHANGES
    # =====================================================

    current_filter = (
        search,
        effective_filter,
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

    page = st.session_state.page

    # =====================================================
    # HEADER
    # =====================================================

    st.markdown(
        """
        <div id="visionboard-top"></div>
        """,
        unsafe_allow_html=True,
    )

    st.header(
        "VisionBoard Career Portal"
    )

    st.caption(
        "Discover the latest opportunities "
        "from Fortune 500 companies across "
        "India and worldwide."
    )

    # =====================================================
    # LOAD JOBS
    # =====================================================

    jobs = load_search_results(
        search
    )

    # =====================================================
    # SAFETY
    # =====================================================

    if jobs is None:
        jobs = []

    jobs = list(jobs)

    # =====================================================
    # RANKING
    # =====================================================

    try:

        jobs = rank_jobs(
            jobs
        )

    except Exception:
        # Ranking must never break the portal.
        pass

    # =====================================================
    # MAIN RADIO FILTER
    # =====================================================

    jobs = apply_location_filter(
        jobs,
        effective_filter,
    )

    # =====================================================
    # FINAL RECOMMENDED ORDER
    # =====================================================

    jobs = sort_recommended_jobs(
        jobs
    )

    # =====================================================
    # COUNTS
    # =====================================================

    total_jobs = len(jobs)

    india_count = sum(
        1
        for job in jobs
        if is_india_job(job)
    )

    remote_count = sum(
        1
        for job in jobs
        if is_remote_job(job)
    )

    abroad_count = sum(
        1
        for job in jobs
        if is_abroad_job(job)
    )

    preferred_count = sum(
        1
        for job in jobs
        if is_preferred_company(job)
    )

    # =====================================================
    # HEADER STATISTICS
    # =====================================================

    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🇮🇳 India",
            india_count,
        )

    with c2:

        st.metric(
            "⭐ Preferred",
            preferred_count,
        )

    with c3:

        st.metric(
            "🌍 Remote",
            remote_count,
        )

    with c4:

        st.metric(
            "✈ Abroad",
            abroad_count,
        )

    # =====================================================
    # FILTER STATUS
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
            "Showing global Data Engineering "
            "and Cloud opportunities."
        )

    elif effective_filter == "Verified Jobs":

        status_text = (
            "Showing verified opportunities."
        )

    else:

        status_text = (
            "Showing the latest relevant opportunities."
        )

    st.markdown(
        f"""
        <div style="
            display:inline-block;
            margin:8px 0 14px 0;
            padding:7px 14px;
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
    # RESULTS HEADER
    # =====================================================

    header_left, header_right = st.columns(
        [5, 1]
    )

    with header_left:

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
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "Latest relevant opportunities "
            "from leading companies across "
            "India and worldwide."
        )

    with header_right:

        st.metric(
            "Jobs Found",
            total_jobs,
        )

    # =====================================================
    # NO RESULTS
    # =====================================================

    if total_jobs == 0:

        st.warning(
            """
            No jobs found matching the selected filter.

            Try:
            • Another keyword
            • All Jobs
            • India
            • Remote
            • Another technology
            """
        )

        return

    # =====================================================
    # PAGINATION
    # =====================================================

    actual_total_pages = max(
        1,
        math.ceil(
            total_jobs / PAGE_SIZE
        ),
    )

    total_pages = min(
        actual_total_pages,
        MAX_PAGES,
    )

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
    # TOP PAGINATION
    # =====================================================

    st.divider()

    show_pagination(
        page,
        total_pages,
        "top",
    )

    # =====================================================
    # RESULT RANGE
    # =====================================================

    showing_from = (
        start + 1
    )

    showing_to = min(
        end,
        total_jobs,
    )

    st.info(
        f"Showing **{showing_from}** "
        f"to **{showing_to}** "
        f"of **{total_jobs}** live opportunities."
    )

    # =====================================================
    # JOB CARDS
    # =====================================================

    for job in jobs_to_show:

        try:

            show_job_card(
                job
            )

        except Exception as error:

            st.error(
                f"Unable to display job card: {error}"
            )

        st.markdown(
            "<div style='height:10px'></div>",
            unsafe_allow_html=True,
        )

    # =====================================================
    # BOTTOM PAGINATION
    # =====================================================

    st.divider()

    show_pagination(
        page,
        total_pages,
        "bottom",
    )

    # =====================================================
    # ABOUT
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
            "relevant global Data Engineering and "
            "Cloud careers."
        )

        st.caption(
            "Jobs are automatically synchronized "
            "every 6 hours and ranked to help "
            "candidates find relevant opportunities faster."
        )

    # =====================================================
    # SYNC INFORMATION
    # =====================================================

    st.caption(
        "🔄 Jobs are automatically synchronized "
        "every 6 hours."
    )

    st.caption(
        f"Showing {len(jobs_to_show)} jobs on this page."
    )