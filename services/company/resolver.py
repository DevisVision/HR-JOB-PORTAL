"""
=========================================================
VisionBoard Career Portal
Company Resolver
=========================================================

Responsibilities
----------------
1. Normalize company names
2. Resolve aliases
3. Detect preferred companies
4. Assign company priority
5. Provide logo lookup key

=========================================================
"""

import re

from services.company.aliases import COMPANY_ALIASES
from services.company.preferred_companies import (
    get_company_priority,
    is_preferred_company,
)

# =========================================================
# Words to Remove
# =========================================================

REMOVE_WORDS = {

    "PRIVATE",
    "PVT",
    "PVT.",
    "LIMITED",
    "LTD",
    "LTD.",
    "INC",
    "INC.",
    "LLC",
    "PLC",
    "CORP",
    "CORPORATION",
    "COMPANY",
    "GROUP",

}

# =========================================================
# Clean Company Name
# =========================================================

def clean_company_name(company: str) -> str:
    """
    Removes unnecessary words and punctuation.
    """

    if not company:
        return ""

    company = company.upper()

    company = re.sub(r"[^\w\s&]", " ", company)

    words = []

    for word in company.split():

        if word not in REMOVE_WORDS:

            words.append(word)

    return " ".join(words).strip()


# =========================================================
# Resolve Alias
# =========================================================

def resolve_alias(company: str) -> str:
    """
    Converts aliases into a canonical company name.
    """

    cleaned = clean_company_name(company)

    return COMPANY_ALIASES.get(cleaned, cleaned.title())


# =========================================================
# Company Information
# =========================================================

def resolve_company(company: str) -> dict:
    """
    Returns standardized company information.
    """

    canonical = resolve_alias(company)

    return {

        "original_name": company,

        "company": canonical,

        "preferred": is_preferred_company(canonical),

        "priority": get_company_priority(canonical),

        "logo_key": canonical.lower().replace(" ", "_"),

    }


# =========================================================
# Normalize Job
# =========================================================

def normalize_company(job: dict) -> dict:
    """
    Updates a job dictionary with normalized company data.
    """

    info = resolve_company(job.get("company", ""))

    job["company"] = info["company"]
    job["company_priority"] = info["priority"]
    job["preferred_company"] = info["preferred"]
    job["logo_key"] = info["logo_key"]

    return job


# =========================================================
# Preferred Company Filter
# =========================================================

def filter_preferred_companies(jobs):
    """
    Returns only preferred-company jobs.
    """

    return [

        normalize_company(job)

        for job in jobs

        if resolve_company(
            job.get("company", "")
        )["preferred"]

    ]


# =========================================================
# Sort by Company Priority
# =========================================================

def sort_by_company_priority(jobs):
    """
    Highest-priority companies appear first.
    """

    jobs = [

        normalize_company(job)

        for job in jobs

    ]

    return sorted(

        jobs,

        key=lambda x: (

            x.get("company_priority", 0),

            x.get("company", ""),

        ),

        reverse=True,

    )


# =========================================================
# Search by Company
# =========================================================

def search_company(jobs, company_name):
    """
    Search jobs by company name.
    """

    company_name = resolve_alias(company_name)

    return [

        normalize_company(job)

        for job in jobs

        if resolve_alias(

            job.get("company", "")

        ) == company_name

    ]