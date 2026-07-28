"""
services/normalizers/greenhouse.py

Normalize Greenhouse jobs into the VisionBoard standard schema.
"""

from datetime import datetime

from services.company_logo import get_company_logo


def normalize_greenhouse_job(job):
    """
    Normalize one Greenhouse job.
    """

    if not job:
        return None

    company = job.get("company_name", "Unknown Company").strip()

    # ----------------------------------------------------
    # Location
    # ----------------------------------------------------

    location = ""

    if isinstance(job.get("location"), dict):
        location = job["location"].get("name", "")

    # ----------------------------------------------------
    # Country
    # ----------------------------------------------------

    country = ""

    if location:

        loc = location.lower()

        if "india" in loc:
            country = "India"

        elif "remote" in loc:
            country = "Remote"

    # ----------------------------------------------------
    # Metadata
    # ----------------------------------------------------

    employment = ""

    salary = ""

    work_mode = ""

    skills = []

    metadata = job.get("metadata", [])

    if isinstance(metadata, list):

        for item in metadata:

            if not isinstance(item, dict):
                continue

            name = str(item.get("name", "")).lower()

            value = str(item.get("value", "")).strip()

            if not value:
                continue

            if "employment" in name or "type" in name:
                employment = value

            elif "salary" in name or "compensation" in name:
                salary = value

            elif "remote" in name or "work" in name:
                work_mode = value

            elif "skill" in name:
                skills.append(value)

    # ----------------------------------------------------
    # Description
    # ----------------------------------------------------

    description = (
        job.get("content")
        or job.get("description")
        or ""
    )

    # ----------------------------------------------------
    # Return Standard Schema
    # ----------------------------------------------------

    return {

        "job_id": f"greenhouse_{job.get('id')}",

        "title": job.get("title", ""),

        "company": company,

        "company_logo": get_company_logo(company),

        "location": location,

        "country": country,

        "employment_type": employment,

        "work_mode": work_mode,

        "job_category": "",

        "skills": ", ".join(skills),

        "salary": salary,

        "description": description,

        "source": "Greenhouse",

        "apply_url": job.get("absolute_url", ""),

        "priority": 3,

        "is_active": 1,

        "posted_date": job.get(
            "updated_at",
            datetime.now().isoformat(),
        ),
    }