"""
Lever Job Normalizer

Converts Lever jobs into the VisionBoard standard schema.
"""


def normalize(job):

    if not job:
        return None

    # -------------------------------------------------------
    # Categories
    # -------------------------------------------------------

    categories = job.get("categories", {})

    location = categories.get("location", "")

    employment = categories.get("commitment", "")

    work_mode = categories.get("workplace", "")

    # -------------------------------------------------------
    # Country Detection
    # -------------------------------------------------------

    country = ""

    if location:

        location_lower = location.lower()

        if "india" in location_lower:

            country = "India"

        elif "remote" in location_lower:

            country = "Remote"

    # -------------------------------------------------------
    # Description
    # -------------------------------------------------------

    description = (
        job.get("descriptionPlain")
        or job.get("description")
        or ""
    )

    # -------------------------------------------------------
    # Posted Date
    # -------------------------------------------------------

    posted = ""

    if job.get("createdAt"):

        posted = str(job.get("createdAt"))

    elif job.get("updatedAt"):

        posted = str(job.get("updatedAt"))

    # -------------------------------------------------------
    # Return Standard Format
    # -------------------------------------------------------

    return {

        "job_id": f"lever_{job.get('id')}",

        "title": job.get("text", ""),

        "company": job.get(
            "company_name",
            "Unknown Company"
        ),

        "location": location,

        "country": country,

        "employment_type": employment,

        "work_mode": work_mode,

        "skills": "",

        "salary": "",

        "description": description,

        "source": "Lever",

        "apply_url": job.get(
            "hostedUrl",
            ""
        ),

        "posted_date": posted
    }