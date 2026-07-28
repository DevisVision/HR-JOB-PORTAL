"""
services/aggregators/lever.py

Fetch jobs from Lever public job boards.
"""

import requests

HEADERS = {
    "User-Agent": "VisionBoard-JobPortal"
}

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
    "headspace",

]


def fetch_lever_jobs():
    """
    Fetch raw jobs from all Lever boards.
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
                timeout=30,
            )

            if response.status_code != 200:
                continue

            jobs = response.json()

            for job in jobs:

                job["company_name"] = (
                    company.replace("-", " ").title()
                )

                all_jobs.append(job)

        except Exception:
            continue

    print(f"Lever: {len(all_jobs)} jobs received.")

    return all_jobs


if __name__ == "__main__":

    jobs = fetch_lever_jobs()

    print(len(jobs))    