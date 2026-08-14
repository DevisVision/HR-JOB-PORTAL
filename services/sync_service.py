"""
VisionBoard Career Portal - V5 Job Synchronization Service.

V5 aggregation-only upgrade:
- Active sources: Adzuna, ArbeitNow, Greenhouse, Lever, RemoteOK,
  Remotive and Technopark.
- TheMuse and USAJobs remain in the repository but are intentionally NOT
  registered because their current endpoints are failing.
- Per-source accounting makes it clear where jobs are lost.
- Existing database, ranking, freshness and UI contracts are preserved.
"""

import time
import traceback
from collections import Counter
from datetime import datetime, timezone

from database.db_service import (
    insert_jobs,
    replace_source_and_insert_jobs,
    create_indexes,
    record_sync_completion,
    get_last_successful_sync,
)
from services.company.resolver import normalize_company, sort_by_company_priority
from services.ranking import rank_jobs
from services.filters.job_filter import is_relevant_job

from services.aggregators.adzuna import fetch_adzuna_jobs
from services.aggregators.arbeitnow import fetch_arbeitnow_jobs
from services.aggregators.greenhouse import fetch_greenhouse_jobs
from services.aggregators.lever import fetch_lever_jobs
from services.aggregators.remoteok import fetch_remoteok_jobs
from services.aggregators.remotive import fetch_remotive_jobs
from services.aggregators.technopark import fetch_technopark_jobs

from services.normalizers.adzuna import normalize as normalize_adzuna
from services.normalizers.arbeitnow import normalize as normalize_arbeitnow
from services.normalizers.greenhouse import normalize_greenhouse_job as normalize_greenhouse
from services.normalizers.lever import normalize as normalize_lever
from services.normalizers.remoteok import normalize as normalize_remoteok
from services.normalizers.remotive import normalize as normalize_remotive
from services.normalizers.technopark import normalize as normalize_technopark


PREFERRED_COMPANIES = [
    "IBM", "MICROSOFT", "GOOGLE", "AMAZON", "APPLE", "META", "NETFLIX",
    "ACCENTURE", "COGNIZANT", "CAPGEMINI", "EY", "ERNST & YOUNG",
    "DELOITTE", "KPMG", "PWC", "UST", "ORACLE", "CISCO", "WIPRO",
    "INFOSYS", "TCS", "HCL", "TECH MAHINDRA", "ALLIANZ", "SAP",
    "ADOBE", "NVIDIA",
]

COMPANY_ALIASES = {
    "IBM INDIA": "IBM", "IBM INDIA PVT LTD": "IBM", "IBM GLOBAL": "IBM",
    "ERNST & YOUNG": "EY", "EY GDS": "EY",
    "COGNIZANT TECHNOLOGY SOLUTIONS": "COGNIZANT",
    "CAPGEMINI INDIA": "CAPGEMINI", "TECH MAHINDRA LIMITED": "TECH MAHINDRA",
    "MICROSOFT INDIA": "MICROSOFT", "GOOGLE INDIA": "GOOGLE",
    "AMAZON DEVELOPMENT CENTER": "AMAZON", "WIPRO LIMITED": "WIPRO",
    "TATA CONSULTANCY SERVICES": "TCS", "INFOSYS LIMITED": "INFOSYS",
    "HCL TECHNOLOGIES": "HCL",
}


AGGREGATORS = [
    {"name": "Adzuna", "fetch": fetch_adzuna_jobs, "normalize": normalize_adzuna},
    {"name": "ArbeitNow", "fetch": fetch_arbeitnow_jobs, "normalize": normalize_arbeitnow},
    {"name": "Greenhouse", "fetch": fetch_greenhouse_jobs, "normalize": normalize_greenhouse},
    {"name": "Lever", "fetch": fetch_lever_jobs, "normalize": normalize_lever},
    {"name": "RemoteOK", "fetch": fetch_remoteok_jobs, "normalize": normalize_remoteok},
    {"name": "Remotive", "fetch": fetch_remotive_jobs, "normalize": normalize_remotive},
    {
        "name": "Technopark",
        "fetch": fetch_technopark_jobs,
        "normalize": normalize_technopark,
        "apply_relevance_filter": False,
    },
]

SYNC_STATS = {
    "aggregators": 0,
    "raw_jobs": 0,
    "processed_jobs": 0,
    "saved_jobs": 0,
    "failed_aggregators": [],
    "started": None,
    "completed": None,
    "source_stats": {},
}


def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


