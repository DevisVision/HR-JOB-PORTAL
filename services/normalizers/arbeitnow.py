"""
Normalize Arbeitnow jobs.
"""


def normalize(job):

    if not job:
        return None

    tags = job.get("tags", [])

    return {

        "job_id": str(job.get("slug")),

        "title": job.get("title", ""),

        "company": job.get("company_name", ""),

        "location": job.get("location", ""),

        "country": "",

        "employment_type": job.get("job_type", ""),

        "skills": ", ".join(tags),

        "salary": "",

        "description": job.get("description", ""),

        "source": "Arbeitnow",

        "apply_url": job.get("url", ""),

        "posted_date": job.get("created_at", "")
    }