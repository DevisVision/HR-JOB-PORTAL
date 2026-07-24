"""
Normalize USAJobs.
"""


def normalize(job):

    if not job:
        return None

    data = job.get(
        "MatchedObjectDescriptor",
        {}
    )

    locations = data.get(
        "PositionLocationDisplay",
        ""
    )

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

        "location": locations,

        "country": "USA",

        "employment_type": "",

        "skills": "",

        "salary": "",

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