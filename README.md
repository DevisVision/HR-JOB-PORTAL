# VisionBoard Career Portal — V5.3

V5.3 is a targeted stability upgrade. Existing application, UI, ranking, freshness and database behavior are preserved; the changes are focused on job ingestion/discovery and search reliability.

## Active job sources

- Adzuna
- ArbeitNow
- Greenhouse
- Lever
- RemoteOK
- Remotive
- Technopark

TheMuse and USAJobs are intentionally not registered because their current endpoints were failing during UAT.

## Technopark V5.3

The collector now uses three additive discovery paths:

1. Technopark `/job-crawl`
2. The paginated public `/job-search` directory (`start=0,20,40,...`)
3. VisionBoard job keywords as targeted searches

Each discovered detail page is opened and parsed for the real title, company, posted date, closing date, description, skills and apply URL. Expired postings are rejected at ingestion.

Technopark postings are retained broadly so searches for known or unknown companies can find them. The normal VisionBoard Data/AI relevance filter still controls the default feed.

## Search behavior

The search box remains a single normal search field. HR does **not** need comma-separated criteria.

Examples:

- `UST`
- `IBS`
- `pits`
- `data engineer`
- `UST data engineer`
- `Databricks`
- `Python`
- `Bangalore`

Company aliases and compact company matching are supported, so searches such as `pits` can find `PIT Solutions` without weakening the word-aware protection that prevents `UST` from matching unrelated text such as `customer`.

## Background synchronization

Streamlit does **not** run the expensive synchronization when HR opens the portal. The GitHub Actions workflow runs every 6 hours and refreshes `database/jobs.db` in the repository.

For local testing, run the synchronization manually when you want to refresh the local SQLite database:

```text
python services/sync_service.py
```

Then start Streamlit normally:

```text
streamlit run app.py
```

The portal reads the existing database immediately and does not block HR while a sync is running.
