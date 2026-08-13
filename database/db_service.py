"""
=========================================================
VisionBoard Career Portal
Database Service
=========================================================
Handles:
    • SQLite Connection
    • Generic Query Execution
    • CRUD Operations
    • Search
    • Pagination
    • Dashboard Metrics
=========================================================
"""

import os
import sqlite3
from typing import Dict, List, Optional, Any

# =========================================================
# DATABASE CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_FILE = os.path.join(BASE_DIR, "database", "jobs.db")


# =========================================================
# SQLITE CONNECTION
# =========================================================

def get_connection() -> sqlite3.Connection:
    """
    Creates an optimized SQLite connection.
    """

    conn = sqlite3.connect(DB_FILE)

    conn.row_factory = sqlite3.Row

    # Performance PRAGMA
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA cache_size=-10000;")

    return conn


# =========================================================
# GENERIC QUERY EXECUTOR
# =========================================================

def execute_query(
    query: str,
    params: tuple = (),
    fetch: bool = False,
    fetch_one: bool = False,
):
    """
    Generic SQL executor.

    Parameters
    ----------
    query : SQL query

    params : tuple

    fetch : returns list of dictionaries

    fetch_one : returns one dictionary
    """

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(query, params)

        if fetch_one:

            row = cursor.fetchone()

            if row:

                return dict(row)

            return None

        if fetch:

            rows = cursor.fetchall()

            return [dict(r) for r in rows]

        conn.commit()

        return True

    except Exception as e:

        print(f"[DATABASE ERROR] {e}")

        return None

    finally:

        conn.close()


# =========================================================
# CREATE INDEXES
# =========================================================

def create_indexes():
    """
    Safe to execute multiple times.
    Improves search performance.
    """

    indexes = [

        """
        CREATE INDEX IF NOT EXISTS idx_jobid
        ON jobs(job_id)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_title
        ON jobs(title)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_company
        ON jobs(company)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_country
        ON jobs(country)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_location
        ON jobs(location)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_skills
        ON jobs(skills)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_source
        ON jobs(source)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_posted
        ON jobs(posted_date)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_updated
        ON jobs(updated_at)
        """,

    ]

    conn = get_connection()

    cursor = conn.cursor()

    for sql in indexes:

        cursor.execute(sql)

    conn.commit()

    conn.close()

    print("✅ Database indexes verified.")


# =========================================================
# DATABASE HEALTH CHECK
# =========================================================

def test_connection() -> bool:
    """
    Verifies database connectivity.
    """

    try:

        conn = get_connection()

        conn.execute("SELECT 1")

        conn.close()

        return True

    except Exception as e:

        print(e)

        return False


# =========================================================
# TABLE EXISTS
# =========================================================

def table_exists(table_name: str) -> bool:

    result = execute_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?
        """,
        (table_name,),
        fetch_one=True,
    )

    return result is not None


# =========================================================
# TOTAL RECORDS
# =========================================================

def get_total_job_count() -> int:

    result = execute_query(
        """
        SELECT COUNT(*) AS total
        FROM jobs
        """,
        fetch_one=True,
    )

    if result:

        return result["total"]

    return 0


# =========================================================
# LAST UPDATED
# =========================================================

def get_last_sync():

    result = execute_query(
        """
        SELECT MAX(updated_at) AS sync_time
        FROM jobs
        """,
        fetch_one=True,
    )

    if result:

        return result["sync_time"]

    return None
# =========================================================
# SYNC STATUS
# =========================================================

def ensure_sync_logs_table():
    """Ensure the sync log table exists without changing job data."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            status TEXT,
            jobs_added INTEGER DEFAULT 0,
            jobs_updated INTEGER DEFAULT 0,
            error_message TEXT,
            sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def record_sync_completion(status, jobs_saved=0, error_message=None):
    """Record one completed/failed portal synchronization event."""
    ensure_sync_logs_table()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO sync_logs
        (source, status, jobs_added, jobs_updated, error_message, sync_time)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        ("VisionBoard Sync", status, jobs_saved, 0, error_message),
    )
    conn.commit()
    conn.close()


