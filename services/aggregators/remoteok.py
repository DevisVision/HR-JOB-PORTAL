"""
services/aggregators/remoteok.py

Fetch jobs from RemoteOK API.
"""

import requests

BASE_URL = "https://remoteok.com/api"


def fetch_remoteok_jobs():
    """
    Fetch raw jobs from RemoteOK.
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

        jobs = response.json()

        # First element contains metadata
        if isinstance(jobs, list):
            jobs = jobs[1:]

        print(f"RemoteOK: {len(jobs)} jobs received.")

        return jobs

    except Exception as ex:

        print(f"RemoteOK Error: {ex}")

        return []