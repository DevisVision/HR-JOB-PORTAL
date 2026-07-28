"""
services/normalizers/remotive.py

Normalize Remotive jobs into the VisionBoard standard schema.
"""

from services.company_logo import get_company_logo


def normalize(job):
    """
    Normalize one Remotive job.
    """

    if not job:
        return None

    company = job.get("company_name", "").strip()

    location = job.get(
        "candidate_required_location",
        ""
    )

    tags = job.get("tags", [])

    country = ""

    if location:

        loc = location.lower()

        if "india" in loc:
            country = "India"

        elif "remote" in loc:
            country = "Remote"

    return {

        "job_id": str(job.get("id", "")),

        "title": job.get("title", ""),

        "company": company,

        "company_logo": get_company_logo(company),

        "location": location,

        "country": country,

        "employment_type": job.get("job_type", ""),

        "work_mode": "Remote",

        "job_category": job.get("category", ""),

        "skills": ", ".join(tags),

        "salary": job.get("salary", ""),

        "description": job.get("description", ""),

        "source": "Remotive",

        "apply_url": job.get("url", ""),

        "priority": 2,

        "is_active": 1,

        "posted_date": job.get("publication_date", ""),
    }