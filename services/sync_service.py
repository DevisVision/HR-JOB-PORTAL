"""
=========================================================
VisionBoard Career Portal
Job Synchronization Service
=========================================================
Fetches jobs from all aggregators,
normalizes data,
filters,
ranks,
and saves into SQLite.
=========================================================
"""

import traceback
from datetime import datetime

from database.db_service import (
    insert_jobs,
    create_indexes,
    record_sync_completion,
    get_last_successful_sync,
)
from services.company.resolver import (
    normalize_company,
    sort_by_company_priority,
)

from services.ranking import rank_jobs
# =========================================================
# Aggregators
# =========================================================

from services.aggregators.adzuna import fetch_adzuna_jobs as fetch_adzuna
from services.aggregators.arbeitnow import fetch_arbeitnow_jobs as fetch_arbeitnow
from services.aggregators.greenhouse import fetch_greenhouse_jobs as fetch_greenhouse
from services.aggregators.lever import fetch_lever_jobs as fetch_lever
from services.aggregators.remoteok import fetch_remoteok_jobs as fetch_remoteok
from services.aggregators.remotive import fetch_remotive_jobs as fetch_remotive
from services.aggregators.themuse import fetch_themuse_jobs as fetch_themuse
from services.aggregators.usajobs import fetch_usajobs as fetch_usajobs

# =========================================================
# Normalizers
# =========================================================

from services.normalizers.adzuna import normalize as normalize_adzuna
from services.normalizers.arbeitnow import normalize as normalize_arbeitnow
from services.normalizers.greenhouse import normalize_greenhouse_job as normalize_greenhouse
from services.normalizers.lever import normalize as normalize_lever
from services.normalizers.remoteok import normalize as normalize_remoteok
from services.normalizers.remotive import normalize as normalize_remotive
from services.normalizers.themuse import normalize as normalize_themuse
from services.normalizers.usajobs import normalize as normalize_usajobs


# =========================================================
# Preferred Companies
# =========================================================

PREFERRED_COMPANIES = [

    "IBM",

    "MICROSOFT",

    "GOOGLE",

    "AMAZON",

    "APPLE",

    "META",

    "NETFLIX",

    "ACCENTURE",

    "COGNIZANT",

    "CAPGEMINI",

    "EY",

    "ERNST & YOUNG",

    "DELOITTE",

    "KPMG",

    "PWC",

    "UST",

    "ORACLE",

    "CISCO",

    "WIPRO",

    "INFOSYS",

    "TCS",

    "HCL",

    "TECH MAHINDRA",

    "ALLIANZ",

    "SAP",

    "ADOBE",

    "NVIDIA",

]


# =========================================================
# Aggregator Registry
# =========================================================

AGGREGATORS = [

    {
        "name": "Adzuna",
        "fetch": fetch_adzuna,
        "normalize": normalize_adzuna,
    },

    {
        "name": "ArbeitNow",
        "fetch": fetch_arbeitnow,
        "normalize": normalize_arbeitnow,
    },

    {
        "name": "Greenhouse",
        "fetch": fetch_greenhouse,
        "normalize": normalize_greenhouse,
    },

    {
        "name": "Lever",
        "fetch": fetch_lever,
        "normalize": normalize_lever,
    },

    {
        "name": "RemoteOK",
        "fetch": fetch_remoteok,
        "normalize": normalize_remoteok,
    },

    {
        "name": "Remotive",
        "fetch": fetch_remotive,
        "normalize": normalize_remotive,
    },

    {
        "name": "TheMuse",
        "fetch": fetch_themuse,
        "normalize": normalize_themuse,
    },

    {
        "name": "USAJobs",
        "fetch": fetch_usajobs,
        "normalize": normalize_usajobs,
    },

]


# =========================================================
# Company Name Standardization
# =========================================================

