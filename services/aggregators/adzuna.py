"""Adzuna job source for VisionBoard V5."""

import os
import time
import requests

from dotenv import load_dotenv
from config.job_keywords import JOB_SEARCHES

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
COUNTRY = os.getenv("ADZUNA_COUNTRY", "in")
MAX_PAGES = max(1, int(os.getenv("ADZUNA_MAX_PAGES", "2")))
RESULTS_PER_PAGE = min(50, max(10, int(os.getenv("ADZUNA_RESULTS_PER_PAGE", "50"))))

BASE_URL = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{{page}}"
HEADERS = {"User-Agent": "VisionBoard Job Portal"}


def fetch_adzuna_jobs():
    """Fetch multiple Adzuna pages per configured role, with deduplication."""
    all_jobs = []
    seen = set()
    print("Fetching Adzuna jobs...")

    for keyword in JOB_SEARCHES:
        for page in range(1, MAX_PAGES + 1):
            params = {
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "results_per_page": RESULTS_PER_PAGE,
                "what": keyword,
                "content-type": "application/json",
            }

            for attempt in range(3):
                try:
                    response = requests.get(
                        BASE_URL.format(page=page),
                        params=params,
                        headers=HEADERS,
                        timeout=30,
                    )
                    response.raise_for_status()
                    jobs = response.json().get("results", [])

                    for job in jobs:
                        job_id = str(job.get("id", "")).strip()
                        if not job_id or job_id in seen:
                            continue
                        seen.add(job_id)
                        all_jobs.append(job)

                    # A short final page means later pages are unlikely to add much.
                    if len(jobs) < RESULTS_PER_PAGE:
                        break
                    break

                except requests.exceptions.HTTPError as ex:
                    status = ex.response.status_code if ex.response else None
                    if status in {429, 500, 502, 503, 504} and attempt < 2:
                        time.sleep(2 * (attempt + 1))
                        continue
                    print(f"Adzuna error ({keyword}, page {page}) : {ex}")
                    break
                except requests.exceptions.RequestException as ex:
                    if attempt < 2:
                        time.sleep(2 * (attempt + 1))
                        continue
                    print(f"Adzuna network error ({keyword}, page {page}) : {ex}")
                    break
                except Exception as ex:
                    print(f"Adzuna unexpected error ({keyword}, page {page}) : {ex}")
                    break

            time.sleep(0.15)

    print(f"Adzuna : {len(all_jobs)} unique jobs.")
    return all_jobs
