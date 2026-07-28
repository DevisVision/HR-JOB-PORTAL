"""
services/sync_service.py

Master synchronization service.

Workflow

1. Fetch jobs from all aggregators
2. Normalize jobs
3. Batch insert into SQLite
4. Log synchronization
"""

from datetime import datetime

from database.db_service import insert_jobs
from services.filters.job_filter import is_relevant_job
from services.enrichment import enrich_job

# ===========================================================
# Aggregators
# ===========================================================

from services.aggregators.adzuna import fetch_adzuna_jobs
from services.aggregators.arbeitnow import fetch_arbeitnow_jobs
from services.aggregators.remotive import fetch_remotive_jobs
from services.aggregators.remoteok import fetch_remoteok_jobs
from services.aggregators.greenhouse import fetch_greenhouse_jobs
from services.aggregators.themuse import fetch_themuse_jobs
from services.aggregators.usajobs import fetch_usajobs
from services.aggregators.lever import fetch_lever_jobs

# ===========================================================
# Normalizers
# ===========================================================

from services.normalizers.adzuna import normalize as normalize_adzuna
from services.normalizers.arbeitnow import normalize as normalize_arbeitnow
from services.normalizers.remotive import normalize as normalize_remotive
from services.normalizers.remoteok import normalize as normalize_remoteok
from services.normalizers.greenhouse import (normalize_greenhouse_job)
from services.normalizers.themuse import normalize as normalize_themuse
from services.normalizers.usajobs import normalize as normalize_usajobs
from services.normalizers.lever import normalize as normalize_lever


# ===========================================================
# Generic Processor
# ===========================================================

def process_source(
    source_name,
    fetch_function,
    normalize_function
):
    """
    Fetch, normalize and insert jobs from one source.
    """

    print("\n" + "=" * 70)
    print(f"{source_name.upper()} SYNCHRONIZATION")
    print("=" * 70)

    start_time = datetime.now()

    raw_jobs = fetch_function()

    print(f"Fetched {len(raw_jobs)} jobs.")

    batch_jobs = []

    processed = 0
    failed = 0

    for job in raw_jobs:

        try:

            normalized = normalize_function(job)

            if normalized:

    # ---------------------------------------------
    # Common enrichment
    # ---------------------------------------------
                normalized = enrich_job(normalized)

                batch_jobs.append(normalized)

                processed += 1

        except Exception as ex:

            failed += 1

            print(ex)

    if batch_jobs:

        insert_jobs(batch_jobs)

    duration = (
        datetime.now() - start_time
    ).total_seconds()

    print("-" * 70)
    print(f"Raw Jobs      : {len(raw_jobs)}")
    print(f"Processed     : {processed}")
    print(f"Inserted      : {len(batch_jobs)}")
    print(f"Failed        : {failed}")
    print(f"Execution     : {duration:.2f} sec")
    print("-" * 70)

    return len(batch_jobs)


# ===========================================================
# Master Synchronization
# ===========================================================

def sync_all_jobs():

    print("\n")
    print("=" * 70)
    print("VISIONBOARD JOB PORTAL")
    print("MASTER SYNCHRONIZATION")
    print("=" * 70)

    total = 0

    # -------------------------------------------------------
    # Adzuna
    # -------------------------------------------------------

    total += process_source(
        "Adzuna",
        fetch_adzuna_jobs,
        normalize_adzuna
    )

    # -------------------------------------------------------
    # Arbeitnow
    # -------------------------------------------------------

    total += process_source(
        "Arbeitnow",
        fetch_arbeitnow_jobs,
        normalize_arbeitnow
    )

    # -------------------------------------------------------
    # Remotive
    # -------------------------------------------------------

    total += process_source(
        "Remotive",
        fetch_remotive_jobs,
        normalize_remotive
    )

    # -------------------------------------------------------
    # RemoteOK
    # -------------------------------------------------------

    total += process_source(
        "RemoteOK",
        fetch_remoteok_jobs,
        normalize_remoteok
    )

    # -------------------------------------------------------
    # Greenhouse
    # -------------------------------------------------------

    total += process_source(
        "Greenhouse",
        fetch_greenhouse_jobs,
        normalize_greenhouse_job
    )
    # -------------------------------------------------------
    # Lever
    # -------------------------------------------------------

    #total += process_source(
    #    "Lever",
    #    fetch_lever_jobs,
    #    normalize_lever
    #)
    # -------------------------------------------------------
    # The Muse
    # -------------------------------------------------------

    #try:

    #    total += process_source(
    #        "TheMuse",
    #        fetch_themuse_jobs,
    #        normalize_themuse
    #    )

    #except Exception as ex:

    #    print(f"TheMuse skipped : {ex}")

    # -------------------------------------------------------
    # USAJobs
    # -------------------------------------------------------

    #try:

     #   total += process_source(
    #        "USAJobs",
    #        fetch_usajobs,
     #       normalize_usajobs
     #   )

    #except Exception as ex:

     #   print(f"USAJobs skipped : {ex}")

    print("\n")
    print("=" * 70)
    print(f"TOTAL JOBS SYNCHRONIZED : {total}")
    print("=" * 70)

    return total


if __name__ == "__main__":

    sync_all_jobs()