"""
Greenhouse Job Normalizer

Converts Greenhouse jobs into the standard VisionBoard format.
"""

from datetime import datetime


def normalize_greenhouse_job(job):

    return {

        "job_id": f"greenhouse_{job.get('id')}",

        "title": job.get("title", ""),

        "company": job.get("company_name", "Unknown"),

        "location": (
            job.get("location", {}).get("name", "")
            if isinstance(job.get("location"), dict)
            else ""
        ),

        "country": "",

        "employment_type": "",

        "work_mode": "",

        "skills": "",

        "salary": "",

        "description": "",

        "source": "Greenhouse",

        "apply_url": job.get("absolute_url", ""),

        "posted_date": job.get(
            "updated_at",
            datetime.now().isoformat()
        )

    }