COMPANY_ALIASES = {

    "IBM INDIA": "IBM",
    "IBM INDIA PVT LTD": "IBM",
    "IBM GLOBAL": "IBM",

    "ERNST & YOUNG": "EY",
    "EY GDS": "EY",

    "COGNIZANT TECHNOLOGY SOLUTIONS": "COGNIZANT",

    "CAPGEMINI INDIA": "CAPGEMINI",

    "TECH MAHINDRA LIMITED": "TECH MAHINDRA",

    "MICROSOFT INDIA": "MICROSOFT",

    "GOOGLE INDIA": "GOOGLE",

    "AMAZON DEVELOPMENT CENTER": "AMAZON",

    "WIPRO LIMITED": "WIPRO",

    "TATA CONSULTANCY SERVICES": "TCS",

    "INFOSYS LIMITED": "INFOSYS",

    "HCL TECHNOLOGIES": "HCL",

}


def normalize_company_name(company):

    if not company:
        return "Unknown"

    company = company.strip().upper()

    for alias, canonical in COMPANY_ALIASES.items():

        if alias in company:
            return canonical

    return company.title()


# =========================================================
# Logging Helper
# =========================================================

def log(message):

    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
    )
# =========================================================
# Validate Job
# =========================================================

def is_valid_job(job):
    """
    Basic validation to ensure only useful jobs
    are inserted into the database.
    """

    if not job:
        return False

    required = [
        "job_id",
        "title",
        "company",
        "apply_url",
    ]

    for field in required:

        value = str(job.get(field, "")).strip()

        if value == "":
            return False

    return True


# =========================================================
# Clean Job
# =========================================================

def clean_job(job):
    """
    Cleans and standardizes a normalized job.
    """

    job["company"] = normalize_company_name(
        job.get("company", "")
    )

    job["title"] = str(
        job.get("title", "")
    ).strip()

    job["location"] = str(
        job.get("location", "")
    ).strip()

    job["country"] = str(
        job.get("country", "")
    ).strip()

    job["skills"] = str(
        job.get("skills", "")
    ).strip()

    job["salary"] = str(
        job.get("salary", "")
    ).strip()

    job["employment_type"] = str(
        job.get("employment_type", "")
    ).strip()

    job["description"] = str(
        job.get("description", "")
    ).strip()

    return job


# =========================================================
# Execute One Aggregator
# =========================================================

def run_aggregator(config):
    """
    Fetches and normalizes jobs from one aggregator.
    """

    name = config["name"]

    fetch = config["fetch"]

    normalize = config["normalize"]

    jobs = []

    try:

        log(f"Fetching {name}...")

        raw_jobs = fetch()

        if raw_jobs is None:

            log(f"{name} returned None.")

            return []

        log(f"{name}: {len(raw_jobs)} jobs fetched.")

        for raw in raw_jobs:

            try:

                job = normalize(raw)

                if not is_valid_job(job):

                    continue

                job = clean_job(job)

                jobs.append(job)

            except Exception:

                traceback.print_exc()

        log(f"{name}: {len(jobs)} jobs normalized.")

        return jobs

    except Exception:

        traceback.print_exc()

        log(f"{name}: FAILED")

        return []


# =========================================================
# Fetch All Aggregators
# =========================================================

def fetch_all_jobs():
    """
    Executes all aggregators and combines the results.
    """

    all_jobs = []

    total_sources = len(AGGREGATORS)

    log("=" * 60)

    log(f"Running {total_sources} aggregators...")

    log("=" * 60)

    for config in AGGREGATORS:

        jobs = run_aggregator(config)

        all_jobs.extend(jobs)

        log(
            f"Current Total Jobs : {len(all_jobs)}"
        )

    log("=" * 60)

    log(f"Total Jobs Collected : {len(all_jobs)}")

    log("=" * 60)

    return all_jobs
# =========================================================
# Remove Duplicates
# =========================================================

