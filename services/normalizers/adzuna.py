"""
services/normalizers/adzuna.py

Normalize Adzuna jobs into the VisionBoard standard schema.
"""

from services.company_logo import get_company_logo


def normalize(job):
    """
    Normalize one Adzuna job.
    """

    if not job:
        return None

    company = (
        job.get("company", {})
        .get("display_name", "")
        .strip()
    )

    location = (
        job.get("location", {})
        .get("display_name", "")
    )

    country = ""

    area = (
        job.get("location", {})
        .get("area", [])
    )

    if isinstance(area, list) and area:
        country = area[0]

    salary = ""

    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")

    if salary_min and salary_max:
        salary = f"{salary_min} - {salary_max}"
    elif salary_min:
        salary = str(salary_min)
    elif salary_max:
        salary = str(salary_max)

    return {

        "job_id": str(job.get("id", "")),

        "title": job.get("title", ""),

        "company": company,

        "company_logo": get_company_logo(company),

        "location": location,

        "country": country,

        "employment_type": job.get("contract_type", ""),

        "work_mode": "",

        "job_category": job.get("category", {}).get("label", ""),

        "skills": "",

        "salary": salary,

        "description": job.get("description", ""),

        "source": "Adzuna",

        "apply_url": job.get("redirect_url", ""),

        "priority": 1,

        "is_active": 1,

        "posted_date": job.get("created", ""),
    }