def normalize_company_name(company):
    if not company:
        return "Unknown"
    company = str(company).strip().upper()
    for alias, canonical in COMPANY_ALIASES.items():
        if alias in company:
            return canonical
    return company.title()


def is_valid_job(job):
    if not job:
        return False
    return all(str(job.get(field, "")).strip() for field in ("job_id", "title", "company", "apply_url"))


def clean_job(job):
    job["company"] = normalize_company_name(job.get("company", ""))
    for field in ("title", "location", "country", "skills", "salary", "employment_type", "description", "source", "apply_url", "posted_date"):
        job[field] = str(job.get(field, "") or "").strip()
    return job


def run_aggregator(config):
    name = config["name"]
    source_stats = {
        "fetched": 0, "normalized": 0, "relevant": 0, "invalid": 0,
        "failed": False,
    }
    try:
        log(f"Fetching {name}...")
        raw_jobs = config["fetch"]() or []
        source_stats["fetched"] = len(raw_jobs)
        log(f"{name}: {len(raw_jobs)} jobs fetched.")
        normalized = []
        for raw in raw_jobs:
            try:
                job = config["normalize"](raw)
                if not is_valid_job(job):
                    source_stats["invalid"] += 1
                    continue
                job = clean_job(job)
                normalized.append(job)
            except Exception:
                source_stats["invalid"] += 1
                traceback.print_exc()
        source_stats["normalized"] = len(normalized)

        # Most aggregators use the VisionBoard category filter at ingestion.
        # Technopark is different: it is a directory-style source and must
        # retain every active genuine posting so company searches (UST, IBS,
        # PITS, or any unknown company) can find them later. The home page
        # applies the category filter to the default Technopark feed.
        if config.get("apply_relevance_filter", True):
            accepted = [
                job
                for job in normalized
                if is_relevant_job(
                    job.get("title"),
                    job.get("description"),
                    job.get("skills"),
                )
            ]
        else:
            accepted = normalized

        source_stats["relevant"] = len(accepted)

        SYNC_STATS["source_stats"][name] = source_stats
        log(
            f"{name}: {len(accepted)} "
            f"{'relevant' if config.get('apply_relevance_filter', True) else 'accepted active'} "
            "jobs after normalization/filtering."
        )
        return accepted
    except Exception:
        source_stats["failed"] = True
        SYNC_STATS["source_stats"][name] = source_stats
        traceback.print_exc()
        log(f"{name}: FAILED")
        return []


def fetch_all_jobs():
    all_jobs = []
    for config in AGGREGATORS:
        jobs = run_aggregator(config)
        all_jobs.extend(jobs)
        log(f"Current Total Jobs : {len(all_jobs)}")
    log(f"Total Jobs Collected : {len(all_jobs)}")
    return all_jobs


def remove_duplicates(jobs):
    unique = {}
    for job in jobs:
        source_id = str(job.get("job_id", "")).strip().lower()
        key = (source_id,)
        # If a source has no stable ID, fall back to title/company/location.
        if not source_id:
            key = (
                str(job.get("title", "")).strip().lower(),
                str(job.get("company", "")).strip().lower(),
                str(job.get("location", "")).strip().lower(),
            )
        unique[key] = job
    return list(unique.values())


def filter_quality_jobs(jobs):
    return [
        job for job in jobs
        if len(str(job.get("title", "")).strip()) >= 3
        and str(job.get("company", "")).strip()
        and str(job.get("apply_url", "")).strip()
    ]


def process_jobs(jobs):
    print(f"Processing {len(jobs)} jobs...")
    jobs = [normalize_company(job) for job in jobs]
    before = len(jobs)
    jobs = remove_duplicates(jobs)
    duplicates = before - len(jobs)
    jobs = filter_quality_jobs(jobs)
    jobs = sort_by_company_priority(jobs)
    jobs = rank_jobs(jobs)
    print(f"Duplicates Removed: {duplicates}")
    print(f"Remaining Jobs: {len(jobs)}")
    return jobs


