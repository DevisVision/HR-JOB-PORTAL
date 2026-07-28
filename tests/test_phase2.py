from database.db_service import get_jobs

jobs = get_jobs(10)

for job in jobs:

    print("=" * 60)

    print("TITLE :", job.get("title"))
    print("COMPANY :", job.get("company"))
    print("LOGO :", job.get("company_logo"))
    print("COUNTRY :", job.get("country"))
    print("WORK MODE :", job.get("work_mode"))
    print("PRIORITY :", job.get("priority"))
