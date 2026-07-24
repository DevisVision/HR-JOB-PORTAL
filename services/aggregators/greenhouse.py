"""
Greenhouse Jobs Aggregator

Fetches jobs from Greenhouse public job boards.
"""

import requests

from services.filters.job_filter import is_relevant_job


# ----------------------------------------------------------
# Public Greenhouse Job Boards
# ----------------------------------------------------------

GREENHOUSE_COMPANIES = [

    "openai",
    "anthropic",
    "cohere",

    "airbnb",
    "asana",
    "atlassian",
    "benchling",
    "brex",
    "canva",
    "checkr",
    "clickhouse",
    "cockroachlabs",
    "coinbase",
    "confluent",
    "crowdstrike",
    "datadog",
    "discord",
    "docker",
    "dropbox",
    "elastic",
    "figma",
    "fivetran",
    "gitlab",
    "grafana",
    "gusto",
    "hashicorp",
    "hubspot",
    "miro",
    "mongodb",
    "netlify",
    "notion",
    "okta",
    "planet",
    "plaid",
    "postman",
    "qualtrics",
    "ramp",
    "redis",
    "retool",
    "rippling",
    "scaleai",
    "slack",
    "snowflake",
    "sourcegraph",
    "stripe",
    "supabase",
    "snyk",
    "temporal",
    "unity",
    "vercel",
    "webflow",
    "zapier"

]


HEADERS = {

    "User-Agent": "Mozilla/5.0"

}


def fetch_greenhouse_jobs():

    """
    Fetch jobs from all configured Greenhouse boards.
    """

    all_jobs = []

    for company in GREENHOUSE_COMPANIES:

        url = (
            f"https://boards-api.greenhouse.io/v1/boards/"
            f"{company}/jobs"
        )

        try:

            response = requests.get(

                url,

                headers=HEADERS,

                timeout=30

            )

            if response.status_code != 200:
                continue

            data = response.json()

            jobs = data.get("jobs", [])

            for job in jobs:

                title = job.get("title", "")

                description = ""

                if not is_relevant_job(

                    title=title,

                    description=description,

                    tags=""

                ):

                    continue

                job["company_name"] = company.title()

                all_jobs.append(job)

        except Exception:

            continue

    print(f"Greenhouse : {len(all_jobs)} matching jobs.")

    return all_jobs


if __name__ == "__main__":

    jobs = fetch_greenhouse_jobs()

    print(f"Retrieved {len(jobs)} jobs")

    if jobs:

        print("\nSample Job\n")

        print(jobs[0])