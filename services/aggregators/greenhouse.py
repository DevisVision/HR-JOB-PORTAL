"""
services/aggregators/greenhouse.py

Fetch jobs from Greenhouse public job boards.
"""

import requests

HEADERS = {
    "User-Agent": "VisionBoard-JobPortal"
}

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
    "zapier",

]


def fetch_greenhouse_jobs():
    """
    Fetch raw jobs from all configured Greenhouse boards.
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
                timeout=30,
            )

            if response.status_code != 200:
                continue

            jobs = response.json().get("jobs", [])

            for job in jobs:

                job["company_name"] = company.title()

                all_jobs.append(job)

        except Exception:
            continue

    print(f"Greenhouse: {len(all_jobs)} jobs received.")

    return all_jobs


if __name__ == "__main__":

    jobs = fetch_greenhouse_jobs()

    print(len(jobs))