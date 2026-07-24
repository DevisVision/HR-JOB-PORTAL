"""
Normalize The Muse jobs.
"""


def normalize(job):

    if not job:
        return None

    locations = job.get("locations", [])

    location = ""

    if locations:

        location = locations[0].get("name", "")

    return {

        "job_id": str(job.get("id")),

        "title": job.get("name", ""),

        "company": job.get(
            "company",
            {}
        ).get("name", ""),

        "location": location,

        "country": "",

        "employment_type": "",

        "skills": "",

        "salary": "",

        "description": job.get(
            "contents",
            ""
        ),

        "source": "TheMuse",

        "apply_url": job.get(
            "refs",
            {}
        ).get(
            "landing_page",
            ""
        ),

        "posted_date": job.get(
            "publication_date",
            ""
        )
    }