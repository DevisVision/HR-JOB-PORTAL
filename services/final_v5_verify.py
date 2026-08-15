"""Final V5 verification helper.

Run from the project root:

    python -m services.final_v5_verify

This does not modify the database.
"""

import sqlite3

from database.db_service import DB_FILE


def main():
    conn = sqlite3.connect(DB_FILE)

    print("=" * 70)
    print("VisionBoard V5 FINAL DATABASE CHECK")
    print("=" * 70)

    queries = {
        "TOTAL": "SELECT COUNT(*) FROM jobs",
        "UST": "SELECT COUNT(*) FROM jobs WHERE LOWER(TRIM(company))='ust'",
        "IBS": "SELECT COUNT(*) FROM jobs WHERE LOWER(company) LIKE '%ibs%'",
        "PITS": "SELECT COUNT(*) FROM jobs WHERE LOWER(company) LIKE '%pit%'",
        "TECHNOPARK": (
            "SELECT COUNT(*) FROM jobs "
            "WHERE LOWER(TRIM(source))='technopark'"
        ),
        "TECHNOPARK_MENU": (
            "SELECT COUNT(*) FROM jobs "
            "WHERE LOWER(TRIM(source))='technopark' "
            "AND LOWER(TRIM(company))='menu'"
        ),
    }

    for name, sql in queries.items():
        print(f"{name:<20}: {conn.execute(sql).fetchone()[0]}")

    print("\nTechnopark companies:")
    rows = conn.execute(
        """
        SELECT company, COUNT(*) AS total
        FROM jobs
        WHERE LOWER(TRIM(source))='technopark'
        GROUP BY company
        ORDER BY total DESC, company
        LIMIT 50
        """
    ).fetchall()

    for company, total in rows:
        print(f"  {company:<45} {total}")

    print("\nFresh Data Engineering jobs:")
    rows = conn.execute(
        """
        SELECT title, company, posted_date, source
        FROM jobs
        WHERE LOWER(title) LIKE '%data engineer%'
        ORDER BY posted_date DESC
        LIMIT 20
        """
    ).fetchall()

    for row in rows:
        print("  ", row)

    print("=" * 70)
    conn.close()


if __name__ == "__main__":
    main()
