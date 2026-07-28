"""
services/aggregators/adzuna.py

Fetch jobs from Adzuna API.
"""

import os
import requests
from dotenv import load_dotenv

# Load .env FIRST
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def fetch_adzuna_jobs(
    country="in",
    page=1,
    results_per_page=50,
):
    """
    Fetch jobs from Adzuna API.
    """

    if not APP_ID or not APP_KEY:
        print("Adzuna API credentials not found.")
        return []

    url = f"{BASE_URL}/{country}/search/{page}"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", [])

    except Exception as ex:

        print(f"Adzuna Error: {ex}")

        return []