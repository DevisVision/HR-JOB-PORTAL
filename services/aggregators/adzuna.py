import os
import time
import requests

from dotenv import load_dotenv
from config.job_keywords import JOB_SEARCHES

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
COUNTRY = os.getenv("ADZUNA_COUNTRY", "in")

BASE_URL = (
    f"https://api.adzuna.com/v1/api/jobs/"
    f"{COUNTRY}/search/1"
)

HEADERS = {
    "User-Agent": "VisionBoard Job Portal"
}


def fetch_adzuna_jobs():
    """
    Fetch jobs from Adzuna.

    Features:
    - Duplicate removal
    - Automatic retry on temporary server errors
    - Rate-limit friendly
    """

    all_jobs = []
    seen = set()

    print("Fetching Adzuna jobs...")

    for keyword in JOB_SEARCHES:

        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 50,
            "what": keyword,
            "content-type": "application/json"
        }

        max_retries = 3

        for attempt in range(max_retries):

            try:

                response = requests.get(
                    BASE_URL,
                    params=params,
                    headers=HEADERS,
                    timeout=30
                )

                response.raise_for_status()

                jobs = response.json().get("results", [])

                for job in jobs:

                    job_id = job.get("id")

                    if job_id not in seen:
                        seen.add(job_id)
                        all_jobs.append(job)

                # Success, stop retrying
                break

            except requests.exceptions.HTTPError as ex:

                status_code = ex.response.status_code if ex.response else None

                # Retry only for temporary server errors
                if status_code == 503 and attempt < max_retries - 1:

                    print(
                        f"503 received for '{keyword}'. "
                        f"Retrying ({attempt + 1}/{max_retries})..."
                    )

                    time.sleep(2)

                    continue

                print(f"Adzuna error ({keyword}) : {ex}")

                break

            except requests.exceptions.RequestException as ex:

                print(f"Network error ({keyword}) : {ex}")

                break

            except Exception as ex:

                print(f"Unexpected error ({keyword}) : {ex}")

                break

        # Small delay to reduce throttling
        time.sleep(0.2)

    print(f"Adzuna : {len(all_jobs)} unique jobs.")

    return all_jobs