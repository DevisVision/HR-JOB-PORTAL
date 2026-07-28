"""
RemoteOK Job Normalizer
"""

from services.company_logo import get_company_logo


def normalize(job):

    if not job:
        return None


    company = job.get(
        "company",
        ""
    )


    location = job.get(
        "location",
        ""
    )


    country = ""

    location_text = location.lower()


    if "india" in location_text:
        country = "India"

    elif "remote" in location_text:
        country = "Remote"


    tags = job.get(
        "tags",
        []
    )


    if isinstance(tags, list):

        skills = ", ".join(tags)

    else:

        skills = ""


    return {


        "job_id":
            f"remoteok_{job.get('id')}",


        "title":
            job.get(
                "position",
                ""
            ),


        "company":
            company,


        "company_logo":
            get_company_logo(company),


        "location":
            location,


        "country":
            country,


        "employment_type":
            job.get(
                "employment_type",
                ""
            ),


        "work_mode":
            "Remote",


        "job_category":
            "",


        "skills":
            skills,


        "salary":
            "",


        "description":
            job.get(
                "description",
                ""
            ),


        "source":
            "RemoteOK",


        "apply_url":
            job.get(
                "apply_url"
            )
            or job.get(
                "url",
                ""
            ),


        "priority":
            2,


        "is_active":
            1,


        "posted_date":
            job.get(
                "date",
                ""
            )
    }