def save_jobs(jobs):
    """Save the sync batch without leaving stale Technopark rows behind.

    Technopark is a directory source.  When its employer parsing changes,
    INSERT OR REPLACE alone cannot remove the old malformed rows (for
    example company='Menu').  When a non-empty Technopark batch is present,
    replace_source_and_insert_jobs performs a source-only replacement inside
    one transaction.  All other sources keep the existing INSERT behavior.
    """
    if not jobs:
        log("No jobs to save.")
        return 0

    try:
        technopark_jobs = [
            job for job in jobs
            if str(job.get("source", "")).strip().lower() == "technopark"
        ]

        if technopark_jobs:
            saved = replace_source_and_insert_jobs(
                jobs,
                source="Technopark",
            )
            log(
                f"Successfully refreshed Technopark and saved "
                f"{len(jobs)} total jobs."
            )
        else:
            saved = insert_jobs(jobs)
            log(f"Successfully saved {len(jobs)} jobs.")

        create_indexes()
        return saved

    except Exception:
        traceback.print_exc()
        log("Database insert failed; transaction was rolled back.")
        return 0


def reset_statistics():
    SYNC_STATS.update({
        "aggregators": len(AGGREGATORS),
        "raw_jobs": 0,
        "processed_jobs": 0,
        "saved_jobs": 0,
        "failed_aggregators": [],
        "started": datetime.now(),
        "completed": None,
        "source_stats": {},
    })


def print_statistics():
    print("\n" + "=" * 70)
    print(" VisionBoard V5 Synchronization Statistics")
    print("=" * 70)
    print(f"Started              : {SYNC_STATS['started']}")
    print(f"Completed            : {SYNC_STATS['completed']}")
    print(f"Aggregators          : {SYNC_STATS['aggregators']}")
    print(f"Raw Jobs             : {SYNC_STATS['raw_jobs']}")
    print(f"Processed Jobs       : {SYNC_STATS['processed_jobs']}")
    print(f"Saved Jobs           : {SYNC_STATS['saved_jobs']}")
    print(f"Failed Sources       : {len(SYNC_STATS['failed_aggregators'])}")
    print("\nSource Breakdown")
    for name, stats in SYNC_STATS["source_stats"].items():
        status = "FAILED" if stats["failed"] else "OK"
        print(
            f"  {name:<12} {status:<6} "
            f"Fetched={stats['fetched']:<5} "
            f"Normalized={stats['normalized']:<5} "
            f"Relevant/Accepted={stats['relevant']:<5} "
            f"Invalid={stats['invalid']}"
        )
    print("=" * 70 + "\n")


def database_maintenance():
    log("Running database maintenance...")
    create_indexes()
    log("Database optimized.")


def update_statistics(raw_jobs, processed_jobs, saved_jobs):
    SYNC_STATS["raw_jobs"] = raw_jobs
    SYNC_STATS["processed_jobs"] = processed_jobs
    SYNC_STATS["saved_jobs"] = saved_jobs
    SYNC_STATS["completed"] = datetime.now()


def print_health_report():
    failed = [name for name, stats in SYNC_STATS["source_stats"].items() if stats["failed"]]
    SYNC_STATS["failed_aggregators"] = failed
    print("\n" + "=" * 70)
    print(" Aggregator Health Report")
    print("=" * 70)
    print(f"Total Aggregators : {len(AGGREGATORS)}")
    print(f"Successful        : {len(AGGREGATORS) - len(failed)}")
    print(f"Failed            : {len(failed)}")
    for source in failed:
        print("  ✖", source)
    print("=" * 70 + "\n")


def safe_sync():
    reset_statistics()
    log("=" * 70)
    log("Starting V5 Safe Synchronization")
    log("=" * 70)
    try:
        all_jobs = fetch_all_jobs()
        raw_jobs = len(all_jobs)
        processed = process_jobs(all_jobs)
        saved = save_jobs(processed)
        database_maintenance()
        update_statistics(raw_jobs, len(processed), saved)
        print_health_report()
        if SYNC_STATS["failed_aggregators"] and not processed:
            record_sync_completion("failed", saved, "; ".join(SYNC_STATS["failed_aggregators"]))
        else:
            record_sync_completion("completed", saved)
        print_statistics()
        log("V5 Synchronization Finished Successfully.")
        return saved
    except Exception as exc:
        try:
            record_sync_completion("failed", 0, str(exc))
        except Exception:
            pass
        raise


def sync_is_due(interval_hours=6):
    last_sync = get_last_successful_sync()
    if not last_sync:
        return True
    try:
        last_dt = datetime.fromisoformat(str(last_sync).replace("Z", "+00:00"))
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - last_dt).total_seconds() >= interval_hours * 3600
    except (TypeError, ValueError):
        return True


def maybe_run_scheduled_sync(interval_hours=6):
    if not sync_is_due(interval_hours):
        return False
    safe_sync()
    return True


if __name__ == "__main__":
    safe_sync()
