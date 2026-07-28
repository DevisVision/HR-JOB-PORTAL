"""
Normalize USAJobs into VisionBoard standard schema.
"""


def normalize(job):

    if not job:
        return None

    data = job.get(
        "MatchedObjectDescriptor",
        {}
    )

    # --------------------------------------------
    # Location
    # --------------------------------------------

    location = data.get(
        "PositionLocationDisplay",
        ""
    )

    # --------------------------------------------
    # Employment Type
    # --------------------------------------------

    employment = ""

    schedule = data.get("PositionSchedule", [])

    if schedule:

        employment = schedule[0].get(
            "Name",
            ""
        )

    # --------------------------------------------
    # Work Mode
    # --------------------------------------------

    work_mode = ""

    if "remote" in location.lower():

        work_mode = "Remote"

    # --------------------------------------------
    # Salary
    # --------------------------------------------

    salary = ""

    remuneration = data.get(
        "PositionRemuneration",
        []
    )

    if remuneration:

        minimum = remuneration[0].get(
            "MinimumRange"
        )

        maximum = remuneration[0].get(
            "MaximumRange"
        )

        if minimum and maximum:

            salary = f"${minimum:,} - ${maximum:,}"

    # --------------------------------------------
    # Return
    # --------------------------------------------

    return {

        "job_id": str(
            data.get(
                "PositionID",
                ""
            )
        ),

        "title": data.get(
            "PositionTitle",
            ""
        ),

        "company": "USA Government",

        "location": location,

        "country": "USA",

        "employment_type": employment,

        "work_mode": work_mode,

        "skills": "",

        "salary": salary,

        "description": data.get(
            "UserArea",
            {}
        ).get(
            "Details",
            {}
        ).get(
            "JobSummary",
            ""
        ),

        "source": "USAJobs",

        "apply_url": data.get(
            "PositionURI",
            ""
        ),

        "posted_date": data.get(
            "PublicationStartDate",
            ""
        )
    }