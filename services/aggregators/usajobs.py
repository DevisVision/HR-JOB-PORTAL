import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://data.usajobs.gov/api/search"

USER_AGENT = os.getenv("USAJOBS_USER_AGENT")
AUTH_KEY = os.getenv("USAJOBS_AUTH_KEY")


def fetch_usajobs():
    """
    Fetch jobs from USAJobs.
    """

    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": USER_AGENT,
        "Authorization-Key": AUTH_KEY
    }

    params = {
        "Keyword": "Data Engineer"
    }

    try:

        response = requests.get(
            BASE_URL,
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        jobs = (
            response.json()
            .get("SearchResult", {})
            .get("SearchResultItems", [])
        )

        print(f"USAJobs : {len(jobs)} jobs found.")

        return jobs

    except Exception as e:

        print("Failed to fetch USAJobs.")

        print(e)

        return []