import requests

BASE_URL = "https://www.themuse.com/api/public/jobs"


def fetch_themuse_jobs():
    """
    Fetch jobs from The Muse.
    """

    try:

        response = requests.get(
            BASE_URL,
            timeout=30,
            headers={
                "User-Agent": "VisionBoard-JobPortal"
            }
        )

        response.raise_for_status()

        jobs = response.json().get(
            "results",
            []
        )

        print(f"The Muse : {len(jobs)} jobs found.")

        return jobs

    except Exception as e:

        print("Failed to fetch The Muse.")

        print(e)

        return []