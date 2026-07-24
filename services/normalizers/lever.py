"""
Lever Job Normalizer
"""


def normalize(job):

    categories = job.get("categories", {})

    return {

        "job_id": f"lever_{job.get('id')}",

        "title": job.get("text", ""),

        "company": job.get("company_name", ""),

        "location": categories.get("location", ""),

        "country": "",

        "employment_type": categories.get(
            "commitment",
            ""
        ),

        "skills": "",

        "salary": "",

        "description": job.get(
            "descriptionPlain",
            ""
        ),

        "source": "Lever",

        "apply_url": job.get(
            "hostedUrl",
            ""
        ),

        "posted_date": ""

    }