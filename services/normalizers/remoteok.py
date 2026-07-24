"""
Normalize RemoteOK jobs.
"""


def normalize(job):

    if not job:
        return None

    tags = job.get("tags", [])

    return {

        "job_id": str(job.get("id")),

        "title": job.get("position", ""),

        "company": job.get("company", ""),

        "location": job.get("location", ""),

        "country": "",

        "employment_type": "",

        "skills": ", ".join(tags),

        "salary": "",

        "description": job.get(
            "description",
            ""
        ),

        "source": "RemoteOK",

        "apply_url": job.get("apply_url") or job.get("url", ""),

        "posted_date": job.get(
            "date",
            ""
        )
    }