def get_last_successful_sync():
    """Return the timestamp of the latest successful full sync."""
    ensure_sync_logs_table()
    result = execute_query(
        """
        SELECT MAX(sync_time) AS sync_time
        FROM sync_logs
        WHERE status = 'completed'
          AND source = 'VisionBoard Sync'
        """,
        fetch_one=True,
    )
    return result["sync_time"] if result else None


# =========================================================
# INSERT SINGLE JOB
# =========================================================

def insert_job(job: Dict) -> bool:
    """
    Insert or update a single job.
    """

    query = """
    INSERT OR REPLACE INTO jobs
    (
        job_id,
        title,
        company,
        location,
        country,
        employment_type,
        skills,
        salary,
        description,
        source,
        apply_url,
        posted_date,
        updated_at
    )
    VALUES
    (
        ?,?,?,?,?,?,?,?,?,?,?,?,
        CURRENT_TIMESTAMP
    )
    """

    params = (

        job.get("job_id"),

        job.get("title"),

        job.get("company"),

        job.get("location"),

        job.get("country"),

        job.get("employment_type"),

        job.get("skills"),

        job.get("salary"),

        job.get("description"),

        job.get("source"),

        job.get("apply_url"),

        job.get("posted_date"),

    )

    return execute_query(query, params)


# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

save_job = insert_job


# =========================================================
# BULK INSERT
# =========================================================

def insert_jobs(jobs: List[Dict]) -> int:
    """
    Bulk insert jobs.
    Returns number of records inserted.
    """

    if not jobs:
        return 0

    conn = get_connection()

    cursor = conn.cursor()

    query = """
    INSERT OR REPLACE INTO jobs
    (
        job_id,
        title,
        company,
        location,
        country,
        employment_type,
        skills,
        salary,
        description,
        source,
        apply_url,
        posted_date,
        updated_at
    )
    VALUES
    (
        ?,?,?,?,?,?,?,?,?,?,?,?,
        CURRENT_TIMESTAMP
    )
    """

    records = []

    for job in jobs:

        records.append(

            (

                job.get("job_id"),

                job.get("title"),

                job.get("company"),

                job.get("location"),

                job.get("country"),

                job.get("employment_type"),

                job.get("skills"),

                job.get("salary"),

                job.get("description"),

                job.get("source"),

                job.get("apply_url"),

                job.get("posted_date"),

            )

        )

    cursor.executemany(query, records)

    conn.commit()

    inserted = cursor.rowcount

    conn.close()

    return inserted


# =========================================================
# JOB EXISTS
# =========================================================

def job_exists(job_id: str) -> bool:
    """
    Checks whether a Job ID already exists.
    """

    result = execute_query(
        """
        SELECT job_id
        FROM jobs
        WHERE job_id=?
        LIMIT 1
        """,
        (job_id,),
        fetch_one=True,
    )

    return result is not None


# =========================================================
# DELETE JOB
# =========================================================

def delete_job(job_id: str):

    execute_query(
        """
        DELETE
        FROM jobs
        WHERE job_id=?
        """,
        (job_id,),
    )


# =========================================================
# DELETE OLD JOBS
# =========================================================

def delete_old_jobs(days: int = 90):
    """
    Deletes jobs older than specified number of days.
    """

    execute_query(
        """
        DELETE
        FROM jobs
        WHERE date(updated_at)
        <
        date('now', ?)
        """,
        (f"-{days} day",),
    )


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicate_jobs():
    """
    Removes duplicate records while keeping
    the newest one.
    """

    execute_query(
        """
        DELETE FROM jobs

        WHERE rowid NOT IN (

            SELECT MAX(rowid)

            FROM jobs

            GROUP BY

                title,

                company,

                location

        )
        """
    )


# =========================================================
# VACUUM DATABASE
# =========================================================

def vacuum_database():
    """
    Rebuild database file
    and reclaim free space.
    """

    conn = get_connection()

    conn.execute("VACUUM")

    conn.close()


