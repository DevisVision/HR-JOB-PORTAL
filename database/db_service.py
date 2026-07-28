#db_service.py
import sqlite3
import os
from typing import List, Dict, Optional

from config.search_categories import SEARCH_CATEGORIES

DB_FILE = os.path.join("database", "jobs.db")


# =====================================================================================================================================================
# Database Connection ****************** everywhere, you'll simply write: return execute_query(sql, params, fetch=True)
# =====================================================================================================================================================
def get_connection():
    """
    Returns an optimized SQLite connection.
    """

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA cache_size=-10000;")

    return conn
# =====================================================
# Create Database Helper
# =====================================================
def execute_query(query, params=None, fetch=False):
    """
    Generic SQL executor.
    """

    conn = get_connection()

    try:

        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            return [dict(r) for r in cursor.fetchall()]

        conn.commit()

    finally:

        conn.close()

# =====================================================
# Create Database Indexes
# =====================================================
def create_indexes():
    """
    Creates indexes to improve query performance.
    Safe to run multiple times.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        indexes = [

            "CREATE INDEX IF NOT EXISTS idx_title ON jobs(title)",

            "CREATE INDEX IF NOT EXISTS idx_company ON jobs(company)",

            "CREATE INDEX IF NOT EXISTS idx_country ON jobs(country)",

            "CREATE INDEX IF NOT EXISTS idx_location ON jobs(location)",

            "CREATE INDEX IF NOT EXISTS idx_skills ON jobs(skills)",

            "CREATE INDEX IF NOT EXISTS idx_source ON jobs(source)",

            "CREATE INDEX IF NOT EXISTS idx_posted_date ON jobs(posted_date)",

            "CREATE INDEX IF NOT EXISTS idx_updated_at ON jobs(updated_at)"

        ]

        for index in indexes:
            cursor.execute(index)

        conn.commit()

        print("✅ Database indexes created successfully.")

    except Exception as e:
        print(f"❌ Failed to create indexes: {e}")

    finally:
        conn.close()

# =====================================================
# Insert / Update Single Job
# =====================================================
def insert_job(job: Dict):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO jobs (
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
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
        ),
    )

    conn.commit()
    conn.close()


save_job = insert_job


# =====================================================
# Bulk Insert
# =====================================================
def insert_jobs(jobs: List[Dict]):

    if not jobs:
        return

    conn = get_connection()
    cursor = conn.cursor()

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

    cursor.executemany(
        """
        INSERT OR REPLACE INTO jobs (
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        records,
    )

    conn.commit()
    conn.close()


# =====================================================
# Latest Jobs
# =====================================================
def get_jobs(limit: int = 100):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


# =====================================================
# Category Search
# =====================================================
def get_jobs_by_category(
        category: str,
        limit: int = 100
):

    if category == "All Jobs":
        return get_jobs(limit)

    conn = get_connection()
    cursor = conn.cursor()

    if category == "India":

        cursor.execute(
            """
            SELECT *
            FROM jobs
            WHERE LOWER(country) LIKE '%india%'
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    keywords = SEARCH_CATEGORIES.get(category, [])

    if not keywords:
        conn.close()
        return []

    conditions = []
    values = []

    for word in keywords:

        conditions.append(
            """
            LOWER(title) LIKE ?
            OR LOWER(skills) LIKE ?
            OR LOWER(description) LIKE ?
            """
        )

        pattern = f"%{word.lower()}%"

        values.extend(
            [
                pattern,
                pattern,
                pattern
            ]
        )

    query = f"""
        SELECT *
        FROM jobs
        WHERE {' OR '.join(conditions)}
        ORDER BY updated_at DESC
        LIMIT ?
    """

    values.append(limit)

    cursor.execute(query, values)

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


# =====================================================
# Search Jobs
# =====================================================
def search_jobs(
        keyword: str,
        category: str = "All Jobs"
):

    conn = get_connection()
    cursor = conn.cursor()

    pattern = f"%{keyword.lower()}%"

    query = """
        SELECT *
        FROM jobs
        WHERE
        (
            LOWER(title) LIKE ?
            OR LOWER(company) LIKE ?
            OR LOWER(skills) LIKE ?
            OR LOWER(location) LIKE ?
            OR LOWER(country) LIKE ?
            OR LOWER(description) LIKE ?
        )
    """

    values = [
        pattern,
        pattern,
        pattern,
        pattern,
        pattern,
        pattern
    ]

    if category != "All Jobs":

        keywords = SEARCH_CATEGORIES.get(category, [])

        if keywords:

            category_conditions = []

            for word in keywords:

                category_conditions.append(
                    """
                    LOWER(title) LIKE ?
                    OR LOWER(skills) LIKE ?
                    OR LOWER(description) LIKE ?
                    """
                )

                p = f"%{word.lower()}%"

                values.extend([p, p, p])

            query += (
                " AND ("
                + " OR ".join(category_conditions)
                + ")"
            )

    query += """
        ORDER BY updated_at DESC
    """

    cursor.execute(query, values)

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return rows


# =====================================================
# Metrics
# =====================================================
def get_job_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM jobs"
    )

    count = cursor.fetchone()[0]
    conn.close()

    return count


def get_india_job_count():
    return len(
        get_jobs_by_category(
            "India",
            limit=10000
        )
    )


def get_remote_job_count():
    return len(
        get_jobs_by_category(
            "Remote",
            limit=10000
        )
    )