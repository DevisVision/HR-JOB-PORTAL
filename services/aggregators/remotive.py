"""
services/aggregators/remotive.py

Fetch jobs from Remotive API.
"""

import requests

BASE_URL = "https://remotive.com/api/remote-jobs"


def fetch_remotive_jobs():
    """
    Fetch raw jobs from Remotive.
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

        jobs = response.json().get(
            "jobs",
            [],
        )

        print(f"Remotive: {len(jobs)} jobs received.")

        return jobs

    except Exception as ex:

        print(f"Remotive Error: {ex}")

        return []