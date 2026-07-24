"""
services/normalizers/adzuna.py

Normalize Adzuna jobs into the standard VisionBoard schema.
"""


def normalize(job):
    """
    Normalize one Adzuna job.
    """

    if not job:
        return None

    company = (
        job.get("company", {})
           .get("display_name", "")
    )

    location = (
        job.get("location", {})
           .get("display_name", "")
    )

    country = (
        job.get("location", {})
           .get("area", [""])
    )

    if isinstance(country, list):
        country = country[0] if country else ""

    salary = ""

    if job.get("salary_min") and job.get("salary_max"):

        salary = (
            f"{job.get('salary_min')} - "
            f"{job.get('salary_max')}"
        )

    elif job.get("salary_min"):

        salary = str(job.get("salary_min"))

    elif job.get("salary_max"):

        salary = str(job.get("salary_max"))

    return {

        "job_id": str(job.get("id")),

        "title": job.get("title", ""),

        "company": company,

        "location": location,

        "country": country,

        "employment_type": job.get("contract_type", ""),

        "skills": "",

        "salary": salary,

        "description": job.get("description", ""),

        "source": "Adzuna",

        "apply_url": job.get("redirect_url", ""),

        "posted_date": job.get("created", "")
    }