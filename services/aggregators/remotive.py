import requests

from services.filters.job_filter import is_relevant_job

BASE_URL = "https://remotive.com/api/remote-jobs"


def fetch_remotive_jobs():

    headers = {
        "User-Agent": "VisionBoard-JobPortal"
    }

    try:

        response = requests.get(
            BASE_URL,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        jobs = response.json().get(
            "jobs",
            []
        )

        filtered = []

        for job in jobs:

            if is_relevant_job(
                job.get("title", ""),
                job.get("description", ""),
                " ".join(job.get("tags", []))
            ):

                filtered.append(job)

        print(f"Remotive : {len(filtered)} matching jobs.")

        return filtered

    except Exception as e:

        print(e)

        return []