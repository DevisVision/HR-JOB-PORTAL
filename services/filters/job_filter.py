"""
=========================================================
VisionBoard Career Portal
Backend Job Relevance Filter
services/filters/job_filter.py
=========================================================

Used by job aggregators before normalization.

Purpose:
    - Keep relevant Data / AI / Cloud / Analytics jobs
    - Remove DevOps-only roles
    - Remove Airflow-only roles
    - Avoid filtering out legitimate Data Engineer jobs
      merely because DevOps/Airflow is mentioned in the
      description.
=========================================================
"""

import re

from config.job_keywords import JOB_SEARCHES


# =========================================================
# EXCLUDED JOB TITLE KEYWORDS
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
    "apache airflow",
]


# =========================================================
# SAFE TEXT
# =========================================================

def safe_text(value):
    if value is None:
        return ""

    return str(value).strip()


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):
    text = safe_text(value).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# =========================================================
# EXCLUDED TITLE CHECK
# =========================================================

def is_excluded_title(title):
    """
    Exclude only jobs whose TITLE is specifically
    DevOps/Airflow focused.

    Example:

        DevOps Engineer
            -> excluded

        Airflow Engineer
            -> excluded

        Data Engineer - Airflow
            -> allowed

        Azure Data Engineer - DevOps knowledge
            -> allowed
    """

    title = normalize_text(title)

    if not title:
        return False

    return any(
        keyword in title
        for keyword in EXCLUDED_JOB_TITLE_KEYWORDS
    )


# =========================================================
# SEARCH KEYWORD CHECK
# =========================================================

def contains_job_keyword(
    title,
    description,
    tags,
):
    """
    Checks whether the job matches one of the
    configured VisionBoard search keywords.
    """

    combined_text = " ".join(
        [
            normalize_text(title),
            normalize_text(description),
            normalize_text(tags),
        ]
    )

    if not combined_text:
        return False

    for keyword in JOB_SEARCHES:

        keyword = normalize_text(keyword)

        if not keyword:
            continue

        if keyword in combined_text:
            return True

    return False


# =========================================================
# MAIN RELEVANCE FILTER
# =========================================================

def is_relevant_job(
    title="",
    description="",
    tags="",
):
    """
    Determine whether a job should be accepted
    by the aggregator.

    Rules:

    1. Empty title -> reject
    2. DevOps/Airflow-only title -> reject
    3. Must contain at least one configured
       VisionBoard job keyword
    """

    title = safe_text(title)
    description = safe_text(description)
    tags = safe_text(tags)

    # -----------------------------------------------------
    # Title is mandatory
    # -----------------------------------------------------

    if not title:
        return False

    # -----------------------------------------------------
    # Remove unwanted job categories
    # -----------------------------------------------------

    if is_excluded_title(title):
        return False

    # -----------------------------------------------------
    # Check relevance
    # -----------------------------------------------------

    return contains_job_keyword(
        title,
        description,
        tags,
    )