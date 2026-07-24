"""
Normalize Remotive jobs.
"""


def normalize(job):

    if not job:
        return None

    tags = job.get("tags", [])

    return {

        "job_id": str(job.get("id")),

        "title": job.get("title", ""),

        "company": job.get("company_name", ""),

        "location": job.get(
            "candidate_required_location",
            ""
        ),

        "country": "",

        "employment_type": job.get(
            "job_type",
            ""
        ),

        "skills": ", ".join(tags),

        "salary": job.get(
            "salary",
            ""
        ),

        "description": job.get(
            "description",
            ""
        ),

        "source": "Remotive",

        "apply_url": job.get(
            "url",
            ""
        ),

        "posted_date": job.get(
            "publication_date",
            ""
        )
    }