"""
Normalize The Muse jobs into the VisionBoard standard schema.
"""


def normalize(job):

    if not job:
        return None

    # -------------------------------------------------------
    # Location
    # -------------------------------------------------------

    locations = job.get("locations", [])

    location = ""

    if locations:

        location = locations[0].get("name", "")

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
    # Employment Type
    # -------------------------------------------------------

    employment = ""

    levels = job.get("levels", [])

    if levels:

        employment = levels[0].get("name", "")

    # -------------------------------------------------------
    # Work Mode
    # -------------------------------------------------------

    work_mode = ""

    if "remote" in location.lower():

        work_mode = "Remote"

    # -------------------------------------------------------
    # Return Standard Format
    # -------------------------------------------------------

    return {

        "job_id": str(job.get("id")),

        "title": job.get("name", ""),

        "company": job.get(
            "company",
            {}
        ).get(
            "name",
            ""
        ),

        "location": location,

        "country": country,

        "employment_type": employment,

        "work_mode": work_mode,

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