def remove_duplicates(jobs):
    """
    Remove duplicate jobs based on
    Title + Company + Location.
    """

    unique = {}

    for job in jobs:

        key = (
            job.get("title", "").strip().lower(),
            job.get("company", "").strip().lower(),
            job.get("location", "").strip().lower(),
        )

        unique[key] = job

    return list(unique.values())



# =========================================================
# Quality Filter
# =========================================================

def filter_quality_jobs(jobs):

    filtered = []

    for job in jobs:

        if not job.get("title"):
            continue

        if not job.get("company"):
            continue

        if not job.get("apply_url"):
            continue

        if len(job.get("title", "")) < 3:
            continue

        filtered.append(job)

    return filtered


# =========================================================
# Fortune Company Priority
# =========================================================

def apply_company_priority(jobs):
    """
    Gives preferred companies the highest priority.
    """

    preferred = []

    others = []

    for job in jobs:

        company = str(
            job.get("company", "")
        ).upper()

        if company in PREFERRED_COMPANIES:

            job["priority"] = 100

            preferred.append(job)

        else:

            job["priority"] = 10

            others.append(job)

    log(
        f"Preferred Companies : {len(preferred)}"
    )

    return preferred + others


# =========================================================
# India Priority
# =========================================================

INDIA_KEYWORDS = [

    "india",

    "bangalore",

    "bengaluru",

    "hyderabad",

    "pune",

    "chennai",

    "gurgaon",

    "gurugram",

    "noida",

    "kochi",

    "mumbai",

    "delhi",

]


def prioritize_india_jobs(jobs):

    india = []

    world = []

    for job in jobs:

        text = (

            str(job.get("country", "")) +

            " " +

            str(job.get("location", ""))

        ).lower()

        if any(city in text for city in INDIA_KEYWORDS):

            india.append(job)

        else:

            world.append(job)

    return india + world


# =========================================================
# Processing Pipeline
# =========================================================

def process_jobs(jobs):
    """
    Complete processing pipeline.
    """

    print(f"Processing {len(jobs)} jobs...")

    # Normalize company names
    jobs = [normalize_company(job) for job in jobs]

    # Remove duplicates
    jobs = remove_duplicates(jobs)

    # Remove low quality jobs
    jobs = filter_quality_jobs(jobs)

    # India first
    jobs = prioritize_india_jobs(jobs)

    # Preferred companies first
    jobs = sort_by_company_priority(jobs)

    # Final ranking
    jobs = rank_jobs(jobs)

    print(f"Remaining Jobs: {len(jobs)}")

    return jobs

# ---------------------------------------
# Remove Low Quality Jobs
# ---------------------------------------

def filter_quality_jobs(jobs):

    filtered = []

    for job in jobs:

        if not job.get("title"):
            continue

        if not job.get("company"):
            continue

        if not job.get("apply_url"):
            continue

        if len(job.get("title", "")) < 3:
            continue

        filtered.append(job)

    return filtered

    # ---------------------------------------
    # India First
    # ---------------------------------------

    jobs = prioritize_india_jobs(jobs)

    # ---------------------------------------
    # Preferred Companies First
    # ---------------------------------------

    jobs = sort_by_company_priority(jobs)

    # ---------------------------------------
    # Final Ranking
    # ---------------------------------------

    jobs = rank_jobs(jobs)

    print(f"Remaining Jobs : {len(jobs)}")

    return jobs
# =========================================================
# Save Jobs
# =========================================================

def save_jobs(jobs):
    """
    Saves processed jobs into the database.
    """

    if not jobs:

        log("No jobs to save.")

        return 0

    try:

        insert_jobs(jobs)

        create_indexes()

        log(f"Successfully saved {len(jobs)} jobs.")

        return len(jobs)

    except Exception:

        traceback.print_exc()

        log("Database insert failed.")

        return 0


# =========================================================
# Synchronization Summary
# =========================================================