# =========================================================
# ANALYZE DATABASE
# =========================================================

def analyze_database():
    """
    Updates SQLite statistics
    for better query planning.
    """

    conn = get_connection()

    conn.execute("ANALYZE")

    conn.close()


# =========================================================
# DATABASE STATISTICS
# =========================================================

def database_statistics():

    return {

        "total_jobs": get_total_job_count(),

        "last_sync": get_last_sync(),

        "table_exists": table_exists("jobs"),

        "database": DB_FILE,

    }
# =========================================================
# SEARCH JOBS (ADVANCED)
# =========================================================

def search_jobs(
    keyword: str = "",
    category: str = "All Jobs",
    company: str = "",
    country: str = "",
    employment_type: str = "",
    source: str = "",
    limit: int = 100,
    offset: int = 0,
):
    """
    Advanced Job Search
    """

    sql = """
    SELECT *
    FROM jobs
    WHERE 1=1
    """

    params = []

    # -----------------------------------------------------
    # Keyword Search
    # -----------------------------------------------------

    if keyword:

        sql += """
        AND
        (
            LOWER(title) LIKE ?
            OR LOWER(company) LIKE ?
            OR LOWER(skills) LIKE ?
            OR LOWER(description) LIKE ?
            OR LOWER(location) LIKE ?
        )
        """

        pattern = f"%{keyword.lower()}%"

        params.extend([
            pattern,
            pattern,
            pattern,
            pattern,
            pattern,
        ])

    # -----------------------------------------------------
    # Company
    # -----------------------------------------------------

    if company and company != "All":

        sql += """
        AND LOWER(company)=?
        """

        params.append(company.lower())

    # -----------------------------------------------------
    # Country
    # -----------------------------------------------------

    if country and country != "All":

        sql += """
        AND LOWER(country) LIKE ?
        """

        params.append(f"%{country.lower()}%")

    # -----------------------------------------------------
    # Employment
    # -----------------------------------------------------

    if employment_type and employment_type != "All":

        sql += """
        AND LOWER(employment_type)=?
        """

        params.append(employment_type.lower())

    # -----------------------------------------------------
    # Source
    # -----------------------------------------------------

    if source and source != "All":

        sql += """
        AND LOWER(source)=?
        """

        params.append(source.lower())

    # -----------------------------------------------------
    # Category
    # -----------------------------------------------------

    if category == "India":

        sql += """
        AND
        (
            LOWER(country) LIKE '%india%'
            OR LOWER(location) LIKE '%india%'
        )
        """

    elif category == "Remote":

        sql += """
        AND
        (
            LOWER(location) LIKE '%remote%'
            OR LOWER(description) LIKE '%remote%'
        )
        """

    # -----------------------------------------------------
    # Latest First
    # -----------------------------------------------------

    sql += """
    ORDER BY
        posted_date DESC,
        updated_at DESC
    LIMIT ?
    OFFSET ?
    """

    params.extend([limit, offset])

    return execute_query(
        sql,
        tuple(params),
        fetch=True,
    )


# =========================================================
# GET LATEST JOBS
# =========================================================

def get_jobs(
    limit: int = 100,
    offset: int = 0,
):

    return execute_query(
        """
        SELECT *
        FROM jobs
        ORDER BY
            updated_at DESC
        LIMIT ?
        OFFSET ?
        """,
        (
            limit,
            offset,
        ),
        fetch=True,
    )


# =========================================================
# GET JOB BY ID
# =========================================================

def get_job(job_id):

    return execute_query(
        """
        SELECT *
        FROM jobs
        WHERE job_id=?
        """,
        (job_id,),
        fetch_one=True,
    )


# =========================================================
# GET JOBS BY COMPANY
# =========================================================

