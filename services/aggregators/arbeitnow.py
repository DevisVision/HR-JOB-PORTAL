"""
services/aggregators/arbeitnow.py

Fetch jobs from Arbeitnow API.
"""

import requests

BASE_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch_arbeitnow_jobs():
    """
    Fetch raw jobs from Arbeitnow.
    """

    headers = {
        "User-Agent": "VisionBoard-JobPortal"
    }

    try:

        response = requests.get(
            BASE_URL,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        jobs = response.json().get("data", [])

        print(f"Arbeitnow: {len(jobs)} jobs received.")

        return jobs

    except Exception as ex:

        print(f"Arbeitnow Error: {ex}")

        return []