def print_summary(raw_count, final_count):

    print()

    print("=" * 70)
    print(" VisionBoard Career Portal - Synchronization Summary")
    print("=" * 70)

    print(f"Raw Jobs Retrieved      : {raw_count}")
    print(f"Final Jobs Saved        : {final_count}")
    print(f"Duplicates Removed      : {raw_count - final_count}")
    print(f"Completed At            : {datetime.now()}")

    print("=" * 70)
    print()


# =========================================================
# Main Synchronization Pipeline
# =========================================================

def sync_jobs():
    """
    Main synchronization workflow.
    """

    log("=" * 70)
    log("Starting VisionBoard Job Synchronization")
    log("=" * 70)

    # -----------------------------------------
    # Fetch Jobs
    # -----------------------------------------

    jobs = fetch_all_jobs()

    raw_count = len(jobs)

    if raw_count == 0:

        log("No jobs received from any aggregator.")

        return

    # -----------------------------------------
    # Process Jobs
    # -----------------------------------------

    jobs = process_jobs(jobs)

    final_count = len(jobs)

    # -----------------------------------------
    # Save to Database
    # -----------------------------------------

    saved = save_jobs(jobs)

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    print_summary(raw_count, saved)

    log("Synchronization Completed Successfully.")


# =========================================================
# Run from Command Line
# =========================================================

if __name__ == "__main__":

    sync_jobs()
# =========================================================
# Sync Statistics
# =========================================================

SYNC_STATS = {

    "aggregators": 0,

    "raw_jobs": 0,

    "processed_jobs": 0,

    "saved_jobs": 0,

    "failed_aggregators": [],

    "started": None,

    "completed": None,

}


# =========================================================
# Reset Statistics
# =========================================================

def reset_statistics():

    SYNC_STATS["aggregators"] = 0

    SYNC_STATS["raw_jobs"] = 0

    SYNC_STATS["processed_jobs"] = 0

    SYNC_STATS["saved_jobs"] = 0

    SYNC_STATS["failed_aggregators"] = []

    SYNC_STATS["started"] = datetime.now()

    SYNC_STATS["completed"] = None


# =========================================================
# Print Statistics
# =========================================================

def print_statistics():

    print()

    print("=" * 70)

    print(" VisionBoard Synchronization Statistics")

    print("=" * 70)

    print(
        f"Started              : {SYNC_STATS['started']}"
    )

    print(
        f"Completed            : {SYNC_STATS['completed']}"
    )

    print(
        f"Aggregators          : {SYNC_STATS['aggregators']}"
    )

    print(
        f"Raw Jobs             : {SYNC_STATS['raw_jobs']}"
    )

    print(
        f"Processed Jobs       : {SYNC_STATS['processed_jobs']}"
    )

    print(
        f"Saved Jobs           : {SYNC_STATS['saved_jobs']}"
    )

    print(
        f"Failed Sources       : "
        f"{len(SYNC_STATS['failed_aggregators'])}"
    )

    if SYNC_STATS["failed_aggregators"]:

        print()

        print("Failed Aggregators:")

        for item in SYNC_STATS["failed_aggregators"]:

            print("  •", item)

    print("=" * 70)

    print()


# =========================================================
# Database Maintenance
# =========================================================

def database_maintenance():

    log("Running database maintenance...")

    create_indexes()

    log("Database optimized.")


# =========================================================
# Update Statistics
# =========================================================

def update_statistics(
    raw_jobs,
    processed_jobs,
    saved_jobs,
):

    SYNC_STATS["aggregators"] = len(AGGREGATORS)

    SYNC_STATS["raw_jobs"] = raw_jobs

    SYNC_STATS["processed_jobs"] = processed_jobs

    SYNC_STATS["saved_jobs"] = saved_jobs

    SYNC_STATS["completed"] = datetime.now()


# =========================================================
# Scheduler Entry Point
# =========================================================

