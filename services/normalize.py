"""
services/normalize.py
"""

from services.company_logo import get_company_logo


def normalize_adzuna_job(job):

    company = (
        job.get("company", {})
        .get("display_name", "")
        .strip()
    )

    return {

        "job_id": str(job.get("id", "")),

        "title": job.get("title", ""),

        "company": company,

        "company_logo": get_company_logo(company),

        "location": (
            job.get("location", {})
            .get("display_name", "")
        ),

        "country": "",

        "employment_type": job.get("contract_type", ""),

        "work_mode": "",

        "job_category": "",

        "skills": "",

        "salary": (
            f"{job.get('salary_min','')} - {job.get('salary_max','')}"
            if job.get("salary_min")
            else ""
        ),

        "description": job.get("description", ""),

        "source": "Adzuna",

        "apply_url": job.get("redirect_url", ""),

        "priority": 1,

        "is_active": 1,

        "posted_date": job.get("created", ""),
    }