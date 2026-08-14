"""
database/init_db.py

Initializes the SQLite database.

Creates:
    - jobs table
    - sync_logs table
    - indexes
"""

import os
import sqlite3

# =====================================================
# Database Configuration
# =====================================================

DATABASE_DIR = "database"
DATABASE_FILE = os.path.join(DATABASE_DIR, "jobs.db")

os.makedirs(DATABASE_DIR, exist_ok=True)


# =====================================================
# Database Connection
# =====================================================

def get_connection():

    conn = sqlite3.connect(DATABASE_FILE)

    # Better SQLite performance
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA cache_size=-10000;")

    return conn


# =====================================================
# Validate Existing Database
# =====================================================

def validate_database():

    if not os.path.exists(DATABASE_FILE):
        return

    try:

        conn = sqlite3.connect(DATABASE_FILE)
        conn.execute("SELECT 1")
        conn.close()

    except sqlite3.DatabaseError:

        print("Corrupted database detected.")
        print("Recreating database...")

        os.remove(DATABASE_FILE)


# =====================================================
# Create Tables
# =====================================================

def create_tables(cursor):

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (

            job_id TEXT PRIMARY KEY,

            title TEXT,
            company TEXT,
            location TEXT,
            country TEXT,

            employment_type TEXT,

            skills TEXT,

            salary TEXT,

            description TEXT,

            source TEXT,

            apply_url TEXT,

            posted_date TEXT,

            closing_date TEXT,

            updated_at TIMESTAMP
            DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sync_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            source TEXT,

            status TEXT,

            jobs_added INTEGER DEFAULT 0,

            jobs_updated INTEGER DEFAULT 0,

            error_message TEXT,

            sync_time TIMESTAMP
            DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


# =====================================================
# Create Database Indexes
# =====================================================

def create_indexes(cursor):

    cursor.executescript(
        """

        CREATE INDEX IF NOT EXISTS idx_job_title
        ON jobs(title);

        CREATE INDEX IF NOT EXISTS idx_company
        ON jobs(company);

        CREATE INDEX IF NOT EXISTS idx_location
        ON jobs(location);

        CREATE INDEX IF NOT EXISTS idx_country
        ON jobs(country);

        CREATE INDEX IF NOT EXISTS idx_skills
        ON jobs(skills);

        CREATE INDEX IF NOT EXISTS idx_source
        ON jobs(source);

        CREATE INDEX IF NOT EXISTS idx_posted_date
        ON jobs(posted_date);

        CREATE INDEX IF NOT EXISTS idx_closing_date
        ON jobs(closing_date);

        CREATE INDEX IF NOT EXISTS idx_updated
        ON jobs(updated_at);

        """
    )


# =====================================================
# Initialize Database
# =====================================================

def initialize_database():

    validate_database()

    conn = get_connection()

    try:

        cursor = conn.cursor()

        create_tables(cursor)

        create_indexes(cursor)

        conn.commit()

        print("=" * 60)
        print("VisionBoard Database Initialized Successfully")
        print("=" * 60)
        print(f"Database : {DATABASE_FILE}")
        print("Tables   : jobs, sync_logs")
        print("Indexes  : Created")
        print("=" * 60)

    finally:

        conn.close()


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    initialize_database()