def scheduled_sync():

    log("=" * 70)

    log("Scheduled Synchronization Started")

    log("=" * 70)

    reset_statistics()

    jobs = fetch_all_jobs()

    raw_jobs = len(jobs)

    jobs = process_jobs(jobs)

    processed_jobs = len(jobs)

    saved_jobs = save_jobs(jobs)

    database_maintenance()

    update_statistics(

        raw_jobs,

        processed_jobs,

        saved_jobs,

    )

    print_statistics()

    log("Scheduled Synchronization Finished.")
# =========================================================
# Retry Helper
# =========================================================

import time


def run_aggregator_with_retry(config, retries=2, delay=2):
    """
    Runs one aggregator with retry support.
    """

    for attempt in range(1, retries + 2):

        try:

            return run_aggregator(config)

        except Exception:

            traceback.print_exc()

            log(
                f"{config['name']} failed "
                f"(Attempt {attempt}/{retries + 1})"
            )

            if attempt <= retries:

                time.sleep(delay)

    SYNC_STATS["failed_aggregators"].append(
        config["name"]
    )

    return []


# =========================================================
# Health Report
# =========================================================

def print_health_report():

    print()
    print("=" * 70)
    print(" Aggregator Health Report")
    print("=" * 70)

    total = len(AGGREGATORS)

    failed = len(
        SYNC_STATS["failed_aggregators"]
    )

    successful = total - failed

    print(f"Total Aggregators : {total}")
    print(f"Successful        : {successful}")
    print(f"Failed            : {failed}")

    if failed:

        print()

        for source in SYNC_STATS["failed_aggregators"]:

            print("  ✖", source)

    print("=" * 70)
    print()


# =========================================================
# Safe Synchronization
# =========================================================

def safe_sync():

    reset_statistics()

    all_jobs = []

    log("=" * 70)
    log("Starting Safe Synchronization")
    log("=" * 70)

    try:
        for config in AGGREGATORS:

            jobs = run_aggregator_with_retry(config)

            all_jobs.extend(jobs)

        raw_jobs = len(all_jobs)

        processed_jobs = process_jobs(all_jobs)

        saved_jobs = save_jobs(processed_jobs)

        database_maintenance()

        update_statistics(
            raw_jobs,
            len(processed_jobs),
            saved_jobs,
        )

        # Record the completion separately from individual job updated_at values.
        # This does not alter job filtering, ranking, ordering, or posted dates.
        if SYNC_STATS["failed_aggregators"] and not processed_jobs:
            record_sync_completion(
                "failed",
                saved_jobs,
                "; ".join(SYNC_STATS["failed_aggregators"]),
            )
        else:
            record_sync_completion("completed", saved_jobs)

        print_statistics()
        print_health_report()
        log("Synchronization Finished Successfully.")

        return saved_jobs

    except Exception as exc:
        try:
            record_sync_completion("failed", 0, str(exc))
        except Exception:
            pass
        raise


def sync_is_due(interval_hours=6):
    """Return True when the portal has never completed a sync or the last one is older than the interval."""
    last_sync = get_last_successful_sync()

    if not last_sync:
        return True

    try:
        last_dt = datetime.fromisoformat(str(last_sync).replace("Z", "+00:00"))
        # SQLite CURRENT_TIMESTAMP is stored as UTC. Treat a naive
        # timestamp from sync_logs as UTC, not as the Streamlit server's
        # local time. This keeps the 6-hour interval correct on Cloud.
        if last_dt.tzinfo is None:
            from datetime import timezone
            last_dt = last_dt.replace(tzinfo=timezone.utc)

        from datetime import timezone
        now = datetime.now(timezone.utc)
        return (now - last_dt).total_seconds() >= interval_hours * 3600
    except (TypeError, ValueError):
        # A malformed/missing sync timestamp should cause a safe refresh.
        return True


def maybe_run_scheduled_sync(interval_hours=6):
    """Run the existing safe sync only when the last successful sync is due."""
    if not sync_is_due(interval_hours):
        return False

    safe_sync()
    return True


# =========================================================
# Application Entry Point
# =========================================================

if __name__ == "__main__":

    safe_sync()