# VisionBoard Career Portal V5.5 Final

## What is fixed

1. **Technopark employer extraction**
   - Stores the real employer (for example UST) instead of values such as
     `Technopark Job Posting For ...`.
   - Uses the detail page as the source of truth.
   - Adds safe email/website fallback only when the employer line cannot be
     parsed.

2. **Technopark search coverage**
   - Active Technopark postings remain in the database even when they are not
     part of the default VisionBoard Data/AI/Cloud feed.
   - Explicit searches can find them by company, title, skills, location,
     source, or URL.

3. **Company search accuracy**
   - `UST` no longer matches unrelated words such as `Gusto` or `customer`.
   - `IBS`, `PITS`, and unknown company names use the same search path.
   - No comma-separated search syntax is required.

4. **HR experience**
   - Streamlit does **not** run synchronization on page load.
   - A separate background scheduler runs the sync every 6 hours.
   - HR can refresh/search the portal while the scheduler is collecting data.

## First run

From the project root:

```text
python -m services.sync_service
```

This performs one immediate full synchronization.

Then start the background scheduler separately:

```text
python -m services.background_scheduler
```

Or double-click:

```text
run_background_scheduler.bat
```

For production/HR use on Windows, register the scheduler command with
Windows Task Scheduler so it starts automatically when the server starts.

## Verify after synchronization

```text
python -c "import sqlite3; c=sqlite3.connect('database/jobs.db'); print('UST:', c.execute(\"SELECT COUNT(*) FROM jobs WHERE lower(company)='ust'\").fetchone()[0]); print('Technopark:', c.execute(\"SELECT COUNT(*) FROM jobs WHERE lower(source)='technopark'\").fetchone()[0]); print('Technopark UST:', c.execute(\"SELECT COUNT(*) FROM jobs WHERE lower(source)='technopark' AND lower(company)='ust'\").fetchone()[0])"
```

Then test in the portal:

- `UST`
- `IBS`
- `PITS`
- `Technopark`
- `data engineer`
- `UST data engineer`

No comma-separated criteria are needed.


## V5.5 corrective fixes
- Technopark employer extraction now uses the employer/address block and corporate website/email before any fallback.
- The crawler label `Technopark Job Posting For ...` is never accepted as the employer.
- Search no longer uses arbitrary compact-substring matching, preventing `UST` from matching `Customer`.
- Compact company matching is limited to exact/prefix/acronym cases.
- Existing aggregators and the six-hour background scheduler are otherwise unchanged.

After replacing the project, run one full sync from the project root:

```bat
python -m services.sync_service
```

Then test `UST`, `IBS`, `PITS`, `Technopark`, `data engineer`, and `UST data engineer`.
