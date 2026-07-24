import requests

from config.job_keywords import JOB_SEARCHES
from services.filters.job_filter import is_relevant_job

BASE_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch_arbeitnow_jobs():
    """
    Fetch and filter relevant jobs from Arbeitnow.
    """

    headers = {
        "User-Agent": "VisionBoard-JobPortal"
    }

    filtered_jobs = []

    try:

        response = requests.get(
            BASE_URL,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        jobs = response.json().get("data", [])

        print(f"Arbeitnow : {len(jobs)} jobs received.")

        seen = set()

        for job in jobs:

            title = job.get("title", "")
            description = job.get("description", "")
            tags = " ".join(job.get("tags", []))

            if is_relevant_job(title, description, tags):

                job_id = job.get("slug")

                if job_id not in seen:
                    filtered_jobs.append(job)
                    seen.add(job_id)

        print(f"Arbeitnow : {len(filtered_jobs)} matching jobs.")

        return filtered_jobs

    except Exception as e:

        print("Failed to fetch Arbeitnow jobs.")
        print(e)

        return []