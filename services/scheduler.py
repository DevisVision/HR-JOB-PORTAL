"""
sync_service.py

Fetches jobs from Adzuna,
normalizes them,
and stores them in SQLite.
"""

from services.aggregators.adzuna import fetch_adzuna_jobs
from services.normalize import normalize_adzuna_job
from database.db_service import insert_job


def sync_adzuna():
    """
    Fetch jobs from Adzuna,
    normalize them,
    and save them into SQLite.
    """

    print("=" * 60)
    print("Starting Adzuna Job Synchronization...")
    print("=" * 60)

    raw_jobs = fetch_adzuna_jobs()

    print(f"\nFetched {len(raw_jobs)} raw jobs.\n")

    success = 0
    failed = 0

    for job in raw_jobs:

        try:

            normalized_job = normalize_adzuna_job(job)

            insert_job(normalized_job)

            success += 1

        except Exception as e:

            failed += 1

            print(
                f"Failed to process Job ID "
                f"{job.get('id', 'Unknown')} : {e}"
            )

    print("\n" + "=" * 60)
    print("Synchronization Completed")
    print("=" * 60)

    print(f"Jobs Processed : {len(raw_jobs)}")
    print(f"Inserted/Updated : {success}")
    print(f"Failed : {failed}")

    return success


if __name__ == "__main__":

    sync_adzuna()