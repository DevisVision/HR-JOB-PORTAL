"""
Lever Jobs Aggregator

Fetches jobs from Lever public job boards.
"""

import requests

from services.filters.job_filter import is_relevant_job


# ----------------------------------------------------------
# Public Lever Job Boards
# ----------------------------------------------------------

LEVER_COMPANIES = [

    "netflix",
    "atlassian",
    "discord",
    "robinhood",
    "zapier",
    "circleci",
    "eventbrite",
    "flexport",
    "hudl",
    "plaid",
    "scale-ai",
    "rippling",
    "canva",
    "headspace"

]


HEADERS = {

    "User-Agent": "Mozilla/5.0"

}


def fetch_lever_jobs():

    """
    Fetch jobs from all configured Lever boards.
    """

    all_jobs = []

    for company in LEVER_COMPANIES:

        url = (
            f"https://api.lever.co/v0/postings/"
            f"{company}?mode=json"
        )

        try:

            response = requests.get(

                url,

                headers=HEADERS,

                timeout=30

            )
            print(f"{company} -> {response.status_code}")
            if response.status_code != 200:
                continue

            jobs = response.json()
            print(f"{company}: {len(jobs)} jobs")
            for job in jobs:

                title = job.get("text", "")

                description = job.get(
                    "descriptionPlain",
                    ""
                )

                if not is_relevant_job(

                    title=title,

                    description=description,

                    tags=""

                ):

                    continue

                job["company_name"] = company.replace(
                    "-",
                    " "
                ).title()

                all_jobs.append(job)

        except Exception:

            continue

    print(f"Lever : {len(all_jobs)} matching jobs.")

    return all_jobs


if __name__ == "__main__":

    jobs = fetch_lever_jobs()

    print(f"Retrieved {len(jobs)} jobs")

    if jobs:

        print("\nSample Job\n")

        print(jobs[0])