def get_jobs_by_company(
    company,
    limit=100,
):

    return execute_query(
        """
        SELECT *
        FROM jobs
        WHERE LOWER(company)=?
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (
            company.lower(),
            limit,
        ),
        fetch=True,
    )


# =========================================================
# GET JOBS BY COUNTRY
# =========================================================

def get_jobs_by_country(
    country,
    limit=100,
):

    return execute_query(
        """
        SELECT *
        FROM jobs
        WHERE LOWER(country)
        LIKE ?
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (
            f"%{country.lower()}%",
            limit,
        ),
        fetch=True,
    )


# =========================================================
# GET JOBS BY SOURCE
# =========================================================

def get_jobs_by_source(
    source,
    limit=100,
):

    return execute_query(
        """
        SELECT *
        FROM jobs
        WHERE LOWER(source)=?
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (
            source.lower(),
            limit,
        ),
        fetch=True,
    )
# =========================================================
# PAGINATED JOBS
# =========================================================

def get_jobs_paginated(
    page: int = 1,
    page_size: int = 20,
):

    if page < 1:
        page = 1

    offset = (page - 1) * page_size

    return execute_query(
        """
        SELECT *
        FROM jobs
        ORDER BY
            updated_at DESC
        LIMIT ?
        OFFSET ?
        """,
        (
            page_size,
            offset,
        ),
        fetch=True,
    )


# =========================================================
# DISTINCT COMPANIES
# =========================================================

def get_companies():

    rows = execute_query(
        """
        SELECT DISTINCT company
        FROM jobs
        WHERE company IS NOT NULL
          AND TRIM(company) <> ''
        ORDER BY company
        """,
        fetch=True,
    )

    return [r["company"] for r in rows]


# =========================================================
# DISTINCT COUNTRIES
# =========================================================

def get_countries():

    rows = execute_query(
        """
        SELECT DISTINCT country
        FROM jobs
        WHERE country IS NOT NULL
          AND TRIM(country) <> ''
        ORDER BY country
        """,
        fetch=True,
    )

    return [r["country"] for r in rows]


# =========================================================
# DISTINCT LOCATIONS
# =========================================================

def get_locations():

    rows = execute_query(
        """
        SELECT DISTINCT location
        FROM jobs
        WHERE location IS NOT NULL
          AND TRIM(location) <> ''
        ORDER BY location
        """,
        fetch=True,
    )

    return [r["location"] for r in rows]


# =========================================================
# DISTINCT SOURCES
# =========================================================

def get_sources():

    rows = execute_query(
        """
        SELECT DISTINCT source
        FROM jobs
        WHERE source IS NOT NULL
          AND TRIM(source) <> ''
        ORDER BY source
        """,
        fetch=True,
    )

    return [r["source"] for r in rows]


# =========================================================
# DISTINCT SKILLS
# =========================================================

def get_skills():

    rows = execute_query(
        """
        SELECT skills
        FROM jobs
        WHERE skills IS NOT NULL
        """,
        fetch=True,
    )

    skills = set()

    for row in rows:

        value = row["skills"]

        if not value:
            continue

        for skill in value.split(","):

            skill = skill.strip()

            if skill:

                skills.add(skill)

    return sorted(skills)


# =========================================================
# INDIA JOBS
# =========================================================

def get_india_jobs(limit=200):

    return execute_query(
        """
        SELECT *
        FROM jobs

        WHERE

            LOWER(country) LIKE '%india%'

            OR LOWER(location) LIKE '%india%'

        ORDER BY

            updated_at DESC

        LIMIT ?
        """,
        (limit,),
        fetch=True,
    )


# =========================================================
# REMOTE JOBS
# =========================================================

def get_remote_jobs(limit=200):

    return execute_query(
        """
        SELECT *
        FROM jobs

        WHERE

            LOWER(location) LIKE '%remote%'

            OR LOWER(description) LIKE '%remote%'

        ORDER BY

            updated_at DESC

        LIMIT ?
        """,
        (limit,),
        fetch=True,
    )


# =========================================================
# FORTUNE COMPANY JOBS
# =========================================================

FORTUNE_COMPANIES = [

    "IBM",

    "ACCENTURE",

    "COGNIZANT",

    "CAPGEMINI",

    "MICROSOFT",

    "GOOGLE",

    "AMAZON",

    "ORACLE",

    "EY",

    "KPMG",

    "DELOITTE",

    "PWC",

    "UST",

    "WIPRO",

    "INFOSYS",

    "TCS",

    "HCL",

    "TECH MAHINDRA",

    "CISCO",

    "ALLIANZ",

]


def get_fortune_jobs(limit=500):

    conditions = []

    params = []

    for company in FORTUNE_COMPANIES:

        conditions.append(
            "UPPER(company) LIKE ?"
        )

        params.append(f"%{company}%")

    sql = f"""
        SELECT *

        FROM jobs

        WHERE

        {' OR '.join(conditions)}

        ORDER BY

            updated_at DESC

        LIMIT ?
    """

    params.append(limit)

    return execute_query(
        sql,
        tuple(params),
        fetch=True,
    )


# =========================================================
# TOTAL PAGES
# =========================================================

def get_total_pages(
    page_size=20,
):

    total = get_total_job_count()

    if total == 0:

        return 1

    return (total + page_size - 1) // page_size


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

def get_dashboard_summary():

    return {

        "total_jobs": get_total_job_count(),

        "india_jobs": len(get_india_jobs()),

        "remote_jobs": len(get_remote_jobs()),

        "companies": len(get_companies()),

        "countries": len(get_countries()),

        "sources": len(get_sources()),

        "last_sync": get_last_sync(),

    }
# =========================================================
# DASHBOARD METRICS
# =========================================================

def get_job_count() -> int:
    """
    Returns total number of jobs.
    """
    return get_total_job_count()


def get_india_job_count() -> int:

    result = execute_query(
        """
        SELECT COUNT(*) AS total
        FROM jobs
        WHERE
            LOWER(country) LIKE '%india%'
            OR LOWER(location) LIKE '%india%'
        """,
        fetch_one=True,
    )

    return result["total"] if result else 0


def get_remote_job_count() -> int:

    result = execute_query(
        """
        SELECT COUNT(*) AS total
        FROM jobs
        WHERE
            LOWER(location) LIKE '%remote%'
            OR LOWER(description) LIKE '%remote%'
        """,
        fetch_one=True,
    )

    return result["total"] if result else 0


def get_abroad_job_count() -> int:

    result = execute_query(
        """
        SELECT COUNT(*) AS total
        FROM jobs
        WHERE
            LOWER(country) NOT LIKE '%india%'
        """,
        fetch_one=True,
    )

    return result["total"] if result else 0


# =========================================================
# COMPANY ANALYTICS
# =========================================================

def get_top_companies(limit: int = 20):

    return execute_query(
        """
        SELECT
            company,
            COUNT(*) AS total_jobs

        FROM jobs

        WHERE company IS NOT NULL

        GROUP BY company

        ORDER BY total_jobs DESC

        LIMIT ?
        """,
        (limit,),
        fetch=True,
    )


# =========================================================
# SOURCE ANALYTICS
# =========================================================

def get_source_statistics():

    return execute_query(
        """
        SELECT
            source,
            COUNT(*) AS total_jobs

        FROM jobs

        GROUP BY source

        ORDER BY total_jobs DESC
        """,
        fetch=True,
    )


# =========================================================
# COUNTRY ANALYTICS
# =========================================================

def get_country_statistics():

    return execute_query(
        """
        SELECT
            country,
            COUNT(*) AS total_jobs

        FROM jobs

        GROUP BY country

        ORDER BY total_jobs DESC
        """,
        fetch=True,
    )


# =========================================================
# RECENT JOBS
# =========================================================

def get_recent_jobs(limit: int = 20):

    return execute_query(
        """
        SELECT *

        FROM jobs

        ORDER BY updated_at DESC

        LIMIT ?
        """,
        (limit,),
        fetch=True,
    )


# =========================================================
# LATEST FORTUNE JOBS
# =========================================================

def get_latest_fortune_jobs(limit: int = 100):

    conditions = []
    params = []

    for company in FORTUNE_COMPANIES:

        conditions.append("UPPER(company) LIKE ?")

        params.append(f"%{company}%")

    sql = f"""
    SELECT *

    FROM jobs

    WHERE

    {' OR '.join(conditions)}

    ORDER BY

        posted_date DESC,
        updated_at DESC

    LIMIT ?
    """

    params.append(limit)

    return execute_query(
        sql,
        tuple(params),
        fetch=True,
    )


# =========================================================
# DATABASE SUMMARY
# =========================================================

def get_database_summary():

    return {

        "total_jobs": get_job_count(),

        "india_jobs": get_india_job_count(),

        "remote_jobs": get_remote_job_count(),

        "abroad_jobs": get_abroad_job_count(),

        "companies": len(get_companies()),

        "countries": len(get_countries()),

        "locations": len(get_locations()),

        "sources": len(get_sources()),

        "skills": len(get_skills()),

        "last_sync": get_last_sync(),

    }


# =========================================================
# HEALTH REPORT
# =========================================================

def database_health():

    return {

        "database_exists": os.path.exists(DB_FILE),

        "connection_ok": test_connection(),

        "table_exists": table_exists("jobs"),

        "total_jobs": get_job_count(),

        "last_sync": get_last_sync(),

    }
# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():
    """
    Initializes the database by verifying the
    connection and creating indexes.
    Safe to call every application startup.
    """

    if not table_exists("jobs"):

        raise RuntimeError(
            "jobs table does not exist. "
            "Run database/init_db.py first."
        )

    create_indexes()

    print("✅ Database initialized successfully.")


# =========================================================
# CLEAR DATABASE
# =========================================================

def clear_jobs():

    execute_query(
        """
        DELETE FROM jobs
        """
    )


# =========================================================
# GET DATABASE FILE SIZE
# =========================================================

def get_database_size():

    if not os.path.exists(DB_FILE):

        return 0

    size = os.path.getsize(DB_FILE)

    return round(size / (1024 * 1024), 2)


# =========================================================
# OPTIMIZE DATABASE
# =========================================================

def optimize_database():
    """
    Performs database maintenance.
    """

    remove_duplicate_jobs()

    analyze_database()

    vacuum_database()

    create_indexes()

    print("✅ Database optimized.")


# =========================================================
# SEARCH SUGGESTIONS
# =========================================================

def get_search_suggestions(limit=15):

    sql = """
    SELECT DISTINCT title

    FROM jobs

    WHERE title IS NOT NULL

    ORDER BY title

    LIMIT ?
    """

    rows = execute_query(
        sql,
        (limit,),
        fetch=True,
    )

    return [r["title"] for r in rows]


# =========================================================
# COMPANY SUGGESTIONS
# =========================================================

def get_company_suggestions(limit=100):

    sql = """
    SELECT DISTINCT company

    FROM jobs

    WHERE company IS NOT NULL

    ORDER BY company

    LIMIT ?
    """

    rows = execute_query(
        sql,
        (limit,),
        fetch=True,
    )

    return [r["company"] for r in rows]


# =========================================================
# LOCATION SUGGESTIONS
# =========================================================

def get_location_suggestions(limit=100):

    sql = """
    SELECT DISTINCT location

    FROM jobs

    WHERE location IS NOT NULL

    ORDER BY location

    LIMIT ?
    """

    rows = execute_query(
        sql,
        (limit,),
        fetch=True,
    )

    return [r["location"] for r in rows]


# =========================================================
# DATABASE INFORMATION
# =========================================================

def get_database_info():

    return {

        "database": DB_FILE,

        "database_size_mb": get_database_size(),

        "total_jobs": get_job_count(),

        "india_jobs": get_india_job_count(),

        "remote_jobs": get_remote_job_count(),

        "abroad_jobs": get_abroad_job_count(),

        "companies": len(get_companies()),

        "countries": len(get_countries()),

        "sources": len(get_sources()),

        "last_sync": get_last_sync(),

    }


# =========================================================
# STARTUP
# =========================================================

try:

    initialize_database()

except Exception as e:

    print(e)