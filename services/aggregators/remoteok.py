import requests

from services.filters.job_filter import is_relevant_job

BASE_URL = "https://remoteok.com/api"


def fetch_remoteok_jobs():

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

        jobs = response.json()

        if isinstance(jobs, list):
            jobs = jobs[1:]

        filtered = []

        for job in jobs:

            if is_relevant_job(
                job.get("position", ""),
                job.get("description", ""),
                " ".join(job.get("tags", []))
            ):

                filtered.append(job)

        print(f"RemoteOK : {len(filtered)} matching jobs.")

        return filtered

    except Exception as e:

        print(e)

        return []